#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para buscar credenciales configuradas en el proyecto local
"""
import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

print("=" * 60)
print("BUSCANDO CREDENCIALES CONFIGURADAS")
print("=" * 60)

# 1. Buscar archivo .env
print("\n1. BUSCANDO ARCHIVO .env...")
env_files = ['.env', '.env.local', '.env.production', 'env_production.txt', 'env_vps_production.txt']
found_env = False
for env_file in env_files:
    env_path = BASE_DIR / env_file
    if env_path.exists():
        print(f"   [OK] Encontrado: {env_file}")
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"   Contenido relevante:")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if any(keyword in line.upper() for keyword in ['POSTGRES', 'EMAIL', 'TWILIO', 'DATABASE']):
                            # Ocultar passwords
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                if any(secret in key.upper() for secret in ['PASSWORD', 'TOKEN', 'SECRET', 'KEY']):
                                    if value and value not in ['', 'tu-', 'TU_']:
                                        masked = value[:4] + '*' * min(20, len(value) - 4) if len(value) > 4 else '****'
                                        print(f"      {key}={masked}")
                                else:
                                    print(f"      {line}")
        except Exception as e:
            print(f"   [ERROR] Error leyendo archivo: {e}")
        found_env = True

if not found_env:
    print("   [NO] No se encontro archivo .env")

# 2. Variables de entorno del sistema
print("\n2. VARIABLES DE ENTORNO DEL SISTEMA...")
env_vars = {
    'POSTGRES_DB': os.environ.get('POSTGRES_DB'),
    'POSTGRES_USER': os.environ.get('POSTGRES_USER'),
    'POSTGRES_PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
    'POSTGRES_HOST': os.environ.get('POSTGRES_HOST'),
    'EMAIL_HOST_USER': os.environ.get('EMAIL_HOST_USER'),
    'EMAIL_HOST_PASSWORD': os.environ.get('EMAIL_HOST_PASSWORD'),
    'TWILIO_ACCOUNT_SID': os.environ.get('TWILIO_ACCOUNT_SID'),
    'TWILIO_AUTH_TOKEN': os.environ.get('TWILIO_AUTH_TOKEN'),
    'TWILIO_WHATSAPP_NUMBER': os.environ.get('TWILIO_WHATSAPP_NUMBER'),
}

found_vars = False
for key, value in env_vars.items():
    if value:
        found_vars = True
        if 'PASSWORD' in key or 'TOKEN' in key or 'SECRET' in key:
            masked = value[:4] + '*' * min(20, len(value) - 4) if len(value) > 4 else '****'
            print(f"   [OK] {key}={masked}")
        else:
            print(f"   [OK] {key}={value}")

if not found_vars:
    print("   [NO] No se encontraron variables de entorno configuradas")

# 3. Buscar en docker-compose.yml
print("\n3. BUSCANDO EN docker-compose.yml...")
docker_compose = BASE_DIR / 'docker-compose.yml'
if docker_compose.exists():
    try:
        with open(docker_compose, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'POSTGRES_DB' in content:
                print("   [OK] Encontrado docker-compose.yml con configuracion PostgreSQL")
                # Extraer valores
                db_match = re.search(r'POSTGRES_DB[:\s]*([^\s\n]+)', content)
                user_match = re.search(r'POSTGRES_USER[:\s]*([^\s\n]+)', content)
                pwd_match = re.search(r'POSTGRES_PASSWORD[:\s]*([^\s\n]+)', content)
                
                if db_match:
                    print(f"      POSTGRES_DB: {db_match.group(1)}")
                if user_match:
                    print(f"      POSTGRES_USER: {user_match.group(1)}")
                if pwd_match:
                    pwd = pwd_match.group(1).strip('"\'${}')
                    print(f"      POSTGRES_PASSWORD: {pwd}")
    except Exception as e:
        print(f"   [ERROR] Error leyendo docker-compose.yml: {e}")

# 4. Valores por defecto encontrados
print("\n4. VALORES POR DEFECTO EN EL PROYECTO...")
print("   PostgreSQL (Docker):")
print("      POSTGRES_DB: vitalmix")
print("      POSTGRES_USER: vitaluser")
print("      POSTGRES_PASSWORD: vitalpass")
print("")
print("   Email:")
print("      EMAIL_HOST: smtp.gmail.com")
print("      EMAIL_PORT: 587")
print("      EMAIL_USE_TLS: True")
print("")
print("   Twilio:")
print("      TWILIO_WHATSAPP_NUMBER: +14155238886 (sandbox)")

# 5. Resumen y recomendaciones
print("\n" + "=" * 60)
print("RESUMEN Y RECOMENDACIONES")
print("=" * 60)
print("""
Si no encontraste las credenciales:

1. PostgreSQL:
   - Valores por defecto en Docker: vitalmix/vitaluser/vitalpass
   - Para VPS: Puedes crear nuevos valores seguros

2. Email:
   - Revisa tu cuenta de Gmail
   - Necesitas una "Contrasena de aplicacion" de Gmail
   - O configura SendGrid/AWS SES

3. Twilio:
   - Accede a https://console.twilio.com
   - Ve a Dashboard para ver Account SID y Auth Token
   - Si no tienes cuenta, puedes crear una gratis

PARA LA VPS:
- Puedes usar valores nuevos y seguros (RECOMENDADO)
- O recuperar las credenciales desde tu cuenta de Twilio/Gmail
- El script deploy_vps.sh creara la base de datos automaticamente
""")

print("\n[OK] Busqueda completada")
