#!/bin/bash

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

echo "🔍 Verificando despliegue de APPO..."

# 1. Verificar contenedores
print_status "Verificando contenedores..."
if docker compose ps | grep -q "Up"; then
    print_success "Todos los contenedores están corriendo"
    docker compose ps
else
    print_error "Algunos contenedores no están corriendo"
    docker compose ps
    exit 1
fi

# 2. Verificar puertos
print_status "Verificando puertos..."
if netstat -tlnp | grep -q ":80 "; then
    print_success "Puerto 80 está abierto"
else
    print_error "Puerto 80 no está abierto"
fi

if netstat -tlnp | grep -q ":443 "; then
    print_success "Puerto 443 está abierto"
else
    print_warning "Puerto 443 no está abierto (normal si no hay SSL)"
fi

# 3. Verificar DNS
print_status "Verificando DNS..."
IP_DOMINIO=$(dig +short appo.com.co | tail -n1)
if [[ "$IP_DOMINIO" == "92.113.39.100" ]]; then
    print_success "DNS apunta correctamente a 92.113.39.100"
else
    print_warning "DNS apunta a $IP_DOMINIO, esperado: 92.113.39.100"
fi

# 4. Verificar certificados SSL
print_status "Verificando certificados SSL..."
if [ -f "/etc/letsencrypt/live/appo.com.co/fullchain.pem" ]; then
    print_success "Certificados SSL existen"
    
    # Verificar fecha de expiración
    EXPIRY=$(openssl x509 -enddate -noout -in /etc/letsencrypt/live/appo.com.co/fullchain.pem | cut -d= -f2)
    print_status "Certificado expira: $EXPIRY"
else
    print_warning "Certificados SSL no encontrados"
fi

# 5. Verificar logs
print_status "Verificando logs..."
if [ -d "logs" ]; then
    print_success "Directorio de logs existe"
    ls -la logs/
else
    print_warning "Directorio de logs no existe"
fi

# 6. Verificar archivos estáticos
print_status "Verificando archivos estáticos..."
if [ -d "staticfiles" ]; then
    print_success "Directorio staticfiles existe"
    echo "Archivos estáticos: $(find staticfiles -type f | wc -l)"
else
    print_warning "Directorio staticfiles no existe"
fi

# 7. Verificar base de datos
print_status "Verificando base de datos..."
if docker compose exec db pg_isready -U vitaluser -d vitalmix; then
    print_success "Base de datos PostgreSQL está funcionando"
else
    print_error "Base de datos PostgreSQL no está funcionando"
fi

# 8. Verificar Redis
print_status "Verificando Redis..."
if docker compose exec redis redis-cli ping | grep -q "PONG"; then
    print_success "Redis está funcionando"
else
    print_error "Redis no está funcionando"
fi

# 9. Verificar Nginx
print_status "Verificando Nginx..."
if docker compose exec nginx nginx -t; then
    print_success "Configuración de Nginx es válida"
else
    print_error "Configuración de Nginx NO es válida"
fi

# 10. Verificar aplicación web
print_status "Verificando aplicación web..."
if curl -f -s http://localhost:8000/ > /dev/null; then
    print_success "Aplicación web responde en puerto 8000"
else
    print_error "Aplicación web no responde en puerto 8000"
fi

# 11. Verificar dominio
print_status "Verificando dominio..."
if curl -f -s http://appo.com.co/ > /dev/null; then
    print_success "Dominio responde correctamente"
else
    print_warning "Dominio no responde (puede ser normal si no hay SSL)"
fi

# 12. Verificar SSL (si existe)
print_status "Verificando SSL..."
if curl -f -s https://appo.com.co/ > /dev/null; then
    print_success "SSL funciona correctamente"
else
    print_warning "SSL no funciona (puede ser normal si no está configurado)"
fi

# 13. Verificar firewall
print_status "Verificando firewall..."
if ufw status | grep -q "Status: active"; then
    print_success "Firewall está activo"
    ufw status numbered
else
    print_warning "Firewall no está activo"
fi

# 14. Verificar espacio en disco
print_status "Verificando espacio en disco..."
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_success "Espacio en disco OK: ${DISK_USAGE}% usado"
else
    print_warning "Espacio en disco bajo: ${DISK_USAGE}% usado"
fi

# 15. Verificar memoria
print_status "Verificando memoria..."
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
print_status "Memoria usada: ${MEMORY_USAGE}%"

# 16. Verificar logs de errores
print_status "Verificando logs de errores..."
if [ -f "logs/nginx/error.log" ]; then
    ERROR_COUNT=$(tail -100 logs/nginx/error.log | grep -c "error\|Error\|ERROR")
    if [ "$ERROR_COUNT" -eq 0 ]; then
        print_success "No hay errores recientes en logs de Nginx"
    else
        print_warning "Encontrados $ERROR_COUNT errores en logs de Nginx"
    fi
else
    print_warning "Archivo de logs de Nginx no encontrado"
fi

# 17. Verificar health checks
print_status "Verificando health checks..."
if docker compose exec web curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    print_success "Health check de aplicación OK"
else
    print_warning "Health check de aplicación falló"
fi

# 18. Resumen final
echo
echo "📊 RESUMEN DE VERIFICACIÓN:"
echo "=========================="
echo "✅ Contenedores: $(docker compose ps --filter 'status=running' --format 'table {{.Name}}' | wc -l) corriendo"
echo "✅ Puertos: $(netstat -tlnp | grep -E ':(80|443)' | wc -l) abiertos"
echo "✅ DNS: $(dig +short appo.com.co | wc -l) registros"
echo "✅ SSL: $(ls -la /etc/letsencrypt/live/appo.com.co/ 2>/dev/null | wc -l) certificados"
echo "✅ Logs: $(find logs -type f 2>/dev/null | wc -l) archivos"
echo "✅ Estáticos: $(find staticfiles -type f 2>/dev/null | wc -l) archivos"
echo "✅ Firewall: $(ufw status | grep -c 'ALLOW') reglas"

echo
print_success "¡Verificación completada!"
echo
echo "🌐 URLs importantes:"
echo "   - Sitio: https://appo.com.co"
echo "   - Admin: https://appo.com.co/admin/"
echo "   - API: https://appo.com.co/api/"
echo
echo "📦 Comandos útiles:"
echo "   - Logs en tiempo real: docker compose logs -f"
echo "   - Logs de Nginx: tail -f logs/nginx/access.log"
echo "   - Logs de errores: tail -f logs/nginx/error.log"
echo "   - Reiniciar: docker compose restart"
echo "   - Parar: docker compose down"
echo "   - Superusuario: docker compose exec web python manage.py createsuperuser" 