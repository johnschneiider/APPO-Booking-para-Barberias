#!/usr/bin/env python
"""
Script para probar recordatorios con botones de edición
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.models import Reserva
from clientes.twilio_whatsapp_service import twilio_whatsapp_service
from django.utils import timezone

def probar_recordatorios_con_botones():
    """Probar recordatorios con botones de edición"""
    print("🚀 Probando recordatorios con botones de edición...")
    
    try:
        # Buscar una reserva para mañana
        mañana = timezone.now().date() + timezone.timedelta(days=1)
        reservas = Reserva.objects.filter(fecha=mañana, estado='confirmado')
        
        if not reservas.exists():
            print("❌ No hay reservas para mañana. Creando una...")
            
            # Crear una reserva de prueba
            from django.contrib.auth import get_user_model
            from profesionales.models import Profesional
            from negocios.models import Negocio, ServicioNegocio
            
            User = get_user_model()
            
            cliente = User.objects.first()
            profesional = Profesional.objects.first()
            negocio = Negocio.objects.first()
            servicio = ServicioNegocio.objects.first()
            
            if cliente and profesional and negocio and servicio:
                # Actualizar teléfono del cliente
                cliente.telefono = '3117451274'
                cliente.save()
                
                # Crear reserva
                reserva = Reserva.objects.create(
                    cliente=cliente,
                    profesional=profesional,
                    peluquero=negocio,
                    servicio=servicio,
                    fecha=mañana,
                    hora_inicio=timezone.datetime.min.time().replace(hour=10, minute=0),
                    hora_fin=timezone.datetime.min.time().replace(hour=11, minute=0),
                    estado='confirmado',
                    notas='Reserva de prueba para recordatorios con botones'
                )
                
                print(f"✅ Reserva creada: #{reserva.id}")
            else:
                print("❌ No se pueden crear los objetos necesarios")
                return
        else:
            reserva = reservas.first()
            print(f"📋 Usando reserva existente: #{reserva.id}")
        
        # Actualizar teléfono si es necesario
        if reserva.cliente.telefono != '3117451274':
            reserva.cliente.telefono = '3117451274'
            reserva.cliente.save()
            print(f"✅ Teléfono actualizado a: {reserva.cliente.telefono}")
        
        # Probar recordatorio de 1 día antes
        print("\n📤 Enviando recordatorio de 1 día antes con botones...")
        resultado_dia = twilio_whatsapp_service.send_recordatorio_dia_antes(reserva)
        
        print(f"✅ Resultado día antes: {resultado_dia}")
        
        if resultado_dia.get('success'):
            print("🎉 ¡Recordatorio de 1 día enviado exitosamente!")
            print(f"   Message ID: {resultado_dia.get('message_id')}")
        else:
            print(f"❌ Error día antes: {resultado_dia.get('error')}")
        
        # Probar recordatorio de 3 horas antes
        print("\n📤 Enviando recordatorio de 3 horas antes con botones...")
        resultado_tres = twilio_whatsapp_service.send_recordatorio_tres_horas(reserva)
        
        print(f"✅ Resultado 3 horas: {resultado_tres}")
        
        if resultado_tres.get('success'):
            print("🎉 ¡Recordatorio de 3 horas enviado exitosamente!")
            print(f"   Message ID: {resultado_tres.get('message_id')}")
        else:
            print(f"❌ Error 3 horas: {resultado_tres.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_recordatorios_con_botones()


