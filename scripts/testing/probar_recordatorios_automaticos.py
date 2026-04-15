#!/usr/bin/env python
"""
Script para probar el sistema de recordatorios automáticos
"""

import os
import django
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.models import Reserva
from clientes.twilio_whatsapp_service import twilio_whatsapp_service

def probar_recordatorio_dia_antes():
    """Probar recordatorio de 1 día antes"""
    print("📅 Probando recordatorio de 1 día antes...")
    
    try:
        # Crear una reserva para mañana
        from django.utils import timezone
        mañana = timezone.now() + timezone.timedelta(days=1)
        
        # Buscar una reserva existente o crear una de prueba
        reserva = Reserva.objects.filter(
            fecha=mañana.date(),
            estado='confirmada'
        ).first()
        
        if not reserva:
            print("❌ No hay reservas para mañana. Creando una de prueba...")
            # Aquí podrías crear una reserva de prueba si es necesario
            return
        
        print(f"📋 Reserva encontrada: #{reserva.id}")
        print(f"👤 Cliente: {reserva.cliente.username}")
        print(f"📱 Teléfono: {reserva.cliente.telefono}")
        print(f"📅 Fecha: {reserva.fecha}")
        print(f"🕐 Hora: {reserva.hora_inicio}")
        
        # Actualizar teléfono si es necesario
        if reserva.cliente.telefono != '3117451274':
            reserva.cliente.telefono = '3117451274'
            reserva.cliente.save()
            print(f"✅ Teléfono actualizado a: {reserva.cliente.telefono}")
        
        # Enviar recordatorio
        print("📤 Enviando recordatorio de 1 día antes...")
        resultado = twilio_whatsapp_service.send_recordatorio_dia_antes(reserva)
        
        if resultado.get('success'):
            print("🎉 ¡Recordatorio enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def probar_recordatorio_tres_horas():
    """Probar recordatorio de 3 horas antes"""
    print("\n⏰ Probando recordatorio de 3 horas antes...")
    
    try:
        # Buscar una reserva para hoy en las próximas horas
        from django.utils import timezone
        ahora = timezone.now()
        tres_horas_desde_ahora = ahora + timezone.timedelta(hours=3)
        
        reserva = Reserva.objects.filter(
            fecha=ahora.date(),
            hora_inicio__gte=ahora.time(),
            hora_inicio__lte=tres_horas_desde_ahora.time(),
            estado='confirmada'
        ).first()
        
        if not reserva:
            print("❌ No hay reservas en las próximas 3 horas")
            return
        
        print(f"📋 Reserva encontrada: #{reserva.id}")
        print(f"👤 Cliente: {reserva.cliente.username}")
        print(f"📱 Teléfono: {reserva.cliente.telefono}")
        print(f"📅 Fecha: {reserva.fecha}")
        print(f"🕐 Hora: {reserva.hora_inicio}")
        
        # Actualizar teléfono si es necesario
        if reserva.cliente.telefono != '3117451274':
            reserva.cliente.telefono = '3117451274'
            reserva.cliente.save()
            print(f"✅ Teléfono actualizado a: {reserva.cliente.telefono}")
        
        # Enviar recordatorio
        print("📤 Enviando recordatorio de 3 horas antes...")
        resultado = twilio_whatsapp_service.send_recordatorio_tres_horas(reserva)
        
        if resultado.get('success'):
            print("🎉 ¡Recordatorio enviado exitosamente!")
            print(f"   Message ID: {resultado.get('message_id')}")
        else:
            print(f"❌ Error: {resultado.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def mostrar_reservas_proximas():
    """Mostrar reservas próximas para debugging"""
    print("\n📊 Reservas próximas:")
    
    try:
        from django.utils import timezone
        ahora = timezone.now()
        mañana = ahora + timezone.timedelta(days=1)
        
        # Reservas para mañana
        reservas_mañana = Reserva.objects.filter(
            fecha=mañana.date(),
            estado='confirmada'
        )
        
        print(f"📅 Reservas para mañana ({mañana.date()}): {reservas_mañana.count()}")
        for reserva in reservas_mañana[:5]:  # Mostrar solo las primeras 5
            print(f"  - #{reserva.id}: {reserva.cliente.username} a las {reserva.hora_inicio}")
        
        # Reservas para hoy en las próximas horas
        tres_horas_desde_ahora = ahora + timezone.timedelta(hours=3)
        reservas_hoy = Reserva.objects.filter(
            fecha=ahora.date(),
            hora_inicio__gte=ahora.time(),
            hora_inicio__lte=tres_horas_desde_ahora.time(),
            estado='confirmada'
        )
        
        print(f"⏰ Reservas para hoy en las próximas 3 horas: {reservas_hoy.count()}")
        for reserva in reservas_hoy[:5]:  # Mostrar solo las primeras 5
            print(f"  - #{reserva.id}: {reserva.cliente.username} a las {reserva.hora_inicio}")
            
    except Exception as e:
        print(f"❌ Error mostrando reservas: {e}")

if __name__ == "__main__":
    print("🚀 Probando sistema de recordatorios automáticos")
    print("=" * 60)
    
    # Mostrar reservas próximas
    mostrar_reservas_proximas()
    
    # Probar recordatorios
    probar_recordatorio_dia_antes()
    probar_recordatorio_tres_horas()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas")
