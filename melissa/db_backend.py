"""
Backend personalizado de PostgreSQL que maneja correctamente la codificación UTF-8
"""
from django.db.backends.postgresql.base import DatabaseWrapper as PostgreSQLDatabaseWrapper
from django.db.backends.postgresql.operations import DatabaseOperations
import logging

logger = logging.getLogger(__name__)


class DatabaseWrapper(PostgreSQLDatabaseWrapper):
    """
    Wrapper personalizado que asegura codificación UTF-8 correcta
    """
    
    def get_connection_params(self):
        """Obtiene parámetros de conexión asegurando codificación UTF-8"""
        params = super().get_connection_params()
        
        # Asegurar que todos los valores string están en UTF-8
        for key, value in params.items():
            if isinstance(value, str):
                try:
                    # Validar que es UTF-8 válido
                    value.encode('utf-8')
                except UnicodeEncodeError:
                    # Si hay error, limpiar el valor
                    logger.warning(f"Carácter no-UTF-8 encontrado en parámetro {key}, limpiando...")
                    params[key] = value.encode('utf-8', errors='replace').decode('utf-8')
        
        return params
    
    def get_new_connection(self, conn_params):
        """Crea nueva conexión asegurando codificación UTF-8"""
        # Asegurar que client_encoding está en las opciones
        if 'options' not in conn_params:
            conn_params['options'] = {}
        
        if 'client_encoding' not in conn_params['options']:
            conn_params['options']['client_encoding'] = 'UTF8'
        
        try:
            return super().get_new_connection(conn_params)
        except UnicodeDecodeError as e:
            logger.error(f"Error de codificación al conectar: {e}")
            # Intentar limpiar parámetros y reconectar
            for key, value in list(conn_params.items()):
                if isinstance(value, str):
                    try:
                        value.encode('utf-8')
                    except UnicodeEncodeError:
                        conn_params[key] = value.encode('utf-8', errors='replace').decode('utf-8')
            return super().get_new_connection(conn_params)
