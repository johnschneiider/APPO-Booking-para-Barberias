"""
Servicio principal para el sistema de recordatorios de APPO
Maneja el envío por email, WhatsApp y SMS de manera compatible con el código existente
"""

import logging
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from .models import (
    Recordatorio, ConfiguracionRecordatorio, PlantillaRecordatorio,
    TipoRecordatorio, EstadoRecordatorio, CanalNotificacion, HistorialRecordatorio
)

logger = logging.getLogger(__name__)

class ServicioRecordatorios:
    """
    Servicio principal para gestionar recordatorios
    """
    
    def __init__(self):
        self.email_service = None
        self.whatsapp_service = None
        self.sms_service = None
        
        # Inicializar servicios disponibles
        self._inicializar_servicios()
    
    def _inicializar_servicios(self):
        """Inicializa los servicios de notificación disponibles"""
        try:
            # Servicio de email
            from cuentas.email_service import email_service
            self.email_service = email_service
            logger.info("Servicio de email inicializado para recordatorios")
        except ImportError:
            logger.warning("Servicio de email no disponible para recordatorios")
        
        try:
            # Intentar Meta WhatsApp primero
            from clientes.meta_whatsapp_service import meta_whatsapp_service
            if meta_whatsapp_service.is_enabled():
                self.whatsapp_service = meta_whatsapp_service
                logger.info("Servicio de WhatsApp (Meta) inicializado para recordatorios")
            else:
                raise ImportError("Meta WhatsApp no está habilitado")
        except (ImportError, AttributeError):
            try:
                # Fallback a Twilio
                from clientes.twilio_whatsapp_service import twilio_whatsapp_service
                if twilio_whatsapp_service.is_enabled():
                    self.whatsapp_service = twilio_whatsapp_service
                    logger.info("Servicio de WhatsApp (Twilio) inicializado para recordatorios")
                else:
                    raise ImportError("Twilio WhatsApp no está habilitado")
            except (ImportError, AttributeError):
                try:
                    # Fallback al servicio de WhatsApp existente
                    from clientes.whatsapp_service import whatsapp_service
                    self.whatsapp_service = whatsapp_service
                    logger.info("Servicio de WhatsApp (API directa) inicializado para recordatorios")
                except ImportError:
                    logger.warning("Servicio de WhatsApp no disponible para recordatorios")
        
        try:
            # Servicio de SMS (usando Twilio)
            if hasattr(settings, 'TWILIO_ACCOUNT_SID'):
                self.sms_service = self._crear_servicio_twilio()
                logger.info("Servicio de SMS (Twilio) inicializado para recordatorios")
        except Exception as e:
            logger.warning(f"Servicio de SMS no disponible: {e}")
    
    def _crear_servicio_twilio(self):
        """Crea el servicio de Twilio para WhatsApp y SMS"""
        try:
            from twilio.rest import Client
            
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            return {
                'client': client,
                'whatsapp_number': getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None),
                'sms_number': getattr(settings, 'TWILIO_SMS_NUMBER', None),
                'enabled': True
            }
        except ImportError:
            logger.warning("Twilio no instalado, servicio no disponible")
            return None
        except Exception as e:
            logger.error(f"Error inicializando Twilio: {e}")
            return None
    
    def crear_recordatorio(
        self,
        tipo: str,
        destinatario,
        fecha_evento: timezone.datetime,
        contenido_relacionado=None,
        canales: List[str] = None,
        contexto_template: Dict = None,
        prioridad: int = 5
    ) -> Recordatorio:
        """
        Crea un nuevo recordatorio programado
        
        Args:
            tipo: Tipo de recordatorio (ver TipoRecordatorio)
            destinatario: Usuario que recibirá el recordatorio
            fecha_evento: Fecha y hora del evento
            contenido_relacionado: Objeto relacionado (reserva, suscripción, etc.)
            canales: Lista de canales a usar (email, whatsapp, sms)
            contexto_template: Variables para el template
            prioridad: Prioridad del recordatorio (1=alta, 10=baja)
        """
        try:
            # Obtener configuración del tipo de recordatorio
            config = self._obtener_configuracion(tipo)
            
            # Calcular fecha de envío
            fecha_envio = self._calcular_fecha_envio(fecha_evento, config)
            
            # Canales por defecto si no se especifican
            if not canales:
                canales = config.canales_habilitados if config else ['email']
            
            # Limpiar contexto para JSON serializable
            contexto_limpio = self._limpiar_contexto_json(contexto_template or {})
            
            # Crear el recordatorio
            recordatorio = Recordatorio.objects.create(
                tipo=tipo,
                destinatario=destinatario,
                fecha_programada=fecha_envio,
                canales_habilitados=canales,
                prioridad=prioridad,
                contexto_template=contexto_limpio
            )
            
            # Asociar contenido relacionado si existe
            if contenido_relacionado:
                recordatorio.content_type = ContentType.objects.get_for_model(contenido_relacionado)
                recordatorio.object_id = contenido_relacionado.id
                recordatorio.save()
            
            # Crear entrada en historial
            HistorialRecordatorio.objects.create(
                recordatorio=recordatorio,
                accion='creado',
                detalles={'canales': canales, 'fecha_evento': fecha_evento.isoformat()}
            )
            
            logger.info(f"Recordatorio creado: {recordatorio.id} - {tipo} para {destinatario}")
            return recordatorio
            
        except Exception as e:
            logger.error(f"Error creando recordatorio: {e}")
            raise
    
    def _obtener_configuracion(self, tipo: str) -> Optional[ConfiguracionRecordatorio]:
        """Obtiene la configuración para un tipo de recordatorio"""
        try:
            return ConfiguracionRecordatorio.objects.get(tipo=tipo, activo=True)
        except ConfiguracionRecordatorio.DoesNotExist:
            # Crear configuración por defecto
            return self._crear_configuracion_por_defecto(tipo)
    
    def _crear_configuracion_por_defecto(self, tipo: str) -> ConfiguracionRecordatorio:
        """Crea configuración por defecto para un tipo de recordatorio"""
        configuraciones_por_defecto = {
            TipoRecordatorio.RECORDATORIO_DIA_ANTES: {
                'anticipacion_horas': 24,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 3
            },
            TipoRecordatorio.RECORDATORIO_TRES_HORAS: {
                'anticipacion_horas': 3,
                'canales_habilitados': ['email', 'whatsapp', 'sms'],
                'reintentos_maximos': 5
            },
            TipoRecordatorio.RESERVA_CONFIRMADA: {
                'anticipacion_horas': 0,
                'canales_habilitados': ['email', 'whatsapp'],
                'reintentos_maximos': 2
            }
        }
        
        config = configuraciones_por_defecto.get(tipo, {
            'anticipacion_horas': 24,
            'canales_habilitados': ['email'],
            'reintentos_maximos': 3
        })
        
        return ConfiguracionRecordatorio.objects.create(
            tipo=tipo,
            **config
        )
    
    def _calcular_fecha_envio(self, fecha_evento: timezone.datetime, config: ConfiguracionRecordatorio) -> timezone.datetime:
        """Calcula la fecha de envío basada en la configuración"""
        if config:
            anticipacion = timezone.timedelta(minutes=config.anticipacion_total_minutos)
            return fecha_evento - anticipacion
        else:
            # Por defecto: 24 horas antes
            return fecha_evento - timezone.timedelta(hours=24)
    
    def procesar_recordatorios_pendientes(self) -> Dict[str, int]:
        """
        Procesa todos los recordatorios pendientes que están listos para enviar
        
        Returns:
            Dict con estadísticas del procesamiento
        """
        ahora = timezone.now()
        estadisticas = {
            'procesados': 0,
            'enviados': 0,
            'fallidos': 0,
            'reintentos': 0
        }
        
        # Obtener recordatorios pendientes listos para enviar
        recordatorios = Recordatorio.objects.filter(
            estado=EstadoRecordatorio.PENDIENTE,
            fecha_programada__lte=ahora
        ).order_by('prioridad', 'fecha_programada')
        
        for recordatorio in recordatorios:
            try:
                resultado = self._procesar_recordatorio(recordatorio)
                estadisticas['procesados'] += 1
                
                if resultado['enviado']:
                    estadisticas['enviados'] += 1
                elif resultado['fallido']:
                    estadisticas['fallidos'] += 1
                elif resultado['reintento']:
                    estadisticas['reintentos'] += 1
                    
            except Exception as e:
                logger.error(f"Error procesando recordatorio {recordatorio.id}: {e}")
                estadisticas['fallidos'] += 1
        
        logger.info(f"Recordatorios procesados: {estadisticas}")
        return estadisticas
    
    def _procesar_recordatorio(self, recordatorio: Recordatorio) -> Dict[str, bool]:
        """
        Procesa un recordatorio específico
        
        Returns:
            Dict con el resultado del procesamiento
        """
        resultado = {
            'enviado': False,
            'fallido': False,
            'reintento': False
        }
        
        # Procesar cada canal habilitado
        for canal in recordatorio.canales_habilitados:
            try:
                if self._enviar_por_canal(recordatorio, canal):
                    recordatorio.marcar_enviado(canal)
                    resultado['enviado'] = True
                else:
                    recordatorio.marcar_fallido(canal, "Error en envío")
                    resultado['fallido'] = True
                    
            except Exception as e:
                logger.error(f"Error enviando recordatorio {recordatorio.id} por {canal}: {e}")
                recordatorio.marcar_fallido(canal, str(e))
                resultado['fallido'] = True
        
        # Programar reintento si es necesario
        if resultado['fallido'] and recordatorio.puede_reintentar:
            if recordatorio.programar_reintento('email', delay_minutos=15):
                resultado['reintento'] = True
                resultado['fallido'] = False
        
        return resultado
    
    def _enviar_por_canal(self, recordatorio: Recordatorio, canal: str) -> bool:
        """
        Envía un recordatorio por un canal específico con fallback inteligente
        
        Args:
            recordatorio: El recordatorio a enviar
            canal: Canal de envío (email, whatsapp, sms)
        
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        try:
            # Renderizar contenido del recordatorio
            contenido = self._renderizar_recordatorio(recordatorio)
            
            if canal == CanalNotificacion.EMAIL:
                return self._enviar_email(recordatorio, contenido)
            elif canal == CanalNotificacion.WHATSAPP:
                # Intentar WhatsApp primero
                if self._enviar_whatsapp(recordatorio, contenido):
                    return True
                
                # Si WhatsApp falla, intentar SMS como fallback
                logger.info(f"WhatsApp falló para {recordatorio.destinatario}, intentando SMS...")
                if self._enviar_sms(recordatorio, contenido):
                    logger.info(f"SMS enviado exitosamente como fallback de WhatsApp")
                    return True
                
                # Si ambos fallan, intentar email como último recurso
                logger.info(f"SMS también falló, intentando email como último recurso...")
                return self._enviar_email(recordatorio, contenido)
                
            elif canal == CanalNotificacion.SMS:
                return self._enviar_sms(recordatorio, contenido)
            else:
                logger.warning(f"Canal no soportado: {canal}")
                return False
                
        except Exception as e:
            logger.error(f"Error enviando por canal {canal}: {e}")
            return False
    
    def _renderizar_recordatorio(self, recordatorio: Recordatorio) -> Dict[str, str]:
        """
        Renderiza el contenido del recordatorio usando templates
        """
        try:
            # Buscar plantilla específica
            plantilla = PlantillaRecordatorio.objects.filter(
                tipo=recordatorio.tipo,
                activa=True
            ).first()
            
            if plantilla:
                return plantilla.renderizar(recordatorio.contexto_template)
            
            # Usar templates existentes como fallback
            return self._renderizar_template_fallback(recordatorio)
            
        except Exception as e:
            logger.error(f"Error renderizando recordatorio: {e}")
            # Devolver contenido básico
            return {
                'asunto': recordatorio.asunto or f"Recordatorio: {recordatorio.tipo}",
                'mensaje': recordatorio.mensaje or "Tienes un recordatorio pendiente",
                'mensaje_html': recordatorio.mensaje_html
            }
    
    def _renderizar_template_fallback(self, recordatorio: Recordatorio) -> Dict[str, str]:
        """
        Renderiza usando templates existentes como fallback
        """
        contexto = recordatorio.contexto_template.copy()
        contexto.update({
            'recordatorio': recordatorio,
            'destinatario': recordatorio.destinatario,
            'fecha_evento': recordatorio.fecha_programada
        })
        
        # Mapear tipos a templates existentes
        mapeo_templates = {
            TipoRecordatorio.RECORDATORIO_DIA_ANTES: 'emails/recordatorio_dia_antes',
            TipoRecordatorio.RECORDATORIO_TRES_HORAS: 'emails/recordatorio_tres_horas',
            TipoRecordatorio.RESERVA_CONFIRMADA: 'emails/reserva_confirmada',
            TipoRecordatorio.RESERVA_CANCELADA: 'emails/reserva_cancelada',
            TipoRecordatorio.RESERVA_REAGENDADA: 'emails/reserva_reagendada'
        }
        
        template_name = mapeo_templates.get(recordatorio.tipo, 'emails/recordatorio_dia_antes')
        
        try:
            # Renderizar HTML
            mensaje_html = render_to_string(f'{template_name}.html', contexto)
            
            # Renderizar texto
            mensaje_texto = render_to_string(f'{template_name}.txt', contexto)
            
            # Generar asunto
            asunto = f"Recordatorio: {recordatorio.tipo.replace('_', ' ').title()}"
            
            return {
                'asunto': asunto,
                'mensaje': mensaje_texto,
                'mensaje_html': mensaje_html
            }
            
        except Exception as e:
            logger.error(f"Error renderizando template fallback: {e}")
            return {
                'asunto': f"Recordatorio: {recordatorio.tipo}",
                'mensaje': "Tienes un recordatorio pendiente",
                'mensaje_html': None
            }
    
    def _enviar_email(self, recordatorio: Recordatorio, contenido: Dict[str, str]) -> bool:
        """Envía recordatorio por email"""
        if not self.email_service:
            logger.warning("Servicio de email no disponible")
            return False
        
        try:
            return self.email_service.send_email(
                subject=contenido['asunto'],
                message=contenido['mensaje'],
                recipient_list=[recordatorio.destinatario.email],
                html_message=contenido.get('mensaje_html'),
                fail_silently=True
            )
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def _enviar_whatsapp(self, recordatorio: Recordatorio, contenido: Dict[str, str]) -> bool:
        """Envía recordatorio por WhatsApp"""
        if not self.whatsapp_service:
            logger.warning("Servicio de WhatsApp no disponible")
            return False
        
        try:
            if hasattr(recordatorio.destinatario, 'telefono') and recordatorio.destinatario.telefono:
                # Verificar si es Meta WhatsApp API
                if hasattr(self.whatsapp_service, 'send_text_message'):
                    # Usar Meta WhatsApp API
                    resultado = self.whatsapp_service.send_text_message(
                        recordatorio.destinatario.telefono,
                        contenido['mensaje']
                    )
                    return resultado.get('success', False)
                elif isinstance(self.whatsapp_service, dict) and self.whatsapp_service.get('enabled'):
                    # Usar Twilio WhatsApp (fallback)
                    return self._enviar_whatsapp_twilio(recordatorio, contenido)
                else:
                    # Usar servicio de WhatsApp existente (fallback)
                    return self.whatsapp_service.send_message(
                        recordatorio.destinatario.telefono,
                        contenido['mensaje']
                    )
            else:
                logger.warning(f"Usuario {recordatorio.destinatario} no tiene teléfono configurado")
                return False
        except Exception as e:
            logger.error(f"Error enviando WhatsApp: {e}")
            return False
    
    def _enviar_whatsapp_twilio(self, recordatorio: Recordatorio, contenido: Dict[str, str]) -> bool:
        """Envía WhatsApp usando Twilio"""
        try:
            from twilio.rest import Client
            
            client = self.whatsapp_service['client']
            whatsapp_number = self.whatsapp_service['whatsapp_number']
            
            if not whatsapp_number:
                logger.warning("Número de WhatsApp de Twilio no configurado")
                return False
            
            # Formatear número de teléfono
            telefono = self._formatear_telefono_twilio(recordatorio.destinatario.telefono)
            
            # Enviar mensaje de WhatsApp
            message = client.messages.create(
                from_=f'whatsapp:{whatsapp_number}',
                body=contenido['mensaje'],
                to=f'whatsapp:{telefono}'
            )
            
            logger.info(f"WhatsApp enviado via Twilio: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando WhatsApp via Twilio: {e}")
            return False
    
    def _enviar_sms(self, recordatorio: Recordatorio, contenido: Dict[str, str]) -> bool:
        """Envía recordatorio por SMS"""
        if not self.sms_service:
            logger.warning("Servicio de SMS no disponible")
            return False
        
        try:
            if hasattr(recordatorio.destinatario, 'telefono') and recordatorio.destinatario.telefono:
                # Verificar si es Twilio
                if isinstance(self.sms_service, dict) and self.sms_service.get('enabled'):
                    # Usar Twilio SMS
                    return self._enviar_sms_twilio(recordatorio, contenido)
                else:
                    logger.warning("Servicio de SMS no es Twilio")
                    return False
            else:
                logger.warning(f"Usuario {recordatorio.destinatario} no tiene teléfono configurado")
                return False
        except Exception as e:
            logger.error(f"Error enviando SMS: {e}")
            return False
    
    def _enviar_sms_twilio(self, recordatorio: Recordatorio, contenido: Dict[str, str]) -> bool:
        """Envía SMS usando Twilio"""
        try:
            client = self.sms_service['client']
            sms_number = self.sms_service['sms_number']
            
            if not sms_number:
                logger.warning("Número de SMS de Twilio no configurado")
                return False
            
            # Formatear número de teléfono
            telefono = self._formatear_telefono_twilio(recordatorio.destinatario.telefono)
            
            # Enviar SMS
            message = client.messages.create(
                body=contenido['mensaje'],
                from_=sms_number,
                to=telefono
            )
            
            logger.info(f"SMS enviado via Twilio: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error enviando SMS via Twilio: {e}")
            return False
    
    def _limpiar_contexto_json(self, contexto: Dict) -> Dict:
        """Limpia el contexto para que sea JSON serializable"""
        contexto_limpio = {}
        
        for clave, valor in contexto.items():
            if isinstance(valor, (str, int, float, bool, list, dict)):
                contexto_limpio[clave] = valor
            elif hasattr(valor, 'id'):
                # Para objetos de Django, guardar solo el ID
                contexto_limpio[clave + '_id'] = valor.id
                if hasattr(valor, '__str__'):
                    contexto_limpio[clave + '_nombre'] = str(valor)
            elif hasattr(valor, '__str__'):
                # Para otros objetos, convertir a string
                contexto_limpio[clave] = str(valor)
            else:
                # Omitir valores no serializables
                contexto_limpio[clave] = None
        
        return contexto_limpio
    
    def _formatear_telefono_twilio(self, telefono: str) -> str:
        """Formatea número de teléfono para Twilio"""
        import re
        
        # Limpiar el número
        telefono_limpio = re.sub(r'[\s\-\(\)]', '', str(telefono))
        
        # Si no tiene código de país, agregar +57 (Colombia)
        if not telefono_limpio.startswith('+'):
            if telefono_limpio.startswith('57'):
                telefono_limpio = '+' + telefono_limpio
            elif telefono_limpio.startswith('0'):
                telefono_limpio = '+57' + telefono_limpio[1:]
            else:
                telefono_limpio = '+57' + telefono_limpio
        
        return telefono_limpio
    
    # Métodos de compatibilidad con código existente
    
    def enviar_recordatorio_dia_antes(self, reserva) -> bool:
        """
        Método de compatibilidad con código existente
        Envía recordatorio un día antes de la reserva
        """
        try:
            fecha_evento = timezone.make_aware(
                timezone.datetime.combine(reserva.fecha, reserva.hora_inicio)
            )
            
            contexto = {
                'cliente': reserva.cliente,
                'reserva': reserva,
                'negocio': reserva.peluquero,
                'profesional': reserva.profesional,
                'fecha_formateada': reserva.fecha.strftime('%A, %d de %B de %Y'),
                'hora_formateada': reserva.hora_inicio.strftime('%H:%M')
            }
            
            recordatorio = self.crear_recordatorio(
                tipo=TipoRecordatorio.RECORDATORIO_DIA_ANTES,
                destinatario=reserva.cliente,
                fecha_evento=fecha_evento,
                contenido_relacionado=reserva,
                canales=['email', 'whatsapp'],
                contexto_template=contexto,
                prioridad=3
            )
            
            return recordatorio is not None
            
        except Exception as e:
            logger.error(f"Error creando recordatorio día antes: {e}")
            return False
    
    def enviar_recordatorio_confirmacion(self, reserva) -> bool:
        """
        Método de compatibilidad con código existente
        Envía recordatorio inmediato de confirmación de reserva
        """
        try:
            fecha_evento = timezone.make_aware(
                timezone.datetime.combine(reserva.fecha, reserva.hora_inicio)
            )
            
            contexto = {
                'cliente': reserva.cliente,
                'reserva': reserva,
                'negocio': reserva.peluquero,
                'profesional': reserva.profesional,
                'fecha_formateada': reserva.fecha.strftime('%A, %d de %B de %Y'),
                'hora_formateada': reserva.hora_inicio.strftime('%H:%M')
            }
            
            recordatorio = self.crear_recordatorio(
                tipo=TipoRecordatorio.RESERVA_CONFIRMADA,
                destinatario=reserva.cliente,
                fecha_evento=fecha_evento,
                contenido_relacionado=reserva,
                canales=['email', 'whatsapp'],
                contexto_template=contexto,
                prioridad=5  # Prioridad normal para confirmaciones
            )
            
            return recordatorio is not None
            
        except Exception as e:
            logger.error(f"Error creando recordatorio de confirmación: {e}")
            return False

    def enviar_recordatorio_tres_horas(self, reserva) -> bool:
        """
        Método de compatibilidad con código existente
        Envía recordatorio 3 horas antes de la reserva
        """
        try:
            fecha_evento = timezone.make_aware(
                timezone.datetime.combine(reserva.fecha, reserva.hora_inicio)
            )
            
            contexto = {
                'cliente': reserva.cliente,
                'reserva': reserva,
                'negocio': reserva.peluquero,
                'profesional': reserva.profesional,
                'fecha_formateada': reserva.fecha.strftime('%A, %d de %B de %Y'),
                'hora_formateada': reserva.hora_inicio.strftime('%H:%M')
            }
            
            recordatorio = self.crear_recordatorio(
                tipo=TipoRecordatorio.RECORDATORIO_TRES_HORAS,
                destinatario=reserva.cliente,
                fecha_evento=fecha_evento,
                contenido_relacionado=reserva,
                canales=['email', 'whatsapp', 'sms'],
                contexto_template=contexto,
                prioridad=1  # Alta prioridad para recordatorios cercanos
            )
            
            return recordatorio is not None
            
        except Exception as e:
            logger.error(f"Error creando recordatorio tres horas: {e}")
            return False

# Instancia global del servicio
servicio_recordatorios = ServicioRecordatorios()

# Funciones de compatibilidad para código existente
def enviar_recordatorio_confirmacion(reserva):
    """Wrapper para compatibilidad con código existente"""
    return servicio_recordatorios.enviar_recordatorio_confirmacion(reserva)

def enviar_recordatorio_dia_antes(reserva):
    """Wrapper para compatibilidad con código existente"""
    return servicio_recordatorios.enviar_recordatorio_dia_antes(reserva)

def enviar_recordatorio_tres_horas(reserva):
    """Wrapper para compatibilidad con código existente"""
    return servicio_recordatorios.enviar_recordatorio_tres_horas(reserva)
