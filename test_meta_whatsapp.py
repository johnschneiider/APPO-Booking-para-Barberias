#!/usr/bin/env python
"""
Script de prueba para Meta WhatsApp API
Usa las credenciales que obtuviste de Meta for Developers
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.meta_whatsapp_service import meta_whatsapp_service

def test_whatsapp_connection():
    """Prueba la conexión con Meta WhatsApp API"""
    print("🔍 Probando conexión con Meta WhatsApp API...")
    
    # Verificar configuración
    print(f"✅ Habilitado: {meta_whatsapp_service.is_enabled()}")
    print(f"✅ Phone Number ID: {meta_whatsapp_service.phone_number_id}")
    print(f"✅ API Version: {meta_whatsapp_service.api_version}")
    print(f"✅ Access Token: {'*' * 20}...{meta_whatsapp_service.access_token[-10:]}")
    
    return meta_whatsapp_service.is_enabled()

def test_hello_world_template():
    """Prueba el template hello_world que te dieron"""
    print("\n📱 Probando template 'hello_world'...")
    
    # Número de prueba (ajusta este número al tuyo)
    test_phone = "+573117451274"  # El número del curl que te dieron
    
    resultado = meta_whatsapp_service.send_template_message(
        to_phone=test_phone,
        template_name='hello_world',
        language_code='en_US'
    )
    
    if resultado.get('success'):
        print(f"✅ Template enviado exitosamente!")
        print(f"   Message ID: {resultado.get('message_id')}")
        return True
    else:
        print(f"❌ Error enviando template: {resultado.get('error')}")
        return False

def test_text_message():
    """Prueba envío de mensaje de texto simple"""
    print("\n💬 Probando mensaje de texto...")
    
    test_phone = "+573117451274"
    message = "¡Hola! Este es un mensaje de prueba desde Melissa con Meta WhatsApp API 🚀"
    
    resultado = meta_whatsapp_service.send_text_message(
        to_phone=test_phone,
        message=message
    )
    
    if resultado.get('success'):
        print(f"✅ Mensaje de texto enviado exitosamente!")
        print(f"   Message ID: {resultado.get('message_id')}")
        return True
    else:
        print(f"❌ Error enviando mensaje: {resultado.get('error')}")
        return False

def test_welcome_message():
    """Prueba mensaje de bienvenida interactivo"""
    print("\n🎉 Probando mensaje de bienvenida interactivo...")
    
    test_phone = "+573117451274"
    
    resultado = meta_whatsapp_service.send_welcome_message(test_phone)
    
    if resultado.get('success'):
        print(f"✅ Mensaje de bienvenida enviado exitosamente!")
        print(f"   Message ID: {resultado.get('message_id')}")
        return True
    else:
        print(f"❌ Error enviando bienvenida: {resultado.get('error')}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de Meta WhatsApp API")
    print("=" * 50)
    
    # Verificar conexión
    if not test_whatsapp_connection():
        print("❌ No se puede conectar con Meta WhatsApp API")
        print("   Verifica las credenciales en settings.py")
        return
    
    print("\n" + "=" * 50)
    print("📋 Ejecutando pruebas...")
    
    # Ejecutar pruebas
    tests = [
        ("Template hello_world", test_hello_world_template),
        ("Mensaje de texto", test_text_message),
        ("Mensaje de bienvenida", test_welcome_message),
    ]
    
    resultados = []
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {str(e)}")
            resultados.append((nombre, False))
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{status} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Resultado: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡Todas las pruebas pasaron! Meta WhatsApp API está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    main()
