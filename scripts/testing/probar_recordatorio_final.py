#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.models import Reserva
from clientes.twilio_whatsapp_service import twilio_whatsapp_service
from django.utils import timezone

print("🚀 Probando recordatorio de WhatsApp...")

# Buscar una reserva para mañana
mañana = timezone.now().date() + timezone.timedelta(days=1)
reservas = Reserva.objects.filter(fecha=mañana, estado='confirmado')

print(f"📅 Fecha mañana: {mañana}")
print(f"📊 Reservas encontradas: {reservas.count()}")

if reservas.exists():
    reserva = reservas.first()
    print(f"📋 Usando reserva: #{reserva.id}")
    print(f"👤 Cliente: {reserva.cliente.username}")
    print(f"📱 Teléfono: {reserva.cliente.telefono}")
    
    # Actualizar teléfono si es necesario
    if reserva.cliente.telefono != '3117451274':
        reserva.cliente.telefono = '3117451274'
        reserva.cliente.save()
        print(f"✅ Teléfono actualizado a: {reserva.cliente.telefono}")
    
    # Enviar recordatorio
    print("📤 Enviando recordatorio...")
    resultado = twilio_whatsapp_service.send_recordatorio_dia_antes(reserva)
    
    print(f"✅ Resultado: {resultado}")
    
    if resultado.get('success'):
        print("🎉 ¡Recordatorio enviado exitosamente!")
        print(f"   Message ID: {resultado.get('message_id')}")
    else:
        print(f"❌ Error: {resultado.get('error')}")
else:
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
            notas='Reserva de prueba para recordatorios'
        )
        
        print(f"✅ Reserva creada: #{reserva.id}")
        
        # Enviar recordatorio
        print("📤 Enviando recordatorio...")
        resultado = twilio_whatsapp_service.send_recordatorio_dia_antes(reserva)
        
        print(f"✅ Resultado: {resultado}")
        
        if resultado.get('success'):
            print("🎉 ¡Recordatorio enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
    else:
        print("❌ No se pueden crear los objetos necesarios")
