#!/usr/bin/env python
"""
Script para verificar y crear la tabla de fidelización en PostgreSQL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.db import connection
from django.core.management import call_command

def verificar_tabla():
    """Verifica si la tabla existe y la crea si no"""
    with connection.cursor() as cursor:
        # Verificar si la tabla existe
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'fidelizacion_mensajes'
            );
        """)
        existe = cursor.fetchone()[0]
        
        if existe:
            print("✅ La tabla fidelizacion_mensajes existe")
        else:
            print("❌ La tabla fidelizacion_mensajes NO existe")
            print("📝 Aplicando migración...")
            call_command('migrate', 'fidelizacion', verbosity=2)
            
            # Verificar de nuevo
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'fidelizacion_mensajes'
                );
            """)
            existe = cursor.fetchone()[0]
            if existe:
                print("✅ Tabla creada exitosamente")
            else:
                print("❌ Error: No se pudo crear la tabla")

if __name__ == '__main__':
    verificar_tabla()

