#!/bin/bash
# Script para actualizar la app fidelizacion en la VPS

set -e

echo "🔄 Actualizando sistema de fidelización..."

cd /var/www/appo.com.co

# 1. Activar entorno virtual
source venv/bin/activate

# 2. Actualizar código desde GitHub
echo "📥 Descargando cambios desde GitHub..."
git pull origin main

# 3. Crear migraciones
echo "📝 Creando migraciones..."
python manage.py makemigrations fidelizacion

# 4. Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
python manage.py migrate fidelizacion

# 5. Reiniciar servicio para que el loop se inicie
echo "🔄 Reiniciando servicio appo..."
sudo systemctl restart appo

# 6. Esperar un momento
sleep 3

# 7. Verificar estado del servicio
echo "✅ Verificando estado del servicio..."
sudo systemctl status appo --no-pager -l

echo ""
echo "✅ Actualización completada!"
echo ""
echo "📋 Para verificar que el loop está corriendo, ejecuta:"
echo "   sudo journalctl -u appo -f | grep -i fidelizacion"
echo ""
echo "📋 Para ver los mensajes en el admin:"
echo "   https://appo.com.co/admin/fidelizacion/mensajefidelizacion/"

