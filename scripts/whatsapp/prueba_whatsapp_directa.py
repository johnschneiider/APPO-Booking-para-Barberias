#!/usr/bin/env python
"""
Prueba directa de WhatsApp Meta API
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def probar_whatsapp():
    """Prueba directa de WhatsApp"""
    print("🚀 Probando Meta WhatsApp API...")
    
    try:
        from clientes.meta_whatsapp_service import meta_whatsapp_service
        
        print(f"✅ Servicio cargado: {meta_whatsapp_service}")
        print(f"✅ Habilitado: {meta_whatsapp_service.is_enabled()}")
        print(f"✅ Phone Number ID: {meta_whatsapp_service.phone_number_id}")
        
        # Probar mensaje de texto
        print("\n📱 Enviando mensaje de prueba...")
        resultado = meta_whatsapp_service.send_text_message(
            "+573117451274",
            "¡Hola! Este es un mensaje de prueba desde Melissa 🚀"
        )
        
        print(f"Resultado: {resultado}")
        
        if resultado.get('success'):
            print("✅ ¡Mensaje enviado exitosamente!")
        else:
            print(f"❌ Error: {resultado.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_whatsapp()
