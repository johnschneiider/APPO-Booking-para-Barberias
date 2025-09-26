#!/usr/bin/env python
"""
Script para diagnosticar por qué no llega WhatsApp automáticamente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def diagnosticar_whatsapp_automatico():
    """Diagnosticar el envío automático de WhatsApp"""
    print("🔍 DIAGNÓSTICO DE WHATSAPP AUTOMÁTICO")
    print("=" * 50)
    
    try:
        from clientes.models import Reserva
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        from clientes.utils import enviar_email_reserva_confirmada
        
        # Buscar la reserva 389
        reserva = Reserva.objects.get(id=389)
        
        print(f"✅ Reserva encontrada: {reserva.id}")
        print(f"✅ Cliente: {reserva.cliente.username}")
        print(f"✅ Teléfono: {reserva.cliente.telefono}")
        print(f"✅ ¿Tiene teléfono?: {bool(reserva.cliente.telefono)}")
        print(f"✅ Negocio: {reserva.peluquero.nombre}")
        
        # Verificar servicio de WhatsApp
        print(f"\n🔧 Estado del servicio de WhatsApp:")
        print(f"✅ Habilitado: {twilio_whatsapp_service.is_enabled()}")
        print(f"✅ Account SID: {twilio_whatsapp_service.account_sid}")
        print(f"✅ WhatsApp Number: {twilio_whatsapp_service.whatsapp_number}")
        
        # Simular el envío automático
        print(f"\n📱 Simulando envío automático...")
        resultado = enviar_email_reserva_confirmada(reserva)
        
        print(f"✅ Resultado del envío automático: {resultado}")
        
        if resultado:
            print("✅ ¡El envío automático funcionó!")
        else:
            print("❌ El envío automático falló")
            
        # Probar envío directo
        print(f"\n📱 Probando envío directo...")
        resultado_directo = twilio_whatsapp_service.send_reserva_confirmada(reserva)
        
        print(f"✅ Resultado envío directo: {resultado_directo}")
        
        if resultado_directo.get('success'):
            print("✅ ¡Envío directo funcionó!")
            print(f"   Message ID: {resultado_directo.get('message_id')}")
        else:
            print(f"❌ Error envío directo: {resultado_directo.get('error')}")
            
    except Reserva.DoesNotExist:
        print("❌ Reserva 389 no encontrada")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnosticar_whatsapp_automatico()
