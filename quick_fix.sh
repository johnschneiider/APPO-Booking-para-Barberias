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

echo "🔧 Aplicando corrección rápida..."

# 1. Detener contenedores
print_status "Deteniendo contenedores..."
docker compose down

# 2. Crear carpeta certbot
print_status "Creando carpeta certbot..."
mkdir -p ./certbot/www
echo "test-appo" > ./certbot/www/test.txt

# 3. Verificar configuración de nginx
print_status "Verificando configuración de Nginx..."
if docker compose exec nginx nginx -t 2>/dev/null; then
    print_success "Configuración de Nginx válida"
else
    print_warning "Nginx no está corriendo, continuando..."
fi

# 4. Levantar solo nginx
print_status "Levantando Nginx..."
docker compose up -d nginx

# 5. Esperar y probar
print_status "Esperando a que Nginx esté listo..."
sleep 5

# 6. Probar .well-known
print_status "Probando acceso a .well-known..."
for i in {1..10}; do
    CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt || true)
    if [[ "$CHALLENGE" == "test-appo" ]]; then
        print_success "✅ Nginx funciona correctamente"
        break
    fi
    if [[ $i -eq 10 ]]; then
        print_error "❌ Nginx no funciona correctamente"
        print_status "Logs de Nginx:"
        docker compose logs nginx
        exit 1
    fi
    sleep 1
done

print_success "✅ Corrección aplicada correctamente!"
print_status "Ahora puedes ejecutar: ./deploy.sh" 