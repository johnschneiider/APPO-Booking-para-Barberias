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

# 2. Verificar que PostgreSQL esté instalado y corriendo
print_status "🗄️ Verificando PostgreSQL..."
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL no está instalado. Instalando..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
    print_success "PostgreSQL instalado"
else
    print_success "PostgreSQL ya está instalado"
fi

# Verificar y iniciar PostgreSQL si no está corriendo
if ! systemctl is-active --quiet postgresql; then
    print_warning "PostgreSQL no está corriendo. Iniciando..."
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    sleep 3  # Esperar a que PostgreSQL inicie
    print_success "PostgreSQL iniciado"
else
    print_success "PostgreSQL ya está corriendo"
fi

# 3. Generar credenciales de PostgreSQL automáticamente
print_status "🗄️ Generando credenciales de PostgreSQL..."
# Generar password seguro de 32 caracteres
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
DB_NAME="appo_db"
DB_USER="appo_user"

print_status "Credenciales generadas:"
print_status "  Database: $DB_NAME"
print_status "  User: $DB_USER"
print_status "  Password: [GENERADO AUTOMÁTICAMENTE]"

# Crear usuario y base de datos
print_status "Creando usuario y base de datos en PostgreSQL..."
sudo -u postgres psql <<EOF
-- Eliminar usuario y base de datos si existen (para recrear desde cero)
DROP DATABASE IF EXISTS $DB_NAME;
DROP USER IF EXISTS $DB_USER;

-- Crear usuario con password seguro
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Crear base de datos
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;

-- Conectar a la base de datos y otorgar privilegios en el esquema público
\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;
EOF

print_success "Base de datos creada desde cero"

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

# 5. Instalar dependencias del sistema para OpenCV
print_status "📦 Instalando dependencias del sistema para OpenCV..."
sudo apt update
sudo apt install -y libgl1-mesa-glx libglib2.0-0 2>/dev/null || print_warning "No se pudieron instalar algunas dependencias de OpenCV"
print_success "Dependencias del sistema instaladas"

# 6. Instalar dependencias de Python
print_status "📦 Instalando dependencias de Python..."
if [ ! -d "venv" ]; then
    print_status "Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dependencias instaladas"

# 7. Configurar .env con credenciales generadas
print_status "⚙️ Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    if [ -f "env_vps_production.txt" ]; then
        cp env_vps_production.txt .env
        print_success "Archivo .env creado desde plantilla"
    else
        print_error "No se encontró env_vps_production.txt"
        exit 1
    fi
fi

# Generar SECRET_KEY si no está configurado
if grep -q "django-insecure-production-key-change-this-immediately" .env || ! grep -q "^SECRET_KEY=" .env; then
    print_status "Generando SECRET_KEY..."
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    if grep -q "^SECRET_KEY=" .env; then
        sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        echo "SECRET_KEY=$SECRET_KEY" >> .env
    fi
    print_success "SECRET_KEY generado"
fi

# Actualizar credenciales de PostgreSQL en .env
print_status "Actualizando credenciales de PostgreSQL en .env..."
sed -i "s/^POSTGRES_DB=.*/POSTGRES_DB=$DB_NAME/" .env
sed -i "s/^POSTGRES_USER=.*/POSTGRES_USER=$DB_USER/" .env
sed -i "s/^POSTGRES_PASSWORD=.*/POSTGRES_PASSWORD=$DB_PASSWORD/" .env
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME|" .env

# Configurar USING_DOCKER=no
if ! grep -q "^USING_DOCKER=" .env; then
    echo "USING_DOCKER=no" >> .env
else
    sed -i "s/^USING_DOCKER=.*/USING_DOCKER=no/" .env
fi

print_success "Variables de entorno configuradas"
print_warning "⚠️  IMPORTANTE: Edita .env para configurar EMAIL_HOST_USER, EMAIL_HOST_PASSWORD y credenciales de Twilio si las necesitas"

# 8. Cargar variables de entorno
print_status "📋 Cargando variables de entorno..."
# Cargar variables de entorno de forma segura (evitar errores de sintaxis)
set -a
export $(grep -v '^#' .env | grep -v '^$' | grep '=' | xargs -0 2>/dev/null || grep -v '^#' .env | grep -v '^$' | grep '=' | xargs)
set +a

# 9. Ejecutar migraciones
print_status "🗄️ Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput
print_success "Migraciones completadas"

# 10. Repoblar base de datos con datos de ejemplo
print_status "📊 Repoblando base de datos con datos de ejemplo..."
if python manage.py poblar_demo --help &>/dev/null; then
    python manage.py poblar_demo
    print_success "Base de datos repoblada con datos de ejemplo"
else
    print_warning "Comando poblar_demo no encontrado, saltando repoblación"
fi

# 11. Configurar sistema de recordatorios
print_status "🔔 Configurando sistema de recordatorios..."
if python manage.py setup_recordatorios --help &>/dev/null; then
    python manage.py setup_recordatorios --force --templates
    print_success "Sistema de recordatorios configurado"
else
    print_warning "Comando setup_recordatorios no encontrado, saltando configuración"
fi

# 12. Configurar planes de suscripción
print_status "💳 Configurando planes de suscripción..."
if python manage.py poblar_planes_suscripcion --help &>/dev/null; then
    python manage.py poblar_planes_suscripcion
    print_success "Planes de suscripción configurados"
else
    print_warning "Comando poblar_planes_suscripcion no encontrado, saltando configuración"
fi

# 13. Recopilar archivos estáticos
print_status "📁 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput
print_success "Archivos estáticos recopilados"

# 14. Configurar Nginx
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

# 15. Configurar SSL con Certbot
print_status "🔒 Configurando SSL..."
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    print_status "Obteniendo certificado SSL..."
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    print_success "Certificado SSL obtenido"
else
    print_success "Certificado SSL ya existe"
fi

# 16. Verificar configuración de Nginx
print_status "🔍 Verificando configuración de Nginx..."
if sudo nginx -t; then
    print_success "Configuración de Nginx válida"
    sudo systemctl reload nginx
    print_success "Nginx recargado"
else
    print_error "Error en la configuración de Nginx"
    exit 1
fi

# 17. Crear servicio systemd para Gunicorn (opcional pero recomendado)
print_status "🔧 Configurando servicio systemd para Gunicorn..."
# Leer variables de PostgreSQL del .env
POSTGRES_DB_VAL=$(grep "^POSTGRES_DB=" .env | cut -d'=' -f2)
POSTGRES_USER_VAL=$(grep "^POSTGRES_USER=" .env | cut -d'=' -f2)
POSTGRES_PASSWORD_VAL=$(grep "^POSTGRES_PASSWORD=" .env | cut -d'=' -f2)
USING_DOCKER_VAL=$(grep "^USING_DOCKER=" .env | cut -d'=' -f2 || echo "no")
DEBUG_VAL=$(grep "^DEBUG=" .env | cut -d'=' -f2 || echo "False")
SECRET_KEY_VAL=$(grep "^SECRET_KEY=" .env | cut -d'=' -f2)

sudo tee /etc/systemd/system/appo.service > /dev/null <<EOF
[Unit]
Description=APPO Gunicorn daemon
After=network.target postgresql.service

[Service]
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
Environment="POSTGRES_DB=$POSTGRES_DB_VAL"
Environment="POSTGRES_USER=$POSTGRES_USER_VAL"
Environment="POSTGRES_PASSWORD=$POSTGRES_PASSWORD_VAL"
Environment="POSTGRES_HOST=localhost"
Environment="POSTGRES_PORT=5432"
Environment="USING_DOCKER=$USING_DOCKER_VAL"
Environment="DEBUG=$DEBUG_VAL"
Environment="SECRET_KEY=$SECRET_KEY_VAL"
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

# 18. Verificación final
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
print_status ""
print_status "═══════════════════════════════════════════════════════════"
print_status "📋 INFORMACIÓN IMPORTANTE"
print_status "═══════════════════════════════════════════════════════════"
print_status ""
print_status "🌐 URL: https://$DOMAIN"
print_status ""
print_status "👤 Usuario Superadmin:"
print_status "   Username: superadmin"
print_status "   Password: Malware01"
print_status "   Email: super@demo.com"
print_status ""
print_status "🗄️ Base de datos PostgreSQL:"
print_status "   Database: $DB_NAME"
print_status "   User: $DB_USER"
print_status "   Password: [Guardada en .env]"
print_status ""
print_status "📝 Credenciales guardadas en: $PROJECT_DIR/.env"
print_status ""
print_status "═══════════════════════════════════════════════════════════"
print_status "🔧 COMANDOS ÚTILES"
print_status "═══════════════════════════════════════════════════════════"
print_status "📊 Ver estado: sudo systemctl status appo"
print_status "📝 Ver logs: sudo journalctl -u appo -f"
print_status "🔄 Reiniciar: sudo systemctl restart appo"
print_status "🗄️ Acceder a DB: psql -U $DB_USER -d $DB_NAME"
print_status ""
print_status "⚠️  RECUERDA: Edita .env para configurar EMAIL y TWILIO si los necesitas"
print_status ""

