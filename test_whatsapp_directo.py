#!/usr/bin/env python
"""
Script de prueba para verificar el servicio de WhatsApp directo (sin Twilio)
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from clientes.whatsapp_service import WhatsAppService
from cuentas.models import UsuarioPersonalizado

def test_configuracion_whatsapp():
    """Prueba la configuración de WhatsApp Business API"""
    print("🔍 Verificando configuración de WhatsApp Business API...")
    
    config = getattr(settings, 'WHATSAPP_CONFIG', {})
    
    print(f"  ENABLED: {config.get('ENABLED', False)}")
    print(f"  API_URL: {config.get('API_URL', 'No configurado')}")
    print(f"  PHONE_NUMBER_ID: {config.get('PHONE_NUMBER_ID', 'No configurado')}")
    print(f"  ACCESS_TOKEN: {'✅ Configurado' if config.get('ACCESS_TOKEN') else '❌ No configurado'}")
    print(f"  VERIFY_TOKEN: {'✅ Configurado' if config.get('VERIFY_TOKEN') else '❌ No configurado'}")
    
    # Verificar si está habilitado
    if not config.get('ENABLED'):
        print("  ❌ WhatsApp no está habilitado en la configuración")
        return False
    
    if not config.get('ACCESS_TOKEN'):
        print("  ❌ No hay ACCESS_TOKEN configurado")
        return False
    
    print("  ✅ Configuración básica de WhatsApp OK")
    return True

def test_servicio_whatsapp():
    """Prueba el servicio de WhatsApp"""
    print("\n🔍 Verificando servicio de WhatsApp...")
    
    try:
        servicio = WhatsAppService()
        print("  ✅ Servicio de WhatsApp creado")
        
        # Verificar si está habilitado
        if servicio.is_enabled():
            print("  ✅ Servicio de WhatsApp habilitado")
            return servicio
        else:
            print("  ❌ Servicio de WhatsApp no está habilitado")
            return None
            
    except Exception as e:
        print(f"  ❌ Error creando servicio de WhatsApp: {e}")
        return None

def buscar_usuarios_con_telefono():
    """Busca usuarios con teléfono válido"""
    print("\n🔍 Buscando usuarios con teléfono...")
    
    usuarios = UsuarioPersonalizado.objects.filter(telefono__isnull=False).exclude(telefono='')
    
    if not usuarios:
        print("  ❌ No hay usuarios con teléfono configurado")
        return None
    
    print(f"  ✅ Encontrados {usuarios.count()} usuarios con teléfono:")
    for usuario in usuarios[:5]:  # Mostrar solo los primeros 5
        print(f"    - {usuario.username}: {usuario.telefono}")
    
    # Retornar el primer usuario con teléfono válido
    return usuarios.first()

def test_envio_mensaje(servicio, usuario):
    """Prueba el envío de un mensaje de WhatsApp"""
    print(f"\n🔍 Probando envío de mensaje a {usuario.username}...")
    
    try:
        # Formatear número de teléfono
        telefono_formateado = servicio.format_phone_number(usuario.telefono)
        print(f"  📱 Número original: {usuario.telefono}")
        print(f"  📱 Número formateado: {telefono_formateado}")
        
        # Mensaje de prueba
        mensaje = f"Hola {usuario.username}, este es un mensaje de prueba del sistema de recordatorios de APPO. Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        print(f"  💬 Mensaje: {mensaje[:100]}...")
        
        # Intentar enviar mensaje personalizado
        resultado = servicio.send_custom_message(telefono_formateado, mensaje)
        
        if resultado:
            print("  ✅ Mensaje enviado exitosamente")
        else:
            print("  ❌ Error enviando mensaje")
        
        return resultado
        
    except Exception as e:
        print(f"  ❌ Error en envío: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del servicio de WhatsApp directo...\n")
    
    # Test 1: Configuración de WhatsApp
    config_ok = test_configuracion_whatsapp()
    
    if not config_ok:
        print("\n❌ La configuración de WhatsApp no está completa")
        print("💡 Para configurar WhatsApp Business API necesitas:")
        print("   1. PHONE_NUMBER_ID de Facebook Developer")
        print("   2. ACCESS_TOKEN de Facebook Developer")
        print("   3. VERIFY_TOKEN personalizado")
        print("   4. Configurar webhook en Facebook Developer")
        return
    
    # Test 2: Servicio de WhatsApp
    servicio = test_servicio_whatsapp()
    
    if not servicio:
        print("\n❌ El servicio de WhatsApp no está funcionando")
        return
    
    # Test 3: Buscar usuario con teléfono
    usuario = buscar_usuarios_con_telefono()
    
    if not usuario:
        print("\n❌ No hay usuarios con teléfono para probar")
        return
    
    # Test 4: Envío de mensaje
    envio_ok = test_envio_mensaje(servicio, usuario)
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    print(f"  Configuración WhatsApp: {'✅' if config_ok else '❌'}")
    print(f"  Servicio WhatsApp: {'✅' if servicio else '❌'}")
    print(f"  Usuario con teléfono: {'✅' if usuario else '❌'}")
    print(f"  Mensaje enviado: {'✅' if envio_ok else '❌'}")
    
    if config_ok and servicio and usuario and envio_ok:
        print("\n🎉 ¡Todas las pruebas pasaron! WhatsApp está funcionando correctamente.")
        print("💡 Ahora puedes usar este servicio como fallback en el sistema de recordatorios.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        
        if not envio_ok:
            print("\n💡 Para que WhatsApp funcione correctamente:")
            print("   1. Verifica que el ACCESS_TOKEN sea válido")
            print("   2. Asegúrate de que el PHONE_NUMBER_ID sea correcto")
            print("   3. Verifica que el webhook esté configurado en Facebook Developer")
            print("   4. Los números de teléfono deben estar en formato internacional")

if __name__ == '__main__':
    from datetime import datetime
    main()
