import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from .models import Usuario, Planilla, Adscripcion, Plazas, Directorio, BajasExpedientes, MovimientoPlaza, PersonalAcumulado, ArchivoSubido, ArchivoSubido, Convenio
from django.db import connection
import csv
from datetime import datetime
from django.conf import settings
from .forms import ArchivoForm
from django.db.models import IntegerField, F
from django.db.models.functions import Cast
from django.http import JsonResponse

def login_usuario(request):
    mensaje = ''
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        recordar = request.POST.get('recordar')

        try:
            user = Usuario.objects.get(nombre_usuario=usuario, contrasena=contrasena, estatus=True)
            user.ultimo_ingreso = timezone.now()
            user.save()

            response = redirect('planilla')
            max_age = 60*60*24*30 if recordar else None
            response.set_cookie('usuario', usuario, max_age=max_age)
            response.set_cookie('autorizacion', user.autorizacion, max_age=max_age)
            return response

        except Usuario.DoesNotExist:
            mensaje = 'Usuario o contraseña incorrectos, intenta nuevamente.'

    return render(request, 'planilla/login.html', {'mensaje': mensaje})

def logout_usuario(request):
    response = redirect('login_usuario')
    response.delete_cookie('usuario')
    response.delete_cookie('autorizacion')
    return response

def lista_planilla(request):
    datos = Planilla.objects.all().order_by('clave')  # orden ascendente por clave numérica
    usuario_cookie = request.COOKIES.get('usuario', '')
    autorizacion = ''
    if usuario_cookie:
        usuario_obj = Usuario.objects.filter(nombre_usuario=usuario_cookie).first()
        if usuario_obj:
            autorizacion = usuario_obj.autorizacion

    return render(request, 'planilla/lista.html', {
        'datos': datos,
        'autorizacion_usuario': autorizacion,
    })

def lista(request):
    datos = Planilla.objects.all()
    return render(request, 'planilla/lista.html', {'datos': datos})

def plazas(request):
    return render(request, 'planilla/plazas.html')

def files(request):
    return render(request, 'planilla/files.html')

def test(request):
    return render(request, 'planilla/prueba.html')

def dplanteles(request):
    return render(request, 'planilla/debug_planteles.html')

def anexo_ejecucion(request):
    plazas = Plazas.objects.all()
    return render(request, 'planilla/anexo_ejecucion.html', {'plazas': plazas})

def historial(request):
    return render(request, 'planilla/historial.html')

def debug_planteles(request):
    planteles = Adscripcion.objects.filter(activo="1").order_by('nombre')
    return render(request, 'planilla/debug_planteles.html', {'planteles': planteles})

@csrf_exempt
def altas_nueva(request):
    if request.method == 'POST':
        nombre = f"{request.POST.get('nombre', '').strip()} {request.POST.get('apellido_paterno', '').strip()} {request.POST.get('apellido_materno', '').strip()}"

        plantel_id = request.POST.get('plantel', '')
        adscripcion_obj = Adscripcion.objects.filter(id=plantel_id).first()
        adscripcion_texto = adscripcion_obj.nombre if adscripcion_obj else ''
        departamento = adscripcion_obj.municipio if adscripcion_obj else ''

        # clave ahora es int (PK en planilla3)
        clave_str = request.POST.get('no_personal', '').strip()
        try:
            clave = int(clave_str)
        except ValueError:
            messages.error(request, '❌ La clave debe ser numérica.')
            return redirect('altas_nueva')

        if Planilla.objects.filter(clave=clave).exists():
            messages.error(request, '❌ Ya existe un registro con ese número de personal.')
            return redirect('altas_nueva')

        # Mapear sindicalizado a boolean
        sind_raw = (request.POST.get('sindicalizado', '') or '').strip().lower()
        if sind_raw in ('si', 'sí', 'true', 't', '1', 'yes'):
            sind_val = True
        elif sind_raw in ('no', 'false', 'f', '0'):
            sind_val = False
        else:
            sind_val = None  # si viene vacío o irreconocible

        fecha_ingreso = request.POST.get('fecha_ingreso', None) or None  # deja que Django la parsee si viene YYYY-MM-DD

        Planilla.objects.create(
            clave=clave,
            nombre=nombre,
            adscripcion=adscripcion_texto,
            departamento=departamento,
            rfc=request.POST.get('rfc', '').strip(),
            curp=request.POST.get('curp', '').strip(),
            puesto=request.POST.get('categoria', '').strip(),
            sindicato=sind_val,
            fecha_de_ingreso=fecha_ingreso
        )

        messages.success(request, '✅ Registro guardado correctamente.')
        return redirect('planilla')

    # GET: siguiente clave (max + 1)
    ultimo = Planilla.objects.order_by('-clave').values_list('clave', flat=True).first()
    siguiente_clave = str((ultimo or 0) + 1)

    planteles = Adscripcion.objects.all().order_by('nombre')
    return render(request, 'planilla/altas_nueva.html', {
        'planteles': planteles,
        'siguiente_clave': siguiente_clave
    })


@csrf_exempt
def eliminar_registro(request, no):
    if request.method == 'POST':
        try:
            registro = Planilla.objects.get(clave=int(no))
            registro.delete()
            return JsonResponse({'mensaje': 'Registro eliminado'})
        except (Planilla.DoesNotExist, ValueError):
            return JsonResponse({'error': 'Registro no encontrado'}, status=404)
    return HttpResponseNotAllowed(['POST'])

from django.shortcuts import render
from django.db import connection

def consulta(request):
    empleado = None
    empleado_items = []
    clave_busqueda = request.GET.get('clave')
    campos_bloqueados = [
         'clave', 'puesto', 'banco', 'cuenta', 'salario_base',
         'situacion_adm', 'email', 'zona'
    ]
    campos_ocultos = ['banco', 'cuenta', 'salario_base']

    autorizacion_usuario = request.COOKIES.get('autorizacion', 'lector')

    if clave_busqueda:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    clave, nombre, adscripcion, departamento, puesto, 
                    rfc, curp, nss, fecha_de_ingreso, sindicato, 
                    cp, banco, cuenta, salario_base, situacion_adm, 
                    email, zona
                FROM planilla3
                WHERE clave = %s
            """, [clave_busqueda])
            row = cursor.fetchone()

        if row:
            empleado = {
                'clave': row[0],
                'nombre': row[1],
                'adscripcion': row[2],
                'departamento': row[3],
                'puesto': row[4],
                'rfc': row[5],
                'curp': row[6],
                'nss': row[7],
                'fecha_de_ingreso': row[8],
                'sindicato': row[9],
                'cp': row[10],
                'banco': row[11],
                'cuenta': row[12],
                'salario_base': row[13],
                'situacion_adm': row[14],
                'email': row[15],
                'zona': row[16],
            }

    if empleado:
        empleado_items = list(empleado.items())

    return render(request, 'planilla/consulta.html', {
        'empleado_items': empleado_items,
        'clave_busqueda': clave_busqueda,
        'autorizacion_usuario': autorizacion_usuario,
        'campos_bloqueados': campos_bloqueados,
        'campos_ocultos': campos_ocultos if autorizacion_usuario == 'consultor' else []
    })


    
def estadisticas(request):
    trabajadores = Planilla.objects.all()
    total_trabajadores = trabajadores.count()
    puestos_unicos = trabajadores.values_list('puesto', flat=True).distinct().count()

    lista_puestos = [
	"SECRETARIA DE DIRECTOR DE AREA", "ALMACENISTA", "ENCARGADO DE ORDEN", "TAQUIMECANOGRAFA", "VIGILANTE", "PROGRAMADOR", "PROF ASOCIADO B TT", "JEFE DE OFICINA",
	"COORDINADOR ACADEMICO", "AUXILIAR DE SERVICIOS Y MANTTO.", "CAPTURISTA", "PROF CECYT II", "TECNICO ESPECIALIZADO", "DIRECTOR DE PLANTEL B", "OFICIAL DE MANTENIMIENTO",
	"TRABAJADORA SOCIAL", "ANALISTA ESPECIALIZADO", "DIRECTOR DE PLANTEL A", "PROF ASOCIADO C TT", "PROF TITULAR C TC", "SECRETARIA DE DIRECTOR DE PLANTEL", "PROF TITULAR A MT", "PROF TITULAR C MT", "DIRECTOR DE AREA", "PROF CECYT I", "TEC DOC ASOC A TT", "SUPERVISOR", "ENFERMERA", "ADMINISTRATIVO ESPECIALIZADO", "PROF ASOCIADO B TC",
	"PROF TITULAR B TT", "LABORATORISTA", "PROF ASOCIADO B MT", "BIBLIOTECARIO", "JEFE DE DEPARTAMENTO", "PROF TITULAR B TC", "PROF TITULAR B MT", "PROF TITULAR A TC",
	"PROF ASOCIADO C MT", "TEC DOC ASOC B TT", "PROF TITULAR A TT", "TEC DOC ASOC C TT", "PROF ASOCIADO C TC", "INGENIERO EN SISTEMAS", "TEC DOC CECYT I", 
	"COOR. DE TECNICOS ESPECIALIZADOS", "PROF TITULAR C TT", "DIRECTOR GENERAL", "TEC DOC ASOC A TC", "PROF CECYT III", "SECRETARIA DE DIRECTOR GENERAL"
    ]

    puestos_lista = []
    conteo_y_coincidencia = []
    puestos_labels = []
    puestos_data = []
    puestos_sin_ocupar = 0

    for puesto in lista_puestos:
        cantidad_planilla = trabajadores.filter(puesto=puesto).count()
        cantidad_plazas = Plazas.objects.filter(denominacion=puesto).count()
        existe_en_plazas = cantidad_plazas > 0

        if cantidad_planilla > 0:
            puestos_lista.append({'label': puesto, 'cantidad': cantidad_planilla})
            puestos_labels.append(puesto)
            puestos_data.append(cantidad_planilla)
        else:
            puestos_sin_ocupar += 1

        conteo_y_coincidencia.append({
            'puesto': puesto,
            'cantidad_planilla': cantidad_planilla,
            'cantidad_plazas': cantidad_plazas,
            'coincide': existe_en_plazas,
            'diferencia': cantidad_planilla - cantidad_plazas,
        })

    puestos_tuplas = list(zip(puestos_labels, puestos_data))

    context = {
        'total_trabajadores': total_trabajadores,
        'puestos_unicos': puestos_unicos,
        'puestos_sin_ocupar': puestos_sin_ocupar,
        'conteo_y_coincidencia': conteo_y_coincidencia,
        'puestos_lista': puestos_lista,
        'puestos_labels': puestos_labels,
        'puestos_data': puestos_data,
        'puestos_tuplas': puestos_tuplas,
    }

    return render(request, 'planilla/estadisticas.html', context)

def directorio(request):
    directorio = Directorio.objects.all().order_by('id')
    return render(request, 'planilla/directorio.html', {'directorio': directorio})
    
def altas_lista(request):
    # Obtiene la fecha actual
    hoy = timezone.now()
    
    # Filtra por mes y año de ingreso
    altas_mes_actual = Planilla.objects.filter(
        fecha_de_ingreso__year=hoy.year,
        fecha_de_ingreso__month=hoy.month
    ).order_by('-fecha_de_ingreso')

    context = {
        'altas': altas_mes_actual
    }
    return render(request, 'planilla/altas_lista.html', context)

import json
from django.shortcuts import render
from .models import Planilla  # Ajusta según tu modelo real

def arbol(request):
    # Lista de planteles para el selector
    planteles = Planilla.objects.values_list('adscripcion', flat=True).distinct()
    adscripcion = request.GET.get('adscripcion')
    tree_data = {}

    if adscripcion:
        empleados = Planilla.objects.filter(adscripcion=adscripcion)

        # Director: solo directivos cuyo puesto empieza con 'DIRECTOR DE PLANTEL'
        director = empleados.filter(
            puesto__istartswith='DIRECTOR DE PLANTEL',
            tipo__iexact='Directivo'
        ).first()

        director_node = {
            "name": f"{director.puesto}\n{director.nombre}" if director else "Sin Director",
            "children": []
        }

        # Coordinadores
        coord_admins = empleados.filter(puesto__icontains='COORDINADOR ADMINISTRATIVO')
        coord_acads = empleados.filter(puesto__icontains='COORDINADOR ACADEMICO')

        # Nodo de coordinadores (nivel superior)
        coordinadores_node = {"name": "Coordinadores", "children": []}

        if coord_admins.exists():
            coordinadores_node["children"].append({
                "name": "Administrativos",
                "children": [{"name": f"{c.puesto}\n{c.nombre}"} for c in coord_admins]
            })

        if coord_acads.exists():
            coordinadores_node["children"].append({
                "name": "Académicos",
                "children": [{"name": f"{c.puesto}\n{c.nombre}"} for c in coord_acads]
            })

        if coordinadores_node["children"]:
            director_node["children"].append(coordinadores_node)

        # Empleados regulares por tipo
        administrativos = empleados.filter(tipo__iexact='Administrativo')\
            .exclude(puesto__icontains='COORDINADOR')\
            .exclude(puesto__istartswith='DIRECTOR')

        docentes = empleados.filter(tipo__iexact='Docente')

        if administrativos.exists():
            director_node["children"].append({
                "name": "Administrativos",
                "label": {"position": "left", "align": "right"},
                "collapsed": False,
                "children": [{"name": f"{o.puesto}\n{o.nombre}"} for o in administrativos]
            })

        if docentes.exists():
            director_node["children"].append({
                "name": "Docentes",
                "label": {"position": "right", "align": "left"},
                "collapsed": False,
                "children": [{"name": f"{o.puesto}\n{o.nombre}"} for o in docentes]
            })

        # Árbol final
        tree_data = {"name": adscripcion, "children": [director_node]}

    return render(request, 'planilla/organigrama.html', {
        "planteles": planteles,
        "tree_data": json.dumps(tree_data)  # JSON válido para ECharts
    })


from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection

def quincenas(request):
    if request.method == 'POST':
        clave = request.POST.get('clave')

        # Obtener datos planilla
        with connection.cursor() as cursor:
            cursor.execute("SELECT clave, nombre, adscripcion, departamento FROM planilla3 WHERE clave = %s", [clave])
            row = cursor.fetchone()
            planilla = {
                'clave': row[0],
                'nombre': row[1],
                'adscripcion': row[2],
                'departamento': row[3],
            } if row else None

        # Obtener quincenas sin limpieza ni filtrado
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM quincenas_pago WHERE clave = %s", [clave])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        quincenas_list = [list(r) for r in rows]

        return JsonResponse({
            'planilla': planilla,
            'columns': columns,
            'quincenas': quincenas_list,
        })

    return render(request, 'planilla/quincenas_24.html')
    
from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection

def quincenasf(request):
    if request.method == 'POST':
        clave = request.POST.get('clave', '').strip()

        with connection.cursor() as cursor:
            cursor.execute("SELECT clave, nombre, adscripcion, departamento FROM planilla3 WHERE clave = %s", [clave])
            row = cursor.fetchone()
            planilla = {
                'clave': row[0],
                'nombre': row[1],
                'adscripcion': row[2],
                'departamento': row[3],
            } if row else None

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM quincenas_pago WHERE clave = %s", [clave])
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

        if rows:
            transposed = list(zip(*rows))
            cleaned_columns = []
            cleaned_transposed = []

            for col_name, col_values in zip(columns, transposed):
                clean_values = []
                exclude_column = True

                for v in col_values:
                    if isinstance(v, str) and v.strip() == "#N/D":
                        clean_values.append("")
                    else:
                        clean_values.append(v)
                        if v not in [None, '', "#N/D"]:
                            exclude_column = False

                if col_name == 'clave' or not exclude_column:
                    cleaned_columns.append(col_name)
                    cleaned_transposed.append(clean_values)

            cleaned_rows = list(zip(*cleaned_transposed))
            quincenas_list = [list(r) for r in cleaned_rows]
        else:
            cleaned_columns = []
            quincenas_list = []

        return JsonResponse({
            'planilla': planilla,
            'columns': cleaned_columns,
            'quincenas': quincenas_list,
        })

    return render(request, 'planilla/quincenas_f.html')

    
from django.shortcuts import render, redirect
from django.db import connection
from django.urls import reverse
from django.contrib import messages

def planilla_baja(request):
    trabajador = None
    if request.method == 'POST':
        clave = request.POST.get('clave')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT clave, nombre, adscripcion, departamento, puesto, rfc, curp
                FROM planilla3 WHERE clave = %s
            """, [clave])
            row = cursor.fetchone()
            if row:
                trabajador = {
                    'clave': row[0],
                    'nombre': row[1],
                    'adscripcion': row[2],
                    'departamento': row[3],
                    'puesto': row[4],
                    'rfc': row[5],
                    'curp': row[6],
                }
            else:
                messages.error(request, "No se encontró al trabajador con esa clave.")
    return render(request, 'planilla/planilla_baja.html', {'trabajador': trabajador})

def dar_de_baja(request, clave):
    if request.method == 'POST':
        motivo = request.POST.get('motivo', '')
        usuario = request.user.username if request.user.is_authenticated else 'admin'
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO bajas (clave, motivo, usuario_que_baja)
                VALUES (%s, %s, %s)
            """, [clave, motivo, usuario])
        messages.success(request, "Trabajador dado de baja correctamente.")
        return redirect(reverse('planilla_baja'))

from django.shortcuts import render
from django.db import connection
from django.contrib import messages

from django.shortcuts import render
from django.db import connection

def planilla_bajas_lista(request):
    trabajadores = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.clave, p.nombre, p.adscripcion, p.departamento, p.puesto, p.rfc, p.curp
            FROM planilla3 p
            WHERE EXISTS (
                SELECT 1 FROM bajas b WHERE b.clave::text = p.clave::text
            )
            ORDER BY p.adscripcion, p.nombre
        """)
        rows = cursor.fetchall()
        for row in rows:
            trabajadores.append({
                'clave': row[0],
                'nombre': row[1],
                'adscripcion': row[2],
                'departamento': row[3],
                'puesto': row[4],
                'rfc': row[5],
                'curp': row[6],
            })
    return render(request, 'planilla/planilla_bajas_lista.html', {'trabajadores': trabajadores})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import BajasExpedientes
from django.views.decorators.csrf import csrf_exempt
import json

def bajas_expedientes_lista(request):
    expedientes = BajasExpedientes.objects.all().values(
        'id', 'clave', 'nombre', 'departamento', 'puesto', 'anaquel', 'ubicacion'
    )
    data = list(expedientes)
    return JsonResponse({'data': data})

from django.views.decorators.csrf import csrf_exempt  # solo si decides usarlo

def bajas_expedientes_actualizar(request, expediente_id):
    if request.method == 'POST':
        expediente = get_object_or_404(BajasExpedientes, id=expediente_id)
        import json
        data = json.loads(request.body)

        expediente.clave = data.get('clave', expediente.clave)
        expediente.nombre = data.get('nombre', expediente.nombre)
        expediente.departamento = data.get('departamento', expediente.departamento)
        expediente.puesto = data.get('puesto', expediente.puesto)
        expediente.anaquel = data.get('anaquel', expediente.anaquel)
        expediente.ubicacion = data.get('ubicacion', expediente.ubicacion)

        expediente.fecha_baja = data.get('fecha_baja') or None
        expediente.caja = data.get('caja')
        expediente.observaciones = data.get('observaciones')
        expediente.prestado = data.get('prestado', False)
        expediente.fecha_prestamo = data.get('fecha_prestamo') or None
        expediente.prestado_a = data.get('prestado_a')
        expediente.fecha_devolucion = data.get('fecha_devolucion') or None
        expediente.devuelto = data.get('devuelto', False)

        expediente.save()
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
        
def bajas_expedientes_view(request):
    return render(request, 'planilla/bajas_expedientes.html')
    
from django.http import JsonResponse, Http404

def bajas_expedientes_obtener(request, expediente_id):
    try:
        expediente = BajasExpedientes.objects.values(
            'id', 'clave', 'nombre', 'departamento', 'puesto',
            'anaquel', 'ubicacion', 'fecha_baja', 'caja', 'observaciones'
        ).get(id=expediente_id)

        # Si fecha_baja es None, enviar como '', para evitar problemas en el input date
        expediente['fecha_baja'] = expediente['fecha_baja'].isoformat() if expediente['fecha_baja'] else ''

        return JsonResponse(expediente)
    except BajasExpedientes.DoesNotExist:
        raise Http404("Expediente no encontrado")

from django.shortcuts import render, redirect
from .forms import MovimientoPlazaForm

from django.shortcuts import render
from .models import MovimientoPlaza

from django.shortcuts import render
from .models import MovimientoPlaza

def lista_movimientos_plaza(request):
    lista_movimientos_plaza = MovimientoPlaza.objects.all().order_by('-fecha_movimiento', '-secuencial')
    return render(request, 'planilla/lista_movimientos_plaza.html', {'lista_movimientos_plaza': lista_movimientos_plaza})
    
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
from django.views.decorators.csrf import csrf_exempt

def beneficiarios_trabajador_view(request):
    """Retorna el HTML de búsqueda de beneficiarios"""
    return render(request, 'planilla/beneficiarios_trabajador.html')

@csrf_exempt
def beneficiarios_trabajador_json(request):
    """Retorna los datos en JSON para DataTable (GET = todos, POST = filtrado por clave)"""
    with connection.cursor() as cursor:
        if request.method == 'GET':
            cursor.execute("""
                SELECT 
                    p.nombre AS nombre_trabajador, p.departamento, p.puesto, p.clave, p.sindicato,
                    b.nombre_beneficiario, b.banco, b.cuenta_deposito,
                    b.porcentaje_1, b.porcentaje_2, b.porcentaje_3, b.porcentaje_4,
                    b.cantidad_fija, b.notas_1, b.notas_2, b.notas_3, b.notas_4,
                    b.no_expediente, b.no_oficio, b.fecha_documento, b.lugar_documento,
                    b.resolucion, b.porcentaje_oscar
                FROM planilla2 p
                INNER JOIN beneficiarios b ON p.clave = b.clave
            """)
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return JsonResponse({"data": data})

        elif request.method == 'POST':
            clave = request.POST.get('clave')
            # Verificar trabajador
            cursor.execute("SELECT COUNT(*) FROM planilla2 WHERE clave = %s", [clave])
            if cursor.fetchone()[0] == 0:
                return JsonResponse({"data": [], "mensaje": "La clave no existe en trabajadores."})
            
            # Verificar beneficiarios
            cursor.execute("SELECT COUNT(*) FROM beneficiarios WHERE clave = %s", [clave])
            if cursor.fetchone()[0] == 0:
                return JsonResponse({"data": [], "mensaje": "No se encontraron datos en beneficiarios para la clave ingresada."})

            cursor.execute("""
                SELECT 
                    p.nombre AS nombre_trabajador, p.departamento, p.puesto, p.clave, p.sindicato,
                    b.nombre_beneficiario, b.banco, b.cuenta_deposito,
                    b.porcentaje_1, b.porcentaje_2, b.porcentaje_3, b.porcentaje_4,
                    b.cantidad_fija, b.notas_1, b.notas_2, b.notas_3, b.notas_4,
                    b.no_expediente, b.no_oficio, b.fecha_documento, b.lugar_documento,
                    b.resolucion, b.porcentaje_oscar
                FROM planilla2 p
                INNER JOIN beneficiarios b ON p.clave = b.clave
                WHERE p.clave = %s
            """, [clave])
            columns = [col[0] for col in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return JsonResponse({"data": data, "mensaje": ""})

from django.shortcuts import render
from .models import PersonalAcumulado

def cargar_personal_acumulado(request):
    personal = PersonalAcumulado.objects.all().order_by('clave')
    return render(request, 'planilla/personal_acumulado.html', {'personal': personal})
    
# views.py

def subir_archivo(request):
    if request.method == 'POST':
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.subido_por = request.COOKIES.get('usuario', 'anónimo')
            archivo.save()
            return redirect('lista_archivos')
    else:
        form = ArchivoForm()
    return render(request, 'planilla/subir_archivo.html', {'form': form})   
    
def lista_archivos(request):
    archivos = ArchivoSubido.objects.all().order_by('-fecha_subida')
    return render(request, 'planilla/lista_archivos.html', {'archivos': archivos})   
    
def eliminar_archivo(request, archivo_id):
    archivo = get_object_or_404(ArchivoSubido, id=archivo_id)

    if request.method == "POST":
        ruta_archivo = archivo.archivo.path
        archivo.delete()  # Esto elimina también el archivo físico si `upload_to` es usado correctamente
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
        messages.success(request, "Archivo eliminado correctamente.")
    
    return redirect('lista_archivos')
    
from django.shortcuts import render
from django.db import connection

def personal_sindicalizado_view(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT p.clave, p.nombre, p.departamento, p.puesto, p.fecha_de_ingreso
            FROM planilla3 p
            INNER JOIN personal_sindicalizado s ON p.clave = s.numero
            ORDER BY p.nombre;
        """)
        filas = cursor.fetchall()

    context = {
        'datos': filas,
    }
    return render(request, 'planilla/personal_sindicalizado.html', context)

import os
from django.shortcuts import render
from django.conf import settings

def listar_archivos(request):
    ruta_carpeta = os.path.join(settings.MEDIA_ROOT, 'oscart')
    archivos_info = []

    if os.path.exists(ruta_carpeta):
        for archivo in os.listdir(ruta_carpeta):
            ruta_archivo = os.path.join(ruta_carpeta, archivo)
            if os.path.isfile(ruta_archivo):
                tamaño_kb = round(os.path.getsize(ruta_archivo) / 1024, 2)
                archivos_info.append({
                    'nombre': archivo,
                    'tamaño_kb': tamaño_kb
                })

    contexto = {
        'archivos': archivos_info,
        'total': len(archivos_info)
    }
    return render(request, 'planilla/lista_archivos.html', contexto)

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.urls import reverse

@csrf_exempt
def eliminar_archivo(request):
    if request.method == 'POST':
        nombre_archivo = request.POST.get('archivo')
        ruta_archivo = os.path.join(settings.MEDIA_ROOT, 'oscart', nombre_archivo)

        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

    return HttpResponseRedirect(reverse('lista_archivos'))    
    
from django.shortcuts import render

def condiciones_generales(request):
    return render(request, 'planilla/condiciones_generales.html')  
    
from django.shortcuts import render

# Vista para el mapa de CECYTEV
def mapa_cecytev(request):
    # No necesitamos pasar datos, todo está en JS
    return render(request, 'planilla/mapa.html')    
    
from django.shortcuts import render
from .models import Planilla, Convenio


def convenio_planilla_view(request):
    # Obtener todos los convenios
    convenios_qs = Convenio.objects.all()
    convenios_dict = {c.clave: c for c in convenios_qs}

    # Filtrar solo los trabajadores que tienen convenio
    claves_convenio = convenios_dict.keys()
    planillas = Planilla.objects.filter(clave__in=claves_convenio)

    # Construir datos combinados
    datos = []
    for p in planillas:
        c = convenios_dict.get(p.clave)
        datos.append({
            'clave': p.clave,
            'nombre': p.nombre,
            'adscripcion': p.adscripcion,
            'puesto': p.puesto,
            'funcion_en_plantel': c.funcion_en_plantel if c else '',
            'oficio': c.oficio if c else '',
        })

    return render(request, 'planilla/convenio_planilla.html', {'datos': datos})

