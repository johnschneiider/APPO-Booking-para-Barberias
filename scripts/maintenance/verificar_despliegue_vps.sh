#!/bin/bash
# Script para verificar que el despliegue esté completo y funcionando

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

echo "═══════════════════════════════════════════════════════════"
echo "🔍 VERIFICANDO DESPLIEGUE DE APPO"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 1. Verificar servicios
print_status "1. Verificando servicios del sistema..."

# PostgreSQL
if systemctl is-active --quiet postgresql; then
    print_success "PostgreSQL está corriendo"
else
    print_error "PostgreSQL NO está corriendo"
    echo "   Solución: sudo systemctl start postgresql"
fi

# Redis
if systemctl is-active --quiet redis-server; then
    print_success "Redis está corriendo"
else
    print_error "Redis NO está corriendo"
    echo "   Solución: sudo systemctl start redis-server"
fi

# Nginx
if systemctl is-active --quiet nginx; then
    print_success "Nginx está corriendo"
else
    print_error "Nginx NO está corriendo"
    echo "   Solución: sudo systemctl start nginx"
fi

# Gunicorn (servicio appo)
if systemctl is-active --quiet appo; then
    print_success "Gunicorn (appo) está corriendo"
else
    print_error "Gunicorn (appo) NO está corriendo"
    echo "   Solución: sudo systemctl start appo"
fi

echo ""

# 2. Verificar configuración de Nginx
print_status "2. Verificando configuración de Nginx..."
if [ -f "/etc/nginx/sites-enabled/appo.com.co" ]; then
    print_success "Configuración de Nginx encontrada"
    if sudo nginx -t 2>&1 | grep -q "successful"; then
        print_success "Configuración de Nginx es válida"
    else
        print_error "Error en la configuración de Nginx"
        echo "   Ejecuta: sudo nginx -t"
    fi
else
    print_error "Configuración de Nginx NO encontrada"
    echo "   Solución: Verifica que nginx-appo.conf esté en /etc/nginx/sites-enabled/"
fi

echo ""

# 3. Verificar certificado SSL
print_status "3. Verificando certificado SSL..."
if [ -f "/etc/letsencrypt/live/appo.com.co/fullchain.pem" ]; then
    print_success "Certificado SSL encontrado"
    CERT_EXPIRY=$(sudo openssl x509 -enddate -noout -in /etc/letsencrypt/live/appo.com.co/fullchain.pem | cut -d= -f2)
    print_status "   Certificado válido hasta: $CERT_EXPIRY"
else
    print_warning "Certificado SSL NO encontrado"
    echo "   Solución: sudo certbot --nginx -d appo.com.co -d www.appo.com.co"
fi

echo ""

# 4. Verificar que Gunicorn responda
print_status "4. Verificando que Gunicorn responda en localhost:8888..."
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8888/health/ | grep -q "200\|404"; then
    print_success "Gunicorn responde en localhost:8888"
else
    print_error "Gunicorn NO responde en localhost:8888"
    echo "   Verifica logs: sudo journalctl -u appo -n 50"
fi

echo ""

# 5. Verificar base de datos
print_status "5. Verificando conexión a base de datos..."
if [ -f ".env" ]; then
    source .env
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;" &>/dev/null; then
        print_success "Conexión a base de datos exitosa"
    else
        print_error "No se puede conectar a la base de datos"
        echo "   Verifica credenciales en .env"
    fi
else
    print_warning "Archivo .env no encontrado"
fi

echo ""

# 6. Verificar DNS
print_status "6. Verificando DNS..."
DOMAIN_IP=$(dig +short appo.com.co | tail -n1)
SERVER_IP=$(curl -4 -s ifconfig.me)

if [ "$DOMAIN_IP" == "$SERVER_IP" ]; then
    print_success "DNS configurado correctamente"
    print_status "   appo.com.co apunta a: $DOMAIN_IP"
else
    print_warning "DNS puede no estar configurado correctamente"
    print_status "   appo.com.co apunta a: $DOMAIN_IP"
    print_status "   IP del servidor: $SERVER_IP"
fi

echo ""

# 7. Verificar acceso HTTP/HTTPS
print_status "7. Verificando acceso web..."

# HTTP
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://appo.com.co 2>/dev/null || echo "000")
if [ "$HTTP_CODE" == "301" ] || [ "$HTTP_CODE" == "302" ] || [ "$HTTP_CODE" == "200" ]; then
    print_success "HTTP responde (código: $HTTP_CODE)"
else
    print_warning "HTTP no responde correctamente (código: $HTTP_CODE)"
fi

# HTTPS
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://appo.com.co 2>/dev/null || echo "000")
if [ "$HTTPS_CODE" == "200" ] || [ "$HTTPS_CODE" == "301" ] || [ "$HTTPS_CODE" == "302" ]; then
    print_success "HTTPS responde (código: $HTTPS_CODE)"
else
    print_warning "HTTPS no responde correctamente (código: $HTTPS_CODE)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📋 RESUMEN"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Resumen final
ALL_OK=true

if ! systemctl is-active --quiet appo; then
    ALL_OK=false
fi

if ! systemctl is-active --quiet nginx; then
    ALL_OK=false
fi

if [ "$HTTPS_CODE" != "200" ] && [ "$HTTPS_CODE" != "301" ] && [ "$HTTPS_CODE" != "302" ]; then
    ALL_OK=false
fi

if [ "$ALL_OK" = true ]; then
    print_success "🎉 ¡Todo parece estar funcionando correctamente!"
    echo ""
    print_status "🌐 Accede a tu aplicación en:"
    print_status "   https://appo.com.co"
    echo ""
    print_status "👤 Usuario superadmin:"
    print_status "   Username: superadmin"
    print_status "   Password: Malware01"
else
    print_warning "⚠️ Hay algunos problemas que resolver"
    echo ""
    print_status "Comandos útiles para diagnosticar:"
    print_status "   Ver logs de Gunicorn: sudo journalctl -u appo -f"
    print_status "   Ver logs de Nginx: sudo tail -f /var/log/nginx/error.log"
    print_status "   Reiniciar servicios: sudo systemctl restart appo nginx"
fi

echo ""

