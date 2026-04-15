#!/bin/bash
# Script para crear la tabla de fidelización directamente en PostgreSQL
# Usa las mismas variables de entorno que el servicio systemd

set -e

cd /var/www/appo.com.co
source venv/bin/activate

# Cargar variables de entorno desde .env (solo las de PostgreSQL)
if [ -f .env ]; then
    # Cargar solo variables de PostgreSQL, evitando valores con caracteres especiales
    while IFS='=' read -r key value; do
        # Ignorar comentarios y líneas vacías
        [[ "$key" =~ ^#.*$ ]] && continue
        [[ -z "$key" ]] && continue
        
        # Solo exportar variables de PostgreSQL
        if [[ "$key" == "POSTGRES_DB" ]] || [[ "$key" == "POSTGRES_USER" ]] || [[ "$key" == "POSTGRES_PASSWORD" ]] || [[ "$key" == "POSTGRES_HOST" ]] || [[ "$key" == "POSTGRES_PORT" ]]; then
            # Limpiar espacios y comillas
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs | sed "s/^['\"]//;s/['\"]$//")
            export "$key=$value"
        fi
    done < <(grep -E '^POSTGRES_' .env)
    echo "✅ Variables de PostgreSQL cargadas desde .env"
else
    echo "❌ Error: Archivo .env no encontrado"
    exit 1
fi

# Verificar que las variables de PostgreSQL estén configuradas
if [ -z "$POSTGRES_DB" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ]; then
    echo "❌ Error: Variables de PostgreSQL no configuradas en .env"
    echo "   Necesitas: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD"
    exit 1
fi

echo "📊 Configuración de PostgreSQL:"
echo "   DB: $POSTGRES_DB"
echo "   USER: $POSTGRES_USER"
echo "   HOST: ${POSTGRES_HOST:-localhost}"
echo "   PORT: ${POSTGRES_PORT:-5432}"

# Exportar variables para que Django las use
export POSTGRES_DB
export POSTGRES_USER
export POSTGRES_PASSWORD
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5432}

# Ejecutar el script de Python con las variables cargadas
echo ""
echo "📝 Creando tabla fidelizacion_mensajes..."
python crear_tabla_fidelizacion.py

# Verificar que se creó correctamente
echo ""
echo "🔍 Verificando que la tabla existe..."
python manage.py shell << EOF
from django.conf import settings
from django.db import connection

db_engine = settings.DATABASES['default']['ENGINE']
print(f"Base de datos: {db_engine}")

if 'postgresql' in db_engine:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'fidelizacion_mensajes'
            );
        """)
        existe = cursor.fetchone()[0]
        if existe:
            print("✅ Tabla fidelizacion_mensajes existe")
        else:
            print("❌ Tabla fidelizacion_mensajes NO existe")
else:
    print("⚠️ No se está usando PostgreSQL")
EOF

echo ""
echo "✅ Proceso completado"

