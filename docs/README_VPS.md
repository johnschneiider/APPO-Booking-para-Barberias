# 🚀 Guía de Despliegue APPO en VPS (Sin Docker)

Esta guía te ayudará a desplegar APPO en una VPS con Nginx compartido, siguiendo la misma estructura que tus otros proyectos (predicta.com.co, vitalmix.com.co).

## 📋 Requisitos Previos

- VPS con Debian/Ubuntu
- Acceso root o sudo
- Dominio `appo.com.co` apuntando a tu VPS
- Nginx ya instalado y configurado (compartido con otros proyectos)
- PostgreSQL instalado (o se instalará automáticamente)
- Redis instalado (o se instalará automáticamente)
- Python 3.8+ instalado

## 🔧 Pasos de Despliegue

### 1. Preparar el Proyecto en Local

Antes de hacer push, asegúrate de tener estos archivos en tu repositorio:

- ✅ `nginx-appo.conf` - Configuración de Nginx
- ✅ `env_vps_production.txt` - Plantilla de variables de entorno
- ✅ `deploy_vps.sh` - Script de despliegue automatizado
- ✅ `melissa/settings.py` - Ya modificado para soportar VPS

### 2. Hacer Push a GitHub

```bash
git add .
git commit -m "Preparar proyecto para despliegue en VPS sin Docker"
git push origin main
```

### 3. En la VPS - Clonar el Repositorio

```bash
cd /var/www
sudo git clone [TU_REPOSITORIO_GITHUB] appo.com.co
cd appo.com.co
sudo chown -R $USER:$USER .
```

### 4. Ejecutar Script de Despliegue

```bash
chmod +x deploy_vps.sh
./deploy_vps.sh
```

El script automáticamente:
- ✅ Crea directorios necesarios
- ✅ Instala PostgreSQL y Redis si no están
- ✅ Crea base de datos PostgreSQL
- ✅ Instala dependencias de Python
- ✅ Configura variables de entorno
- ✅ Ejecuta migraciones
- ✅ Recopila archivos estáticos
- ✅ Configura Nginx
- ✅ Obtiene certificado SSL
- ✅ Crea servicio systemd para Gunicorn

### 5. Configurar Variables de Entorno

**IMPORTANTE**: Después del despliegue, edita el archivo `.env`:

```bash
nano .env
```

Asegúrate de configurar:
- `SECRET_KEY` - Ya generado automáticamente
- `POSTGRES_PASSWORD` - Contraseña segura para PostgreSQL
- `EMAIL_HOST_USER` - Tu email
- `EMAIL_HOST_PASSWORD` - Contraseña de aplicación
- `TWILIO_ACCOUNT_SID` - Si usas Twilio
- `TWILIO_AUTH_TOKEN` - Si usas Twilio

### 6. Reiniciar Servicios

```bash
sudo systemctl restart appo
sudo systemctl restart nginx
```

## 🔍 Verificación

### Verificar que todo esté corriendo:

```bash
# Verificar Gunicorn
sudo systemctl status appo

# Verificar Nginx
sudo systemctl status nginx

# Verificar Redis
sudo systemctl status redis-server

# Verificar PostgreSQL
sudo systemctl status postgresql
```

### Ver logs:

```bash
# Logs de Gunicorn
sudo journalctl -u appo -f

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Logs de Django
tail -f /var/www/appo.com.co/logs/django.log
```

## 📁 Estructura de Directorios

```
/var/www/appo.com.co/
├── manage.py
├── melissa/
├── staticfiles/          # Archivos estáticos recopilados
├── media/                # Archivos subidos por usuarios
├── logs/                 # Logs de la aplicación
├── venv/                 # Entorno virtual de Python
├── .env                  # Variables de entorno (NO subir a Git)
└── ...
```

## 🔄 Actualizaciones Futuras

Cuando hagas cambios y quieras actualizar en la VPS:

```bash
cd /var/www/appo.com.co
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # Si hay nuevas dependencias
python manage.py migrate         # Si hay nuevas migraciones
python manage.py collectstatic --noinput
sudo systemctl restart appo
```

## 🛠️ Comandos Útiles

### Reiniciar aplicación:
```bash
sudo systemctl restart appo
```

### Ver logs en tiempo real:
```bash
sudo journalctl -u appo -f
```

### Crear superusuario:
```bash
cd /var/www/appo.com.co
source venv/bin/activate
python manage.py createsuperuser
```

### Verificar configuración de Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Renovar certificado SSL:
```bash
sudo certbot renew
sudo systemctl reload nginx
```

## 🐛 Solución de Problemas

### Error: "No se puede conectar a PostgreSQL"
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Verificar credenciales en .env
cat .env | grep POSTGRES
```

### Error: "No se puede conectar a Redis"
```bash
# Verificar que Redis esté corriendo
sudo systemctl status redis-server

# Probar conexión
redis-cli ping
```

### Error: "502 Bad Gateway"
```bash
# Verificar que Gunicorn esté corriendo
sudo systemctl status appo

# Ver logs de Gunicorn
sudo journalctl -u appo -n 50
```

### Error: "Static files no se cargan"
```bash
# Recopilar archivos estáticos de nuevo
cd /var/www/appo.com.co
source venv/bin/activate
python manage.py collectstatic --noinput

# Verificar permisos
sudo chown -R $USER:$USER staticfiles/
```

## 📝 Notas Importantes

1. **Puerto 8000**: La aplicación corre en `127.0.0.1:8000` (solo localhost), Nginx hace el proxy
2. **Base de datos**: Se crea automáticamente con el nombre y usuario especificados en `.env`
3. **SSL**: Se configura automáticamente con Let's Encrypt
4. **Servicio systemd**: Gunicorn se ejecuta como servicio del sistema, se reinicia automáticamente
5. **Logs**: Se guardan en `/var/www/appo.com.co/logs/` y también en journalctl

## 🔐 Seguridad

- ✅ El archivo `.env` NO debe subirse a Git (ya está en `.gitignore`)
- ✅ PostgreSQL solo acepta conexiones locales
- ✅ Redis solo acepta conexiones locales
- ✅ Gunicorn solo escucha en localhost
- ✅ SSL configurado con certificados válidos
- ✅ HSTS habilitado

## 📞 Soporte

Si encuentras problemas, revisa los logs y verifica:
1. Que todos los servicios estén corriendo
2. Que las variables de entorno estén correctas
3. Que los permisos de archivos sean correctos
4. Que el dominio apunte correctamente a la VPS

