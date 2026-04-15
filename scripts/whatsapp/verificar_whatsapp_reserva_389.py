#!/usr/bin/env python
"""
Script para verificar WhatsApp de la reserva 389
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def verificar_whatsapp_reserva_389():
    """Verificar WhatsApp de la reserva 389"""
    print("🔍 Verificando WhatsApp de la reserva 389...")
    
    try:
        from clientes.models import Reserva
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        
        # Buscar la reserva 389
        reserva = Reserva.objects.get(id=389)
        
        print(f"✅ Reserva encontrada: {reserva.id}")
        print(f"✅ Cliente: {reserva.cliente.username}")
        print(f"✅ Teléfono: {reserva.cliente.telefono}")
        print(f"✅ Negocio: {reserva.peluquero.nombre}")
        print(f"✅ Fecha: {reserva.fecha}")
        print(f"✅ Hora: {reserva.hora_inicio}")
        
        # Verificar si el servicio está habilitado
        print(f"\n🔧 Estado del servicio:")
        print(f"✅ Habilitado: {twilio_whatsapp_service.is_enabled()}")
        print(f"✅ Account SID: {twilio_whatsapp_service.account_sid}")
        print(f"✅ WhatsApp Number: {twilio_whatsapp_service.whatsapp_number}")
        
        # Enviar WhatsApp
        print(f"\n📱 Enviando WhatsApp...")
        resultado = twilio_whatsapp_service.send_reserva_confirmada(reserva)
        
        print(f"Resultado: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡WhatsApp enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
            
    except Reserva.DoesNotExist:
        print("❌ Reserva 389 no encontrada")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_whatsapp_reserva_389()
