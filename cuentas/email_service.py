"""
Servicio de Email Avanzado para APPO
Integra SendGrid (principal) y AWS SES (respaldo) con sistema de fallback
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Union
from django.conf import settings
from django.core.mail import send_mail as django_send_mail
from django.template.loader import render_to_string
from django.utils import timezone
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent, TextContent
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import json
import time

logger = logging.getLogger(__name__)

class EmailService:
    """
    Servicio de email avanzado con múltiples proveedores y sistema de fallback
    """
    
    def __init__(self):
        self.sendgrid_enabled = bool(settings.SENDGRID_API_KEY)
        self.aws_ses_enabled = bool(settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY)
        self.smtp_enabled = bool(settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)
        
        # Inicializar clientes
        if self.sendgrid_enabled:
            try:
                self.sendgrid_client = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
                logger.info("SendGrid client inicializado correctamente")
            except Exception as e:
                logger.error(f"Error inicializando SendGrid: {e}")
                self.sendgrid_enabled = False
        
        if self.aws_ses_enabled:
            try:
                self.ses_client = boto3.client(
                    'ses',
                    region_name=settings.AWS_SES_REGION_NAME,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
                logger.info("AWS SES client inicializado correctamente")
            except Exception as e:
                logger.error(f"Error inicializando AWS SES: {e}")
                self.aws_ses_enabled = False
    
    def send_email(
        self,
        subject: str,
        message: str,
        recipient_list: List[str],
        from_email: Optional[str] = None,
        html_message: Optional[str] = None,
        fail_silently: bool = False,
        template_name: Optional[str] = None,
        context: Optional[Dict] = None,
        attachments: Optional[List[Dict]] = None,
        tracking_enabled: bool = None
    ) -> bool:
        """
        Envía email usando el mejor proveedor disponible con sistema de fallback
        """
        if tracking_enabled is None:
            tracking_enabled = getattr(settings, 'EMAIL_TRACKING_ENABLED', True)
        
        # Preparar datos del email
        email_data = {
            'subject': subject,
            'message': message,
            'recipient_list': recipient_list,
            'from_email': from_email or settings.DEFAULT_FROM_EMAIL,
            'html_message': html_message,
            'attachments': attachments or [],
            'tracking_enabled': tracking_enabled
        }
        
        # Intentar con SendGrid primero (mejor rendimiento)
        if self.sendgrid_enabled:
            try:
                if self._send_with_sendgrid(email_data):
                    logger.info(f"Email enviado exitosamente con SendGrid a {len(recipient_list)} destinatarios")
                    return True
            except Exception as e:
                logger.warning(f"Error con SendGrid, intentando AWS SES: {e}")
        
        # Intentar con AWS SES como respaldo
        if self.aws_ses_enabled:
            try:
                if self._send_with_aws_ses(email_data):
                    logger.info(f"Email enviado exitosamente con AWS SES a {len(recipient_list)} destinatarios")
                    return True
            except Exception as e:
                logger.warning(f"Error con AWS SES, intentando SMTP: {e}")
        
        # Intentar con SMTP como último recurso
        if self.smtp_enabled:
            try:
                if self._send_with_smtp(email_data):
                    logger.info(f"Email enviado exitosamente con SMTP a {len(recipient_list)} destinatarios")
                    return True
            except Exception as e:
                logger.error(f"Error con SMTP: {e}")
        
        # Si llegamos aquí, ningún método funcionó
        error_msg = "Todos los métodos de envío de email fallaron"
        logger.error(error_msg)
        
        if not fail_silently:
            raise Exception(error_msg)
        
        return False
    
    def _send_with_sendgrid(self, email_data: Dict) -> bool:
        """Envía email usando SendGrid"""
        try:
            # Crear mensaje SendGrid
            from_email = Email(email_data['from_email'])
            to_emails = [To(email) for email in email_data['recipient_list']]
            
            # Crear contenido
            if email_data['html_message']:
                content = HtmlContent(email_data['html_message'])
            else:
                content = TextContent(email_data['message'])
            
            # Crear mail
            mail = Mail(from_email, to_emails, email_data['subject'], content)
            
            # Agregar tracking si está habilitado
            if email_data['tracking_enabled']:
                mail.tracking_settings = {
                    'click_tracking': {
                        'enable': getattr(settings, 'EMAIL_CLICK_TRACKING', True),
                        'enable_text': True
                    },
                    'open_tracking': {
                        'enable': getattr(settings, 'EMAIL_OPEN_TRACKING', True)
                    }
                }
            
            # Enviar
            response = self.sendgrid_client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                logger.debug(f"SendGrid response: {response.status_code}")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando con SendGrid: {e}")
            return False
    
    def _send_with_aws_ses(self, email_data: Dict) -> bool:
        """Envía email usando AWS SES"""
        try:
            # Preparar destinatarios
            destination = {
                'ToAddresses': email_data['recipient_list']
            }
            
            # Preparar contenido
            if email_data['html_message']:
                message = {
                    'Subject': {
                        'Data': email_data['subject'],
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': email_data['html_message'],
                            'Charset': 'UTF-8'
                        },
                        'Text': {
                            'Data': email_data['message'],
                            'Charset': 'UTF-8'
                        }
                    }
                }
            else:
                message = {
                    'Subject': {
                        'Data': email_data['subject'],
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Text': {
                            'Data': email_data['message'],
                            'Charset': 'UTF-8'
                        }
                    }
                }
            
            # Enviar email
            response = self.ses_client.send_email(
                Source=email_data['from_email'],
                Destination=destination,
                Message=message
            )
            
            logger.debug(f"AWS SES response: {response}")
            return True
            
        except ClientError as e:
            logger.error(f"AWS SES ClientError: {e}")
            return False
        except Exception as e:
            logger.error(f"Error enviando con AWS SES: {e}")
            return False
    
    def _send_with_smtp(self, email_data: Dict) -> bool:
        """Envía email usando SMTP tradicional"""
        try:
            # Usar Django send_mail como fallback
            return django_send_mail(
                subject=email_data['subject'],
                message=email_data['message'],
                from_email=email_data['from_email'],
                recipient_list=email_data['recipient_list'],
                html_message=email_data['html_message'],
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Error enviando con SMTP: {e}")
            return False
    
    def send_template_email(
        self,
        template_name: str,
        context: Dict,
        subject: str,
        recipient_list: List[str],
        from_email: Optional[str] = None,
        fail_silently: bool = False
    ) -> bool:
        """
        Envía email usando un template específico
        """
        try:
            # Renderizar templates
            html_template = f'emails/{template_name}.html'
            text_template = f'emails/{template_name}.txt'
            
            html_content = render_to_string(html_template, context)
            text_content = render_to_string(text_template, context)
            
            # Enviar email
            return self.send_email(
                subject=subject,
                message=text_content,
                recipient_list=recipient_list,
                from_email=from_email,
                html_message=html_content,
                fail_silently=fail_silently
            )
            
        except Exception as e:
            logger.error(f"Error enviando email con template {template_name}: {e}")
            if not fail_silently:
                raise
            return False
    
    def send_bulk_email(
        self,
        subject: str,
        message: str,
        recipient_list: List[str],
        from_email: Optional[str] = None,
        html_message: Optional[str] = None,
        batch_size: int = None,
        delay: int = None
    ) -> Dict[str, int]:
        """
        Envía emails en lotes para mejor rendimiento
        """
        if batch_size is None:
            batch_size = getattr(settings, 'EMAIL_QUEUE_BATCH_SIZE', 100)
        
        if delay is None:
            delay = getattr(settings, 'EMAIL_QUEUE_DELAY', 5)
        
        total_sent = 0
        total_failed = 0
        
        # Dividir en lotes
        for i in range(0, len(recipient_list), batch_size):
            batch = recipient_list[i:i + batch_size]
            
            try:
                success = self.send_email(
                    subject=subject,
                    message=message,
                    recipient_list=batch,
                    from_email=from_email,
                    html_message=html_message,
                    fail_silently=True
                )
                
                if success:
                    total_sent += len(batch)
                else:
                    total_failed += len(batch)
                
                # Delay entre lotes
                if delay > 0 and i + batch_size < len(recipient_list):
                    time.sleep(delay)
                    
            except Exception as e:
                logger.error(f"Error enviando lote de emails: {e}")
                total_failed += len(batch)
        
        logger.info(f"Bulk email completado: {total_sent} enviados, {total_failed} fallidos")
        
        return {
            'sent': total_sent,
            'failed': total_failed,
            'total': len(recipient_list)
        }
    
    def get_delivery_status(self, message_id: str) -> Dict:
        """
        Obtiene el estado de entrega de un email (si el proveedor lo soporta)
        """
        # SendGrid tracking
        if self.sendgrid_enabled and message_id.startswith('sg_'):
            try:
                # Implementar tracking de SendGrid
                pass
            except Exception as e:
                logger.error(f"Error obteniendo status de SendGrid: {e}")
        
        # AWS SES tracking
        if self.aws_ses_enabled and message_id.startswith('ses_'):
            try:
                # Implementar tracking de AWS SES
                pass
            except Exception as e:
                logger.error(f"Error obteniendo status de AWS SES: {e}")
        
        return {'status': 'unknown', 'message_id': message_id}
    
    def get_provider_status(self) -> Dict:
        """
        Obtiene el estado de todos los proveedores de email
        """
        return {
            'sendgrid': {
                'enabled': self.sendgrid_enabled,
                'status': 'active' if self.sendgrid_enabled else 'disabled'
            },
            'aws_ses': {
                'enabled': self.aws_ses_enabled,
                'status': 'active' if self.aws_ses_enabled else 'disabled'
            },
            'smtp': {
                'enabled': self.smtp_enabled,
                'status': 'active' if self.smtp_enabled else 'disabled'
            }
        }

# Instancia global del servicio de email
email_service = EmailService()

# Funciones de conveniencia para compatibilidad con código existente
def send_email(*args, **kwargs):
    """Wrapper para compatibilidad con código existente"""
    return email_service.send_email(*args, **kwargs)

def send_template_email(*args, **kwargs):
    """Wrapper para compatibilidad con código existente"""
    return email_service.send_template_email(*args, **kwargs)
