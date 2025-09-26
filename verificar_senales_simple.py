#!/usr/bin/env python
"""
Verificación simple de señales
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def main():
    print("🔍 VERIFICANDO SEÑALES DE RECORDATORIOS")
    print("=" * 50)
    
    try:
        # Verificar si se importan los signals
        import recordatorios.signals
        print("✅ Signals importados correctamente")
        
        # Verificar funciones específicas
        from recordatorios.signals import crear_recordatorios_reserva, eliminar_recordatorios_reserva
        print("✅ Funciones de signals disponibles")
        
        # Verificar si están en el módulo
        print(f"crear_recordatorios_reserva: {crear_recordatorios_reserva}")
        print(f"eliminar_recordatorios_reserva: {eliminar_recordatorios_reserva}")
        
        # Verificar si hay receivers conectados
        from django.db.models.signals import post_save
        from clientes.models import Reserva
        
        # Obtener receivers de manera segura
        try:
            receivers = post_save._live_receivers
            print(f"📡 Total receivers: {len(receivers)}")
            
            # Buscar receivers para Reserva
            reserva_receivers = []
            for receiver in receivers:
                if hasattr(receiver, 'sender') and receiver.sender == Reserva:
                    reserva_receivers.append(receiver)
                    print(f"✅ Receiver para Reserva: {receiver.__name__}")
            
            print(f"🎯 Receivers para Reserva: {len(reserva_receivers)}")
            
            if reserva_receivers:
                print("✅ Las señales están conectadas correctamente")
                print("💡 Los recordatorios deberían crearse automáticamente")
            else:
                print("❌ No hay señales conectadas para Reserva")
                print("💡 Por eso no llegan los mensajes de WhatsApp")
                
        except Exception as e:
            print(f"⚠️ Error verificando receivers: {e}")
            print("💡 Esto indica que las señales no están conectadas")
            
    except Exception as e:
        print(f"❌ Error importando signals: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
