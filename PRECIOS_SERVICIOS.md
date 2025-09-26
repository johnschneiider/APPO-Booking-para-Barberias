# Gestión de Precios de Servicios - Negocios

## Resumen
Se ha implementado la funcionalidad para que los negocios puedan asignar precios a sus servicios en la página de edición del negocio.

## Funcionalidades Implementadas

### 1. Campos de Precio y Duración
- **Duración**: Campo numérico en minutos (1-480)
- **Precio**: Campo numérico en pesos con decimales (opcional)

### 2. Interfaz de Usuario Mejorada

#### Vista de Cards
Cada servicio se muestra en una card individual con:
```
┌─────────────────────────────┐
│ ☑️ Nombre del Servicio      │ ← Checkbox + Nombre
├─────────────────────────────┤
│ ⏰ Duración: [30] min       │ ← Campo duración
│ 💰 Precio: $[1500.00]      │ ← Campo precio
└─────────────────────────────┘
```

#### Características Visuales
- **Cards Responsive**: Se adaptan a diferentes tamaños de pantalla
- **Hover Effects**: Animación suave al pasar el mouse
- **Input Groups**: Campos con iconos y unidades
- **Validación**: Campos con restricciones apropiadas

### 3. Campos de Entrada

#### Duración
- **Tipo**: `number`
- **Rango**: 1-480 minutos
- **Unidad**: minutos
- **Icono**: ⏰ (reloj)

#### Precio
- **Tipo**: `number`
- **Rango**: 0+ (con decimales)
- **Unidad**: pesos ($)
- **Icono**: 💰 (moneda)
- **Opcional**: Puede dejarse vacío

### 4. Procesamiento de Datos

#### Lógica de Guardado
```python
# Actualizar duración
nueva_duracion = request.POST.get(f'duracion_{sn.id}')
if nueva_duracion:
    try:
        sn.duracion = int(nueva_duracion)
    except ValueError:
        pass

# Actualizar precio
nuevo_precio = request.POST.get(f'precio_{sn.id}')
if nuevo_precio:
    try:
        if nuevo_precio.strip():  # Solo si no está vacío
            sn.precio = float(nuevo_precio)
        else:
            sn.precio = None  # Si está vacío, establecer como None
    except ValueError:
        pass  # Si no es un número válido, mantener el precio actual
```

#### Validaciones
- **Duración**: Debe ser un entero entre 1 y 480
- **Precio**: Debe ser un número válido (puede ser decimal)
- **Campos Vacíos**: Se manejan apropiadamente

### 5. Modelo de Datos

#### ServicioNegocio
```python
class ServicioNegocio(models.Model):
    negocio = models.ForeignKey('Negocio', on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    duracion = models.PositiveIntegerField(default=30, help_text='Duración en minutos')
    precio = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    activo = models.BooleanField(default=True)
```

### 6. Responsive Design

#### Breakpoints
- **Desktop (>768px)**: 3 columnas por fila
- **Tablet (576px-768px)**: 2 columnas por fila
- **Mobile (<576px)**: 1 columna por fila

#### Optimizaciones Móviles
- Cards más compactas en pantallas pequeñas
- Campos de entrada optimizados para touch
- Texto escalable según tamaño de pantalla

### 7. Estilos CSS

#### Clases Principales
```css
.servicio-card          /* Card principal del servicio */
.servicio-card:hover    /* Efecto hover */
.input-group-sm        /* Grupos de entrada pequeños */
.form-check-label      /* Etiqueta del checkbox */
```

#### Animaciones
- Transición suave en hover
- Transformación translateY(-2px)
- Sombra dinámica

### 8. Funcionalidades Adicionales

#### Información Contextual
- Texto de ayuda explicativo
- Iconos informativos
- Tooltips en campos

#### Validación en Tiempo Real
- Campos con restricciones HTML5
- Validación del lado del servidor
- Manejo de errores apropiado

### 9. Flujo de Trabajo

#### Para el Negocio
1. Acceder a "Editar Negocio"
2. Navegar a la sección "Servicios"
3. Seleccionar servicios activos
4. Configurar duración para cada servicio
5. Asignar precio (opcional)
6. Guardar cambios

#### Para el Sistema
1. Procesar formulario POST
2. Validar datos de entrada
3. Actualizar registros de ServicioNegocio
4. Manejar errores apropiadamente
5. Mostrar mensaje de éxito

### 10. Casos de Uso

#### Escenarios Comunes
- **Nuevo Servicio**: Agregar servicio con precio y duración
- **Actualizar Precio**: Modificar precio existente
- **Desactivar Servicio**: Marcar como inactivo
- **Servicio Sin Precio**: Dejar campo precio vacío

#### Validaciones Específicas
- Precio no puede ser negativo
- Duración debe ser razonable (1-480 min)
- Campos vacíos se manejan como None

### 11. Beneficios

#### Para el Negocio
- **Control Total**: Gestionar precios y duraciones
- **Flexibilidad**: Precios opcionales
- **Claridad**: Interfaz intuitiva y organizada

#### Para el Sistema
- **Datos Estructurados**: Información organizada
- **Escalabilidad**: Fácil agregar más campos
- **Mantenibilidad**: Código limpio y documentado

### 12. Próximas Mejoras Posibles

#### Funcionalidades Futuras
- **Descuentos**: Porcentajes de descuento
- **Precios Variables**: Según día/hora
- **Paquetes**: Combinaciones de servicios
- **Monedas**: Soporte para diferentes monedas

#### Mejoras Técnicas
- **Validación AJAX**: En tiempo real
- **Autoguardado**: Guardar automáticamente
- **Historial**: Versiones de precios
- **Exportación**: Reportes de precios

## Resultado Final
Los negocios ahora pueden gestionar completamente sus servicios con precios y duraciones personalizadas, proporcionando una experiencia de usuario mejorada y datos más completos para el sistema de reservas. 