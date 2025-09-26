#!/bin/bash

echo "🔄 Reiniciando Docker con configuración de desarrollo..."

# Detener todos los contenedores
echo "⏹️ Deteniendo contenedores..."
docker compose down

# Limpiar contenedores y volúmenes (opcional)
echo "🧹 Limpiando contenedores..."
docker compose down --volumes --remove-orphans

# Reconstruir las imágenes
echo "🔨 Reconstruyendo imágenes..."
docker compose build --no-cache

# Iniciar los servicios
echo "🚀 Iniciando servicios..."
docker compose up -d

# Mostrar el estado
echo "📊 Estado de los contenedores:"
docker compose ps

echo ""
echo "✅ Docker reiniciado con configuración de desarrollo"
echo "🌐 Accede a la aplicación en: http://localhost:8080"
echo "📝 Logs de nginx: docker compose logs nginx"
echo "📝 Logs de web: docker compose logs web"
