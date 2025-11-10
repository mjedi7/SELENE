from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_usuario, name='login_usuario'),
    path('logout/', views.logout_usuario, name='logout_usuario'),    
    path('altas/nueva/', views.altas_nueva, name='altas_nueva'),
    path('plazas/', views.plazas, name='control_plazas'),
    path('', views.lista_planilla, name='planilla'),
    path('anexo-ejecucion/', views.anexo_ejecucion, name='anexo_ejecucion'),
    path('historial/', views.historial, name='historial'),
    path('debug-planteles/', views.debug_planteles),
    path('planilla/eliminar/<int:no>/', views.eliminar_registro, name='eliminar_registro'),
    path('consulta/', views.consulta, name='consulta'),
    path('estadisticas/', views.estadisticas, name='estadisticas'),
    path('debug-planteles/', views.dplanteles, name='dplanteles'),
    path('directorio/', views.directorio, name='directorio'),
    path('arbol/', views.arbol, name='arbol'),
    path('altas/lista/', views.altas_lista, name='altas_lista'),
    path('quincenas/', views.quincenas, name='quincenas'),
    path('quincenasf/', views.quincenasf, name='quincenasf'),
    path('planilla/baja/', views.planilla_baja, name='planilla_baja'),
    path('planilla/dar_de_baja/<str:clave>/', views.dar_de_baja, name='dar_de_baja'),
    path('planilla/bajas_lista_todos/', views.planilla_bajas_lista, name='planilla_bajas_lista'),
    path('bajas_expedientes/actualizar/<int:expediente_id>/', views.bajas_expedientes_actualizar, name='bajas_expedientes_actualizar'),
    path('bajas_expedientes/obtener/<int:expediente_id>/', views.bajas_expedientes_obtener, name='bajas_expedientes_obtener'),
    # HTML
    path('bajas_expedientes/', views.bajas_expedientes_view, name='bajas_expedientes'),
    # JSON
    path('bajas_expedientes/listar/', views.bajas_expedientes_lista, name='bajas_expedientes_lista'),
    path('lista_movimientos_plaza/', views.lista_movimientos_plaza, name='lista_movimientos_plaza'),
    path('beneficiarios_trabajador/', views.beneficiarios_trabajador_view, name='beneficiarios_trabajador'),
    path('beneficiarios_trabajador/datos/', views.beneficiarios_trabajador_json, name='beneficiarios_trabajador_json'),
    path('personal_acumulado/', views.cargar_personal_acumulado, name='personal_acumulado'),
    path('subir/', views.subir_archivo, name='subir_archivo'),
    path('archivos/', views.lista_archivos, name='lista_archivos'),    
    path('eliminar_archivo/<int:archivo_id>/', views.eliminar_archivo, name='eliminar_archivo'),
    path('personal_sindicalizado/', views.personal_sindicalizado_view, name='personal_sindicalizado'),
    path('listar_archivos/', views.listar_archivos, name='listar_archivos'),
    path('archivos/eliminar/', views.eliminar_archivo, name='eliminar_archivo'),
    path('condiciones-generales/', views.condiciones_generales, name='condiciones_generales'),
    path('mapa/', views.mapa_cecytev, name='mapa_cecytev'),    
    path('convenio-planilla/', views.convenio_planilla_view, name='convenio_planilla'),
    path('quincenas3/', views.buscar_quincenas, name='buscar_quincenas'),    
    path("planilla4/", views.ver_planilla, name="ver_planilla"),
    path("comparar-plazas/", views.comparar_plazas, name="comparar_plazas"),
    path("ley-estatal-servicio-civil/", views.lesc, name="lesc"),
    path('directorio/direccion/', views.directorio_direccion, name='directorio_direccion'),
    path('directorio/planteles/', views.directorio_planteles, name='directorio_planteles'),    
    path('planilla-detalle/', views.planilla_list, name='planilla_list'),
    path('planilla-detalle/<int:pk>/detalle/', views.planilla_detalle, name='planilla_detalle'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)