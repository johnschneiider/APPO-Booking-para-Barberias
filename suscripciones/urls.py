from django.urls import path
from . import views

app_name = 'suscripciones'

urlpatterns = [
    # URLs para negocios (dentro del contexto del negocio)
    path('negocio/<int:negocio_id>/planes/', views.planes_negocio, name='planes_negocio'),
    path('negocio/<int:negocio_id>/planes/crear/', views.crear_plan, name='crear_plan'),
    path('negocio/<int:negocio_id>/planes/<int:plan_id>/editar/', views.editar_plan, name='editar_plan'),
    path('negocio/<int:negocio_id>/suscripciones/', views.negocio_suscripciones, name='negocio_suscripciones'),
    path('negocio/<int:negocio_id>/dashboard/', views.dashboard_suscripciones, name='dashboard_suscripciones'),
    
    # URLs para clientes
    path('cliente/suscripciones/', views.cliente_suscripciones, name='cliente_suscripciones'),
    path('planes/disponibles/', views.planes_disponibles, name='planes_disponibles'),
    
    # URLs de API (dentro del contexto del negocio)
    path('api/negocio/<int:negocio_id>/suscripcion/<int:suscripcion_id>/detalles/', views.api_suscripcion_detalles, name='api_suscripcion_detalles'),
    path('api/negocio/<int:negocio_id>/suscripcion/<int:suscripcion_id>/renovar/', views.api_renovar_suscripcion, name='api_renovar_suscripcion'),
    path('api/negocio/<int:negocio_id>/suscripcion/<int:suscripcion_id>/recordatorio/', views.api_enviar_recordatorio, name='api_enviar_recordatorio'),
    path('api/negocio/<int:negocio_id>/plan/<int:plan_id>/detalles/', views.api_plan_detalles, name='api_plan_detalles'),
    path('api/negocio/<int:negocio_id>/plan/<int:plan_id>/editar/', views.api_editar_plan, name='api_editar_plan'),
    path('api/negocio/<int:negocio_id>/plan/<int:plan_id>/eliminar/', views.api_eliminar_plan, name='api_eliminar_plan'),
    path('api/negocio/<int:negocio_id>/plan/<int:plan_id>/toggle/', views.api_toggle_plan, name='api_toggle_plan'),
    
    # URLs de suscripción
    path('suscribirse/<int:plan_id>/', views.suscribirse_plan, name='suscribirse_plan'),
    path('cancelar/<int:suscripcion_id>/', views.cancelar_suscripcion, name='cancelar_suscripcion'),
]
