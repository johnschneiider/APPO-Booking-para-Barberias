from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from negocios.models import Negocio, Servicio

User = get_user_model()

class Profesional(models.Model):
    """Modelo para el perfil del profesional (peluquero)"""
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil_profesional')
    nombre_completo = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, blank=True)
    experiencia_anos = models.PositiveIntegerField(default=0)
    descripcion = models.TextField(blank=True)
    foto_perfil = models.ImageField(upload_to='profesionales/fotos/', blank=True, null=True)
    portada = models.ImageField(upload_to='profesionales/portadas/', blank=True, null=True)
    cv = models.FileField(upload_to='profesionales/cv/', blank=True, null=True)
    certificaciones = models.TextField(blank=True)
    disponible = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    servicios = models.ManyToManyField(Servicio, blank=True, related_name='profesionales')

    class Meta:
        verbose_name = 'Profesional'
        verbose_name_plural = 'Profesionales'

    def __str__(self):
        return f"{self.nombre_completo} - {self.especialidad}"

class Matriculacion(models.Model):
    """Modelo para la matriculación de un profesional a un negocio"""
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    )
    
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='matriculaciones')
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='matriculaciones')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    mensaje_solicitud = models.TextField(blank=True)
    mensaje_respuesta = models.TextField(blank=True)
    salario_propuesto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    horario_propuesto = models.TextField(blank=True)
    
    # Salario asignado por el negocio (después de ser aceptado)
    salario_mensual = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Salario mensual asignado por el negocio'
    )
    cargo = models.CharField(
        max_length=100, blank=True, default='Barbero',
        help_text='Cargo o rol del profesional en el negocio'
    )
    
    class Meta:
        verbose_name = 'Matriculación'
        verbose_name_plural = 'Matriculaciones'
        unique_together = ['profesional', 'negocio']

    def __str__(self):
        return f"{self.profesional.nombre_completo} -> {self.negocio.nombre} ({self.estado})"

    def aprobar(self, mensaje_respuesta=""):
        self.estado = 'aprobada'
        self.fecha_respuesta = timezone.now()
        self.mensaje_respuesta = mensaje_respuesta
        self.save()
        
        # Copiar horarios del negocio al profesional automáticamente
        self._asignar_horarios_negocio()
        
        # Asignar todos los servicios del negocio al profesional
        self._asignar_servicios_negocio()
    
    def _asignar_horarios_negocio(self):
        """Copia los horarios del negocio al profesional si no tiene horarios asignados"""
        from datetime import time as dt_time
        
        # Si el profesional ya tiene horarios, no los sobreescribimos
        if self.profesional.horarios.exists():
            return
        
        # Mapeo de nombres de días (Negocio -> HorarioProfesional)
        dia_mapping = {
            'Lunes': 'lunes',
            'Martes': 'martes',
            'Miércoles': 'miercoles',
            'Jueves': 'jueves',
            'Viernes': 'viernes',
            'Sábado': 'sabado',
            'Domingo': 'domingo'
        }
        
        horario_negocio = self.negocio.horario_atencion or {}
        
        for dia_nombre, horario in horario_negocio.items():
            if horario and horario.get('inicio') and horario.get('fin'):
                try:
                    # Convertir strings a objetos time
                    hora_inicio = dt_time.fromisoformat(horario['inicio'])
                    hora_fin = dt_time.fromisoformat(horario['fin'])
                    dia_semana = dia_mapping.get(dia_nombre)
                    
                    if dia_semana:
                        HorarioProfesional.objects.create(
                            profesional=self.profesional,
                            dia_semana=dia_semana,
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin,
                            disponible=True
                        )
                except (ValueError, TypeError):
                    continue
    
    def _asignar_servicios_negocio(self):
        """Asigna todos los servicios del negocio al profesional si no tiene servicios"""
        from negocios.models import ServicioNegocio
        
        # Si el profesional ya tiene servicios, no los sobreescribimos
        if self.profesional.servicios.exists():
            return
        
        # Obtener todos los servicios activos del negocio
        servicios_negocio = ServicioNegocio.objects.filter(negocio=self.negocio, activo=True)
        servicios = [sn.servicio for sn in servicios_negocio]
        
        if servicios:
            self.profesional.servicios.set(servicios)

    def rechazar(self, mensaje_respuesta=""):
        self.estado = 'rechazada'
        self.fecha_respuesta = timezone.now()
        self.mensaje_respuesta = mensaje_respuesta
        self.save()

class Notificacion(models.Model):
    """Modelo para las notificaciones del profesional"""
    TIPO_CHOICES = (
        ('reserva', 'Nueva Reserva'),
        ('matriculacion', 'Respuesta Matriculación'),
        ('solicitud_ausencia', 'Respuesta Solicitud Ausencia'),
        ('dia_descanso', 'Día de Descanso'),
        ('sistema', 'Notificación del Sistema'),
    )
    
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    url_relacionada = models.URLField(blank=True)
    
    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.profesional.nombre_completo} - {self.titulo}"

    def marcar_como_leida(self):
        self.leida = True
        self.fecha_lectura = timezone.now()
        self.save()

class HorarioProfesional(models.Model):
    """Modelo para los horarios de trabajo del profesional"""
    DIAS_SEMANA = (
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    )
    
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(max_length=10, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    disponible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Horario Profesional'
        verbose_name_plural = 'Horarios Profesionales'
        unique_together = ['profesional', 'dia_semana']

    def __str__(self):
        return f"{self.profesional.nombre_completo} - {self.dia_semana} ({self.hora_inicio}-{self.hora_fin})"

class MetricaProfesional(models.Model):
    profesional = models.ForeignKey('Profesional', on_delete=models.CASCADE, related_name='metricas')
    fecha = models.DateField()
    total_turnos = models.IntegerField(default=0)
    turnos_completados = models.IntegerField(default=0)
    turnos_cancelados = models.IntegerField(default=0)
    ingresos_totales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    calificacion_promedio = models.FloatField(default=0)
    horas_trabajadas = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    class Meta:
        unique_together = ['profesional', 'fecha']
        ordering = ['-fecha']
    def __str__(self):
        return f"{self.profesional.nombre_completo} - {self.fecha}"

class SolicitudAusencia(models.Model):
    """Modelo para las solicitudes de ausencia del profesional"""
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('cancelada', 'Cancelada'),
    )
    
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='solicitudes_ausencia')
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='solicitudes_ausencia')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(null=True, blank=True)
    comentario_respuesta = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Solicitud de Ausencia'
        verbose_name_plural = 'Solicitudes de Ausencia'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"{self.profesional.nombre_completo} - {self.fecha_inicio} a {self.fecha_fin} ({self.estado})"

    def aprobar(self, comentario=""):
        print(f"DEBUG: === MÉTODO APROBAR EJECUTADO ===")
        print(f"DEBUG: Aprobando solicitud {self.id}, estado actual: {self.estado}")
        print(f"DEBUG: Comentario recibido: '{comentario}'")
        
        self.estado = 'aprobada'
        self.fecha_respuesta = timezone.now()
        self.comentario_respuesta = comentario
        
        print(f"DEBUG: Antes de guardar - estado: {self.estado}")
        self.save()
        print(f"DEBUG: Después de guardar - estado: {self.estado}")
        
        # Crear la ausencia aprobada
        ausencia = AusenciaProfesional.objects.create(
            profesional=self.profesional,
            fecha_inicio=self.fecha_inicio,
            fecha_fin=self.fecha_fin,
            motivo=self.motivo,
            activo=True
        )
        print(f"DEBUG: Ausencia creada: {ausencia}")
        print(f"DEBUG: === FIN MÉTODO APROBAR ===")

    def rechazar(self, comentario=""):
        self.estado = 'rechazada'
        self.fecha_respuesta = timezone.now()
        self.comentario_respuesta = comentario
        self.save()

class AusenciaProfesional(models.Model):
    """Modelo para las ausencias aprobadas del profesional"""
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='ausencias')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ausencia Profesional'
        verbose_name_plural = 'Ausencias Profesionales'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.profesional.nombre_completo} - {self.fecha_inicio} a {self.fecha_fin} ({'Activa' if self.activo else 'Inactiva'})"
