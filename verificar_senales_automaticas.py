#!/usr/bin/env python
"""
Script para verificar y conectar señales automáticas
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def verificar_senales():
    """Verifica si las señales están conectadas"""
    print("🔍 Verificando señales automáticas...")
    
    try:
        from django.db.models.signals import post_save
        from clientes.models import Reserva
        
        # Verificar receivers conectados
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

def conectar_senales():
    """Conecta las señales si no están conectadas"""
    print("\n🔌 Conectando señales...")
    
    try:
        from django.db.models.signals import post_save, post_delete
        from recordatorios.signals import crear_recordatorios_reserva, eliminar_recordatorios_reserva
        from clientes.models import Reserva
        
        # Conectar señales
        post_save.connect(crear_recordatorios_reserva, sender=Reserva, weak=False)
        post_delete.connect(eliminar_recordatorios_reserva, sender=Reserva, weak=False)
        
        print("✅ Señales conectadas exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error conectando señales: {e}")
        return False

def probar_reserva_existente():
    """Prueba crear recordatorios para una reserva existente"""
    print("\n🧪 Probando con reserva existente...")
    
    try:
        from recordatorios.services import servicio_recordatorios
        from clientes.models import Reserva
        
        # Buscar reserva reciente (384)
        reserva = Reserva.objects.get(id=384)
        print(f"✅ Reserva encontrada: {reserva.id}")
        print(f"Cliente: {reserva.cliente.email}")
        print(f"Teléfono: {reserva.cliente.telefono}")
        
        # Crear recordatorio manualmente
        print("📱 Creando recordatorio de confirmación...")
        resultado = servicio_recordatorios.enviar_recordatorio_confirmacion(reserva)
        
        if resultado:
            print("✅ Recordatorio creado manualmente")
            print("📤 Enviando WhatsApp...")
            
            # Buscar y enviar el recordatorio
            from recordatorios.models import Recordatorio
            from django.contrib.contenttypes.models import ContentType
            
            content_type = ContentType.objects.get_for_model(Reserva)
            recordatorio = Recordatorio.objects.filter(
                content_type=content_type,
                object_id=reserva.id,
                tipo='reserva_confirmada'
            ).order_by('-fecha_creacion').first()
            
            if recordatorio:
                print(f"✅ Recordatorio encontrado: ID {recordatorio.id}")
                print(f"Estado: {recordatorio.estado}")
                
                # Enviar ahora
                if recordatorio.estado == 'pendiente':
                    servicio_recordatorios._procesar_recordatorio(recordatorio)
                    
                    # Verificar estado
                    recordatorio.refresh_from_db()
                    print(f"Estado después del envío: {recordatorio.estado}")
                    
                    if recordatorio.estado == 'enviado':
                        print("🎉 ¡WhatsApp enviado exitosamente!")
                        return True
                    else:
                        print(f"⚠️ Estado: {recordatorio.estado}")
                        return False
                else:
                    print(f"⚠️ Recordatorio no está pendiente: {recordatorio.estado}")
                    return False
            else:
                print("❌ No se encontró el recordatorio")
                return False
        else:
            print("❌ Error creando recordatorio")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 VERIFICANDO SEÑALES AUTOMÁTICAS")
    print("=" * 50)
    
    # Verificar señales
    senales_ok = verificar_senales()
    
    if not senales_ok:
        print("\n⚠️ Las señales no están conectadas")
        print("🔌 Conectando señales...")
        
        if conectar_senales():
            print("\n🎉 ¡Señales conectadas exitosamente!")
            print("💡 Ahora los recordatorios se crearán automáticamente")
        else:
            print("\n❌ Error conectando señales")
            return
    else:
        print("\n✅ Las señales ya están conectadas")
    
    # Probar con reserva existente
    print("\n🧪 Probando sistema completo...")
    resultado = probar_reserva_existente()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    
    if senales_ok and resultado:
        print("🎉 ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
        print("💡 Los recordatorios se crearán automáticamente")
        print("📱 WhatsApp está funcionando")
    elif resultado:
        print("⚠️ WhatsApp funciona pero las señales no están conectadas")
        print("💡 Necesitas reiniciar el servidor")
    else:
        print("❌ El sistema tiene problemas")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Reiniciar el servidor Django")
    print("2. Crear una nueva reserva para probar")
    print("3. Verificar que llegue WhatsApp automáticamente")

if __name__ == '__main__':
    main()
