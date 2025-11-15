#!/bin/bash
# Script para crear superusuario de Django en producción

set -e

echo "🔐 Creando superusuario para APPO..."

cd /var/www/appo.com.co
source venv/bin/activate

# Cargar variables de entorno
export $(grep -v '^#' .env | grep -v '^$' | grep '=' | xargs)

# Crear superusuario
python manage.py createsuperuser

echo "✅ Superusuario creado exitosamente"
echo ""
echo "📋 Puedes acceder al admin en: https://appo.com.co/admin/"

