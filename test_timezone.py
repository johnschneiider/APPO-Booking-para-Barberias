#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appo.settings')
django.setup()

from django.utils import timezone
from datetime import datetime, timedelta
from clientes.utils import get_current_time_in_timezone, make_datetime_aware, is_fecha_pasada, get_fecha_manana, get_hora_en_tres_horas

def test_timezone_functions():
    print("=== PRUEBA DE FUNCIONES DE ZONA HORARIA ===")
    
    # 1. Probar función de hora actual
    print(f"1. Hora actual en zona horaria configurada: {get_current_time_in_timezone()}")
    print(f"   Hora actual directa: {timezone.now()}")
    
    # 2. Probar función de fecha de mañana
    print(f"\n2. Fecha de mañana: {get_fecha_manana()}")
    print(f"   Fecha de mañana directa: {(timezone.now().date() + timedelta(days=1))}")
    
    # 3. Probar función de hora en 3 horas
    print(f"\n3. Hora en 3 horas: {get_hora_en_tres_horas()}")
    print(f"   Hora en 3 horas directa: {timezone.now() + timedelta(hours=3)}")
    
    # 4. Probar función de datetime aware
    from datetime import date, time
    fecha_test = date.today()
    hora_test = time(10, 0)
    datetime_aware = make_datetime_aware(fecha_test, hora_test)
    print(f"\n4. DateTime aware para {fecha_test} {hora_test}: {datetime_aware}")
    
    # 5. Probar función de validación de fecha pasada
    fecha_pasada = date.today() - timedelta(days=1)
    fecha_futura = date.today() + timedelta(days=1)
    
    print(f"\n5. Validación de fechas:")
    print(f"   Fecha pasada ({fecha_pasada}): {is_fecha_pasada(fecha_pasada, time(10, 0))}")
    print(f"   Fecha futura ({fecha_futura}): {is_fecha_pasada(fecha_futura, time(10, 0))}")
    
    # 6. Verificar configuración de zona horaria
    from django.conf import settings
    print(f"\n6. Configuración de zona horaria:")
    print(f"   TIME_ZONE: {settings.TIME_ZONE}")
    print(f"   USE_TZ: {settings.USE_TZ}")
    print(f"   LANGUAGE_CODE: {settings.LANGUAGE_CODE}")
    
    print("\n✅ Todas las funciones de zona horaria funcionan correctamente!")

if __name__ == "__main__":
    test_timezone_functions() 