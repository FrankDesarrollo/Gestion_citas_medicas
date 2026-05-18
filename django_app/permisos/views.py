"""
Vistas para gestión de permisos.
Fase 2 (Frank) implementa la lógica CRUD completa.
Fase 3 (Milton) implementa los templates.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from citas.decorators import rol_requerido
from .models import Modulo, PermisoRol, PermisoUsuario


@login_required
@rol_requerido(['administrativo'])
def permisos_matriz(request):
    """Matriz visual: filas=roles, columnas=módulos, celdas=4 checkboxes CRUD."""
    roles = ['administrativo', 'medico', 'paciente', 'auxiliar_medico']
    modulos = Modulo.objects.filter(activo='S')

    if request.method == 'POST':
        for modulo in modulos:
            for rol in roles:
                permiso, _ = PermisoRol.objects.get_or_create(rol=rol, modulo=modulo)
                prefix = f"{rol}__{modulo.codigo}__"
                permiso.puede_ver = bool(request.POST.get(prefix + 'ver'))
                permiso.puede_crear = bool(request.POST.get(prefix + 'crear'))
                permiso.puede_editar = bool(request.POST.get(prefix + 'editar'))
                permiso.puede_eliminar = bool(request.POST.get(prefix + 'eliminar'))
                permiso.save()
        messages.success(request, 'Permisos actualizados correctamente.')
        return redirect('permisos:matriz')

    # Construir la matriz para el template
    matriz = {}
    for rol in roles:
        matriz[rol] = {}
        for modulo in modulos:
            try:
                p = PermisoRol.objects.get(rol=rol, modulo=modulo)
            except PermisoRol.DoesNotExist:
                p = PermisoRol(rol=rol, modulo=modulo)
            matriz[rol][modulo.codigo] = p

    return render(request, 'permisos/matriz.html', {
        'roles': roles,
        'modulos': modulos,
        'matriz': matriz,
    })


@login_required
@rol_requerido(['administrativo'])
def permisos_usuario_detalle(request, usuario_id):
    """Override de permisos por usuario individual."""
    usuario = get_object_or_404(User, pk=usuario_id)
    modulos = Modulo.objects.filter(activo='S')

    if request.method == 'POST':
        for modulo in modulos:
            prefix = f"{modulo.codigo}__"
            # Si el checkbox 'override' está marcado, guarda el valor explícito
            if request.POST.get(prefix + 'override'):
                permiso, _ = PermisoUsuario.objects.get_or_create(usuario=usuario, modulo=modulo)
                permiso.puede_ver = bool(request.POST.get(prefix + 'ver'))
                permiso.puede_crear = bool(request.POST.get(prefix + 'crear'))
                permiso.puede_editar = bool(request.POST.get(prefix + 'editar'))
                permiso.puede_eliminar = bool(request.POST.get(prefix + 'eliminar'))
                permiso.save()
            else:
                # Sin override: eliminar el registro para heredar del rol
                PermisoUsuario.objects.filter(usuario=usuario, modulo=modulo).delete()
        messages.success(request, f'Permisos de {usuario.username} actualizados.')
        return redirect('permisos:usuario_detalle', usuario_id=usuario_id)

    permisos_dict = {
        pu.modulo.codigo: pu
        for pu in PermisoUsuario.objects.filter(usuario=usuario)
    }

    return render(request, 'permisos/usuario_detalle.html', {
        'usuario_obj': usuario,
        'modulos': modulos,
        'permisos_dict': permisos_dict,
    })


@login_required
@rol_requerido(['administrativo'])
def permisos_usuario_reset(request, usuario_id):
    """Elimina todos los overrides del usuario (vuelve a heredar del rol)."""
    if request.method == 'POST':
        usuario = get_object_or_404(User, pk=usuario_id)
        PermisoUsuario.objects.filter(usuario=usuario).delete()
        messages.success(request, f'Permisos de {usuario.username} restablecidos al rol por defecto.')
    return redirect('permisos:usuario_detalle', usuario_id=usuario_id)
