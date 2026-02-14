from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, timedelta
import random

from django.contrib.auth import get_user_model
from profesionales.models import Profesional, Matriculacion
from negocios.models import ServicioNegocio
from clientes.models import Reserva


User = get_user_model()


class Command(BaseCommand):
    help = "Genera reservas futuras (demo) para profesionales de poblar_demo, sin tocar usuarios reales."

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=7, help='Días hacia adelante para generar reservas (default: 7)')
        parser.add_argument('--por-dia', dest='por_dia', type=int, default=2, help='Reservas por día por profesional (default: 2)')
        parser.add_argument('--max-pros', dest='max_pros', type=int, default=50, help='Máximo de profesionales demo a usar (default: 50)')

    def handle(self, *args, **options):
        dias = max(1, options['dias'])
        por_dia = max(1, options['por_dia'])
        max_pros = max(1, options['max_pros'])

        # Clientes demo (creados por poblar_demo: cliente1..cliente20)
        clientes_demo = list(
            User.objects.filter(tipo='cliente', username__startswith='cliente').order_by('id')
        )
        if not clientes_demo:
            self.stdout.write(self.style.WARNING("No hay clientes demo (cliente1...). No se crearán reservas."))
            return

        # Profesionales demo (profesional1..., tipo profesional)
        profesionales_demo = list(
            Profesional.objects.filter(usuario__username__startswith='profesional').select_related('usuario')
        )[:max_pros]
        if not profesionales_demo:
            self.stdout.write(self.style.WARNING("No hay profesionales demo (profesional1...)."))
            return

        hoy = timezone.now().date()
        creadas = 0

        for prof in profesionales_demo:
            # Obtener un negocio donde esté aprobado
            matricula = (
                Matriculacion.objects.filter(profesional=prof, estado='aprobada')
                .select_related('negocio')
                .first()
            )
            if not matricula or not matricula.negocio:
                continue
            negocio = matricula.negocio

            servicio_negocio = (
                ServicioNegocio.objects.filter(negocio=negocio, activo=True).order_by('?').first()
            )
            if not servicio_negocio:
                continue

            for d in range(dias):
                fecha = hoy + timedelta(days=d+1)  # siempre a futuro (mañana en adelante)
                for slot in range(por_dia):
                    hora_inicio = time(9 + slot, 0)
                    hora_fin = time(9 + slot, 45)
                    cliente = random.choice(clientes_demo)

                    reserva, created = Reserva.objects.get_or_create(
                        profesional=prof,
                        peluquero=negocio,
                        cliente=cliente,
                        fecha=fecha,
                        hora_inicio=hora_inicio,
                        defaults={
                            'hora_fin': hora_fin,
                            'servicio': servicio_negocio,
                            'estado': 'confirmado',
                            'notas': 'Cita demo auto-generada (futuro).',
                        }
                    )
                    if created:
                        creadas += 1

        self.stdout.write(self.style.SUCCESS(f"Reservas futuras creadas: {creadas}"))
