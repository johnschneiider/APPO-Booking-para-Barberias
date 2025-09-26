#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appo.settings')
django.setup()

from profesionales.models import Profesional, HorarioProfesional
from datetime import date, time
from datetime import datetime

def test_horarios_fix():
    print("=== PRUEBA DE CORRECCIÓN DE HORARIOS ===")
    
    # Buscar el profesional del error (ID 1106 según el log)
    try:
        profesional = Profesional.objects.get(id=1106)
        print(f"✅ Profesional encontrado: {profesional.nombre_completo}")
    except Profesional.DoesNotExist:
        print("❌ Profesional con ID 1106 no encontrado")
        # Buscar cualquier profesional con horarios
        profesional = Profesional.objects.filter(horarios__isnull=False).first()
        if profesional:
            print(f"✅ Usando profesional alternativo: {profesional.nombre_completo}")
        else:
            print("❌ No hay profesionales con horarios configurados")
            return
    
    # Verificar horarios del profesional
    horarios = HorarioProfesional.objects.filter(profesional=profesional)
    print(f"\n📅 Horarios configurados para {profesional.nombre_completo}:")
    
    if not horarios.exists():
        print("❌ NO HAY HORARIOS CONFIGURADOS")
        return
    
    for horario in horarios:
        print(f"   {horario.get_dia_semana_display()}: {horario.hora_inicio} - {horario.hora_fin} ({'Disponible' if horario.disponible else 'No disponible'})")
    
    # Probar con la fecha del error (2025-07-31 es jueves)
    fecha_test = date(2025, 7, 31)  # Jueves
    nombre_dia = fecha_test.strftime('%A')
    print(f"\n📅 Probando fecha: {fecha_test} ({nombre_dia})")
    
    # Aplicar la misma lógica del formulario corregido
    nombre_dia_es = {
        'Monday': 'lunes',
        'Tuesday': 'martes',
        'Wednesday': 'miercoles',
        'Thursday': 'jueves',
        'Friday': 'viernes',
        'Saturday': 'sabado',
        'Sunday': 'domingo'
    }.get(nombre_dia, nombre_dia.lower())
    
    print(f"   Nombre en inglés: {nombre_dia}")
    print(f"   Nombre en español: {nombre_dia_es}")
    
    # Buscar horario para ese día
    horario_dia = HorarioProfesional.objects.filter(
        profesional=profesional, 
        dia_semana=nombre_dia_es, 
        disponible=True
    ).first()
    
    if horario_dia:
        print(f"✅ Horario encontrado: {horario_dia.hora_inicio} - {horario_dia.hora_fin}")
        
        # Probar con la hora del error (09:00)
        hora_test = time(9, 0)
        print(f"   Probando hora: {hora_test}")
        
        if horario_dia.hora_inicio <= hora_test < horario_dia.hora_fin:
            print(f"✅ Hora {hora_test} está dentro del horario")
        else:
            print(f"❌ Hora {hora_test} NO está dentro del horario")
    else:
        print(f"❌ No hay horario configurado para {nombre_dia_es}")
    
    # Probar con diferentes días de la semana
    print(f"\n🧪 Probando todos los días de la semana:")
    dias_test = [
        date(2025, 7, 28),  # Lunes
        date(2025, 7, 29),  # Martes
        date(2025, 7, 30),  # Miércoles
        date(2025, 7, 31),  # Jueves
        date(2025, 8, 1),   # Viernes
        date(2025, 8, 2),   # Sábado
        date(2025, 8, 3),   # Domingo
    ]
    
    for fecha in dias_test:
        nombre_dia = fecha.strftime('%A')
        nombre_dia_es = {
            'Monday': 'lunes',
            'Tuesday': 'martes',
            'Wednesday': 'miercoles',
            'Thursday': 'jueves',
            'Friday': 'viernes',
            'Saturday': 'sabado',
            'Sunday': 'domingo'
        }.get(nombre_dia, nombre_dia.lower())
        
        horario = HorarioProfesional.objects.filter(
            profesional=profesional, 
            dia_semana=nombre_dia_es, 
            disponible=True
        ).first()
        
        if horario:
            print(f"   ✅ {fecha.strftime('%d/%m')} ({nombre_dia_es}): {horario.hora_inicio} - {horario.hora_fin}")
        else:
            print(f"   ❌ {fecha.strftime('%d/%m')} ({nombre_dia_es}): No configurado")
    
    print(f"\n✅ Corrección de horarios probada exitosamente!")

if __name__ == "__main__":
    test_horarios_fix() 