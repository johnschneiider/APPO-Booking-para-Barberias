"""
Comando para enviar recordatorios automáticos
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from clientes.models import Reserva
from clientes.utils import get_whatsapp_service
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
        
        # Calcular fecha de mañana (en la zona horaria del proyecto)
        ahora = timezone.localtime(timezone.now())
        fecha_manana = (ahora + timezone.timedelta(days=1)).date()
        
        # Buscar reservas para mañana
        reservas_manana = Reserva.objects.filter(
            fecha=fecha_manana,
            estado__in=['pendiente', 'confirmado'],
            recordatorio_dia_enviado=False
        ).select_related('cliente', 'peluquero', 'servicio__servicio')
        
        if verbose:
            self.stdout.write(f'📊 Encontradas {reservas_manana.count()} reservas para mañana (sin recordatorio enviado)')
        
        enviados = 0
        errores = 0

        whatsapp_service = None
        if not dry_run:
            whatsapp_service = get_whatsapp_service()
            if not (whatsapp_service and whatsapp_service.is_enabled()):
                self.stdout.write(self.style.WARNING('⚠️  WhatsApp no disponible (no se enviarán recordatorios).'))
                return
        
        for reserva in reservas_manana:
            try:
                if verbose:
                    self.stdout.write(f'  📝 Procesando reserva #{reserva.id} - {reserva.cliente.username}')
                
                if not dry_run:
                    # Enviar recordatorio real
                    resultado = whatsapp_service.send_recordatorio_dia_antes(reserva)
                    
                    if resultado.get('success'):
                        enviados += 1
                        reserva.recordatorio_dia_enviado = True
                        reserva.save(update_fields=['recordatorio_dia_enviado'])
                        if verbose:
                            self.stdout.write(f'    ✅ Recordatorio enviado')
                    else:
                        errores += 1
                        if verbose:
                            self.stdout.write(f'    ❌ Error: {resultado.get("error") or resultado}')
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
        
        # Calcular rango de tiempo (3 horas desde ahora) en zona horaria local
        ahora = timezone.localtime(timezone.now())
        fin = ahora + timezone.timedelta(hours=3)
        
        # Buscar reservas en las próximas 3 horas (maneja cruce de medianoche)
        if fin.date() == ahora.date():
            reservas_proximas = Reserva.objects.filter(
                fecha=ahora.date(),
                hora_inicio__gte=ahora.time(),
                hora_inicio__lte=fin.time(),
                estado__in=['pendiente', 'confirmado'],
                recordatorio_tres_horas_enviado=False
            )
        else:
            reservas_proximas = Reserva.objects.filter(
                (
                    (Q(fecha=ahora.date(), hora_inicio__gte=ahora.time()))
                    | (Q(fecha=fin.date(), hora_inicio__lte=fin.time()))
                ),
                estado__in=['pendiente', 'confirmado'],
                recordatorio_tres_horas_enviado=False
            )

        reservas_proximas = reservas_proximas.select_related('cliente', 'peluquero', 'servicio__servicio')
        
        if verbose:
            self.stdout.write(f'📊 Encontradas {reservas_proximas.count()} reservas en las próximas 3 horas (sin recordatorio enviado)')
        
        enviados = 0
        errores = 0

        whatsapp_service = None
        if not dry_run:
            whatsapp_service = get_whatsapp_service()
            if not (whatsapp_service and whatsapp_service.is_enabled()):
                self.stdout.write(self.style.WARNING('⚠️  WhatsApp no disponible (no se enviarán recordatorios).'))
                return
        
        for reserva in reservas_proximas:
            try:
                if verbose:
                    self.stdout.write(f'  📝 Procesando reserva #{reserva.id} - {reserva.cliente.username}')
                
                if not dry_run:
                    # Enviar recordatorio real
                    resultado = whatsapp_service.send_recordatorio_tres_horas(reserva)
                    
                    if resultado.get('success'):
                        enviados += 1
                        reserva.recordatorio_tres_horas_enviado = True
                        reserva.save(update_fields=['recordatorio_tres_horas_enviado'])
                        if verbose:
                            self.stdout.write(f'    ✅ Recordatorio enviado')
                    else:
                        errores += 1
                        if verbose:
                            self.stdout.write(f'    ❌ Error: {resultado.get("error") or resultado}')
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
