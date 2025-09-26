#!/usr/bin/env python
"""
Script para probar el envío automático de WhatsApp
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def probar_whatsapp_automatico():
    """Probar el envío automático de WhatsApp"""
    print("🔍 Probando envío automático de WhatsApp...")
    
    try:
        from clientes.models import Reserva
        from clientes.utils import enviar_email_reserva_confirmada
        
        # Buscar la reserva 389
        reserva = Reserva.objects.get(id=389)
        
        print(f"✅ Reserva: {reserva.id}")
        print(f"✅ Cliente: {reserva.cliente.username}")
        print(f"✅ Teléfono: {reserva.cliente.telefono}")
        
        # Simular el envío automático
        print(f"\n📱 Enviando notificación automática...")
        resultado = enviar_email_reserva_confirmada(reserva)
        
        print(f"✅ Resultado: {resultado}")
        
        if resultado:
            print("🎉 ¡Notificación enviada exitosamente!")
        else:
            print("❌ No se pudo enviar la notificación")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_whatsapp_automatico()
