def user_context(request):
    """
    Procesador de contexto personalizado para agregar información del usuario
    a todas las plantillas
    """
    context = {}
    
    if request.user.is_authenticated:
        context['es_cliente'] = getattr(request.user, 'tipo', None) == 'cliente'
        context['es_negocio'] = getattr(request.user, 'tipo', None) == 'negocio'
        context['tiene_negocios'] = hasattr(request.user, 'negocios') and request.user.negocios.exists()
        context['nombre_usuario'] = request.user.get_full_name() or request.user.username
    else:
        context['es_cliente'] = False
        context['es_negocio'] = False
        context['tiene_negocios'] = False
        context['nombre_usuario'] = None
    
    return context

def user_type(request):
    """
    Context processor para hacer disponible el tipo de usuario en todas las plantillas
    """
    context = {
        'is_cliente': False,
        'is_negocio': False,
    }
    
    if request.user.is_authenticated:
        context['is_cliente'] = request.user.tipo == 'cliente'
        context['is_negocio'] = request.user.tipo == 'negocio'
    
    return context

def tipo_usuario(request):
    user = request.user
    is_cliente = getattr(user, 'tipo', None) == 'cliente'
    is_negocio = getattr(user, 'tipo', None) == 'negocio'
    is_profesional = getattr(user, 'tipo', None) == 'profesional'
    return {
        'is_cliente': is_cliente,
        'is_negocio': is_negocio,
        'is_profesional': is_profesional,
    } 


def app_metrics(request):
    """
    Métricas globales de la plataforma (para marketing/UI):
    - total_reservas_app: total real de reservas en la DB
    - total_reservas_app_mkt: total mostrado (total real + offset de marketing)
    """
    from django.conf import settings
    from django.core.cache import cache

    offset = getattr(settings, 'RESERVAS_MARKETING_OFFSET', 879)
    cache_key = 'appo:total_reservas_app'

    total = cache.get(cache_key)
    if total is None:
        try:
            from clientes.models import Reserva
            total = Reserva.objects.count()
        except Exception:
            total = 0
        cache.set(cache_key, total, 60)  # 1 minuto

    try:
        total_mkt = int(total) + int(offset)
    except Exception:
        total_mkt = 879

    return {
        'total_reservas_app': total,
        'total_reservas_app_mkt': total_mkt,
    }


def google_maps_key(request):
    """Expone la API key de Google Maps a los templates de forma segura."""
    from django.conf import settings
    return {
        'GOOGLE_MAPS_API_KEY': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }