#!/usr/bin/env python
"""
Script final para probar WhatsApp con reservas reales
"""

import os
import django
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def probar_whatsapp_directo():
    """Probar WhatsApp directamente"""
    print("🔍 Probando WhatsApp Meta API...")
    
    try:
        from clientes.meta_whatsapp_service import meta_whatsapp_service
        
        print(f"✅ Servicio cargado")
        print(f"✅ Habilitado: {meta_whatsapp_service.is_enabled()}")
        print(f"✅ Phone Number ID: {meta_whatsapp_service.phone_number_id}")
        
        # Probar mensaje simple
        resultado = meta_whatsapp_service.send_text_message(
            "+573117451274",
            "¡Hola! Prueba desde Melissa 🚀"
        )
        
        print(f"Resultado mensaje: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Mensaje enviado exitosamente!")
            return True
        else:
            print(f"❌ Error: {resultado.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_con_reserva_real():
    """Probar con la reserva que se creó (ID: 388)"""
    print("\n🎯 Probando con reserva real...")
    
    try:
        from clientes.models import Reserva
        from clientes.utils import enviar_email_reserva_confirmada
        
        # Buscar la reserva 388 que se creó
        reserva = Reserva.objects.get(id=388)
        
        print(f"✅ Reserva encontrada: {reserva.id}")
        print(f"✅ Cliente: {reserva.cliente.username}")
        print(f"✅ Teléfono: {reserva.cliente.telefono}")
        print(f"✅ Negocio: {reserva.peluquero.nombre}")
        print(f"✅ Fecha: {reserva.fecha}")
        print(f"✅ Hora: {reserva.hora_inicio}")
        
        # Enviar confirmación (esto incluirá WhatsApp)
        print("\n📱 Enviando confirmación de reserva...")
        resultado = enviar_email_reserva_confirmada(reserva)
        
        if resultado:
            print("✅ ¡Confirmación enviada exitosamente!")
            print("   (Incluye email + WhatsApp)")
            return True
        else:
            print("❌ Error enviando confirmación")
            return False
            
    except Reserva.DoesNotExist:
        print("❌ Reserva 388 no encontrada")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_con_nueva_reserva():
    """Crear una nueva reserva de prueba"""
    print("\n🆕 Creando nueva reserva de prueba...")
    
    try:
        from clientes.models import Reserva, Negocio, ServicioNegocio
        from cuentas.models import UsuarioPersonalizado
        from django.utils import timezone
        
        # Buscar un negocio activo
        negocio = Negocio.objects.filter(activo=True).first()
        if not negocio:
            print("❌ No hay negocios activos")
            return False
        
        # Buscar un servicio
        servicio = ServicioNegocio.objects.filter(negocio=negocio).first()
        if not servicio:
            print("❌ No hay servicios para el negocio")
            return False
        
        # Buscar un usuario con teléfono
        usuario = UsuarioPersonalizado.objects.filter(telefono__isnull=False).first()
        if not usuario:
            print("❌ No hay usuarios con teléfono")
            return False
        
        print(f"✅ Usando negocio: {negocio.nombre}")
        print(f"✅ Usando servicio: {servicio.servicio.nombre}")
        print(f"✅ Usando usuario: {usuario.username} - {usuario.telefono}")
        
        # Crear reserva de prueba
        reserva = Reserva.objects.create(
            cliente=usuario,
            peluquero=negocio,
            servicio=servicio,
            fecha=timezone.now().date() + timezone.timedelta(days=1),
            hora_inicio=timezone.now().time().replace(hour=10, minute=0),
            estado='confirmado'
        )
        
        print(f"✅ Reserva creada: {reserva.id}")
        
        # Enviar confirmación
        from clientes.utils import enviar_email_reserva_confirmada
        resultado = enviar_email_reserva_confirmada(reserva)
        
        if resultado:
            print("✅ ¡Confirmación enviada exitosamente!")
            return True
        else:
            print("❌ Error enviando confirmación")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 PRUEBA FINAL DE WHATSAPP CON RESERVAS")
    print("=" * 50)
    
    pruebas = [
        ("WhatsApp directo", probar_whatsapp_directo),
        ("Con reserva real (388)", probar_con_reserva_real),
        ("Con nueva reserva", probar_con_nueva_reserva),
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
    print("📊 RESUMEN FINAL")
    print("=" * 50)
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "✅ EXITOSO" if resultado else "❌ FALLIDO"
        print(f"{status} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Resultado: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos > 0:
        print("🎉 ¡WhatsApp está funcionando! Revisa el número +573117451274")
        print("📱 Deberías recibir mensajes de confirmación de reservas")
    else:
        print("⚠️  Todas las pruebas fallaron. Revisa la configuración.")
    
    print("\n💡 Para probar en la web:")
    print("   1. Ve a http://127.0.0.1:8000/")
    print("   2. Haz una reserva")
    print("   3. Revisa WhatsApp en el número del cliente")

if __name__ == "__main__":
    main()
