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

# Función para detectar y resolver conflictos de puertos
resolve_port_conflicts() {
    print_status "🔍 Detectando conflictos de puertos..."
    
    # Verificar si Nginx del sistema está corriendo
    if systemctl is-active --quiet nginx 2>/dev/null; then
        print_warning "Nginx del sistema está activo y puede causar conflictos"
        print_status "Deteniendo y deshabilitando Nginx del sistema..."
        sudo systemctl stop nginx 2>/dev/null || true
        sudo systemctl disable nginx 2>/dev/null || true
        print_success "Nginx del sistema detenido y deshabilitado"
    fi
    
    # Verificar puerto 80
    if lsof -i:80 2>/dev/null | grep -v docker | grep -q LISTEN; then
        print_warning "Puerto 80 ocupado por proceso no-Docker"
        print_status "Deteniendo procesos en puerto 80..."
        sudo fuser -k 80/tcp 2>/dev/null || true
        sleep 2
        print_success "Puerto 80 liberado"
    fi
    
    # Verificar puerto 443
    if lsof -i:443 2>/dev/null | grep -v docker | grep -q LISTEN; then
        print_warning "Puerto 443 ocupado por proceso no-Docker"
        print_status "Deteniendo procesos en puerto 443..."
        sudo fuser -k 443/tcp 2>/dev/null || true
        sleep 2
        print_success "Puerto 443 liberado"
    fi
    
    print_success "Puertos verificados"
}

# Función para instalar dependencias del sistema
install_dependencies() {
    print_status "📦 Instalando dependencias del sistema..."
    sudo apt update
    sudo apt install -y curl lsof python3 python3-pip dnsutils
    print_success "Dependencias instaladas"
}

# Función para crear directorios necesarios
setup_directories() {
    print_status "📁 Creando directorios necesarios..."
    mkdir -p logs/{nginx,postgresql,redis,django}
    mkdir -p staticfiles
    mkdir -p media
    mkdir -p certbot/www/.well-known/acme-challenge
    print_success "Directorios creados"
}

# Función para configurar .env
setup_env() {
    if [ ! -f ".env" ]; then
        print_warning "Archivo .env no encontrado. Creando desde plantilla..."
        if [ -f "env_production.txt" ]; then
            cp env_production.txt .env
            # Generar secret key
            SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
            echo "SECRET_KEY=$SECRET_KEY" >> .env
            print_warning "Archivo .env creado. Edita manualmente antes de continuar."
            read -p "¿Ya editaste el archivo .env? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_error "Debes editar el archivo .env antes de continuar"
                exit 1
            fi
        else
            print_error "No se encontró env_production.txt"
            exit 1
        fi
    fi
}

# Función para verificar que el dominio apunte al servidor
verify_domain() {
    print_status "Verificando que el dominio apunte a este servidor..."
    IP_LOCAL=$(curl -4 -s ifconfig.me)
    IP_DOMINIO=$(dig +short appo.com.co | tail -n1)

    if [[ "$IP_LOCAL" != "$IP_DOMINIO" ]]; then
        print_error "El dominio appo.com.co no apunta a este servidor."
        echo "➡️ IP actual: $IP_LOCAL | IP del dominio: $IP_DOMINIO"
        exit 1
    fi

    print_success "El dominio apunta correctamente."
}

# Función para configurar SSL PRIMERO
setup_ssl() {
    print_status "🔒 Configurando SSL con Let's Encrypt..."
    
    # Instalar certbot si no está instalado
    if ! command -v certbot &> /dev/null; then
        print_status "Instalando certbot..."
        sudo apt install -y certbot
    fi
    
    # Verificar si ya existen certificados
    if [ -f "/etc/letsencrypt/live/appo.com.co/fullchain.pem" ]; then
        print_success "Certificados SSL ya existen"
        return 0
    fi
    
    # Obtener certificado
    print_status "Obteniendo certificado SSL..."
    sudo certbot certonly --webroot -w ./certbot/www -d appo.com.co -d www.appo.com.co --non-interactive --agree-tos --email admin@appo.com.co
    
    if [ -f "/etc/letsencrypt/live/appo.com.co/fullchain.pem" ]; then
        print_success "Certificado SSL obtenido correctamente"
        return 0
    else
        print_warning "No se pudieron obtener los certificados SSL"
        return 1
    fi
}

# Función para crear configuración de Nginx CON SSL
create_nginx_config() {
    print_status "🔧 Creando configuración de Nginx con SSL..."
    
    mkdir -p nginx
    
    # Verificar si existen certificados SSL
    if [ -f "/etc/letsencrypt/live/appo.com.co/fullchain.pem" ]; then
        print_status "Creando configuración de Nginx CON SSL..."
        cat > nginx/nginx.conf << 'EOF'
user  nginx;
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    keepalive_timeout  65;

    # Compresión gzip
    gzip on;
    gzip_disable "msie6";
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Configuración del servidor HTTP (redirige a HTTPS)
    server {
        listen 80;
        server_name appo.com.co www.appo.com.co localhost 127.0.0.1 _;

        # Ruta especial para el desafío de Let's Encrypt
        location ^~ /.well-known/acme-challenge/ {
            root /var/www/certbot;
            default_type "text/plain";
            try_files $uri =404;
        }

        # Redirigir todo a HTTPS excepto el desafío de Let's Encrypt
        location / {
            return 301 https://$host$request_uri;
        }
    }

    # Configuración del servidor HTTPS
    server {
        listen 443 ssl http2;
        server_name appo.com.co www.appo.com.co;

        # Configuración SSL
        ssl_certificate /etc/letsencrypt/live/appo.com.co/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/appo.com.co/privkey.pem;
        
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

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

        # Health check
        location /health/ {
            proxy_pass http://web:8000/health/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Proxy hacia la aplicación Django
        location / {
            proxy_pass http://web:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Aumentar tamaño máximo del cuerpo
        client_max_body_size 20M;

        error_page 404 /404.html;
            location = /40x.html {}

        error_page 500 502 503 504 /50x.html;
            location = /50x.html {}
    }
}
EOF
    else
        print_warning "No hay certificados SSL, creando configuración HTTP básica..."
        cat > nginx/nginx.conf << 'EOF'
user  nginx;
worker_processes  1;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    keepalive_timeout  65;

    server {
        listen 80;
        server_name appo.com.co www.appo.com.co localhost 127.0.0.1 _;

        # Ruta especial para el desafío de Let's Encrypt
        location ^~ /.well-known/acme-challenge/ {
            root /var/www/certbot;
            default_type "text/plain";
            try_files $uri =404;
        }

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

        # Health check
        location /health/ {
            proxy_pass http://web:8000/health/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Proxy hacia la aplicación Django
        location / {
            proxy_pass http://web:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        client_max_body_size 20M;
    }
}
EOF
    fi
    
    print_success "Configuración de Nginx creada"
}

# Función para restaurar docker-compose.yml
restore_docker_compose() {
    print_status "🔧 Restaurando docker-compose.yml..."
    
    cat > docker-compose.yml << 'EOF'
services:
  web:
    build: .
    command: gunicorn melissa.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
    environment:
      - SECRET_KEY=${SECRET_KEY:-django-insecure-production-key-change-this-immediately}
      - DEBUG=${DEBUG:-False}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-appo.com.co,www.appo.com.co,92.113.39.100}
      - USING_DOCKER=yes
      - POSTGRES_DB=${POSTGRES_DB:-vitalmix}
      - POSTGRES_USER=${POSTGRES_USER:-vitaluser}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-vitalpass}
      - REDIS_URL=${REDIS_URL:-redis://redis:6379/0}
      - DATABASE_URL=${DATABASE_URL:-postgresql://vitaluser:vitalpass@db:5432/vitalmix}
    expose:
      - "8000"
    volumes:
      - .:/app
      - ./media:/app/media
      - ./logs:/app/logs
      - ./staticfiles:/app/staticfiles
    depends_on:
      - redis
      - db
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-vitalmix}
      POSTGRES_USER: ${POSTGRES_USER:-vitaluser}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-vitalpass}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./logs/postgresql:/var/log/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-vitaluser} -d ${POSTGRES_DB:-vitalmix}"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7
    restart: always
    volumes:
      - redis_data:/data
      - ./logs/redis:/var/log/redis
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:1.25
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - web
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis_data:
  pgdata:
EOF
    
    print_success "docker-compose.yml restaurado"
}

# Función principal
main() {
    print_status "🚀 Iniciando despliegue de APPO..."
    
    # 1. Resolver conflictos de puertos
    resolve_port_conflicts
    
    # 2. Instalar dependencias
    install_dependencies
    
    # 3. Crear directorios
    setup_directories
    
    # 4. Configurar .env
    setup_env
    
    # 5. Verificar dominio
    verify_domain
    
    # 6. Configurar SSL PRIMERO
    setup_ssl
    
    # 7. Crear configuración de Nginx (con o sin SSL según corresponda)
    create_nginx_config
    
    # 8. Restaurar docker-compose.yml
    restore_docker_compose
    
    # 9. Detener contenedores existentes
    print_status "🛑 Deteniendo contenedores existentes..."
    docker compose down 2>/dev/null || true
    
    # 10. Limpiar imágenes
    print_status "🧹 Limpiando imágenes no utilizadas..."
    docker system prune -f
    
    # 11. Construir y levantar servicios
    print_status "🔨 Construyendo y levantando servicios..."
    docker compose up -d --build
    
    # 12. Esperar a que estén listos
    print_status "⏳ Esperando a que los servicios estén listos..."
    sleep 15
    
    # 13. Ejecutar migraciones
    print_status "🗄️ Ejecutando migraciones..."
    docker compose exec web python manage.py migrate
    
    # 14. Recopilar archivos estáticos
    print_status "📁 Recopilando archivos estáticos..."
    docker compose exec web python manage.py collectstatic --noinput
    
    # 15. Verificación final
    print_status "🔍 Verificación final..."
    docker compose ps
    
    print_success "🎉 Despliegue completado exitosamente!"
    print_status "🌐 Accede a tu aplicación en: https://appo.com.co"
    print_status "📊 Verifica el estado con: docker compose ps"
    print_status "📝 Ver logs con: docker compose logs -f"
}

# Ejecutar función principal
main "$@"
