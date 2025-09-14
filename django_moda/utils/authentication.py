# django_moda/utils/authentication.py
from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    Variante de SessionAuthentication que NO requiere token CSRF.
    Útil para APIs REST consumidas por Postman, Next.js o apps externas
    que ya manejan cookies de sesión pero no envían CSRF.
    """

    def enforce_csrf(self, request):
        return  # 👈 desactiva validación CSRF
