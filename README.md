# APPO - Sistema de Reservas

## 🚀 Despliegue Automático

El proyecto incluye un sistema de despliegue completamente automático que maneja todos los problemas comunes.

### Despliegue Rápido

```bash
# Solo ejecuta esto:
./deploy.sh
```

El script automáticamente:
1. ✅ **Diagnóstico completo**: Verifica archivos, volúmenes, configuración y logs
2. ✅ **Corrección automática**: Arregla problemas de Nginx, volúmenes y SSL
3. ✅ **Configuración progresiva**: HTTP → SSL → HTTPS
4. ✅ **Despliegue completo**: Base de datos, migraciones, certificados SSL

## 🔧 Problemas Comunes y Soluciones

### Error: "Nginx no funciona correctamente"

**Causa**: Conflictos de configuración, volúmenes no mapeados, certificados SSL faltantes.

**Solución**: El `deploy.sh` lo corrige automáticamente:
- Detecta problemas de volúmenes
- Corrige configuración de Nginx
- Prueba configuraciones progresivamente
- Configura SSL automáticamente

### Error: "Archivo no existe dentro del contenedor"

**Causa**: Volumen no mapeado correctamente.

**Solución**: Automática en `deploy.sh`:
- Verifica mapeo de volúmenes
- Agrega volumen si falta
- Crea configuración mínima para pruebas

## 📁 Estructura del Proyecto

```
melissa/
├── deploy.sh                    # Despliegue automático completo
├── docker-compose.yml           # Configuración de servicios
├── nginx/
│   ├── nginx.conf              # Configuración principal
│   ├── ssl.conf                # Configuración SSL inicial
│   ├── ssl_simple.conf         # Configuración simplificada
│   └── ssl_minimal.conf        # Configuración mínima
├── certbot/www/                # Archivos de validación SSL
├── logs/                       # Directorio de logs
├── staticfiles/                # Archivos estáticos
├── media/                      # Archivos de medios
├── env_production.txt          # Variables de entorno para producción
└── README.md                   # Este archivo
```

## 🛠️ Comandos Útiles

```bash
# Despliegue completo
./deploy.sh

# Verificar despliegue
./verificar_despliegue.sh

# Ver logs
docker compose logs nginx

# Reiniciar servicios
docker compose restart

# Verificar estado
docker compose ps

# Crear superusuario
docker compose exec web python manage.py createsuperuser
```

## 🔍 Verificación

Para verificar que todo funciona:

```bash
# Localmente
curl http://localhost/.well-known/acme-challenge/test.txt

# Desde el dominio
curl http://appo.com.co/.well-known/acme-challenge/test.txt
```

Ambos deben devolver `test-appo`.

## 🌐 URLs del Sistema

- **Sitio principal**: https://appo.com.co
- **Admin**: https://appo.com.co/admin/
- **API**: https://appo.com.co/api/

## 📋 Requisitos

- Docker y Docker Compose
- Dominio apuntando al servidor (appo.com.co → 92.113.39.100)
- Puerto 80 libre
- Acceso root al servidor
- VPS Debian

## 🔐 Configuración SSL

El sistema obtiene certificados SSL automáticamente usando Let's Encrypt:
- Certificados válidos por 90 días
- Renovación automática configurada
- HSTS habilitado
- Configuración SSL moderna

## 🚨 Solución de Problemas

### Si el deploy falla:

1. **Verificar logs**: `docker compose logs nginx`
2. **Verificar volúmenes**: `docker compose exec nginx ls -la /var/www/certbot/`
3. **Verificar configuración**: `docker compose exec nginx nginx -t`
4. **Reintentar**: `./deploy.sh`

### Problemas comunes:

- **Puerto 80 ocupado**: El script lo libera automáticamente
- **Dominio no apunta**: Verificar DNS antes del deploy
- **Certificados SSL**: Se obtienen automáticamente
- **Base de datos**: Se configura automáticamente

## 📝 Notas Importantes

- **Completamente automático**: No requiere intervención manual
- **Diagnóstico automático**: Detecta y corrige problemas
- **Configuración progresiva**: HTTP → SSL → HTTPS
- **Sin conflictos**: Un solo bloque server por puerto
- **Volumen correcto**: Mapeo automático de certbot
- **Variables de entorno**: Configuración segura para producción
- **Logs organizados**: Directorios separados para cada servicio
- **Health checks**: Monitoreo automático de servicios

## 🎯 Flujo del Despliegue

1. **Diagnóstico**: Verifica todo automáticamente
2. **Corrección**: Arregla problemas si los encuentra
3. **Configuración**: HTTP inicial → SSL → HTTPS
4. **Verificación**: Asegura que todo funcione
5. **Despliegue**: Servicios completos con SSL

## 🔧 Configuración de Producción

### Variables de Entorno
El sistema usa variables de entorno para configuración segura:
- `SECRET_KEY`: Generada automáticamente
- `DEBUG=False`: Para producción
- `ALLOWED_HOSTS`: Dominios permitidos
- `DATABASE_URL`: Conexión a PostgreSQL
- `REDIS_URL`: Conexión a Redis

### Servicios Docker
- **web**: Django + Gunicorn (3 workers)
- **db**: PostgreSQL 15
- **redis**: Redis 7
- **nginx**: Nginx 1.25 (puertos 80, 443)

### Volúmenes
- `pgdata`: Datos de PostgreSQL
- `redis_data`: Datos de Redis
- `./certbot/www:/var/www/certbot`: Certbot files
- `./media:/app/media`: Media files
- `./staticfiles:/app/staticfiles`: Static files
- `./logs:/app/logs`: Logs de aplicación

## 🛡️ Seguridad

### Firewall
- Puerto 80 (HTTP) abierto
- Puerto 443 (HTTPS) abierto
- Puerto 22 (SSH) abierto
- UFW configurado automáticamente

### SSL/TLS
- Certificados Let's Encrypt automáticos
- HSTS habilitado
- Configuración SSL moderna
- Redirección HTTP → HTTPS

### Base de Datos
- PostgreSQL con usuario específico
- Contraseñas seguras
- Volúmenes persistentes
- Health checks automáticos

## 📊 Monitoreo

### Health Checks
- Verificación automática de servicios
- Logs organizados por servicio
- Alertas de errores
- Monitoreo de recursos

### Logs
- `logs/nginx/`: Logs de Nginx
- `logs/postgresql/`: Logs de PostgreSQL
- `logs/redis/`: Logs de Redis
- `logs/django/`: Logs de Django

---

**El sistema está diseñado para ser completamente automático. Solo ejecuta `./deploy.sh` y todo se configurará correctamente.** 