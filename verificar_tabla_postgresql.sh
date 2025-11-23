#!/bin/bash
# Script para verificar que la tabla existe en PostgreSQL

cd /var/www/appo.com.co
source venv/bin/activate

# Cargar solo variables de PostgreSQL
while IFS='=' read -r key value; do
    [[ "$key" =~ ^#.*$ ]] && continue
    [[ -z "$key" ]] && continue
    if [[ "$key" == "POSTGRES_DB" ]] || [[ "$key" == "POSTGRES_USER" ]] || [[ "$key" == "POSTGRES_PASSWORD" ]] || [[ "$key" == "POSTGRES_HOST" ]] || [[ "$key" == "POSTGRES_PORT" ]]; then
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs | sed "s/^['\"]//;s/['\"]$//")
        export "$key=$value"
    fi
done < <(grep -E '^POSTGRES_' .env)

echo "🔍 Verificando tabla fidelizacion_mensajes en PostgreSQL..."
echo "   Base de datos: $POSTGRES_DB"
echo "   Usuario: $POSTGRES_USER"
echo ""

# Verificar que la tabla existe
PGPASSWORD=$POSTGRES_PASSWORD psql -h ${POSTGRES_HOST:-localhost} -U $POSTGRES_USER -d $POSTGRES_DB -c "\d fidelizacion_mensajes" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ La tabla fidelizacion_mensajes existe en PostgreSQL"
    
    # Contar registros
    COUNT=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h ${POSTGRES_HOST:-localhost} -U $POSTGRES_USER -d $POSTGRES_DB -t -c "SELECT COUNT(*) FROM fidelizacion_mensajes;" 2>/dev/null | xargs)
    echo "   Registros en la tabla: $COUNT"
else
    echo ""
    echo "❌ La tabla fidelizacion_mensajes NO existe en PostgreSQL"
fi

