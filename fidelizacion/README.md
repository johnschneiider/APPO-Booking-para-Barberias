# Sistema de Fidelización por WhatsApp

Sistema de fidelización que envía mensajes automáticos por WhatsApp cuando se crean reservas.

## Características

1. **Confirmación inmediata**: Envía un mensaje de confirmación cuando se crea una reserva
2. **Recordatorio 24h antes**: Envía un recordatorio 24 horas antes de la cita
3. **Recordatorio 1h antes**: Envía un recordatorio 1 hora antes de la cita

## Funcionamiento

### Sistema de Loop

El sistema utiliza un **thread con loop** que revisa periódicamente (cada 60 segundos) los mensajes programados y los envía cuando corresponde. **No requiere Celery**.

### Flujo Automático

1. Cuando se crea una reserva (señal Django `post_save`):
   - Se crea un mensaje de confirmación programado para enviar inmediatamente
   - Se crea un recordatorio programado para 24h antes de la cita
   - Se crea un recordatorio programado para 1h antes de la cita

2. El loop de procesamiento:
   - Revisa cada 60 segundos los mensajes con `estado=PROGRAMADO` y `fecha_programada <= ahora`
   - Envía los mensajes usando el servicio de WhatsApp existente
   - Marca los mensajes como enviados o fallidos según el resultado

3. Si una reserva se cancela:
   - Todos los mensajes pendientes se cancelan automáticamente

## Configuración

### 1. Instalación

La app ya está integrada en `settings.py`. Solo necesitas ejecutar las migraciones:

```bash
python manage.py makemigrations fidelizacion
python manage.py migrate
```

### 2. Configuración de WhatsApp

Asegúrate de tener configurado el servicio de WhatsApp en `settings.py`:

```python
WHATSAPP_CONFIG = {
    'ENABLED': True,
    'API_URL': 'https://api.twilio.com',
    'PHONE_NUMBER_ID': 'tu_phone_number_id',
    'ACCESS_TOKEN': 'tu_access_token',
    # ...
}
```

### 3. Verificar que el loop esté corriendo

El loop se inicia automáticamente cuando Django arranca. Puedes verificar en los logs:

```
Loop de procesamiento de mensajes iniciado
```

## Uso

### Envío Automático

Los mensajes se envían automáticamente cuando:
- Se crea una nueva reserva
- Se alcanza la fecha programada del recordatorio

### Procesamiento Manual

Si necesitas procesar mensajes manualmente:

```bash
python manage.py procesar_mensajes
```

### Administración

Puedes gestionar los mensajes desde el admin de Django:

- Ver todos los mensajes programados
- Ver estado de envío
- Ver intentos fallidos
- Cancelar mensajes manualmente

## Modelos

### MensajeFidelizacion

- `tipo`: Tipo de mensaje (confirmación, recordatorio 24h, recordatorio 1h)
- `estado`: Estado del mensaje (pendiente, programado, enviado, fallido, cancelado)
- `destinatario`: Usuario que recibirá el mensaje
- `reserva`: Reserva relacionada
- `fecha_programada`: Cuándo se debe enviar
- `fecha_envio`: Cuándo se envió realmente
- `mensaje`: Contenido del mensaje
- `intentos_envio`: Número de intentos realizados
- `error_mensaje`: Mensaje de error si falló

## Señales Django

- `post_save` en `Reserva`: Crea los mensajes cuando se crea una reserva
- `pre_delete` en `Reserva`: Cancela mensajes cuando se elimina una reserva
- `post_save` en `Reserva`: Cancela mensajes si la reserva se cancela

## Personalización

### Modificar mensajes

Edita los métodos en `fidelizacion/services.py`:

- `crear_mensaje_confirmacion()`: Mensaje de confirmación
- `crear_recordatorio_24h()`: Recordatorio 24h antes
- `crear_recordatorio_1h()`: Recordatorio 1h antes

### Modificar intervalo de revisión

En `fidelizacion/services.py`, clase `MensajeLoopService`:

```python
self.check_interval = 60  # Cambiar a los segundos deseados
```

## Troubleshooting

### El loop no se inicia

Verifica los logs de Django. El loop solo se inicia en modo producción (no en modo de migración o test).

### Los mensajes no se envían

1. Verifica que WhatsApp esté configurado correctamente
2. Verifica que el cliente tenga teléfono configurado
3. Revisa los logs para ver errores específicos
4. Verifica el estado de los mensajes en el admin

### Mensajes duplicados

El sistema evita duplicados verificando el estado de la reserva antes de enviar.

## Notas Importantes

- El loop se ejecuta en un thread daemon, se detendrá cuando el proceso principal termine
- Los mensajes se procesan en lotes de máximo 10 a la vez
- Si un mensaje falla, se reintenta hasta 3 veces antes de marcarlo como fallido
- Los mensajes se cancelan automáticamente si la reserva se cancela

