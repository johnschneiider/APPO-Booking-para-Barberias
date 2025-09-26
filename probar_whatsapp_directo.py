#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

try:
    from clientes.twilio_whatsapp_service import twilio_whatsapp_service
    
    print("🔍 Probando WhatsApp con número 3117451274...")
    
    # Probar mensaje simple
    resultado = twilio_whatsapp_service.send_text_message(
        "3117451274", 
        "¡Hola! Este es un mensaje de prueba desde Melissa 🚀"
    )
    
    print(f"✅ Resultado: {resultado}")
    
    if resultado.get('success'):
        print("🎉 ¡Mensaje enviado exitosamente!")
        print(f"   Message ID: {resultado.get('message_id')}")
        
        # Verificar estado
        import time
        print("⏳ Esperando 5 segundos...")
        time.sleep(5)
        
        message_id = resultado.get('message_id')
        estado = twilio_whatsapp_service.get_message_status(message_id)
        print(f"📊 Estado: {estado}")
        
        if estado.get('success'):
            data = estado.get('data', {})
            status = data.get('status', '')
            print(f"📱 Estado final: {status}")
            
            if status == 'delivered':
                print("✅ ¡Mensaje entregado!")
            elif status == 'sent':
                print("📤 Mensaje enviado")
            elif status == 'failed':
                print("❌ Mensaje falló")
            else:
                print(f"❓ Estado: {status}")
    else:
        print(f"❌ Error: {resultado.get('error')}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
