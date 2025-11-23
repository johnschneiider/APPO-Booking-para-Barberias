"""
Modelos para el sistema de fidelización por WhatsApp
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid


class TipoMensaje(models.TextChoices):
    """Tipos de mensajes de fidelización"""
    CONFIRMACION_RESERVA = 'confirmacion_reserva', 'Confirmación de Reserva'
    RECORDATORIO_24H = 'recordatorio_24h', 'Recordatorio 24 Horas Antes'
    RECORDATORIO_1H = 'recordatorio_1h', 'Recordatorio 1 Hora Antes'


class EstadoMensaje(models.TextChoices):
    """Estados del mensaje"""
    PENDIENTE = 'pendiente', 'Pendiente'
    PROGRAMADO = 'programado', 'Programado'
    ENVIADO = 'enviado', 'Enviado'
    FALLIDO = 'fallido', 'Fallido'
    CANCELADO = 'cancelado', 'Cancelado'


class MensajeFidelizacion(models.Model):
    """
    Modelo para gestionar mensajes de fidelización programados
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Tipo y estado
    tipo = models.CharField(max_length=50, choices=TipoMensaje.choices)
    estado = models.CharField(
        max_length=20, 
        choices=EstadoMensaje.choices, 
        default=EstadoMensaje.PENDIENTE
    )
    
    # Destinatario
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='mensajes_fidelizacion'
    )
    
    # Relación con reserva
    reserva = models.ForeignKey(
        'clientes.Reserva',
        on_delete=models.CASCADE,
        related_name='mensajes_fidelizacion',
        null=True,
        blank=True
    )
    
    # Programación
    fecha_programada = models.DateTimeField(help_text="Fecha y hora en que se debe enviar el mensaje")
    fecha_envio = models.DateTimeField(null=True, blank=True)
    
    # Contenido del mensaje
    mensaje = models.TextField(help_text="Contenido del mensaje de WhatsApp")
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    intentos_envio = models.PositiveIntegerField(default=0)
    max_intentos = models.PositiveIntegerField(default=3)
    error_mensaje = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'fidelizacion_mensajes'
        verbose_name = 'Mensaje de Fidelización'
        verbose_name_plural = 'Mensajes de Fidelización'
        ordering = ['fecha_programada']
        indexes = [
            models.Index(fields=['estado', 'fecha_programada']),
            models.Index(fields=['tipo', 'reserva']),
            models.Index(fields=['fecha_programada']),
        ]
    
    def __str__(self):
        return f"{self.tipo} - {self.destinatario} ({self.estado})"
    
    def marcar_enviado(self):
        """Marca el mensaje como enviado"""
        self.estado = EstadoMensaje.ENVIADO
        self.fecha_envio = timezone.now()
        self.save()
    
    def marcar_fallido(self, error=""):
        """Marca el mensaje como fallido"""
        self.intentos_envio += 1
        self.error_mensaje = error
        if self.intentos_envio >= self.max_intentos:
            self.estado = EstadoMensaje.FALLIDO
        self.save()
    
    def cancelar(self):
        """Cancela el mensaje"""
        self.estado = EstadoMensaje.CANCELADO
        self.save()

