#!/usr/bin/env python
"""
Script simple para verificar y crear recordatorios manualmente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
django.setup()

def verificar_sistema():
    """Verifica el estado básico del sistema"""
    print("🔍 Verificando sistema de recordatorios...")
    
    try:
        from recordatorios.models import Recordatorio, TipoRecordatorio
        from cuentas.models import UsuarioPersonalizado
        from clientes.models import Reserva
        
        # Verificar modelos
        print("✅ Modelos importados correctamente")
        
        # Verificar tipos de recordatorios
        tipos = TipoRecordatorio.choices
        print(f"✅ Tipos de recordatorios: {len(tipos)}")
        
        # Verificar usuarios
        usuarios = UsuarioPersonalizado.objects.filter(telefono__isnull=False).exclude(telefono='')
        print(f"✅ Usuarios con teléfono: {usuarios.count()}")
        
        if usuarios.exists():
            usuario = usuarios.first()
            print(f"   Usuario: {usuario.email} - Tel: {usuario.telefono}")
        
        # Verificar reservas
        reservas = Reserva.objects.all()
        print(f"✅ Total reservas: {reservas.count()}")
        
        # Verificar recordatorios
        recordatorios = Recordatorio.objects.all()
        print(f"✅ Total recordatorios: {recordatorios.count()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando sistema: {e}")
        return False

def crear_recordatorio_manual():
    """Crea un recordatorio manualmente para probar"""
    print("\n🧪 Creando recordatorio manual...")
    
    try:
        from recordatorios.services import servicio_recordatorios
        from cuentas.models import UsuarioPersonalizado
        from clientes.models import Reserva
        
        # Buscar usuario
        usuario = UsuarioPersonalizado.objects.filter(telefono__isnull=False).exclude(telefono='').first()
        
        if not usuario:
            print("❌ No hay usuarios con teléfono")
            return False
        
        print(f"✅ Usuario: {usuario.email}")
        
        # Buscar reserva
        reserva = Reserva.objects.filter(cliente=usuario).first()
        
        if not reserva:
            print("❌ No hay reservas para este usuario")
            return False
        
        print(f"✅ Reserva: ID {reserva.id} - Fecha: {reserva.fecha}")
        
        # Crear recordatorio
        resultado = servicio_recordatorios.enviar_recordatorio_confirmacion(reserva)
        
        if resultado:
            print("✅ Recordatorio creado exitosamente")
            return True
        else:
            print("❌ Error creando recordatorio")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Función principal"""
    print("🚀 Verificando y probando sistema de recordatorios...\n")
    
    # Verificar sistema
    sistema_ok = verificar_sistema()
    
    if sistema_ok:
        # Crear recordatorio manual
        recordatorio_ok = crear_recordatorio_manual()
        
        # Resumen
        print("\n" + "="*60)
        print("📊 RESUMEN")
        print("="*60)
        print(f"  Sistema: ✅")
        print(f"  Recordatorio manual: {'✅' if recordatorio_ok else '❌'}")
        
        if recordatorio_ok:
            print("\n🎉 ¡El sistema está funcionando!")
            print("💡 El problema está en las señales automáticas")
        else:
            print("\n⚠️  El sistema tiene problemas")
    else:
        print("\n❌ El sistema no está configurado correctamente")

if __name__ == '__main__':
    main()
