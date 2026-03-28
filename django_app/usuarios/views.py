"""
VISTAS DE AUTENTICACIÓN CON VALIDACIÓN DE ROL
Sistema de Gestión de Citas Médicas

El login exige que el usuario seleccione su ROL.
Una vez validado, el rol se guarda en la sesión y se usa
en cada vista para controlar el acceso a funciones y datos.

FLUJO DE AUTENTICACIÓN:
  1. Usuario ingresa: username, password, rol
  2. Django valida username/password con auth.authenticate()
  3. Se verifica que el rol seleccionado sea válido
  4. Se guarda rol_usuario en request.session
  5. Se redirige al menú principal
"""

import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

logger = logging.getLogger('citas')

ROLES_VALIDOS = {
    'medico': 'Médico',
    'paciente': 'Paciente',
    'administrativo': 'Administrativo',
    'auxiliar_medico': 'Auxiliar Médico',
}


def login_view(request):
    """
    Vista de Login con validación de ROL.
    
    GET:  Muestra el formulario de login
    POST: Valida credenciales + rol y crea la sesión
    """
    # Si ya está autenticado, ir al menú
    if request.user.is_authenticated and request.session.get('rol_usuario'):
        return redirect('menu_principal')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        rol = request.POST.get('rol', '').strip()

        # Validar que todos los campos estén presentes
        if not username or not password or not rol:
            error = 'Por favor complete todos los campos: usuario, contraseña y rol.'

        # Validar que el rol seleccionado sea uno de los permitidos
        elif rol not in ROLES_VALIDOS:
            error = f'El rol seleccionado "{rol}" no es válido.'
            logger.warning(f"Intento de login con rol inválido: {rol} (usuario: {username})")

        else:
            # Autenticar con Django
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)

                    # Guardar el ROL en la sesión
                    request.session['rol_usuario'] = rol
                    request.session['nombre_rol'] = ROLES_VALIDOS[rol]

                    logger.info(
                        f"LOGIN EXITOSO: usuario={username}, "
                        f"rol={rol}, ip={request.META.get('REMOTE_ADDR')}"
                    )
                    messages.success(
                        request,
                        f'Bienvenido/a {user.get_full_name() or username}. '
                        f'Ha ingresado como: {ROLES_VALIDOS[rol]}'
                    )
                    return redirect('menu_principal')
                else:
                    error = 'Su cuenta está desactivada. Contacte al administrador.'
            else:
                error = 'Usuario o contraseña incorrectos.'
                logger.warning(
                    f"FALLO LOGIN: usuario={username}, "
                    f"ip={request.META.get('REMOTE_ADDR')}"
                )

    return render(request, 'usuarios/login.html', {
        'titulo': 'Iniciar Sesión',
        'error': error,
        'roles': ROLES_VALIDOS,
        'rol_seleccionado': request.POST.get('rol', '') if request.method == 'POST' else '',
    })


@login_required
def logout_view(request):
    """
    Cerrar sesión.
    Limpia todos los datos de sesión incluyendo el rol.
    """
    username = request.user.username
    rol = request.session.get('rol_usuario', 'desconocido')
    logout(request)
    logger.info(f"LOGOUT: usuario={username}, rol={rol}")
    messages.info(request, 'Ha cerrado sesión exitosamente.')
    return redirect('login')
