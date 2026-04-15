#!/usr/bin/env python
"""
Script para verificar si el recordatorio se envió por WhatsApp
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def main():
    print("🔍 Verificando envío de WhatsApp...")
    
    try:
        from recordatorios.models import Recordatorio
        from django.contrib.contenttypes.models import ContentType
        
        # Buscar recordatorios para reserva 382
        from clientes.models import Reserva
        content_type = ContentType.objects.get_for_model(Reserva)
        recordatorios = Recordatorio.objects.filter(
            content_type=content_type,
            object_id=382
        )
        
        print(f"📊 Total recordatorios: {recordatorios.count()}")
        
        for recordatorio in recordatorios:
            print(f"\n📋 Recordatorio ID: {recordatorio.id}")
            print(f"   Tipo: {recordatorio.tipo}")
            print(f"   Estado: {recordatorio.estado}")
            print(f"   Canales habilitados: {recordatorio.canales_habilitados}")
            print(f"   Fecha creación: {recordatorio.fecha_creacion}")
            print(f"   Fecha envío: {recordatorio.fecha_envio}")
            print(f"   Destinatario: {recordatorio.destinatario.email}")
            print(f"   Teléfono: {recordatorio.destinatario.telefono}")
            
            # Si está pendiente, intentar enviar
            if recordatorio.estado == 'pendiente':
                print("📤 Enviando recordatorio ahora...")
                from recordatorios.services import servicio_recordatorios
                servicio_recordatorios._procesar_recordatorio(recordatorio)
                
                # Verificar estado después
                recordatorio.refresh_from_db()
                print(f"   Estado después del envío: {recordatorio.estado}")
                
                if recordatorio.estado == 'enviado':
                    print("🎉 ¡WhatsApp enviado exitosamente!")
                elif recordatorio.estado == 'fallido':
                    print("❌ WhatsApp falló")
                else:
                    print(f"⚠️ Estado: {recordatorio.estado}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
