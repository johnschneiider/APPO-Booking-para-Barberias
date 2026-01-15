"""
Template tags personalizados para autenticación social
"""
from django import template
from django.core.exceptions import ImproperlyConfigured

register = template.Library()


@register.simple_tag(takes_context=True)
def safe_provider_login_url(context, provider_id):
    """
    Obtiene la URL de login del provider de forma segura.
    Si el provider no está configurado, retorna None.
    """
    try:
        from allauth.socialaccount.templatetags.socialaccount import provider_login_url
        request = context.get('request')
        if not request:
            return None
        return provider_login_url(context, provider_id)
    except (ValueError, ImproperlyConfigured, AttributeError):
        # Provider no configurado o no disponible
        return None


@register.simple_tag(takes_context=True)
def get_available_providers(context):
    """
    Obtiene los providers disponibles de forma segura.
    Si no hay providers configurados, retorna una lista vacía.
    """
    try:
        from allauth.socialaccount.templatetags.socialaccount import get_providers
        providers = get_providers(context)
        return providers if providers else []
    except (ValueError, ImproperlyConfigured, AttributeError):
        # No hay providers configurados
        return []


@register.simple_tag(takes_context=True)
def is_provider_available(context, provider_id):
    """
    Verifica si un provider específico está disponible.
    Retorna True si está disponible, False en caso contrario.
    """
    try:
        providers = get_available_providers(context)
        return any(p.id == provider_id for p in providers)
    except:
        return False
