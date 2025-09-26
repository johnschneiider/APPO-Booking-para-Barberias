from django.core.management.base import BaseCommand
from clientes.whatsapp_service import whatsapp_service
from clientes.models import Reserva
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Prueba las notificaciones de WhatsApp'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tipo',
            type=str,
            choices=['confirmada', 'cancelada', 'reagendada', 'recordatorio_dia', 'recordatorio_tres_horas', 'inasistencia'],
            help='Tipo de notificación a probar'
        )
        parser.add_argument(
            '--reserva-id',
            type=int,
            help='ID de la reserva para probar'
        )
        parser.add_argument(
            '--telefono',
            type=str,
            help='Número de teléfono para probar (sin reserva)'
        )

    def handle(self, *args, **options):
        tipo = options.get('tipo')
        reserva_id = options.get('reserva_id')
        telefono = options.get('telefono')
        
        if not whatsapp_service.is_enabled():
            self.stdout.write(
                self.style.ERROR('❌ WhatsApp no está habilitado. Verifica la configuración.')
            )
            return
        
        self.stdout.write("🔧 Probando servicio de WhatsApp...")
        
        if telefono:
            # Probar mensaje personalizado
            self.test_custom_message(telefono)
        elif reserva_id:
            # Probar con reserva específica
            self.test_with_reserva(reserva_id, tipo)
        else:
            # Probar con reserva de ejemplo
            self.test_with_sample_reserva(tipo)
    
    def test_custom_message(self, telefono):
        """Prueba mensaje personalizado"""
        self.stdout.write(f"📱 Enviando mensaje personalizado a {telefono}...")
        
        message = """🧪 Prueba de WhatsApp - Melissa

Este es un mensaje de prueba del sistema de notificaciones.

Funcionalidades disponibles:
• Confirmación de reservas
• Recordatorios automáticos
• Cancelaciones
• Reagendamientos
• Notificaciones de inasistencia

¡El sistema está funcionando correctamente! ✅"""
        
        success = whatsapp_service.send_custom_message(telefono, message)
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Mensaje enviado exitosamente a {telefono}")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Error enviando mensaje a {telefono}")
            )
    
    def test_with_reserva(self, reserva_id, tipo):
        """Prueba con reserva específica"""
        try:
            reserva = Reserva.objects.get(id=reserva_id)
            self.test_notification_type(reserva, tipo)
        except Reserva.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Reserva con ID {reserva_id} no encontrada")
            )
    
    def test_with_sample_reserva(self, tipo):
        """Prueba con reserva de ejemplo"""
        # Crear reserva de ejemplo para pruebas
        from cuentas.models import UsuarioPersonalizado
        from negocios.models import Negocio
        
        try:
            # Buscar usuario y negocio existentes
            usuario = UsuarioPersonalizado.objects.filter(tipo='cliente').first()
            negocio = Negocio.objects.filter(activo=True).first()
            
            if not usuario or not negocio:
                self.stdout.write(
                    self.style.ERROR("❌ No hay usuarios o negocios disponibles para la prueba")
                )
                return
            
            # Crear reserva de ejemplo
            reserva = Reserva.objects.create(
                cliente=usuario,
                peluquero=negocio,
                fecha=timezone.now().date() + timedelta(days=1),
                hora_inicio=timezone.now().time(),
                hora_fin=(timezone.now() + timedelta(minutes=30)).time(),
                estado='confirmado'
            )
            
            self.stdout.write(f"📋 Usando reserva de ejemplo: {reserva}")
            self.test_notification_type(reserva, tipo)
            
            # Limpiar reserva de ejemplo
            reserva.delete()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error creando reserva de ejemplo: {str(e)}")
            )
    
    def test_notification_type(self, reserva, tipo):
        """Prueba tipo específico de notificación"""
        if tipo == 'confirmada':
            self.stdout.write("📅 Probando notificación de reserva confirmada...")
            success = whatsapp_service.send_reserva_confirmada(reserva)
        elif tipo == 'cancelada':
            self.stdout.write("❌ Probando notificación de reserva cancelada...")
            success = whatsapp_service.send_reserva_cancelada(reserva, "Prueba del sistema")
        elif tipo == 'reagendada':
            self.stdout.write("🔄 Probando notificación de reserva reagendada...")
            fecha_anterior = reserva.fecha - timedelta(days=1)
            hora_anterior = reserva.hora_inicio
            success = whatsapp_service.send_reserva_reagendada(reserva, fecha_anterior, hora_anterior)
        elif tipo == 'recordatorio_dia':
            self.stdout.write("📅 Probando recordatorio de 1 día antes...")
            success = whatsapp_service.send_recordatorio_dia_antes(reserva)
        elif tipo == 'recordatorio_tres_horas':
            self.stdout.write("⏰ Probando recordatorio de 3 horas antes...")
            success = whatsapp_service.send_recordatorio_tres_horas(reserva)
        elif tipo == 'inasistencia':
            self.stdout.write("🚫 Probando notificación de inasistencia...")
            success = whatsapp_service.send_inasistencia(reserva, "Prueba del sistema")
        else:
            self.stdout.write("📱 Probando mensaje personalizado...")
            message = f"Prueba del sistema - Reserva #{reserva.id}"
            success = whatsapp_service.send_custom_message(reserva.cliente.telefono, message)
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Notificación de {tipo} enviada exitosamente")
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"❌ Error enviando notificación de {tipo}")
            ) 