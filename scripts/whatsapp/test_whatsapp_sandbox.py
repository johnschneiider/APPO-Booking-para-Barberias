#!/usr/bin/env python
"""
Script para probar WhatsApp Sandbox
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def main():
    print("🚀 Probando WhatsApp Sandbox...")
    
    try:
        from django.conf import settings
        from recordatorios.services import servicio_recordatorios
        from clientes.models import Reserva
        
        # Verificar configuración
        print(f"✅ Account SID: {settings.TWILIO_ACCOUNT_SID}")
        print(f"✅ WhatsApp Number: {settings.TWILIO_WHATSAPP_NUMBER}")
        print(f"✅ SMS Number: {settings.TWILIO_SMS_NUMBER}")
        
        # Buscar reserva reciente (383)
        reserva = Reserva.objects.get(id=383)
        print(f"\n✅ Reserva encontrada: {reserva.id}")
        print(f"Cliente: {reserva.cliente.email}")
        print(f"Teléfono: {reserva.cliente.telefono}")
        
        # Crear recordatorio de confirmación
        print("\n📱 Creando recordatorio de confirmación...")
        resultado = servicio_recordatorios.enviar_recordatorio_confirmacion(reserva)
        
        if resultado:
            print("✅ Recordatorio creado")
            print("📤 Intentando enviar WhatsApp...")
            
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
                print(f"Canales: {recordatorio.canales_habilitados}")
                
                # Enviar ahora
                if recordatorio.estado == 'pendiente':
                    print("📤 Enviando recordatorio...")
                    servicio_recordatorios._procesar_recordatorio(recordatorio)
                    
                    # Verificar estado
                    recordatorio.refresh_from_db()
                    print(f"Estado después del envío: {recordatorio.estado}")
                    
                    if recordatorio.estado == 'enviado':
                        print("🎉 ¡WhatsApp enviado exitosamente!")
                    else:
                        print(f"⚠️ Estado: {recordatorio.estado}")
                else:
                    print(f"⚠️ Recordatorio no está pendiente: {recordatorio.estado}")
            else:
                print("❌ No se encontró el recordatorio")
        else:
            print("❌ Error creando recordatorio")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
