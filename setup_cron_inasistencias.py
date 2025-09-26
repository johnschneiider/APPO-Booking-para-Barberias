#!/usr/bin/env python3
"""
Script para configurar el procesamiento automático de inasistencias
"""

import os
import sys
from datetime import datetime, timedelta

def crear_cron_job():
    """Crear entrada en crontab para procesar inasistencias cada 5 minutos"""
    
    # Obtener la ruta del proyecto
    proyecto_path = os.path.dirname(os.path.abspath(__file__))
    
    # Comando para procesar inasistencias
    comando = f"cd {proyecto_path} && python manage.py procesar_inasistencias"
    
    # Entrada de crontab (cada 5 minutos)
    cron_entry = f"*/5 * * * * {comando} >> logs/inasistencias.log 2>&1"
    
    print("🔧 Configurando procesamiento automático de inasistencias...")
    print(f"📁 Directorio del proyecto: {proyecto_path}")
    print(f"⏰ Frecuencia: Cada 5 minutos")
    print(f"📝 Comando: {comando}")
    
    # Crear archivo temporal con la entrada de cron
    temp_file = "/tmp/cron_inasistencias"
    with open(temp_file, 'w') as f:
        f.write(cron_entry + "\n")
    
    # Agregar al crontab
    os.system(f"crontab -l 2>/dev/null | cat - {temp_file} | crontab -")
    
    # Limpiar archivo temporal
    os.remove(temp_file)
    
    print("✅ Cron job configurado exitosamente!")
    print("📊 Los logs se guardarán en: logs/inasistencias.log")

def crear_cron_job_windows():
    """Crear tarea programada en Windows"""
    
    proyecto_path = os.path.dirname(os.path.abspath(__file__))
    comando = f'cd /d "{proyecto_path}" && python manage.py procesar_inasistencias'
    
    # Crear archivo batch
    batch_file = os.path.join(proyecto_path, "procesar_inasistencias.bat")
    with open(batch_file, 'w') as f:
        f.write(f'@echo off\n')
        f.write(f'cd /d "{proyecto_path}"\n')
        f.write(f'python manage.py procesar_inasistencias\n')
        f.write(f'pause\n')
    
    print("🔧 Configurando tarea programada en Windows...")
    print(f"📁 Directorio del proyecto: {proyecto_path}")
    print(f"⏰ Frecuencia: Cada 5 minutos")
    print(f"📝 Archivo batch creado: {batch_file}")
    
    # Crear tarea programada usando schtasks
    task_name = "APPO_ProcesarInasistencias"
    schedule = "every 5 minutes"
    
    # Comando para crear la tarea
    schtasks_cmd = f'schtasks /create /tn "{task_name}" /tr "{batch_file}" /sc minute /mo 5 /f'
    
    print(f"🔄 Ejecutando: {schtasks_cmd}")
    result = os.system(schtasks_cmd)
    
    if result == 0:
        print("✅ Tarea programada creada exitosamente!")
        print("📊 Para ver las tareas: schtasks /query")
        print("📊 Para eliminar la tarea: schtasks /delete /tn APPO_ProcesarInasistencias")
    else:
        print("❌ Error al crear la tarea programada")
        print("💡 Ejecuta el script como administrador")

def verificar_configuracion():
    """Verificar que la configuración esté correcta"""
    
    print("🔍 Verificando configuración...")
    
    # Verificar que existe el comando
    proyecto_path = os.path.dirname(os.path.abspath(__file__))
    manage_py = os.path.join(proyecto_path, "manage.py")
    
    if not os.path.exists(manage_py):
        print("❌ Error: No se encontró manage.py")
        return False
    
    # Verificar que existe el comando personalizado
    comando_path = os.path.join(proyecto_path, "clientes", "management", "commands", "procesar_inasistencias.py")
    
    if not os.path.exists(comando_path):
        print("❌ Error: No se encontró el comando procesar_inasistencias.py")
        return False
    
    # Crear directorio de logs si no existe
    logs_dir = os.path.join(proyecto_path, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print("📁 Directorio de logs creado")
    
    print("✅ Configuración verificada correctamente")
    return True

def main():
    """Función principal"""
    
    print("🚀 Configurador de Procesamiento Automático de Inasistencias")
    print("=" * 60)
    
    # Verificar configuración
    if not verificar_configuracion():
        sys.exit(1)
    
    # Detectar sistema operativo
    if os.name == 'nt':  # Windows
        print("🪟 Detectado Windows")
        crear_cron_job_windows()
    else:  # Linux/Mac
        print("🐧 Detectado Linux/Mac")
        crear_cron_job()
    
    print("\n📋 Instrucciones adicionales:")
    print("1. El sistema procesará inasistencias cada 5 minutos")
    print("2. Los logs se guardarán en logs/inasistencias.log")
    print("3. Para probar manualmente: python manage.py procesar_inasistencias")
    print("4. Para ver logs en tiempo real: tail -f logs/inasistencias.log")

if __name__ == "__main__":
    main() 