# 📧 Sistema de Emails Avanzado - APPO

## 🎯 **Descripción General**

Sistema de email profesional integrado que combina **SendGrid** (servicio principal), **AWS SES** (respaldo) y **SMTP tradicional** (último recurso) con sistema de fallback automático, tracking completo y métricas avanzadas.

## ✨ **Características Principales**

### 🔄 **Sistema de Fallback Inteligente**
- **SendGrid**: Servicio principal (mejor rendimiento y features)
- **AWS SES**: Servicio de respaldo (alta confiabilidad)
- **SMTP**: Último recurso (compatibilidad total)

### 📊 **Tracking y Métricas**
- Estado de entrega en tiempo real
- Tracking de apertura y clicks
- Métricas de rendimiento por proveedor
- Historial completo de emails

### 🚀 **Rendimiento y Escalabilidad**
- Envío en lotes (bulk email)
- Rate limiting configurable
- Cola de emails asíncrona
- Timeouts configurables

### 🎨 **Templates y Personalización**
- Templates HTML y texto
- Contexto dinámico
- Estilos CSS integrados
- Responsive design

## 🛠️ **Instalación y Configuración**

### 1. **Instalar Dependencias**

```bash
pip install sendgrid==6.11.0 boto3==1.34.0 django-anymail==10.2
```

### 2. **Configurar Variables de Entorno**

```bash
# Configuración de SendGrid (servicio principal)
SENDGRID_API_KEY=tu-sendgrid-api-key
SENDGRID_FROM_EMAIL=noreply@appo.com.co
SENDGRID_FROM_NAME=APPO

# Configuración de AWS SES (servicio de respaldo)
AWS_ACCESS_KEY_ID=tu-aws-access-key
AWS_SECRET_ACCESS_KEY=tu-aws-secret-key
AWS_SES_REGION_NAME=us-east-1
AWS_SES_REGION_ENDPOINT=email.us-east-1.amazonaws.com

# Configuración avanzada
EMAIL_TRACKING_ENABLED=True
EMAIL_OPEN_TRACKING=True
EMAIL_CLICK_TRACKING=True
EMAIL_QUEUE_ENABLED=False
EMAIL_RATE_LIMIT=100/hour
```

### 3. **Configurar Django Settings**

```python
# melissa/settings.py

# Configuración de SendGrid
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@appo.com.co')

# Configuración de AWS SES
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION_NAME', 'us-east-1')

# Configuración de tracking
EMAIL_TRACKING_ENABLED = True
EMAIL_OPEN_TRACKING = True
EMAIL_CLICK_TRACKING = True
```

### 4. **Ejecutar Migraciones**

```bash
python manage.py makemigrations cuentas
python manage.py migrate
```

## 🚀 **Uso del Servicio**

### **Envío Básico**

```python
from cuentas.email_service import email_service

# Email simple
success = email_service.send_email(
    subject='Asunto del email',
    message='Contenido en texto plano',
    recipient_list=['usuario@ejemplo.com'],
    html_message='<h1>Contenido HTML</h1>'
)
```

### **Envío con Template**

```python
# Usar template existente
context = {
    'usuario': 'Juan Pérez',
    'negocio': 'Salón de Belleza',
    'fecha': '15 de Agosto'
}

success = email_service.send_template_email(
    template_name='recordatorio_dia_antes',
    context=context,
    subject='Recordatorio de tu cita',
    recipient_list=['cliente@ejemplo.com']
)
```

### **Envío en Lotes**

```python
# Enviar a múltiples destinatarios
emails = ['usuario1@ejemplo.com', 'usuario2@ejemplo.com', 'usuario3@ejemplo.com']

resultado = email_service.send_bulk_email(
    subject='Anuncio importante',
    message='Mensaje para todos',
    recipient_list=emails,
    batch_size=50,  # Enviar en lotes de 50
    delay=2         # 2 segundos entre lotes
)

print(f"Enviados: {resultado['sent']}, Fallidos: {resultado['failed']}")
```

## 📊 **Tracking y Métricas**

### **Modelo EmailTracking**

```python
from cuentas.models import EmailTracking

# Crear tracking manual
tracking = EmailTracking.objects.create(
    subject='Email de prueba',
    recipient='usuario@ejemplo.com',
    from_email='noreply@appo.com.co',
    proveedor='sendgrid',
    template_name='recordatorio_dia_antes'
)

# Marcar como entregado
tracking.marcar_entregado()

# Marcar como abierto
tracking.marcar_abierto()

# Marcar como clickeado
tracking.marcar_clickeado()
```

### **Consultar Métricas**

```python
# Estadísticas generales
total_emails = EmailTracking.objects.count()
emails_entregados = EmailTracking.objects.filter(estado='entregado').count()
tasa_entrega = (emails_entregados / total_emails) * 100

# Por proveedor
sendgrid_emails = EmailTracking.objects.filter(proveedor='sendgrid').count()
aws_ses_emails = EmailTracking.objects.filter(proveedor='aws_ses').count()

# Por fecha
from django.utils import timezone
from datetime import timedelta

hoy = timezone.now().date()
emails_hoy = EmailTracking.objects.filter(enviado_en__date=hoy).count()
```

## 🧪 **Pruebas y Testing**

### **Comando de Prueba**

```bash
# Prueba básica
python manage.py test_email_service --email tu-email@ejemplo.com

# Prueba con template
python manage.py test_email_service --email tu-email@ejemplo.com --template

# Prueba con proveedor específico
python manage.py test_email_service --email tu-email@ejemplo.com --provider sendgrid
```

### **Prueba en Código**

```python
from cuentas.email_service import email_service

# Verificar estado de proveedores
status = email_service.get_provider_status()
print(f"SendGrid: {status['sendgrid']['status']}")
print(f"AWS SES: {status['aws_ses']['status']}")
print(f"SMTP: {status['smtp']['status']}")

# Probar envío
try:
    success = email_service.send_email(
        subject='Test',
        message='Mensaje de prueba',
        recipient_list=['test@ejemplo.com']
    )
    print(f"Enviado: {success}")
except Exception as e:
    print(f"Error: {e}")
```

## 🔧 **Configuración Avanzada**

### **Rate Limiting**

```python
# En settings.py
EMAIL_RATE_LIMIT = '100/hour'           # 100 emails por hora
EMAIL_RATE_LIMIT_PER_USER = '10/hour'   # 10 emails por usuario por hora
```

### **Cola de Emails**

```python
# Habilitar cola
EMAIL_QUEUE_ENABLED = True
EMAIL_QUEUE_BATCH_SIZE = 100
EMAIL_QUEUE_DELAY = 5  # segundos entre lotes
```

### **Timeouts y SSL**

```python
EMAIL_TIMEOUT = 30
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
```

## 📈 **Monitoreo y Logs**

### **Logs del Sistema**

```python
import logging

logger = logging.getLogger(__name__)

# El servicio registra automáticamente:
# - Inicialización de proveedores
# - Envíos exitosos/fallidos
# - Cambios de estado de tracking
# - Errores y warnings
```

### **Métricas en Admin**

- Dashboard completo en Django Admin
- Filtros por estado, proveedor, fecha
- Métricas de tiempo de entrega
- Estadísticas de rendimiento

## 🚨 **Solución de Problemas**

### **SendGrid No Funciona**

```bash
# Verificar API key
echo $SENDGRID_API_KEY

# Verificar logs
python manage.py test_email_service --provider sendgrid
```

### **AWS SES No Funciona**

```bash
# Verificar credenciales
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# Verificar región
echo $AWS_SES_REGION_NAME
```

### **Tracking No Funciona**

```python
# Verificar configuración
from django.conf import settings
print(f"Tracking enabled: {settings.EMAIL_TRACKING_ENABLED}")
print(f"Open tracking: {settings.EMAIL_OPEN_TRACKING}")
print(f"Click tracking: {settings.EMAIL_CLICK_TRACKING}")
```

## 🔄 **Migración desde Sistema Anterior**

### **Cambiar Importaciones**

```python
# ANTES
from django.core.mail import send_mail

# DESPUÉS
from cuentas.email_service import send_email
# O mantener compatibilidad
from cuentas.email_service import email_service
```

### **Actualizar Funciones**

```python
# El servicio mantiene la misma API que Django send_mail
# Solo agregar parámetros opcionales para tracking
```

## 📚 **Recursos Adicionales**

### **Documentación Oficial**
- [SendGrid API Documentation](https://sendgrid.com/docs/api-reference/)
- [AWS SES Documentation](https://docs.aws.amazon.com/ses/)
- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)

### **Templates de Email**
- Ubicación: `templates/emails/`
- Formatos: HTML y texto plano
- Responsive design incluido
- Variables de contexto dinámicas

### **Comandos de Gestión**
- `test_email_service`: Probar el servicio
- `send_bulk_emails`: Envío masivo
- `email_analytics`: Reportes y métricas

## 🎉 **Beneficios del Nuevo Sistema**

1. **Confiabilidad**: Múltiples proveedores con fallback automático
2. **Rendimiento**: SendGrid para alta velocidad, AWS SES para confiabilidad
3. **Tracking**: Métricas completas de entrega y engagement
4. **Escalabilidad**: Envío en lotes y rate limiting
5. **Monitoreo**: Dashboard completo en admin
6. **Compatibilidad**: API idéntica al sistema anterior
7. **Flexibilidad**: Configuración por entorno
8. **Profesional**: Cumple estándares empresariales

---

**¿Necesitas ayuda?** Revisa los logs del sistema o ejecuta el comando de prueba para diagnosticar problemas.
