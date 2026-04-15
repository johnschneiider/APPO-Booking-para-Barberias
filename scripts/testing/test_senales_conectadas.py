#!/usr/bin/env python
"""
Script para probar si las señales de recordatorios están conectadas y funcionando
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def test_senales():
    """Prueba si las señales están conectadas"""
    print("🧪 Probando señales de recordatorios...")
    
    try:
        from django.db.models.signals import post_save
        from clientes.models import Reserva
        
        # Verificar si hay receivers conectados
        receivers = post_save._live_receivers
        print(f"📡 Total receivers conectados: {len(receivers)}")
        
        # Buscar receivers específicos para Reserva
        reserva_receivers = []
        for receiver in receivers:
            if hasattr(receiver, 'sender'):
                if receiver.sender == Reserva:
                    reserva_receivers.append(receiver)
                    print(f"✅ Receiver encontrado: {receiver.__name__}")
        
        print(f"🎯 Receivers para Reserva: {len(reserva_receivers)}")
        
        if reserva_receivers:
            print("✅ Las señales están conectadas correctamente")
            return True
        else:
            print("❌ No hay señales conectadas para Reserva")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando señales: {e}")
        return False

def test_recordatorio_manual():
    """Prueba crear un recordatorio manualmente"""
    print("\n🧪 Probando creación manual de recordatorio...")
    
    try:
        from recordatorios.services import servicio_recordatorios
        from cuentas.models import UsuarioPersonalizado
        from clientes.models import Reserva
        
        # Buscar usuario con teléfono
        usuario = UsuarioPersonalizado.objects.filter(telefono__isnull=False).exclude(telefono='').first()
        
        if not usuario:
            print("❌ No hay usuarios con teléfono")
            return False
        
        print(f"✅ Usuario encontrado: {usuario.email} - Tel: {usuario.telefono}")
        
        # Buscar reserva reciente
        reserva = Reserva.objects.filter(cliente=usuario).order_by('-id').first()
        
        if not reserva:
            print("❌ No hay reservas para este usuario")
            return False
        
        print(f"✅ Reserva encontrada: ID {reserva.id} - Fecha: {reserva.fecha}")
        
        # Intentar crear recordatorio manualmente
        resultado = servicio_recordatorios.enviar_recordatorio_confirmacion(reserva)
        
        if resultado:
            print("✅ Recordatorio creado manualmente")
            return True
        else:
            print("❌ Error creando recordatorio manualmente")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba manual: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Probando sistema de señales de recordatorios...\n")
    
    # Probar señales
    senales_ok = test_senales()
    
    # Probar recordatorio manual
    manual_ok = test_recordatorio_manual()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"  Señales conectadas: {'✅' if senales_ok else '❌'}")
    print(f"  Recordatorio manual: {'✅' if manual_ok else '❌'}")
    
    if senales_ok and manual_ok:
        print("\n🎉 ¡El sistema está funcionando correctamente!")
        print("💡 Los recordatorios se crearán automáticamente al hacer reservas")
    elif manual_ok:
        print("\n⚠️  El sistema funciona manualmente pero las señales no están conectadas")
        print("💡 Necesitas reiniciar el servidor para que las señales se conecten")
    else:
        print("\n❌ El sistema tiene problemas")
        print("💡 Revisa la configuración y los logs")

if __name__ == '__main__':
    main()
