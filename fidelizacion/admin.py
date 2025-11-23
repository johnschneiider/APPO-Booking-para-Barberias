"""
Admin para el sistema de fidelización
"""
from django.contrib import admin
from .models import MensajeFidelizacion, TipoMensaje, EstadoMensaje


@admin.register(MensajeFidelizacion)
class MensajeFidelizacionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'tipo', 'destinatario', 'estado', 
        'fecha_programada', 'fecha_envio', 'intentos_envio'
    ]
    list_filter = ['tipo', 'estado', 'fecha_programada']
    search_fields = ['destinatario__username', 'destinatario__email', 'mensaje']
    readonly_fields = ['id', 'fecha_creacion', 'fecha_modificacion', 'fecha_envio']
    date_hierarchy = 'fecha_programada'
    
    fieldsets = (
        ('Información General', {
            'fields': ('id', 'tipo', 'estado', 'destinatario', 'reserva')
        }),
        ('Programación', {
            'fields': ('fecha_programada', 'fecha_envio')
        }),
        ('Contenido', {
            'fields': ('mensaje',)
        }),
        ('Metadatos', {
            'fields': ('intentos_envio', 'max_intentos', 'error_mensaje', 
                      'fecha_creacion', 'fecha_modificacion')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('destinatario', 'reserva')

