"""
Comando para enviar recordatorios automáticos
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from clientes.models import Reserva
from clientes.twilio_whatsapp_service import twilio_whatsapp_service
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Envía recordatorios automáticos de reservas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['dia_antes', 'tres_horas', 'todos'],
            default='todos',
            help='Tipo de recordatorio a enviar'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula el envío sin enviar realmente'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada'
        )
    
    def handle(self, *args, **options):
        tipo = options['tipo']
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        self.stdout.write(
            self.style.SUCCESS(f'🚀 Iniciando envío de recordatorios: {tipo}')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  MODO SIMULACIÓN - No se enviarán mensajes')
            )
        
        # Procesar según el tipo
        if tipo == 'dia_antes' or tipo == 'todos':
            self._enviar_recordatorios_dia_antes(dry_run, verbose)
        
        if tipo == 'tres_horas' or tipo == 'todos':
            self._enviar_recordatorios_tres_horas(dry_run, verbose)
    
    def _enviar_recordatorios_dia_antes(self, dry_run, verbose):
        """Envía recordatorios 24 horas antes de la cita"""
        self.stdout.write('\n📅 Procesando recordatorios de 1 día antes...')
        
        # Calcular fecha de mañana
        ahora = timezone.now()
        mañana = ahora + timezone.timedelta(days=1)
        fecha_mañana = mañana.date()
        
        # Buscar reservas para mañana
        reservas_mañana = Reserva.objects.filter(
            fecha=fecha_mañana,
            estado='confirmada'
        ).select_related('cliente', 'peluquero', 'servicio__servicio')
        
        if verbose:
            self.stdout.write(f'📊 Encontradas {reservas_mañana.count()} reservas para mañana')
        
        enviados = 0
        errores = 0
        
        for reserva in reservas_mañana:
            try:
                if verbose:
                    self.stdout.write(f'  📝 Procesando reserva #{reserva.id} - {reserva.cliente.username}')
                
                if not dry_run:
                    # Enviar recordatorio real
                    resultado = twilio_whatsapp_service.send_recordatorio_dia_antes(reserva)
                    
                    if resultado.get('success'):
                        enviados += 1
                        if verbose:
                            self.stdout.write(f'    ✅ Recordatorio enviado')
                    else:
                        errores += 1
                        if verbose:
                            self.stdout.write(f'    ❌ Error: {resultado.get("error")}')
                else:
                    # Simular envío
                    enviados += 1
                    if verbose:
                        self.stdout.write(f'    📤 Simulando envío de recordatorio')
                        
            except Exception as e:
                errores += 1
                logger.error(f"Error enviando recordatorio para reserva {reserva.id}: {e}")
                if verbose:
                    self.stdout.write(f'    💥 Error: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Recordatorios de 1 día: {enviados} enviados, {errores} errores')
        )
    
    def _enviar_recordatorios_tres_horas(self, dry_run, verbose):
        """Envía recordatorios 3 horas antes de la cita"""
        self.stdout.write('\n⏰ Procesando recordatorios de 3 horas antes...')
        
        # Calcular rango de tiempo (3 horas desde ahora)
        ahora = timezone.now()
        tres_horas_desde_ahora = ahora + timezone.timedelta(hours=3)
        
        # Buscar reservas en las próximas 3 horas
        reservas_proximas = Reserva.objects.filter(
            fecha=ahora.date(),
            hora_inicio__gte=ahora.time(),
            hora_inicio__lte=tres_horas_desde_ahora.time(),
            estado='confirmada'
        ).select_related('cliente', 'peluquero', 'servicio__servicio')
        
        if verbose:
            self.stdout.write(f'📊 Encontradas {reservas_proximas.count()} reservas en las próximas 3 horas')
        
        enviados = 0
        errores = 0
        
        for reserva in reservas_proximas:
            try:
                if verbose:
                    self.stdout.write(f'  📝 Procesando reserva #{reserva.id} - {reserva.cliente.username}')
                
                if not dry_run:
                    # Enviar recordatorio real
                    resultado = twilio_whatsapp_service.send_recordatorio_tres_horas(reserva)
                    
                    if resultado.get('success'):
                        enviados += 1
                        if verbose:
                            self.stdout.write(f'    ✅ Recordatorio enviado')
                    else:
                        errores += 1
                        if verbose:
                            self.stdout.write(f'    ❌ Error: {resultado.get("error")}')
                else:
                    # Simular envío
                    enviados += 1
                    if verbose:
                        self.stdout.write(f'    📤 Simulando envío de recordatorio')
                        
            except Exception as e:
                errores += 1
                logger.error(f"Error enviando recordatorio para reserva {reserva.id}: {e}")
                if verbose:
                    self.stdout.write(f'    💥 Error: {e}')
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Recordatorios de 3 horas: {enviados} enviados, {errores} errores')
        )
