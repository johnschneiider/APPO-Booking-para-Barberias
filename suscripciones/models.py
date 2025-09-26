from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()

class PlanSuscripcion(models.Model):
    """Modelo para los planes de suscripción que ofrecen los negocios"""
    negocio = models.ForeignKey('negocios.Negocio', on_delete=models.CASCADE, related_name='planes_suscripcion')
    nombre = models.CharField(max_length=100, help_text="Nombre del plan (ej: Básico, Premium, VIP)")
    descripcion = models.TextField(help_text="Descripción detallada del plan")
    precio_mensual = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Precio mensual en la moneda local"
    )
    activo = models.BooleanField(default=True, help_text="Si el plan está disponible para suscripciones")
    destacado = models.BooleanField(default=False, help_text="Si el plan debe destacarse en la lista")
    duracion_meses = models.PositiveIntegerField(default=12, help_text="Duración del plan en meses")
    limite_suscriptores = models.PositiveIntegerField(default=0, help_text="0 = sin límite, otro número = límite máximo")
    imagen = models.ImageField(upload_to='planes_suscripcion/', blank=True, null=True, help_text="Imagen representativa del plan")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Configuración del plan
    max_servicios_mes = models.PositiveIntegerField(
        default=0, 
        help_text="0 = ilimitado, otro número = límite mensual"
    )
    descuento_servicios = models.PositiveIntegerField(
        default=0, 
        help_text="Porcentaje de descuento en servicios (0-100)"
    )
    prioridad_reservas = models.BooleanField(
        default=False, 
        help_text="Si los suscriptores tienen prioridad en reservas"
    )
    
    class Meta:
        verbose_name = 'Plan de Suscripción'
        verbose_name_plural = 'Planes de Suscripción'
        unique_together = ['negocio', 'nombre']
        ordering = ['precio_mensual']
    
    def __str__(self):
        return f"{self.nombre} - {self.negocio.nombre} (${self.precio_mensual})"
    
    @property
    def es_ilimitado(self):
        """Retorna True si el plan tiene servicios ilimitados"""
        return self.max_servicios_mes == 0
    
    def get_precio_formateado(self):
        """Retorna el precio formateado como string"""
        return f"${self.precio_mensual}"
    
    @property
    def total_suscriptores(self):
        """Retorna el total de suscriptores activos"""
        return self.suscripciones.filter(estado='activa').count()
    
    @property
    def ingresos_mensuales(self):
        """Retorna los ingresos mensuales del plan"""
        return self.total_suscriptores * self.precio_mensual

class Suscripcion(models.Model):
    """Modelo para las suscripciones activas de los clientes"""
    ESTADOS_CHOICES = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('expirada', 'Expirada'),
        ('pendiente_pago', 'Pendiente de Pago'),
        ('suspendida', 'Suspendida'),
    ]
    
    cliente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suscripciones')
    plan = models.ForeignKey(PlanSuscripcion, on_delete=models.CASCADE, related_name='suscripciones')
    negocio = models.ForeignKey('negocios.Negocio', on_delete=models.CASCADE, related_name='suscripciones')
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADOS_CHOICES, default='pendiente_pago')
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    fecha_cancelacion = models.DateTimeField(null=True, blank=True)
    
    # Información de pago
    precio_actual = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default='COP', help_text="Código de moneda (COP, USD, etc.)")
    
    # Contadores y límites
    servicios_utilizados_mes = models.PositiveIntegerField(default=0)
    ultimo_reset_mes = models.DateField(default=timezone.now)
    
    # Configuración automática
    renovacion_automatica = models.BooleanField(default=True)
    notificar_antes_renovacion = models.BooleanField(default=True)
    
    # Metadatos
    notas = models.TextField(blank=True, help_text="Notas adicionales sobre la suscripción")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
        unique_together = ['cliente', 'negocio', 'plan']
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.cliente.get_full_name()} - {self.plan.nombre} en {self.negocio.nombre}"

class BeneficioSuscripcion(models.Model):
    """Modelo para los beneficios incluidos en cada plan de suscripción"""
    plan = models.ForeignKey(PlanSuscripcion, on_delete=models.CASCADE, related_name='beneficios')
    descripcion = models.CharField(max_length=200, help_text="Descripción del beneficio")
    activo = models.BooleanField(default=True, help_text="Si el beneficio está activo")
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición del beneficio")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Beneficio de Suscripción'
        verbose_name_plural = 'Beneficios de Suscripción'
        ordering = ['orden', 'fecha_creacion']
        unique_together = ['plan', 'descripcion']
    
    def __str__(self):
        return f"{self.descripcion} - {self.plan.nombre}"
    
    @property
    def esta_activa(self):
        """Retorna True si la suscripción está activa y no ha expirado"""
        if self.estado != 'activa':
            return False
        if self.fecha_fin and timezone.now() > self.fecha_fin:
            return False
        return True
    
    @property
    def dias_restantes(self):
        """Retorna los días restantes de la suscripción"""
        if not self.fecha_fin:
            return None
        delta = self.fecha_fin - timezone.now()
        return max(0, delta.days)
    
    @property
    def puede_usar_servicio(self):
        """Retorna True si el cliente puede usar un servicio con su suscripción"""
        if not self.esta_activa:
            return False
        if self.plan.es_ilimitado:
            return True
        return self.servicios_utilizados_mes < self.plan.max_servicios_mes
    
    def usar_servicio(self):
        """Marca que se ha usado un servicio"""
        if self.plan.es_ilimitado:
            return True
        
        if self.servicios_utilizados_mes < self.plan.max_servicios_mes:
            self.servicios_utilizados_mes += 1
            self.save()
            return True
        return False
    
    def reset_contador_mensual(self):
        """Resetea el contador de servicios utilizados al inicio del mes"""
        hoy = timezone.now().date()
        if hoy.month != self.ultimo_reset_mes.month or hoy.year != self.ultimo_reset_mes.year:
            self.servicios_utilizados_mes = 0
            self.ultimo_reset_mes = hoy
            self.save()
    
    def cancelar(self, motivo=""):
        """Cancela la suscripción"""
        self.estado = 'cancelada'
        self.fecha_cancelacion = timezone.now()
        if motivo:
            self.notas += f"\nCancelada: {motivo}"
        self.save()
    
    def renovar(self):
        """Renueva la suscripción por otro mes"""
        if self.estado == 'activa':
            # Calcular nueva fecha de fin (un mes después)
            if self.fecha_fin:
                nueva_fecha = self.fecha_fin + timezone.timedelta(days=30)
            else:
                nueva_fecha = timezone.now() + timezone.timedelta(days=30)
            
            self.fecha_fin = nueva_fecha
            self.servicios_utilizados_mes = 0
            self.ultimo_reset_mes = timezone.now().date()
            self.save()
            return True
        return False

class PagoSuscripcion(models.Model):
    """Modelo para el historial de pagos de suscripciones"""
    ESTADOS_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completado', 'Completado'),
        ('fallido', 'Fallido'),
        ('reembolsado', 'Reembolsado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODOS_PAGO_CHOICES = [
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
        ('transferencia', 'Transferencia Bancaria'),
        ('efectivo', 'Efectivo'),
        ('pse', 'PSE'),
        ('paypal', 'PayPal'),
        ('otro', 'Otro'),
    ]
    
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=3, default='COP')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO_CHOICES)
    
    # Estado del pago
    estado = models.CharField(max_length=20, choices=ESTADOS_PAGO_CHOICES, default='pendiente')
    
    # Información de transacción
    referencia_pago = models.CharField(max_length=100, blank=True, help_text="Referencia o ID de la transacción")
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(help_text="Fecha límite para realizar el pago")
    
    # Metadatos
    descripcion = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pago de Suscripción'
        verbose_name_plural = 'Pagos de Suscripciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pago {self.referencia_pago} - {self.suscripcion} - ${self.monto}"
    
    @property
    def esta_vencido(self):
        """Retorna True si el pago está vencido"""
        return timezone.now() > self.fecha_vencimiento
    
    def marcar_completado(self, referencia_pago=""):
        """Marca el pago como completado"""
        self.estado = 'completado'
        self.fecha_pago = timezone.now()
        if referencia_pago:
            self.referencia_pago = referencia_pago
        self.save()
        
        # Activar la suscripción si estaba pendiente
        if self.suscripcion.estado == 'pendiente_pago':
            self.suscripcion.estado = 'activa'
            self.suscripcion.save()

class HistorialSuscripcion(models.Model):
    """Modelo para el historial completo de cambios en suscripciones"""
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE, related_name='historial')
    accion = models.CharField(max_length=50, choices=[
        ('creada', 'Creada'),
        ('activada', 'Activada'),
        ('renovada', 'Renovada'),
        ('cancelada', 'Cancelada'),
        ('suspendida', 'Suspendida'),
        ('estado_cambiado', 'Estado Cambiado'),
        ('plan_cambiado', 'Plan Cambiado'),
        ('pago_realizado', 'Pago Realizado'),
        ('pago_fallido', 'Pago Fallido'),
    ])
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario_responsable = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Usuario que realizó la acción"
    )
    
    class Meta:
        verbose_name = 'Historial de Suscripción'
        verbose_name_plural = 'Historial de Suscripciones'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.accion} - {self.suscripcion} - {self.fecha}"
