from django.urls import path
from . import views

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
]