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
    if systemctl is-active --quiet nginx; then
        print_warning "Nginx del sistema está activo y puede causar conflictos"
        print_status "Deteniendo y deshabilitando Nginx del sistema..."
        sudo systemctl stop nginx 2>/dev/null || true
        sudo systemctl disable nginx 2>/dev/null || true
        print_success "Nginx del sistema detenido y deshabilitado"
    fi
    
    # Verificar puerto 80
    if lsof -i:80 | grep -v docker | grep -q LISTEN; then
        print_warning "Puerto 80 ocupado por proceso no-Docker"
        print_status "Deteniendo procesos en puerto 80..."
        sudo fuser -k 80/tcp 2>/dev/null || true
        sleep 2
        print_success "Puerto 80 liberado"
    fi
    
    # Verificar puerto 443
    if lsof -i:443 | grep -v docker | grep -q LISTEN; then
        print_warning "Puerto 443 ocupado por proceso no-Docker"
        print_status "Deteniendo procesos en puerto 443..."
        sudo fuser -k 443/tcp 2>/dev/null || true
        sleep 2
        print_success "Puerto 443 liberado"
    fi
    
    # Verificar que solo Docker use los puertos
    if lsof -i:80 | grep -q docker && lsof -i:443 | grep -q docker; then
        print_success "Puertos 80 y 443 están disponibles para Docker"
    else
        print_warning "Algunos puertos aún pueden estar ocupados"
    fi
}

# Función para crear directorios de logs
setup_logs() {
    print_status "📁 Configurando directorios de logs..."
    mkdir -p logs/{nginx,postgresql,redis,django}
    mkdir -p staticfiles
    mkdir -p media
    print_success "Directorios de logs creados"
}

# Función para generar secret key segura
generate_secret_key() {
    print_status "🔐 Generando secret key segura..."
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    echo "SECRET_KEY=$SECRET_KEY" >> .env
    print_success "Secret key generada y agregada al .env"
}

# Función para diagnóstico completo
diagnose_nginx() {
    print_status "🔍 Realizando diagnóstico completo de Nginx..."
    
    # 1. Verificar archivo de prueba
    print_status "Verificando archivo de prueba..."
    mkdir -p ./certbot/www/.well-known/acme-challenge
    
    if [ -d "./certbot/www/.well-known/acme-challenge" ]; then
        print_success "Directorio certbot creado correctamente"
    else
        print_error "No se pudo crear el directorio certbot"
        return 1
    fi
    
    # 2. Verificar contenedor
    print_status "Verificando contenedor Nginx..."
    if docker compose ps nginx | grep -q "Up"; then
        print_success "Contenedor Nginx está corriendo"
    else
        print_warning "Contenedor Nginx no está corriendo, levantando..."
        docker compose up -d nginx
        sleep 3
    fi
    
    # 3. Verificar y corregir archivo test.txt
    if ! verify_and_fix_test_file; then
        print_error "No se pudo verificar/corregir el archivo test.txt"
        return 1
    fi
    
    # 4. Verificar configuración de Nginx
    print_status "Verificando configuración de Nginx..."
    if docker compose exec nginx nginx -t 2>/dev/null; then
        print_success "Configuración de Nginx es válida"
    else
        print_error "Configuración de Nginx NO es válida"
        docker compose exec nginx nginx -t
        return 1
    fi
    
    return 0
}

# Función para corregir mapeo de volúmenes
fix_volume_mapping() {
    print_status "🔧 Corrigiendo mapeo de volúmenes..."
    
    # 1. Crear archivo de prueba
    mkdir -p ./certbot/www/.well-known/acme-challenge
    
    # 2. Verificar configuración de volúmenes
    print_status "Verificando configuración de volúmenes..."
    if grep -q "./certbot/www:/var/www/certbot" docker-compose.yml; then
        print_success "Volumen configurado correctamente en docker-compose.yml"
    else
        print_error "Volumen NO está configurado correctamente"
        print_status "Agregando volumen al docker-compose.yml..."
        sed -i '/nginx:/,/restart: always/ { /volumes:/,/restart: always/ { /- \.\/certbot\/www:\/var\/www\/certbot/! s/restart: always/      - .\/certbot\/www:\/var\/www\/certbot\n    restart: always/ } }' docker-compose.yml
    fi
    
    # 3. Crear configuración mínima
    print_status "Creando configuración mínima..."
    cat > nginx/ssl_minimal.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
        try_files $uri =404;
    }

    location / {
        return 200 "OK";
    }
}
EOF
    
    # 4. Usar configuración mínima
    print_status "Usando configuración mínima..."
    cp nginx/ssl_minimal.conf nginx/ssl.conf
    
    # 5. Levantar nginx
    print_status "Levantando Nginx..."
    docker compose up -d nginx
    
    # 6. Esperar
    print_status "Esperando a que Nginx esté listo..."
    sleep 5
    
    # 7. Verificar y corregir archivo test.txt
    if ! verify_and_fix_test_file; then
        print_error "No se pudo verificar/corregir el archivo test.txt"
        return 1
    fi
    
    # 8. Probar acceso
    print_status "Probando acceso a .well-known..."
    for i in {1..10}; do
        CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt | tr -d '\r\n' || true)
        if [[ "$CHALLENGE" == "test-appo" ]]; then
            print_success "✅ Nginx funciona correctamente con mapeo de volúmenes corregido"
            return 0
        fi
        if [[ $i -eq 10 ]]; then
            print_error "❌ Nginx no funciona después de corregir volúmenes"
            print_status "Logs de Nginx:"
            docker compose logs nginx
            return 1
        fi
        sleep 1
    done
}

# Función para verificar y corregir Nginx con configuración simplificada
verify_and_fix_nginx() {
    print_status "🔧 Verificando y corrigiendo configuración de Nginx..."
    
    # 1. Detener contenedores existentes
    print_status "Deteniendo contenedores existentes..."
    docker compose down
    
    # 2. Limpiar imágenes no utilizadas
    print_status "Limpiando imágenes no utilizadas..."
    docker image prune -f
    
    # 3. Verificar puerto 80
    print_status "Verificando puerto 80..."
    if lsof -i:80 | grep -q LISTEN; then
        print_warning "Puerto 80 ocupado. Deteniendo procesos..."
        sudo fuser -k 80/tcp || true
        sleep 2
    fi
    
    # 4. Crear carpeta certbot (el archivo se creará automáticamente dentro del contenedor)
    print_status "Creando carpeta certbot..."
    mkdir -p ./certbot/www/.well-known/acme-challenge
    
    # 5. Probar con configuración simplificada primero
    print_status "Probando con configuración simplificada..."
    cp nginx/ssl_simple.conf nginx/ssl.conf
    
    # 6. Levantar solo nginx para prueba
    print_status "Levantando Nginx para prueba..."
    docker compose up -d nginx
    
    # 7. Esperar y probar
    print_status "Esperando a que Nginx esté listo..."
    sleep 5
    
    # 8. Probar .well-known
    print_status "Probando acceso a .well-known..."
    for i in {1..15}; do
        CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt | tr -d '\r\n' || true)
        if [[ "$CHALLENGE" == "test-appo" ]]; then
            print_success "✅ Nginx funciona correctamente"
            
            # 9. Probar configuración completa
            print_status "Probando configuración completa..."
            cp nginx/ssl.conf nginx/ssl.conf.backup
            cp nginx/ssl_simple.conf nginx/ssl.conf
            
            docker compose restart nginx
            sleep 5
            
            CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt | tr -d '\r\n' || true)
            if [[ "$CHALLENGE" == "test-appo" ]]; then
                print_success "✅ Configuración completa funciona"
                return 0
            else
                print_warning "⚠️ Configuración completa falló, usando simplificada"
                cp nginx/ssl.conf.backup nginx/ssl.conf
                docker compose restart nginx
                return 0
            fi
        fi
        
        if [[ $i -eq 15 ]]; then
            print_error "❌ Nginx no funciona correctamente después de 15 intentos"
            print_status "Logs de Nginx:"
            docker compose logs nginx
            print_status "Intentando reiniciar Nginx..."
            docker compose restart nginx
            sleep 5
            CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt | tr -d '\r\n' || true)
            if [[ "$CHALLENGE" == "test-appo" ]]; then
                print_success "✅ Nginx funciona después del reinicio"
                return 0
            else
                print_error "❌ Nginx sigue sin funcionar. Revisa la configuración."
                
                # Intentar corregir mapeo de volúmenes
                if ! fix_volume_mapping; then
                    return 1
                fi
            fi
        fi
        sleep 1
    done
}

# Función para verificar y corregir el archivo test.txt
verify_and_fix_test_file() {
    print_status "🔍 Verificando archivo test.txt..."
    
    # 1. Verificar si el archivo existe en la ubicación correcta
    if docker compose exec nginx ls -la /var/www/certbot/.well-known/acme-challenge/test.txt 2>/dev/null; then
        print_success "Archivo test.txt existe en ubicación correcta"
        
        # 2. Verificar contenido
        CONTENT=$(docker compose exec nginx cat /var/www/certbot/.well-known/acme-challenge/test.txt | tr -d '\r\n')
        if [[ "$CONTENT" == "test-appo" ]]; then
            print_success "Contenido del archivo es correcto"
            return 0
        else
            print_warning "Contenido incorrecto: '$CONTENT'"
        fi
    else
        print_warning "Archivo test.txt no existe en ubicación correcta"
    fi
    
    # 3. Verificar si existe en ubicación incorrecta
    if docker compose exec nginx ls -la /var/www/certbot/test.txt 2>/dev/null; then
        print_warning "Archivo test.txt existe en ubicación incorrecta, eliminando..."
        docker compose exec nginx rm /var/www/certbot/test.txt
    fi
    
    # 4. Crear archivo en ubicación correcta
    print_status "Creando archivo test.txt en ubicación correcta..."
    docker compose exec nginx bash -c "mkdir -p /var/www/certbot/.well-known/acme-challenge && echo -n 'test-appo' > /var/www/certbot/.well-known/acme-challenge/test.txt"
    
    # 5. Verificar que se creó correctamente
    if docker compose exec nginx ls -la /var/www/certbot/.well-known/acme-challenge/test.txt 2>/dev/null; then
        CONTENT=$(docker compose exec nginx cat /var/www/certbot/.well-known/acme-challenge/test.txt | tr -d '\r\n')
        if [[ "$CONTENT" == "test-appo" ]]; then
            print_success "✅ Archivo test.txt creado y verificado correctamente"
            return 0
        else
            print_error "❌ No se pudo crear el archivo test.txt correctamente"
            return 1
        fi
    else
        print_error "❌ No se pudo crear el archivo test.txt"
        return 1
    fi
}

echo "🚀 Iniciando despliegue de APPO..."

# 1. Resolver conflictos de puertos
resolve_port_conflicts

# 2. Verificar entorno
if [ ! -f "docker-compose.yml" ]; then
    print_error "No se encontró docker-compose.yml. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

if ! command -v docker &>/dev/null; then
    print_error "Docker no está instalado."
    exit 1
fi

if ! docker compose version &>/dev/null; then
    print_error "Docker Compose no está disponible (revisa tu instalación de Docker 20.10+)."
    exit 1
fi

# 3. Configurar logs
setup_logs

# 4. .env
if [ ! -f ".env" ]; then
    print_warning "Archivo .env no encontrado. Creando desde plantilla..."
    if [ -f "env_production.txt" ]; then
        cp env_production.txt .env
        generate_secret_key
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

# 5. Diagnóstico completo
if ! diagnose_nginx; then
    print_warning "Diagnóstico mostró problemas, aplicando correcciones..."
fi

# 6. Verificar y corregir Nginx automáticamente
if ! verify_and_fix_nginx; then
    print_error "No se pudo corregir la configuración de Nginx. Revisa los logs."
    exit 1
fi

# 7. Dominio apuntando
print_status "Verificando que el dominio apunte a este servidor..."
IP_LOCAL=$(curl -4 -s ifconfig.me)
IP_DOMINIO=$(dig +short appo.com.co | tail -n1)

if [[ "$IP_LOCAL" != "$IP_DOMINIO" ]]; then
    print_error "El dominio appo.com.co no apunta a este servidor."
    echo "➡️ IP actual: $IP_LOCAL | IP del dominio: $IP_DOMINIO"
    exit 1
fi

print_success "El dominio apunta correctamente."

# 8. Dependencias
print_status "Verificando dependencias del sistema..."
apt-get update -y -qq
apt-get install -y -qq curl wget git unzip certbot lsof dnsutils

# 9. Verificar desafío en nginx desde el dominio
print_status "Verificando acceso desde el dominio..."
for i in {1..10}; do
    CHALLENGE=$(curl -s http://appo.com.co/.well-known/acme-challenge/test.txt | tr -d '\r\n' || true)
    if [[ "$CHALLENGE" == "test-appo" ]]; then
        print_success "✅ El dominio responde correctamente"
        break
    fi
    if [[ $i -eq 10 ]]; then
        print_warning "⚠️ El dominio no responde correctamente. Continuando de todas formas..."
    fi
    sleep 1
done

# 10. Solicitar certificado
print_status "Solicitando certificado SSL..."
certbot certonly --webroot -w ./certbot/www \
    --non-interactive --agree-tos --email contacto@appo.com.co \
    -d appo.com.co -d www.appo.com.co

if [[ $? -ne 0 ]]; then
    print_error "Fallo la obtención del certificado SSL."
    exit 1
fi

print_success "Certificado SSL obtenido correctamente."

# 11. Configurar SSL
print_status "Configurando SSL..."
if [ -f "/etc/letsencrypt/live/appo.com.co/fullchain.pem" ]; then
    # Crear configuración SSL
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
    print_status "Actualizando configuración de Nginx para SSL..."
    sed -i 's|./nginx/ssl.conf:/etc/nginx/ssl.conf:ro|./nginx/ssl_production.conf:/etc/nginx/ssl.conf:ro|' docker-compose.yml
    
    print_success "Configuración SSL creada correctamente"
else
    print_error "No se encontraron los certificados SSL después de la obtención."
    exit 1
fi

# 12. Reiniciar nginx con SSL
print_status "Reiniciando Nginx con SSL..."
docker compose restart nginx

# 13. Build de contenedores
print_status "Construyendo contenedores Docker..."
docker compose build --no-cache

# 14. Levantar contenedores
print_status "Levantando todos los servicios..."
docker compose up -d
sleep 10

# 15. Verificar servicios
if ! docker compose ps | grep -q "Up"; then
    print_error "Los contenedores no están corriendo correctamente"
    docker compose logs
    exit 1
fi

# 16. DB & migraciones
print_status "Configurando base de datos..."
docker compose exec -T db psql -U postgres -c "CREATE USER vitaluser WITH PASSWORD 'vitalpass';" 2>/dev/null || true
docker compose exec -T db psql -U postgres -c "CREATE DATABASE vitalmix OWNER vitaluser;" 2>/dev/null || true
docker compose exec -T db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE vitalmix TO vitaluser;" 2>/dev/null || true

print_status "Aplicando migraciones de Django..."
docker compose exec web python manage.py migrate

print_status "Recolectando archivos estáticos..."
docker compose exec web python manage.py collectstatic --noinput

print_status "Verificando superusuario..."
if ! docker compose exec web python manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" | grep -q "True"; then
    print_warning "No se encontró superusuario. Puedes crearlo con:"
    echo "👉 docker compose exec web python manage.py createsuperuser"
fi

# 17. Configurar firewall
print_status "Configurando firewall..."
if command -v ufw &> /dev/null; then
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    ufw --force enable
    print_success "Firewall configurado correctamente"
else
    print_warning "UFW no está instalado. Instalando..."
    apt-get install -y ufw
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    ufw --force enable
    print_success "Firewall instalado y configurado"
fi

# 18. Resultado final
print_success "¡Despliegue completo y exitoso!"

echo
echo "🌐 Sitio: https://appo.com.co"
echo "🔐 Admin: https://appo.com.co/admin/"
echo
echo "📦 Comandos útiles:"
echo "   - Logs: docker compose logs -f"
echo "   - Reinicio: docker compose restart"
echo "   - Parar: docker compose down"
echo "   - Superusuario: docker compose exec web python manage.py createsuperuser"
echo "   - Ver logs: tail -f logs/nginx/access.log"
echo
print_success "¡APPO está listo para producción! 🚀"
