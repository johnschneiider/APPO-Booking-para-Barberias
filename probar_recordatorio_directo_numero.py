#!/usr/bin/env python
"""
Script para probar envío de recordatorios directamente a un número específico
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from clientes.models import Reserva
from negocios.models import Negocio, ServicioNegocio
from profesionales.models import Profesional
from clientes.utils import get_whatsapp_service
from datetime import time

User = get_user_model()

def probar_recordatorio_dia_antes(numero_telefono='3117451274'):
    """Prueba envío de recordatorio 1 día antes directamente"""
    print(f"\n📅 Probando recordatorio DÍA ANTES al {numero_telefono}...")
    
    try:
        # Buscar o crear cliente con ese teléfono
        cliente = User.objects.filter(telefono=numero_telefono).first()
        if not cliente:
            # Buscar cualquier cliente y actualizar su teléfono
            cliente = User.objects.filter(tipo='cliente').first()
            if not cliente:
                print("❌ No hay clientes en la base de datos")
                return False
            cliente.telefono = numero_telefono
            cliente.save()
            print(f"✅ Cliente encontrado/actualizado: {cliente.username} - {cliente.telefono}")
        else:
            print(f"✅ Cliente encontrado: {cliente.username} - {cliente.telefono}")
        
        # Buscar negocio, servicio y profesional
        negocio = Negocio.objects.first()
        if not negocio:
            print("❌ No hay negocios en la base de datos")
            return False
        
        servicio_negocio = ServicioNegocio.objects.filter(negocio=negocio).first()
        if not servicio_negocio:
            print("❌ No hay servicios para el negocio")
            return False
        
        profesional = Profesional.objects.first()
        
        # Crear reserva para mañana (asegurar que no tenga recordatorio enviado)
        manana = timezone.now() + timezone.timedelta(days=1)
        reserva = Reserva.objects.create(
            cliente=cliente,
            peluquero=negocio,
            profesional=profesional,
            servicio=servicio_negocio,
            fecha=manana.date(),
            hora_inicio=time(10, 0),
            hora_fin=time(11, 0),
            estado='confirmado',
            recordatorio_dia_enviado=False,  # Asegurar que puede enviarse
            notas='Reserva de prueba para recordatorio día antes'
        )
        
        print(f"✅ Reserva creada: ID {reserva.id} para {reserva.fecha} a las {reserva.hora_inicio}")
        
        # Obtener servicio WhatsApp
        whatsapp_service = get_whatsapp_service()
        if not whatsapp_service or not whatsapp_service.is_enabled():
            print("❌ WhatsApp no está disponible o no está habilitado")
            return False
        
        print("📤 Enviando recordatorio día antes...")
        resultado = whatsapp_service.send_recordatorio_dia_antes(reserva)
        
        if resultado.get('success'):
            print(f"✅ Recordatorio enviado exitosamente!")
            print(f"   Message SID: {resultado.get('message_id', 'N/A')}")
            reserva.recordatorio_dia_enviado = True
            reserva.save(update_fields=['recordatorio_dia_enviado'])
            return True
        else:
            print(f"❌ Error enviando recordatorio: {resultado.get('error') or resultado}")
            if resultado.get('error_code'):
                print(f"   Error Code: {resultado.get('error_code')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_recordatorio_tres_horas(numero_telefono='3117451274'):
    """Prueba envío de recordatorio 3 horas antes directamente"""
    print(f"\n⏰ Probando recordatorio 3 HORAS ANTES al {numero_telefono}...")
    
    try:
        # Buscar o crear cliente con ese teléfono
        cliente = User.objects.filter(telefono=numero_telefono).first()
        if not cliente:
            cliente = User.objects.filter(tipo='cliente').first()
            if not cliente:
                print("❌ No hay clientes en la base de datos")
                return False
            cliente.telefono = numero_telefono
            cliente.save()
            print(f"✅ Cliente encontrado/actualizado: {cliente.username} - {cliente.telefono}")
        else:
            print(f"✅ Cliente encontrado: {cliente.username} - {cliente.telefono}")
        
        # Buscar negocio, servicio y profesional
        negocio = Negocio.objects.first()
        if not negocio:
            print("❌ No hay negocios en la base de datos")
            return False
        
        servicio_negocio = ServicioNegocio.objects.filter(negocio=negocio).first()
        if not servicio_negocio:
            print("❌ No hay servicios para el negocio")
            return False
        
        profesional = Profesional.objects.first()
        
        # Crear reserva para dentro de 3 horas
        ahora = timezone.localtime(timezone.now())
        tres_horas = ahora + timezone.timedelta(hours=3, minutes=30)  # 3.5 horas para dar margen
        
        reserva = Reserva.objects.create(
            cliente=cliente,
            peluquero=negocio,
            profesional=profesional,
            servicio=servicio_negocio,
            fecha=tres_horas.date(),
            hora_inicio=tres_horas.time(),
            hora_fin=(tres_horas + timezone.timedelta(hours=1)).time(),
            estado='confirmado',
            recordatorio_tres_horas_enviado=False,  # Asegurar que puede enviarse
            notas='Reserva de prueba para recordatorio 3 horas'
        )
        
        print(f"✅ Reserva creada: ID {reserva.id} para {reserva.fecha} a las {reserva.hora_inicio}")
        
        # Obtener servicio WhatsApp
        whatsapp_service = get_whatsapp_service()
        if not whatsapp_service or not whatsapp_service.is_enabled():
            print("❌ WhatsApp no está disponible o no está habilitado")
            return False
        
        print("📤 Enviando recordatorio 3 horas antes...")
        resultado = whatsapp_service.send_recordatorio_tres_horas(reserva)
        
        if resultado.get('success'):
            print(f"✅ Recordatorio enviado exitosamente!")
            print(f"   Message SID: {resultado.get('message_id', 'N/A')}")
            reserva.recordatorio_tres_horas_enviado = True
            reserva.save(update_fields=['recordatorio_tres_horas_enviado'])
            return True
        else:
            print(f"❌ Error enviando recordatorio: {resultado.get('error') or resultado}")
            if resultado.get('error_code'):
                print(f"   Error Code: {resultado.get('error_code')}")
                if resultado.get('error_code') == '63112':
                    print("   ⚠️  Este error indica que Meta deshabilitó el WABA/sender")
                elif resultado.get('error_code') == '63016':
                    print("   ⚠️  Este error indica problema con template o conversación no iniciada")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    numero = '3117451274'
    print("="*60)
    print("🧪 PRUEBA DE RECORDATORIOS WHATSAPP")
    print("="*60)
    
    # Probar ambos recordatorios
    resultado1 = probar_recordatorio_dia_antes(numero)
    resultado2 = probar_recordatorio_tres_horas(numero)
    
    print("\n" + "="*60)
    print("📊 RESUMEN")
    print("="*60)
    print(f"  Recordatorio Día Antes: {'✅ Enviado' if resultado1 else '❌ Falló'}")
    print(f"  Recordatorio 3 Horas: {'✅ Enviado' if resultado2 else '❌ Falló'}")
    print("="*60)
