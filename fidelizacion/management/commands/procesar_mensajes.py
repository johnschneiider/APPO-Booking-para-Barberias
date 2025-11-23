"""
Comando de gestión para procesar mensajes manualmente
"""
from django.core.management.base import BaseCommand
from fidelizacion.services import MensajeLoopService


class Command(BaseCommand):
    help = 'Procesa mensajes de fidelización pendientes manualmente'
    
    def handle(self, *args, **options):
        self.stdout.write('Procesando mensajes de fidelización...')
        
        # Crear instancia del servicio y procesar
        servicio = MensajeLoopService()
        servicio._procesar_mensajes()
        
        self.stdout.write(self.style.SUCCESS('Mensajes procesados exitosamente'))

