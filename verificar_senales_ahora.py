#!/usr/bin/env python
"""
Verificar estado actual de señales después de reiniciar servidor
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def main():
    print("🔍 VERIFICANDO ESTADO ACTUAL DE SEÑALES")
    print("=" * 50)
    
    try:
        from django.db.models.signals import post_save
        from clientes.models import Reserva
        
        # Verificar receivers conectados
        receivers = post_save._live_receivers
        print(f"📡 Total receivers conectados: {len(receivers)}")
        
        # Buscar receivers específicos para Reserva
        reserva_receivers = []
        for i, receiver in enumerate(receivers):
            print(f"Receiver {i}: {receiver}")
            if hasattr(receiver, 'sender'):
                if receiver.sender == Reserva:
                    reserva_receivers.append(receiver)
                    print(f"✅ Receiver para Reserva: {receiver.__name__}")
        
        print(f"\n🎯 Receivers para Reserva: {len(reserva_receivers)}")
        
        if reserva_receivers:
            print("✅ Las señales están conectadas correctamente")
            print("💡 Los recordatorios deberían crearse automáticamente")
        else:
            print("❌ No hay señales conectadas para Reserva")
            print("💡 Por eso no llegan los mensajes de WhatsApp")
            
    except Exception as e:
        print(f"❌ Error verificando señales: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
