from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from negocios.models import Negocio
from suscripciones.models import PlanSuscripcion, BeneficioSuscripcion
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Pobla la base de datos con planes de suscripción de ejemplo para negocios existentes'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando población de planes de suscripción...')
        
        # Obtener negocios existentes
        negocios = Negocio.objects.filter(activo=True)
        
        if not negocios.exists():
            self.stdout.write(self.style.WARNING('No hay negocios activos para crear planes'))
            return
        
        planes_creados = 0
        
        for negocio in negocios:
            self.stdout.write(f'Creando planes para: {negocio.nombre}')
            
            # Plan Básico
            plan_basico, created = PlanSuscripcion.objects.get_or_create(
                negocio=negocio,
                nombre='Básico',
                defaults={
                    'descripcion': 'Plan básico con beneficios esenciales para clientes frecuentes',
                    'precio_mensual': Decimal('29.99'),
                    'max_servicios_mes': 3,
                    'descuento_servicios': 10,
                    'prioridad_reservas': False,
                    'activo': True
                }
            )
            
            if created:
                planes_creados += 1
                self.stdout.write(f'  - Plan Básico creado: ${plan_basico.precio_mensual}')
                
                # Beneficios del plan básico
                BeneficioSuscripcion.objects.create(
                    plan=plan_basico,
                    nombre='Descuento 10% en servicios',
                    descripcion='Obtén un 10% de descuento en todos los servicios',
                    tipo_beneficio='descuento',
                    valor='10%',
                    activo=True
                )
                
                BeneficioSuscripcion.objects.create(
                    plan=plan_basico,
                    nombre='3 servicios por mes',
                    descripcion='Disfruta de hasta 3 servicios por mes',
                    tipo_beneficio='servicio_gratis',
                    valor='3 servicios',
                    activo=True
                )
            
            # Plan Premium
            plan_premium, created = PlanSuscripcion.objects.get_or_create(
                negocio=negocio,
                nombre='Premium',
                defaults={
                    'descripcion': 'Plan premium con beneficios exclusivos y prioridad en reservas',
                    'precio_mensual': Decimal('59.99'),
                    'max_servicios_mes': 6,
                    'descuento_servicios': 20,
                    'prioridad_reservas': True,
                    'activo': True
                }
            )
            
            if created:
                planes_creados += 1
                self.stdout.write(f'  - Plan Premium creado: ${plan_premium.precio_mensual}')
                
                # Beneficios del plan premium
                BeneficioSuscripcion.objects.create(
                    plan=plan_premium,
                    nombre='Descuento 20% en servicios',
                    descripcion='Obtén un 20% de descuento en todos los servicios',
                    tipo_beneficio='descuento',
                    valor='20%',
                    activo=True
                )
                
                BeneficioSuscripcion.objects.create(
                    plan=plan_premium,
                    nombre='6 servicios por mes',
                    descripcion='Disfruta de hasta 6 servicios por mes',
                    tipo_beneficio='servicio_gratis',
                    valor='6 servicios',
                    activo=True
                )
                
                BeneficioSuscripcion.objects.create(
                    plan=plan_premium,
                    nombre='Prioridad en reservas',
                    descripcion='Tus reservas tienen prioridad sobre clientes sin suscripción',
                    tipo_beneficio='prioridad',
                    valor='Prioridad alta',
                    activo=True
                )
            
            # Plan VIP
            plan_vip, created = PlanSuscripcion.objects.get_or_create(
                negocio=negocio,
                nombre='VIP',
                defaults={
                    'descripcion': 'Plan VIP con servicios ilimitados y beneficios exclusivos',
                    'precio_mensual': Decimal('99.99'),
                    'max_servicios_mes': 0,  # 0 = ilimitado
                    'descuento_servicios': 30,
                    'prioridad_reservas': True,
                    'activo': True
                }
            )
            
            if created:
                planes_creados += 1
                self.stdout.write(f'  - Plan VIP creado: ${plan_vip.precio_mensual}')
                
                # Beneficios del plan VIP
                BeneficioSuscripcion.objects.create(
                    plan=plan_vip,
                    nombre='Descuento 30% en servicios',
                    descripcion='Obtén un 30% de descuento en todos los servicios',
                    tipo_beneficio='descuento',
                    valor='30%',
                    activo=True
                )
                
                BeneficioSuscripcion.objects.create(
                    plan=plan_vip,
                    nombre='Servicios ilimitados',
                    descripcion='Disfruta de servicios ilimitados por mes',
                    tipo_beneficio='servicio_gratis',
                    valor='Ilimitado',
                    activo=True
                )
                
                BeneficioSuscripcion.objects.create(
                    plan=plan_vip,
                    nombre='Prioridad máxima en reservas',
                    descripcion='Tus reservas tienen la máxima prioridad',
                    tipo_beneficio='prioridad',
                    valor='Prioridad máxima',
                    activo=True
                )
                
                BeneficioSuscripcion.objects.create(
                    plan=plan_vip,
                    nombre='Beneficios exclusivos',
                    descripcion='Acceso a servicios y promociones exclusivas',
                    tipo_beneficio='exclusivo',
                    valor='Exclusivo',
                    activo=True
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Población completada. Se crearon {planes_creados} planes de suscripción para {negocios.count()} negocios.'
            )
        )
