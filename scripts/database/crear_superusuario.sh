#!/bin/bash
# Script para crear superusuario de Django en producción

set -e

echo "🔐 Creando superusuario para APPO..."

cd /var/www/appo.com.co
source venv/bin/activate

# Cargar variables de entorno de forma segura
set -a
source <(grep -v '^#' .env | grep -v '^$' | grep '=' | sed 's/^/export /')
set +a

# Parámetros del superusuario
SUPERUSER_USERNAME="${1:-admin}"
SUPERUSER_EMAIL="${2:-admin@appo.com.co}"
SUPERUSER_PASSWORD="${3:-1234}"

echo "📋 Creando superusuario:"
echo "   Username: $SUPERUSER_USERNAME"
echo "   Email: $SUPERUSER_EMAIL"
echo "   Password: $SUPERUSER_PASSWORD"
echo ""

# Crear superusuario usando Django shell
python manage.py shell <<PYEOF
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = '$SUPERUSER_USERNAME'
email = '$SUPERUSER_EMAIL'
password = '$SUPERUSER_PASSWORD'

# Verificar si el usuario ya existe
if User.objects.filter(username=username).exists():
    print(f"⚠️  El usuario '{username}' ya existe. Actualizando contraseña...")
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"✅ Usuario '{username}' actualizado exitosamente")
else:
    # Crear nuevo superusuario
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"✅ Superusuario '{username}' creado exitosamente")
PYEOF

echo ""
echo "✅ Proceso completado"
echo ""
echo "📋 Puedes acceder al admin en: https://appo.com.co/admin/"
echo "   Username: $SUPERUSER_USERNAME"
echo "   Password: $SUPERUSER_PASSWORD"

