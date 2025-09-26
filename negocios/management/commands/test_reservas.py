from django.core.management.base import BaseCommand
from clientes.models import Reserva
from negocios.models import Negocio
from django.utils import timezone

class Command(BaseCommand):
    help = 'Test command to check reservations in database'

    def add_arguments(self, parser):
        parser.add_argument('--negocio_id', type=int, help='ID del negocio a verificar')

    def handle(self, *args, **options):
        negocio_id = options.get('negocio_id')
        
        if negocio_id:
            try:
                negocio = Negocio.objects.get(id=negocio_id)
                self.stdout.write(f"Verificando reservas para negocio: {negocio.nombre} (ID: {negocio.id})")
                
                # Verificar todas las reservas del negocio
                reservas = Reserva.objects.filter(peluquero=negocio)
                self.stdout.write(f"Total de reservas encontradas: {reservas.count()}")
                
                for reserva in reservas:
                    self.stdout.write(f"  - Reserva {reserva.id}: {reserva.cliente.username} - {reserva.fecha} {reserva.hora_inicio} - Estado: {reserva.estado}")
                
                # Verificar reservas de hoy
                hoy = timezone.now().date()
                reservas_hoy = reservas.filter(fecha=hoy)
                self.stdout.write(f"Reservas de hoy ({hoy}): {reservas_hoy.count()}")
                
                for reserva in reservas_hoy:
                    self.stdout.write(f"  - {reserva.cliente.username} - {reserva.hora_inicio} - {reserva.servicio.nombre if reserva.servicio else 'Sin servicio'}")
                
            except Negocio.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"No se encontró negocio con ID {negocio_id}"))
        else:
            # Mostrar todos los negocios
            negocios = Negocio.objects.all()
            self.stdout.write("Negocios disponibles:")
            for negocio in negocios:
                reservas_count = Reserva.objects.filter(peluquero=negocio).count()
                self.stdout.write(f"  - {negocio.nombre} (ID: {negocio.id}) - {reservas_count} reservas")
