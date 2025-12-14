"""
Backend de autenticación personalizado para APPO.

Características:
- Username case-insensitive (no distingue mayúsculas/minúsculas)
- Contraseña case-sensitive (sí distingue mayúsculas/minúsculas)
- Permite login con email o username
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class CaseInsensitiveAuthBackend(ModelBackend):
    """
    Backend de autenticación que permite login sin distinguir 
    mayúsculas/minúsculas en el username o email.
    
    Ejemplos válidos (si el usuario es "JohnDoe"):
    - johndoe / password123 ✅
    - JOHNDOE / password123 ✅
    - JohnDoe / password123 ✅
    - johndoe / PASSWORD123 ❌ (contraseña sí es case-sensitive)
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica al usuario buscando por username o email 
        sin distinguir mayúsculas/minúsculas.
        """
        if username is None or password is None:
            return None
        
        try:
            # Buscar usuario por username o email (case-insensitive)
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            # Ejecutar el hasher de contraseña para evitar timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            # Si hay múltiples usuarios (no debería pasar), tomar el primero
            user = User.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).first()
        
        # Verificar contraseña (case-sensitive) y que el usuario esté activo
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """Obtiene el usuario por ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None



