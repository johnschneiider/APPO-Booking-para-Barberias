#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar y aplicar la migración de ClienteProvisional manualmente
si es necesario
"""

import django
import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.db import connection

print("="*60)
print("VERIFICANDO ESTADO DE LA MIGRACIÓN")
print("="*60)

# Verificar si la columna cliente_id permite NULL
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, is_nullable, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'clientes_reserva' 
        AND column_name = 'cliente_id';
    """)
    resultado = cursor.fetchone()
    
    if resultado:
        col_name, is_nullable, data_type = resultado
        print(f"\nColumna 'cliente_id':")
        print(f"  - Permite NULL: {is_nullable}")
        print(f"  - Tipo de datos: {data_type}")
        
        if is_nullable == 'NO':
            print("\n❌ PROBLEMA: La columna 'cliente_id' NO permite NULL")
            print("\nSolución:")
            print("Ejecuta este comando SQL en PostgreSQL:")
            print("\n  ALTER TABLE clientes_reserva ALTER COLUMN cliente_id DROP NOT NULL;")
            print("\nO ejecuta la migración:")
            print("  python manage.py migrate clientes 0013")
        else:
            print("\n✅ OK: La columna 'cliente_id' permite NULL")
    else:
        print("\n⚠️ No se encontró la columna 'cliente_id'")
    
    # Verificar si existe la columna cliente_provisional_id
    cursor.execute("""
        SELECT column_name, is_nullable, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'clientes_reserva' 
        AND column_name = 'cliente_provisional_id';
    """)
    resultado2 = cursor.fetchone()
    
    if resultado2:
        col_name, is_nullable, data_type = resultado2
        print(f"\nColumna 'cliente_provisional_id':")
        print(f"  - Permite NULL: {is_nullable}")
        print(f"  - Tipo de datos: {data_type}")
    else:
        print("\n❌ PROBLEMA: La columna 'cliente_provisional_id' NO existe")
        print("La migración 0013 no se ha aplicado completamente")

print("\n" + "="*60)
