from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuarioPersonalizado, RateLimitConfig, EmailTracking

class UsuarioAdmin(UserAdmin):
    model = UsuarioPersonalizado
    list_display = ['username', 'email', 'tipo', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('tipo', 'telefono',)}),
    )

admin.site.register(UsuarioPersonalizado, UsuarioAdmin)

@admin.register(RateLimitConfig)
class RateLimitConfigAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'clave', 'limite', 'activo', 'fecha_modificacion']
    list_filter = ['activo', 'fecha_creacion', 'fecha_modificacion']
    search_fields = ['nombre', 'clave', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'clave', 'limite', 'activo')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('nombre')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Limpiar caché de rate limiting después de cambios
        from django.core.cache import cache
        cache.clear()

@admin.register(EmailTracking)
class EmailTrackingAdmin(admin.ModelAdmin):
    list_display = ['subject', 'recipient', 'estado', 'proveedor', 'enviado_en', 'negocio']
    list_filter = ['estado', 'proveedor', 'enviado_en', 'negocio']
    search_fields = ['subject', 'recipient', 'from_email', 'message_id']
    readonly_fields = ['enviado_en', 'entregado_en', 'abierto_en', 'clickeado_en', 'tiempo_entrega', 'tiempo_apertura']
    ordering = ['-enviado_en']
    
    fieldsets = (
        ('Información del Email', {
            'fields': ('subject', 'recipient', 'from_email', 'message_id', 'template_name')
        }),
        ('Tracking', {
            'fields': ('estado', 'proveedor', 'enviado_en', 'entregado_en', 'abierto_en', 'clickeado_en')
        }),
        ('Métricas', {
            'fields': ('tiempo_entrega', 'tiempo_apertura'),
            'classes': ('collapse',)
        }),
        ('Relaciones', {
            'fields': ('usuario', 'negocio'),
            'classes': ('collapse',)
        }),
        ('Información Adicional', {
            'fields': ('context_data', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    def tiempo_entrega(self, obj):
        """Muestra el tiempo de entrega de forma legible"""
        if obj.tiempo_entrega:
            total_seconds = obj.tiempo_entrega.total_seconds()
            if total_seconds < 60:
                return f"{int(total_seconds)}s"
            elif total_seconds < 3600:
                return f"{int(total_seconds // 60)}m {int(total_seconds % 60)}s"
            else:
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        return "-"
    
    def tiempo_apertura(self, obj):
        """Muestra el tiempo de apertura de forma legible"""
        if obj.tiempo_apertura:
            total_seconds = obj.tiempo_apertura.total_seconds()
            if total_seconds < 60:
                return f"{int(total_seconds)}s"
            elif total_seconds < 3600:
                return f"{int(total_seconds // 60)}m {int(total_seconds % 60)}s"
            else:
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        return "-"
    
    tiempo_entrega.short_description = 'Tiempo Entrega'
    tiempo_apertura.short_description = 'Tiempo Apertura'
