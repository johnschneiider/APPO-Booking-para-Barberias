#!/bin/bash
# Script para resolver el problema de fidelización en VPS

set -e

cd /var/www/appo.com.co
source venv/bin/activate

echo "🔄 Resolviendo problema de fidelización..."

# 1. Resolver conflicto de git
echo "📥 Actualizando código..."
git stash
git pull origin main
git stash pop || true

# 2. Verificar que la tabla existe
echo "🔍 Verificando tabla..."
PGPASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2 | xargs) \
psql -h localhost -U $(grep "^POSTGRES_USER=" .env | cut -d'=' -f2 | xargs) \
-d $(grep "^POSTGRES_DB=" .env | cut -d'=' -f2 | xargs) \
-c "SELECT COUNT(*) FROM fidelizacion_mensajes;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Tabla fidelizacion_mensajes existe"
else
    echo "❌ Tabla no existe, creándola..."
    # Crear tabla directamente
    PGPASSWORD=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2 | xargs) \
    psql -h localhost -U $(grep "^POSTGRES_USER=" .env | cut -d'=' -f2 | xargs) \
    -d $(grep "^POSTGRES_DB=" .env | cut -d'=' -f2 | xargs) << 'SQL'
CREATE TABLE IF NOT EXISTS fidelizacion_mensajes (
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

CREATE INDEX IF NOT EXISTS fidelizacion_mensajes_estado_fecha ON fidelizacion_mensajes(estado, fecha_programada);
CREATE INDEX IF NOT EXISTS fidelizacion_mensajes_tipo_reserva ON fidelizacion_mensajes(tipo, reserva_id);
CREATE INDEX IF NOT EXISTS fidelizacion_mensajes_fecha_programada ON fidelizacion_mensajes(fecha_programada);
CREATE INDEX IF NOT EXISTS fidelizacion_mensajes_estado ON fidelizacion_mensajes(estado);

INSERT INTO django_migrations (app, name, applied) 
VALUES ('fidelizacion', '0001_initial', NOW())
ON CONFLICT DO NOTHING;
SQL
    echo "✅ Tabla creada"
fi

# 3. Recargar y reiniciar servicio completamente
echo "🔄 Reiniciando servicio..."
sudo systemctl daemon-reload
sudo systemctl stop appo
sleep 3
sudo systemctl start appo

# 4. Esperar a que se inicie
echo "⏳ Esperando a que el servicio se inicie..."
sleep 10

# 5. Verificar estado
echo "📊 Estado del servicio:"
sudo systemctl status appo --no-pager -l | head -20

echo ""
echo "✅ Proceso completado"
echo ""
echo "📋 Para ver logs en tiempo real:"
echo "   sudo journalctl -u appo -f | grep -i fidelizacion"

