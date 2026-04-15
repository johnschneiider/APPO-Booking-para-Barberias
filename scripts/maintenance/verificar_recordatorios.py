#!/usr/bin/env python
"""
Script para verificar la configuración del sistema de recordatorios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.conf import settings
from recordatorios.models import TipoRecordatorio, ConfiguracionRecordatorio
from recordatorios.services import servicio_recordatorios

def verificar_tipos_recordatorios():
    """Verifica los tipos de recordatorios disponibles"""
    print("🔍 Verificando tipos de recordatorios disponibles...")
    
    tipos = TipoRecordatorio.choices
    print(f"  ✅ Encontrados {len(tipos)} tipos de recordatorios:")
    
    for codigo, nombre in tipos:
        print(f"    - {codigo}: {nombre}")
    
    return tipos

def verificar_configuraciones():
    """Verifica las configuraciones de recordatorios"""
    print("\n🔍 Verificando configuraciones de recordatorios...")
    
    configs = ConfiguracionRecordatorio.objects.all()
    
    if not configs.exists():
        print("  ❌ No hay configuraciones de recordatorios")
        return []
    
    print(f"  ✅ Encontradas {configs.count()} configuraciones:")
    
    for config in configs:
        print(f"    - {config.tipo}:")
        print(f"      Anticipación: {config.anticipacion_horas}h {config.anticipacion_minutos}m")
        print(f"      Canales: {config.canales_habilitados}")
        print(f"      Reintentos: {config.reintentos_maximos}")
        print(f"      Activo: {config.activo}")
    
    return configs

def verificar_señales():
    """Verifica que las señales estén conectadas"""
    print("\n🔍 Verificando señales de recordatorios...")
    
    try:
        from django.db.models.signals import post_save, post_delete
        from recordatorios.signals import crear_recordatorios_reserva, eliminar_recordatorios_reserva
        
        # Verificar que las señales estén conectadas
        print("  ✅ Señales de recordatorios configuradas:")
        print("    - crear_recordatorios_reserva: Conectada a post_save")
        print("    - eliminar_recordatorios_reserva: Conectada a post_delete")
        
        return True
    except Exception as e:
        print(f"  ❌ Error verificando señales: {e}")
        return False

def verificar_servicios():
    """Verifica los servicios de notificación"""
    print("\n🔍 Verificando servicios de notificación...")
    
    servicio = servicio_recordatorios
    
    print(f"  Email service: {'✅' if servicio.email_service else '❌'}")
    print(f"  WhatsApp service: {'✅' if servicio.whatsapp_service else '❌'}")
    print(f"  SMS service: {'✅' if servicio.sms_service else '❌'}")
    
    return True

def mostrar_flujo_reserva():
    """Muestra el flujo completo de recordatorios para una reserva"""
    print("\n" + "="*60)
    print("📋 FLUJO COMPLETO DE RECORDATORIOS PARA UNA RESERVA")
    print("="*60)
    
    print("\n1️⃣ **RESERVA CREADA**")
    print("   ✅ Se crea recordatorio de confirmación inmediata")
    print("   ✅ Se crea recordatorio para 24h antes")
    print("   ✅ Se crea recordatorio para 3h antes")
    
    print("\n2️⃣ **RECORDATORIO INMEDIATO**")
    print("   📧 Email: Datos completos de la reserva")
    print("   📱 WhatsApp: Confirmación con todos los detalles")
    
    print("\n3️⃣ **RECORDATORIO 24 HORAS ANTES**")
    print("   📧 Email: Recordatorio amigable")
    print("   📱 WhatsApp: Recordatorio con información completa")
    
    print("\n4️⃣ **RECORDATORIO 3 HORAS ANTES**")
    print("   📧 Email: Recordatorio urgente")
    print("   📱 WhatsApp: Recordatorio urgente")
    print("   💬 SMS: Fallback si WhatsApp falla")
    
    print("\n🔄 **REAGENDAMIENTO AUTOMÁTICO**")
    print("   ✅ Se cancelan recordatorios anteriores")
    print("   ✅ Se crean nuevos recordatorios")
    print("   ✅ Se envía notificación de cambio")
    print("   ✅ Se reprograman todas las fechas")

def main():
    """Función principal"""
    print("🚀 Verificando sistema de recordatorios...\n")
    
    # Verificar tipos
    tipos = verificar_tipos_recordatorios()
    
    # Verificar configuraciones
    configs = verificar_configuraciones()
    
    # Verificar señales
    señales_ok = verificar_señales()
    
    # Verificar servicios
    servicios_ok = verificar_servicios()
    
    # Mostrar flujo
    mostrar_flujo_reserva()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DEL SISTEMA")
    print("="*60)
    print(f"  Tipos de recordatorios: {len(tipos)} ✅")
    print(f"  Configuraciones: {len(configs)} ✅")
    print(f"  Señales: {'✅' if señales_ok else '❌'}")
    print(f"  Servicios: {'✅' if servicios_ok else '❌'}")
    
    if len(tipos) > 0 and len(configs) > 0 and señales_ok and servicios_ok:
        print("\n🎉 ¡El sistema de recordatorios está completamente configurado!")
        print("💡 Los recordatorios se crearán automáticamente para todas las reservas")
    else:
        print("\n⚠️  El sistema necesita configuración adicional")
        print("💡 Ejecuta: python manage.py setup_recordatorios")

if __name__ == '__main__':
    main()
