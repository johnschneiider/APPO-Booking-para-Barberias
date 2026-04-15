#!/usr/bin/env python
"""
Script simple para probar el sistema de recordatorios
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

from recordatorios.models import Recordatorio, TipoRecordatorio
from cuentas.models import UsuarioPersonalizado

def test_simple():
    """Prueba simple del sistema"""
    print("🧪 Prueba simple del sistema de recordatorios...")
    
    try:
        # Verificar que el modelo funciona
        print("✅ Modelo Recordatorio importado correctamente")
        
        # Verificar tipos disponibles
        tipos = TipoRecordatorio.choices
        print(f"✅ Tipos de recordatorios: {len(tipos)}")
        
        # Verificar usuarios
        usuarios = UsuarioPersonalizado.objects.filter(telefono__isnull=False).exclude(telefono='')
        print(f"✅ Usuarios con teléfono: {usuarios.count()}")
        
        if usuarios.exists():
            usuario = usuarios.first()
            print(f"   Usuario: {usuario.email} - Tel: {usuario.telefono}")
        
        # Verificar recordatorios existentes
        recordatorios = Recordatorio.objects.all()
        print(f"✅ Recordatorios en BD: {recordatorios.count()}")
        
        print("\n🎉 Sistema básico funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    test_simple()
