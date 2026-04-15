#!/usr/bin/env python
"""
Probar WhatsApp con la reserva 388 que ya existe
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def probar_whatsapp_reserva_388():
    """Probar WhatsApp con la reserva 388"""
    print("🎯 Probando WhatsApp con reserva 388...")
    
    try:
        from clientes.models import Reserva
        from clientes.meta_whatsapp_service import meta_whatsapp_service
        
        # Obtener la reserva 388
        reserva = Reserva.objects.get(id=388)
        
        print(f"✅ Reserva: {reserva.id}")
        print(f"✅ Cliente: {reserva.cliente.username}")
        print(f"✅ Teléfono: {reserva.cliente.telefono}")
        print(f"✅ Negocio: {reserva.peluquero.nombre}")
        print(f"✅ Fecha: {reserva.fecha}")
        print(f"✅ Hora: {reserva.hora_inicio}")
        
        # Enviar confirmación de reserva por WhatsApp
        print("\n📱 Enviando confirmación de reserva por WhatsApp...")
        resultado = meta_whatsapp_service.send_reserva_confirmada(reserva)
        
        print(f"Resultado: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Confirmación de reserva enviada por WhatsApp!")
            print(f"   Message ID: {resultado.get('message_id')}")
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

def probar_mensaje_personalizado():
    """Probar mensaje personalizado"""
    print("\n💬 Probando mensaje personalizado...")
    
    try:
        from clientes.meta_whatsapp_service import meta_whatsapp_service
        
        mensaje = """¡Hola! 👋

Tu reserva ha sido confirmada:

📍 Negocio: Hair Salon "Trendy"
📅 Fecha: 7 de septiembre de 2025
🕐 Hora: 4:00 PM
💇‍♀️ Servicio: Corte de cabello

¡Te esperamos! ✨"""
        
        resultado = meta_whatsapp_service.send_text_message(
            "+573117451274",
            mensaje
        )
        
        print(f"Resultado: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Mensaje personalizado enviado!")
            return True
        else:
            print(f"❌ Error: {resultado.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA DE WHATSAPP CON RESERVA 388")
    print("=" * 50)
    
    pruebas = [
        ("WhatsApp con reserva 388", probar_whatsapp_reserva_388),
        ("Mensaje personalizado", probar_mensaje_personalizado),
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
        print("🎉 ¡WhatsApp está funcionando perfectamente!")
        print("📱 Revisa WhatsApp en el número +573117451274")
        print("💡 Ahora puedes hacer reservas en la web y recibirás WhatsApp")
    else:
        print("⚠️  Las pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    main()
