#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.models import Reserva
from clientes.twilio_whatsapp_service import twilio_whatsapp_service

def probar_mensaje_personalizado():
    """Probar el nuevo mensaje personalizado de confirmación"""
    print("🎨 Probando mensaje personalizado de confirmación...")
    
    try:
        # Obtener la reserva 389
        reserva = Reserva.objects.get(id=389)
        print(f"📋 Reserva encontrada: {reserva.id}")
        print(f"👤 Cliente: {reserva.cliente.username}")
        print(f"📱 Teléfono: {reserva.cliente.telefono}")
        
        # Actualizar el teléfono al número correcto
        reserva.cliente.telefono = '3117451274'
        reserva.cliente.save()
        print(f"✅ Teléfono actualizado a: {reserva.cliente.telefono}")
        
        # Probar el nuevo mensaje personalizado
        print("📤 Enviando mensaje personalizado...")
        resultado = twilio_whatsapp_service.send_reserva_confirmada(reserva)
        
        print(f"✅ Resultado: {resultado}")
        
        if resultado.get('success'):
            print("🎉 ¡Mensaje personalizado enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_mensaje_personalizado()
