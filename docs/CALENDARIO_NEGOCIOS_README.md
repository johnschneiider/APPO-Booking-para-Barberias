# 📅 Calendario de Negocios - Implementación Completa

## 🎯 **Descripción General**

El calendario de negocios es una interfaz moderna y funcional que permite a los propietarios de negocios visualizar y gestionar las reservas de sus profesionales en tiempo real. El diseño está basado en una imagen de referencia que muestra un layout limpio con tiempo en el eje Y y profesionales en columnas.

## ✨ **Características Principales**

### 🕐 **Vista de Tiempo**
- **Intervalos de 1 hora** (8:00 AM - 8:00 PM)
- **Eje Y**: Horarios claramente marcados
- **Columnas**: Un profesional por columna
- **Scroll vertical**: Para ver más horarios

### 👥 **Gestión de Profesionales**
- **Headers personalizados** con fotos de perfil
- **Avatares por defecto** para profesionales sin foto
- **Estado de disponibilidad** visible
- **Filtros por profesional**

### 🎨 **Diseño Visual**
- **Header de navegación** con botones específicos:
  - Botón "Hoy" (redondeado)
  - Navegación por días (flechas izquierda/derecha)
  - Fecha central (formato: "mié 13 ago")
  - Iconos de gestión (personas, filtros)
  - Botones de acción (configuración, calendario, refresh)
  - Dropdown de vista (Día/Semana/Mes)
  - Botón "Añadir" (negro con dropdown)
- **Sidebar colapsable** con filtros y estadísticas
- **Colores por estado** de reserva

## 🚀 **Cómo Acceder**

1. **Iniciar sesión** como usuario tipo "negocio"
2. **Hacer clic** en el icono de usuario en `base.html`
3. **Seleccionar** "Calendario" del menú desplegable
4. **URL**: `/negocios/{negocio_id}/calendario/`

## 🛠 **Tecnologías Utilizadas**

- **Frontend**: FullCalendar 6.1.10 con plugins de recursos
- **Backend**: Django con APIs REST
- **Estilos**: CSS personalizado con variables CSS
- **Responsive**: Bootstrap 5 + Media queries
- **Iconos**: Bootstrap Icons

## 📁 **Archivos Implementados**

### **Template Principal**
- `negocios/templates/negocios/calendario.html`
  - Header de navegación personalizado
  - Integración con FullCalendar
  - **Sistema de fallback** para mostrar calendario básico
  - Modales para detalles y gestión
  - Filtros en sidebar

### **Estilos CSS**
- `static/css/negocios/calendario.css`
  - Variables de color personalizadas
  - Estilos para recursos (profesionales)
  - **Estilos para calendario fallback**
  - Responsive design
  - Animaciones y transiciones

### **Backend APIs**
- `negocios/views.py`
  - `calendario_reservas()`: Renderiza la vista principal
  - `api_reservas_negocio()`: Obtiene reservas con filtros
  - `api_estadisticas_negocio()`: Estadísticas diarias
  - `api_usuarios_negocio()`: Lista de profesionales

### **Navegación**
- `templates/base.html`
  - Enlace "Calendario" en menú de usuario
  - Solo visible para usuarios tipo negocio

## 🔧 **Configuración de FullCalendar**

```javascript
calendar = new FullCalendar.Calendar(document.getElementById('calendario'), {
    initialView: 'resourceTimeGridDay',
    locale: 'es',
    headerToolbar: false, // Toolbar personalizada
    height: 'auto',
    slotMinTime: '08:00:00',
    slotMaxTime: '20:00:00',
    slotDuration: '01:00:00', // Intervalos de 1 hora
    resources: recursos, // Profesionales como recursos
    events: cargarReservas, // Carga dinámica de reservas
    resourceLabelDidMount: personalizarHeaderRecurso,
    slotLabelDidMount: personalizarEtiquetasTiempo,
    resourceAreaWidth: '200px', // Ancho fijo para columnas
    slotMinWidth: 100, // Ancho mínimo de columnas de tiempo
    expandRows: true // Expandir filas
});
```

## 🆘 **Sistema de Fallback**

Si FullCalendar no se carga correctamente, el sistema muestra un **calendario básico HTML** que garantiza que siempre se vean los profesionales en columnas:

### **Características del Fallback:**
- **Grid HTML puro** con CSS flexbox
- **Columnas de profesionales** con avatares
- **Filas de tiempo** de 8:00 AM a 8:00 PM
- **Responsive design** para móviles
- **Estilos consistentes** con el tema principal

### **Cuándo se Activa:**
1. **FullCalendar no está disponible**
2. **Error en la inicialización**
3. **Problemas de carga de recursos**

## 📊 **Estructura de Datos**

### **Recursos (Profesionales)**
```json
{
    "id": "prof_123",
    "title": "Johnes Jimenez",
    "tipo": "profesional",
    "color": "#3788d8"
}
```

### **Eventos (Reservas)**
```json
{
    "id": "456",
    "title": "Cliente - Servicio",
    "start": "2024-01-15T11:30:00",
    "end": "2024-01-15T12:30:00",
    "resourceId": "prof_123",
    "backgroundColor": "#28a745",
    "extendedProps": {
        "estado": "confirmada",
        "cliente_nombre": "Cliente",
        "servicio_nombre": "Corte",
        "profesional_nombre": "Johnes Jimenez",
        "precio": 25.00
    }
}
```

## 🎨 **Sistema de Colores**

- **Confirmada**: Verde (#28a745)
- **Pendiente**: Amarillo (#ffc107)
- **Completada**: Azul (#17a2b8)
- **Cancelada**: Rojo (#dc3545)
- **No Show**: Gris (#6c757d)

## 📱 **Responsive Design**

- **Desktop**: Layout completo con sidebar
- **Tablet**: Sidebar colapsable
- **Mobile**: Navegación vertical, botones apilados

## 🔄 **Funcionalidades en Tiempo Real**

### **Filtros Activos**
- **Por fecha**: Selector de fecha
- **Por profesional**: Dropdown de profesionales
- **Por estado**: Filtro de estados de reserva

### **Navegación**
- **Botón "Hoy"**: Regresa a la fecha actual
- **Flechas**: Navegación por días
- **Vistas**: Día, Semana, Mes
- **Refresh**: Actualiza datos

### **Gestión**
- **Ver detalles**: Click en reserva
- **Gestionar profesionales**: Modal de gestión
- **Estadísticas**: Métricas diarias actualizadas

## 🚀 **APIs Endpoints**

### **GET** `/negocios/{id}/api/reservas/`
- **Parámetros**: `start`, `end` (fechas)
- **Retorna**: Lista de reservas con metadatos

### **GET** `/negocios/{id}/api/estadisticas/`
- **Parámetros**: `fecha` (YYYY-MM-DD)
- **Retorna**: Estadísticas del día

### **GET** `/negocios/{id}/api/usuarios/`
- **Retorna**: Lista de profesionales activos

## 🔮 **Mejoras Futuras**

1. **Drag & Drop**: Mover reservas entre horarios
2. **Crear reservas**: Desde el calendario
3. **Notificaciones**: Alertas en tiempo real
4. **Exportar**: PDF, Excel del calendario
5. **Sincronización**: Con Google Calendar, Outlook
6. **Temas**: Modo oscuro/claro

## 🐛 **Solución de Problemas**

### **Calendario no carga**
- Verificar que FullCalendar esté incluido
- Revisar consola del navegador
- Confirmar que las APIs respondan
- **El sistema fallback se activará automáticamente**

### **Profesionales no aparecen**
- Verificar que tengan `Matriculacion.estado = 'aprobada'`
- Confirmar que `Profesional.disponible = True`
- Revisar logs de la API
- **Se mostrará mensaje "Sin Profesionales"**

### **Reservas no se muestran**
- Verificar formato de fecha en la API
- Confirmar que `Reserva.profesional` esté asignado
- Revisar permisos de usuario

## 📝 **Notas de Implementación**

- **Intervalos de 1 hora**: Configurado en `slotDuration: '01:00:00'`
- **Headers personalizados**: Implementado en `resourceLabelDidMount`
- **Navegación personalizada**: Toolbar oculta, botones personalizados
- **Sistema de fallback**: Garantiza visualización siempre
- **Responsive**: CSS con breakpoints específicos
- **Accesibilidad**: Alt text en imágenes, contraste adecuado

## 🔍 **Debug y Logging**

El sistema incluye logging extensivo para facilitar la depuración:

```javascript
console.log('DOM cargado, iniciando calendario...');
console.log('Recursos cargados:', recursos);
console.log('FullCalendar disponible, creando calendario...');
console.log('Calendario renderizado exitosamente');
```

## 📋 **Requisitos del Sistema**

### **Frontend:**
- Navegador moderno con soporte ES6+
- Conexión a internet para CDN de FullCalendar
- JavaScript habilitado

### **Backend:**
- Django 4.x+
- Base de datos con soporte para relaciones
- Usuarios autenticados tipo "negocio"

---

**Estado**: ✅ **Implementado y Funcional con Sistema de Fallback**
**Última actualización**: Enero 2025
**Versión**: 2.1 (Con sistema de fallback garantizado)
**Característica destacada**: **Siempre muestra profesionales en columnas**
