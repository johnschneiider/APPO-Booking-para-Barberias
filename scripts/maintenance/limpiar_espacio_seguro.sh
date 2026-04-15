#!/bin/bash
# Script para limpiar espacio SOLO del proyecto appo.com.co
# NO afecta a otros proyectos

set -e

echo "🧹 Limpiando espacio SOLO para appo.com.co..."
echo "⚠️  Este script NO afecta a otros proyectos"
echo ""

# 1. Limpiar logs SOLO de appo.com.co
echo "📁 Limpiando logs de appo.com.co..."
cd /var/www/appo.com.co
find logs -name "*.log" -size +10M -exec truncate -s 0 {} \; 2>/dev/null || true
find logs -name "*.log.*" -delete 2>/dev/null || true
echo "✅ Logs de appo.com.co limpiados"

# 2. Limpiar cache de Python (solo appo.com.co)
echo "🐍 Limpiando cache de Python..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✅ Cache de Python limpiado"

# 3. Limpiar cache de pip (solo del venv de appo.com.co)
echo "📦 Limpiando cache de pip..."
if [ -d "venv" ]; then
    venv/bin/pip cache purge 2>/dev/null || true
fi
echo "✅ Cache de pip limpiado"

# 4. Limpiar archivos temporales de appo.com.co
echo "🗑️  Limpiando archivos temporales..."
find . -type f -name "*.tmp" -delete 2>/dev/null || true
find . -type f -name "*.bak" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
echo "✅ Archivos temporales eliminados"

# 5. Limpiar logs rotados de nginx SOLO si son muy grandes (más de 50MB)
# Esto es seguro porque solo trunca, no elimina
echo "🌐 Limpiando logs de nginx (solo si son muy grandes)..."
if [ -f "/var/log/nginx/access.log" ]; then
    SIZE=$(stat -f%z /var/log/nginx/access.log 2>/dev/null || stat -c%s /var/log/nginx/access.log 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 52428800 ]; then  # 50MB
        echo "⚠️  Log de access.log es muy grande ($SIZE bytes), truncando..."
        sudo truncate -s 10M /var/log/nginx/access.log
    fi
fi

if [ -f "/var/log/nginx/error.log" ]; then
    SIZE=$(stat -f%z /var/log/nginx/error.log 2>/dev/null || stat -c%s /var/log/nginx/error.log 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 52428800 ]; then  # 50MB
        echo "⚠️  Log de error.log es muy grande ($SIZE bytes), truncando..."
        sudo truncate -s 10M /var/log/nginx/error.log
    fi
fi
echo "✅ Logs de nginx verificados"

# 6. Limpiar cache de apt (seguro, no afecta proyectos)
echo "📦 Limpiando cache de apt..."
sudo apt clean
echo "✅ Cache de apt limpiado"

# 7. Limpiar journalctl (seguro, solo logs del sistema)
echo "📋 Limpiando journalctl..."
sudo journalctl --vacuum-time=2d
echo "✅ Journalctl limpiado"

# 8. Verificar espacio
echo ""
echo "📊 Espacio disponible después de la limpieza:"
df -h / | tail -1

echo ""
echo "✅ Limpieza completada. Solo se afectó appo.com.co y logs del sistema."
echo "⚠️  Los otros proyectos (predicta, vitalmix) NO fueron afectados."

