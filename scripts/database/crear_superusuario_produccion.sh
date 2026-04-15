#!/bin/bash
# Script para crear superusuario en producción después de pérdida de datos

cd /var/www/appo.com.co
source venv/bin/activate

echo "🔐 Creando superusuario 'john' con contraseña '1234'..."

python manage.py shell <<PYEOF
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'john'
email = 'john@appo.com.co'
password = '1234'

# Verificar si el usuario ya existe
if User.objects.filter(username=username).exists():
    print(f"⚠️  El usuario '{username}' ya existe. Actualizando contraseña y permisos...")
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.email = email
    user.save()
    print(f"✅ Usuario '{username}' actualizado exitosamente")
else:
    # Crear nuevo superusuario
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            tipo='super_admin'
        )
        print(f"✅ Superusuario '{username}' creado exitosamente")
    except Exception as e:
        print(f"❌ Error al crear superusuario: {e}")
        # Intentar crear sin tipo personalizado
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f"✅ Superusuario '{username}' creado exitosamente (sin tipo personalizado)")
PYEOF

echo ""
echo "✅ Proceso completado"
echo ""
echo "📋 Puedes acceder al admin en: https://appo.com.co/admin/"
echo "   Username: john"
echo "   Password: 1234"
