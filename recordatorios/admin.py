"""
Admin para la app de recordatorios
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Recordatorio, ConfiguracionRecordatorio, PlantillaRecordatorio,
    HistorialRecordatorio, TipoRecordatorio, EstadoRecordatorio, CanalNotificacion
)

@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = [
        'id_corto', 'tipo', 'destinatario', 'estado', 'fecha_programada',
        'canales_display', 'prioridad', 'reintentos_info'
    ]
    list_filter = [
        'estado', 'tipo', 'fecha_programada', 'fecha_creacion',
        'prioridad', 'reintentos_actuales'
    ]
    search_fields = [
        'destinatario__username', 'destinatario__email', 'asunto',
        'mensaje', 'id'
    ]
    readonly_fields = [
        'id', 'fecha_creacion', 'fecha_modificacion', 'fecha_envio',
        'fecha_entrega', 'reintentos_actuales', 'canales_enviados'
    ]
    ordering = ['-fecha_programada', '-prioridad']
    date_hierarchy = 'fecha_programada'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'tipo', 'destinatario', 'estado', 'prioridad')
        }),
        ('Contenido', {
            'fields': ('asunto', 'mensaje', 'mensaje_html', 'template_name', 'contexto_template')
        }),
        ('Programación', {
            'fields': ('fecha_programada', 'fecha_envio', 'fecha_entrega')
        }),
        ('Canales', {
            'fields': ('canales_habilitados', 'canales_enviados')
        }),
        ('Configuración', {
            'fields': ('reintentos_maximos', 'reintentos_actuales', 'contenido_relacionado')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion', 'creado_por'),
            'classes': ('collapse',)
        }),
    )
    
    def id_corto(self, obj):
        """Muestra solo los primeros 8 caracteres del UUID"""
        return str(obj.id)[:8]
    id_corto.short_description = 'ID'
    
    def canales_display(self, obj):
        """Muestra los canales de forma legible"""
        if not obj.canales_habilitados:
            return "-"
        
        canales = []
        for canal in obj.canales_habilitados:
            if canal in obj.canales_enviados:
                estado = obj.canales_enviados[canal].get('estado', 'desconocido')
                if estado == 'enviado':
                    canales.append(f"<span style='color: green;'>{canal} ✓</span>")
                elif estado == 'entregado':
                    canales.append(f"<span style='color: blue;'>{canal} ✓✓</span>")
                elif estado == 'fallido':
                    canales.append(f"<span style='color: red;'>{canal} ✗</span>")
                else:
                    canales.append(f"<span style='color: orange;'>{canal} ?</span>")
            else:
                canales.append(f"<span style='color: gray;'>{canal} ⏳</span>")
        
        return mark_safe(" ".join(canales))
    canales_display.short_description = 'Canales'
    
    def reintentos_info(self, obj):
        """Muestra información de reintentos"""
        if obj.reintentos_actuales == 0:
            return f"0/{obj.reintentos_maximos}"
        elif obj.reintentos_actuales >= obj.reintentos_maximos:
            return format_html(
                '<span style="color: red;">{}/{} (Agotado)</span>',
                obj.reintentos_actuales, obj.reintentos_maximos
            )
        else:
            return format_html(
                '<span style="color: orange;">{}/{} (Pendiente)</span>',
                obj.reintentos_actuales, obj.reintentos_maximos
            )
    reintentos_info.short_description = 'Reintentos'
    
    def contenido_relacionado(self, obj):
        """Muestra el contenido relacionado con enlaces"""
        if obj.content_type and obj.object_id:
            try:
                objeto = obj.content_type.get_object_for_this_type(id=obj.object_id)
                if hasattr(objeto, 'get_absolute_url'):
                    url = objeto.get_absolute_url()
                    return format_html('<a href="{}">{}</a>', url, str(objeto))
                else:
                    return str(objeto)
            except:
                return f"{obj.content_type} #{obj.object_id}"
        return "-"
    contenido_relacionado.short_description = 'Contenido Relacionado'
    
    actions = ['reprogramar_recordatorios', 'cancelar_recordatorios', 'forzar_envio']
    
    def reprogramar_recordatorios(self, request, queryset):
        """Reprograma recordatorios fallidos"""
        count = 0
        for recordatorio in queryset.filter(estado=EstadoRecordatorio.FALLIDO):
            if recordatorio.programar_reintento('email', delay_minutos=30):
                count += 1
        
        self.message_user(
            request,
            f"{count} recordatorios reprogramados exitosamente."
        )
    reprogramar_recordatorios.short_description = "Reprogramar recordatorios fallidos"
    
    def cancelar_recordatorios(self, request, queryset):
        """Cancela recordatorios pendientes"""
        count = queryset.filter(estado=EstadoRecordatorio.PENDIENTE).update(
            estado=EstadoRecordatorio.CANCELADO
        )
        
        self.message_user(
            request,
            f"{count} recordatorios cancelados exitosamente."
        )
    cancelar_recordatorios.short_description = "Cancelar recordatorios pendientes"
    
    def forzar_envio(self, request, queryset):
        """Fuerza el envío inmediato de recordatorios"""
        from .services import servicio_recordatorios
        
        count = 0
        for recordatorio in queryset.filter(estado=EstadoRecordatorio.PENDIENTE):
            try:
                resultado = servicio_recordatorios._procesar_recordatorio(recordatorio)
                if resultado['enviado']:
                    count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Error enviando recordatorio {recordatorio.id}: {e}",
                    level='ERROR'
                )
        
        self.message_user(
            request,
            f"{count} recordatorios enviados exitosamente."
        )
    forzar_envio.short_description = "Forzar envío inmediato"

@admin.register(ConfiguracionRecordatorio)
class ConfiguracionRecordatorioAdmin(admin.ModelAdmin):
    list_display = [
        'tipo', 'anticipacion_display', 'canales_habilitados', 
        'reintentos_maximos', 'activo', 'fecha_modificacion'
    ]
    list_filter = ['activo', 'fecha_creacion', 'fecha_modificacion']
    search_fields = ['tipo']
    ordering = ['tipo']
    
    fieldsets = (
        ('Configuración Básica', {
            'fields': ('tipo', 'activo')
        }),
        ('Timing', {
            'fields': ('anticipacion_horas', 'anticipacion_minutos')
        }),
        ('Canales', {
            'fields': ('canales_habilitados',)
        }),
        ('Templates', {
            'fields': ('template_email', 'template_whatsapp', 'template_sms'),
            'classes': ('collapse',)
        }),
        ('Reintentos', {
            'fields': ('reintentos_maximos', 'delay_reintentos_minutos')
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def anticipacion_display(self, obj):
        """Muestra la anticipación de forma legible"""
        if obj.anticipacion_horas == 0 and obj.anticipacion_minutos == 0:
            return "Inmediato"
        elif obj.anticipacion_horas == 0:
            return f"{obj.anticipacion_minutos} minutos antes"
        elif obj.anticipacion_minutos == 0:
            return f"{obj.anticipacion_horas} horas antes"
        else:
            return f"{obj.anticipacion_horas}h {obj.anticipacion_minutos}m antes"
    anticipacion_display.short_description = 'Anticipación'
    
    def canales_habilitados(self, obj):
        """Muestra los canales de forma legible"""
        if not obj.canales_habilitados:
            return "-"
        
        canales = []
        for canal in obj.canales_habilitados:
            if canal == 'email':
                canales.append("📧 Email")
            elif canal == 'whatsapp':
                canales.append("📱 WhatsApp")
            elif canal == 'sms':
                canales.append("💬 SMS")
            else:
                canales.append(canal.title())
        
        return " ".join(canales)
    canales_habilitados.short_description = 'Canales'

@admin.register(PlantillaRecordatorio)
class PlantillaRecordatorioAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'tipo', 'activa', 'variables_disponibles_display',
        'creado_por', 'fecha_modificacion'
    ]
    list_filter = ['tipo', 'activa', 'fecha_creacion', 'fecha_modificacion']
    search_fields = ['nombre', 'asunto', 'mensaje_texto']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'tipo', 'activa', 'creado_por')
        }),
        ('Contenido', {
            'fields': ('asunto', 'mensaje_texto', 'mensaje_html')
        }),
        ('Variables', {
            'fields': ('variables_disponibles',),
            'description': 'Lista de variables disponibles para usar en la plantilla'
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    
    def variables_disponibles_display(self, obj):
        """Muestra las variables disponibles de forma legible"""
        if not obj.variables_disponibles:
            return "-"
        
        variables = []
        for var in obj.variables_disponibles:
            variables.append(f"<code>{{{{ {var} }}}}</code>")
        
        return mark_safe(" ".join(variables))
    variables_disponibles_display.short_description = 'Variables Disponibles'
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es nuevo
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(HistorialRecordatorio)
class HistorialRecordatorioAdmin(admin.ModelAdmin):
    list_display = [
        'recordatorio_corto', 'accion', 'canal', 'usuario_responsable',
        'fecha_accion', 'detalles_display'
    ]
    list_filter = [
        'accion', 'canal', 'fecha_accion', 'usuario_responsable'
    ]
    search_fields = [
        'recordatorio__id', 'accion', 'mensaje_error'
    ]
    ordering = ['-fecha_accion']
    readonly_fields = ['fecha_accion']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('recordatorio', 'accion', 'canal', 'usuario_responsable')
        }),
        ('Detalles', {
            'fields': ('detalles', 'mensaje_error')
        }),
        ('Timing', {
            'fields': ('fecha_accion',)
        }),
    )
    
    def recordatorio_corto(self, obj):
        """Muestra el recordatorio de forma abreviada"""
        return f"{obj.recordatorio.tipo} - {obj.recordatorio.destinatario}"
    recordatorio_corto.short_description = 'Recordatorio'
    
    def detalles_display(self, obj):
        """Muestra los detalles de forma legible"""
        if not obj.detalles:
            return "-"
        
        detalles = []
        for key, value in obj.detalles.items():
            if isinstance(value, str) and len(value) > 50:
                detalles.append(f"{key}: {value[:50]}...")
            else:
                detalles.append(f"{key}: {value}")
        
        return " | ".join(detalles)
    detalles_display.short_description = 'Detalles'

# Configuración del admin
admin.site.site_header = "APPO - Administración de Recordatorios"
admin.site.site_title = "APPO Recordatorios"
admin.site.index_title = "Panel de Control de Recordatorios"

# Nota: TipoRecordatorio, EstadoRecordatorio y CanalNotificacion son clases de choices,
# no modelos Django, por lo que no se pueden registrar en el admin
