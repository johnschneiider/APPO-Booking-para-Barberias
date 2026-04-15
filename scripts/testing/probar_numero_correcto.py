#!/usr/bin/env python
"""
Script para probar con el número correcto 3117451274
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def probar_numero_correcto():
    """Probar con el número correcto"""
    print("🔍 Probando con el número correcto: 3117451274")
    
    try:
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        
        # Probar con el número correcto
        numero_correcto = "3117451274"
        
        print(f"📱 Enviando mensaje a: {numero_correcto}")
        resultado = twilio_whatsapp_service.send_text_message(
            numero_correcto,
            "¡Hola! Este es un mensaje de prueba desde Melissa 🚀"
        )
        
        print(f"✅ Resultado: {resultado}")
        
        if resultado.get('success'):
            print("🎉 ¡Mensaje enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
            
            # Verificar estado después de un momento
            import time
            print("⏳ Esperando 5 segundos para verificar estado...")
            time.sleep(5)
            
            message_id = resultado.get('message_id')
            estado = twilio_whatsapp_service.get_message_status(message_id)
            print(f"📊 Estado del mensaje: {estado}")
            
            if estado.get('success'):
                data = estado.get('data', {})
                status = data.get('status', '')
                print(f"📱 Estado final: {status}")
                
                if status == 'delivered':
                    print("✅ ¡Mensaje entregado exitosamente!")
                elif status == 'sent':
                    print("📤 Mensaje enviado, esperando entrega...")
                elif status == 'failed':
                    print("❌ Mensaje falló al entregarse")
                    print(f"   Error: {data.get('error_code', 'N/A')}")
                else:
                    print(f"❓ Estado: {status}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_numero_correcto()
