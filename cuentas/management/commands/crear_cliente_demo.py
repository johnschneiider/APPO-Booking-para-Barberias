from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea un usuario cliente de demostración'

    def handle(self, *args, **options):
        try:
            # Crear usuario cliente si no existe
            cliente_user, created = User.objects.get_or_create(
                username='cliente_demo',
                defaults={
                    'email': 'cliente_demo@demo.com',
                    'first_name': 'María',
                    'last_name': 'González',
                    'tipo': 'cliente',
                    'is_active': True
                }
            )
            
            if created:
                cliente_user.set_password('demo123')
                cliente_user.save()
                self.stdout.write(
                    self.style.SUCCESS('✅ Usuario cliente creado exitosamente!')
                )
                self.stdout.write(
                    self.style.SUCCESS('👤 Usuario: cliente_demo')
                )
                self.stdout.write(
                    self.style.SUCCESS('🔑 Contraseña: demo123')
                )
                self.stdout.write(
                    self.style.SUCCESS('📧 Email: cliente_demo@demo.com')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Usuario cliente ya existe: cliente_demo / demo123')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creando cliente demo: {str(e)}')
            )
