from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PlanSuscripcion, 
    Suscripcion, 
    PagoSuscripcion, 
    BeneficioSuscripcion, 
    HistorialSuscripcion
)

@admin.register(PlanSuscripcion)
class PlanSuscripcionAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 
        'negocio', 
        'precio_mensual', 
        'destacado',
        'duracion_meses',
        'activo', 
        'fecha_creacion'
    ]
    list_filter = ['activo', 'destacado', 'negocio', 'fecha_creacion']
    search_fields = ['nombre', 'negocio__nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('negocio', 'nombre', 'descripcion', 'precio_mensual', 'activo', 'destacado')
        }),
        ('Configuración del Plan', {
            'fields': ('duracion_meses', 'limite_suscriptores', 'max_servicios_mes', 'descuento_servicios', 'prioridad_reservas')
        }),
        ('Imagen', {
            'fields': ('imagen',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('negocio')

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = [
        'cliente', 
        'plan', 
        'negocio', 
        'estado', 
        'precio_actual', 
        'fecha_inicio', 
        'dias_restantes_display',
        'servicios_utilizados'
    ]
    list_filter = [
        'estado', 
        'negocio', 
        'plan', 
        'renovacion_automatica', 
        'fecha_inicio', 
        'fecha_creacion'
    ]
    search_fields = [
        'cliente__email', 
        'cliente__first_name', 
        'cliente__last_name', 
        'negocio__nombre', 
        'plan__nombre'
    ]
    readonly_fields = [
        'fecha_creacion', 
        'fecha_actualizacion', 
        'servicios_utilizados_mes', 
        'ultimo_reset_mes'
    ]
    
    fieldsets = (
        ('Información de Suscripción', {
            'fields': ('cliente', 'plan', 'negocio', 'estado')
        }),
        ('Fechas y Estado', {
            'fields': ('fecha_inicio', 'fecha_fin', 'fecha_cancelacion')
        }),
        ('Información de Pago', {
            'fields': ('precio_actual', 'moneda')
        }),
        ('Contadores', {
            'fields': ('servicios_utilizados_mes', 'ultimo_reset_mes'),
            'classes': ('collapse',)
        }),
        ('Configuración', {
            'fields': ('renovacion_automatica', 'notificar_antes_renovacion')
        }),
        ('Metadatos', {
            'fields': ('notas', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activar_suscripciones', 'cancelar_suscripciones', 'renovar_suscripciones']
    
    def dias_restantes_display(self, obj):
        dias = obj.dias_restantes
        if dias is None:
            return "Sin fecha de fin"
        elif dias == 0:
            return format_html('<span style="color: red;">Vence hoy</span>')
        elif dias <= 7:
            return format_html(f'<span style="color: orange;">{dias} días</span>')
        else:
            return f"{dias} días"
    dias_restantes_display.short_description = 'Días Restantes'
    
    def servicios_utilizados(self, obj):
        if obj.plan.es_ilimitado:
            return "Ilimitado"
        return f"{obj.servicios_utilizados_mes}/{obj.plan.max_servicios_mes}"
    servicios_utilizados.short_description = 'Servicios Utilizados'
    
    def activar_suscripciones(self, request, queryset):
        for suscripcion in queryset:
            if suscripcion.estado == 'pendiente_pago':
                suscripcion.estado = 'activa'
                suscripcion.save()
        self.message_user(request, f"{queryset.count()} suscripciones activadas")
    activar_suscripciones.short_description = "Activar suscripciones seleccionadas"
    
    def cancelar_suscripciones(self, request, queryset):
        for suscripcion in queryset:
            suscripcion.cancelar("Cancelada desde admin")
        self.message_user(request, f"{queryset.count()} suscripciones canceladas")
    cancelar_suscripciones.short_description = "Cancelar suscripciones seleccionadas"
    
    def renovar_suscripciones(self, request, queryset):
        renovadas = 0
        for suscripcion in queryset:
            if suscripcion.renovar():
                renovadas += 1
        self.message_user(request, f"{renovadas} suscripciones renovadas")
    renovar_suscripciones.short_description = "Renovar suscripciones seleccionadas"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('cliente', 'plan', 'negocio')

@admin.register(PagoSuscripcion)
class PagoSuscripcionAdmin(admin.ModelAdmin):
    list_display = [
        'referencia_pago', 
        'suscripcion', 
        'monto', 
        'moneda', 
        'estado', 
        'metodo_pago', 
        'fecha_vencimiento',
        'esta_vencido_display'
    ]
    list_filter = [
        'estado', 
        'metodo_pago', 
        'moneda', 
        'fecha_creacion', 
        'fecha_pago'
    ]
    search_fields = [
        'referencia_pago', 
        'suscripcion__cliente__email',
        'suscripcion__negocio__nombre'
    ]
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('suscripcion', 'monto', 'moneda', 'metodo_pago')
        }),
        ('Estado y Fechas', {
            'fields': ('estado', 'fecha_vencimiento', 'fecha_pago')
        }),
        ('Transacción', {
            'fields': ('referencia_pago', 'descripcion')
        }),
        ('Metadatos', {
            'fields': ('notas', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['marcar_completados', 'marcar_fallidos']
    
    def esta_vencido_display(self, obj):
        if obj.esta_vencido:
            return format_html('<span style="color: red;">Vencido</span>')
        return format_html('<span style="color: green;">Vigente</span>')
    esta_vencido_display.short_description = 'Estado Vencimiento'
    
    def marcar_completados(self, request, queryset):
        for pago in queryset:
            if pago.estado == 'pendiente':
                pago.marcar_completado()
        self.message_user(request, f"{queryset.count()} pagos marcados como completados")
    marcar_completados.short_description = "Marcar pagos como completados"
    
    def marcar_fallidos(self, request, queryset):
        queryset.update(estado='fallido')
        self.message_user(request, f"{queryset.count()} pagos marcados como fallidos")
    marcar_fallidos.short_description = "Marcar pagos como fallidos"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('suscripcion__cliente', 'suscripcion__negocio')

@admin.register(BeneficioSuscripcion)
class BeneficioSuscripcionAdmin(admin.ModelAdmin):
    list_display = ['descripcion', 'plan', 'orden', 'activo']
    list_filter = ['activo', 'plan__negocio', 'fecha_creacion']
    search_fields = ['descripcion', 'plan__nombre']
    
    fieldsets = (
        ('Información del Beneficio', {
            'fields': ('plan', 'descripcion', 'activo', 'orden')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('plan__negocio')

@admin.register(HistorialSuscripcion)
class HistorialSuscripcionAdmin(admin.ModelAdmin):
    list_display = [
        'suscripcion', 
        'accion', 
        'fecha', 
        'usuario_responsable'
    ]
    list_filter = ['accion', 'fecha', 'suscripcion__negocio']
    search_fields = [
        'suscripcion__cliente__email',
        'suscripcion__negocio__nombre',
        'descripcion'
    ]
    readonly_fields = ['fecha']
    
    fieldsets = (
        ('Información del Historial', {
            'fields': ('suscripcion', 'accion', 'descripcion', 'fecha')
        }),
        ('Usuario Responsable', {
            'fields': ('usuario_responsable',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'suscripcion__cliente', 
            'suscripcion__negocio', 
            'usuario_responsable'
        )
