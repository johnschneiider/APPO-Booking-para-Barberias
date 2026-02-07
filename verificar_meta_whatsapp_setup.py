#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar la configuración de Meta WhatsApp API
"""

import requests
import json

PHONE_NUMBER_ID = "980127665178312"
ACCESS_TOKEN = "EAFyLg5JAXrMBQekqoyekuWG06dEV29W47rhrkFnw9nochYCGsSXEX0Js814JaQrxhYgYCR291GtSFORlazuZA4v3D7T6a8pJXATtrDLDX5O9aO6pByFAtqIIza4W3ZAjzZAtZADPVGI5F8jQ9THx9Rt132WlbyqipJxFtkBeJHdj8lUY2H8ff8VDFo3TOqllXJzC8sXzjmLvTfSTXEVNFK7NDZAa6GTpAtV37gvCKmDxZBh6ZBsYo6zzBrb0ZAZCmar144ZBwpxfoF5HJdU5eZBIODXZBkYPsgZDZD"
API_VERSION = "v22.0"

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

print("="*60)
print("VERIFICANDO CONFIGURACION META WHATSAPP")
print("="*60)

# Prueba 1: Verificar información del Phone Number ID
print("\n1. Verificando Phone Number ID...")
print("-"*60)

url1 = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}"
try:
    response = requests.get(url1, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Info del número: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
        # Si falla, puede ser que necesitemos usar otro endpoint
        print("\nIntentando obtener info del WABA...")
        url_waba = f"https://graph.facebook.com/{API_VERSION}/me/phone_numbers"
        response_waba = requests.get(url_waba, headers=headers)
        print(f"Status: {response_waba.status_code}")
        if response_waba.status_code == 200:
            print(f"Números disponibles: {response_waba.text}")
        else:
            print(f"Error: {response_waba.text}")
except Exception as e:
    print(f"Error: {e}")

# Prueba 2: Listar templates disponibles
print("\n2. Listando templates disponibles...")
print("-"*60)

url2 = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/message_templates"
try:
    response = requests.get(url2, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        templates = response.json()
        print(f"Templates encontrados: {len(templates.get('data', []))}")
        for template in templates.get('data', []):
            print(f"\n  - Nombre: {template.get('name')}")
            print(f"    Idioma: {template.get('language')}")
            print(f"    Estado: {template.get('status')}")
            print(f"    Categoría: {template.get('category')}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Prueba 3: Verificar permisos del Access Token
print("\n3. Verificando permisos del Access Token...")
print("-"*60)

url3 = f"https://graph.facebook.com/{API_VERSION}/me/permissions"
try:
    response = requests.get(url3, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        perms = response.json()
        print(f"Permisos: {json.dumps(perms, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Prueba 4: Obtener información del WABA
print("\n4. Verificando WhatsApp Business Account...")
print("-"*60)

url4 = f"https://graph.facebook.com/{API_VERSION}/me?fields=id,name"
try:
    response = requests.get(url4, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"WABA Info: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("Ahora intentemos enviar un mensaje...")
print("="*60)

# Prueba 5: Intentar enviar mensaje usando el template 'appo' que creaste
print("\n5. Intentando enviar mensaje con template 'appo'...")
print("-"*60)

# Para números de prueba de Meta, a veces necesitas que el destinatario esté en tu lista de números permitidos
# Probemos con tu número
TO_PHONE = "573117451274"  # Tu número

url5 = f"https://graph.facebook.com/{API_VERSION}/{PHONE_NUMBER_ID}/messages"

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
                {"type": "text", "text": "Hola! Prueba desde Meta WhatsApp API"}
            ]
        }]
    }
}

print(f"Enviando a: {TO_PHONE}")
print(f"Template: appo")
print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(url5, headers=headers, json=payload)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        message_id = data.get('messages', [{}])[0].get('id', 'N/A')
        print(f"\n[OK] Mensaje enviado exitosamente!")
        print(f"Message ID: {message_id}")
    else:
        error_data = response.json() if response.text else {}
        error_msg = error_data.get('error', {}).get('message', 'Error desconocido')
        error_code = error_data.get('error', {}).get('code', 'N/A')
        print(f"\n[ERROR] Falló el envío")
        print(f"Error Code: {error_code}")
        print(f"Error Message: {error_msg}")
        
        # Si es un error de permisos o número no verificado
        if error_code == 100:
            print("\nPosibles soluciones:")
            print("1. Verifica que el número destino esté en tu lista de números permitidos")
            print("2. Para números de prueba, solo puedes enviar a números previamente verificados")
            print("3. Verifica que el Access Token tenga permisos whatsapp_business_messaging")
except Exception as e:
    print(f"\n[ERROR] Excepción: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
