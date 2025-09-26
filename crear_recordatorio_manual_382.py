#!/usr/bin/env python
"""
Script para crear un recordatorio manual para la reserva 382
y probar si WhatsApp está funcionando
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def crear_recordatorio_manual():
    """Crea un recordatorio manual para la reserva 382"""
    print("🚀 Creando recordatorio manual para reserva 382...")
    
    try:
        from recordatorios.services import servicio_recordatorios
        from clientes.models import Reserva
        
        # Buscar la reserva 382
        reserva = Reserva.objects.get(id=382)
        print(f"✅ Reserva encontrada: ID {reserva.id}")
        print(f"   Cliente: {reserva.cliente.email}")
        print(f"   Teléfono: {reserva.cliente.telefono}")
        print(f"   Fecha: {reserva.fecha}")
        print(f"   Hora: {reserva.hora_inicio}")
        print(f"   Profesional: {reserva.profesional}")
        print(f"   Negocio: {reserva.peluquero}")
        
        # Crear recordatorio de confirmación
        print("\n📱 Creando recordatorio de confirmación...")
        resultado = servicio_recordatorios.enviar_recordatorio_confirmacion(reserva)
        
        if resultado:
            print("✅ Recordatorio creado exitosamente")
            print("📤 Intentando enviar WhatsApp...")
            
            # Verificar si se creó el recordatorio
            from recordatorios.models import Recordatorio
            recordatorio = Recordatorio.objects.filter(
                content_type__model='reserva',
                object_id=reserva.id,
                tipo='confirmacion'
            ).first()
            
            if recordatorio:
                print(f"✅ Recordatorio en BD: ID {recordatorio.id}")
                print(f"   Estado: {recordatorio.estado}")
                print(f"   Canal: {recordatorio.canal}")
                print(f"   Fecha envío: {recordatorio.fecha_envio}")
                
                # Intentar enviar ahora
                if recordatorio.estado == 'pendiente':
                    print("📤 Enviando recordatorio ahora...")
                    servicio_recordatorios.enviar_recordatorio(recordatorio)
                    
                    # Verificar estado después del envío
                    recordatorio.refresh_from_db()
                    print(f"   Estado después del envío: {recordatorio.estado}")
                    
                    if recordatorio.estado == 'enviado':
                        print("🎉 ¡WhatsApp enviado exitosamente!")
                        return True
                    elif recordatorio.estado == 'fallido':
                        print("❌ WhatsApp falló")
                        return False
                    else:
                        print(f"⚠️ Estado inesperado: {recordatorio.estado}")
                        return False
                else:
                    print(f"⚠️ Recordatorio no está pendiente: {recordatorio.estado}")
                    return False
            else:
                print("❌ No se creó el recordatorio en la BD")
                return False
        else:
            print("❌ Error creando recordatorio")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def verificar_recordatorios_existentes():
    """Verifica recordatorios existentes para la reserva 382"""
    print("\n🔍 Verificando recordatorios existentes...")
    
    try:
        from recordatorios.models import Recordatorio
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model('clientes.Reserva')
        recordatorios = Recordatorio.objects.filter(
            content_type=content_type,
            object_id=382
        )
        
        print(f"📊 Total recordatorios para reserva 382: {recordatorios.count()}")
        
        for recordatorio in recordatorios:
            print(f"   ID: {recordatorio.id}")
            print(f"   Tipo: {recordatorio.tipo}")
            print(f"   Estado: {recordatorio.estado}")
            print(f"   Canal: {recordatorio.canal}")
            print(f"   Fecha creación: {recordatorio.fecha_creacion}")
            print(f"   Fecha envío: {recordatorio.fecha_envio}")
            print("   ---")
            
    except Exception as e:
        print(f"❌ Error verificando recordatorios: {e}")

def main():
    """Función principal"""
    print("🚀 SISTEMA DE PRUEBA DE WHATSAPP")
    print("=" * 50)
    
    # Verificar recordatorios existentes
    verificar_recordatorios_existentes()
    
    # Crear recordatorio manual
    resultado = crear_recordatorio_manual()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN")
    print("=" * 50)
    
    if resultado:
        print("🎉 ¡ÉXITO! WhatsApp está funcionando")
        print("💡 El problema era que las señales no estaban conectadas")
        print("🔧 Ahora necesitamos conectar las señales para futuras reservas")
    else:
        print("❌ WhatsApp NO está funcionando")
        print("🔍 Revisar configuración de Twilio")
    
    print("\n💡 PRÓXIMOS PASOS:")
    print("1. Verificar que llegó el mensaje de WhatsApp")
    print("2. Conectar las señales para futuras reservas")
    print("3. Probar con una nueva reserva")

if __name__ == '__main__':
    main()
