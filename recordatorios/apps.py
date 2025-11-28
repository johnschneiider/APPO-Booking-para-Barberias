from django.apps import AppConfig


class RecordatoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recordatorios'
    verbose_name = 'Sistema de Recordatorios y Notificaciones'
    
    def ready(self):
        """
        Se ejecuta cuando la app está lista.
        Conecta las señales para notificaciones automáticas.
        """
        import logging
        logger = logging.getLogger('recordatorios')
        
        try:
            # Importar y conectar señales
            from . import signals
            signals.conectar_senales()
            logger.info("✅ App de recordatorios inicializada - Señales conectadas")
        except ImportError as e:
            logger.warning(f"⚠️ No se pudieron importar las señales: {e}")
        except Exception as e:
            logger.error(f"❌ Error inicializando app de recordatorios: {e}")
