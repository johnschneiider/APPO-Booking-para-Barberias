#!/bin/bash
set -e

# Script de despliegue para VPS sin Docker
# =========================================
# Este script configura APPO en una VPS con Nginx compartido

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() { echo -e "${BLUE}📋 $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Variables
PROJECT_DIR="/var/www/appo.com.co"
NGINX_SITE="appo.com.co"
DOMAIN="appo.com.co"

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    print_error "No se encontró manage.py. Asegúrate de estar en el directorio del proyecto."
    exit 1
fi

print_status "🚀 Iniciando despliegue de APPO en VPS..."

# 1. Crear directorios necesarios
print_status "📁 Creando directorios..."
sudo mkdir -p $PROJECT_DIR/{staticfiles,media,logs}
sudo chown -R $USER:$USER $PROJECT_DIR
mkdir -p logs/{nginx,postgresql,redis,django}
print_success "Directorios creados"

# 2. Verificar que PostgreSQL esté instalado
print_status "🗄️ Verificando PostgreSQL..."
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL no está instalado. Instalando..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
    print_success "PostgreSQL instalado"
else
    print_success "PostgreSQL ya está instalado"
fi

# 3. Crear base de datos PostgreSQL (si no existe)
print_status "🗄️ Configurando base de datos..."
if [ -f ".env" ]; then
    source .env
    DB_NAME=${POSTGRES_DB:-appo_db}
    DB_USER=${POSTGRES_USER:-appo_user}
    DB_PASSWORD=${POSTGRES_PASSWORD:-appo_pass}
else
    print_warning "No se encontró .env. Usando valores por defecto."
    DB_NAME="appo_db"
    DB_USER="appo_user"
    DB_PASSWORD="appo_pass"
fi

# Crear usuario y base de datos
sudo -u postgres psql <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
    END IF;
END
\$\$;

SELECT 'CREATE DATABASE $DB_NAME OWNER $DB_USER'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

print_success "Base de datos configurada"

# 4. Verificar que Redis esté instalado
print_status "🔴 Verificando Redis..."
if ! command -v redis-cli &> /dev/null; then
    print_warning "Redis no está instalado. Instalando..."
    sudo apt install -y redis-server
    sudo systemctl enable redis-server
    sudo systemctl start redis-server
    print_success "Redis instalado y corriendo"
else
    if systemctl is-active --quiet redis-server; then
        print_success "Redis ya está corriendo"
    else
        print_warning "Redis instalado pero no corriendo. Iniciando..."
        sudo systemctl start redis-server
        print_success "Redis iniciado"
    fi
fi

# 5. Instalar dependencias de Python
print_status "📦 Instalando dependencias de Python..."
if [ ! -d "venv" ]; then
    print_status "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dependencias instaladas"

# 6. Configurar .env si no existe
print_status "⚙️ Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    if [ -f "env_vps_production.txt" ]; then
        cp env_vps_production.txt .env
        print_warning "Archivo .env creado desde plantilla. ¡IMPORTANTE: Edita .env con tus valores reales!"
        print_warning "Especialmente: SECRET_KEY, POSTGRES_PASSWORD, y credenciales de email/Twilio"
        read -p "¿Ya editaste el archivo .env? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Debes editar el archivo .env antes de continuar"
            exit 1
        fi
    else
        print_error "No se encontró env_vps_production.txt"
        exit 1
    fi
fi

# Generar SECRET_KEY si no está configurado
if grep -q "django-insecure-production-key-change-this-immediately" .env; then
    print_status "Generando SECRET_KEY..."
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    print_success "SECRET_KEY generado"
fi

# 7. Ejecutar migraciones
print_status "🗄️ Ejecutando migraciones..."
source .env
export $(cat .env | grep -v '^#' | xargs)
python manage.py migrate
print_success "Migraciones completadas"

# 8. Recopilar archivos estáticos
print_status "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput
print_success "Archivos estáticos recopilados"

# 9. Configurar Nginx
print_status "🌐 Configurando Nginx..."
if [ -f "nginx-appo.conf" ]; then
    sudo cp nginx-appo.conf /etc/nginx/sites-available/$NGINX_SITE
    if [ ! -L "/etc/nginx/sites-enabled/$NGINX_SITE" ]; then
        sudo ln -s /etc/nginx/sites-available/$NGINX_SITE /etc/nginx/sites-enabled/
    fi
    print_success "Configuración de Nginx copiada"
else
    print_error "No se encontró nginx-appo.conf"
    exit 1
fi

# 10. Configurar SSL con Certbot
print_status "🔒 Configurando SSL..."
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    print_status "Obteniendo certificado SSL..."
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    print_success "Certificado SSL obtenido"
else
    print_success "Certificado SSL ya existe"
fi

# 11. Verificar configuración de Nginx
print_status "🔍 Verificando configuración de Nginx..."
if sudo nginx -t; then
    print_success "Configuración de Nginx válida"
    sudo systemctl reload nginx
    print_success "Nginx recargado"
else
    print_error "Error en la configuración de Nginx"
    exit 1
fi

# 12. Crear servicio systemd para Gunicorn (opcional pero recomendado)
print_status "🔧 Configurando servicio systemd para Gunicorn..."
sudo tee /etc/systemd/system/appo.service > /dev/null <<EOF
[Unit]
Description=APPO Gunicorn daemon
After=network.target

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn \\
    --workers 3 \\
    --timeout 120 \\
    --bind 127.0.0.1:8000 \\
    --access-logfile $PROJECT_DIR/logs/gunicorn-access.log \\
    --error-logfile $PROJECT_DIR/logs/gunicorn-error.log \\
    melissa.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable appo
sudo systemctl restart appo
print_success "Servicio systemd configurado y iniciado"

# 13. Verificación final
print_status "🔍 Verificación final..."
sleep 2

# Verificar que Gunicorn esté corriendo
if systemctl is-active --quiet appo; then
    print_success "Gunicorn está corriendo"
else
    print_error "Gunicorn no está corriendo. Revisa los logs: sudo journalctl -u appo -n 50"
fi

# Verificar que Nginx esté corriendo
if systemctl is-active --quiet nginx; then
    print_success "Nginx está corriendo"
else
    print_error "Nginx no está corriendo"
fi

# Verificar que Redis esté corriendo
if systemctl is-active --quiet redis-server; then
    print_success "Redis está corriendo"
else
    print_error "Redis no está corriendo"
fi

print_success "🎉 Despliegue completado exitosamente!"
print_status "🌐 Accede a tu aplicación en: https://$DOMAIN"
print_status "📊 Verifica el estado con: sudo systemctl status appo"
print_status "📝 Ver logs con: sudo journalctl -u appo -f"
print_status "🔄 Reiniciar servicio: sudo systemctl restart appo"

