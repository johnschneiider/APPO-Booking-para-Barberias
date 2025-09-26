# Sistema de Suscripciones - Melissa

## Descripción

El sistema de suscripciones permite a los negocios crear planes mensuales para que los clientes se suscriban, generando ingresos recurrentes y fidelizando a la clientela.

## Características Principales

### Para Negocios
- **Gestión de Planes**: Crear, editar y eliminar planes de suscripción
- **Dashboard de Suscripciones**: Métricas y estadísticas en tiempo real
- **Gestión de Suscriptores**: Ver, renovar y gestionar suscripciones activas
- **Beneficios Personalizables**: Agregar beneficios específicos a cada plan
- **Imágenes de Planes**: Subir imágenes representativas para cada plan

### Para Clientes
- **Explorar Planes**: Ver todos los planes disponibles de diferentes negocios
- **Filtros Avanzados**: Buscar por categoría, ubicación, precio y duración
- **Suscripción Fácil**: Proceso simplificado de suscripción
- **Gestión de Suscripciones**: Ver, renovar y cancelar suscripciones activas
- **Historial Completo**: Acceso al historial de suscripciones y pagos

## Estructura del Proyecto

```
suscripciones/
├── templates/
│   ├── base_suscripciones.html          # Plantilla base
│   ├── negocio_suscripciones.html       # Vista de suscripciones del negocio
│   ├── planes_negocio.html              # Gestión de planes del negocio
│   ├── plan_suscripcion_form.html       # Formulario de planes
│   ├── cliente_suscripciones.html       # Suscripciones del cliente
│   ├── planes_disponibles.html          # Planes disponibles para clientes
│   └── dashboard_suscripciones.html     # Dashboard del negocio
├── static/
│   ├── css/
│   │   └── suscripciones.css            # Estilos principales
│   └── js/
│       └── suscripciones.js             # Funcionalidades JavaScript
├── models.py                            # Modelos de datos
├── views.py                             # Lógica de negocio
├── forms.py                             # Formularios
├── urls.py                              # Configuración de URLs
└── admin.py                             # Configuración del admin
```

## Modelos Principales

### PlanSuscripcion
- **nombre**: Nombre del plan
- **descripcion**: Descripción detallada
- **precio_mensual**: Precio mensual en pesos
- **duracion_meses**: Duración del plan (1-12 meses)
- **max_suscripciones**: Límite de suscriptores (opcional)
- **activo**: Estado del plan
- **destacado**: Plan destacado en búsquedas
- **imagen**: Imagen representativa del plan

### Suscripcion
- **cliente**: Usuario que se suscribe
- **negocio**: Negocio al que se suscribe
- **plan**: Plan seleccionado
- **fecha_inicio**: Fecha de inicio
- **fecha_vencimiento**: Fecha de vencimiento
- **estado**: Estado actual (activa, vencida, cancelada, etc.)

### BeneficioSuscripcion
- **plan**: Plan al que pertenece
- **nombre**: Nombre del beneficio
- **descripcion**: Descripción detallada
- **tipo_beneficio**: Categoría del beneficio
- **valor**: Valor o descripción del beneficio
- **activo**: Estado del beneficio

## URLs Principales

### Negocios
- `/suscripciones/negocio/planes/` - Gestión de planes
- `/suscripciones/negocio/planes/crear/` - Crear nuevo plan
- `/suscripciones/negocio/planes/<id>/editar/` - Editar plan
- `/suscripciones/negocio/suscripciones/` - Ver suscripciones
- `/suscripciones/negocio/dashboard/` - Dashboard de suscripciones

### Clientes
- `/suscripciones/cliente/suscripciones/` - Mis suscripciones
- `/suscripciones/planes/disponibles/` - Planes disponibles
- `/suscripciones/suscribirse/<id>/` - Suscribirse a un plan

### API
- `/suscripciones/api/suscripcion/<id>/detalles/` - Detalles de suscripción
- `/suscripciones/api/suscripcion/<id>/renovar/` - Renovar suscripción
- `/suscripciones/api/plan/<id>/detalles/` - Detalles del plan
- `/suscripciones/api/plan/<id>/eliminar/` - Eliminar plan

## Funcionalidades JavaScript

### Filtros y Búsqueda
- Filtrado por estado, plan y texto
- Búsqueda avanzada con múltiples criterios
- Ordenamiento por diferentes parámetros

### Gestión de Planes
- Crear y editar planes
- Agregar/eliminar beneficios
- Subir imágenes
- Activar/desactivar planes

### Gestión de Suscripciones
- Ver detalles completos
- Renovar suscripciones
- Enviar recordatorios
- Cancelar suscripciones

### Dashboard
- Gráficos de evolución
- Estadísticas en tiempo real
- Alertas y notificaciones
- Exportación de datos

## Estilos CSS

### Diseño Responsivo
- Grid system adaptable
- Breakpoints para móvil, tablet y desktop
- Componentes flexibles

### Tema Visual
- Gradientes modernos
- Sombras y efectos hover
- Iconografía FontAwesome
- Paleta de colores consistente

### Componentes
- Tarjetas de estadísticas
- Tablas responsivas
- Modales Bootstrap
- Formularios estilizados

## Integración con el Sistema

### Dashboard del Negocio
- KPIs de suscripciones integrados
- Enlaces directos a gestión
- Métricas en tiempo real

### Navegación
- Menú de suscripciones en el panel del negocio
- Acceso rápido desde el dashboard principal
- Breadcrumbs y navegación contextual

### Permisos
- Verificación de propiedad del negocio
- Acceso diferenciado por tipo de usuario
- Validaciones de seguridad

## Configuración

### Settings
```python
INSTALLED_APPS = [
    ...
    'suscripciones',
]

# Configuración de medios para imágenes
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### URLs del Proyecto
```python
urlpatterns = [
    ...
    path('suscripciones/', include('suscripciones.urls')),
]
```

### Migraciones
```bash
python manage.py makemigrations suscripciones
python manage.py migrate
```

## Uso

### Para Negocios
1. Acceder al dashboard del negocio
2. Ir a la sección de suscripciones
3. Crear planes atractivos con beneficios claros
4. Gestionar suscriptores activos
5. Monitorear métricas y crecimiento

### Para Clientes
1. Explorar planes disponibles
2. Aplicar filtros según preferencias
3. Suscribirse al plan deseado
4. Gestionar suscripción activa
5. Renovar o cancelar según necesidad

## Personalización

### Temas Visuales
- Modificar variables CSS en `suscripciones.css`
- Ajustar colores y gradientes
- Personalizar iconos y tipografía

### Funcionalidades
- Extender modelos con campos adicionales
- Agregar nuevos tipos de beneficios
- Implementar sistemas de pagos específicos

### Integraciones
- Conectar con sistemas de facturación
- Integrar con pasarelas de pago
- Conectar con sistemas de email marketing

## Mantenimiento

### Tareas Programadas
- Verificación diaria de suscripciones vencidas
- Envío de recordatorios automáticos
- Limpieza de datos obsoletos

### Monitoreo
- Logs de actividad del sistema
- Métricas de rendimiento
- Alertas de errores críticos

### Backup
- Respaldo regular de la base de datos
- Versionado de plantillas y archivos estáticos
- Documentación de cambios

## Soporte

### Documentación
- Este README
- Comentarios en el código
- Docstrings de funciones

### Contacto
- Equipo de desarrollo
- Sistema de tickets
- Base de conocimientos

---

**Desarrollado para Melissa - Sistema de Gestión de Negocios de Belleza**
