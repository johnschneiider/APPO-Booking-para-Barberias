#!/usr/bin/env python
"""
Script para verificar el estado del mensaje en Twilio
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def verificar_estado_mensaje():
    """Verificar el estado del último mensaje enviado"""
    print("🔍 Verificando estado del mensaje en Twilio...")
    
    try:
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        
        # Message ID del último mensaje enviado
        message_id = "MM543c9a73135281f60f8f7b13ec9fc385"
        
        print(f"📱 Verificando mensaje: {message_id}")
        
        # Obtener estado del mensaje
        estado = twilio_whatsapp_service.get_message_status(message_id)
        
        print(f"✅ Estado del mensaje: {estado}")
        
        if estado.get('success'):
            data = estado.get('data', {})
            print(f"📊 Detalles del mensaje:")
            print(f"   - SID: {data.get('sid')}")
            print(f"   - Estado: {data.get('status')}")
            print(f"   - Para: {data.get('to')}")
            print(f"   - De: {data.get('from')}")
            print(f"   - Creado: {data.get('date_created')}")
            print(f"   - Enviado: {data.get('date_sent')}")
            print(f"   - Actualizado: {data.get('date_updated')}")
            
            # Interpretar el estado
            status = data.get('status', '')
            if status == 'queued':
                print("⏳ El mensaje está en cola para envío")
            elif status == 'sent':
                print("✅ El mensaje fue enviado exitosamente")
            elif status == 'delivered':
                print("📱 El mensaje fue entregado al destinatario")
            elif status == 'failed':
                print("❌ El mensaje falló al enviarse")
            elif status == 'undelivered':
                print("⚠️ El mensaje no pudo ser entregado")
            else:
                print(f"❓ Estado desconocido: {status}")
        else:
            print(f"❌ Error obteniendo estado: {estado.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_estado_mensaje()
