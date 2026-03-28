"""
VISTAS DEL SISTEMA DE CITAS MÉDICAS
Arquitectura MVT - La "V" (View)

Las vistas conectan los Modelos con los Templates.
Aquí se implementa el control de acceso basado en ROLES:
- Cada vista verifica el rol del usuario antes de ejecutar
- Cada acción (INSERT, UPDATE, DELETE) se controla según el rol
- El rol determina también qué usuario de BD se usa para la conexión

ROLES Y PERMISOS:
  medico          → Solo LIST y READ de catálogos
  paciente        → Solo LIST y READ de sus datos
  administrativo  → CRUD completo (List, Create, Read, Update, Delete)
  auxiliar_medico → List, Read y Create en algunos módulos
"""

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Departamento, Municipio, Sede, Consultorio
from .forms import DepartamentoForm, MunicipioForm, SedeForm, ConsultorioForm
from .decorators import rol_requerido, puede_crear, puede_editar, puede_eliminar

logger = logging.getLogger('citas')

ROLES_CRUD_COMPLETO = ['administrativo']
ROLES_SOLO_LECTURA = ['medico', 'paciente']
ROLES_LECTURA_CREACION = ['auxiliar_medico']


# ===========================================================
# VISTA: MENÚ PRINCIPAL
# ===========================================================
@login_required
def menu_principal(request):
    """
    Vista del menú principal.
    Muestra opciones según el rol del usuario en sesión.
    """
    rol = request.session.get('rol_usuario', '')
    contexto = {
        'rol': rol,
        'usuario': request.user,
        'titulo': 'Menú Principal',
        'puede_gestionar_maestros': rol in ROLES_CRUD_COMPLETO,
        'es_medico': rol == 'medico',
        'es_paciente': rol == 'paciente',
        'es_auxiliar': rol == 'auxiliar_medico',
    }
    logger.info(f"Usuario {request.user.username} (rol: {rol}) accedió al menú principal")
    return render(request, 'citas/menu.html', contexto)


# ===========================================================
# CRUD: DEPARTAMENTOS
# ===========================================================

@login_required
def departamentos_lista(request):
    """
    LIST: Listar todos los departamentos.
    Todos los roles pueden ver esta lista.
    """
    rol = request.session.get('rol_usuario', '')
    busqueda = request.GET.get('q', '')

    departamentos = Departamento.objects.all()
    if busqueda:
        departamentos = departamentos.filter(
            nombre_departamento__icontains=busqueda
        ) | departamentos.filter(
            codigo_dane__icontains=busqueda
        )

    # Paginación: 10 registros por página
    paginator = Paginator(departamentos, 10)
    page = request.GET.get('page')
    try:
        departamentos_paginados = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        departamentos_paginados = paginator.page(1)

    contexto = {
        'titulo': 'Gestión de Departamentos',
        'departamentos': departamentos_paginados,
        'busqueda': busqueda,
        'rol': rol,
        'puede_crear': rol in ROLES_CRUD_COMPLETO,
        'puede_editar': rol in ROLES_CRUD_COMPLETO,
        'puede_eliminar': rol in ROLES_CRUD_COMPLETO,
        'total_registros': departamentos.count(),
    }
    return render(request, 'citas/departamentos/lista.html', contexto)


@login_required
@rol_requerido(['administrativo'])
def departamentos_crear(request):
    """
    CREATE: Crear nuevo departamento.
    Solo el rol ADMINISTRATIVO puede crear.
    """
    if request.method == 'POST':
        form = DepartamentoForm(request.POST)
        if form.is_valid():
            departamento = form.save(commit=False)
            departamento.usuario_creacion = request.user.username
            departamento.save()
            logger.info(
                f"DEPARTAMENTO CREADO: {departamento.nombre_departamento} "
                f"por {request.user.username} (rol: {request.session.get('rol_usuario')})"
            )
            messages.success(
                request,
                f'✅ Departamento "{departamento.nombre_departamento}" creado exitosamente.'
            )
            return redirect('departamentos_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        form = DepartamentoForm()

    return render(request, 'citas/departamentos/formulario.html', {
        'form': form,
        'titulo': 'Crear Departamento',
        'accion': 'Crear',
        'url_cancelar': 'departamentos_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
def departamentos_detalle(request, pk):
    """READ: Ver detalle de un departamento."""
    departamento = get_object_or_404(Departamento, pk=pk)
    municipios = departamento.municipios.filter(activo='S')
    return render(request, 'citas/departamentos/detalle.html', {
        'titulo': f'Departamento: {departamento.nombre_departamento}',
        'departamento': departamento,
        'municipios': municipios,
        'rol': request.session.get('rol_usuario', ''),
        'puede_editar': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO,
    })


@login_required
@rol_requerido(['administrativo'])
def departamentos_editar(request, pk):
    """
    UPDATE: Editar un departamento existente.
    Solo el rol ADMINISTRATIVO puede editar.
    """
    departamento = get_object_or_404(Departamento, pk=pk)
    if request.method == 'POST':
        form = DepartamentoForm(request.POST, instance=departamento)
        if form.is_valid():
            dep = form.save(commit=False)
            dep.fecha_modificacion = timezone.now().date()
            dep.save()
            logger.info(
                f"DEPARTAMENTO ACTUALIZADO: ID={pk} "
                f"por {request.user.username} (rol: {request.session.get('rol_usuario')})"
            )
            messages.success(
                request,
                f'✅ Departamento "{dep.nombre_departamento}" actualizado exitosamente.'
            )
            return redirect('departamentos_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        form = DepartamentoForm(instance=departamento)

    return render(request, 'citas/departamentos/formulario.html', {
        'form': form,
        'titulo': 'Editar Departamento',
        'accion': 'Actualizar',
        'departamento': departamento,
        'url_cancelar': 'departamentos_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo'])
def departamentos_eliminar(request, pk):
    """
    DELETE: Eliminar un departamento.
    Solo el rol ADMINISTRATIVO puede eliminar.
    En realidad hacemos un "soft delete" cambiando activo='N'.
    """
    departamento = get_object_or_404(Departamento, pk=pk)
    if request.method == 'POST':
        nombre = departamento.nombre_departamento
        # Verificar si tiene municipios activos
        if departamento.municipios.filter(activo='S').exists():
            messages.error(
                request,
                f'❌ No se puede eliminar el departamento "{nombre}" '
                f'porque tiene municipios activos asociados.'
            )
            return redirect('departamentos_lista')
        # Soft delete
        departamento.activo = 'N'
        departamento.fecha_modificacion = timezone.now().date()
        departamento.save()
        logger.info(
            f"DEPARTAMENTO DESACTIVADO: {nombre} (ID={pk}) "
            f"por {request.user.username} (rol: {request.session.get('rol_usuario')})"
        )
        messages.success(request, f'✅ Departamento "{nombre}" desactivado exitosamente.')
        return redirect('departamentos_lista')

    return render(request, 'citas/departamentos/confirmar_eliminar.html', {
        'titulo': 'Desactivar Departamento',
        'departamento': departamento,
        'rol': request.session.get('rol_usuario', ''),
    })


# ===========================================================
# CRUD: MUNICIPIOS
# ===========================================================

@login_required
def municipios_lista(request):
    """LIST: Listar municipios con filtros."""
    rol = request.session.get('rol_usuario', '')
    busqueda = request.GET.get('q', '')
    departamento_id = request.GET.get('departamento', '')

    municipios = Municipio.objects.select_related('id_departamento').all()

    if busqueda:
        municipios = municipios.filter(nombre_municipio__icontains=busqueda)
    if departamento_id:
        municipios = municipios.filter(id_departamento=departamento_id)

    paginator = Paginator(municipios, 10)
    page = request.GET.get('page')
    try:
        municipios_paginados = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        municipios_paginados = paginator.page(1)

    departamentos = Departamento.objects.filter(activo='S').order_by('nombre_departamento')

    return render(request, 'citas/municipios/lista.html', {
        'titulo': 'Gestión de Municipios',
        'municipios': municipios_paginados,
        'departamentos': departamentos,
        'busqueda': busqueda,
        'departamento_seleccionado': departamento_id,
        'rol': rol,
        'puede_crear': rol in ROLES_CRUD_COMPLETO,
        'puede_editar': rol in ROLES_CRUD_COMPLETO,
        'puede_eliminar': rol in ROLES_CRUD_COMPLETO,
        'total_registros': municipios.count(),
    })


@login_required
@rol_requerido(['administrativo'])
def municipios_crear(request):
    """CREATE: Crear nuevo municipio."""
    if request.method == 'POST':
        form = MunicipioForm(request.POST)
        if form.is_valid():
            municipio = form.save(commit=False)
            municipio.usuario_creacion = request.user.username
            municipio.save()
            messages.success(
                request,
                f'✅ Municipio "{municipio.nombre_municipio}" creado exitosamente.'
            )
            return redirect('municipios_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        form = MunicipioForm()

    return render(request, 'citas/municipios/formulario.html', {
        'form': form,
        'titulo': 'Crear Municipio',
        'accion': 'Crear',
        'url_cancelar': 'municipios_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
def municipios_detalle(request, pk):
    """READ: Ver detalle de un municipio."""
    municipio = get_object_or_404(Municipio, pk=pk)
    return render(request, 'citas/municipios/detalle.html', {
        'titulo': f'Municipio: {municipio.nombre_municipio}',
        'municipio': municipio,
        'rol': request.session.get('rol_usuario', ''),
        'puede_editar': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO,
    })


@login_required
@rol_requerido(['administrativo'])
def municipios_editar(request, pk):
    """UPDATE: Editar municipio."""
    municipio = get_object_or_404(Municipio, pk=pk)
    if request.method == 'POST':
        form = MunicipioForm(request.POST, instance=municipio)
        if form.is_valid():
            mun = form.save(commit=False)
            mun.fecha_modificacion = timezone.now().date()
            mun.save()
            messages.success(
                request,
                f'✅ Municipio "{mun.nombre_municipio}" actualizado exitosamente.'
            )
            return redirect('municipios_lista')
    else:
        form = MunicipioForm(instance=municipio)

    return render(request, 'citas/municipios/formulario.html', {
        'form': form,
        'titulo': 'Editar Municipio',
        'accion': 'Actualizar',
        'municipio': municipio,
        'url_cancelar': 'municipios_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo'])
def municipios_eliminar(request, pk):
    """DELETE (Soft): Desactivar municipio."""
    municipio = get_object_or_404(Municipio, pk=pk)
    if request.method == 'POST':
        nombre = municipio.nombre_municipio
        if municipio.sedes.filter(activo='S').exists():
            messages.error(
                request,
                f'❌ No se puede desactivar "{nombre}" porque tiene sedes activas.'
            )
            return redirect('municipios_lista')
        municipio.activo = 'N'
        municipio.fecha_modificacion = timezone.now().date()
        municipio.save()
        messages.success(request, f'✅ Municipio "{nombre}" desactivado.')
        return redirect('municipios_lista')

    return render(request, 'citas/municipios/confirmar_eliminar.html', {
        'titulo': 'Desactivar Municipio',
        'municipio': municipio,
        'rol': request.session.get('rol_usuario', ''),
    })


# ===========================================================
# CRUD: SEDES
# ===========================================================

@login_required
def sedes_lista(request):
    """LIST: Listar sedes."""
    rol = request.session.get('rol_usuario', '')
    busqueda = request.GET.get('q', '')

    sedes = Sede.objects.select_related('id_municipio__id_departamento').all()
    if busqueda:
        sedes = sedes.filter(nombre_sede__icontains=busqueda) | \
                sedes.filter(codigo_sede__icontains=busqueda)

    paginator = Paginator(sedes, 10)
    page = request.GET.get('page')
    try:
        sedes_paginadas = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        sedes_paginadas = paginator.page(1)

    return render(request, 'citas/sedes/lista.html', {
        'titulo': 'Gestión de Sedes',
        'sedes': sedes_paginadas,
        'busqueda': busqueda,
        'rol': rol,
        'puede_crear': rol in ROLES_CRUD_COMPLETO,
        'puede_editar': rol in ROLES_CRUD_COMPLETO,
        'puede_eliminar': rol in ROLES_CRUD_COMPLETO,
        'total_registros': sedes.count(),
    })


@login_required
@rol_requerido(['administrativo'])
def sedes_crear(request):
    """CREATE: Crear nueva sede."""
    if request.method == 'POST':
        form = SedeForm(request.POST)
        if form.is_valid():
            sede = form.save(commit=False)
            sede.usuario_creacion = request.user.username
            sede.save()
            messages.success(request, f'✅ Sede "{sede.nombre_sede}" creada exitosamente.')
            return redirect('sedes_lista')
    else:
        form = SedeForm()

    return render(request, 'citas/sedes/formulario.html', {
        'form': form,
        'titulo': 'Crear Sede',
        'accion': 'Crear',
        'url_cancelar': 'sedes_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
def sedes_detalle(request, pk):
    """READ: Ver detalle de una sede."""
    sede = get_object_or_404(Sede, pk=pk)
    consultorios = sede.consultorios.filter(activo='S')
    return render(request, 'citas/sedes/detalle.html', {
        'titulo': f'Sede: {sede.nombre_sede}',
        'sede': sede,
        'consultorios': consultorios,
        'rol': request.session.get('rol_usuario', ''),
        'puede_editar': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO,
    })


@login_required
@rol_requerido(['administrativo'])
def sedes_editar(request, pk):
    """UPDATE: Editar sede."""
    sede = get_object_or_404(Sede, pk=pk)
    if request.method == 'POST':
        form = SedeForm(request.POST, instance=sede)
        if form.is_valid():
            s = form.save(commit=False)
            s.fecha_modificacion = timezone.now().date()
            s.save()
            messages.success(request, f'✅ Sede "{s.nombre_sede}" actualizada.')
            return redirect('sedes_lista')
    else:
        form = SedeForm(instance=sede)

    return render(request, 'citas/sedes/formulario.html', {
        'form': form,
        'titulo': 'Editar Sede',
        'accion': 'Actualizar',
        'sede': sede,
        'url_cancelar': 'sedes_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo'])
def sedes_eliminar(request, pk):
    """DELETE (Soft): Desactivar sede."""
    sede = get_object_or_404(Sede, pk=pk)
    if request.method == 'POST':
        nombre = sede.nombre_sede
        if sede.consultorios.filter(activo='S').exists():
            messages.error(request, f'❌ No se puede desactivar "{nombre}" porque tiene consultorios activos.')
            return redirect('sedes_lista')
        sede.activo = 'N'
        sede.fecha_modificacion = timezone.now().date()
        sede.save()
        messages.success(request, f'✅ Sede "{nombre}" desactivada.')
        return redirect('sedes_lista')

    return render(request, 'citas/sedes/confirmar_eliminar.html', {
        'titulo': 'Desactivar Sede',
        'sede': sede,
        'rol': request.session.get('rol_usuario', ''),
    })


# ===========================================================
# CRUD: CONSULTORIOS
# ===========================================================

@login_required
def consultorios_lista(request):
    """LIST: Listar consultorios."""
    rol = request.session.get('rol_usuario', '')
    busqueda = request.GET.get('q', '')
    sede_id = request.GET.get('sede', '')

    consultorios = Consultorio.objects.select_related('id_sede').all()
    if busqueda:
        consultorios = consultorios.filter(nombre_consultorio__icontains=busqueda) | \
                       consultorios.filter(codigo_consultorio__icontains=busqueda)
    if sede_id:
        consultorios = consultorios.filter(id_sede=sede_id)

    paginator = Paginator(consultorios, 10)
    page = request.GET.get('page')
    try:
        consultorios_paginados = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        consultorios_paginados = paginator.page(1)

    sedes = Sede.objects.filter(activo='S').order_by('nombre_sede')

    return render(request, 'citas/consultorios/lista.html', {
        'titulo': 'Gestión de Consultorios',
        'consultorios': consultorios_paginados,
        'sedes': sedes,
        'busqueda': busqueda,
        'sede_seleccionada': sede_id,
        'rol': rol,
        'puede_crear': rol in ROLES_CRUD_COMPLETO,
        'puede_editar': rol in ROLES_CRUD_COMPLETO,
        'puede_eliminar': rol in ROLES_CRUD_COMPLETO,
        'total_registros': consultorios.count(),
    })


@login_required
@rol_requerido(['administrativo'])
def consultorios_crear(request):
    """CREATE: Crear nuevo consultorio."""
    if request.method == 'POST':
        form = ConsultorioForm(request.POST)
        if form.is_valid():
            consultorio = form.save(commit=False)
            consultorio.usuario_creacion = request.user.username
            consultorio.save()
            messages.success(request, f'✅ Consultorio "{consultorio.nombre_consultorio}" creado.')
            return redirect('consultorios_lista')
    else:
        form = ConsultorioForm()

    return render(request, 'citas/consultorios/formulario.html', {
        'form': form,
        'titulo': 'Crear Consultorio',
        'accion': 'Crear',
        'url_cancelar': 'consultorios_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
def consultorios_detalle(request, pk):
    """READ: Ver detalle de un consultorio."""
    consultorio = get_object_or_404(Consultorio, pk=pk)
    return render(request, 'citas/consultorios/detalle.html', {
        'titulo': f'Consultorio: {consultorio.nombre_consultorio}',
        'consultorio': consultorio,
        'rol': request.session.get('rol_usuario', ''),
        'puede_editar': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO,
    })


@login_required
@rol_requerido(['administrativo'])
def consultorios_editar(request, pk):
    """UPDATE: Editar consultorio."""
    consultorio = get_object_or_404(Consultorio, pk=pk)
    if request.method == 'POST':
        form = ConsultorioForm(request.POST, instance=consultorio)
        if form.is_valid():
            c = form.save(commit=False)
            c.fecha_modificacion = timezone.now().date()
            c.save()
            messages.success(request, f'✅ Consultorio "{c.nombre_consultorio}" actualizado.')
            return redirect('consultorios_lista')
    else:
        form = ConsultorioForm(instance=consultorio)

    return render(request, 'citas/consultorios/formulario.html', {
        'form': form,
        'titulo': 'Editar Consultorio',
        'accion': 'Actualizar',
        'consultorio': consultorio,
        'url_cancelar': 'consultorios_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo'])
def consultorios_eliminar(request, pk):
    """DELETE (Soft): Desactivar consultorio."""
    consultorio = get_object_or_404(Consultorio, pk=pk)
    if request.method == 'POST':
        nombre = consultorio.nombre_consultorio
        consultorio.activo = 'N'
        consultorio.fecha_modificacion = timezone.now().date()
        consultorio.save()
        messages.success(request, f'✅ Consultorio "{nombre}" desactivado.')
        return redirect('consultorios_lista')

    return render(request, 'citas/consultorios/confirmar_eliminar.html', {
        'titulo': 'Desactivar Consultorio',
        'consultorio': consultorio,
        'rol': request.session.get('rol_usuario', ''),
    })


# ===========================================================
# VISTA: ACCESO DENEGADO
# ===========================================================
def acceso_denegado(request):
    """Vista para cuando un usuario intenta acceder a una función no permitida."""
    rol = request.session.get('rol_usuario', 'desconocido')
    return render(request, 'citas/acceso_denegado.html', {
        'titulo': 'Acceso Denegado',
        'rol': rol,
        'mensaje': f'El rol "{rol}" no tiene permisos para realizar esta acción.'
    }, status=403)
