from django.db import models

class Planilla(models.Model):
    clave = models.TextField(primary_key=True)  # PK actual en planilla2
    nombre = models.TextField(blank=False, null=False)
    adscripcion = models.TextField(blank=True, null=True)
    departamento = models.TextField(blank=True, null=True)
    puesto = models.TextField(blank=True, null=True)
    rfc = models.TextField(blank=True, null=True)
    curp = models.TextField(blank=True, null=True)
    nss = models.TextField(blank=True, null=True)
    fecha_de_ingreso = models.DateField(blank=True, null=True)
    sindicato = models.TextField(blank=True, null=True)
    cp = models.CharField(max_length=10, blank=True, null=True)
    banco = models.TextField(blank=True, null=True)
    cuenta = models.TextField(blank=True, null=True)
    salario_base = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    situacion_adm = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)
    zona = models.IntegerField(blank=True, null=True)
    no = models.BigIntegerField(unique=True)  # ya existe como BIGSERIAL NOT NULL en planilla2

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.no is None:
            raise ValueError("El campo 'no' no puede ser None")

    class Meta:
        db_table = 'planilla2'   # CAMBIA AQUI

class Adscripcion(models.Model):
    nombre = models.CharField(max_length=100)
    clave_adscripcion = models.CharField(max_length=20, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    zona = models.CharField(max_length=10, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    activo = models.CharField(max_length=100, default='1')  # o el valor que prefieras
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'adscripcion'  # Esta apunta a tabla 'adscripcion'

class Plazas(models.Model):
    codigo = models.CharField(max_length=20)
    denominacion = models.CharField(max_length=255)
    zona_economica = models.CharField(max_length=10)
    nivel_salarial = models.CharField(max_length=10)
    plazas = models.IntegerField()
    horas = models.IntegerField()
    
    class Meta:
        db_table = 'plazas'  # Esta apunta a tabla 'plazas'

class Directorio(models.Model):
    cct = models.TextField(blank=True, null=True)
    clave_adscripcion = models.TextField(blank=True, null=True)
    nombre = models.TextField(blank=True, null=True)
    nombre_departamento_corto = models.TextField(blank=True, null=True)
    area = models.TextField(blank=True, null=True)
    calle_numero = models.TextField(blank=True, null=True)
    colonia_zona = models.TextField(blank=True, null=True)
    codigo_postal = models.TextField(blank=True, null=True)
    ciudad_estado = models.TextField(blank=True, null=True)
    telefono_plantel = models.TextField(blank=True, null=True)
    telefono_plantel2 = models.TextField(blank=True, null=True)
    extension_depto = models.TextField(blank=True, null=True)
    extensiones_aux = models.TextField(blank=True, null=True)
    director = models.TextField(blank=True, null=True)
    coordinador_administrativo = models.TextField(blank=True, null=True)
    coordinador_academico = models.TextField(blank=True, null=True)
    municipio = models.CharField(max_length=255, blank=True, null=True)
    zona = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    activo = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adscripcion'

    def __str__(self):
        return self.nombre
        
class Usuario(models.Model):
    contrasena = models.CharField(max_length=128)
    ultimo_ingreso = models.DateTimeField(blank=True, null=True)
    autorizacion = models.CharField(max_length=20)
    nombre_usuario = models.CharField(max_length=150, unique=True)
    email = models.CharField(max_length=254, unique=True, blank=True, null=True)
    estatus = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.nombre_usuario
        
from django.db import models

class BajasExpedientes(models.Model):
    clave = models.CharField(max_length=20)
    nombre = models.CharField(max_length=150)
    departamento = models.CharField(max_length=100)
    puesto = models.CharField(max_length=100)
    anaquel = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=100)
    fecha_baja = models.DateField(null=True, blank=True)
    caja = models.CharField(max_length=20, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    prestado = models.BooleanField(default=False)
    fecha_prestamo = models.DateField(null=True, blank=True)
    prestado_a = models.CharField(max_length=100, null=True, blank=True)
    fecha_devolucion = models.DateField(null=True, blank=True)
    devuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.clave} - {self.nombre}"      

    class Meta:
        db_table = 'bajas_expedientes'        