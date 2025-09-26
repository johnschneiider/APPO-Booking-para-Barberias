from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from negocios.models import Negocio
from suscripciones.models import PlanSuscripcion, BeneficioSuscripcion
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea un negocio de demostración con planes de suscripción'

    def handle(self, *args, **options):
        try:
            # Crear usuario negocio si no existe
            negocio_user, created = User.objects.get_or_create(
                username='negocio_demo',
                defaults={
                    'email': 'negocio_demo@demo.com',
                    'first_name': 'Salón',
                    'last_name': 'Demo',
                    'tipo': 'negocio',
                    'is_active': True
                }
            )
            
            if created:
                negocio_user.set_password('demo123')
                negocio_user.save()
                self.stdout.write(
                    self.style.SUCCESS('Usuario negocio creado: negocio_demo / demo123')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Usuario negocio ya existe: negocio_demo / demo123')
                )

            # Crear negocio si no existe
            negocio, created = Negocio.objects.get_or_create(
                nombre='Salón de Belleza "Glamour"',
                defaults={
                    'propietario': negocio_user,
                    'descripcion': 'Salón de belleza premium con los mejores profesionales y servicios de calidad.',
                    'direccion': 'Cra. 29 #42a-10, Cali, Valle del Cauca',
                    'ciudad': 'Cali',
                    'provincia': 'Valle del Cauca',
                    'telefono': '+57 300 123 4567',
                    'email': 'info@glamour.com',
                    'activo': True,
                    'categoria': 'peluqueria',
                    'horario_apertura': '09:00:00',
                    'horario_cierre': '18:00:00',
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Negocio creado: {negocio.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Negocio ya existe: {negocio.nombre}')
                )

            # Crear planes de suscripción usando los campos correctos del modelo
            planes_data = [
                {
                    'nombre': 'Plan Básico',
                    'descripcion': 'Acceso a servicios básicos de peluquería',
                    'precio_mensual': 88.00,
                    'max_servicios_mes': 1,
                    'descuento_servicios': 10,
                    'prioridad_reservas': False,
                    'beneficios': [
                        '1 corte de cabello por mes',
                        'Descuento del 10% en productos',
                        'Acceso prioritario a reservas',
                        'Newsletter con tips de belleza'
                    ]
                },
                {
                    'nombre': 'Plan Premium',
                    'descripcion': 'Servicios completos de belleza y tratamientos especiales',
                    'precio_mensual': 150.00,
                    'max_servicios_mes': 2,
                    'descuento_servicios': 20,
                    'prioridad_reservas': True,
                    'beneficios': [
                        '2 servicios por mes (corte, color, peinado)',
                        'Descuento del 20% en productos',
                        'Reservas prioritarias',
                        'Tratamientos especiales incluidos',
                        'Acceso a eventos exclusivos',
                        'Consultas personalizadas'
                    ]
                },
                {
                    'nombre': 'Plan VIP',
                    'descripcion': 'Experiencia premium con todos los servicios incluidos',
                    'precio_mensual': 250.00,
                    'max_servicios_mes': 0,  # 0 = ilimitado
                    'descuento_servicios': 30,
                    'prioridad_reservas': True,
                    'beneficios': [
                        'Servicios ilimitados por mes',
                        'Descuento del 30% en productos',
                        'Reservas VIP con horarios exclusivos',
                        'Tratamientos premium incluidos',
                        'Acceso a masterclass',
                        'Productos de regalo mensuales',
                        'Soporte personalizado 24/7'
                    ]
                }
            ]

            for plan_data in planes_data:
                beneficios = plan_data.pop('beneficios')
                
                plan, created = PlanSuscripcion.objects.get_or_create(
                    nombre=plan_data['nombre'],
                    negocio=negocio,
                    defaults=plan_data
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Plan creado: {plan.nombre} - ${plan.precio_mensual}')
                    )
                    
                    # Crear beneficios del plan
                    for beneficio_desc in beneficios:
                        BeneficioSuscripcion.objects.create(
                            plan=plan,
                            descripcion=beneficio_desc
                        )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'  - {len(beneficios)} beneficios creados')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Plan ya existe: {plan.nombre}')
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Negocio de demostración configurado exitosamente!\n'
                    f'📱 URL pública: /clientes/peluquero/{negocio.id}/\n'
                    f'👤 Usuario: negocio_demo / demo123\n'
                    f'🏪 Negocio: {negocio.nombre}\n'
                    f'📋 Planes: {PlanSuscripcion.objects.filter(negocio=negocio).count()} creados'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creando negocio demo: {str(e)}')
            )
