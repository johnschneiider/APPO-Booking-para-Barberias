@echo off
echo 🔄 Deteniendo contenedores Docker...
docker-compose down

echo 🧹 Limpiando volúmenes...
docker-compose down -v

echo 🔨 Reconstruyendo imágenes...
docker-compose build --no-cache

echo 🚀 Iniciando contenedores...
docker-compose up -d

echo ⏳ Esperando que la base de datos esté lista...
timeout /t 10 /nobreak

echo 🗄️ Ejecutando migraciones...
docker-compose exec web python manage.py migrate

echo 📦 Recolectando archivos estáticos...
docker-compose exec web python manage.py collectstatic --noinput

echo ✅ ¡Docker reiniciado exitosamente!
echo 🌐 La aplicación está disponible en: http://localhost
echo 📊 Logs: docker-compose logs -f web
pause 