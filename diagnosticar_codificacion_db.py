#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para diagnosticar problemas de codificación en variables de entorno de base de datos
"""
import os
import sys
import io
from pathlib import Path

# Configurar stdout para UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Cargar variables de entorno
from dotenv import load_dotenv
try:
    load_dotenv(encoding='utf-8')
except:
    load_dotenv()

# Variables a verificar
db_vars = [
    'POSTGRES_DB',
    'POSTGRES_USER',
    'POSTGRES_PASSWORD',
    'POSTGRES_HOST',
    'POSTGRES_PORT',
]

print("=" * 60)
print("DIAGNÓSTICO DE CODIFICACIÓN - VARIABLES DE BASE DE DATOS")
print("=" * 60)
print()

for var in db_vars:
    value = os.environ.get(var, 'NO DEFINIDA')
    
    if value == 'NO DEFINIDA':
        print(f"[ERROR] {var}: NO DEFINIDA")
        continue
    
    # Verificar tipo
    print(f"[INFO] {var}:")
    print(f"   Tipo: {type(value)}")
    print(f"   Longitud: {len(str(value))}")
    
    # Si es bytes, mostrar información
    if isinstance(value, bytes):
        print(f"   [WARNING] Es BYTES (debe ser string)")
        try:
            decoded_utf8 = value.decode('utf-8')
            print(f"   [OK] Decodificacion UTF-8: OK")
            print(f"   Valor (UTF-8): {decoded_utf8[:50]}...")
        except UnicodeDecodeError as e:
            print(f"   [ERROR] Error UTF-8: {e}")
            try:
                decoded_latin1 = value.decode('latin-1')
                print(f"   [WARNING] Decodificacion Latin-1: OK")
                print(f"   Valor (Latin-1): {decoded_latin1[:50]}...")
            except Exception as e2:
                print(f"   [ERROR] Error Latin-1: {e2}")
    
    # Si es string, verificar codificación
    elif isinstance(value, str):
        print(f"   [OK] Es STRING")
        try:
            # Intentar codificar a UTF-8
            value.encode('utf-8')
            print(f"   [OK] Codificacion UTF-8: VALIDA")
            # Mostrar primeros caracteres (ocultar contraseña)
            if 'PASSWORD' in var:
                print(f"   Valor: {'*' * min(len(value), 20)}")
            else:
                print(f"   Valor: {value[:50]}")
        except UnicodeEncodeError as e:
            print(f"   [ERROR] Error codificacion UTF-8: {e}")
            print(f"   Posicion del error: {e.start}-{e.end}")
            # Mostrar bytes problemáticos
            try:
                bytes_value = value.encode('latin-1')
                print(f"   Bytes problematicos: {bytes_value[e.start:e.end]}")
                print(f"   Hex: {bytes_value[e.start:e.end].hex()}")
            except:
                pass
    
    # Verificar si hay caracteres problemáticos
    try:
        str_value = str(value)
        problematic_chars = []
        for i, char in enumerate(str_value):
            try:
                char.encode('utf-8')
            except UnicodeEncodeError:
                problematic_chars.append((i, char, ord(char)))
        
        if problematic_chars:
            print(f"   [WARNING] Caracteres problematicos encontrados:")
            for i, char, code in problematic_chars[:5]:  # Mostrar solo los primeros 5
                print(f"      Posicion {i}: {repr(char)} (codigo: {code}, hex: {hex(code)})")
                if i < len(str_value) - 1:
                    context = str_value[max(0, i-10):i+10]
                    print(f"      Contexto: ...{context}...")
    except Exception as e:
        print(f"   [ERROR] Error verificando caracteres: {e}")
    
    print()

print("=" * 60)
print("RECOMENDACIONES:")
print("=" * 60)
print("1. Asegúrate de que el archivo .env esté guardado en UTF-8")
print("2. Si hay caracteres especiales, úsalos directamente en UTF-8")
print("3. Evita copiar/pegar desde aplicaciones que usen otra codificación")
print("4. Si el problema persiste, recrea el archivo .env desde cero")
print()
