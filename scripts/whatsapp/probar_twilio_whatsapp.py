#!/usr/bin/env python
"""
Script para probar Twilio WhatsApp
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def probar_twilio_whatsapp():
    """Probar Twilio WhatsApp"""
    print("🔍 Probando Twilio WhatsApp...")
    
    try:
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        
        print(f"✅ Servicio cargado")
        print(f"✅ Habilitado: {twilio_whatsapp_service.is_enabled()}")
        print(f"✅ Account SID: {twilio_whatsapp_service.account_sid}")
        print(f"✅ WhatsApp Number: {twilio_whatsapp_service.whatsapp_number}")
        
        # Probar mensaje de texto
        print("\n📱 Enviando mensaje de texto...")
        resultado = twilio_whatsapp_service.send_text_message(
            "+573117451274",
            "¡Hola! Prueba desde Melissa con Twilio WhatsApp 🚀"
        )
        
        print(f"Resultado: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Mensaje enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
            return True
        else:
            print(f"❌ Error: {resultado.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_template_twilio():
    """Probar template de Twilio"""
    print("\n📋 Probando template de Twilio...")
    
    try:
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        
        # Variables para el template
        variables = {
            "1": "12/1",  # Fecha
            "2": "3pm"    # Hora
        }
        
        resultado = twilio_whatsapp_service.send_template_message(
            "+573117451274",
            "HXb5b62575e6e4ff6129ad7c8efe1f983e",  # Content SID
            variables
        )
        
        print(f"Resultado template: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Template enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
            return True
        else:
            print(f"❌ Error: {resultado.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_con_reserva():
    """Probar con reserva real"""
    print("\n🎯 Probando con reserva real...")
    
    try:
        from clientes.models import Reserva
        from clientes.twilio_whatsapp_service import twilio_whatsapp_service
        
        # Buscar la reserva 388
        reserva = Reserva.objects.get(id=388)
        
        print(f"✅ Reserva: {reserva.id}")
        print(f"✅ Cliente: {reserva.cliente.username}")
        print(f"✅ Teléfono: {reserva.cliente.telefono}")
        print(f"✅ Negocio: {reserva.peluquero.nombre}")
        
        # Enviar confirmación
        resultado = twilio_whatsapp_service.send_reserva_confirmada(reserva)
        
        print(f"Resultado: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Confirmación de reserva enviada!")
            return True
        else:
            print(f"❌ Error: {resultado.get('error')}")
            return False
            
    except Reserva.DoesNotExist:
        print("❌ Reserva 388 no encontrada")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA DE TWILIO WHATSAPP")
    print("=" * 50)
    
    pruebas = [
        ("Twilio WhatsApp básico", probar_twilio_whatsapp),
        ("Template de Twilio", probar_template_twilio),
        ("Con reserva real", probar_con_reserva),
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
    print("📊 RESUMEN")
    print("=" * 50)
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{status} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Resultado: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos > 0:
        print("🎉 ¡Twilio WhatsApp está funcionando!")
        print("📱 Revisa WhatsApp en el número +573117451274")
    else:
        print("⚠️  Las pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    main()
