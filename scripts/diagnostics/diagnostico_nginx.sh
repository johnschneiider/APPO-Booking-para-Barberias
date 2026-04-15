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

echo "🔍 Diagnóstico completo de Nginx..."

# 1. Verificar archivo de prueba
print_status "Verificando archivo de prueba..."
if [ -f "./certbot/www/test.txt" ]; then
    print_success "Archivo test.txt existe en host"
    echo "Contenido: $(cat ./certbot/www/test.txt)"
else
    print_error "Archivo test.txt NO existe en host"
    mkdir -p ./certbot/www
    echo "test-appo" > ./certbot/www/test.txt
    print_status "Archivo creado"
fi

# 2. Verificar contenedor
print_status "Verificando contenedor Nginx..."
if docker compose ps nginx | grep -q "Up"; then
    print_success "Contenedor Nginx está corriendo"
else
    print_error "Contenedor Nginx NO está corriendo"
    docker compose up -d nginx
    sleep 3
fi

# 3. Verificar archivo dentro del contenedor
print_status "Verificando archivo dentro del contenedor..."
if docker compose exec nginx ls -la /var/www/certbot/test.txt 2>/dev/null; then
    print_success "Archivo existe dentro del contenedor"
    echo "Contenido: $(docker compose exec nginx cat /var/www/certbot/test.txt)"
else
    print_error "Archivo NO existe dentro del contenedor"
fi

# 4. Verificar configuración de Nginx
print_status "Verificando configuración de Nginx..."
if docker compose exec nginx nginx -t 2>/dev/null; then
    print_success "Configuración de Nginx es válida"
else
    print_error "Configuración de Nginx NO es válida"
    docker compose exec nginx nginx -t
fi

# 5. Verificar logs de Nginx
print_status "Verificando logs de Nginx..."
docker compose logs nginx --tail=10

# 6. Probar acceso directo
print_status "Probando acceso directo..."
RESPONSE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt || echo "ERROR")
echo "Respuesta: '$RESPONSE'"

# 7. Verificar puertos
print_status "Verificando puertos..."
netstat -tlnp | grep :80 || echo "Puerto 80 no está escuchando"

# 8. Verificar volúmenes
print_status "Verificando volúmenes..."
docker compose exec nginx ls -la /var/www/certbot/

print_status "Diagnóstico completado" 