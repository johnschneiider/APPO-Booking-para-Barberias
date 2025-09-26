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

echo "🧪 Probando configuración de despliegue..."

# Función para verificar y corregir Nginx (copiada del deploy.sh)
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
    
    # 4. Crear carpeta certbot
    print_status "Creando carpeta certbot..."
    mkdir -p ./certbot/www
    echo "test-appo" > ./certbot/www/test.txt
    
    # 5. Levantar solo nginx para prueba
    print_status "Levantando Nginx para prueba..."
    docker compose up -d nginx
    
    # 6. Esperar y probar
    print_status "Esperando a que Nginx esté listo..."
    sleep 5
    
    # 7. Probar .well-known
    print_status "Probando acceso a .well-known..."
    for i in {1..15}; do
        CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt || true)
        if [[ "$CHALLENGE" == "test-appo" ]]; then
            print_success "✅ Nginx funciona correctamente"
            return 0
        fi
        if [[ $i -eq 15 ]]; then
            print_error "❌ Nginx no funciona correctamente después de 15 intentos"
            print_status "Logs de Nginx:"
            docker compose logs nginx
            print_status "Intentando reiniciar Nginx..."
            docker compose restart nginx
            sleep 5
            CHALLENGE=$(curl -s http://localhost/.well-known/acme-challenge/test.txt || true)
            if [[ "$CHALLENGE" == "test-appo" ]]; then
                print_success "✅ Nginx funciona después del reinicio"
                return 0
            else
                print_error "❌ Nginx sigue sin funcionar. Revisa la configuración."
                return 1
            fi
        fi
        sleep 1
    done
}

# Verificar entorno
if [ ! -f "docker-compose.yml" ]; then
    print_error "No se encontró docker-compose.yml. Ejecuta este script desde la raíz del proyecto."
    exit 1
fi

if ! command -v docker &>/dev/null; then
    print_error "Docker no está instalado."
    exit 1
fi

if ! docker compose version &>/dev/null; then
    print_error "Docker Compose no está disponible."
    exit 1
fi

# Verificar y corregir Nginx
if ! verify_and_fix_nginx; then
    print_error "No se pudo corregir la configuración de Nginx."
    exit 1
fi

# Verificar dominio
print_status "Verificando dominio..."
IP_LOCAL=$(curl -4 -s ifconfig.me)
IP_DOMINIO=$(dig +short appo.com.co | tail -n1)

if [[ "$IP_LOCAL" != "$IP_DOMINIO" ]]; then
    print_warning "⚠️ El dominio appo.com.co no apunta a este servidor."
    echo "➡️ IP actual: $IP_LOCAL | IP del dominio: $IP_DOMINIO"
else
    print_success "✅ El dominio apunta correctamente."
fi

# Probar acceso desde el dominio
print_status "Probando acceso desde el dominio..."
for i in {1..5}; do
    CHALLENGE=$(curl -s http://appo.com.co/.well-known/acme-challenge/test.txt || true)
    if [[ "$CHALLENGE" == "test-appo" ]]; then
        print_success "✅ El dominio responde correctamente"
        break
    fi
    if [[ $i -eq 5 ]]; then
        print_warning "⚠️ El dominio no responde correctamente (puede ser normal si no está configurado)"
    fi
    sleep 1
done

print_success "✅ Prueba completada exitosamente!"
print_status "Ahora puedes ejecutar el deploy completo con: ./deploy.sh" 