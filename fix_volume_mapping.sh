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

echo "🔧 Corrigiendo mapeo de volúmenes..."

# 1. Detener contenedores
print_status "Deteniendo contenedores..."
docker compose down

# 2. Verificar archivo en host
print_status "Verificando archivo en host..."
mkdir -p ./certbot/www
echo "test-appo" > ./certbot/www/test.txt
ls -la ./certbot/www/

# 3. Verificar docker-compose.yml
print_status "Verificando configuración de volúmenes..."
if grep -q "./certbot/www:/var/www/certbot" docker-compose.yml; then
    print_success "Volumen configurado correctamente en docker-compose.yml"
else
    print_error "Volumen NO está configurado correctamente"
    print_status "Agregando volumen al docker-compose.yml..."
    # Buscar la línea de volúmenes de nginx y agregar el volumen
    sed -i '/nginx:/,/restart: always/ { /volumes:/,/restart: always/ { /- \.\/certbot\/www:\/var\/www\/certbot/! s/restart: always/      - .\/certbot\/www:\/var\/www\/certbot\n    restart: always/ } }' docker-compose.yml
fi

# 4. Crear configuración nginx mínima
print_status "Creando configuración nginx mínima..."
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

# 5. Usar configuración mínima
print_status "Usando configuración mínima..."
cp nginx/ssl_minimal.conf nginx/ssl.conf

# 6. Levantar nginx
print_status "Levantando Nginx..."
docker compose up -d nginx

# 7. Esperar
print_status "Esperando a que Nginx esté listo..."
sleep 5

# 8. Verificar archivo dentro del contenedor
print_status "Verificando archivo dentro del contenedor..."
if docker compose exec nginx ls -la /var/www/certbot/test.txt 2>/dev/null; then
    print_success "Archivo existe dentro del contenedor"
    echo "Contenido: $(docker compose exec nginx cat /var/www/certbot/test.txt)"
else
    print_error "Archivo NO existe dentro del contenedor"
    print_status "Verificando volúmenes..."
    docker compose exec nginx ls -la /var/www/certbot/
    print_status "Verificando configuración de volúmenes..."
    docker compose exec nginx mount | grep certbot || echo "No se encontró volumen certbot"
    exit 1
fi

# 9. Probar acceso
print_status "Probando acceso a .well-known..."
for i in {1..10}; do
    CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt || true)
    if [[ "$CHALLENGE" == "test-appo" ]]; then
        print_success "✅ Nginx funciona correctamente con mapeo de volúmenes corregido"
        break
    fi
    if [[ $i -eq 10 ]]; then
        print_error "❌ Nginx no funciona después de corregir volúmenes"
        print_status "Logs de Nginx:"
        docker compose logs nginx
        exit 1
    fi
    sleep 1
done

print_success "✅ Mapeo de volúmenes corregido!"
print_status "Ahora puedes ejecutar: ./deploy.sh" 