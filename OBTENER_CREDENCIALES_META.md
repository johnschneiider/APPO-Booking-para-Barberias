# 🔑 Cómo obtener credenciales de Meta WhatsApp API

## Paso 1: Acceder a Meta Business Manager

1. Ve a: https://business.facebook.com/
2. Inicia sesión con tu cuenta de Facebook Business
3. Selecciona tu **WhatsApp Business Account (WABA)**: "Appo" (ID: 1404338604602662)

## Paso 2: Obtener Phone Number ID

1. En **Meta Business Manager**, ve a:
   - **WhatsApp Manager** → **Phone numbers**
   - O directamente: https://business.facebook.com/wa/manage/phone-numbers/
2. Selecciona el número que quieres usar
3. Copia el **Phone Number ID** (es un número largo como: `123456789012345`)

**O desde la URL cuando estés viendo el número:**
- Si la URL es: `https://business.facebook.com/wa/manage/phone-numbers/123456789012345/`
- El **Phone Number ID** es: `123456789012345`

## Paso 3: Obtener Access Token

### Opción A: Token temporal (para pruebas rápidas)

1. Ve a: https://developers.facebook.com/
2. Selecciona tu **App** de WhatsApp Business
3. Ve a: **WhatsApp** → **API Setup**
4. En **Temporary access token**, haz clic en **Copy**
5. Este token expira en 24 horas (solo para pruebas)

### Opción B: Token permanente (para producción)

1. En **Meta Business Manager**, ve a:
   - **Settings** → **Business Settings** → **WhatsApp Accounts**
   - O: https://business.facebook.com/settings/whatsapp-accounts
2. Selecciona tu **WhatsApp Business Account**
3. Ve a: **WhatsApp Manager** → **API Setup**
4. En **System user access token**:
   - Si no tienes un System User, créalo:
     - **Business Settings** → **System Users** → **Add**
     - Permisos: `whatsapp_business_messaging`, `whatsapp_business_management`
   - Genera un token con permisos:
     - `whatsapp_business_messaging`
     - `whatsapp_business_management`
5. Copia el **Access Token** (empieza con `EAAB...` o `EAA...`)

## Paso 4: Verificar API Version

- Actualmente Meta usa: `v21.0` o `v22.0`
- Puedes verificarlo en: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started

## Paso 5: Configurar en .env

Agrega estas variables a tu `.env`:

```env
META_WHATSAPP_ENABLED=True
META_WHATSAPP_PHONE_NUMBER_ID=tu_phone_number_id_aqui
META_WHATSAPP_ACCESS_TOKEN=tu_access_token_aqui
META_WHATSAPP_API_VERSION=v21.0
META_WHATSAPP_VERIFY_TOKEN=appo_whatsapp_verify_2024
META_WHATSAPP_WEBHOOK_SECRET=appo_webhook_secret_2024
```

## Verificar que todo funciona

Después de configurar, prueba con:

```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); import django; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings'); django.setup(); from clientes.utils import get_whatsapp_service; ws = get_whatsapp_service(); print('Servicio:', ws.__class__.__name__); print('Habilitado:', ws.is_enabled());"
```

Si ves `MetaWhatsAppService` y `True`, está funcionando.
