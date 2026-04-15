#!/usr/bin/env python
"""
Enviar mensaje de WhatsApp ahora mismo
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def enviar_mensaje_ahora():
    """Enviar mensaje de prueba ahora"""
    print("📱 Enviando mensaje de prueba...")
    
    try:
        from clientes.meta_whatsapp_service import meta_whatsapp_service
        
        mensaje = """🎉 ¡HOLA! 

Este es un mensaje de prueba desde Melissa.

Si recibes este mensaje, significa que WhatsApp está funcionando perfectamente.

¡Tu sistema de reservas ya puede enviar notificaciones por WhatsApp! 🚀

- Fecha: 5 de septiembre de 2025
- Hora: 8:18 PM
- Sistema: Melissa WhatsApp API"""
        
        resultado = meta_whatsapp_service.send_text_message(
            "+573117451274",
            mensaje
        )
        
        print(f"Resultado: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Mensaje enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
            print("📱 Revisa tu WhatsApp ahora")
            return True
        else:
            print(f"❌ Error: {resultado.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    enviar_mensaje_ahora()
