from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from decimal import Decimal

class UsuarioPersonalizado(AbstractUser):
    TIPO_USUARIO = (
        ('cliente', 'Cliente'),
        ('negocio', 'Negocio'),
        ('profesional', 'Profesional'),
        ('super_admin', 'Super Administrador'),
    )
    tipo = models.CharField(max_length=15, choices=TIPO_USUARIO, default='cliente')
    telefono = models.CharField(max_length=15, blank=True)
    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('', 'Prefiero no decirlo'),
    ]
    genero = models.CharField(max_length=20, choices=GENERO_CHOICES, blank=True, null=True, default='')
    fecha_nacimiento = models.DateField(blank=True, null=True)

class Feedback(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('resuelto', 'Resuelto'),
        ('cerrado', 'Cerrado'),
    )
    
    PRIORIDAD_CHOICES = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )
    
    # Información del ticket
    numero_ticket = models.CharField(max_length=20, unique=True, blank=True)
    titulo = models.CharField(max_length=200, blank=True)
    usuario = models.ForeignKey('UsuarioPersonalizado', on_delete=models.CASCADE, related_name='feedbacks_enviados')
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    categoria = models.CharField(max_length=50, blank=True, help_text='Ej: Bug, Sugerencia, Consulta, etc.')
    
    # Archivos adjuntos
    imagen = models.ImageField(upload_to='feedback/', blank=True, null=True)
    archivos_adjuntos = models.JSONField(default=list, blank=True, help_text='Lista de archivos adjuntos')
    
    # Metadatos
    asignado_a = models.ForeignKey('UsuarioPersonalizado', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets_asignados')
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    tiempo_resolucion = models.DurationField(null=True, blank=True)
    
    # Etiquetas y seguimiento
    etiquetas = models.ManyToManyField('UsuarioPersonalizado', related_name='feedback_etiquetado', blank=True)
    leido_por_admin = models.BooleanField(default=False)
    leido_por_usuario = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Ticket de Feedback'
        verbose_name_plural = 'Tickets de Feedback'

    def __str__(self):
        return f"Ticket #{self.numero_ticket} - {self.usuario.username} - {self.estado}"

    def save(self, *args, **kwargs):
        if not self.numero_ticket:
            # Generar número de ticket único
            ultimo_ticket = Feedback.objects.order_by('-id').first()
            if ultimo_ticket:
                parte = ultimo_ticket.numero_ticket.split('-')[1] if '-' in ultimo_ticket.numero_ticket else '0'
                try:
                    ultimo_numero = int(parte)
                except ValueError:
                    try:
                        ultimo_numero = int(parte, 16)  # intenta como hexadecimal
                    except ValueError:
                        ultimo_numero = 0  # valor por defecto si no es número
                self.numero_ticket = f"TICKET-{ultimo_numero + 1:06d}"
            else:
                self.numero_ticket = "TICKET-000001"
        
        if not self.titulo:
            self.titulo = f"Feedback de {self.usuario.username}"
        
        super().save(*args, **kwargs)

    def cambiar_estado(self, nuevo_estado, usuario_admin=None):
        """Cambiar el estado del ticket y registrar la acción"""
        print(f"cambiar_estado called: {self.estado} -> {nuevo_estado}")  # Debug
        self.estado = nuevo_estado
        if nuevo_estado in ['resuelto', 'cerrado'] and not self.fecha_resolucion:
            self.fecha_resolucion = timezone.now()
            if self.fecha:
                self.tiempo_resolucion = self.fecha_resolucion - self.fecha
        print(f"Saving ticket with estado: {self.estado}")  # Debug
        self.save()
        print(f"Ticket saved successfully. Current estado: {self.estado}")  # Debug
        
        # Crear respuesta automática del sistema
        RespuestaTicket.objects.create(
            ticket=self,
            autor=usuario_admin or self.asignado_a,
            mensaje=f"Estado del ticket cambiado a: {dict(self.ESTADO_CHOICES)[nuevo_estado]}",
            es_sistema=True
        )
        print(f"System response created for state change")  # Debug

class RespuestaTicket(models.Model):
    """Modelo para las respuestas en el sistema de tickets"""
    ticket = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='respuestas')
    autor = models.ForeignKey('UsuarioPersonalizado', on_delete=models.CASCADE, related_name='respuestas_ticket')
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    es_sistema = models.BooleanField(default=False, help_text='Si es una respuesta automática del sistema')


class BusinessCheckoutIntent(models.Model):
    """
    Registro de intención de cobro para negocios (plan plataforma).
    Se usa para almacenar el método de pago (token placeholder) y el periodo de trial.
    """
    ESTADO_CHOICES = [
        ('trial_activo', 'Trial activo'),
        ('metodo_guardado', 'Método de pago guardado'),
        ('pendiente', 'Pendiente'),
        ('cancelado', 'Cancelado'),
    ]

    usuario = models.ForeignKey(
        UsuarioPersonalizado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkout_intents'
    )
    negocio = models.ForeignKey(
        'negocios.Negocio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='checkout_intents'
    )

    nombre_negocio = models.CharField(max_length=150)
    email_contacto = models.EmailField()
    telefono_contacto = models.CharField(max_length=30, blank=True)
    numero_barberos = models.PositiveIntegerField(default=1)

    # Datos del plan
    precio_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('49000.00'))
    moneda = models.CharField(max_length=5, default='COP')
    trial_inicio = models.DateTimeField(default=timezone.now)
    trial_fin = models.DateTimeField(null=True, blank=True)
    auto_cobro = models.BooleanField(default=True)

    # Campos PayU (placeholders para tokenización)
    payu_customer_id = models.CharField(max_length=100, blank=True)
    payu_token = models.CharField(max_length=150, blank=True)
    payu_card_mask = models.CharField(max_length=30, blank=True, help_text="Últimos dígitos o referencia segura")
    payu_state = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='pendiente')

    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = "Intento de checkout de negocio"
        verbose_name_plural = "Intentos de checkout de negocio"

    def __str__(self):
        return f"{self.nombre_negocio} - {self.email_contacto}"

    @property
    def dias_trial_restantes(self):
        if not self.trial_fin:
            return None
        delta = self.trial_fin - timezone.now()
        return max(0, delta.days)
    archivos_adjuntos = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['fecha']
        verbose_name = 'Respuesta de Ticket'
        verbose_name_plural = 'Respuestas de Tickets'

    def __str__(self):
        return f"Respuesta en {self.ticket.numero_ticket} - {self.autor.username}"

class NotificacionAdmin(models.Model):
    TIPO_CHOICES = (
        ('feedback', 'Nuevo Feedback'),
        ('sistema', 'Notificación del Sistema'),
        ('ticket', 'Nuevo Ticket'),
        ('respuesta_ticket', 'Nueva Respuesta en Ticket'),
    )
    destinatario = models.ForeignKey('UsuarioPersonalizado', on_delete=models.CASCADE, related_name='notificaciones_admin')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    url_relacionada = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Notificación Admin'
        verbose_name_plural = 'Notificaciones Admin'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{str(self.destinatario)} - {self.titulo}"

    def marcar_como_leida(self):
        self.leida = True
        self.fecha_lectura = timezone.now()
        self.save() 

class RateLimitConfig(models.Model):
    """Configuración de rate limiting para el sistema"""
    nombre = models.CharField(max_length=100, unique=True, help_text="Nombre descriptivo de la configuración")
    clave = models.CharField(max_length=50, unique=True, help_text="Clave única para identificar la configuración")
    limite = models.CharField(max_length=20, help_text="Límite en formato 'número/período' (ej: 5/m, 10/h, 100/d)")
    descripcion = models.TextField(help_text="Descripción de qué protege esta configuración")
    activo = models.BooleanField(default=True, help_text="Si esta configuración está activa")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuración de Rate Limiting"
        verbose_name_plural = "Configuraciones de Rate Limiting"
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.limite})"
    
    @classmethod
    def get_config(cls, clave, default=None):
        """Obtener configuración por clave"""
        try:
            config = cls.objects.get(clave=clave, activo=True)
            return config.limite
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def get_all_configs(cls):
        """Obtener todas las configuraciones activas como diccionario"""
        configs = {}
        for config in cls.objects.filter(activo=True):
            configs[config.clave] = config.limite
        return configs 

class EmailTracking(models.Model):
    """
    Modelo para tracking de emails enviados
    """
    ESTADO_CHOICES = [
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('abierto', 'Abierto'),
        ('clickeado', 'Clickeado'),
        ('rebotado', 'Rebotado'),
        ('fallido', 'Fallido'),
    ]
    
    PROVEEDOR_CHOICES = [
        ('sendgrid', 'SendGrid'),
        ('aws_ses', 'AWS SES'),
        ('smtp', 'SMTP'),
    ]
    
    # Información del email
    subject = models.CharField(max_length=255)
    recipient = models.EmailField()
    from_email = models.EmailField()
    
    # Tracking
    message_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='enviado')
    proveedor = models.CharField(max_length=20, choices=PROVEEDOR_CHOICES)
    
    # Métricas
    enviado_en = models.DateTimeField(auto_now_add=True)
    entregado_en = models.DateTimeField(null=True, blank=True)
    abierto_en = models.DateTimeField(null=True, blank=True)
    clickeado_en = models.DateTimeField(null=True, blank=True)
    
    # Información adicional
    template_name = models.CharField(max_length=100, null=True, blank=True)
    context_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Relaciones
    usuario = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE, null=True, blank=True)
    negocio = models.ForeignKey('negocios.Negocio', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'email_tracking'
        verbose_name = 'Email Tracking'
        verbose_name_plural = 'Emails Tracking'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['proveedor']),
            models.Index(fields=['enviado_en']),
            models.Index(fields=['recipient']),
        ]
    
    def __str__(self):
        return f"{self.subject} -> {self.recipient} ({self.estado})"
    
    def marcar_entregado(self):
        """Marca el email como entregado"""
        self.estado = 'entregado'
        self.entregado_en = timezone.now()
        self.save()
    
    def marcar_abierto(self):
        """Marca el email como abierto"""
        self.estado = 'abierto'
        self.abierto_en = timezone.now()
        self.save()
    
    def marcar_clickeado(self):
        """Marca el email como clickeado"""
        self.estado = 'clickeado'
        self.clickeado_en = timezone.now()
        self.save()
    
    def marcar_fallido(self, error_message=""):
        """Marca el email como fallido"""
        self.estado = 'fallido'
        self.error_message = error_message
        self.save()
    
    @property
    def tiempo_entrega(self):
        """Calcula el tiempo entre envío y entrega"""
        if self.entregado_en and self.enviado_en:
            return self.entregado_en - self.enviado_en
        return None
    
    @property
    def tiempo_apertura(self):
        """Calcula el tiempo entre entrega y apertura"""
        if self.abierto_en and self.entregado_en:
            return self.abierto_en - self.entregado_en
        return None 
