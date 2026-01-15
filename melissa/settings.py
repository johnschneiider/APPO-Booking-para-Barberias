import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
import socket

# Cargar variables de entorno desde .env con codificación UTF-8
# Usar encoding='utf-8' para evitar problemas con caracteres especiales
try:
    # python-dotenv soporta encoding desde versiones recientes
    import dotenv
    if hasattr(dotenv, 'load_dotenv'):
        # Intentar cargar con encoding UTF-8
        try:
            load_dotenv(encoding='utf-8')
        except TypeError:
            # Si la versión no soporta encoding, cargar sin él
            load_dotenv()
    else:
        load_dotenv()
except Exception as e:
    # Si falla, intentar sin especificar encoding
    print(f"Warning: Error cargando .env: {e}")
    load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-super-secreta-para-desarrollo')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = [
    'appo.com.co',
    'www.appo.com.co',
    '92.113.39.100',
    'localhost',
    '127.0.0.1',
]

AUTH_USER_MODEL = 'cuentas.UsuarioPersonalizado'

# Configuración de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
# X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configuración de sesiones
SESSION_COOKIE_SECURE = not DEBUG  # True en producción, False en desarrollo
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax' if DEBUG else 'Strict'
CSRF_COOKIE_SECURE = not DEBUG  # True en producción, False en desarrollo
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax' if DEBUG else 'Strict'
SESSION_COOKIE_AGE = 86400  # 24 horas
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False  # Cambiado a False para evitar problemas de concurrencia
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_CACHE_ALIAS = 'default'



CSRF_TRUSTED_ORIGINS = [
    "https://appo.com.co",
    "https://www.appo.com.co",
    "http://appo.com.co",
    "http://www.appo.com.co",
    "https://92.113.39.100",
    "http://92.113.39.100",
    "https://vitalmix.com.co",
    "https://www.vitalmix.com.co",
]
# Configuración de mensajes
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'corsheaders',
    'channels',
    'widget_tweaks',
    
    # Local apps
    'cuentas',
    'negocios',
    'clientes',
    'profesionales',
    'chat',
    'ia_visagismo',
    'suscripciones',
    'recordatorios.apps.RecordatoriosConfig',
    'fidelizacion',
    'django.contrib.humanize',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'cuentas.middleware.AuthenticationMiddleware',
    'cuentas.middleware.UserTypeMiddleware',
    #'cuentas.middleware.RateLimitMiddleware',
    'cuentas.middleware.ActivityLoggingMiddleware',
    'clientes.middleware.ActividadUsuarioMiddleware',
]

ROOT_URLCONF = 'melissa.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cuentas.context_processors.tipo_usuario',
            ],
        },
    },
]

WSGI_APPLICATION = 'melissa.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Configuración de base de datos
# Prioridad: DATABASE_URL > PostgreSQL individual > SQLite (solo desarrollo)

# Si hay DATABASE_URL, usarlo directamente (evita problemas de codificación)
database_url = os.environ.get('DATABASE_URL', '')
if database_url and database_url.startswith('postgresql://'):
    # Limpiar y normalizar DATABASE_URL
    try:
        # Asegurar que es UTF-8 válido
        if isinstance(database_url, bytes):
            database_url = database_url.decode('utf-8', errors='replace')
        database_url = str(database_url).strip()
        # Validar que puede codificarse a UTF-8
        database_url.encode('utf-8')
        
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                # Usar DATABASE_URL directamente
            }
        }
        # Parsear DATABASE_URL manualmente para evitar problemas
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        
        DATABASES['default'].update({
            'NAME': parsed.path[1:] if parsed.path else 'appo_db',  # Remover el / inicial
            'USER': parsed.username or 'appo_user',
            'PASSWORD': parsed.password or '',
            'HOST': parsed.hostname or 'localhost',
            'PORT': str(parsed.port) if parsed.port else '5432',
            'OPTIONS': {
                'client_encoding': 'UTF8',
                'connect_timeout': 10,
            },
            'CONN_MAX_AGE': 600,
        })
    except Exception as e:
        print(f"Warning: Error parseando DATABASE_URL: {e}")
        # Continuar con configuración individual
        database_url = None

if not database_url and os.environ.get('POSTGRES_DB'):
    # Configuración para PostgreSQL del sistema (producción/VPS)
    # Leer variables de entorno con manejo seguro de codificación
    def safe_getenv(key, default=''):
        """Obtiene variable de entorno manejando correctamente la codificación UTF-8"""
        try:
            value = os.environ.get(key, default)
            if value is None:
                return default
            
            # Si es bytes, decodificar con diferentes codificaciones
            if isinstance(value, bytes):
                # Intentar UTF-8 primero
                try:
                    value = value.decode('utf-8')
                except UnicodeDecodeError:
                    # Si falla, intentar latin-1 (que puede decodificar cualquier byte)
                    try:
                        value = value.decode('latin-1')
                        # Luego intentar convertir a UTF-8
                        value = value.encode('latin-1').decode('utf-8', errors='replace')
                    except:
                        # Último recurso: usar errors='replace'
                        value = value.decode('utf-8', errors='replace')
            
            # Si es string, asegurar que es UTF-8 válido y limpiar
            if isinstance(value, str):
                # Intentar codificar a UTF-8 para validar
                try:
                    # Normalizar y limpiar el string
                    value = value.strip()
                    # Validar que puede codificarse a UTF-8
                    value.encode('utf-8')
                except UnicodeEncodeError:
                    # Si hay caracteres no-UTF-8, limpiarlos
                    try:
                        # Asumir que viene de latin-1 y convertir
                        value = value.encode('latin-1').decode('utf-8', errors='replace')
                    except:
                        # Si todo falla, reemplazar caracteres problemáticos
                        value = value.encode('utf-8', errors='replace').decode('utf-8')
                        # Limpiar caracteres de control y no imprimibles
                        value = ''.join(char for char in value if char.isprintable() or char.isspace())
            
            return value
        except Exception as e:
            # Si hay cualquier error, usar el valor por defecto
            print(f"Warning: Error de codificación al leer {key}: {e}")
            return default
    
    # Leer variables con manejo seguro
    db_name = safe_getenv('POSTGRES_DB', 'appo_db')
    db_user = safe_getenv('POSTGRES_USER', 'appo_user')
    db_password = safe_getenv('POSTGRES_PASSWORD', '')
    db_host = safe_getenv('POSTGRES_HOST', 'localhost')
    db_port = safe_getenv('POSTGRES_PORT', '5432')
    
    # Asegurar que todos los valores son strings válidos y limpios
    db_name = str(db_name).strip() if db_name else 'appo_db'
    db_user = str(db_user).strip() if db_user else 'appo_user'
    db_password = str(db_password).strip() if db_password else ''
    db_host = str(db_host).strip() if db_host else 'localhost'
    db_port = str(db_port).strip() if db_port else '5432'
    
    # Limpiar cualquier carácter problemático de la contraseña especialmente
    # (puede tener caracteres especiales que causan problemas)
    if db_password:
        # Asegurar que la contraseña solo tenga caracteres seguros para DSN
        import re
        # Permitir letras, números y caracteres comunes de contraseña
        db_password = re.sub(r'[^\w\s\-_!@#$%^&*()+=\[\]{}|;:,.<>?/~`]', '', db_password)
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': db_port,
            # Opciones adicionales para manejar codificación
            'OPTIONS': {
                'client_encoding': 'UTF8',
                # Forzar UTF-8 en la conexión
                'connect_timeout': 10,
            },
            # Usar connect_timeout para evitar problemas de conexión
            'CONN_MAX_AGE': 600,
        }
    }
else:
    # Configuración para SQLite en desarrollo local (solo si no hay PostgreSQL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / "db.sqlite3",
        }
    }

# Configuración de caché
# Intentar usar Redis si está disponible (del sistema)
redis_url = os.environ.get('REDIS_URL', '')
if redis_url or not DEBUG:
    # Usar Redis en producción (del sistema)
    try:
        import redis
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': redis_url or 'redis://localhost:6379/1',
            }
        }
    except (ImportError, Exception):
        # Fallback a memoria local si Redis no está disponible
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        }
else:
    # Configuración de caché para desarrollo local
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuración de archivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Configuración de django-allauth
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_PASSWORD_MIN_LENGTH = 8
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGIN_REDIRECT_URL = '/cuentas/dashboard/'
ACCOUNT_SIGNUP_REDIRECT_URL = '/'

# Custom User Model
AUTHENTICATION_BACKENDS = [
    'cuentas.backends.CaseInsensitiveAuthBackend',  # Username case-insensitive
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# Configuración de django-allauth
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_SIGNUP_REDIRECT_URL = '/'

# CORS Settings
CORS_ALLOWED_ORIGINS = [
    "https://appo.com.co",
    "https://www.appo.com.co",
    "http://appo.com.co",
    "http://www.appo.com.co",
    "https://92.113.39.100",
    "http://92.113.39.100",
    "http://localhost",
    "http://localhost:80",
    "http://127.0.0.1:8000",
]

CORS_ALLOW_CREDENTIALS = True

# Configuraciones adicionales de CORS
CORS_ALLOW_ALL_ORIGINS = False  # Solo permitir orígenes específicos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Google OAuth Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# Configuraciones adicionales para autenticación social
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_LOGIN_ON_GET = True

# Email Configuration (for development) - Comentado para usar SMTP real
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_USE_TLS = False
# EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# Configuración avanzada de Email con servicios profesionales
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Configuración principal de email
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'APPO <noreply@appo.com.co>')

# Configuración de SendGrid (servicio principal)
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'noreply@appo.com.co')
SENDGRID_FROM_NAME = os.environ.get('SENDGRID_FROM_NAME', 'APPO')

# Configuración de AWS SES (servicio de respaldo)
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
AWS_SES_REGION_NAME = os.environ.get('AWS_SES_REGION_NAME', 'us-east-1')
AWS_SES_REGION_ENDPOINT = os.environ.get('AWS_SES_REGION_ENDPOINT', 'email.us-east-1.amazonaws.com')

# Configuración de email avanzada
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '30'))
EMAIL_SSL_KEYFILE = os.environ.get('EMAIL_SSL_KEYFILE', '')
EMAIL_SSL_CERTFILE = os.environ.get('EMAIL_SSL_CERTFILE', '')

# Configuración de templates de email
EMAIL_TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates', 'emails')
EMAIL_DEFAULT_CHARSET = 'utf-8'

# Configuración de cola de emails
EMAIL_QUEUE_ENABLED = os.environ.get('EMAIL_QUEUE_ENABLED', 'False').lower() == 'true'
EMAIL_QUEUE_BATCH_SIZE = int(os.environ.get('EMAIL_QUEUE_BATCH_SIZE', '100'))
EMAIL_QUEUE_DELAY = int(os.environ.get('EMAIL_QUEUE_DELAY', '5'))

# Configuración de tracking de emails
EMAIL_TRACKING_ENABLED = os.environ.get('EMAIL_TRACKING_ENABLED', 'True').lower() == 'true'
EMAIL_OPEN_TRACKING = os.environ.get('EMAIL_OPEN_TRACKING', 'True').lower() == 'true'
EMAIL_CLICK_TRACKING = os.environ.get('EMAIL_CLICK_TRACKING', 'True').lower() == 'true'

# Configuración de rate limiting para emails
EMAIL_RATE_LIMIT = os.environ.get('EMAIL_RATE_LIMIT', '100/hour')  # 100 emails por hora
EMAIL_RATE_LIMIT_PER_USER = os.environ.get('EMAIL_RATE_LIMIT_PER_USER', '10/hour')  # 10 emails por usuario por hora

# Configuración de mensajes
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Configuración de CSRF para desarrollo
CSRF_USE_SESSIONS = True  # Usar sesiones para CSRF
CSRF_COOKIE_DOMAIN = None  # Permitir cookies en cualquier dominio
SESSION_COOKIE_DOMAIN = None  # Permitir cookies de sesión en cualquier dominio
CSRF_TRUSTED_ORIGINS = [
    "https://appo.com.co",
    "https://www.appo.com.co",
    "https://vitalmix.com.co",
    "https://www.vitalmix.com.co",
    "http://localhost",
    "http://localhost:80",
    "http://127.0.0.1:8000",
]

# Configuración de adaptadores personalizados
ACCOUNT_ADAPTER = 'cuentas.adapters.CustomAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'cuentas.adapters.CustomSocialAccountAdapter'

# Django Channels Configuration
ASGI_APPLICATION = 'melissa.asgi.application'

# Channel Layers Configuration (Redis backend)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}

# Configuración para desarrollo (sin Redis)
if DEBUG:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }

# Configuración de Replicate (IA Generativa)
REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')

# Celery settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Configuración de Twilio WhatsApp
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', '+14155238886')  # Número de WhatsApp de Twilio
TWILIO_WHATSAPP_ENABLED = os.getenv('TWILIO_WHATSAPP_ENABLED', 'true').lower() == 'true'
TWILIO_TEMPLATE_TEXTO_LIBRE = os.getenv('TWILIO_TEMPLATE_TEXTO_LIBRE', '')  # Content SID (HX...) para primer contacto
TWILIO_TEMPLATE_TEXTO_LIBRE_VAR_KEY = os.getenv('TWILIO_TEMPLATE_TEXTO_LIBRE_VAR_KEY', '1')  # ej: 1 o body

# Templates específicos por evento (recomendado para producción)
# Cada variable se manda via Content API (content_sid + content_variables)
TWILIO_TEMPLATE_RESERVA_CONFIRMADA = os.getenv('TWILIO_TEMPLATE_RESERVA_CONFIRMADA', '')
TWILIO_TEMPLATE_RESERVA_CANCELADA = os.getenv('TWILIO_TEMPLATE_RESERVA_CANCELADA', '')
TWILIO_TEMPLATE_RESERVA_REAGENDADA = os.getenv('TWILIO_TEMPLATE_RESERVA_REAGENDADA', '')
TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES = os.getenv('TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES', '')
TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS = os.getenv('TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS', '')
TWILIO_TEMPLATE_INASISTENCIA = os.getenv('TWILIO_TEMPLATE_INASISTENCIA', '')

# URL base de la aplicación
if not DEBUG:
    BASE_URL = 'https://appo.com.co'  # Producción
else:
    BASE_URL = 'http://127.0.0.1:8000'  # Desarrollo

# Configuración de WhatsApp Business API (Usando Twilio)
WHATSAPP_CONFIG = {
    'ENABLED': TWILIO_WHATSAPP_ENABLED,
    'PROVIDER': 'twilio',
    'ACCOUNT_SID': TWILIO_ACCOUNT_SID,
    'AUTH_TOKEN': TWILIO_AUTH_TOKEN,
    'WHATSAPP_NUMBER': TWILIO_WHATSAPP_NUMBER,
    'TEXTO_LIBRE_VAR_KEY': TWILIO_TEMPLATE_TEXTO_LIBRE_VAR_KEY,
    'TEMPLATES': {
        'reserva_confirmada': TWILIO_TEMPLATE_RESERVA_CONFIRMADA,
        'recordatorio_dia_antes': TWILIO_TEMPLATE_RECORDATORIO_DIA_ANTES,
        'recordatorio_tres_horas': TWILIO_TEMPLATE_RECORDATORIO_TRES_HORAS,
        'reserva_cancelada': TWILIO_TEMPLATE_RESERVA_CANCELADA,
        'reserva_reagendada': TWILIO_TEMPLATE_RESERVA_REAGENDADA,
        'inasistencia': TWILIO_TEMPLATE_INASISTENCIA,
        # Template genérica para “primer mensaje” / fuera de ventana (por ejemplo: body = "{{1}}")
        'texto_libre': TWILIO_TEMPLATE_TEXTO_LIBRE,
    }
}

# Configuración de Meta WhatsApp Business API
META_WHATSAPP_ENABLED = os.getenv('META_WHATSAPP_ENABLED', 'False').lower() == 'true'
META_WHATSAPP_PHONE_NUMBER_ID = os.getenv('META_WHATSAPP_PHONE_NUMBER_ID', '')
# El token puede venir como META_WHATSAPP_ACCESS_TOKEN o TOKEN_WHATSAPP (para compatibilidad)
META_WHATSAPP_ACCESS_TOKEN = os.getenv('META_WHATSAPP_ACCESS_TOKEN') or os.getenv('TOKEN_WHATSAPP', '')
META_WHATSAPP_VERIFY_TOKEN = os.getenv('META_WHATSAPP_VERIFY_TOKEN', 'appo_whatsapp_verify_2024')
META_WHATSAPP_WEBHOOK_SECRET = os.getenv('META_WHATSAPP_WEBHOOK_SECRET', 'appo_webhook_secret_2024')
META_WHATSAPP_API_VERSION = os.getenv('META_WHATSAPP_API_VERSION', 'v22.0')

# Nombres de templates de Meta (los nombres exactos que creaste en Meta WhatsApp Manager)
META_TEMPLATE_RESERVA_CONFIRMADA = os.getenv('META_TEMPLATE_RESERVA_CONFIRMADA', 'reserva_confirmada_appo')
META_TEMPLATE_RECORDATORIO_DIA_ANTES = os.getenv('META_TEMPLATE_RECORDATORIO_DIA_ANTES', 'recordatorio_dia_antes_appo')
META_TEMPLATE_RECORDATORIO_TRES_HORAS = os.getenv('META_TEMPLATE_RECORDATORIO_TRES_HORAS', 'recordatorio_tres_horas_appo')
META_TEMPLATE_RESERVA_CANCELADA = os.getenv('META_TEMPLATE_RESERVA_CANCELADA', 'reserva_cancelada_appo')
META_TEMPLATE_RESERVA_REAGENDADA = os.getenv('META_TEMPLATE_RESERVA_REAGENDADA', 'reserva_reagendada_appo')
META_TEMPLATE_INASISTENCIA = os.getenv('META_TEMPLATE_INASISTENCIA', 'inasistencia_appo')

# Google Maps API Key (Places, Maps JavaScript, Geocoding)
# API_KEY = 'AIzaSyAn0n-nfpaAcvWeEWRg7iGIgNxC9X1FYHg'

# Configuración de Logging
import os
from pathlib import Path

# Crear directorio de logs si no existe
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

# Configuración de caché para rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 300,  # 5 minutos
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        }
    }
}

# Configuración de Rate Limiting
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_KEY_PREFIX = 'rl'

# Configuraciones específicas de rate limiting
RATELIMIT_SETTINGS = {
    'LOGIN_RATE': '5/m',  # 5 intentos por minuto
    'REGISTER_RATE': '3000/h',  # 3 registros por hora
    'RESERVATION_RATE': '10/h',  # 10 reservas por hora
    'API_RATE': '100/h',  # 100 requests por hora para APIs
    'GENERAL_RATE': '1000/h',  # 1000 requests por hora general
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'detailed': {
            'format': '[{asctime}] {levelname} {name} {funcName}:{lineno} - {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
        'file_general': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'melissa_general.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'file_errors': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'melissa_errors.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'file_security': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'melissa_security.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'file_activity': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'melissa_activity.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'detailed',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_general'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['file_errors', 'mail_admins', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'file_errors'],
            'level': 'WARNING',
            'propagate': False,
        },
        # Loggers personalizados para Melissa
        'melissa.security': {
            'handlers': ['file_security', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'melissa.activity': {
            'handlers': ['file_activity', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'melissa.errors': {
            'handlers': ['file_errors', 'mail_admins', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'melissa.business': {
            'handlers': ['file_activity', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'melissa.recordatorios': {
            'handlers': ['file_activity', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console', 'file_errors'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file_general'],
        'level': 'WARNING',
    },
}

# Configuración de Twilio para WhatsApp y SMS
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', '+14155238886')  # WhatsApp Sandbox
TWILIO_SMS_NUMBER = os.getenv('TWILIO_SMS_NUMBER', '+18578871809')  # SMS sigue usando tu número

# Configuración de recordatorios
RECORDATORIOS_EMAIL_ENABLED = True
RECORDATORIOS_WHATSAPP_ENABLED = True
RECORDATORIOS_SMS_ENABLED = False

# Fidelización (sistema alterno de mensajes programados). Para evitar duplicados
# con el sistema de recordatorios, la confirmación inmediata se puede activar explícitamente.
FIDELIZACION_CONFIRMACION_INMEDIATA = os.getenv('FIDELIZACION_CONFIRMACION_INMEDIATA', 'False').lower() == 'true'