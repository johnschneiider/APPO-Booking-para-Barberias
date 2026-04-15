#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para obtener el Phone Number ID correcto desde el WABA
"""

import requests
import json

ACCESS_TOKEN = "EAFyLg5JAXrMBQekqoyekuWG06dEV29W47rhrkFnw9nochYCGsSXEX0Js814JaQrxhYgYCR291GtSFORlazuZA4v3D7T6a8pJXATtrDLDX5O9aO6pByFAtqIIza4W3ZAjzZAtZADPVGI5F8jQ9THx9Rt132WlbyqipJxFtkBeJHdj8lUY2H8ff8VDFo3TOqllXJzC8sXzjmLvTfSTXEVNFK7NDZAa6GTpAtV37gvCKmDxZBh6ZBsYo6zzBrb0ZAZCmar144ZBwpxfoF5HJdU5eZBIODXZBkYPsgZDZD"
API_VERSION = "v22.0"
WABA_ID = "122157641048829165"  # Vital Mix WABA ID

headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

print("="*60)
print("OBTENIENDO PHONE NUMBER ID CORRECTO")
print("="*60)

# Método 1: Obtener números desde el WABA directamente
print("\n1. Obteniendo números desde WABA...")
print("-"*60)

url1 = f"https://graph.facebook.com/{API_VERSION}/{WABA_ID}/phone_numbers"
try:
    response = requests.get(url1, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Respuesta completa: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        phone_numbers = data.get('data', [])
        if phone_numbers:
            print(f"\nNúmeros encontrados: {len(phone_numbers)}")
            for num in phone_numbers:
                phone_id = num.get('id')
                verified_name = num.get('verified_name', 'N/A')
                display_phone_number = num.get('display_phone_number', 'N/A')
                quality_rating = num.get('quality_rating', 'N/A')
                
                print(f"\n  Phone Number ID: {phone_id}")
                print(f"  Número: {display_phone_number}")
                print(f"  Nombre verificado: {verified_name}")
                print(f"  Quality Rating: {quality_rating}")
        else:
            print("No se encontraron números en este WABA")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Método 2: Intentar obtener desde el endpoint de phone_numbers del WABA
print("\n2. Intentando método alternativo...")
print("-"*60)

url2 = f"https://graph.facebook.com/{API_VERSION}/{WABA_ID}?fields=phone_numbers"
try:
    response = requests.get(url2, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")

# Método 3: Buscar números de prueba (si es número de prueba)
print("\n3. Verificando si hay números de prueba...")
print("-"*60)

# Para números de prueba, a veces están en otro endpoint
url3 = f"https://graph.facebook.com/{API_VERSION}/me?fields=phone_numbers"
try:
    response = requests.get(url3, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Respuesta: {json.dumps(data, indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")

# Método 4: Intentar obtener desde WhatsApp Manager API
print("\n4. Intentando desde WhatsApp Manager API...")
print("-"*60)

# A veces el Phone Number ID está en la configuración de la app
# Si el número es +1 555 201 5498, es un número de prueba de Meta
# Los números de prueba suelen tener un formato diferente

print("\nNota: El número +1 555 201 5498 es un número de PRUEBA de Meta.")
print("Para números de prueba, el Phone Number ID puede estar en:")
print("1. WhatsApp Manager → Phone numbers → Selecciona el número → Ver detalles")
print("2. O en la URL cuando estás viendo el número en Meta Business Manager")

print("\n" + "="*60)
print("INSTRUCCIONES PARA OBTENER EL PHONE NUMBER ID:")
print("="*60)
print("""
1. Ve a: https://business.facebook.com/wa/manage/phone-numbers/
2. Busca el número +1 555 201 5498
3. Haz clic en el número
4. En la URL del navegador, verás algo como:
   .../phone-numbers/XXXXXXXXXX/...
   Donde XXXXXXXXXX es tu Phone Number ID correcto

O en los detalles del número, busca "Phone number ID" o "ID del número"
""")

print("\n" + "="*60)
