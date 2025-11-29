# Sistema de Notificaciones y Recordatorios

## 📋 Descripción

Este módulo centraliza **todas las notificaciones por WhatsApp** de la aplicación APPO. 

Las notificaciones se envían automáticamente cuando:
- ✅ Se **agenda** una cita
- ❌ Se **cancela** una cita
- 📅 Se **reprograma** una cita

## 🚀 Uso Rápido

Las notificaciones son **automáticas**. No necesitas hacer nada adicional cuando creas, cancelas o reprogramas una reserva desde el código existente.

```python
# Esto ya envía la notificación automáticamente:
reserva = Reserva.objects.create(
    cliente=cliente,
    peluquero=negocio,
    fecha=fecha,
    hora_inicio=hora_inicio,
    hora_fin=hora_fin,
    servicio=servicio
)
# ✅ Notificación de "cita agendada" enviada automáticamente

# Esto también:
reserva.estado = 'cancelado'
reserva.save()
# ✅ Notificación de "cita cancelada" enviada automáticamente

# Y esto también:
reserva.fecha = nueva_fecha
reserva.save()
# ✅ Notificación de "cita reprogramada" enviada automáticamente
```

## 📱 Uso Manual (si lo necesitas)

```python
from recordatorios import (
    notificar_cita_agendada,
    notificar_cita_cancelada,
    notificar_cita_reprogramada
)

# Notificar cita agendada
resultado = notificar_cita_agendada(reserva)

# Notificar cancelación con motivo
resultado = notificar_cita_cancelada(reserva, motivo="Cliente no disponible")

# Notificar reprogramación
resultado = notificar_cita_reprogramada(
    reserva,
    fecha_anterior=fecha_vieja,
    hora_anterior=hora_vieja
)

# Verificar resultado
if resultado['success']:
    print(f"Mensaje enviado: {resultado['message_id']}")
else:
    print(f"Error: {resultado['error']}")
```

## 🔧 Configuración

El sistema usa **Twilio** para enviar mensajes de WhatsApp. Asegúrate de tener estas variables de entorno configuradas:

```env
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_NUMBER=+14155238886  # Número de WhatsApp de Twilio
```

## 📁 Estructura de Archivos

```
recordatorios/
├── __init__.py              # Expone funciones principales
├── apps.py                  # Configuración de la app Django
├── models.py                # Modelos de recordatorios
├── signals.py               # Señales automáticas (nueva cita, cancelación, etc.)
├── whatsapp_service.py      # Servicio centralizado de WhatsApp
├── services.py              # Servicio general de recordatorios (legacy)
└── README.md                # Esta documentación
```

## 🔄 Flujo de Notificaciones

```
┌─────────────────┐
│  Nueva Reserva  │──────► Señal post_save ──────► notificar_cita_agendada()
└─────────────────┘

┌─────────────────┐
│ Reserva Modif.  │──────► Señal post_save ──────► Detectar cambio
└─────────────────┘                                      │
                                                         ▼
                              ┌─────────────────────────────────────┐
                              │ ¿Cambió fecha/hora?                 │
                              │   → notificar_cita_reprogramada()   │
                              │ ¿Estado = 'cancelado'?              │
                              │   → notificar_cita_cancelada()      │
                              └─────────────────────────────────────┘
```

## 📊 Verificar Configuración

```python
from recordatorios.whatsapp_service import notificacion_whatsapp

# Ver estado de la configuración
config = notificacion_whatsapp.verificar_configuracion()
print(config)
# {
#     'enabled': True,
#     'has_client': True,
#     'whatsapp_number': '+14155***',
#     'twilio_configured': True
# }
```

## 🧪 Verificar Señales

```python
from recordatorios.signals import verificar_conexion_signals

# Ver si las señales están conectadas
estado = verificar_conexion_signals()
print(estado)
# {
#     'connected': True,
#     'reserva_model': "<class 'clientes.models.Reserva'>",
#     'pre_save_count': 1,
#     'post_save_count': 1,
#     'post_delete_count': 1,
#     'whatsapp_enabled': True
# }
```

## 📝 Plantillas de Mensajes

Los mensajes incluyen emojis y formato para WhatsApp:

### Cita Agendada
```
🎉 ¡Hola [Nombre]!

¡Tu cita ha sido agendada con éxito! ✨

📅 *Fecha:* 15 de enero de 2025
🕐 *Hora:* 10:30
💇 *Profesional:* María García
💄 *Servicio:* Corte de cabello
📍 *Lugar:* Salón Bella

Te enviaremos un recordatorio antes de tu cita.

¡Te esperamos! 💖

_APPO - Tu agenda de belleza_
```

### Cita Cancelada
```
😔 Hola [Nombre]

Tu cita ha sido cancelada:

📅 *Fecha:* 15 de enero de 2025
🕐 *Hora:* 10:30
📍 *Lugar:* Salón Bella

📝 *Motivo:* [Motivo de cancelación]

Si deseas reagendar tu cita, puedes hacerlo desde la app.

¡Esperamos verte pronto! 💖
```

### Cita Reprogramada
```
📅 ¡Hola [Nombre]!

Tu cita ha sido reprogramada:

❌ *Fecha anterior:* 15 de enero a las 10:30

✅ *Nueva fecha:* 20 de enero de 2025
🕐 *Nueva hora:* 14:00
💇 *Profesional:* María García
📍 *Lugar:* Salón Bella

Te enviaremos un recordatorio antes de tu nueva cita.

¡Te esperamos! ✨
```

## 🔮 Próximamente (Sin Celery)

El sistema está preparado para manejar recordatorios programados sin Celery. 
Opciones alternativas para procesar recordatorios:

1. **Cron job** con `python manage.py enviar_recordatorios`
2. **APScheduler** integrado en Django
3. **Django-background-tasks**
4. **Worker manual** con loop infinito

## 🐛 Troubleshooting

### El mensaje no se envía

1. Verifica las credenciales de Twilio:
```python
from recordatorios.whatsapp_service import notificacion_whatsapp
print(notificacion_whatsapp.verificar_configuracion())
```

2. Verifica que el cliente tenga teléfono:
```python
print(reserva.cliente.telefono)  # Debe tener un número válido
```

3. Revisa los logs:
```bash
tail -f logs/melissa_activity.log | grep whatsapp
```

### Las señales no se ejecutan

1. Verifica que las señales estén conectadas:
```python
from recordatorios.signals import verificar_conexion_signals
print(verificar_conexion_signals())
```

2. Asegúrate de que `recordatorios` está en `INSTALLED_APPS` de settings.py

---

**Desarrollado para APPO** 💇‍♀️✨


