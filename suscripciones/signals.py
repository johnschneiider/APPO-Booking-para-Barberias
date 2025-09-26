from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Suscripcion, 
    PagoSuscripcion, 
    HistorialSuscripcion,
    PlanSuscripcion
)

@receiver(post_save, sender=Suscripcion)
def crear_historial_suscripcion(sender, instance, created, **kwargs):
    """Crear entrada en el historial cuando se crea o modifica una suscripción"""
    if created:
        accion = 'creada'
        descripcion = f"Suscripción creada al plan {instance.plan.nombre}"
    else:
        accion = 'estado_cambiado'
        descripcion = f"Estado cambiado a {instance.estado}"
    
    HistorialSuscripcion.objects.create(
        suscripcion=instance,
        accion=accion,
        descripcion=descripcion,
        usuario_responsable=instance.cliente
    )

@receiver(post_save, sender=PagoSuscripcion)
def manejar_pago_completado(sender, instance, created, **kwargs):
    """Manejar cuando se completa un pago"""
    if not created and instance.estado == 'completado':
        # Crear entrada en el historial
        HistorialSuscripcion.objects.create(
            suscripcion=instance.suscripcion,
            accion='pago_realizado',
            descripcion=f"Pago completado: ${instance.monto} {instance.moneda}",
            usuario_responsable=instance.suscripcion.cliente
        )
        
        # Enviar email de confirmación
        if hasattr(settings, 'SEND_EMAILS') and settings.SEND_EMAILS:
            try:
                send_mail(
                    subject=f'Pago Confirmado - {instance.suscripcion.plan.nombre}',
                    message=f'''
                    Hola {instance.suscripcion.cliente.get_full_name()},
                    
                    Tu pago de ${instance.monto} {instance.moneda} ha sido confirmado.
                    Tu suscripción al plan {instance.suscripcion.plan.nombre} está ahora activa.
                    
                    Gracias por tu suscripción.
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[instance.suscripcion.cliente.email],
                    fail_silently=True
                )
            except Exception as e:
                print(f"Error enviando email: {e}")

@receiver(post_save, sender=Suscripcion)
def notificar_renovacion_proxima(sender, instance, **kwargs):
    """Notificar cuando la suscripción está próxima a renovarse"""
    if instance.estado == 'activa' and instance.notificar_antes_renovacion:
        if instance.fecha_fin:
            dias_restantes = (instance.fecha_fin - timezone.now()).days
            
            # Notificar 7 días antes
            if dias_restantes == 7:
                if hasattr(settings, 'SEND_EMAILS') and settings.SEND_EMAILS:
                    try:
                        send_mail(
                            subject=f'Tu suscripción se renueva en 7 días',
                            message=f'''
                            Hola {instance.cliente.get_full_name()},
                            
                            Tu suscripción al plan {instance.plan.nombre} se renovará automáticamente en 7 días.
                            Monto: ${instance.precio_actual} {instance.moneda}
                            
                            Si no deseas la renovación automática, puedes cancelar desde tu perfil.
                            ''',
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[instance.cliente.email],
                            fail_silently=True
                        )
                    except Exception as e:
                        print(f"Error enviando email de renovación: {e}")

@receiver(post_save, sender=Suscripcion)
def manejar_suscripcion_expirada(sender, instance, **kwargs):
    """Manejar suscripciones expiradas"""
    if instance.fecha_fin and instance.fecha_fin < timezone.now():
        if instance.estado == 'activa':
            instance.estado = 'expirada'
            instance.save()
            
            # Crear entrada en el historial
            HistorialSuscripcion.objects.create(
                suscripcion=instance,
                accion='estado_cambiado',
                descripcion="Suscripción expirada automáticamente",
                usuario_responsable=None
            )
            
            # Notificar al cliente
            if hasattr(settings, 'SEND_EMAILS') and settings.SEND_EMAILS:
                try:
                    send_mail(
                        subject='Tu suscripción ha expirado',
                        message=f'''
                        Hola {instance.cliente.get_full_name()},
                        
                        Tu suscripción al plan {instance.plan.nombre} ha expirado.
                        Para continuar disfrutando de los beneficios, renueva tu suscripción.
                        
                        Gracias por tu preferencia.
                        ''',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[instance.cliente.email],
                        fail_silently=True
                    )
                except Exception as e:
                    print(f"Error enviando email de expiración: {e}")

@receiver(post_delete, sender=Suscripcion)
def crear_historial_eliminacion(sender, instance, **kwargs):
    """Crear entrada en el historial cuando se elimina una suscripción"""
    HistorialSuscripcion.objects.create(
        suscripcion=instance,
        accion='cancelada',
        descripcion="Suscripción eliminada del sistema",
        usuario_responsable=None
    )
