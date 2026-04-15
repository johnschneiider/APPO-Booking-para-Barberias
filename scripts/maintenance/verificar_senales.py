#!/usr/bin/env python
"""
Script para verificar el estado de las señales de recordatorios
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def verificar_senales():
    """Verifica si las señales están conectadas"""
    print("🔍 Verificando señales de recordatorios...")
    
    try:
        from django.db.models.signals import post_save, post_delete
        from recordatorios.signals import crear_recordatorios_reserva, eliminar_recordatorios_reserva
        
        # Verificar señales conectadas
        print(f"✅ Señales importadas correctamente")
        
        # Verificar si están conectadas a post_save
        receivers = post_save._live_receivers
        print(f"📡 Receivers conectados a post_save: {len(receivers)}")
        
        # Buscar señales específicas
        reserva_receivers = [r for r in receivers if hasattr(r, 'sender_name') and r.sender_name == 'clientes.Reserva']
        print(f"🎯 Receivers para Reserva: {len(reserva_receivers)}")
        
        if reserva_receivers:
            print("✅ Señales de reserva conectadas")
            return True
        else:
            print("❌ Señales de reserva NO conectadas")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando señales: {e}")
        return False

def conectar_senales():
    """Conecta las señales si no están conectadas"""
    print("\n🔌 Conectando señales...")
    
    try:
        from django.db.models.signals import post_save, post_delete
        from recordatorios.signals import crear_recordatorios_reserva, eliminar_recordatorios_reserva
        from clientes.models import Reserva
        
        # Conectar señales
        post_save.connect(crear_recordatorios_reserva, sender=Reserva)
        post_delete.connect(eliminar_recordatorios_reserva, sender=Reserva)
        
        print("✅ Señales conectadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando señales: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando sistema de señales de recordatorios...\n")
    
    # Verificar estado actual
    senales_ok = verificar_senales()
    
    if not senales_ok:
        print("\n⚠️  Las señales no están conectadas")
        print("🔌 Conectando señales...")
        
        if conectar_senales():
            print("\n🎉 ¡Señales conectadas exitosamente!")
            print("💡 Ahora los recordatorios se crearán automáticamente")
        else:
            print("\n❌ Error conectando señales")
    else:
        print("\n✅ Las señales ya están conectadas")

if __name__ == '__main__':
    main()
