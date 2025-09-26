#!/usr/bin/env python
"""
Script para configurar Meta WhatsApp API con las credenciales que obtuviste
"""

import os
import sys
from pathlib import Path

def configurar_variables_entorno():
    """Configura las variables de entorno para Meta WhatsApp"""
    
    print("🔧 Configurando Meta WhatsApp API...")
    
    # Credenciales que obtuviste
    config = {
        'META_WHATSAPP_ENABLED': 'True',
        'META_WHATSAPP_PHONE_NUMBER_ID': '820173994505603',
        'META_WHATSAPP_ACCESS_TOKEN': 'EAATS2umJcBMBPaMuSWbNzZC3sRYoKsDcavdJ8p79x7T3l7Ak2yp3uqhdlax1ji7lky3AY4UB1ucS7MjKUtrJvGSPcqxswlIGZCKjeAF1qRWpCv2LIrdvcJyCVa1iAWyFmZBzGX4RvayzsA2ZAqsqVyRNZATw6ZBEN93ZCT3yXzNr0yjXvQL4m7oBzfe1Lq83UFrx0eEZAalK6IKsRDzfZC8ITWzHggHg3M8H7fqcNfhR5KsSq9QZDZD',
        'META_WHATSAPP_VERIFY_TOKEN': 'melissa_whatsapp_verify_2024',
        'META_WHATSAPP_WEBHOOK_SECRET': 'melissa_webhook_secret_2024',
        'META_WHATSAPP_API_VERSION': 'v22.0',
        'META_WHATSAPP_WEBHOOK_URL': 'https://tu-dominio.com/clientes/meta-whatsapp/webhook/',
    }
    
    # Crear archivo .env
    env_content = "# Configuración de Meta WhatsApp API\n"
    env_content += "# Generado automáticamente\n\n"
    
    for key, value in config.items():
        env_content += f"{key}={value}\n"
    
    # Escribir archivo .env
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Archivo .env creado con las credenciales de Meta")
    
    # Mostrar configuración
    print("\n📋 Configuración aplicada:")
    for key, value in config.items():
        if 'TOKEN' in key or 'SECRET' in key:
            display_value = f"{'*' * 20}...{value[-10:]}" if len(value) > 20 else "***"
        else:
            display_value = value
        print(f"   {key}: {display_value}")
    
    return True

def mostrar_instrucciones():
    """Muestra las instrucciones para continuar"""
    
    print("\n" + "=" * 60)
    print("🚀 PRÓXIMOS PASOS")
    print("=" * 60)
    
    print("\n1️⃣  Configurar webhook en Meta for Developers:")
    print("   - Ve a: https://developers.facebook.com/apps")
    print("   - Selecciona tu aplicación")
    print("   - WhatsApp > Configuration")
    print("   - Webhook URL: https://tu-dominio.com/clientes/meta-whatsapp/webhook/")
    print("   - Verify Token: melissa_whatsapp_verify_2024")
    print("   - Suscribirse a: messages, message_deliveries, message_reads")
    
    print("\n2️⃣  Probar la conexión:")
    print("   python test_meta_whatsapp.py")
    
    print("\n3️⃣  Probar envío de mensaje:")
    print("   python manage.py shell")
    print("   >>> from clientes.meta_whatsapp_service import meta_whatsapp_service")
    print("   >>> resultado = meta_whatsapp_service.send_text_message('+573117451274', '¡Hola desde Melissa!')")
    print("   >>> print(resultado)")
    
    print("\n4️⃣  Verificar en WhatsApp:")
    print("   - Abre WhatsApp en el número +573117451274")
    print("   - Deberías recibir los mensajes de prueba")
    
    print("\n" + "=" * 60)
    print("📞 ¿Necesitas ayuda?")
    print("   - Revisa los logs en: logs/django.log")
    print("   - Verifica que el número esté en formato internacional")
    print("   - Asegúrate de que el token no haya expirado")

def main():
    """Función principal"""
    print("🎯 Configurador de Meta WhatsApp API para Melissa")
    print("=" * 50)
    
    try:
        # Configurar variables de entorno
        configurar_variables_entorno()
        
        # Mostrar instrucciones
        mostrar_instrucciones()
        
        print("\n✅ ¡Configuración completada!")
        print("   Ahora puedes ejecutar las pruebas con: python test_meta_whatsapp.py")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()
