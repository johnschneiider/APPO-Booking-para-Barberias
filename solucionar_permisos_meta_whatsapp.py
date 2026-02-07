#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar y ayudar a resolver problemas de permisos en Meta WhatsApp
"""

print("="*60)
print("SOLUCION PARA ERROR DE PERMISOS META WHATSAPP")
print("="*60)

print("""
ERROR ENCONTRADO:
-----------------
(#200) You do not have the necessary permissions to send messages 
on behalf of this WhatsApp Business Account

SOLUCION:
---------
El System User que generaste el token NO tiene acceso al WABA 
(WhatsApp Business Account) o al número de teléfono.

PASOS PARA SOLUCIONARLO:
""")

print("""
1. IR A META BUSINESS MANAGER:
   https://business.facebook.com/settings/system-users

2. SELECCIONAR TU SYSTEM USER:
   - Busca "appo_empleado" o "appo_user" (el que usaste para generar el token)
   - Haz clic en él

3. ASIGNAR ACTIVOS (Assets):
   a) En la pestaña "Activos asignados" o "Assigned Assets"
   b) Haz clic en "Asignar activos" o "Assign Assets"
   c) Selecciona:
      - Tipo: "WhatsApp Business Account"
      - Selecciona tu WABA: "Vital Mix" (o el nombre de tu WABA)
      - Permisos: Marca "Control total" o al menos:
        * whatsapp_business_messaging
        * whatsapp_business_management

4. GENERAR NUEVO TOKEN:
   a) Después de asignar los activos, vuelve a hacer clic en "Generar token"
   b) Asegúrate de seleccionar:
      - El WABA que acabas de asignar
      - Permisos: whatsapp_business_messaging
   c) COPIA EL TOKEN INMEDIATAMENTE (solo se muestra una vez)
   d) Actualiza TOKEN_WHATSAPP en tu .env con el nuevo token

5. VERIFICAR QUE FUNCIONE:
   - Ejecuta: python probar_meta_whatsapp_completo.py
   - Debería funcionar sin el error 403

ALTERNATIVA: VERIFICAR PERMISOS ACTUALES
-----------------------------------------
Si ya asignaste los activos pero sigue fallando:
1. Ve a: https://business.facebook.com/settings/system-users
2. Selecciona tu System User
3. Verifica en "Activos asignados" que aparezca tu WABA
4. Si no aparece, asignalo de nuevo
5. Genera un nuevo token DESPUÉS de asignar el activo

NOTA IMPORTANTE:
----------------
- El System User DEBE tener acceso al WABA antes de generar el token
- Si generaste el token ANTES de asignar el WABA, el token no funcionará
- Debes generar un NUEVO token DESPUÉS de asignar el WABA
""")

print("\n" + "="*60)
print("VERIFICACION RAPIDA")
print("="*60)

print("""
Para verificar si tu System User tiene acceso:

1. Ve a: https://business.facebook.com/settings/system-users
2. Selecciona "appo_empleado" o "appo_user"
3. Ve a la pestaña "Activos asignados"
4. Deberías ver tu WABA (ej: "Vital Mix") listado ahí
5. Si NO lo ves, es el problema - asigna el activo primero

Una vez asignado el activo y generado el nuevo token, todo debería funcionar.
""")

print("\n" + "="*60)
