from django.apps import AppConfig
import os
import sys


class FidelizacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fidelizacion'
    _loop_service = None
    
    def ready(self):
        """Inicializa el sistema de fidelización cuando Django está listo"""
        # Importar señales siempre
        import fidelizacion.signals  # noqa
        
        # Solo iniciar el loop en el proceso principal (no en reloader)
        # Verificar si estamos en modo de migración, test, o shell
        if 'migrate' in sys.argv or 'test' in sys.argv or 'shell' in sys.argv:
            return
        
        # Verificar si estamos en el proceso principal (no en el reloader)
        # En desarrollo con runserver, RUN_MAIN solo es True en el proceso principal
        if os.environ.get('RUN_MAIN') != 'true':
            # En producción o cuando no hay autoreload, iniciar siempre
            if not os.environ.get('DJANGO_AUTORELOAD'):
                self._iniciar_loop()
        else:
            # Estamos en el proceso principal
            self._iniciar_loop()
    
    def _iniciar_loop(self):
        """Inicia el loop de procesamiento de mensajes"""
        # Evitar múltiples instancias usando variable de clase
        if FidelizacionConfig._loop_service is not None:
            return
        
        try:
            from fidelizacion.services import MensajeLoopService
            FidelizacionConfig._loop_service = MensajeLoopService()
            FidelizacionConfig._loop_service.start()
            import logging
            logger = logging.getLogger(__name__)
            logger.info("Loop de procesamiento de mensajes de fidelización iniciado")
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"No se pudo iniciar el loop de mensajes: {e}")

