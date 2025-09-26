#!/usr/bin/env python
"""
Script de prueba para verificar el sistema de recordatorios y WhatsApp
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from recordatorios.services import servicio_recordatorios
from cuentas.models import UsuarioPersonalizado
from clientes.models import Reserva
from datetime import datetime, timedelta

def test_configuracion_twilio():
    """Prueba la configuración de Twilio"""
    print("🔍 Verificando configuración de Twilio...")
    
    print(f"  TWILIO_ACCOUNT_SID: {getattr(settings, 'TWILIO_ACCOUNT_SID', 'No configurado')}")
    print(f"  TWILIO_AUTH_TOKEN: {getattr(settings, 'TWILIO_AUTH_TOKEN', 'No configurado')}")
    print(f"  TWILIO_WHATSAPP_NUMBER: {getattr(settings, 'TWILIO_WHATSAPP_NUMBER', 'No configurado')}")
    print(f"  TWILIO_SMS_NUMBER: {getattr(settings, 'TWILIO_SMS_NUMBER', 'No configurado')}")
    
    # Verificar si Twilio está disponible
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print("  ✅ Twilio client creado exitosamente")
        return True
    except Exception as e:
        print(f"  ❌ Error creando Twilio client: {e}")
        return False

def test_servicio_recordatorios():
    """Prueba el servicio de recordatorios"""
    print("\n🔍 Verificando servicio de recordatorios...")
    
    try:
        servicio = servicio_recordatorios
        print("  ✅ Servicio de recordatorios inicializado")
        
        # Verificar servicios disponibles
        print(f"  Email service: {'✅' if servicio.email_service else '❌'}")
        print(f"  WhatsApp service: {'✅' if servicio.whatsapp_service else '❌'}")
        print(f"  SMS service: {'✅' if servicio.sms_service else '❌'}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error en servicio de recordatorios: {e}")
        return False

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

def test_crear_recordatorio(usuario):
    """Prueba crear un recordatorio de prueba"""
    print(f"\n🔍 Probando creación de recordatorio para {usuario.username}...")
    
    try:
        # Crear recordatorio de prueba
        fecha_evento = datetime.now() + timedelta(hours=1)
        recordatorio = servicio_recordatorios.crear_recordatorio(
            tipo='custom',
            destinatario=usuario,
            fecha_evento=fecha_evento,
            canales=['whatsapp'],
            contexto_template={
                'usuario': usuario.username,
                'mensaje': 'Este es un mensaje de prueba del sistema de recordatorios',
                'fecha': fecha_evento.strftime('%d/%m/%Y %H:%M')
            }
        )
        
        print(f"  ✅ Recordatorio creado: {recordatorio.id}")
        print(f"  Estado: {recordatorio.estado}")
        print(f"  Canales: {recordatorio.canales_habilitados}")
        print(f"  Destinatario: {recordatorio.destinatario.username} - {recordatorio.destinatario.telefono}")
        
        return recordatorio
        
    except Exception as e:
        print(f"  ❌ Error creando recordatorio: {e}")
        return False

def test_envio_whatsapp(recordatorio):
    """Prueba el envío de WhatsApp"""
    print(f"\n🔍 Probando envío de WhatsApp a {recordatorio.destinatario.telefono}...")
    
    try:
        if not servicio_recordatorios.whatsapp_service:
            print("  ❌ Servicio de WhatsApp no disponible")
            return False
        
        # Verificar que el usuario tenga teléfono
        if not recordatorio.destinatario.telefono:
            print("  ❌ Usuario no tiene teléfono configurado")
            return False
        
        print(f"  📱 Enviando a: {recordatorio.destinatario.telefono}")
        
        # Procesar recordatorio inmediatamente
        resultado = servicio_recordatorios._procesar_recordatorio(recordatorio)
        
        print(f"  Resultado: {resultado}")
        
        if resultado.get('enviado'):
            print("  ✅ Recordatorio enviado exitosamente")
        else:
            print(f"  ❌ Error enviando: {resultado.get('error', 'Error desconocido')}")
        
        return resultado.get('enviado', False)
        
    except Exception as e:
        print(f"  ❌ Error en envío de WhatsApp: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema de recordatorios...\n")
    
    # Test 1: Configuración de Twilio
    twilio_ok = test_configuracion_twilio()
    
    # Test 2: Servicio de recordatorios
    servicio_ok = test_servicio_recordatorios()
    
    if not servicio_ok:
        print("\n❌ El servicio de recordatorios no está funcionando correctamente")
        return
    
    # Test 3: Buscar usuario con teléfono
    usuario = buscar_usuarios_con_telefono()
    
    if not usuario:
        print("\n❌ No hay usuarios con teléfono para probar WhatsApp")
        print("💡 Para probar WhatsApp, necesitas usuarios con números de teléfono válidos")
        return
    
    # Test 4: Crear recordatorio
    recordatorio = test_crear_recordatorio(usuario)
    
    if not recordatorio:
        print("\n❌ No se pudo crear el recordatorio de prueba")
        return
    
    # Test 5: Envío de WhatsApp
    whatsapp_ok = test_envio_whatsapp(recordatorio)
    
    # Resumen
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    print(f"  Twilio configurado: {'✅' if twilio_ok else '❌'}")
    print(f"  Servicio recordatorios: {'✅' if servicio_ok else '❌'}")
    print(f"  Usuario con teléfono: {'✅' if usuario else '❌'}")
    print(f"  Recordatorio creado: {'✅' if recordatorio else '❌'}")
    print(f"  WhatsApp enviado: {'✅' if whatsapp_ok else '❌'}")
    
    if twilio_ok and servicio_ok and usuario and recordatorio and whatsapp_ok:
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        
        if not whatsapp_ok:
            print("\n💡 Para que WhatsApp funcione correctamente:")
            print("   1. Asegúrate de que los usuarios tengan números de teléfono válidos")
            print("   2. Los números deben estar en formato internacional (+57... para Colombia)")
            print("   3. Verifica que Twilio tenga acceso al número de destino")

if __name__ == '__main__':
    main()
