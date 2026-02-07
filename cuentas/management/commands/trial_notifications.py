from django.core.management.base import BaseCommand
from django.utils import timezone
from cuentas.models import BusinessCheckoutIntent


class Command(BaseCommand):
    help = "Envía avisos de trial próximo a vencer y registra intentos de cobro fallidos (placeholder)."

    def handle(self, *args, **options):
        hoy = timezone.now()
        en_tres_dias = hoy + timezone.timedelta(days=3)

        # Aviso 3 días antes de fin de trial
        trials_pronto = BusinessCheckoutIntent.objects.filter(
            trial_fin__date=en_tres_dias.date(),
            auto_cobro=True,
        )
        for intent in trials_pronto:
            self.stdout.write(f"[Aviso trial] {intent.email_contacto} vence el {intent.trial_fin.date()} (negocio: {intent.nombre_negocio})")

        # Placeholder para fallos de cobro (no hay integración real)
        fallos = BusinessCheckoutIntent.objects.filter(payu_state='pendiente')
        for intent in fallos:
            self.stdout.write(f"[Cobro fallido placeholder] {intent.email_contacto} (negocio: {intent.nombre_negocio}) - reintentar 2 veces/día.")
