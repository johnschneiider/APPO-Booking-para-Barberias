#!/usr/bin/env python
"""
Script para verificar la configuración de Twilio
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def verificar_configuracion_twilio():
    """Verificar la configuración de Twilio"""
    print("🔍 Verificando configuración de Twilio...")
    
    try:
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        
        print(f"✅ Account SID: {twilio_whatsapp_service.account_sid}")
        print(f"✅ Auth Token: {twilio_whatsapp_service.auth_token[:10]}...")
        print(f"✅ WhatsApp Number: {twilio_whatsapp_service.whatsapp_number}")
        print(f"✅ Habilitado: {twilio_whatsapp_service.is_enabled()}")
        
        # Probar con diferentes formatos de número
        numeros_prueba = [
            "+573217247624",
            "573217247624", 
            "3217247624",
            "+57 321 724 7624",
            "57 321 724 7624"
        ]
        
        print(f"\n📱 Probando diferentes formatos de número:")
        for numero in numeros_prueba:
            print(f"   Probando: {numero}")
            resultado = twilio_whatsapp_service.send_text_message(
                numero,
                f"Prueba con formato: {numero}"
            )
            print(f"   Resultado: {resultado.get('success', False)}")
            if resultado.get('success'):
                print(f"   ✅ ¡Éxito con formato: {numero}!")
                break
            else:
                print(f"   ❌ Falló: {resultado.get('error', 'Error desconocido')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verificar_configuracion_twilio()
