"""
Backend personalizado de PostgreSQL que maneja correctamente la codificación UTF-8

Django requiere que los backends personalizados estén estructurados como:
- melissa/db_backend/base.py con DatabaseWrapper
- melissa/db_backend/__init__.py
- melissa/db_backend/operations.py (opcional)
- etc.

Para simplificar, este módulo exporta directamente lo necesario.
"""
from django.db.backends.postgresql import base, operations, features, introspection, creation
import logging

logger = logging.getLogger(__name__)


class DatabaseWrapper(base.DatabaseWrapper):
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
        except (UnicodeDecodeError, UnicodeEncodeError) as e:
            logger.error(f"Error de codificación al conectar: {e}")
            # Intentar limpiar parámetros y reconectar
            for key, value in list(conn_params.items()):
                if isinstance(value, str):
                    try:
                        value.encode('utf-8')
                    except UnicodeEncodeError:
                        conn_params[key] = value.encode('utf-8', errors='replace').decode('utf-8')
            return super().get_new_connection(conn_params)


# Exportar las clases necesarias para que Django pueda usar el backend
DatabaseOperations = operations.DatabaseOperations
DatabaseFeatures = features.DatabaseFeatures
DatabaseIntrospection = introspection.DatabaseIntrospection
DatabaseCreation = creation.DatabaseCreation
