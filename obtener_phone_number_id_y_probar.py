#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para obtener el Phone Number ID correcto y probar el envío
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
TO_PHONE = "573117451274"  # Tu número de prueba

if not ACCESS_TOKEN:
    print("[ERROR] No se encontro TOKEN_WHATSAPP o META_WHATSAPP_ACCESS_TOKEN en .env")
    sys.exit(1)

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

print("="*60)
print("OBTENIENDO PHONE NUMBER ID Y PROBANDO ENVIO")
print("="*60)

print(f"\nToken encontrado: {ACCESS_TOKEN[:20]}...{ACCESS_TOKEN[-10:]}")
print(f"API Version: {API_VERSION}")

# Paso 1: Obtener información del usuario/empresa
print("\n1. Obteniendo informacion del token...")
print("-"*60)

url1 = f"https://graph.facebook.com/{API_VERSION}/me?fields=id,name"
try:
    response = requests.get(url1, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Usuario/Empresa: {json.dumps(data, indent=2, ensure_ascii=False)}")
        user_id = data.get('id')
        user_name = data.get('name', 'N/A')
    else:
        print(f"Error: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Paso 2: Obtener WABA IDs asociados
print("\n2. Obteniendo WhatsApp Business Accounts...")
print("-"*60)

# Intentar obtener WABAs usando diferentes métodos
waba_ids = []

# Método 1: Desde el usuario
url2 = f"https://graph.facebook.com/{API_VERSION}/me?fields=owned_whatsapp_business_accounts"
try:
    response = requests.get(url2, headers=headers)
    if response.status_code == 200:
        data = response.json()
        wabas = data.get('owned_whatsapp_business_accounts', {}).get('data', [])
        for waba in wabas:
            waba_id = waba.get('id')
            waba_name = waba.get('name', 'N/A')
            waba_ids.append(waba_id)
            print(f"  WABA encontrado: {waba_name} (ID: {waba_id})")
except Exception as e:
    print(f"  Error método 1: {e}")

# Método 2: Buscar directamente
if not waba_ids:
    url3 = f"https://graph.facebook.com/{API_VERSION}/me?fields=whatsapp_business_accounts"
    try:
        response = requests.get(url3, headers=headers)
        if response.status_code == 200:
            data = response.json()
            wabas = data.get('whatsapp_business_accounts', {}).get('data', [])
            for waba in wabas:
                waba_id = waba.get('id')
                waba_name = waba.get('name', 'N/A')
                waba_ids.append(waba_id)
                print(f"  WABA encontrado: {waba_name} (ID: {waba_id})")
    except Exception as e:
        print(f"  Error método 2: {e}")

if not waba_ids:
    print("  No se encontraron WABAs. Usaremos el ID conocido: 122157641048829165")
    waba_ids = ["122157641048829165"]  # Vital Mix WABA ID que vimos antes

# Paso 3: Obtener Phone Numbers desde cada WABA
print("\n3. Obteniendo Phone Numbers de los WABAs...")
print("-"*60)

phone_numbers = []
for waba_id in waba_ids:
    url4 = f"https://graph.facebook.com/{API_VERSION}/{waba_id}/phone_numbers"
    try:
        response = requests.get(url4, headers=headers)
        print(f"\n  WABA {waba_id}: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            phones = data.get('data', [])
            for phone in phones:
                phone_id = phone.get('id')
                display_number = phone.get('display_phone_number', 'N/A')
                verified_name = phone.get('verified_name', 'N/A')
                phone_numbers.append({
                    'id': phone_id,
                    'number': display_number,
                    'verified_name': verified_name,
                    'waba_id': waba_id
                })
                print(f"    Phone Number ID: {phone_id}")
                print(f"    Numero: {display_number}")
                print(f"    Nombre: {verified_name}")
        else:
            print(f"    Error: {response.text}")
    except Exception as e:
        print(f"    Error obteniendo numeros: {e}")

# Paso 4: Si no encontramos números, intentar método alternativo
if not phone_numbers:
    print("\n4. Intentando metodo alternativo para obtener numeros...")
    print("-"*60)
    
    # Intentar desde el endpoint de configuración de WhatsApp
    for waba_id in waba_ids:
        url5 = f"https://graph.facebook.com/{API_VERSION}/{waba_id}?fields=phone_numbers"
        try:
            response = requests.get(url5, headers=headers)
            if response.status_code == 200:
                data = response.json()
                phones = data.get('phone_numbers', {}).get('data', [])
                for phone in phones:
                    phone_id = phone.get('id')
                    display_number = phone.get('display_phone_number', 'N/A')
                    verified_name = phone.get('verified_name', 'N/A')
                    phone_numbers.append({
                        'id': phone_id,
                        'number': display_number,
                        'verified_name': verified_name,
                        'waba_id': waba_id
                    })
                    print(f"  Phone Number ID: {phone_id}")
                    print(f"  Numero: {display_number}")
                    print(f"  Nombre: {verified_name}")
        except Exception as e:
            print(f"  Error: {e}")

# Paso 5: Probar envío con los números encontrados
if phone_numbers:
    print("\n5. Probando envio con los Phone Numbers encontrados...")
    print("-"*60)
    
    for phone_info in phone_numbers:
        phone_id = phone_info['id']
        display_number = phone_info['number']
        
        print(f"\nProbando con Phone Number ID: {phone_id} ({display_number})")
        
        url6 = f"https://graph.facebook.com/{API_VERSION}/{phone_id}/messages"
        
        # Intentar con template 'appo'
        payload = {
            "messaging_product": "whatsapp",
            "to": TO_PHONE,
            "type": "template",
            "template": {
                "name": "appo",
                "language": {
                    "code": "es"
                },
                "components": [{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "Prueba desde Meta WhatsApp API"}
                    ]
                }]
            }
        }
        
        try:
            response = requests.post(url6, headers=headers, json=payload)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                message_id = data.get('messages', [{}])[0].get('id', 'N/A')
                print(f"  [OK] Mensaje enviado exitosamente!")
                print(f"  Message ID: {message_id}")
                print(f"\n  Phone Number ID CORRECTO: {phone_id}")
                print(f"  Numero: {display_number}")
                break  # Si funciona, no probamos los demás
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get('error', {}).get('message', 'Error desconocido')
                error_code = error_data.get('error', {}).get('code', 'N/A')
                print(f"  [ERROR] Code: {error_code}")
                print(f"  Mensaje: {error_msg}")
        except Exception as e:
            print(f"  [ERROR] Excepcion: {e}")
else:
    print("\n[ADVERTENCIA] No se encontraron Phone Numbers via API")
    print("\nNecesitas obtener el Phone Number ID manualmente:")
    print("1. Ve a: https://business.facebook.com/wa/manage/phone-numbers/")
    print("2. Haz clic en tu numero")
    print("3. Copia el Phone Number ID de la URL o detalles")

print("\n" + "="*60)
print("RESUMEN PARA .ENV:")
print("="*60)
if phone_numbers:
    phone_info = phone_numbers[0]  # Usar el primero encontrado
    print(f"META_WHATSAPP_PHONE_NUMBER_ID={phone_info['id']}")
    print(f"META_WHATSAPP_ENABLED=True")
    print(f"META_WHATSAPP_API_VERSION={API_VERSION}")
else:
    print("META_WHATSAPP_PHONE_NUMBER_ID=<OBTENER_DESDE_META_BUSINESS_MANAGER>")
print(f"TOKEN_WHATSAPP=<YA_CONFIGURADO>")
print("="*60)
