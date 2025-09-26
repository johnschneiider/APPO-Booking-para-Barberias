from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Verifica el estado de la base de datos'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Verificando estado de la base de datos...")
        
        try:
            # Verificar conexión
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                
            if result and result[0] == 1:
                self.stdout.write(
                    self.style.SUCCESS("✅ Conexión a la base de datos exitosa")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Error en la conexión a la base de datos")
                )
                return
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error conectando a la base de datos: {str(e)}")
            )
            return
            
        # Verificar configuración
        self.stdout.write(f"📊 Configuración de base de datos:")
        self.stdout.write(f"   - ENGINE: {settings.DATABASES['default']['ENGINE']}")
        self.stdout.write(f"   - NAME: {settings.DATABASES['default']['NAME']}")
        self.stdout.write(f"   - HOST: {settings.DATABASES['default'].get('HOST', 'N/A')}")
        self.stdout.write(f"   - PORT: {settings.DATABASES['default'].get('PORT', 'N/A')}")
        
        # Verificar sesiones
        self.stdout.write(f"🔐 Configuración de sesiones:")
        self.stdout.write(f"   - ENGINE: {getattr(settings, 'SESSION_ENGINE', 'N/A')}")
        self.stdout.write(f"   - SAVE_EVERY_REQUEST: {getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', 'N/A')}")
        
        # Verificar caché
        self.stdout.write(f"💾 Configuración de caché:")
        self.stdout.write(f"   - BACKEND: {settings.CACHES['default']['BACKEND']}")
        
        self.stdout.write(
            self.style.SUCCESS("✅ Verificación completada")
        ) 