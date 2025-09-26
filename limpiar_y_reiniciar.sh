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

echo "🧹 Limpiando y reiniciando todo..."

# 1. Detener todos los contenedores
print_status "Deteniendo contenedores..."
docker compose down

# 2. Limpiar volúmenes (opcional)
read -p "¿Deseas eliminar también los volúmenes de datos? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Eliminando volúmenes..."
    docker volume prune -f
fi

# 3. Limpiar imágenes no utilizadas
print_status "Limpiando imágenes no utilizadas..."
docker image prune -f

# 4. Verificar puerto 80
print_status "Verificando puerto 80..."
if lsof -i:80 | grep -q LISTEN; then
    print_warning "Puerto 80 ocupado. Deteniendo procesos..."
    sudo fuser -k 80/tcp || true
    sleep 2
fi

# 5. Crear carpeta certbot
print_status "Creando carpeta certbot..."
mkdir -p ./certbot/www
echo "test-appo" > ./certbot/www/test.txt

# 6. Verificar configuración de nginx
print_status "Verificando configuración de Nginx..."
if nginx -t 2>/dev/null; then
    print_success "Configuración de Nginx válida"
else
    print_warning "Nginx no está instalado localmente (normal en Docker)"
fi

# 7. Levantar solo nginx para prueba
print_status "Levantando Nginx para prueba..."
docker compose up -d nginx

# 8. Esperar y probar
print_status "Esperando a que Nginx esté listo..."
sleep 5

# 9. Probar .well-known
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
        print_status "Intentando reiniciar Nginx..."
        docker compose restart nginx
        sleep 5
        CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt || true)
        if [[ "$CHALLENGE" == "test-appo" ]]; then
            print_success "✅ Nginx funciona después del reinicio"
        else
            print_error "❌ Nginx sigue sin funcionar"
            exit 1
        fi
    fi
    sleep 1
done

print_success "✅ Limpieza y reinicio completados"
print_status "Ahora puedes ejecutar: ./deploy.sh" 