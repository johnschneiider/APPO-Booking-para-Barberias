#!/usr/bin/env python
"""
Script para verificar el estado real de mensajes en Twilio
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.utils import get_whatsapp_service

# Message SIDs del último test
message_sids = [
    'MMd4fe0b76ab44ae8d980e7ab9673770c4',  # Recordatorio día antes
    'MM4189a1d3e50c16cda26baff50f4ff5b4',  # Recordatorio 3 horas
]

print("="*60)
print("🔍 VERIFICANDO ESTADO DE MENSAJES EN TWILIO")
print("="*60)

whatsapp_service = get_whatsapp_service()
if not whatsapp_service or not whatsapp_service.is_enabled():
    print("❌ WhatsApp no está disponible")
    exit(1)

for i, message_sid in enumerate(message_sids, 1):
    print(f"\n📱 Mensaje {i}: {message_sid}")
    print("-" * 60)
    
    try:
        status_info = whatsapp_service.get_message_status(message_sid)
        
        if status_info and status_info.get('success'):
            # Los datos están en 'data'
            data = status_info.get('data', {})
            status = data.get('status', 'unknown')
            error_code = data.get('error_code')
            error_message = data.get('error_message', '')
            
            print(f"   Estado: {status}")
            
            if error_code:
                print(f"   Error Code: {error_code}")
                print(f"   Error Message: {error_message}")
                
                if error_code == '63112':
                    print("   ⚠️  PROBLEMA: Meta deshabilitó el WABA/sender")
                    print("      Acción: Revisar Meta Business Manager Account Quality")
                elif error_code == '63016':
                    print("   ⚠️  PROBLEMA: Template no aprobado o conversación no iniciada")
                    print("      Acción: Verificar template SID y que cliente haya iniciado conversación")
                elif error_code == '21211':
                    print("   ⚠️  PROBLEMA: Número inválido")
                elif error_code == '21656':
                    print("   ⚠️  PROBLEMA: Variables del template inválidas")
            else:
                print(f"   ✅ Sin errores reportados")
            
            # Información adicional
            print(f"   To: {data.get('to', 'N/A')}")
            print(f"   From: {data.get('from', 'N/A')}")
            print(f"   Date Sent: {data.get('date_sent', 'N/A')}")
            print(f"   Date Updated: {data.get('date_updated', 'N/A')}")
            
            # Estados posibles: queued, sending, sent, delivered, read, failed, undelivered
            if status in ['failed', 'undelivered']:
                print(f"\n   ❌ MENSAJE NO ENTREGADO (status: {status})")
                print(f"      Esto significa que Twilio no pudo entregar el mensaje a WhatsApp/Meta")
            elif status == 'delivered':
                print(f"\n   ✅ MENSAJE ENTREGADO A WHATSAPP")
            elif status == 'read':
                print(f"\n   ✅ MENSAJE LEÍDO POR EL CLIENTE")
            elif status in ['queued', 'sending', 'sent']:
                print(f"\n   ⏳ MENSAJE EN PROCESO (status: {status})")
                print(f"      - 'queued': Twilio lo tiene en cola")
                print(f"      - 'sending': Twilio lo está enviando a Meta")
                print(f"      - 'sent': Twilio lo envió, pero Meta aún no confirma entrega")
                print(f"      Puede tardar unos minutos en cambiar a 'delivered' o 'undelivered'")
            else:
                print(f"\n   ⚠️  Estado desconocido: {status}")
                
        elif status_info and not status_info.get('success'):
            print(f"   ❌ Error obteniendo estado: {status_info.get('error', 'Unknown error')}")
        else:
            print("   ❌ No se pudo obtener información del mensaje")
            
    except Exception as e:
        print(f"   ❌ Error verificando mensaje: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("📊 FIN DE VERIFICACIÓN")
print("="*60)
