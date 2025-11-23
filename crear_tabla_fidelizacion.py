#!/usr/bin/env python
"""
Script para crear la tabla de fidelización en PostgreSQL directamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from django.db import connection
from django.conf import settings
from django.core.management import call_command

def crear_tabla_manualmente():
    """Crea la tabla manualmente en PostgreSQL"""
    db_engine = settings.DATABASES['default']['ENGINE']
    
    if 'postgresql' not in db_engine:
        print(f"❌ Este script solo funciona con PostgreSQL. Base de datos actual: {db_engine}")
        return False
    
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
            print("✅ La tabla fidelizacion_mensajes ya existe")
            return True
        
        print("📝 Creando tabla fidelizacion_mensajes...")
        
        # Crear la tabla manualmente
        cursor.execute("""
            CREATE TABLE fidelizacion_mensajes (
                id UUID PRIMARY KEY,
                tipo VARCHAR(50) NOT NULL,
                estado VARCHAR(20) NOT NULL,
                destinatario_id INTEGER NOT NULL REFERENCES cuentas_usuariopersonalizado(id) ON DELETE CASCADE,
                reserva_id INTEGER REFERENCES clientes_reserva(id) ON DELETE CASCADE,
                fecha_programada TIMESTAMP WITH TIME ZONE NOT NULL,
                fecha_envio TIMESTAMP WITH TIME ZONE,
                mensaje TEXT NOT NULL,
                fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                fecha_modificacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                intentos_envio INTEGER NOT NULL DEFAULT 0,
                max_intentos INTEGER NOT NULL DEFAULT 3,
                error_mensaje TEXT
            );
        """)
        
        # Crear índices
        print("📝 Creando índices...")
        cursor.execute("""
            CREATE INDEX fidelizacion_mensajes_estado_fecha 
            ON fidelizacion_mensajes(estado, fecha_programada);
        """)
        
        cursor.execute("""
            CREATE INDEX fidelizacion_mensajes_tipo_reserva 
            ON fidelizacion_mensajes(tipo, reserva_id);
        """)
        
        cursor.execute("""
            CREATE INDEX fidelizacion_mensajes_fecha_programada 
            ON fidelizacion_mensajes(fecha_programada);
        """)
        
        cursor.execute("""
            CREATE INDEX fidelizacion_mensajes_estado 
            ON fidelizacion_mensajes(estado);
        """)
        
        # Verificar que se creó
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
            
            # Verificar si la migración está marcada como aplicada
            cursor.execute("""
                SELECT COUNT(*) FROM django_migrations 
                WHERE app = 'fidelizacion' AND name = '0001_initial';
            """)
            migracion_aplicada = cursor.fetchone()[0] > 0
            
            if not migracion_aplicada:
                print("📝 Marcando migración como aplicada...")
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied) 
                    VALUES ('fidelizacion', '0001_initial', NOW());
                """)
                print("✅ Migración marcada como aplicada")
            
            return True
        else:
            print("❌ Error: No se pudo crear la tabla")
            return False

if __name__ == '__main__':
    try:
        crear_tabla_manualmente()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

