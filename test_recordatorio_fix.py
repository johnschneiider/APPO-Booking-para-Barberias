#!/usr/bin/env python
"""
Script para probar el sistema de recordatorios después de la corrección
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from recordatorios.services import servicio_recordatorios
from cuentas.models import UsuarioPersonalizado
from clientes.models import Reserva
from datetime import datetime, timedelta

def test_recordatorio_confirmacion():
    """Prueba crear un recordatorio de confirmación"""
    print("🧪 Probando creación de recordatorio de confirmación...")
    
    try:
        # Buscar un usuario con teléfono
        usuario = UsuarioPersonalizado.objects.filter(telefono__isnull=False).exclude(telefono='').first()
        
        if not usuario:
            print("❌ No hay usuarios con teléfono configurado")
            return False
        
        print(f"✅ Usuario encontrado: {usuario.email} - Tel: {usuario.telefono}")
        
        # Buscar una reserva reciente
        reserva = Reserva.objects.filter(cliente=usuario).first()
        
        if not reserva:
            print("❌ No hay reservas para este usuario")
            return False
        
        print(f"✅ Reserva encontrada: {reserva.id} - Fecha: {reserva.fecha}")
        
        # Intentar crear recordatorio de confirmación
        resultado = servicio_recordatorios.enviar_recordatorio_confirmacion(reserva)
        
        if resultado:
            print("✅ Recordatorio de confirmación creado exitosamente")
            return True
        else:
            print("❌ Error creando recordatorio de confirmación")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def test_recordatorio_dia_antes():
    """Prueba crear un recordatorio para el día antes"""
    print("\n🧪 Probando creación de recordatorio día antes...")
    
    try:
        # Buscar un usuario con teléfono
        usuario = UsuarioPersonalizado.objects.filter(telefono__isnull=False).exclude(telefono='').first()
        
        if not usuario:
            print("❌ No hay usuarios con teléfono configurado")
            return False
        
        # Buscar una reserva futura
        reserva = Reserva.objects.filter(
            cliente=usuario,
            fecha__gte=datetime.now().date()
        ).first()
        
        if not reserva:
            print("❌ No hay reservas futuras para este usuario")
            return False
        
        print(f"✅ Reserva futura encontrada: {reserva.id} - Fecha: {reserva.fecha}")
        
        # Intentar crear recordatorio día antes
        resultado = servicio_recordatorios.enviar_recordatorio_dia_antes(reserva)
        
        if resultado:
            print("✅ Recordatorio día antes creado exitosamente")
            return True
        else:
            print("❌ Error creando recordatorio día antes")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Probando sistema de recordatorios corregido...\n")
    
    # Probar recordatorio de confirmación
    confirmacion_ok = test_recordatorio_confirmacion()
    
    # Probar recordatorio día antes
    dia_antes_ok = test_recordatorio_dia_antes()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"  Recordatorio confirmación: {'✅' if confirmacion_ok else '❌'}")
    print(f"  Recordatorio día antes: {'✅' if dia_antes_ok else '❌'}")
    
    if confirmacion_ok and dia_antes_ok:
        print("\n🎉 ¡El sistema de recordatorios está funcionando correctamente!")
        print("💡 Ahora los recordatorios se crearán automáticamente al hacer reservas")
    else:
        print("\n⚠️  El sistema aún tiene problemas")
        print("💡 Revisa los logs para más detalles")

if __name__ == '__main__':
    main()
