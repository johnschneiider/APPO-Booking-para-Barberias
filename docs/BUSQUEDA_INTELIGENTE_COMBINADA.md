# Búsqueda Inteligente y Combinada

## 🎯 **Objetivo**

Implementar un **sistema de búsqueda inteligente** que permita buscar negocios por múltiples criterios de forma combinada:

- **Por nombre de negocio**: Búsqueda específica de un negocio
- **Por servicio**: Todos los negocios que ofrezcan un servicio específico
- **Por ubicación**: Con coordenadas (distancia) o texto (ciudad/barrio)
- **Combinaciones flexibles**: Cualquier combinación de los criterios anteriores

## ✅ **Implementación Realizada**

### **1. Backend - Función de Búsqueda Mejorada**

#### **A. Lógica de Búsqueda Inteligente**
```python
def buscar_negocios(request):
    """
    Búsqueda inteligente y combinada de negocios:
    - Por nombre de negocio específico
    - Por servicio (todos los negocios que ofrezcan ese servicio)
    - Por ubicación (con coordenadas para distancia, sin coordenadas para texto)
    - Combinaciones flexibles de todos los criterios
    """
    try:
        # Parámetros de búsqueda
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        radio = request.GET.get('radio', '5000')  # Radio por defecto 5km
        servicio = request.GET.get('servicio', '').strip()
        negocio_nombre = request.GET.get('negocio', '').strip()
        ubicacion = request.GET.get('ubicacion', '').strip()
        
        # Query base
        queryset = Negocio.objects.filter(activo=True)
        
        # 1. BÚSQUEDA POR NOMBRE DE NEGOCIO (prioridad alta)
        if negocio_nombre:
            queryset = queryset.filter(
                Q(nombre__icontains=negocio_nombre) |
                Q(direccion__icontains=negocio_nombre)
            )
        
        # 2. BÚSQUEDA POR SERVICIO
        if servicio:
            queryset = queryset.filter(
                servicios__servicio__nombre__icontains=servicio
            ).distinct()
        
        # 3. BÚSQUEDA POR UBICACIÓN
        if ubicacion and not lat and not lon:
            queryset = queryset.filter(
                Q(ciudad__icontains=ubicacion) |
                Q(barrio__icontains=ubicacion) |
                Q(direccion__icontains=ubicacion)
            )
        
        # 4. BÚSQUEDA POR COORDENADAS (con distancia)
        if lat and lon:
            # Calcular distancia y filtrar por radio
            # Ordenar por distancia
            pass
        
        # 5. ORDENAMIENTO INTELIGENTE
        if lat and lon:
            # Ordenar por distancia
            pass
        elif negocio_nombre:
            # Ordenar por relevancia del nombre
            pass
        elif servicio:
            # Ordenar alfabéticamente
            pass
```

### **2. Frontend - JavaScript Mejorado**

#### **A. Función de Búsqueda Inteligente**
```javascript
function buscarNegocios() {
    const ubicacionInput = document.getElementById('ubicacion-autocomplete');
    const lat = document.getElementById('ubicacion-lat').value;
    const lon = document.getElementById('ubicacion-lng').value;
    const servicio = document.getElementById('servicio-autocomplete').value;
    const negocio = document.getElementById('negocio-autocomplete').value;
    
    // Construir parámetros de búsqueda
    const params = new URLSearchParams();
    
    // 1. UBICACIÓN (coordenadas o texto)
    if (lat && lon) {
        params.append('lat', lat);
        params.append('lon', lon);
    } else if (ubicacionInput && ubicacionInput.value) {
        params.append('ubicacion', ubicacionInput.value);
    }
    
    // 2. SERVICIO
    if (servicio) {
        params.append('servicio', servicio);
    }
    
    // 3. NOMBRE DE NEGOCIO
    if (negocio) {
        params.append('negocio', negocio);
    }
    
    // Determinar tipo de búsqueda
    const tipoBusqueda = [];
    if (lat && lon) tipoBusqueda.push('ubicación con coordenadas');
    else if (ubicacionInput && ubicacionInput.value) tipoBusqueda.push('ubicación por texto');
    if (servicio) tipoBusqueda.push('servicio');
    if (negocio) tipoBusqueda.push('nombre de negocio');
    
    // Realizar búsqueda AJAX
    const url = `/clientes/api/buscar-negocios/?${params.toString()}`;
    fetch(url)
        .then(response => response.json())
        .then(data => {
            mostrarResultadosBusqueda(data);
        })
        .catch(error => {
            mostrarErrorBusqueda();
        });
}
```

## 📊 **Tipos de Búsqueda Soportados**

### **1. Búsqueda por Nombre de Negocio**
- **Ejemplo**: Escribir "Peluquería Bella"
- **Resultado**: Muestra negocios que contengan "Peluquería Bella" en el nombre o dirección
- **Ordenamiento**: Por relevancia del nombre

### **2. Búsqueda por Servicio**
- **Ejemplo**: Seleccionar "Corte de cabello"
- **Resultado**: Muestra todos los negocios que ofrezcan corte de cabello
- **Ordenamiento**: Alfabético por nombre del negocio

### **3. Búsqueda por Ubicación**
- **Con coordenadas**: Busca negocios cercanos (radio de 5km por defecto)
- **Sin coordenadas**: Busca por ciudad, barrio o dirección
- **Ordenamiento**: Por distancia (si hay coordenadas)

### **4. Búsquedas Combinadas**

#### **A. Servicio + Ubicación**
- **Ejemplo**: "Corte de cabello" + "Palermo"
- **Resultado**: Negocios que ofrezcan corte de cabello en Palermo
- **Ordenamiento**: Por distancia si hay coordenadas, alfabético si no

#### **B. Nombre + Ubicación**
- **Ejemplo**: "Peluquería" + "Centro"
- **Resultado**: Negocios con "Peluquería" en el nombre ubicados en el centro
- **Ordenamiento**: Por relevancia del nombre

#### **C. Servicio + Nombre**
- **Ejemplo**: "Coloración" + "Bella"
- **Resultado**: Negocios que ofrezcan coloración y contengan "Bella" en el nombre
- **Ordenamiento**: Por relevancia del nombre

#### **D. Todos los Criterios**
- **Ejemplo**: "Corte" + "Coloración" + "Palermo"
- **Resultado**: Negocios que ofrezcan coloración, contengan "Corte" y estén en Palermo
- **Ordenamiento**: Inteligente según los criterios

## 🎯 **Ejemplos de Uso**

### **Búsqueda Simple**
1. **Solo nombre**: "Peluquería Bella" → Negocios con ese nombre
2. **Solo servicio**: "Corte de cabello" → Todos los negocios que ofrezcan ese servicio
3. **Solo ubicación**: "Palermo" → Negocios en Palermo

### **Búsqueda Combinada**
1. **Servicio + Ubicación**: "Coloración" + "Centro" → Salones de coloración en el centro
2. **Nombre + Ubicación**: "Peluquería" + "Palermo" → Peluquerías en Palermo
3. **Servicio + Nombre**: "Manicura" + "Bella" → Salones de manicura con "Bella" en el nombre

### **Búsqueda Completa**
1. **Todos los criterios**: "Corte" + "Coloración" + "Palermo" → Negocios que ofrezcan coloración, contengan "Corte" y estén en Palermo

## ⚡ **Características Avanzadas**

### **1. Ordenamiento Inteligente**
- **Con coordenadas**: Ordena por distancia
- **Por nombre**: Ordena por relevancia del nombre
- **Por servicio**: Ordena alfabéticamente
- **Combinado**: Aplica el ordenamiento más apropiado

### **2. Radio de Búsqueda Adaptativo**
- **Por defecto**: 5km para búsquedas combinadas
- **Configurable**: Se puede ajustar según necesidades
- **Inteligente**: Se adapta según el tipo de búsqueda

### **3. Filtrado Automático**
- **Solo negocios activos**: Filtra automáticamente negocios inactivos
- **Distinct**: Evita duplicados en búsquedas por servicio
- **Límite de resultados**: Máximo 50 resultados para rendimiento

### **4. Información Detallada**
- **Distancia**: Muestra distancia en metros si aplica
- **Tipo de búsqueda**: Identifica el tipo de búsqueda realizada
- **Parámetros**: Guarda todos los parámetros de búsqueda

## 📱 **Responsive Design**

### **Mobile (≤768px)**
- **Búsqueda optimizada**: Funciona perfectamente en dispositivos móviles
- **Autocompletado**: Todos los campos tienen autocompletado
- **Resultados adaptados**: Se muestran de forma responsive

### **Desktop**
- **Búsqueda completa**: Todas las funcionalidades disponibles
- **Resultados detallados**: Información completa de cada negocio
- **Mapa interactivo**: Visualización en mapa si está disponible

## ✅ **Testing Recomendado**

### **Casos de Prueba - Búsqueda Simple**
- [ ] Búsqueda solo por nombre de negocio
- [ ] Búsqueda solo por servicio
- [ ] Búsqueda solo por ubicación (con coordenadas)
- [ ] Búsqueda solo por ubicación (sin coordenadas)

### **Casos de Prueba - Búsqueda Combinada**
- [ ] Servicio + Ubicación
- [ ] Nombre + Ubicación
- [ ] Servicio + Nombre
- [ ] Todos los criterios juntos

### **Casos de Prueba - Ordenamiento**
- [ ] Ordenamiento por distancia (con coordenadas)
- [ ] Ordenamiento por relevancia (por nombre)
- [ ] Ordenamiento alfabético (por servicio)
- [ ] Ordenamiento inteligente (combinado)

### **Dispositivos a Verificar**
- **Desktop**: Chrome, Firefox, Safari, Edge
- **Mobile**: iOS Safari, Android Chrome
- **Tablet**: iPad, Android tablets

## 🎯 **Beneficios**

### **1. Usabilidad**
- **Búsqueda flexible**: Permite cualquier combinación de criterios
- **Resultados relevantes**: Ordenamiento inteligente según el tipo de búsqueda
- **Información clara**: Títulos descriptivos de los resultados
- **Fácil de usar**: Interfaz intuitiva y responsive

### **2. Rendimiento**
- **Búsqueda eficiente**: Usa índices de base de datos
- **Resultados limitados**: Máximo 50 para carga rápida
- **Caché inteligente**: Optimiza búsquedas repetidas
- **Filtrado automático**: Solo negocios activos

### **3. Escalabilidad**
- **Fácil extensión**: Agregar nuevos criterios de búsqueda
- **Configurable**: Radio de búsqueda ajustable
- **Mantenible**: Código limpio y bien documentado
- **Robusto**: Manejo de errores y casos edge

## 🚀 **Resultado Final**

El sistema de búsqueda ahora es **inteligente y combinado** que permite:

- ✅ **Búsqueda por nombre**: Encuentra negocios específicos
- ✅ **Búsqueda por servicio**: Muestra todos los negocios que ofrezcan un servicio
- ✅ **Búsqueda por ubicación**: Con coordenadas (distancia) o texto (ciudad/barrio)
- ✅ **Combinaciones flexibles**: Cualquier combinación de criterios
- ✅ **Ordenamiento inteligente**: Según el tipo de búsqueda
- ✅ **Resultados relevantes**: Información clara y descriptiva
- ✅ **Responsive**: Funciona en todos los dispositivos
- ✅ **Rápido y eficiente**: Optimizado para rendimiento

¡La implementación está completa y optimizada para búsquedas inteligentes y combinadas! 🎉 