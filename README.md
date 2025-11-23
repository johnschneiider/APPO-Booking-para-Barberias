# APPO - Sistema de Reservas

## 🚀 Despliegue en VPS

El proyecto está configurado para desplegarse directamente en una VPS sin Docker, usando PostgreSQL y Redis del sistema.

### Despliegue Rápido en VPS

```bash
# Ejecutar script de despliegue
./deploy_vps.sh
```

El script automáticamente:
1. ✅ **Instala dependencias**: PostgreSQL, Redis, Python, Nginx
2. ✅ **Configura base de datos**: Crea usuario y base de datos PostgreSQL
3. ✅ **Instala dependencias Python**: Crea venv e instala requirements
4. ✅ **Configura variables de entorno**: Crea archivo .env
5. ✅ **Aplica migraciones**: Crea todas las tablas necesarias
6. ✅ **Recopila archivos estáticos**: Prepara archivos estáticos
7. ✅ **Configura Nginx**: Configura proxy reverso
8. ✅ **Configura SSL**: Obtiene certificados Let's Encrypt
9. ✅ **Crea servicio systemd**: Configura Gunicorn como servicio

## 📁 Estructura del Proyecto

```
melissa/
├── deploy_vps.sh              # Script de despliegue para VPS
├── sync_vps.sh                # Script para sincronizar cambios
├── nginx-appo.conf            # Configuración de Nginx
├── staticfiles/                # Archivos estáticos
├── media/                      # Archivos de medios
├── env_vps_production.txt     # Plantilla de variables de entorno
└── README.md                   # Este archivo
```

## 🛠️ Comandos Útiles

```bash
# Despliegue completo en VPS
./deploy_vps.sh

# Sincronizar cambios desde GitHub
./sync_vps.sh

# Verificar despliegue
./verificar_despliegue_vps.sh

# Ver logs del servicio
sudo journalctl -u appo -f

# Reiniciar servicio
sudo systemctl restart appo

# Verificar estado del servicio
sudo systemctl status appo

# Crear superusuario
./crear_superusuario.sh admin admin@appo.com.co 1234
```

## 🌐 URLs del Sistema

- **Sitio principal**: https://appo.com.co
- **Admin**: https://appo.com.co/admin/
- **API**: https://appo.com.co/api/

## 📋 Requisitos

- VPS con Debian/Ubuntu
- Acceso root o sudo
- Dominio apuntando al servidor (appo.com.co → IP del servidor)
- PostgreSQL instalado (o se instalará automáticamente)
- Redis instalado (o se instalará automáticamente)
- Python 3.8+
- Nginx instalado (o se instalará automáticamente)

## 🔐 Configuración SSL

El sistema obtiene certificados SSL automáticamente usando Let's Encrypt:
- Certificados válidos por 90 días
- Renovación automática configurada
- HSTS habilitado
- Configuración SSL moderna

## 🚨 Solución de Problemas

### Si el deploy falla:

1. **Verificar logs**: `sudo journalctl -u appo -n 100`
2. **Verificar Nginx**: `sudo nginx -t`
3. **Verificar PostgreSQL**: `sudo systemctl status postgresql`
4. **Verificar Redis**: `sudo systemctl status redis-server`
5. **Reintentar**: `./deploy_vps.sh`

### Problemas comunes:

- **Puerto 80 ocupado**: Verificar con `sudo ss -tlnp | grep :80`
- **Dominio no apunta**: Verificar DNS antes del deploy
- **Certificados SSL**: Se obtienen automáticamente con Certbot
- **Base de datos**: Se configura automáticamente en el script

## 📝 Notas Importantes

- **Sin Docker**: El proyecto usa servicios del sistema directamente
- **PostgreSQL del sistema**: Base de datos instalada en el servidor
- **Redis del sistema**: Cache instalado en el servidor
- **Gunicorn como servicio**: Se ejecuta como servicio systemd
- **Nginx compartido**: Puede compartir puertos 80/443 con otros proyectos

## 🔧 Configuración de Producción

### Variables de Entorno

El sistema usa variables de entorno para configuración segura:
- `SECRET_KEY`: Generada automáticamente
- `DEBUG=False`: Para producción
- `ALLOWED_HOSTS`: Dominios permitidos
- `POSTGRES_DB`: Nombre de la base de datos
- `POSTGRES_USER`: Usuario de PostgreSQL
- `POSTGRES_PASSWORD`: Contraseña de PostgreSQL
- `POSTGRES_HOST`: Host de PostgreSQL (localhost)
- `REDIS_URL`: URL de Redis (opcional)

### Servicios del Sistema

- **Gunicorn**: Servidor WSGI (3 workers)
- **PostgreSQL**: Base de datos del sistema
- **Redis**: Cache del sistema
- **Nginx**: Servidor web (puertos 80, 443)

## 🛡️ Seguridad

### Firewall
- Puerto 80 (HTTP) abierto
- Puerto 443 (HTTPS) abierto
- Puerto 22 (SSH) abierto

### SSL/TLS
- Certificados Let's Encrypt automáticos
- HSTS habilitado
- Configuración SSL moderna
- Redirección HTTP → HTTPS

### Base de Datos
- PostgreSQL con usuario específico
- Contraseñas seguras
- Solo conexiones locales permitidas

## 📊 Monitoreo

### Logs
- `sudo journalctl -u appo`: Logs de Gunicorn
- `/var/log/nginx/`: Logs de Nginx
- `/var/log/postgresql/`: Logs de PostgreSQL

---

**El sistema está diseñado para desplegarse directamente en VPS sin Docker. Usa `./deploy_vps.sh` para un despliegue completo.**
