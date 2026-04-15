# 🔔 Sistema de Recordatorios Avanzado - APPO

## 🎯 **Descripción General**

Sistema de recordatorios profesional que maneja automáticamente notificaciones por **email**, **WhatsApp** y **SMS** para reservas, suscripciones y otros eventos del sistema. Totalmente compatible con el código existente y con integración automática mediante señales Django.

## ✨ **Características Principales**

### 🔄 **Integración Automática**
- **Señales Django**: Se integra automáticamente con reservas, suscripciones e inasistencias
- **Compatibilidad total**: Funciona con el código existente sin modificaciones
- **Creación automática**: Los recordatorios se crean automáticamente cuando se crean reservas

### 📱 **Múltiples Canales de Notificación**
- **📧 Email**: Con templates HTML y texto, usando el sistema de email avanzado
- **📱 WhatsApp**: Integrado con el servicio de WhatsApp Business API existente
- **💬 SMS**: Soporte para Twilio y otros proveedores de SMS
- **🔔 Push Notifications**: Preparado para futuras implementaciones

### ⏰ **Sistema de Programación Inteligente**
- **Anticipación configurable**: 24h, 3h, 1h antes del evento
- **Prioridades**: Sistema de prioridades para recordatorios urgentes
- **Reintentos automáticos**: Hasta 5 reintentos con delays configurables
- **Fallback inteligente**: Si falla un canal, intenta con otros

### 📊 **Tracking y Métricas Completas**
- **Estado en tiempo real**: Pendiente, enviado, entregado, fallido, cancelado
- **Historial completo**: Todas las acciones realizadas en cada recordatorio
- **Métricas por canal**: Rendimiento de email, WhatsApp y SMS
- **Dashboard en admin**: Gestión completa desde Django Admin

## 🏗️ **Arquitectura del Sistema**

### **Modelos Principales**

#### 1. **Recordatorio** (Modelo principal)
```python
class Recordatorio(models.Model):
    # Identificación única con UUID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    
    # Tipo y estado
    tipo = models.CharField(choices=TipoRecordatorio.choices)
    estado = models.CharField(choices=EstadoRecordatorio.choices)
    
    # Destinatario y contenido
    destinatario = models.ForeignKey(UsuarioPersonalizado)
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    mensaje_html = models.TextField()
    
    # Programación
    fecha_programada = models.DateTimeField()
    fecha_envio = models.DateTimeField(null=True)
    fecha_entrega = models.DateTimeField(null=True)
    
    # Canales y reintentos
    canales_habilitados = models.JSONField()  # ['email', 'whatsapp', 'sms']
    canales_enviados = models.JSONField()     # Estado de cada canal
    reintentos_maximos = models.PositiveIntegerField(default=3)
    reintentos_actuales = models.PositiveIntegerField(default=0)
    
    # Relaciones genéricas
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    contenido_relacionado = GenericForeignKey()
```

#### 2. **ConfiguracionRecordatorio**
```python
class ConfiguracionRecordatorio(models.Model):
    tipo = models.CharField(choices=TipoRecordatorio.choices, unique=True)
    anticipacion_horas = models.PositiveIntegerField(default=24)
    anticipacion_minutos = models.PositiveIntegerField(default=0)
    canales_habilitados = models.JSONField(default=['email', 'whatsapp'])
    reintentos_maximos = models.PositiveIntegerField(default=3)
    delay_reintentos_minutos = models.PositiveIntegerField(default=15)
```

#### 3. **PlantillaRecordatorio**
```python
class PlantillaRecordatorio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(choices=TipoRecordatorio.choices)
    asunto = models.CharField(max_length=255)
    mensaje_texto = models.TextField()
    mensaje_html = models.TextField()
    variables_disponibles = models.JSONField()  # ['usuario', 'reserva', 'fecha']
```

#### 4. **HistorialRecordatorio**
```python
class HistorialRecordatorio(models.Model):
    recordatorio = models.ForeignKey(Recordatorio)
    accion = models.CharField(max_length=50)  # 'creado', 'enviado', 'fallido'
    canal = models.CharField(choices=CanalNotificacion.choices)
    detalles = models.JSONField()
    mensaje_error = models.TextField()
```

### **Tipos de Recordatorios Disponibles**
- `reserva_confirmada`: Confirmación inmediata de reserva
- `recordatorio_dia_antes`: 24 horas antes de la cita
- `recordatorio_tres_horas`: 3 horas antes de la cita
- `reserva_cancelada`: Notificación de cancelación
- `reserva_reagendada`: Notificación de cambio de fecha
- `suscripcion_renovacion`: 7 días antes del vencimiento
- `suscripcion_expirada`: Notificación de expiración
- `inasistencia`: Notificación de inasistencia registrada
- `custom`: Recordatorios personalizados

## 🚀 **Instalación y Configuración**

### 1. **Agregar la App a INSTALLED_APPS**
```python
# melissa/settings.py
INSTALLED_APPS = [
    # ... otras apps ...
    'recordatorios',
]
```

### 2. **Ejecutar Migraciones**
```bash
python manage.py makemigrations recordatorios
python manage.py migrate
```

### 3. **Configurar Variables de Entorno (Opcional)**
```bash
# Para SMS con Twilio
TWILIO_ACCOUNT_SID=tu-account-sid
TWILIO_AUTH_TOKEN=tu-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Configuración de recordatorios
RECORDATORIOS_EMAIL_ENABLED=True
RECORDATORIOS_WHATSAPP_ENABLED=True
RECORDATORIOS_SMS_ENABLED=False
```

### 4. **Crear Configuraciones por Defecto**
```bash
python manage.py shell
```
```python
from recordatorios.models import ConfiguracionRecordatorio, TipoRecordatorio

# Configurar recordatorio día antes
ConfiguracionRecordatorio.objects.create(
    tipo=TipoRecordatorio.RECORDATORIO_DIA_ANTES,
    anticipacion_horas=24,
    canales_habilitados=['email', 'whatsapp'],
    reintentos_maximos=3
)

# Configurar recordatorio 3 horas antes
ConfiguracionRecordatorio.objects.create(
    tipo=TipoRecordatorio.RECORDATORIO_TRES_HORAS,
    anticipacion_horas=3,
    canales_habilitados=['email', 'whatsapp', 'sms'],
    reintentos_maximos=5
)
```

## 🔧 **Uso del Sistema**

### **Uso Automático (Recomendado)**

El sistema funciona automáticamente mediante señales Django:

1. **Al crear una reserva**: Se crean automáticamente recordatorios para 24h y 3h antes
2. **Al modificar una reserva**: Se cancelan recordatorios existentes y se crean nuevos
3. **Al cancelar una reserva**: Se crea notificación de cancelación
4. **Al registrar inasistencia**: Se crea notificación inmediata

### **Uso Manual**

#### **Crear Recordatorio Personalizado**
```python
from recordatorios.services import servicio_recordatorios
from datetime import datetime, timedelta

# Crear recordatorio personalizado
recordatorio = servicio_recordatorios.crear_recordatorio(
    tipo='custom',
    destinatario=usuario,
    fecha_evento=datetime.now() + timedelta(days=1),
    canales=['email', 'whatsapp'],
    contexto_template={
        'usuario': usuario.username,
        'mensaje': 'Recordatorio personalizado',
        'fecha': 'mañana'
    },
    prioridad=1
)
```

#### **Enviar Recordatorio Inmediato**
```python
from recordatorios.services import servicio_recordatorios

# Enviar recordatorio inmediato (sin programar)
resultado = servicio_recordatorios._procesar_recordatorio(recordatorio)
if resultado['enviado']:
    print("Recordatorio enviado exitosamente")
```

### **Comandos de Gestión**

#### **Procesar Recordatorios Pendientes**
```bash
# Procesar todos los recordatorios pendientes
python manage.py procesar_recordatorios

# Simular procesamiento (sin enviar)
python manage.py procesar_recordatorios --dry-run

# Procesar solo los primeros 10
python manage.py procesar_recordatorios --limit 10

# Forzar procesamiento de recordatorios vencidos
python manage.py procesar_recordatorios --force

# Modo verbose para debugging
python manage.py procesar_recordatorios --verbose
```

#### **Estadísticas del Sistema**
```bash
# Ver estadísticas generales
python manage.py shell
```
```python
from recordatorios.models import Recordatorio, EstadoRecordatorio

# Total de recordatorios
total = Recordatorio.objects.count()

# Recordatorios pendientes
pendientes = Recordatorio.objects.filter(estado=EstadoRecordatorio.PENDIENTE).count()

# Recordatorios enviados hoy
from django.utils import timezone
hoy = timezone.now().date()
enviados_hoy = Recordatorio.objects.filter(
    fecha_envio__date=hoy
).count()

print(f"Total: {total}, Pendientes: {pendientes}, Enviados hoy: {enviados_hoy}")
```

## 📱 **Configuración de Canales**

### **Email**
- Usa el sistema de email avanzado existente (SendGrid + AWS SES)
- Templates HTML y texto automáticos
- Tracking de entrega y apertura

### **WhatsApp**
- Integrado con el servicio de WhatsApp Business API existente
- Mensajes de texto con formato
- Notificaciones push en tiempo real

### **SMS**
- Soporte para Twilio (configurable)
- Mensajes de texto cortos
- Confirmación de entrega

## 🎨 **Templates y Personalización**

### **Templates Automáticos**
El sistema usa automáticamente los templates existentes:
- `emails/recordatorio_dia_antes.html`
- `emails/recordatorio_tres_horas.html`
- `emails/reserva_confirmada.html`
- `emails/reserva_cancelada.html`

### **Variables Disponibles en Templates**
```html
<!-- Variables automáticas -->
{{ usuario }}           <!-- Usuario destinatario -->
{{ reserva }}           <!-- Objeto reserva -->
{{ negocio }}           <!-- Negocio/peluquero -->
{{ profesional }}       <!-- Profesional asignado -->
{{ fecha_formateada }}  <!-- Fecha en formato legible -->
{{ hora_formateada }}   <!-- Hora en formato legible -->

<!-- Variables personalizadas -->
{{ mensaje }}           <!-- Mensaje personalizado -->
{{ fecha }}             <!-- Fecha personalizada -->
{{ accion }}            <!-- Acción a realizar -->
```

### **Crear Template Personalizado**
```python
from recordatorios.models import PlantillaRecordatorio

plantilla = PlantillaRecordatorio.objects.create(
    nombre='Recordatorio Personalizado',
    tipo='custom',
    asunto='Recordatorio: {{ accion }}',
    mensaje_texto='Hola {{ usuario }}, tienes que {{ accion }} el {{ fecha }}',
    mensaje_html='<h1>Recordatorio</h1><p>Hola {{ usuario }}, tienes que {{ accion }} el {{ fecha }}</p>',
    variables_disponibles=['usuario', 'accion', 'fecha'],
    activa=True
)
```

## 📊 **Monitoreo y Administración**

### **Django Admin**
- **RecordatorioAdmin**: Gestión completa de recordatorios
- **ConfiguracionRecordatorioAdmin**: Configuración de tipos
- **PlantillaRecordatorioAdmin**: Gestión de templates
- **HistorialRecordatorioAdmin**: Historial de acciones

### **Acciones del Admin**
- **Reprogramar recordatorios fallidos**
- **Cancelar recordatorios pendientes**
- **Forzar envío inmediato**
- **Filtros por estado, tipo, fecha**
- **Búsqueda por destinatario, asunto, contenido**

### **Logs del Sistema**
```python
import logging

logger = logging.getLogger('recordatorios')

# Los siguientes eventos se registran automáticamente:
# - Creación de recordatorios
# - Envío exitoso/fallido por canal
# - Cambios de estado
# - Errores y warnings
# - Reintentos programados
```

## 🔄 **Compatibilidad con Código Existente**

### **Funciones de Compatibilidad**
```python
# ANTES (código existente)
from clientes.utils import enviar_recordatorio_dia_antes
from clientes.utils import enviar_recordatorio_tres_horas

# DESPUÉS (nuevo sistema)
from recordatorios.services import enviar_recordatorio_dia_antes
from recordatorios.services import enviar_recordatorio_tres_horas

# Ambas funciones funcionan exactamente igual
enviar_recordatorio_dia_antes(reserva)
enviar_recordatorio_tres_horas(reserva)
```

### **Integración Automática**
- **No requiere cambios** en el código existente
- **Señales Django** se activan automáticamente
- **Templates existentes** se usan como fallback
- **Servicios existentes** se integran automáticamente

## 🚨 **Solución de Problemas**

### **Recordatorios No Se Crean**
```bash
# Verificar señales
python manage.py shell
```
```python
from django.db.models.signals import post_save
from recordatorios.signals import crear_recordatorios_reserva

# Verificar que la señal esté conectada
print(crear_recordatorios_reserva in post_save._live_receivers)
```

### **Recordatorios No Se Envían**
```bash
# Verificar estado de recordatorios
python manage.py shell
```
```python
from recordatorios.models import Recordatorio, EstadoRecordatorio

# Ver recordatorios pendientes
pendientes = Recordatorio.objects.filter(estado=EstadoRecordatorio.PENDIENTE)
print(f"Pendientes: {pendientes.count()}")

# Ver recordatorios vencidos
from django.utils import timezone
vencidos = pendientes.filter(fecha_programada__lt=timezone.now())
print(f"Vencidos: {vencidos.count()}")
```

### **Procesar Recordatorios Manualmente**
```bash
# Forzar procesamiento
python manage.py procesar_recordatorios --force --verbose

# Simular primero
python manage.py procesar_recordatorios --dry-run --verbose
```

## 📈 **Rendimiento y Escalabilidad**

### **Optimizaciones Automáticas**
- **Índices de base de datos** para consultas rápidas
- **Limpieza automática** de recordatorios antiguos
- **Procesamiento en lotes** para grandes volúmenes
- **Rate limiting** por canal de notificación

### **Monitoreo de Rendimiento**
```python
from recordatorios.models import Recordatorio
from django.db.models import Count, Avg
from django.utils import timezone

# Rendimiento por canal
rendimiento_canal = Recordatorio.objects.filter(
    fecha_envio__gte=timezone.now() - timezone.timedelta(days=7)
).values('canales_habilitados').annotate(
    total=Count('id'),
    exitosos=Count('id', filter=models.Q(estado=EstadoRecordatorio.ENVIADO))
)

# Tiempo promedio de entrega
tiempo_entrega = Recordatorio.objects.filter(
    fecha_envio__isnull=False,
    fecha_entrega__isnull=False
).aggregate(
    tiempo_promedio=Avg('fecha_entrega' - 'fecha_envio')
)
```

## 🔮 **Futuras Mejoras**

### **Funcionalidades Planificadas**
- **Notificaciones push** para móviles
- **Webhooks** para integración con sistemas externos
- **API REST** para gestión programática
- **Dashboard web** para usuarios finales
- **Analytics avanzados** con gráficos y reportes
- **Integración con calendarios** (Google Calendar, Outlook)

### **Escalabilidad**
- **Procesamiento asíncrono** con Celery
- **Cola de recordatorios** para alta concurrencia
- **Cache distribuido** para mejor rendimiento
- **Microservicios** para componentes específicos

## 🎉 **Beneficios del Nuevo Sistema**

1. **🔄 Automatización completa** de recordatorios
2. **📱 Múltiples canales** de notificación
3. **⏰ Programación inteligente** con reintentos
4. **📊 Tracking completo** y métricas
5. **🔧 Compatibilidad total** con código existente
6. **🎨 Templates personalizables** y flexibles
7. **📈 Escalabilidad** para crecimiento del negocio
8. **🛡️ Confiabilidad** con sistema de fallback
9. **📱 Experiencia de usuario** mejorada
10. **💰 Reducción de inasistencias** y mejor retención

---

## 🚀 **¡Listo para Usar!**

El sistema de recordatorios está completamente integrado y funcionando. Los recordatorios se crearán automáticamente para todas las nuevas reservas, y puedes gestionar todo desde el Django Admin.

**¿Necesitas ayuda?** Revisa los logs del sistema o ejecuta el comando de procesamiento para diagnosticar problemas.
