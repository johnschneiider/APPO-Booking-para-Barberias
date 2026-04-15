#!/bin/bash
# Script para verificar que el sistema de fidelización está funcionando

cd /var/www/appo.com.co
source venv/bin/activate

echo "🔍 Verificando sistema de fidelización..."
echo ""

# 1. Verificar que la tabla existe
echo "📊 Verificando tabla en PostgreSQL..."
PGPASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2 | xargs) \
psql -h localhost -U $(grep "^POSTGRES_USER=" .env | cut -d'=' -f2 | xargs) \
-d $(grep "^POSTGRES_DB=" .env | cut -d'=' -f2 | xargs) \
-c "SELECT COUNT(*) as total_mensajes FROM fidelizacion_mensajes;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Tabla fidelizacion_mensajes existe y es accesible"
else
    echo "❌ Error accediendo a la tabla"
fi

# 2. Verificar logs recientes
echo ""
echo "📋 Logs recientes de fidelización (últimos 2 minutos):"
sudo journalctl -u appo --since "2 minutes ago" | grep -i fidelizacion | tail -10

# 3. Verificar si hay errores
echo ""
echo "🔍 Buscando errores de fidelización..."
ERRORES=$(sudo journalctl -u appo --since "5 minutes ago" | grep -i "fidelizacion.*error\|fidelizacion.*does not exist" | wc -l)

if [ "$ERRORES" -eq 0 ]; then
    echo "✅ No hay errores de fidelización en los últimos 5 minutos"
else
    echo "⚠️ Se encontraron $ERRORES errores. Revisa los logs:"
    sudo journalctl -u appo --since "5 minutes ago" | grep -i "fidelizacion.*error\|fidelizacion.*does not exist"
fi

# 4. Verificar que el loop está corriendo
echo ""
echo "🔍 Verificando que el loop está activo..."
LOOP_ACTIVO=$(sudo journalctl -u appo --since "5 minutes ago" | grep -i "loop.*mensajes.*iniciado\|loop de procesamiento" | wc -l)

if [ "$LOOP_ACTIVO" -gt 0 ]; then
    echo "✅ Loop de mensajes está activo"
else
    echo "⚠️ No se encontró mensaje de inicio del loop en los últimos 5 minutos"
fi

# 5. Verificar estado del servicio
echo ""
echo "📊 Estado del servicio appo:"
if sudo systemctl is-active appo > /dev/null 2>&1; then
    echo "✅ Servicio activo"
    # Ver detalles del servicio
    echo ""
    echo "📋 Detalles del servicio:"
    sudo systemctl status appo --no-pager -l | head -15
else
    echo "❌ Servicio inactivo"
    echo ""
    echo "⚠️ Intentando iniciar el servicio..."
    sudo systemctl start appo
    sleep 3
    if sudo systemctl is-active appo > /dev/null 2>&1; then
        echo "✅ Servicio iniciado correctamente"
    else
        echo "❌ Error al iniciar el servicio. Revisa los logs:"
        sudo journalctl -u appo -n 20 --no-pager
    fi
fi

echo ""
echo "✅ Verificación completada"

