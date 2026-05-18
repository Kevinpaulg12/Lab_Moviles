from django.urls import path
from . import views

app_name = 'solicitudes'

urlpatterns = [
    path('', views.home, name='home'),
    path('solicitud/crear/', views.crear_solicitud, name='crear_solicitud'),
    path('solicitud/mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('admin/solicitudes/', views.lista_solicitudes, name='lista_solicitudes'),
    path('admin/solicitud/<int:solicitud_id>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('admin/solicitud/<int:solicitud_id>/aprobar/', views.aprobar_solicitud, name='aprobar_solicitud'),
    path('admin/solicitud/<int:solicitud_id>/rechazar/', views.rechazar_solicitud, name='rechazar_solicitud'),
    path('admin/solicitud/<int:solicitud_id>/asignar/', views.asignar_responsable, name='asignar_responsable'),
    path('responsable/asignaciones/', views.mis_asignaciones, name='mis_asignaciones'),
    path('responsable/asignacion/<int:asignacion_id>/completar/', views.completar_asignacion, name='completar_asignacion'),
    path('ajax/materias-por-carrera/<int:carrera_id>/', views.ajax_materias_por_carrera, name='ajax_materias'),
    path('ajax/cursos-por-materia/<int:materia_id>/', views.ajax_cursos_por_materia, name='ajax_cursos'),
]