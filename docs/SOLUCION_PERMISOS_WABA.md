# SOLUCIÓN: Error 403 - Permisos WABA

## Problema Identificado
El System User `appo_user` tiene permisos correctos, pero el token NO está asociado a un WABA específico.

## Solución Paso a Paso

### Paso 1: Asignar WABA al System User (si no lo hiciste)

1. Ve a: https://business.facebook.com/settings/system-users
2. Selecciona "appo_user" (ID: 122093094417221420)
3. Ve a la pestaña "Activos asignados" o "Assigned Assets"
4. Verifica que aparezca el WABA "Vital Mix" (ID: 122157641048829165)
5. Si NO aparece:
   - Haz clic en "Asignar activos" o "Assign Assets"
   - Selecciona: "WhatsApp Business Account"
   - Busca y selecciona: "Vital Mix"
   - Permisos: "Control total" o al menos:
     - whatsapp_business_messaging
     - whatsapp_business_management
   - Guarda

### Paso 2: GENERAR NUEVO TOKEN (IMPORTANTE)

**CRUCIAL: El token debe generarse DESPUÉS de asignar el WABA**

1. Con "appo_user" seleccionado, haz clic en **"Generar token"** o **"Generate token"**
2. En la ventana modal que aparece:
   
   **PASO CRÍTICO**: Debes SELECCIONAR el WABA "Vital Mix":
   - Busca en la lista de activos: **"Vital Mix"** o **"122157641048829165"**
   - **MÁRCALO/SELECCIÓNALO** (debe aparecer un check o estar seleccionado)
   - Permisos: Marca **"whatsapp_business_messaging"**
   
3. Haz clic en "Generar" o "Generate"
4. **COPIA EL TOKEN INMEDIATAMENTE** (solo se muestra una vez)
5. Actualiza `TOKEN_WHATSAPP` en tu `.env`

### Paso 3: Verificar que el token esté asociado al WABA

El token debe estar asociado al WABA, no solo tener los permisos. Cuando generas el token:
- Si ves una lista de "Assets" o "Activos", DEBES seleccionar "Vital Mix"
- Si no ves la lista o no seleccionaste el WABA, el token no funcionará

### Paso 4: Verificar en WhatsApp Manager

1. Ve a: https://business.facebook.com/wa/manage/phone-numbers/
2. Verifica que el número 15558371742 esté en tu WABA "Vital Mix"
3. Si el número está en otro WABA, ese es el problema - necesitas usar ese WABA o mover el número

## Verificación Final

Después de generar el nuevo token, ejecuta:

```bash
python verificar_permisos_token_detallado.py
```

Deberías ver:
- ✅ Permisos granted
- ✅ Acceso al Phone Number ID
- ✅ Acceso de lectura al WABA "Vital Mix" (sin error 400)
- ✅ Lista de números desde el WABA funciona

Si aún falla, el problema puede ser que el número 15558371742 esté en otro WABA diferente a "Vital Mix".
