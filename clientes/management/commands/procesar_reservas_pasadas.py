from django.core.management.base import BaseCommand
from clientes.utils import procesar_reservas_pasadas
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Procesa automáticamente las reservas que ya pasaron y las marca como completadas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular el proceso sin hacer cambios reales'
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        
        if dry_run:
            self.stdout.write("🔍 MODO SIMULACIÓN - No se realizarán cambios reales")
        
        try:
            # Procesar reservas pasadas
            completadas = procesar_reservas_pasadas()
            
            if completadas > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Se procesaron {completadas} reservas pasadas automáticamente'
                    )
                )
                
                # Mostrar detalles de las reservas procesadas
                from clientes.models import Reserva
                from django.utils import timezone
                
                reservas_recientes = Reserva.objects.filter(
                    estado='completado',
                    fecha__lt=timezone.now().date()
                ).order_by('-fecha', '-hora_inicio')[:5]
                
                if reservas_recientes:
                    self.stdout.write("\n📋 Últimas reservas procesadas:")
                    for reserva in reservas_recientes:
                        self.stdout.write(
                            f"   • {reserva.cliente.username} - {reserva.fecha} {reserva.hora_inicio} "
                            f"({reserva.peluquero.nombre})"
                        )
            else:
                self.stdout.write(
                    self.style.WARNING('ℹ️ No hay reservas pasadas para procesar')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error procesando reservas pasadas: {str(e)}')
            )
            logger.error(f"Error en comando procesar_reservas_pasadas: {str(e)}") 