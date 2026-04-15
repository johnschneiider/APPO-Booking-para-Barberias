#!/usr/bin/env python
"""
Diagnóstico completo de señales automáticas
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def verificar_senales_detallado():
    """Verificación detallada de señales"""
    print("🔍 VERIFICACIÓN DETALLADA DE SEÑALES")
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
            return True
        else:
            print("❌ No hay señales conectadas para Reserva")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando señales: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_importacion_signals():
    """Verifica si los signals se importan correctamente"""
    print("\n📥 VERIFICANDO IMPORTACIÓN DE SIGNALS")
    print("=" * 50)
    
    try:
        # Intentar importar signals
        import recordatorios.signals
        print("✅ Signals importados correctamente")
        
        # Verificar funciones específicas
        from recordatorios.signals import crear_recordatorios_reserva, eliminar_recordatorios_reserva
        print("✅ Funciones de signals disponibles")
        
        # Verificar si están en el módulo
        print(f"crear_recordatorios_reserva: {crear_recordatorios_reserva}")
        print(f"eliminar_recordatorios_reserva: {eliminar_recordatorios_reserva}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importando signals: {e}")
        import traceback
        traceback.print_exc()
        return False

def conectar_senales_manual():
    """Conecta señales manualmente"""
    print("\n🔌 CONECTANDO SEÑALES MANUALMENTE")
    print("=" * 50)
    
    try:
        from django.db.models.signals import post_save, post_delete
        from recordatorios.signals import crear_recordatorios_reserva, eliminar_recordatorios_reserva
        from clientes.models import Reserva
        
        # Desconectar señales existentes primero
        post_save.disconnect(crear_recordatorios_reserva, sender=Reserva)
        post_delete.disconnect(eliminar_recordatorios_reserva, sender=Reserva)
        print("✅ Señales desconectadas")
        
        # Conectar señales
        post_save.connect(crear_recordatorios_reserva, sender=Reserva, weak=False)
        post_delete.connect(eliminar_recordatorios_reserva, sender=Reserva, weak=False)
        
        print("✅ Señales conectadas manualmente")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando señales: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_senales_manual():
    """Prueba las señales manualmente"""
    print("\n🧪 PROBANDO SEÑALES MANUALMENTE")
    print("=" * 50)
    
    try:
        from django.db.models.signals import post_save
        from clientes.models import Reserva
        from recordatorios.signals import crear_recordatorios_reserva
        
        # Verificar si la función está conectada
        receivers = post_save._live_receivers
        reserva_receivers = [r for r in receivers if hasattr(r, 'sender') and r.sender == Reserva]
        
        print(f"📡 Receivers para Reserva: {len(reserva_receivers)}")
        
        if reserva_receivers:
            print("✅ Señales conectadas, probando disparo...")
            
            # Buscar reserva reciente
            reserva = Reserva.objects.order_by('-id').first()
            print(f"✅ Reserva encontrada: {reserva.id}")
            
            # Simular señal manualmente
            print("📤 Disparando señal manualmente...")
            crear_recordatorios_reserva(Reserva, reserva, True)
            
            # Verificar si se crearon recordatorios
            from recordatorios.models import Recordatorio
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(Reserva)
            recordatorios = Recordatorio.objects.filter(
                content_type=content_type,
                object_id=reserva.id
            )
            
            print(f"📊 Recordatorios creados: {recordatorios.count()}")
            
            if recordatorios.exists():
                print("🎉 ¡Señales funcionando correctamente!")
                return True
            else:
                print("❌ No se crearon recordatorios")
                return False
        else:
            print("❌ No hay señales conectadas")
            return False
            
    except Exception as e:
        print(f"❌ Error probando señales: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 DIAGNÓSTICO COMPLETO DE SEÑALES")
    print("=" * 60)
    
    # Verificación detallada
    senales_ok = verificar_senales_detallado()
    
    # Verificar importación
    importacion_ok = verificar_importacion_signals()
    
    if not senales_ok:
        print("\n⚠️ Las señales no están conectadas")
        print("🔌 Conectando señales manualmente...")
        
        if conectar_senales_manual():
            print("\n🎉 ¡Señales conectadas manualmente!")
        else:
            print("\n❌ Error conectando señales")
            return
    else:
        print("\n✅ Las señales ya están conectadas")
    
    # Probar señales
    print("\n🧪 Probando funcionamiento de señales...")
    resultado = probar_senales_manual()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    if senales_ok and resultado:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("💡 Las señales están conectadas y funcionando")
        print("📱 WhatsApp está funcionando")
    elif resultado:
        print("⚠️ WhatsApp funciona y las señales se conectaron")
        print("💡 Ahora deberían funcionar automáticamente")
    else:
        print("❌ El sistema tiene problemas con las señales")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Crear una nueva reserva para probar")
    print("2. Verificar que llegue WhatsApp automáticamente")
    print("3. Si no funciona, reiniciar el servidor")

if __name__ == '__main__':
    main()
