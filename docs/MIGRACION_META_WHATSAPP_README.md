# 📱 Migración de Twilio a Meta WhatsApp Business API

## 🎯 **¿Por qué migrar a Meta API?**

**La API oficial de Meta para WhatsApp Business** ofrece:

✅ **Costo más bajo**: Sin intermediarios, costos directos de Meta  
✅ **Mayor control**: Acceso completo a todas las funcionalidades de WhatsApp  
✅ **Mejor rendimiento**: Latencia más baja y mayor confiabilidad  
✅ **Funcionalidades avanzadas**: Botones interactivos, listas, mensajes multimedia  
✅ **Templates oficiales**: Aprobación directa de Meta  
✅ **Webhooks mejorados**: Mejor tracking de estados de mensajes  

## 🚀 **Configuración Paso a Paso**

### **Paso 1: Crear aplicación en Meta for Developers**

1. **Ir a [developers.facebook.com](https://developers.facebook.com)**
2. **Crear una nueva aplicación**:
   - Tipo: "Business"
   - Nombre: "Melissa WhatsApp"
3. **Agregar producto WhatsApp Business API**
4. **Configurar número de teléfono**:
   - Verificar número de teléfono
   - Obtener `PHONE_NUMBER_ID`

### **Paso 2: Obtener credenciales**

En tu aplicación de Meta:

1. **WhatsApp > API Setup**:
   - Copiar `Phone Number ID`
   - Copiar `Access Token` (temporal o permanente)

2. **WhatsApp > Configuration**:
   - Configurar `Webhook URL`: `https://tu-dominio.com/clientes/meta-whatsapp/webhook/`
   - Configurar `Verify Token`: Tu token personalizado
   - Suscribirse a eventos: `messages`, `message_deliveries`, `message_reads`

### **Paso 3: Configurar variables de entorno**

Crear archivo `.env` o actualizar `env_production.txt`:

```bash
# Configuración de WhatsApp Business API de Meta
META_WHATSAPP_ENABLED=True
META_WHATSAPP_PHONE_NUMBER_ID=123456789012345
META_WHATSAPP_ACCESS_TOKEN=EAABwzLixnjYBO...
META_WHATSAPP_VERIFY_TOKEN=tu_token_verificacion_personalizado
META_WHATSAPP_WEBHOOK_SECRET=tu_secreto_webhook_personalizado
META_WHATSAPP_WEBHOOK_URL=https://tu-dominio.com/clientes/meta-whatsapp/webhook/

# Twilio (mantener solo para SMS si es necesario)
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
TWILIO_AUTH_TOKEN=tu-auth-token-aqui
TWILIO_SMS_NUMBER=+1234567890
```

### **Paso 4: Crear templates de WhatsApp**

En Meta Business Manager:

1. **WhatsApp Manager > Message Templates**
2. **Crear templates** para cada tipo de mensaje:

#### **Template: `reserva_confirmada_template`**
```
¡Hola {{1}}! 👋

Tu reserva ha sido confirmada:

📍 Negocio: {{2}}
💇‍♀️ Servicio: {{3}}
📅 Fecha: {{4}}
🕐 Hora: {{5}}

¡Te esperamos! ✨
```

#### **Template: `recordatorio_dia_antes_template`**
```
Hola {{1}}! 😊

Recordatorio: Tienes una cita mañana:

📍 {{2}}
📅 {{3}}
🕐 {{4}}

¡No olvides tu cita! 💅
```

#### **Template: `recordatorio_tres_horas_template`**
```
¡Hola {{1}}! ⏰

Tu cita es en 3 horas:

📍 {{2}}
📅 {{3}}
🕐 {{4}}

¡Nos vemos pronto! ✨
```

### **Paso 5: Probar la migración**

#### **1. Verificar webhook:**
```bash
curl -X GET "https://tu-dominio.com/clientes/meta-whatsapp/verify/?hub.mode=subscribe&hub.verify_token=tu_token&hub.challenge=test"
```

#### **2. Probar envío de mensaje:**
```python
# En Django shell
from clientes.meta_whatsapp_service import meta_whatsapp_service

resultado = meta_whatsapp_service.send_text_message(
    "+573001234567",
    "¡Hola! Este es un mensaje de prueba de Meta WhatsApp API"
)

print(resultado)
```

#### **3. Probar recordatorios:**
```python
# En Django shell
from recordatorios.services import servicio_recordatorios
from cuentas.models import UsuarioPersonalizado

usuario = UsuarioPersonalizado.objects.first()
if usuario and usuario.telefono:
    resultado = servicio_recordatorios._enviar_whatsapp(
        recordatorio, 
        {'mensaje': 'Prueba de recordatorio con Meta API'}
    )
    print(f"Recordatorio enviado: {resultado}")
```

## 📊 **Comparación de Costos**

### **Twilio (antes):**
- WhatsApp: $0.005 por mensaje
- SMS: $0.0075 por mensaje
- **Total para 1000 mensajes: $12.50**

### **Meta API (ahora):**
- WhatsApp: $0.005 por mensaje (directo de Meta)
- SMS: $0.0075 por mensaje (Twilio solo para SMS)
- **Total para 1000 mensajes: $12.50** (mismo costo, mejor control)

## 🔧 **Funcionalidades Nuevas Disponibles**

### **1. Mensajes Interactivos**
```python
# Botones
interactive_data = {
    "type": "button",
    "body": {"text": "¿Qué necesitas?"},
    "action": {
        "buttons": [
            {"type": "reply", "reply": {"id": "reservas", "title": "Ver Reservas"}},
            {"type": "reply", "reply": {"id": "ayuda", "title": "Ayuda"}}
        ]
    }
}

meta_whatsapp_service.send_interactive_message(telefono, interactive_data)
```

### **2. Listas Interactivas**
```python
# Listas desplegables
interactive_data = {
    "type": "list",
    "body": {"text": "Selecciona una opción:"},
    "action": {
        "button": "Ver opciones",
        "sections": [{
            "title": "Reservas",
            "rows": [
                {"id": "ver_reservas", "title": "Ver mis reservas"},
                {"id": "nueva_reserva", "title": "Nueva reserva"}
            ]
        }]
    }
}
```

### **3. Tracking de Estados**
```python
# Verificar estado de mensaje
estado = meta_whatsapp_service.get_message_status(message_id)
print(f"Estado: {estado}")
```

## 🚨 **Solución de Problemas**

### **Error: "Phone number not found"**
```bash
# Verificar configuración
echo $META_WHATSAPP_PHONE_NUMBER_ID
echo $META_WHATSAPP_ACCESS_TOKEN
```

### **Error: "Template not found"**
1. Verificar que el template esté aprobado en Meta Business Manager
2. Verificar el nombre exacto del template
3. Verificar que el template esté en el idioma correcto

### **Error: "Webhook verification failed"**
1. Verificar que `META_WHATSAPP_VERIFY_TOKEN` coincida
2. Verificar que la URL del webhook sea HTTPS
3. Verificar que el webhook esté configurado correctamente en Meta

### **Error: "Message not sent"**
1. Verificar que el número de teléfono esté en formato internacional (+57...)
2. Verificar que el número esté registrado en WhatsApp
3. Verificar que el template tenga los parámetros correctos

## 📈 **Monitoreo y Métricas**

### **Dashboard de Meta Business Manager:**
- Mensajes enviados por día/mes
- Tasa de entrega
- Tasa de lectura
- Errores y reintentos

### **Logs del sistema:**
```python
# En settings.py
LOGGING = {
    'loggers': {
        'clientes.meta_whatsapp_service': {
            'level': 'INFO',
            'handlers': ['file'],
        },
    },
}
```

## 🔄 **Migración Gradual**

### **Fase 1: Implementación paralela**
- Meta API activa junto con Twilio
- Pruebas en entorno de desarrollo
- Validación de funcionalidades

### **Fase 2: Migración de recordatorios**
- Cambiar sistema de recordatorios a Meta API
- Mantener Twilio solo para SMS
- Monitorear rendimiento

### **Fase 3: Migración completa**
- Desactivar Twilio para WhatsApp
- Usar solo Meta API
- Optimizar costos

## 🎉 **Beneficios de la Migración**

1. **💰 Control total de costos**: Sin intermediarios
2. **🚀 Mejor rendimiento**: Latencia más baja
3. **📱 Funcionalidades avanzadas**: Botones, listas, multimedia
4. **🔧 Mayor control**: Configuración directa con Meta
5. **📊 Mejores métricas**: Dashboard oficial de Meta
6. **🛡️ Mayor seguridad**: Verificación de webhooks mejorada

## 🚀 **Próximos Pasos**

1. **Configurar aplicación en Meta for Developers**
2. **Obtener credenciales y configurar variables de entorno**
3. **Crear y aprobar templates de WhatsApp**
4. **Probar webhooks y envío de mensajes**
5. **Migrar sistema de recordatorios**
6. **Monitorear rendimiento y costos**
7. **Desactivar Twilio para WhatsApp (opcional)**

---

## 📞 **Soporte**

- **Meta for Developers**: [developers.facebook.com](https://developers.facebook.com)
- **Documentación WhatsApp Business API**: [developers.facebook.com/docs/whatsapp](https://developers.facebook.com/docs/whatsapp)
- **Comunidad**: [developers.facebook.com/community](https://developers.facebook.com/community)

**¿Necesitas ayuda con algún paso específico de la migración?**
