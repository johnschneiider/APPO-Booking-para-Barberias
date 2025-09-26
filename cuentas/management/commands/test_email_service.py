"""
Comando para probar el servicio de email avanzado
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from cuentas.email_service import email_service
from cuentas.models import EmailTracking
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Prueba el servicio de email avanzado con diferentes proveedores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email de destino para la prueba',
            default='test@example.com'
        )
        parser.add_argument(
            '--provider',
            type=str,
            choices=['sendgrid', 'aws_ses', 'smtp', 'auto'],
            help='Proveedor específico a probar',
            default='auto'
        )
        parser.add_argument(
            '--template',
            action='store_true',
            help='Usar template de email en lugar de texto simple'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando prueba del servicio de email avanzado...')
        )
        
        # Mostrar estado de proveedores
        self.stdout.write('\n📊 Estado de proveedores de email:')
        provider_status = email_service.get_provider_status()
        
        for provider, status in provider_status.items():
            if status['enabled']:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ {provider.upper()}: {status["status"]}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  {provider.upper()}: {status["status"]}')
                )
        
        # Email de prueba
        test_email = options['email']
        test_subject = '🧪 Prueba del Servicio de Email Avanzado - APPO'
        
        if options['template']:
            # Usar template
            test_context = {
                'usuario': 'Usuario de Prueba',
                'fecha': 'Hoy',
                'negocio': 'APPO Test',
                'accion': 'Prueba del sistema'
            }
            
            self.stdout.write('\n📧 Enviando email con template...')
            
            success = email_service.send_template_email(
                template_name='recordatorio_dia_antes',
                context=test_context,
                subject=test_subject,
                recipient_list=[test_email],
                fail_silently=False
            )
        else:
            # Email simple
            test_message = """
            Hola,
            
            Este es un email de prueba del servicio de email avanzado de APPO.
            
            Características:
            ✅ Múltiples proveedores (SendGrid, AWS SES, SMTP)
            ✅ Sistema de fallback automático
            ✅ Tracking de emails
            ✅ Templates personalizables
            ✅ Rate limiting
            ✅ Cola de emails
            
            Saludos,
            Equipo APPO
            """
            
            test_html = f"""
            <html>
            <body>
                <h2>🧪 Prueba del Servicio de Email Avanzado</h2>
                <p>Hola,</p>
                <p>Este es un email de prueba del servicio de email avanzado de <strong>APPO</strong>.</p>
                
                <h3>Características:</h3>
                <ul>
                    <li>✅ Múltiples proveedores (SendGrid, AWS SES, SMTP)</li>
                    <li>✅ Sistema de fallback automático</li>
                    <li>✅ Tracking de emails</li>
                    <li>✅ Templates personalizables</li>
                    <li>✅ Rate limiting</li>
                    <li>✅ Cola de emails</li>
                </ul>
                
                <p><strong>Saludos,<br>Equipo APPO</strong></p>
            </body>
            </html>
            """
            
            self.stdout.write('\n📧 Enviando email simple...')
            
            success = email_service.send_email(
                subject=test_subject,
                message=test_message,
                recipient_list=[test_email],
                html_message=test_html,
                fail_silently=False
            )
        
        if success:
            self.stdout.write(
                self.style.SUCCESS('✅ Email enviado exitosamente!')
            )
            
            # Mostrar tracking si está habilitado
            if getattr(settings, 'EMAIL_TRACKING_ENABLED', False):
                self.stdout.write('\n📈 Verificando tracking...')
                try:
                    tracking = EmailTracking.objects.filter(
                        recipient=test_email,
                        subject=test_subject
                    ).first()
                    
                    if tracking:
                        self.stdout.write(
                            self.style.SUCCESS(f'  📊 Tracking creado: {tracking.estado}')
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING('  ⚠️  No se encontró tracking')
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  ❌ Error verificando tracking: {e}')
                    )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Error enviando email')
            )
        
        # Mostrar estadísticas
        self.stdout.write('\n📊 Estadísticas del servicio:')
        try:
            total_emails = EmailTracking.objects.count()
            emails_enviados = EmailTracking.objects.filter(estado='enviado').count()
            emails_entregados = EmailTracking.objects.filter(estado='entregado').count()
            emails_abiertos = EmailTracking.objects.filter(estado='abierto').count()
            
            self.stdout.write(f'  📧 Total emails: {total_emails}')
            self.stdout.write(f'  📤 Enviados: {emails_enviados}')
            self.stdout.write(f'  📥 Entregados: {emails_entregados}')
            self.stdout.write(f'  👁️  Abiertos: {emails_abiertos}')
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  ⚠️  No se pudieron obtener estadísticas: {e}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Prueba completada!')
        )
