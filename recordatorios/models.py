"""
Modelos para el sistema de recordatorios de APPO
Maneja recordatorios por email, WhatsApp y SMS
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

class TipoRecordatorio(models.TextChoices):
    """Tipos de recordatorios disponibles"""
    RESERVA_CONFIRMADA = 'reserva_confirmada', 'Reserva Confirmada'
    RECORDATORIO_DIA_ANTES = 'recordatorio_dia_antes', 'Recordatorio Día Antes'
    RECORDATORIO_TRES_HORAS = 'recordatorio_tres_horas', 'Recordatorio 3 Horas Antes'
    RESERVA_CANCELADA = 'reserva_cancelada', 'Reserva Cancelada'
    RESERVA_REAGENDADA = 'reserva_reagendada', 'Reserva Reagendada'
    SUSCRIPCION_RENOVACION = 'suscripcion_renovacion', 'Renovación de Suscripción'
    SUSCRIPCION_EXPIRADA = 'suscripcion_expirada', 'Suscripción Expirada'
    INASISTENCIA = 'inasistencia', 'Inasistencia'
    CUSTOM = 'custom', 'Personalizado'

class EstadoRecordatorio(models.TextChoices):
    """Estados del recordatorio"""
    PENDIENTE = 'pendiente', 'Pendiente'
    ENVIADO = 'enviado', 'Enviado'
    ENTREGADO = 'entregado', 'Entregado'
    FALLIDO = 'fallido', 'Fallido'
    CANCELADO = 'cancelado', 'Cancelado'

class CanalNotificacion(models.TextChoices):
    """Canales de notificación disponibles"""
    EMAIL = 'email', 'Email'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    SMS = 'sms', 'SMS'
    PUSH = 'push', 'Push Notification'

class Recordatorio(models.Model):
    """
    Modelo principal para gestionar recordatorios
    """
    # Identificación única
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Tipo y estado
    tipo = models.CharField(max_length=50, choices=TipoRecordatorio.choices)
    estado = models.CharField(max_length=20, choices=EstadoRecordatorio.choices, default=EstadoRecordatorio.PENDIENTE)
    
    # Destinatario
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recordatorios_recibidos')
    
    # Contenido
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    mensaje_html = models.TextField(blank=True, null=True)
    
    # Programación
    fecha_programada = models.DateTimeField()
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    
    # Canales de envío
    canales_habilitados = models.JSONField(default=list)  # Lista de canales a usar
    canales_enviados = models.JSONField(default=dict)     # Estado de cada canal
    
    # Relaciones genéricas (para reservas, suscripciones, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    contenido_relacionado = GenericForeignKey('content_type', 'object_id')
    
    # Configuración
    reintentos_maximos = models.PositiveIntegerField(default=3)
    reintentos_actuales = models.PositiveIntegerField(default=0)
    prioridad = models.PositiveIntegerField(default=5)  # 1=alta, 10=baja
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='recordatorios_creados')
    
    # Configuración de templates
    template_name = models.CharField(max_length=100, blank=True, null=True)
    contexto_template = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'recordatorios'
        verbose_name = 'Recordatorio'
        verbose_name_plural = 'Recordatorios'
        ordering = ['-fecha_programada', '-prioridad']
        indexes = [
            models.Index(fields=['estado', 'fecha_programada']),
            models.Index(fields=['tipo', 'destinatario']),
            models.Index(fields=['fecha_programada']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.tipo} - {self.destinatario} ({self.estado})"
    
    @property
    def esta_programado(self):
        """Verifica si el recordatorio está programado para el futuro"""
        return self.fecha_programada > timezone.now()
    
    @property
    def esta_vencido(self):
        """Verifica si el recordatorio está vencido"""
        return self.fecha_programada < timezone.now() and self.estado == EstadoRecordatorio.PENDIENTE
    
    @property
    def puede_reintentar(self):
        """Verifica si se puede reintentar el envío"""
        return self.reintentos_actuales < self.reintentos_maximos
    
    def marcar_enviado(self, canal):
        """Marca el recordatorio como enviado por un canal específico"""
        if not self.canales_enviados:
            self.canales_enviados = {}
        
        self.canales_enviados[canal] = {
            'estado': 'enviado',
            'fecha': timezone.now().isoformat(),
            'reintentos': self.reintentos_actuales
        }
        
        if not self.fecha_envio:
            self.fecha_envio = timezone.now()
        
        # Si todos los canales están enviados, cambiar estado general
        if len(self.canales_enviados) == len(self.canales_habilitados):
            self.estado = EstadoRecordatorio.ENVIADO
        
        self.save()
    
    def marcar_entregado(self, canal):
        """Marca el recordatorio como entregado por un canal específico"""
        if not self.canales_enviados:
            self.canales_enviados = {}
        
        if canal in self.canales_enviados:
            self.canales_enviados[canal]['estado'] = 'entregado'
            self.canales_enviados[canal]['fecha_entrega'] = timezone.now().isoformat()
        
        if not self.fecha_entrega:
            self.fecha_entrega = timezone.now()
        
        self.save()
    
    def marcar_fallido(self, canal, error=""):
        """Marca el recordatorio como fallido por un canal específico"""
        if not self.canales_enviados:
            self.canales_enviados = {}
        
        self.canales_enviados[canal] = {
            'estado': 'fallido',
            'fecha': timezone.now().isoformat(),
            'error': error,
            'reintentos': self.reintentos_actuales
        }
        
        self.reintentos_actuales += 1
        
        # Si se agotaron los reintentos, marcar como fallido
        if not self.puede_reintentar:
            self.estado = EstadoRecordatorio.FALLIDO
        
        self.save()
    
    def programar_reintento(self, canal, delay_minutos=15):
        """Programa un reintento para un canal específico"""
        if self.puede_reintentar:
            nueva_fecha = timezone.now() + timezone.timedelta(minutes=delay_minutos)
            self.fecha_programada = nueva_fecha
            self.save()
            return True
        return False

class ConfiguracionRecordatorio(models.Model):
    """
    Configuración personalizada para tipos de recordatorios
    """
    tipo = models.CharField(max_length=50, choices=TipoRecordatorio.choices, unique=True)
    
    # Configuración de timing
    anticipacion_horas = models.PositiveIntegerField(default=24)  # Horas antes del evento
    anticipacion_minutos = models.PositiveIntegerField(default=0)
    
    # Canales habilitados por defecto
    canales_habilitados = models.JSONField(default=list)
    
    # Templates
    template_email = models.CharField(max_length=100, blank=True, null=True)
    template_whatsapp = models.CharField(max_length=100, blank=True, null=True)
    template_sms = models.CharField(max_length=100, blank=True, null=True)
    
    # Configuración de reintentos
    reintentos_maximos = models.PositiveIntegerField(default=3)
    delay_reintentos_minutos = models.PositiveIntegerField(default=15)
    
    # Estado
    activo = models.BooleanField(default=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'configuracion_recordatorios'
        verbose_name = 'Configuración de Recordatorio'
        verbose_name_plural = 'Configuraciones de Recordatorios'
    
    def __str__(self):
        return f"Configuración: {self.tipo}"
    
    @property
    def anticipacion_total_minutos(self):
        """Calcula la anticipación total en minutos"""
        return (self.anticipacion_horas * 60) + self.anticipacion_minutos

class HistorialRecordatorio(models.Model):
    """
    Historial de acciones realizadas en recordatorios
    """
    recordatorio = models.ForeignKey(Recordatorio, on_delete=models.CASCADE, related_name='historial')
    
    # Acción realizada
    accion = models.CharField(max_length=50)  # enviado, entregado, fallido, reintento, etc.
    canal = models.CharField(max_length=20, choices=CanalNotificacion.choices, null=True, blank=True)
    
    # Detalles
    detalles = models.JSONField(default=dict)
    mensaje_error = models.TextField(blank=True, null=True)
    
    # Usuario que realizó la acción (si aplica)
    usuario_responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamp
    fecha_accion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'historial_recordatorios'
        verbose_name = 'Historial de Recordatorio'
        verbose_name_plural = 'Historial de Recordatorios'
        ordering = ['-fecha_accion']
    
    def __str__(self):
        return f"{self.recordatorio} - {self.accion} ({self.canal})"

class PlantillaRecordatorio(models.Model):
    """
    Plantillas para diferentes tipos de recordatorios
    """
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=50, choices=TipoRecordatorio.choices)
    
    # Contenido de la plantilla
    asunto = models.CharField(max_length=255)
    mensaje_texto = models.TextField()
    mensaje_html = models.TextField(blank=True, null=True)
    
    # Variables disponibles en la plantilla
    variables_disponibles = models.JSONField(default=list)
    
    # Configuración
    activa = models.BooleanField(default=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'plantillas_recordatorios'
        verbose_name = 'Plantilla de Recordatorio'
        verbose_name_plural = 'Plantillas de Recordatorios'
    
    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
    
    def renderizar(self, contexto):
        """Renderiza la plantilla con el contexto proporcionado"""
        from django.template import Template, Context
        
        try:
            # Renderizar asunto
            template_asunto = Template(self.asunto)
            asunto_renderizado = template_asunto.render(Context(contexto))
            
            # Renderizar mensaje de texto
            template_texto = Template(self.mensaje_texto)
            texto_renderizado = template_texto.render(Context(contexto))
            
            # Renderizar mensaje HTML
            html_renderizado = None
            if self.mensaje_html:
                template_html = Template(self.mensaje_html)
                html_renderizado = template_html.render(Context(contexto))
            
            return {
                'asunto': asunto_renderizado,
                'mensaje': texto_renderizado,
                'mensaje_html': html_renderizado
            }
            
        except Exception as e:
            # En caso de error, devolver la plantilla sin renderizar
            return {
                'asunto': self.asunto,
                'mensaje': self.mensaje_texto,
                'mensaje_html': self.mensaje_html,
                'error_renderizado': str(e)
            }
