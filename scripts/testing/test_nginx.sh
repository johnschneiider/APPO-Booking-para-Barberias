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

echo "🧪 Probando configuración de Nginx..."

# 1. Crear carpeta certbot si no existe
print_status "Creando carpeta ./certbot/www..."
mkdir -p ./certbot/www
echo "test-appo" > ./certbot/www/test.txt

# 2. Detener contenedores existentes
print_status "Deteniendo contenedores existentes..."
docker compose down

# 3. Levantar solo nginx
print_status "Levantando Nginx..."
docker compose up -d nginx

# 4. Esperar a que nginx esté listo
print_status "Esperando a que Nginx esté listo..."
sleep 5

# 5. Probar acceso a .well-known
print_status "Probando acceso a .well-known..."
for i in {1..10}; do
    CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt || true)
    if [[ "$CHALLENGE" == "test-appo" ]]; then
        print_success "✅ Nginx sirve correctamente la carpeta .well-known"
        break
    fi
    if [[ $i -eq 10 ]]; then
        print_error "❌ Nginx no sirve correctamente la carpeta .well-known"
        print_status "Logs de Nginx:"
        docker compose logs nginx
        exit 1
    fi
    sleep 1
done

# 6. Probar acceso al dominio (si está disponible)
print_status "Probando acceso al dominio..."
if curl -s http://appo.com.co/.well-known/acme-challenge/test.txt | grep -q "test-appo"; then
    print_success "✅ El dominio responde correctamente"
else
    print_warning "⚠️ El dominio no responde (puede ser normal si no está configurado)"
fi

print_success "✅ Configuración de Nginx verificada correctamente"
print_status "Puedes continuar con el deploy completo ejecutando: ./deploy.sh" 