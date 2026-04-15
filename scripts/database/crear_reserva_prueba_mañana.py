#!/usr/bin/env python
"""
Script para crear una reserva de prueba para mañana
"""

import os
import django
from datetime import datetime, timedelta
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from clientes.models import Reserva
from profesionales.models import Profesional
from negocios.models import Negocio, ServicioNegocio
from django.contrib.auth import get_user_model

User = get_user_model()

def crear_reserva_prueba_mañana():
    """Crear una reserva de prueba para mañana"""
    print("📅 Creando reserva de prueba para mañana...")
    
    try:
        from django.utils import timezone
        mañana = timezone.now() + timezone.timedelta(days=1)
        
        # Obtener cliente
        cliente = User.objects.first()
        if not cliente:
            print("❌ No hay usuarios en la base de datos")
            return
        
        # Obtener profesional
        profesional = Profesional.objects.first()
        if not profesional:
            print("❌ No hay profesionales en la base de datos")
            return
        
        # Obtener negocio
        negocio = Negocio.objects.first()
        if not negocio:
            print("❌ No hay negocios en la base de datos")
            return
        
        # Obtener servicio
        servicio_negocio = ServicioNegocio.objects.first()
        if not servicio_negocio:
            print("❌ No hay servicios en la base de datos")
            return
        
        # Actualizar teléfono del cliente
        cliente.telefono = '3117451274'
        cliente.save()
        
        # Crear reserva para mañana a las 10:00 AM
        from datetime import time
        hora_inicio = time(10, 0)  # 10:00 AM
        hora_fin = time(11, 0)     # 11:00 AM
        
        reserva = Reserva.objects.create(
            cliente=cliente,
            profesional=profesional,
            peluquero=negocio,
            servicio=servicio_negocio,
            fecha=mañana.date(),
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            estado='confirmado',
            notas='Reserva de prueba para recordatorios'
        )
        
        print(f"✅ Reserva creada exitosamente:")
        print(f"   ID: {reserva.id}")
        print(f"   Cliente: {cliente.username}")
        print(f"   Teléfono: {cliente.telefono}")
        print(f"   Fecha: {reserva.fecha}")
        print(f"   Hora: {reserva.hora_inicio}")
        print(f"   Profesional: {profesional}")
        print(f"   Negocio: {negocio.nombre}")
        
        return reserva
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    crear_reserva_prueba_mañana()
