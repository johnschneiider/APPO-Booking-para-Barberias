from django.apps import AppConfig


class RecordatoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recordatorios'
    verbose_name = 'Sistema de Recordatorios'
    
    def ready(self):
        """
        Se ejecuta cuando la app está lista
        """
        try:
            # Importar señales si existen
            import recordatorios.signals
        except ImportError:
            pass
        
        # Configurar logging específico para recordatorios
        import logging
        logger = logging.getLogger(__name__)
        logger.info("App de recordatorios inicializada")
