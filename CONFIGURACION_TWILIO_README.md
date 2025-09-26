# 📱 Configuración de Twilio para WhatsApp y SMS - APPO

## 🎯 **¿Por qué Twilio?**

**Twilio es la solución más eficiente** para tu sistema de recordatorios porque:

✅ **Un solo proveedor** para WhatsApp y SMS  
✅ **Precios muy bajos** (desde $0.005 por mensaje)  
✅ **API confiable** y fácil de usar  
✅ **WhatsApp oficial** de Meta  
✅ **Cobertura global** en más de 180 países  
✅ **Soporte en español** disponible  

## 🚀 **Configuración Paso a Paso**

### **Paso 1: Crear cuenta en Twilio**

1. **Ir a [twilio.com](https://www.twilio.com)**
2. **Hacer clic en "Sign up for free"**
3. **Completar registro** con tu información
4. **Verificar tu número de teléfono** (recibirás un SMS)
5. **Acceder al Console** de Twilio

### **Paso 2: Obtener credenciales**

En el **Twilio Console**:

1. **Dashboard** → Copiar **Account SID**
2. **Dashboard** → Copiar **Auth Token**
3. **Phone Numbers** → Comprar número para SMS
4. **Messaging** → **Try it out** → **Send a WhatsApp message**

### **Paso 3: Configurar WhatsApp Business API**

1. **En Twilio Console:**
   - Ir a **Messaging** → **Try it out**
   - Hacer clic en **"Send a WhatsApp message"**
   - Seguir las instrucciones para **activar WhatsApp**

2. **Recibirás un número de WhatsApp:**
   - Formato: `+14155238886` (número de prueba)
   - Para producción: Comprar número verificado

### **Paso 4: Configurar variables de entorno**

Crear archivo `.env` en tu proyecto:

```bash
# Configuración de Twilio
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
TWILIO_AUTH_TOKEN=tu-auth-token-aqui
TWILIO_WHATSAPP_NUMBER=+14155238886
TWILIO_SMS_NUMBER=+1234567890

# Configuración de email (como respaldo)
SENDGRID_API_KEY=tu-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@appo.com.co
```

### **Paso 5: Instalar dependencias**

```bash
pip install twilio
```

O agregar a `requirements.txt`:
```
twilio==8.10.0
```

## 📊 **Precios de Twilio (2024)**

### **WhatsApp Business API:**
- **Mensajes de sesión**: $0.005 por mensaje
- **Mensajes de plantilla**: $0.005 por mensaje
- **Mensajes de respuesta gratuita**: 24 horas después del último mensaje

### **SMS:**
- **Colombia**: $0.0075 por SMS
- **Estados Unidos**: $0.0079 por SMS
- **Otros países**: Varía según región

### **Ejemplo de costos para 1000 recordatorios:**
- **WhatsApp**: $5.00
- **SMS**: $7.50
- **Total**: $12.50 por 1000 recordatorios

## 🔧 **Configuración Avanzada**

### **WhatsApp Templates (Recomendado)**

Para **recordatorios automáticos**, crear templates en Twilio:

1. **Template: "recordatorio_cita"**
```
Hola {{1}}, tienes una cita mañana {{2}} a las {{3}}.
📍 {{4}}
👨‍⚕️ {{5}}
💇‍♀️ {{6}}

¡Te esperamos!
```

2. **Variables disponibles:**
   - `{{1}}`: Nombre del cliente
   - `{{2}}`: Fecha de la cita
   - `{{3}}`: Hora de la cita
   - `{{4}}`: Nombre del negocio
   - `{{5}}`: Nombre del profesional
   - `{{6}}`: Servicio contratado

### **Configuración de Webhooks**

Para **tracking avanzado**:

```python
# En settings.py
TWILIO_WEBHOOK_URL = 'https://tu-dominio.com/webhooks/twilio/'
TWILIO_STATUS_CALLBACK = 'https://tu-dominio.com/webhooks/twilio/status/'
```

## 🧪 **Pruebas y Testing**

### **1. Probar WhatsApp:**
```bash
# Enviar recordatorio de prueba
python manage.py procesar_recordatorios --force --limit 1
```

### **2. Probar SMS:**
```bash
# Crear recordatorio con canal SMS
python manage.py shell
```

```python
from recordatorios.services import servicio_recordatorios
from cuentas.models import UsuarioPersonalizado

# Crear recordatorio de prueba
usuario = UsuarioPersonalizado.objects.first()
recordatorio = servicio_recordatorios.crear_recordatorio(
    tipo='custom',
    destinatario=usuario,
    fecha_evento=timezone.now(),
    canales=['sms'],
    contexto_template={'mensaje': 'Prueba de SMS con Twilio'}
)

# Procesar inmediatamente
servicio_recordatorios._procesar_recordatorio(recordatorio)
```

### **3. Verificar logs:**
```bash
# Ver logs de Twilio
tail -f logs/django.log | grep -i twilio
```

## 🚨 **Solución de Problemas**

### **Error: "Account SID not found"**
```bash
# Verificar variable de entorno
echo $TWILIO_ACCOUNT_SID

# Verificar en Django
python manage.py shell
from django.conf import settings
print(settings.TWILIO_ACCOUNT_SID)
```

### **Error: "WhatsApp number not configured"**
```bash
# Verificar número de WhatsApp
echo $TWILIO_WHATSAPP_NUMBER

# El número debe ser: +14155238886 (prueba) o tu número verificado
```

### **Error: "Phone number not valid"**
```bash
# Verificar formato del número
# Debe ser: +573001234567 (Colombia)
# No: 3001234567 o 03001234567
```

### **WhatsApp no se envía**
1. **Verificar sandbox**: Los números de prueba solo funcionan con números verificados
2. **Verificar plantillas**: Usar templates aprobados por Meta
3. **Verificar horarios**: WhatsApp tiene restricciones de envío

## 📈 **Monitoreo y Métricas**

### **Dashboard de Twilio:**
- **Mensajes enviados** por día/mes
- **Tasa de entrega** por canal
- **Errores** y reintentos
- **Costos** por período

### **Logs del sistema:**
```python
# En recordatorios/services.py
logger.info(f"WhatsApp enviado via Twilio: {message.sid}")
logger.info(f"SMS enviado via Twilio: {message.sid}")
```

## 🔒 **Seguridad y Mejores Prácticas**

### **1. Proteger credenciales:**
```bash
# NUNCA commitear .env
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

### **2. Rotar tokens:**
- **Cambiar Auth Token** cada 90 días
- **Usar variables de entorno** en producción
- **No hardcodear** credenciales

### **3. Rate limiting:**
```python
# En settings.py
TWILIO_RATE_LIMIT = '100/minute'  # 100 mensajes por minuto
```

## 🎉 **Beneficios de usar Twilio**

1. **💰 Ahorro de costos**: Un proveedor para todo
2. **🚀 Simplicidad**: Una sola API para WhatsApp y SMS
3. **📊 Tracking completo**: Estado de entrega en tiempo real
4. **🌍 Cobertura global**: Funciona en todo el mundo
5. **🔧 Soporte técnico**: 24/7 en español
6. **📱 WhatsApp oficial**: Sin problemas de bloqueo

## 🚀 **Próximos pasos después de la configuración**

1. **Probar envío** de recordatorios
2. **Configurar templates** de WhatsApp
3. **Implementar webhooks** para tracking
4. **Configurar alertas** de errores
5. **Monitorear costos** y rendimiento

---

## 📞 **Soporte**

- **Twilio Support**: [support.twilio.com](https://support.twilio.com)
- **Documentación**: [twilio.com/docs](https://www.twilio.com/docs)
- **Comunidad**: [twilio.com/community](https://www.twilio.com/community)

**¿Necesitas ayuda con algún paso específico de la configuración?**
