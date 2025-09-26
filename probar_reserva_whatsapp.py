#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.models import Reserva
from clientes.utils import enviar_email_reserva_confirmada

def probar_reserva_whatsapp():
    """Probar el envío automático de WhatsApp para una reserva"""
    print("🔍 Probando envío automático de WhatsApp para reserva...")
    
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
        
        # Probar el envío automático
        print("📤 Enviando notificación de reserva...")
        resultado = enviar_email_reserva_confirmada(reserva)
        
        if resultado:
            print("🎉 ¡Notificación de WhatsApp enviada exitosamente!")
        else:
            print("❌ No se pudo enviar la notificación")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_reserva_whatsapp()