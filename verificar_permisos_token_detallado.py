#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar en detalle los permisos del token y acceso al WABA
"""

import os
import sys
import io
import json
import requests
from dotenv import load_dotenv

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

load_dotenv()

ACCESS_TOKEN = os.getenv('TOKEN_WHATSAPP') or os.getenv('META_WHATSAPP_ACCESS_TOKEN', '')
API_VERSION = os.getenv('META_WHATSAPP_API_VERSION', 'v22.0')
PHONE_NUMBER_ID = os.getenv('META_WHATSAPP_PHONE_NUMBER_ID', '')

if not ACCESS_TOKEN:
    print("[ERROR] No se encontro TOKEN_WHATSAPP en .env")
    sys.exit(1)

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

print("="*60)
print("VERIFICACION DETALLADA DE PERMISOS")
print("="*60)

print(f"\nToken: {ACCESS_TOKEN[:30]}...{ACCESS_TOKEN[-20:]}")
print(f"Phone Number ID: {PHONE_NUMBER_ID}")
print(f"API Version: {API_VERSION}")

# 1. Verificar permisos del token
print("\n1. PERMISOS DEL TOKEN:")
print("-"*60)

url1 = f"https://graph.facebook.com/{API_VERSION}/me/permissions"
try:
    response = requests.get(url1, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("Permisos otorgados:")
        for perm in data.get('data', []):
            status = perm.get('status', '')
            perm_name = perm.get('permission', '')
            icon = "OK" if status == "granted" else "X"
            print(f"  [{icon}] {perm_name}: {status}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# 2. Verificar información del usuario del token
print("\n2. INFORMACION DEL USUARIO DEL TOKEN:")
print("-"*60)

url2 = f"https://graph.facebook.com/{API_VERSION}/me?fields=id,name"
try:
    response = requests.get(url2, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print(f"ID: {data.get('id')}")
        print(f"Nombre: {data.get('name')}")
        user_id = data.get('id')
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# 3. Intentar obtener WABAs desde diferentes endpoints
print("\n3. INTENTANDO OBTENER WABAs:")
print("-"*60)

waba_endpoints = [
    f"{API_VERSION}/me?fields=owned_whatsapp_business_accounts",
    f"{API_VERSION}/me?fields=whatsapp_business_accounts",
    f"{API_VERSION}/{user_id}?fields=owned_whatsapp_business_accounts",
]

for endpoint in waba_endpoints:
    url = f"https://graph.facebook.com/{endpoint}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"\nEndpoint: {endpoint}")
            print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # Buscar WABAs en diferentes estructuras
            wabas = []
            if 'owned_whatsapp_business_accounts' in data:
                wabas = data['owned_whatsapp_business_accounts'].get('data', [])
            elif 'whatsapp_business_accounts' in data:
                wabas = data['whatsapp_business_accounts'].get('data', [])
            
            if wabas:
                print(f"WABAs encontrados: {len(wabas)}")
                for waba in wabas:
                    print(f"  - ID: {waba.get('id')}")
                    print(f"    Nombre: {waba.get('name', 'N/A')}")
        else:
            print(f"Endpoint {endpoint}: Error {response.status_code}")
    except Exception as e:
        print(f"Error en {endpoint}: {e}")

# 4. Verificar acceso directo al Phone Number ID
print("\n4. VERIFICANDO ACCESO AL PHONE NUMBER ID:")
print("-"*60)

if PHONE_NUMBER_ID:
    # Intentar obtener info del número
    url3 = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}?fields=id,display_phone_number,verified_name"
    try:
        response = requests.get(url3, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Numero encontrado:")
            print(f"  ID: {data.get('id')}")
            print(f"  Numero: {data.get('display_phone_number', 'N/A')}")
            print(f"  Nombre: {data.get('verified_name', 'N/A')}")
        else:
            error_data = response.json() if response.text else {}
            error_msg = error_data.get('error', {}).get('message', 'Error desconocido')
            error_code = error_data.get('error', {}).get('code', 'N/A')
            print(f"Error Code: {error_code}")
            print(f"Error Message: {error_msg}")
            
            if error_code == 100:
                print("\n[PROBLEMA] El Phone Number ID no existe o no tienes acceso")
                print("Este Phone Number ID puede ser de otro WABA o no estar asignado a tu System User")
    except Exception as e:
        print(f"Error: {e}")

# 5. Intentar obtener números desde el WABA conocido
print("\n5. INTENTANDO DESDE WABA CONOCIDO (Vital Mix):")
print("-"*60)

WABA_ID = "122157641048829165"  # Vital Mix WABA ID que vimos antes

url4 = f"https://graph.facebook.com/{API_VERSION}/{WABA_ID}/phone_numbers"
try:
    response = requests.get(url4, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        phones = data.get('data', [])
        print(f"Numeros encontrados: {len(phones)}")
        for phone in phones:
            print(f"  - Phone Number ID: {phone.get('id')}")
            print(f"    Numero: {phone.get('display_phone_number', 'N/A')}")
            print(f"    Nombre: {phone.get('verified_name', 'N/A')}")
            
            # Si este es diferente al que tenemos configurado, ese es el problema
            if phone.get('id') != PHONE_NUMBER_ID:
                print(f"\n[ADVERTENCIA] El Phone Number ID configurado ({PHONE_NUMBER_ID})")
                print(f"es diferente al encontrado en el WABA ({phone.get('id')})")
                print(f"Debes usar: {phone.get('id')}")
    else:
        error_data = response.json() if response.text else {}
        error_msg = error_data.get('error', {}).get('message', 'Error desconocido')
        error_code = error_data.get('error', {}).get('code', 'N/A')
        print(f"Error Code: {error_code}")
        print(f"Error Message: {error_msg}")
        
        if error_code == 200:
            print("\n[PROBLEMA CRITICO] No tienes acceso a este WABA")
            print("El System User NO tiene asignado el WABA 'Vital Mix'")
            print("\nSOLUCION:")
            print("1. Ve a: https://business.facebook.com/settings/system-users")
            print("2. Selecciona tu System User")
            print("3. Ve a 'Activos asignados'")
            print("4. Haz clic en 'Asignar activos'")
            print("5. Selecciona 'WhatsApp Business Account'")
            print("6. Busca y selecciona 'Vital Mix' (ID: 122157641048829165)")
            print("7. Permisos: 'Control total' o al menos whatsapp_business_messaging")
            print("8. Guarda y GENERA UN NUEVO TOKEN")
except Exception as e:
    print(f"Error: {e}")

# 6. Verificar acceso de lectura al WABA
print("\n6. VERIFICANDO ACCESO DE LECTURA AL WABA:")
print("-"*60)

url5 = f"https://graph.facebook.com/{API_VERSION}/{WABA_ID}?fields=id,name,timezone_id"
try:
    response = requests.get(url5, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Tienes acceso de lectura al WABA:")
        print(f"  ID: {data.get('id')}")
        print(f"  Nombre: {data.get('name')}")
        print(f"  Timezone: {data.get('timezone_id', 'N/A')}")
    else:
        error_data = response.json() if response.text else {}
        error_msg = error_data.get('error', {}).get('message', 'Error desconocido')
        print(f"[ERROR] No tienes acceso de lectura al WABA: {error_msg}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("DIAGNOSTICO COMPLETO")
print("="*60)

print("""
Si el error persiste, las posibles causas son:

1. System User no tiene el WABA asignado:
   - Verifica en: https://business.facebook.com/settings/system-users
   - Tu System User DEBE aparecer en "Activos asignados" con el WABA "Vital Mix"

2. Permisos incorrectos al generar el token:
   - Al generar el token, DEBES seleccionar el WABA "Vital Mix"
   - Debes marcar el permiso "whatsapp_business_messaging"

3. Phone Number ID incorrecto:
   - El Phone Number ID debe ser del número que está en tu WABA
   - Si el número +1 555 201 5498 es de prueba, puede no estar en tu WABA

4. El número no está verificado/aprobado:
   - Verifica que el número esté en estado "Connected" o "Approved"
   - Ve a: https://business.facebook.com/wa/manage/phone-numbers/
""")

print("="*60)
