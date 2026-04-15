#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar Meta WhatsApp API con las credenciales proporcionadas
"""

import os
import sys
import io
import json
import requests

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

print("="*60)
print("PROBANDO META WHATSAPP API")
print("="*60)

# Credenciales del curl
PHONE_NUMBER_ID = "980127665178312"
ACCESS_TOKEN = "EAFyLg5JAXrMBQekqoyekuWG06dEV29W47rhrkFnw9nochYCGsSXEX0Js814JaQrxhYgYCR291GtSFORlazuZA4v3D7T6a8pJXATtrDLDX5O9aO6pByFAtqIIza4W3ZAjzZAtZADPVGI5F8jQ9THx9Rt132WlbyqipJxFtkBeJHdj8lUY2H8ff8VDFo3TOqllXJzC8sXzjmLvTfSTXEVNFK7NDZAa6GTpAtV37gvCKmDxZBh6ZBsYo6zzBrb0ZAZCmar144ZBwpxfoF5HJdU5eZBIODXZBkYPsgZDZD"
API_VERSION = "v22.0"
TO_PHONE = "573117451274"  # Tu número

# URL del endpoint
url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"

# Headers
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

print(f"\nPhone Number ID: {PHONE_NUMBER_ID}")
print(f"API Version: {API_VERSION}")
print(f"To Phone: {TO_PHONE}")

# Prueba 1: Template de ejemplo (del curl)
print("\n" + "-"*60)
print("PRUEBA 1: Template de ejemplo (jaspers_market_order_confirmation_v1)")
print("-"*60)

payload1 = {
    "messaging_product": "whatsapp",
    "to": TO_PHONE,
    "type": "template",
    "template": {
        "name": "jaspers_market_order_confirmation_v1",
        "language": {
            "code": "en_US"
        },
        "components": [{
            "type": "body",
            "parameters": [
                {"type": "text", "text": "John Doe"},
                {"type": "text", "text": "123456"},
                {"type": "text", "text": "Jan 10, 2026"}
            ]
        }]
    }
}

print(f"Payload: {json.dumps(payload1, indent=2, ensure_ascii=False)}")

try:
    response1 = requests.post(url, headers=headers, json=payload1)
    print(f"\nStatus Code: {response1.status_code}")
    print(f"Response: {response1.text}")
    
    if response1.status_code == 200:
        data = response1.json()
        message_id = data.get('messages', [{}])[0].get('id', 'N/A')
        print(f"\n[OK] Mensaje enviado exitosamente!")
        print(f"Message ID: {message_id}")
    else:
        print(f"\n[ERROR] Falló el envío")
        try:
            error_data = response1.json()
            print(f"Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Error: {response1.text}")
except Exception as e:
    print(f"\n[ERROR] Excepción: {e}")

# Prueba 2: Template simple de texto (si el usuario tiene uno)
print("\n" + "-"*60)
print("PRUEBA 2: Template simple de texto (probando con 'appo')")
print("-"*60)

# Primero intentemos con el template "appo" que el usuario creó
payload2 = {
    "messaging_product": "whatsapp",
    "to": TO_PHONE,
    "type": "template",
    "template": {
        "name": "appo",  # Template que creaste
        "language": {
            "code": "es"
        },
        "components": [{
            "type": "body",
            "parameters": [
                {"type": "text", "text": "Prueba de Meta WhatsApp API"}
            ]
        }]
    }
}

print(f"Payload: {json.dumps(payload2, indent=2, ensure_ascii=False)}")

try:
    response2 = requests.post(url, headers=headers, json=payload2)
    print(f"\nStatus Code: {response2.status_code}")
    print(f"Response: {response2.text}")
    
    if response2.status_code == 200:
        data = response2.json()
        message_id = data.get('messages', [{}])[0].get('id', 'N/A')
        print(f"\n[OK] Mensaje enviado exitosamente!")
        print(f"Message ID: {message_id}")
    else:
        print(f"\n[ERROR] Falló el envío")
        try:
            error_data = response2.json()
            print(f"Error: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Error: {response2.text}")
except Exception as e:
    print(f"\n[ERROR] Excepción: {e}")

# Prueba 3: Listar templates disponibles (si la API lo permite)
print("\n" + "-"*60)
print("PRUEBA 3: Listar templates disponibles")
print("-"*60)

templates_url = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/message_templates"
try:
    response3 = requests.get(templates_url, headers=headers)
    print(f"Status Code: {response3.status_code}")
    if response3.status_code == 200:
        templates_data = response3.json()
        print(f"\nTemplates disponibles:")
        print(json.dumps(templates_data, indent=2, ensure_ascii=False))
    else:
        print(f"Response: {response3.text}")
except Exception as e:
    print(f"[ERROR] Excepción: {e}")

print("\n" + "="*60)
