#!/bin/bash
# Script para configurar SocialApps de django-allauth

set -e

echo "🔧 Configurando SocialApps para django-allauth..."

cd /var/www/appo.com.co
source venv/bin/activate

# Cargar variables de entorno de forma segura
set -a
source <(grep -v '^#' .env | grep -v '^$' | grep '=' | sed 's/^/export /')
set +a

# Leer credenciales del .env
GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-}"
GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET:-}"

python manage.py shell <<PYEOF
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'melissa.settings')
import django
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

# Obtener el sitio actual
site = Site.objects.get_current()

# Configurar Google si hay credenciales
if '$GOOGLE_CLIENT_ID' and '$GOOGLE_CLIENT_SECRET':
    google_app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Google',
            'client_id': '$GOOGLE_CLIENT_ID',
            'secret': '$GOOGLE_CLIENT_SECRET',
        }
    )
    if created:
        print("✅ SocialApp de Google creada")
    else:
        google_app.client_id = '$GOOGLE_CLIENT_ID'
        google_app.secret = '$GOOGLE_CLIENT_SECRET'
        google_app.save()
        print("✅ SocialApp de Google actualizada")
    
    # Asociar con el sitio
    if site not in google_app.sites.all():
        google_app.sites.add(site)
        print("✅ SocialApp de Google asociada con el sitio")
else:
    print("⚠️  No hay credenciales de Google configuradas en .env")
    print("   Para habilitar login con Google, configura:")
    print("   GOOGLE_CLIENT_ID=tu-client-id")
    print("   GOOGLE_CLIENT_SECRET=tu-client-secret")

print(f"\n✅ Configuración completada para el sitio: {site.domain}")
PYEOF

echo ""
echo "✅ Proceso completado"

