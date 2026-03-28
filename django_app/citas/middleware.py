"""
MIDDLEWARE DE ROL DE USUARIO
Sistema de Gestión de Citas Médicas

El middleware intercepta CADA petición HTTP y verifica que el usuario
tenga un rol válido en sesión. Si no tiene rol, lo redirige al login.

En Django, el middleware es código que se ejecuta ANTES y DESPUÉS de
procesar cada vista. Es el lugar ideal para verificar autenticación global.
"""

from django.shortcuts import redirect
from django.urls import reverse


# URLs que no requieren autenticación ni rol
RUTAS_PUBLICAS = [
    '/login/',
    '/logout/',
    '/admin/',
    '/static/',
    '/favicon.ico',
    '/acceso-denegado/',
]


class RolMiddleware:
    """
    Middleware que verifica que el usuario autenticado tenga
    un rol válido en la sesión.
    
    Flujo:
    1. El usuario hace login → se guarda rol_usuario en sesión
    2. En cada petición → el middleware verifica que exista rol_usuario
    3. Si no existe rol → redirige al login
    """

    ROLES_VALIDOS = ['medico', 'paciente', 'administrativo', 'auxiliar_medico']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si la ruta es pública (no requiere rol)
        es_ruta_publica = any(
            request.path.startswith(ruta) for ruta in RUTAS_PUBLICAS
        )

        if not es_ruta_publica and request.user.is_authenticated:
            rol = request.session.get('rol_usuario', '')
            
            # Si el usuario está autenticado pero no tiene rol válido
            if rol not in self.ROLES_VALIDOS:
                # Limpiar sesión y redirigir al login
                request.session.flush()
                return redirect(f'/login/?error=sin_rol')

        response = self.get_response(request)
        return response
