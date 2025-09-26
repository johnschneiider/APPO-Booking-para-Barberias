#!/usr/bin/env python
"""
Script para probar con un mensaje simple
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def probar_mensaje_simple():
    """Probar con un mensaje simple"""
    print("🔍 Probando con mensaje simple...")
    
    try:
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        
        # Probar con mensaje simple
        print("📱 Enviando mensaje simple...")
        resultado = twilio_whatsapp_service.send_text_message(
            "+573217247624",
            "Hola! Este es un mensaje de prueba desde Melissa 🚀"
        )
        
        print(f"✅ Resultado: {resultado}")
        
        if resultado.get('success'):
            print("🎉 ¡Mensaje simple enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
            
            # Verificar estado después de un momento
            import time
            print("⏳ Esperando 5 segundos para verificar estado...")
            time.sleep(5)
            
            message_id = resultado.get('message_id')
            estado = twilio_whatsapp_service.get_message_status(message_id)
            print(f"📊 Estado del mensaje simple: {estado}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_mensaje_simple()
