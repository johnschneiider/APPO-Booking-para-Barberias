#!/bin/bash
# Script para gestionar solo los procesos de Gunicorn de appo.com.co
# NO afecta otros proyectos

set -e

PROJECT_DIR="/var/www/appo.com.co"
SERVICE_NAME="appo"

echo "🔍 Verificando procesos de Gunicorn..."

# Ver TODOS los procesos de gunicorn en el sistema
echo ""
echo "📊 Todos los procesos de Gunicorn en el sistema:"
ps aux | grep gunicorn | grep -v grep || echo "   No hay procesos de Gunicorn"

echo ""
echo "📊 Procesos de Gunicorn de appo.com.co específicamente:"
ps aux | grep gunicorn | grep "$PROJECT_DIR" | grep -v grep || echo "   No hay procesos de appo.com.co"

echo ""
echo "📊 Procesos gestionados por systemd (servicio appo):"
sudo systemctl status $SERVICE_NAME --no-pager -l | grep -E "(PID|gunicorn)" || echo "   Servicio no está corriendo"

echo ""
echo "💡 Para reiniciar SOLO appo.com.co (sin afectar otros proyectos):"
echo "   sudo systemctl restart $SERVICE_NAME"
echo ""
echo "💡 Para detener SOLO appo.com.co:"
echo "   sudo systemctl stop $SERVICE_NAME"
echo ""
echo "💡 Para ver procesos de otros proyectos:"
echo "   ps aux | grep gunicorn | grep -v appo.com.co"

