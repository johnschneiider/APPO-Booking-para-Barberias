from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Multiplica el valor por el argumento.
    Uso: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def add(value, arg):
    """
    Suma el valor con el argumento.
    Uso: {{ value|add:arg }}
    """
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def subtract(value, arg):
    """
    Resta el argumento del valor.
    Uso: {{ value|subtract:arg }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """
    Divide el valor por el argumento.
    Uso: {{ value|divide:arg }}
    """
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0
