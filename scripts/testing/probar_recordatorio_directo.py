#!/usr/bin/env python
"""
Script para probar recordatorio directamente con la reserva 392
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.models import Reserva
from clientes.twilio_whatsapp_service import twilio_whatsapp_service

def probar_recordatorio_directo():
    """Probar recordatorio directamente con la reserva 392"""
    print("📅 Probando recordatorio directamente con reserva 392...")
    
    try:
        # Obtener la reserva 392
        reserva = Reserva.objects.get(id=392)
        print(f"📋 Reserva encontrada: #{reserva.id}")
        print(f"👤 Cliente: {reserva.cliente.username}")
        print(f"📱 Teléfono: {reserva.cliente.telefono}")
        print(f"📅 Fecha: {reserva.fecha}")
        print(f"🕐 Hora: {reserva.hora_inicio}")
        print(f"🏢 Negocio: {reserva.peluquero.nombre}")
        print(f"👨‍💼 Profesional: {reserva.profesional}")
        print(f"💄 Servicio: {reserva.servicio}")
        
        # Asegurar que el teléfono esté correcto
        if reserva.cliente.telefono != '3117451274':
            reserva.cliente.telefono = '3117451274'
            reserva.cliente.save()
            print(f"✅ Teléfono actualizado a: {reserva.cliente.telefono}")
        
        # Enviar recordatorio de 1 día antes
        print("\n📤 Enviando recordatorio de 1 día antes...")
        resultado = twilio_whatsapp_service.send_recordatorio_dia_antes(reserva)
        
        print(f"✅ Resultado: {resultado}")
        
        if resultado.get('success'):
            print("🎉 ¡Recordatorio enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
            
    except Reserva.DoesNotExist:
        print("❌ No se encontró la reserva 392")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_recordatorio_directo()
