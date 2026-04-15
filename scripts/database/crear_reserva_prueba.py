#!/usr/bin/env python
"""
Script para crear una reserva de prueba y verificar el sistema de recordatorios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.utils import timezone
from cuentas.models import UsuarioPersonalizado
from clientes.models import Reserva, Peluquero, Servicio
from profesionales.models import Profesional
from datetime import datetime, timedelta

def crear_reserva_prueba():
    """Crea una reserva de prueba para verificar el sistema"""
    print("🧪 Creando reserva de prueba...")
    
    try:
        # Buscar un usuario con teléfono
        usuario = UsuarioPersonalizado.objects.filter(telefono__isnull=False).exclude(telefono='').first()
        
        if not usuario:
            print("❌ No hay usuarios con teléfono configurado")
            return None
        
        print(f"✅ Usuario encontrado: {usuario.email} - Tel: {usuario.telefono}")
        
        # Buscar un peluquero
        peluquero = Peluquero.objects.filter(activo=True).first()
        
        if not peluquero:
            print("❌ No hay peluqueros activos")
            return None
        
        print(f"✅ Peluquero encontrado: {peluquero.nombre}")
        
        # Buscar un servicio
        servicio = Servicio.objects.filter(negocio=peluquero, activo=True).first()
        
        if not servicio:
            print("❌ No hay servicios activos")
            return None
        
        print(f"✅ Servicio encontrado: {servicio.nombre}")
        
        # Buscar un profesional
        profesional = Profesional.objects.filter(negocio=peluquero, activo=True).first()
        
        if not profesional:
            print("❌ No hay profesionales activos")
            return None
        
        print(f"✅ Profesional encontrado: {profesional.nombre}")
        
        # Crear fecha futura (mañana a las 2 PM)
        fecha_reserva = timezone.now().date() + timedelta(days=1)
        hora_reserva = datetime.strptime('14:00', '%H:%M').time()
        
        # Crear la reserva
        reserva = Reserva.objects.create(
            cliente=usuario,
            peluquero=peluquero,
            servicio=servicio,
            profesional=profesional,
            fecha=fecha_reserva,
            hora_inicio=hora_reserva,
            hora_fin=datetime.strptime('15:00', '%H:%M').time(),
            estado='confirmada'
        )
        
        print(f"✅ Reserva creada exitosamente: ID {reserva.id}")
        print(f"   Fecha: {fecha_reserva}")
        print(f"   Hora: {hora_reserva}")
        print(f"   Servicio: {servicio.nombre}")
        print(f"   Profesional: {profesional.nombre}")
        
        return reserva
        
    except Exception as e:
        print(f"❌ Error creando reserva: {e}")
        return None

def verificar_recordatorios_creados(reserva):
    """Verifica que se hayan creado los recordatorios automáticamente"""
    print("\n🔍 Verificando recordatorios creados...")
    
    try:
        from recordatorios.models import Recordatorio
        
        # Buscar recordatorios para esta reserva
        recordatorios = Recordatorio.objects.filter(
            content_type__model='reserva',
            object_id=reserva.id
        )
        
        if recordatorios.exists():
            print(f"✅ Se crearon {recordatorios.count()} recordatorios:")
            
            for recordatorio in recordatorios:
                print(f"   - {recordatorio.tipo}: {recordatorio.estado}")
                print(f"     Fecha programada: {recordatorio.fecha_programada}")
                print(f"     Canales: {recordatorio.canales_habilitados}")
                print(f"     Prioridad: {recordatorio.prioridad}")
                print()
            
            return True
        else:
            print("❌ No se crearon recordatorios automáticamente")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando recordatorios: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Creando reserva de prueba para verificar sistema de recordatorios...\n")
    
    # Crear reserva de prueba
    reserva = crear_reserva_prueba()
    
    if not reserva:
        print("❌ No se pudo crear la reserva de prueba")
        return
    
    # Esperar un momento para que se procesen las señales
    print("\n⏳ Esperando procesamiento de señales...")
    import time
    time.sleep(2)
    
    # Verificar recordatorios creados
    recordatorios_ok = verificar_recordatorios_creados(reserva)
    
    # Resumen
    print("="*60)
    print("📊 RESUMEN DE LA PRUEBA")
    print("="*60)
    print(f"  Reserva creada: ✅ (ID: {reserva.id})")
    print(f"  Recordatorios creados: {'✅' if recordatorios_ok else '❌'}")
    
    if recordatorios_ok:
        print("\n🎉 ¡El sistema de recordatorios está funcionando correctamente!")
        print("💡 Los recordatorios se crean automáticamente al hacer reservas")
        print("📱 Ahora deberías recibir WhatsApp de confirmación inmediata")
    else:
        print("\n⚠️  El sistema no está creando recordatorios automáticamente")
        print("💡 Revisa las señales y la configuración")

if __name__ == '__main__':
    main()
