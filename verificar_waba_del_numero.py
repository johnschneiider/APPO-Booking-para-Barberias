#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar en qué WABA está realmente el número
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
PHONE_NUMBER_ID = os.getenv('META_WHATSAPP_PHONE_NUMBER_ID', '934844826379145')

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

print("="*60)
print("VERIFICANDO WABA DEL NUMERO")
print("="*60)

print(f"\nPhone Number ID: {PHONE_NUMBER_ID}")

# Intentar obtener el WABA desde el número directamente
print("\n1. Obteniendo informacion del numero...")
print("-"*60)

url1 = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}?fields=id,display_phone_number,verified_name,whatsapp_business_account"
try:
    response = requests.get(url1, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Numero: {data.get('display_phone_number')}")
        print(f"Nombre: {data.get('verified_name')}")
        
        waba_info = data.get('whatsapp_business_account', {})
        if waba_info:
            waba_id = waba_info.get('id', 'N/A')
            waba_name = waba_info.get('name', 'N/A')
            print(f"\n[INFO CRITICO] El numero pertenece al WABA:")
            print(f"  WABA ID: {waba_id}")
            print(f"  WABA Name: {waba_name}")
            
            if waba_id != "122157641048829165":
                print(f"\n[PROBLEMA ENCONTRADO]")
                print(f"El numero esta en el WABA {waba_id} ({waba_name})")
                print(f"Pero tu System User esta configurado para Vital Mix (122157641048829165)")
                print(f"\nSOLUCION:")
                print(f"1. Asigna el WABA {waba_id} ({waba_name}) a tu System User")
                print(f"2. O genera un token seleccionando ese WABA")
            else:
                print(f"\n[OK] El numero esta en Vital Mix (correcto)")
                print(f"El problema es que el token no esta vinculado a este WABA")
        else:
            print("\n[ADVERTENCIA] No se pudo obtener el WABA del numero")
            print("Esto puede indicar que el numero no esta asociado a un WABA")
    else:
        error_data = response.json() if response.text else {}
        error_msg = error_data.get('error', {}).get('message', 'Error desconocido')
        print(f"Error: {error_msg}")
except Exception as e:
    print(f"Error: {e}")

# Intentar obtener desde otra estructura
print("\n2. Intentando obtener WABA desde estructura alternativa...")
print("-"*60)

url2 = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}?fields=id,connected_waba_id"
try:
    response = requests.get(url2, headers=headers)
    if response.status_code == 200:
        data = response.json()
        waba_id = data.get('connected_waba_id', 'N/A')
        if waba_id != 'N/A':
            print(f"Connected WABA ID: {waba_id}")
except Exception as e:
    print(f"Error: {e}")

# Intentar listar todos los WABAs a los que el System User tiene acceso
print("\n3. Intentando listar todos los WABAs accesibles...")
print("-"*60)

# Usar el endpoint correcto para System Users
url3 = f"https://graph.facebook.com/{API_VERSION}/me"
try:
    response = requests.get(url3, headers=headers)
    if response.status_code == 200:
        data = response.json()
        user_id = data.get('id')
        user_name = data.get('name')
        print(f"System User: {user_name} (ID: {user_id})")
        
        # Intentar obtener WABAs usando el endpoint de business
        url4 = f"https://graph.facebook.com/{API_VERSION}/business"
        response2 = requests.get(url4, headers=headers)
        if response2.status_code == 200:
            business_data = response2.json()
            print(f"Business accounts: {json.dumps(business_data, indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("DIAGNOSTICO FINAL")
print("="*60)

print("""
El error 403 indica que:

1. El token tiene permisos correctos (whatsapp_business_messaging)
2. El Phone Number ID existe y es accesible
3. PERO el token NO esta vinculado al WABA correcto

SOLUCION DEFINITIVA:

Cuando generas el token en Meta Business Manager:

1. Ve a: https://business.facebook.com/settings/system-users
2. Selecciona "appo_user"
3. Haz clic en "Generar token"
4. EN LA VENTANA MODAL:
   - DEBES ver una lista de "Assets" o "Activos"
   - Busca "WhatsApp Business Account" o "WABA"
   - DEBES MARCAR/SELECCIONAR el WABA donde esta tu numero
   - Si tu numero es 15558371742, busca en que WABA esta
   - Selecciona ESE WABA (puede ser "Vital Mix" u otro)
   - Permisos: whatsapp_business_messaging
   - Genera el token
5. COPIA EL TOKEN y actualiza .env

IMPORTANTE: Si en la ventana de generar token NO ves una lista de 
WABAs para seleccionar, entonces:
- El System User NO tiene WABAs asignados
- Primero asigna el WABA en "Activos asignados"
- LUEGO genera el token
""")

print("="*60)
