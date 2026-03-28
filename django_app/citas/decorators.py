"""
DECORADORES DE CONTROL DE ACCESO POR ROL
Sistema de Gestión de Citas Médicas

Los decoradores se usan en las vistas para restringir el acceso
según el rol del usuario. Si el usuario no tiene el rol requerido,
es redirigido a la página de acceso denegado.

USO EN VISTAS:
    @login_required
    @rol_requerido(['administrativo', 'auxiliar_medico'])
    def mi_vista(request):
        ...
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def rol_requerido(roles_permitidos):
    """
    Decorador que verifica si el usuario tiene uno de los roles permitidos.
    
    Args:
        roles_permitidos (list): Lista de roles con acceso. Ej: ['administrativo']
    
    Si el rol del usuario NO está en la lista, redirige a 'acceso_denegado'.
    """
    def decorador(vista_func):
        @wraps(vista_func)
        def wrapper(request, *args, **kwargs):
            rol_actual = request.session.get('rol_usuario', '')
            
            if rol_actual not in roles_permitidos:
                messages.warning(
                    request,
                    f'⚠️ Su rol "{rol_actual}" no tiene permiso para realizar esta acción. '
                    f'Roles permitidos: {", ".join(roles_permitidos)}'
                )
                return redirect('acceso_denegado')
            
            return vista_func(request, *args, **kwargs)
        return wrapper
    return decorador


def puede_crear(request):
    """
    Función auxiliar: Verifica si el usuario puede crear registros.
    Retorna True/False según el rol.
    """
    roles_con_permiso = ['administrativo']
    return request.session.get('rol_usuario', '') in roles_con_permiso


def puede_editar(request):
    """
    Función auxiliar: Verifica si el usuario puede editar registros.
    """
    roles_con_permiso = ['administrativo']
    return request.session.get('rol_usuario', '') in roles_con_permiso


def puede_eliminar(request):
    """
    Función auxiliar: Verifica si el usuario puede eliminar/desactivar registros.
    """
    roles_con_permiso = ['administrativo']
    return request.session.get('rol_usuario', '') in roles_con_permiso


def solo_lectura(request):
    """
    Función auxiliar: Verifica si el usuario tiene acceso de solo lectura.
    """
    roles_solo_lectura = ['medico', 'paciente', 'auxiliar_medico']
    return request.session.get('rol_usuario', '') in roles_solo_lectura
