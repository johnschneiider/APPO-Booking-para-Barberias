from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from clientes.models import Reserva, NotificacionCliente
from negocios.models import Negocio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Procesa automáticamente las inasistencias de reservas pasadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar sin hacer cambios reales (solo mostrar qué se haría)',
        )
        parser.add_argument(
            '--minutos-tolerancia',
            type=int,
            default=15,
            help='Minutos de tolerancia antes de marcar como inasistencia (default: 15)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        minutos_tolerancia = options['minutos_tolerancia']
        
        self.stdout.write("🔍 Procesando inasistencias automáticamente...")
        
        # Calcular tiempo límite (hora actual - tolerancia)
        ahora = timezone.now()
        tiempo_limite = ahora - timedelta(minutes=minutos_tolerancia)
        
        # Buscar reservas que deberían ser marcadas como inasistencia
        reservas_para_inasistencia = Reserva.objects.filter(
            Q(fecha__lt=ahora.date()) |  # Reservas de días anteriores
            Q(fecha=ahora.date(), hora_fin__lt=tiempo_limite.time()),  # Reservas de hoy que ya pasaron
            estado__in=['pendiente', 'confirmado']
        )
        
        if dry_run:
            self.stdout.write(f"📊 En modo DRY-RUN - Se marcarían {reservas_para_inasistencia.count()} reservas como inasistencia")
            
            for reserva in reservas_para_inasistencia[:10]:  # Mostrar solo las primeras 10
                self.stdout.write(f"   - {reserva.cliente.username} - {reserva.fecha} {reserva.hora_inicio} - {reserva.peluquero.nombre}")
            
            if reservas_para_inasistencia.count() > 10:
                self.stdout.write(f"   ... y {reservas_para_inasistencia.count() - 10} más")
            
            return
        
        # Procesar inasistencias
        inasistencias_marcadas = 0
        for reserva in reservas_para_inasistencia:
            try:
                # Marcar como inasistencia
                reserva.marcar_inasistencia(motivo="No asistió a la cita programada")
                inasistencias_marcadas += 1
                
                # Crear notificación para el cliente
                NotificacionCliente.objects.create(
                    cliente=reserva.cliente,
                    tipo='sistema',
                    titulo='Inasistencia Registrada',
                    mensaje=f'Se ha registrado tu inasistencia a la cita del {reserva.fecha} a las {reserva.hora_inicio} en {reserva.peluquero.nombre}. Por favor, cancela con anticipación si no puedes asistir.',
                    url_relacionada='/clientes/mis_reservas/'
                )
                
                # Crear notificación para el negocio
                from profesionales.models import Notificacion
                Notificacion.objects.create(
                    profesional=reserva.profesional,
                    tipo='inasistencia',
                    titulo=f'Inasistencia de {reserva.cliente.username}',
                    mensaje=f'El cliente {reserva.cliente.username} no asistió a su cita del {reserva.fecha} a las {reserva.hora_inicio}.',
                    url_relacionada=f'/negocios/panel/{reserva.peluquero.id}/'
                )
                
                self.stdout.write(f"✅ Inasistencia marcada: {reserva.cliente.username} - {reserva.fecha} {reserva.hora_inicio}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error procesando inasistencia {reserva.id}: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f"✅ Proceso completado: {inasistencias_marcadas} inasistencias marcadas")
        )
        
        # Estadísticas adicionales
        total_inasistencias = Reserva.objects.filter(estado='inasistencia').count()
        self.stdout.write(f"📊 Total de inasistencias en el sistema: {total_inasistencias}") 