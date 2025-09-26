#!/usr/bin/env python
"""
Prueba completa de WhatsApp Meta API con configuración directa
"""

import os
import sys
import django
from pathlib import Path

# Configurar variables de entorno antes de cargar Django
os.environ['META_WHATSAPP_ENABLED'] = 'True'
os.environ['META_WHATSAPP_PHONE_NUMBER_ID'] = '820173994505603'
os.environ['META_WHATSAPP_ACCESS_TOKEN'] = 'EAATS2umJcBMBPaMuSWbNzZC3sRYoKsDcavdJ8p79x7T3l7Ak2yp3uqhdlax1ji7lky3AY4UB1ucS7MjKUtrJvGSPcqxswlIGZCKjeAF1qRWpCv2LIrdvcJyCVa1iAWyFmZBzGX4RvayzsA2ZAqsqVyRNZATw6ZBEN93ZCT3yXzNr0yjXvQL4m7oBzfe1Lq83UFrx0eEZAalK6IKsRDzfZC8ITWzHggHg3M8H7fqcNfhR5KsSq9QZDZD'
os.environ['META_WHATSAPP_VERIFY_TOKEN'] = 'melissa_whatsapp_verify_2024'
os.environ['META_WHATSAPP_WEBHOOK_SECRET'] = 'melissa_webhook_secret_2024'
os.environ['META_WHATSAPP_API_VERSION'] = 'v22.0'
os.environ['META_WHATSAPP_WEBHOOK_URL'] = 'https://tu-dominio.com/clientes/meta-whatsapp/webhook/'

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')

try:
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

def probar_whatsapp_basico():
    """Prueba básica de WhatsApp"""
    print("\n🔍 Probando configuración básica...")
    
    try:
        from clientes.meta_whatsapp_service import meta_whatsapp_service
        
        print(f"✅ Servicio cargado correctamente")
        print(f"✅ Habilitado: {meta_whatsapp_service.is_enabled()}")
        print(f"✅ Phone Number ID: {meta_whatsapp_service.phone_number_id}")
        print(f"✅ API Version: {meta_whatsapp_service.api_version}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error cargando servicio: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_mensaje_texto():
    """Prueba envío de mensaje de texto"""
    print("\n📱 Probando envío de mensaje de texto...")
    
    try:
        from clientes.meta_whatsapp_service import meta_whatsapp_service
        
        # Número de prueba (ajusta si es necesario)
        telefono_prueba = "+573117451274"
        mensaje = "¡Hola! Este es un mensaje de prueba desde Melissa 🚀"
        
        print(f"Enviando a: {telefono_prueba}")
        print(f"Mensaje: {mensaje}")
        
        resultado = meta_whatsapp_service.send_text_message(telefono_prueba, mensaje)
        
        print(f"Resultado completo: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Mensaje enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
            return True
        else:
            print(f"❌ Error enviando mensaje: {resultado.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de mensaje: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_template_hello_world():
    """Prueba template hello_world"""
    print("\n📋 Probando template hello_world...")
    
    try:
        from clientes.meta_whatsapp_service import meta_whatsapp_service
        
        telefono_prueba = "+573117451274"
        
        resultado = meta_whatsapp_service.send_template_message(
            to_phone=telefono_prueba,
            template_name='hello_world',
            language_code='en_US'
        )
        
        print(f"Resultado template: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Template enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
            return True
        else:
            print(f"❌ Error enviando template: {resultado.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de template: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_sistema_recordatorios():
    """Prueba el sistema de recordatorios integrado"""
    print("\n🔔 Probando sistema de recordatorios...")
    
    try:
        from recordatorios.services import servicio_recordatorios
        from cuentas.models import UsuarioPersonalizado
        
        # Buscar un usuario con teléfono
        usuario = UsuarioPersonalizado.objects.filter(telefono__isnull=False).first()
        
        if not usuario:
            print("❌ No hay usuarios con teléfono configurado")
            return False
        
        print(f"Probando con usuario: {usuario.username} - {usuario.telefono}")
        
        # Crear un recordatorio de prueba
        from django.utils import timezone
        from recordatorios.models import TipoRecordatorio
        
        recordatorio = servicio_recordatorios.crear_recordatorio(
            tipo=TipoRecordatorio.RECORDATORIO_DIA_ANTES,
            destinatario=usuario,
            fecha_evento=timezone.now() + timezone.timedelta(days=1),
            canales=['whatsapp'],
            contexto_template={
                'mensaje': '¡Hola! Este es un recordatorio de prueba desde Melissa 🎉'
            }
        )
        
        print(f"Recordatorio creado: {recordatorio.id}")
        
        # Procesar el recordatorio inmediatamente
        resultado = servicio_recordatorios._procesar_recordatorio(recordatorio)
        
        print(f"Resultado procesamiento: {resultado}")
        
        if resultado.get('enviado'):
            print("✅ ¡Recordatorio enviado exitosamente!")
            return True
        else:
            print("❌ Error enviando recordatorio")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de recordatorios: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA COMPLETA DE META WHATSAPP API")
    print("=" * 50)
    
    pruebas = [
        ("Configuración básica", probar_whatsapp_basico),
        ("Mensaje de texto", probar_mensaje_texto),
        ("Template hello_world", probar_template_hello_world),
        ("Sistema de recordatorios", probar_sistema_recordatorios),
    ]
    
    resultados = []
    
    for nombre, funcion in pruebas:
        print(f"\n{'='*20} {nombre} {'='*20}")
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error en {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen
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
    
    if exitosos > 0:
        print("🎉 ¡Al menos una prueba funcionó! Revisa WhatsApp en el número +573117451274")
    else:
        print("⚠️  Todas las pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    main()
