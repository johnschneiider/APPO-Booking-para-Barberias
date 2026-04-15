# Sistema de Suscripciones - Melissa

## Descripción General

El Sistema de Suscripciones es una nueva funcionalidad que permite a los negocios (peluquerías) ofrecer planes de suscripción mensual a sus clientes. Los clientes pueden suscribirse a diferentes niveles de planes con beneficios exclusivos como descuentos, servicios gratuitos y prioridad en reservas.

## Características Principales

### 🏢 Para Negocios
- **Crear y gestionar planes de suscripción** con precios y beneficios personalizables
- **Configurar descuentos** en servicios (0-100%)
- **Establecer límites de servicios** por mes (o ilimitados)
- **Prioridad en reservas** para suscriptores
- **Dashboard de suscriptores** con estadísticas y gestión
- **Sistema de pagos** integrado con seguimiento de estado

### 👥 Para Clientes
- **Ver planes disponibles** de cada negocio
- **Suscribirse a planes** con renovación automática opcional
- **Gestionar suscripción** (cancelar, cambiar plan)
- **Ver historial** de pagos y cambios
- **Beneficios automáticos** al reservar servicios

### 🔧 Funcionalidades Técnicas
- **Señales automáticas** para notificaciones y historial
- **API REST** para integración con frontend
- **Sistema de pagos** flexible con múltiples métodos
- **Historial completo** de todas las acciones
- **Validaciones** de seguridad y negocio

## Estructura de la Base de Datos

### Modelos Principales

#### 1. PlanSuscripcion
```python
- negocio: ForeignKey al negocio que ofrece el plan
- nombre: Nombre del plan (Básico, Premium, VIP)
- descripcion: Descripción detallada del plan
- precio_mensual: Precio mensual en la moneda local
- max_servicios_mes: Límite de servicios (0 = ilimitado)
- descuento_servicios: Porcentaje de descuento (0-100%)
- prioridad_reservas: Si los suscriptores tienen prioridad
- activo: Si el plan está disponible
```

#### 2. Suscripcion
```python
- cliente: Usuario suscrito
- plan: Plan de suscripción seleccionado
- negocio: Negocio al que está suscrito
- estado: Activa, Cancelada, Expirada, Pendiente de Pago
- fecha_inicio/fin: Período de la suscripción
- precio_actual: Precio actual del plan
- servicios_utilizados_mes: Contador de servicios usados
- renovacion_automatica: Si se renueva automáticamente
```

#### 3. PagoSuscripcion
```python
- suscripcion: Suscripción asociada
- monto: Cantidad a pagar
- metodo_pago: Tarjeta, Transferencia, Efectivo, PSE, PayPal
- estado: Pendiente, Completado, Fallido, Reembolsado
- fecha_vencimiento: Fecha límite para el pago
- referencia_pago: ID de la transacción
```

#### 4. BeneficioSuscripcion
```python
- plan: Plan al que pertenece el beneficio
- nombre: Nombre del beneficio
- descripcion: Descripción detallada
- tipo_beneficio: Descuento, Servicio Gratis, Prioridad, Exclusivo
- valor: Valor del beneficio (ej: 20%, 1 servicio)
```

#### 5. HistorialSuscripcion
```python
- suscripcion: Suscripción relacionada
- accion: Tipo de acción realizada
- descripcion: Descripción de la acción
- fecha: Fecha y hora de la acción
- usuario_responsable: Usuario que realizó la acción
```

## Planes de Suscripción Predefinidos

### 📋 Plan Básico
- **Precio**: $29.99/mes
- **Servicios**: 3 por mes
- **Descuento**: 10% en servicios
- **Prioridad**: No
- **Beneficios**: Descuento básico, servicios limitados

### ⭐ Plan Premium
- **Precio**: $59.99/mes
- **Servicios**: 6 por mes
- **Descuento**: 20% en servicios
- **Prioridad**: Sí
- **Beneficios**: Descuento mayor, prioridad en reservas

### 👑 Plan VIP
- **Precio**: $99.99/mes
- **Servicios**: Ilimitados
- **Descuento**: 30% en servicios
- **Prioridad**: Máxima
- **Beneficios**: Máximo descuento, servicios ilimitados, exclusividades

## URLs del Sistema

### Para Negocios
```
/suscripciones/negocio/{id}/planes/                    # Gestionar planes
/suscripciones/negocio/{id}/planes/crear/              # Crear nuevo plan
/suscripciones/negocio/{id}/planes/{id}/editar/        # Editar plan
/suscripciones/negocio/{id}/planes/{id}/eliminar/      # Eliminar plan
/suscripciones/negocio/{id}/suscriptores/              # Ver suscriptores
```

### Para Clientes
```
/suscripciones/negocio/{id}/planes-disponibles/        # Ver planes
/suscripciones/negocio/{id}/suscribirse/{plan_id}/     # Suscribirse
/suscripciones/negocio/{id}/mi-suscripcion/            # Gestionar suscripción
/suscripciones/negocio/{id}/cancelar-suscripcion/      # Cancelar
/suscripciones/negocio/{id}/cambiar-plan/              # Cambiar plan
```

### APIs
```
/suscripciones/api/negocio/{id}/planes/                # Obtener planes
/suscripciones/api/negocio/{id}/mi-suscripcion/        # Obtener suscripción
```

## Comandos de Gestión

### Poblar Planes de Suscripción
```bash
python manage.py poblar_planes_suscripcion
```
Este comando crea automáticamente los 3 planes estándar (Básico, Premium, VIP) para todos los negocios activos en el sistema.

## Flujo de Suscripción

### 1. Cliente Ve Planes
- Navega a la página del negocio
- Ve los planes disponibles con precios y beneficios
- Compara características de cada plan

### 2. Cliente Se Suscribe
- Selecciona un plan
- Acepta términos y condiciones
- Confirma renovación automática (opcional)
- Se crea la suscripción en estado "pendiente_pago"

### 3. Proceso de Pago
- Se genera un registro de pago
- Cliente completa el pago por el método elegido
- Al confirmar el pago, la suscripción se activa

### 4. Suscripción Activa
- Cliente disfruta de los beneficios del plan
- Sistema cuenta servicios utilizados (si aplica)
- Notificaciones automáticas antes de renovación

### 5. Renovación o Cancelación
- Renovación automática mensual (configurable)
- Cliente puede cancelar en cualquier momento
- Historial completo de todas las acciones

## Integración con el Sistema Existente

### Reservas
- Los suscriptores pueden tener prioridad en reservas
- Los descuentos se aplican automáticamente
- El sistema verifica límites de servicios

### Notificaciones
- Emails automáticos de confirmación de pago
- Notificaciones de renovación próxima
- Alertas de expiración de suscripción

### Dashboard del Negocio
- Estadísticas de suscriptores activos
- Ingresos mensuales por suscripciones
- Gestión de planes y suscriptores

## Seguridad y Validaciones

### Validaciones de Negocio
- Solo propietarios pueden gestionar planes
- No se pueden eliminar planes con suscriptores activos
- Precios y descuentos tienen límites razonables

### Validaciones de Cliente
- Un cliente solo puede tener una suscripción activa por negocio
- Los planes deben pertenecer al negocio correcto
- Confirmación obligatoria para cancelaciones

### Auditoría
- Historial completo de todas las acciones
- Trazabilidad de pagos y cambios
- Logs de seguridad y acceso

## Configuración del Sistema

### Variables de Entorno
```python
# En settings.py
SEND_EMAILS = True  # Para notificaciones por email
DEFAULT_FROM_EMAIL = 'noreply@melissa.com'
```

### Personalización de Planes
- Cada negocio puede crear planes únicos
- Precios y beneficios completamente personalizables
- Activación/desactivación de planes

## Próximas Funcionalidades

### Fase 2 (Próximas Versiones)
- **Integración con pasarelas de pago** (Stripe, PayPal, etc.)
- **Sistema de referidos** con bonificaciones
- **Planes familiares** con múltiples usuarios
- **Descuentos por volumen** de servicios
- **Sistema de puntos** y recompensas
- **Analytics avanzados** para negocios

### Fase 3 (Futuro)
- **App móvil** para gestión de suscripciones
- **Notificaciones push** en tiempo real
- **Integración con CRM** externos
- **Sistema de fidelización** avanzado
- **Gamificación** para retención de clientes

## Soporte y Mantenimiento

### Comandos Útiles
```bash
# Verificar estado del sistema
python manage.py check

# Crear superusuario
python manage.py createsuperuser

# Ejecutar migraciones
python manage.py migrate

# Poblar datos de ejemplo
python manage.py poblar_planes_suscripcion
```

### Logs y Monitoreo
- Todos los eventos se registran en el historial
- Logs de Django para debugging
- Monitoreo de pagos y transacciones

## Conclusión

El Sistema de Suscripciones representa una evolución significativa de Melissa, transformándola de una plataforma de reservas simple a un ecosistema completo de gestión de clientes y monetización para negocios de belleza.

Este sistema no solo genera ingresos recurrentes para los negocios, sino que también mejora la fidelización de clientes y proporciona una experiencia de usuario más rica y personalizada.

La arquitectura modular y escalable permite futuras expansiones y integraciones, posicionando a Melissa como una solución integral para la gestión moderna de negocios de belleza.
