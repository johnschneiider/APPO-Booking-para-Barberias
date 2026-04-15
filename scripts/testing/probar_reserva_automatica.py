#!/usr/bin/env python
"""
Script para probar el envío automático de WhatsApp al hacer reservas
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def probar_reserva_automatica():
    """Probar el envío automático de WhatsApp"""
    print("🔍 Probando envío automático de WhatsApp...")
    
    try:
        from clientes.models import Reserva
        from clientes.utils import enviar_email_reserva_confirmada
        
        # Buscar la reserva 388
        reserva = Reserva.objects.get(id=388)
        
        print(f"✅ Reserva encontrada: {reserva.id}")
        print(f"✅ Cliente: {reserva.cliente.username}")
        print(f"✅ Teléfono: {reserva.cliente.telefono}")
        print(f"✅ Negocio: {reserva.peluquero.nombre}")
        
        # Simular el envío automático que ocurre al hacer una reserva
        print("\n📱 Simulando envío automático de WhatsApp...")
        resultado = enviar_email_reserva_confirmada(reserva)
        
        print(f"✅ Resultado: {resultado}")
        
        if resultado:
            print("🎉 ¡WhatsApp enviado automáticamente!")
            print("📱 Revisa tu WhatsApp en el número del cliente")
        else:
            print("❌ Error enviando WhatsApp automáticamente")
            
    except Reserva.DoesNotExist:
        print("❌ Reserva 388 no encontrada")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_reserva_automatica()
