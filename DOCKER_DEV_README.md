# 🐳 Docker Development Setup

## 🚀 Inicio Rápido

### 1. Iniciar Docker en modo desarrollo
```bash
docker compose up -d
```

### 2. Acceder a la aplicación
- **URL Principal**: http://localhost:8080
- **Puerto**: 8080 (en lugar de 80 para evitar conflictos)

### 3. Verificar estado
```bash
docker compose ps
```

## 🔧 Comandos Útiles

### Ver logs
```bash
# Todos los servicios
docker compose logs

# Solo nginx
docker compose logs nginx

# Solo web (Django)
docker compose logs web

# Solo base de datos
docker compose logs db

# Solo Redis
docker compose logs redis
```

### Reiniciar servicios
```bash
# Reiniciar todo
docker compose restart

# Reiniciar solo nginx
docker compose restart nginx

# Reiniciar solo web
docker compose restart web
```

### Detener servicios
```bash
# Detener todo
docker compose down

# Detener y limpiar volúmenes
docker compose down --volumes
```

## 📁 Archivos de Configuración

- **nginx-dev.conf**: Configuración de nginx para desarrollo (sin SSL)
- **nginx.conf**: Configuración de nginx para producción (con SSL)

## 🐛 Solución de Problemas

### Nginx no inicia
- Verificar que no hay conflictos de puertos
- Revisar logs: `docker compose logs nginx`

### Imágenes no cargan
- Verificar que los volúmenes están montados correctamente
- Revisar permisos de archivos en `media/` y `staticfiles/`

### Base de datos no conecta
- Verificar que PostgreSQL está iniciado: `docker compose logs db`
- Revisar variables de entorno en `.env`

## 🌐 URLs de Acceso

- **Aplicación Principal**: http://localhost:8080
- **Admin Django**: http://localhost:8080/admin/
- **API Health Check**: http://localhost:8080/health/

## 📝 Notas Importantes

1. **Puerto 8080**: Se usa para evitar conflictos con otros servicios
2. **Sin SSL**: La configuración de desarrollo no incluye certificados SSL
3. **Volúmenes**: Los archivos `media/` y `staticfiles/` se montan desde el host
4. **Logs**: Se guardan en la carpeta `logs/` del proyecto
