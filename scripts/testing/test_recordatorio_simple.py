#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.models import Reserva
from clientes.twilio_whatsapp_service import twilio_whatsapp_service
from django.utils import timezone

# Actualizar reserva 391 para mañana
r = Reserva.objects.get(id=391)
r.estado = 'confirmado'
r.fecha = timezone.now().date() + timezone.timedelta(days=1)
r.cliente.telefono = '3117451274'
r.cliente.save()
r.save()

print(f"Reserva actualizada: #{r.id} - {r.fecha} - {r.estado} - {r.cliente.telefono}")

# Enviar recordatorio
resultado = twilio_whatsapp_service.send_recordatorio_dia_antes(r)
print(f"Resultado: {resultado}")

if resultado.get('success'):
    print("¡Recordatorio enviado!")
else:
    print(f"Error: {resultado.get('error')}")
