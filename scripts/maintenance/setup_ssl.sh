#!/bin/bash
set -e

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

echo "🔒 Configurando SSL..."

# Verificar que los certificados existen
if [ ! -f "/etc/letsencrypt/live/appo.com.co/fullchain.pem" ]; then
    print_error "No se encontraron los certificados SSL. Ejecuta primero el deploy.sh"
    exit 1
fi

# Crear configuración SSL
print_status "Creando configuración SSL..."

cat > nginx/ssl_production.conf << 'EOF'
# Configuración SSL para producción
server {
    listen 80;
    server_name appo.com.co www.appo.com.co;

    # Ruta especial para el desafío de Let's Encrypt
    location ^~ /.well-known/acme-challenge/ {
        root /var/www/certbot;
        default_type "text/plain";
        try_files $uri =404;
    }

    # Redirección de todo lo demás a HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# Configuración HTTPS
server {
    listen 443 ssl http2;
    server_name appo.com.co www.appo.com.co;

    # Certificados SSL
    ssl_certificate /etc/letsencrypt/live/appo.com.co/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/appo.com.co/privkey.pem;

    # Configuración SSL moderna
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Aumentar tamaño máximo del cuerpo
    client_max_body_size 20M;

    # Archivos estáticos
    location /static/ {
        alias /app/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy hacia la aplicación Django
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    error_page 404 /404.html;
        location = /40x.html {}

    error_page 500 502 503 504 /50x.html;
        location = /50x.html {}
}
EOF

# Actualizar docker-compose para usar la nueva configuración SSL
print_status "Actualizando docker-compose.yml..."

# Crear backup del docker-compose original
cp docker-compose.yml docker-compose.yml.backup

# Actualizar docker-compose para incluir el nuevo archivo SSL
sed -i 's|./nginx/ssl.conf:/etc/nginx/ssl.conf:ro|./nginx/ssl_production.conf:/etc/nginx/ssl.conf:ro|' docker-compose.yml

print_success "Configuración SSL creada correctamente"

# Reiniciar nginx
print_status "Reiniciando Nginx con SSL..."
docker compose restart nginx

print_success "✅ SSL configurado correctamente!"
print_status "Tu sitio ahora está disponible en: https://appo.com.co"
