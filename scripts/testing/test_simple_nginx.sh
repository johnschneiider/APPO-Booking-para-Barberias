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

echo "🧪 Probando configuración simplificada de Nginx..."

# 1. Detener contenedores
print_status "Deteniendo contenedores..."
docker compose down

# 2. Crear archivo de prueba
print_status "Creando archivo de prueba..."
mkdir -p ./certbot/www
echo "test-appo" > ./certbot/www/test.txt

# 3. Cambiar a configuración simplificada
print_status "Cambiando a configuración simplificada..."
cp nginx/ssl_simple.conf nginx/ssl.conf

# 4. Levantar nginx
print_status "Levantando Nginx..."
docker compose up -d nginx

# 5. Esperar
print_status "Esperando a que Nginx esté listo..."
sleep 5

# 6. Verificar archivo dentro del contenedor
print_status "Verificando archivo dentro del contenedor..."
if docker compose exec nginx ls -la /var/www/certbot/test.txt 2>/dev/null; then
    print_success "Archivo existe dentro del contenedor"
    echo "Contenido: $(docker compose exec nginx cat /var/www/certbot/test.txt)"
else
    print_error "Archivo NO existe dentro del contenedor"
    print_status "Verificando volúmenes..."
    docker compose exec nginx ls -la /var/www/certbot/
    exit 1
fi

# 7. Probar acceso
print_status "Probando acceso a .well-known..."
for i in {1..10}; do
    CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt || true)
    if [[ "$CHALLENGE" == "test-appo" ]]; then
        print_success "✅ Nginx funciona correctamente con configuración simplificada"
        break
    fi
    if [[ $i -eq 10 ]]; then
        print_error "❌ Nginx no funciona con configuración simplificada"
        print_status "Logs de Nginx:"
        docker compose logs nginx
        exit 1
    fi
    sleep 1
done

print_success "✅ Configuración simplificada funciona!"
print_status "Ahora puedes ejecutar: ./deploy.sh" 