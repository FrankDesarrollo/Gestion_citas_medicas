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

from .models import Departamento, Municipio, Sede, Consultorio, Especialidad, Persona, Medico, Paciente, CitaMedica, AuditoriaAccion
from .forms import (
    DepartamentoForm, MunicipioForm, SedeForm, ConsultorioForm,
    EspecialidadForm, PersonaForm, MedicoForm, PacienteForm,
    CitaMedicaForm, CitaEstadoForm
)
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
    Vista del menú principal (Dashboard).
    Conteos reales por entidad + agenda del día + últimas citas.
    """
    rol = request.session.get('rol_usuario', '')
    hoy = timezone.localdate()

    # Conteos solo de registros activos
    total_departamentos = Departamento.objects.filter(activo='S').count()
    total_municipios = Municipio.objects.filter(activo='S').count()
    total_sedes = Sede.objects.filter(activo='S').count()
    total_consultorios = Consultorio.objects.filter(activo='S').count()
    total_especialidades = Especialidad.objects.filter(activo='S').count()
    total_medicos = Medico.objects.filter(activo='S').count()
    total_pacientes = Paciente.objects.filter(activo='S').count()
    total_citas = CitaMedica.objects.filter(activo='S').count()

    # Citas por estado (solo activas)
    citas_activas = CitaMedica.objects.filter(activo='S')
    citas_por_estado = {
        'PROGRAMADA': citas_activas.filter(estado='PROGRAMADA').count(),
        'CONFIRMADA': citas_activas.filter(estado='CONFIRMADA').count(),
        'ATENDIDA': citas_activas.filter(estado='ATENDIDA').count(),
        'CANCELADA': citas_activas.filter(estado='CANCELADA').count(),
        'NO_ASISTIO': citas_activas.filter(estado='NO_ASISTIO').count(),
    }

    # Agenda del día — citas activas con fecha = hoy
    agenda_hoy = (
        citas_activas
        .filter(fecha_cita=hoy)
        .select_related(
            'id_paciente__id_persona', 'id_medico__id_persona',
            'id_medico__id_especialidad', 'id_consultorio__id_sede',
        )
        .order_by('hora_inicio')
    )

    # Próximas citas (futuras, excluyendo hoy) — máx 5
    proximas_citas = (
        citas_activas
        .filter(fecha_cita__gt=hoy, estado__in=['PROGRAMADA', 'CONFIRMADA'])
        .select_related(
            'id_paciente__id_persona', 'id_medico__id_persona',
            'id_consultorio__id_sede',
        )
        .order_by('fecha_cita', 'hora_inicio')[:5]
    )

    contexto = {
        'rol': rol,
        'usuario': request.user,
        'titulo': 'Dashboard',
        'puede_gestionar_maestros': rol in ROLES_CRUD_COMPLETO,
        'es_medico': rol == 'medico',
        'es_paciente': rol == 'paciente',
        'es_auxiliar': rol == 'auxiliar_medico',
        # Conteos
        'total_departamentos': total_departamentos,
        'total_municipios': total_municipios,
        'total_sedes': total_sedes,
        'total_consultorios': total_consultorios,
        'total_especialidades': total_especialidades,
        'total_medicos': total_medicos,
        'total_pacientes': total_pacientes,
        'total_citas': total_citas,
        'citas_por_estado': citas_por_estado,
        # Agenda
        'agenda_hoy': agenda_hoy,
        'proximas_citas': proximas_citas,
        'hoy': hoy,
    }
    logger.info(f"Usuario {request.user.username} (rol: {rol}) accedió al dashboard")
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


# ===========================================================
# CRUD: ESPECIALIDADES
# ===========================================================

@login_required
def especialidades_lista(request):
    """LIST: Listar especialidades."""
    rol = request.session.get('rol_usuario', '')
    busqueda = request.GET.get('q', '')

    especialidades = Especialidad.objects.all()
    if busqueda:
        especialidades = especialidades.filter(
            nombre_especialidad__icontains=busqueda
        ) | especialidades.filter(
            codigo_especialidad__icontains=busqueda
        )

    paginator = Paginator(especialidades, 10)
    page = request.GET.get('page')
    try:
        especialidades_paginadas = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        especialidades_paginadas = paginator.page(1)

    return render(request, 'citas/especialidades/lista.html', {
        'titulo': 'Gestión de Especialidades Médicas',
        'especialidades': especialidades_paginadas,
        'busqueda': busqueda,
        'rol': rol,
        'puede_crear': rol in ROLES_CRUD_COMPLETO,
        'puede_editar': rol in ROLES_CRUD_COMPLETO,
        'puede_eliminar': rol in ROLES_CRUD_COMPLETO,
        'total_registros': especialidades.count(),
    })


@login_required
@rol_requerido(['administrativo'])
def especialidades_crear(request):
    """CREATE: Crear nueva especialidad."""
    if request.method == 'POST':
        form = EspecialidadForm(request.POST)
        if form.is_valid():
            esp = form.save(commit=False)
            esp.usuario_creacion = request.user.username
            esp.save()
            messages.success(request, f'✅ Especialidad "{esp.nombre_especialidad}" creada.')
            return redirect('especialidades_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        form = EspecialidadForm()

    return render(request, 'citas/especialidades/formulario.html', {
        'form': form,
        'titulo': 'Crear Especialidad',
        'accion': 'Crear',
        'url_cancelar': 'especialidades_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
def especialidades_detalle(request, pk):
    """READ: Ver detalle de una especialidad."""
    especialidad = get_object_or_404(Especialidad, pk=pk)
    medicos = especialidad.medicos.filter(activo='S').select_related('id_persona')
    return render(request, 'citas/especialidades/detalle.html', {
        'titulo': f'Especialidad: {especialidad.nombre_especialidad}',
        'especialidad': especialidad,
        'medicos': medicos,
        'rol': request.session.get('rol_usuario', ''),
        'puede_editar': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO,
    })


@login_required
@rol_requerido(['administrativo'])
def especialidades_editar(request, pk):
    """UPDATE: Editar especialidad."""
    especialidad = get_object_or_404(Especialidad, pk=pk)
    if request.method == 'POST':
        form = EspecialidadForm(request.POST, instance=especialidad)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Especialidad "{especialidad.nombre_especialidad}" actualizada.')
            return redirect('especialidades_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        form = EspecialidadForm(instance=especialidad)

    return render(request, 'citas/especialidades/formulario.html', {
        'form': form,
        'titulo': 'Editar Especialidad',
        'accion': 'Actualizar',
        'url_cancelar': 'especialidades_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo'])
def especialidades_eliminar(request, pk):
    """DELETE (Soft): Desactivar especialidad."""
    especialidad = get_object_or_404(Especialidad, pk=pk)
    if request.method == 'POST':
        nombre = especialidad.nombre_especialidad
        if especialidad.medicos.filter(activo='S').exists():
            messages.error(
                request,
                f'❌ No se puede desactivar "{nombre}" porque tiene médicos activos asociados.'
            )
            return redirect('especialidades_lista')
        especialidad.activo = 'N'
        especialidad.save()
        messages.success(request, f'✅ Especialidad "{nombre}" desactivada.')
        return redirect('especialidades_lista')

    return render(request, 'citas/especialidades/confirmar_eliminar.html', {
        'titulo': 'Desactivar Especialidad',
        'especialidad': especialidad,
        'rol': request.session.get('rol_usuario', ''),
    })


# ===========================================================
# CRUD: MÉDICOS
# ===========================================================

@login_required
def medicos_lista(request):
    """LIST: Listar médicos."""
    rol = request.session.get('rol_usuario', '')
    busqueda = request.GET.get('q', '')
    especialidad_id = request.GET.get('especialidad', '')

    medicos = Medico.objects.select_related('id_persona', 'id_especialidad').all()
    if busqueda:
        medicos = medicos.filter(
            id_persona__primer_nombre__icontains=busqueda
        ) | medicos.filter(
            id_persona__primer_apellido__icontains=busqueda
        ) | medicos.filter(
            numero_registro__icontains=busqueda
        )
    if especialidad_id:
        medicos = medicos.filter(id_especialidad=especialidad_id)

    paginator = Paginator(medicos, 10)
    page = request.GET.get('page')
    try:
        medicos_paginados = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        medicos_paginados = paginator.page(1)

    especialidades = Especialidad.objects.filter(activo='S').order_by('nombre_especialidad')

    return render(request, 'citas/medicos/lista.html', {
        'titulo': 'Gestión de Médicos',
        'medicos': medicos_paginados,
        'especialidades': especialidades,
        'busqueda': busqueda,
        'especialidad_seleccionada': especialidad_id,
        'rol': rol,
        'puede_crear': rol in ROLES_CRUD_COMPLETO,
        'puede_editar': rol in ROLES_CRUD_COMPLETO,
        'puede_eliminar': rol in ROLES_CRUD_COMPLETO,
        'total_registros': medicos.count(),
    })


@login_required
@rol_requerido(['administrativo'])
def medicos_crear(request):
    """CREATE: Crear nuevo médico (Persona + Medico)."""
    if request.method == 'POST':
        persona_form = PersonaForm(request.POST, prefix='persona')
        medico_form = MedicoForm(request.POST, prefix='medico')
        if persona_form.is_valid() and medico_form.is_valid():
            persona = persona_form.save(commit=False)
            persona.usuario_creacion = request.user.username
            persona.save()

            medico = medico_form.save(commit=False)
            medico.id_persona = persona
            medico.save()

            messages.success(
                request,
                f'✅ Médico "{persona.primer_nombre} {persona.primer_apellido}" creado.'
            )
            return redirect('medicos_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        persona_form = PersonaForm(prefix='persona')
        medico_form = MedicoForm(prefix='medico')

    return render(request, 'citas/medicos/formulario.html', {
        'persona_form': persona_form,
        'medico_form': medico_form,
        'titulo': 'Crear Médico',
        'accion': 'Crear',
        'url_cancelar': 'medicos_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
def medicos_detalle(request, pk):
    """READ: Ver detalle de un médico."""
    medico = get_object_or_404(
        Medico.objects.select_related('id_persona', 'id_especialidad'),
        pk=pk
    )
    citas = medico.citas.filter(activo='S').order_by('-fecha_cita', '-hora_inicio')[:10]
    return render(request, 'citas/medicos/detalle.html', {
        'titulo': f'Médico: {medico.nombre_completo}',
        'medico': medico,
        'citas': citas,
        'rol': request.session.get('rol_usuario', ''),
        'puede_editar': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO,
    })


@login_required
@rol_requerido(['administrativo'])
def medicos_editar(request, pk):
    """UPDATE: Editar médico."""
    medico = get_object_or_404(
        Medico.objects.select_related('id_persona'),
        pk=pk
    )
    if request.method == 'POST':
        persona_form = PersonaForm(request.POST, instance=medico.id_persona, prefix='persona')
        medico_form = MedicoForm(request.POST, instance=medico, prefix='medico')
        if persona_form.is_valid() and medico_form.is_valid():
            persona_form.save()
            medico_form.save()
            messages.success(request, f'✅ Médico "{medico.nombre_completo}" actualizado.')
            return redirect('medicos_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        persona_form = PersonaForm(instance=medico.id_persona, prefix='persona')
        medico_form = MedicoForm(instance=medico, prefix='medico')

    return render(request, 'citas/medicos/formulario.html', {
        'persona_form': persona_form,
        'medico_form': medico_form,
        'titulo': 'Editar Médico',
        'accion': 'Actualizar',
        'url_cancelar': 'medicos_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo'])
def medicos_eliminar(request, pk):
    """DELETE (Soft): Desactivar médico."""
    medico = get_object_or_404(Medico, pk=pk)
    if request.method == 'POST':
        nombre = medico.nombre_completo
        medico.activo = 'N'
        medico.fecha_modificacion = timezone.now().date()
        medico.save()
        messages.success(request, f'✅ Médico "{nombre}" desactivado.')
        return redirect('medicos_lista')

    return render(request, 'citas/medicos/confirmar_eliminar.html', {
        'titulo': 'Desactivar Médico',
        'medico': medico,
        'rol': request.session.get('rol_usuario', ''),
    })


# ===========================================================
# CRUD: PACIENTES
# ===========================================================

@login_required
def pacientes_lista(request):
    """LIST: Listar pacientes."""
    rol = request.session.get('rol_usuario', '')
    busqueda = request.GET.get('q', '')

    pacientes = Paciente.objects.select_related('id_persona').all()

    if busqueda:
        pacientes = pacientes.filter(
            id_persona__primer_nombre__icontains=busqueda
        ) | pacientes.filter(
            id_persona__primer_apellido__icontains=busqueda
        ) | pacientes.filter(
            numero_historia__icontains=busqueda
        )

    # Pacientes solo ven sus propios datos
    if rol == 'paciente':
        # Si hay un usuario de persona vinculado, filtrar
        persona = Persona.objects.filter(
            numero_documento=request.user.username
        ).first()
        if persona:
            pacientes = pacientes.filter(id_persona=persona)

    paginator = Paginator(pacientes, 10)
    page = request.GET.get('page')
    try:
        pacientes_paginados = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        pacientes_paginados = paginator.page(1)

    return render(request, 'citas/pacientes/lista.html', {
        'titulo': 'Gestión de Pacientes',
        'pacientes': pacientes_paginados,
        'busqueda': busqueda,
        'rol': rol,
        'puede_crear': rol in ROLES_CRUD_COMPLETO,
        'puede_editar': rol in ROLES_CRUD_COMPLETO,
        'puede_eliminar': rol in ROLES_CRUD_COMPLETO,
        'total_registros': pacientes.count(),
    })


@login_required
@rol_requerido(['administrativo'])
def pacientes_crear(request):
    """CREATE: Crear nuevo paciente (Persona + Paciente)."""
    if request.method == 'POST':
        persona_form = PersonaForm(request.POST, prefix='persona')
        paciente_form = PacienteForm(request.POST, prefix='paciente')
        if persona_form.is_valid() and paciente_form.is_valid():
            persona = persona_form.save(commit=False)
            persona.usuario_creacion = request.user.username
            persona.save()

            paciente = paciente_form.save(commit=False)
            paciente.id_persona = persona
            paciente.save()

            messages.success(
                request,
                f'✅ Paciente "{persona.primer_nombre} {persona.primer_apellido}" creado.'
            )
            return redirect('pacientes_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        persona_form = PersonaForm(prefix='persona')
        paciente_form = PacienteForm(prefix='paciente')

    return render(request, 'citas/pacientes/formulario.html', {
        'persona_form': persona_form,
        'paciente_form': paciente_form,
        'titulo': 'Crear Paciente',
        'accion': 'Crear',
        'url_cancelar': 'pacientes_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
def pacientes_detalle(request, pk):
    """READ: Ver detalle de un paciente."""
    paciente = get_object_or_404(
        Paciente.objects.select_related('id_persona'),
        pk=pk
    )
    citas = paciente.citas.filter(activo='S').order_by('-fecha_cita', '-hora_inicio')[:10]
    return render(request, 'citas/pacientes/detalle.html', {
        'titulo': f'Paciente: {paciente.nombre_completo}',
        'paciente': paciente,
        'citas': citas,
        'rol': request.session.get('rol_usuario', ''),
        'puede_editar': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO,
    })


@login_required
@rol_requerido(['administrativo'])
def pacientes_editar(request, pk):
    """UPDATE: Editar paciente."""
    paciente = get_object_or_404(
        Paciente.objects.select_related('id_persona'),
        pk=pk
    )
    if request.method == 'POST':
        persona_form = PersonaForm(request.POST, instance=paciente.id_persona, prefix='persona')
        paciente_form = PacienteForm(request.POST, instance=paciente, prefix='paciente')
        if persona_form.is_valid() and paciente_form.is_valid():
            persona_form.save()
            paciente_form.save()
            messages.success(request, f'✅ Paciente "{paciente.nombre_completo}" actualizado.')
            return redirect('pacientes_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        persona_form = PersonaForm(instance=paciente.id_persona, prefix='persona')
        paciente_form = PacienteForm(instance=paciente, prefix='paciente')

    return render(request, 'citas/pacientes/formulario.html', {
        'persona_form': persona_form,
        'paciente_form': paciente_form,
        'titulo': 'Editar Paciente',
        'accion': 'Actualizar',
        'url_cancelar': 'pacientes_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo'])
def pacientes_eliminar(request, pk):
    """DELETE (Soft): Desactivar paciente."""
    paciente = get_object_or_404(Paciente, pk=pk)
    if request.method == 'POST':
        nombre = paciente.nombre_completo
        paciente.activo = 'N'
        paciente.save()
        messages.success(request, f'✅ Paciente "{nombre}" desactivado.')
        return redirect('pacientes_lista')

    return render(request, 'citas/pacientes/confirmar_eliminar.html', {
        'titulo': 'Desactivar Paciente',
        'paciente': paciente,
        'rol': request.session.get('rol_usuario', ''),
    })


# ===========================================================
# CRUD: CITAS MÉDICAS
# ===========================================================

ESTADOS_TRANSICION = {
    'PROGRAMADA': ['CONFIRMADA', 'CANCELADA'],
    'CONFIRMADA': ['ATENDIDA', 'CANCELADA', 'NO_ASISTIO'],
    'ATENDIDA': [],
    'CANCELADA': [],
    'NO_ASISTIO': [],
}


def _generar_numero_cita():
    """Genera un número único de cita: CITA-YYYYMMDD-XXXX."""
    from datetime import datetime
    fecha = datetime.now().strftime('%Y%m%d')
    ultimo = CitaMedica.objects.filter(numero_cita__startswith=f'CITA-{fecha}').count()
    return f'CITA-{fecha}-{ultimo + 1:04d}'


@login_required
def citas_lista(request):
    """LIST: Listar citas médicas con filtros por rol y estado."""
    rol = request.session.get('rol_usuario', '')
    busqueda = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    fecha = request.GET.get('fecha', '')

    citas = CitaMedica.objects.select_related(
        'id_paciente__id_persona',
        'id_medico__id_persona',
        'id_medico__id_especialidad',
        'id_consultorio__id_sede'
    ).filter(activo='S')

    # Filtro por rol
    if rol == 'paciente':
        persona = Persona.objects.filter(
            numero_documento=request.user.username
        ).first()
        if persona:
            paciente = Paciente.objects.filter(id_persona=persona).first()
            if paciente:
                citas = citas.filter(id_paciente=paciente)
    elif rol == 'medico':
        persona = Persona.objects.filter(
            numero_documento=request.user.username
        ).first()
        if persona:
            medico = Medico.objects.filter(id_persona=persona).first()
            if medico:
                citas = citas.filter(id_medico=medico)

    # Filtros adicionales
    if busqueda:
        citas = citas.filter(
            numero_cita__icontains=busqueda
        ) | citas.filter(
            id_paciente__id_persona__primer_nombre__icontains=busqueda
        ) | citas.filter(
            id_medico__id_persona__primer_nombre__icontains=busqueda
        )
    if estado:
        citas = citas.filter(estado=estado)
    if fecha:
        citas = citas.filter(fecha_cita=fecha)

    citas = citas.order_by('-fecha_cita', '-hora_inicio')

    paginator = Paginator(citas, 10)
    page = request.GET.get('page')
    try:
        citas_paginadas = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        citas_paginadas = paginator.page(1)

    return render(request, 'citas/citas_medicas/lista.html', {
        'titulo': 'Gestión de Citas Médicas',
        'citas': citas_paginadas,
        'busqueda': busqueda,
        'estado_seleccionado': estado,
        'fecha_seleccionada': fecha,
        'rol': rol,
        'puede_crear': rol in ROLES_CRUD_COMPLETO or rol == 'auxiliar_medico',
        'puede_editar': rol in ROLES_CRUD_COMPLETO,
        'puede_eliminar': rol in ROLES_CRUD_COMPLETO,
        'total_registros': citas.count(),
    })


@login_required
@rol_requerido(['administrativo', 'auxiliar_medico'])
def citas_crear(request):
    """CREATE: Crear nueva cita médica."""
    if request.method == 'POST':
        form = CitaMedicaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.numero_cita = _generar_numero_cita()
            cita.usuario_creacion = request.user.username
            cita.estado = 'PROGRAMADA'
            cita.save()
            messages.success(
                request,
                f'✅ Cita "{cita.numero_cita}" creada para el {cita.fecha_cita} a las {cita.hora_inicio}.'
            )
            return redirect('citas_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        form = CitaMedicaForm()

    return render(request, 'citas/citas_medicas/formulario.html', {
        'form': form,
        'titulo': 'Crear Cita Médica',
        'accion': 'Crear',
        'url_cancelar': 'citas_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
def citas_detalle(request, pk):
    """READ: Ver detalle de una cita médica."""
    cita = get_object_or_404(
        CitaMedica.objects.select_related(
            'id_paciente__id_persona',
            'id_medico__id_persona', 'id_medico__id_especialidad',
            'id_consultorio__id_sede'
        ),
        pk=pk
    )
    estados_permitidos = ESTADOS_TRANSICION.get(cita.estado, [])
    return render(request, 'citas/citas_medicas/detalle.html', {
        'titulo': f'Cita #{cita.numero_cita}',
        'cita': cita,
        'estados_permitidos': estados_permitidos,
        'rol': request.session.get('rol_usuario', ''),
        'puede_cambiar_estado': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO or request.session.get('rol_usuario', '') == 'medico',
        'puede_editar': request.session.get('rol_usuario', '') in ROLES_CRUD_COMPLETO,
    })


@login_required
@rol_requerido(['administrativo'])
def citas_editar(request, pk):
    """UPDATE: Editar cita médica."""
    cita = get_object_or_404(CitaMedica, pk=pk)
    if request.method == 'POST':
        form = CitaMedicaForm(request.POST, instance=cita)
        if form.is_valid():
            c = form.save(commit=False)
            c.fecha_modificacion = timezone.now().date()
            c.save()
            messages.success(request, f'✅ Cita "{c.numero_cita}" actualizada.')
            return redirect('citas_lista')
        else:
            messages.error(request, '❌ Por favor corrija los errores del formulario.')
    else:
        form = CitaMedicaForm(instance=cita)

    return render(request, 'citas/citas_medicas/formulario.html', {
        'form': form,
        'titulo': 'Editar Cita Médica',
        'accion': 'Actualizar',
        'url_cancelar': 'citas_lista',
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo'])
def citas_eliminar(request, pk):
    """DELETE (Soft): Desactivar (cancelar) una cita médica."""
    cita = get_object_or_404(CitaMedica, pk=pk)
    if request.method == 'POST':
        cita.activo = 'N'
        cita.estado = 'CANCELADA'
        cita.fecha_modificacion = timezone.now().date()
        cita.save()
        messages.success(request, f'✅ Cita "{cita.numero_cita}" cancelada y desactivada.')
        return redirect('citas_lista')

    return render(request, 'citas/citas_medicas/confirmar_eliminar.html', {
        'titulo': 'Cancelar Cita Médica',
        'cita': cita,
        'rol': request.session.get('rol_usuario', ''),
    })


@login_required
@rol_requerido(['administrativo', 'medico'])
def citas_cambiar_estado(request, pk):
    """Cambiar el estado de una cita médica (confirmar, atender, etc.)."""
    cita = get_object_or_404(CitaMedica, pk=pk)
    estados_permitidos = ESTADOS_TRANSICION.get(cita.estado, [])

    if not estados_permitidos:
        messages.error(
            request,
            f'❌ La cita en estado "{cita.estado}" no permite cambios de estado.'
        )
        return redirect('citas_detalle', pk=pk)

    if request.method == 'POST':
        form = CitaEstadoForm(request.POST, instance=cita)
        if form.is_valid():
            nuevo_estado = form.cleaned_data['estado']
            if nuevo_estado not in estados_permitidos:
                messages.error(
                    request,
                    f'❌ No se puede cambiar de "{cita.estado}" a "{nuevo_estado}".'
                )
            else:
                c = form.save(commit=False)
                c.fecha_modificacion = timezone.now().date()
                c.save()
                messages.success(
                    request,
                    f'✅ Estado de cita "{cita.numero_cita}" cambiado a "{nuevo_estado}".'
                )
                return redirect('citas_detalle', pk=pk)
        else:
            messages.error(request, '❌ Por favor corrija los errores.')
    else:
        form = CitaEstadoForm(instance=cita)

    return render(request, 'citas/citas_medicas/cambiar_estado.html', {
        'form': form,
        'titulo': f'Cambiar Estado — Cita #{cita.numero_cita}',
        'cita': cita,
        'estados_permitidos': estados_permitidos,
        'rol': request.session.get('rol_usuario', ''),
    })


# ===========================================================
# AUDITORÍA (solo lectura) — Fase 4
# ===========================================================
@login_required
@rol_requerido(['administrativo'])
def auditoria_lista(request):
    """
    LIST: Vista de auditoría de acciones.
    Solo administrativo. Muestra los registros que llenan los triggers
    de Oracle (en SQLite dev queda vacía hasta que se inserte manual).
    Filtros: tabla, accion, fecha desde/hasta, búsqueda libre.
    """
    qs = AuditoriaAccion.objects.all()

    tabla = request.GET.get('tabla', '').strip()
    accion = request.GET.get('accion', '').strip()
    desde = request.GET.get('desde', '').strip()
    hasta = request.GET.get('hasta', '').strip()
    busqueda = request.GET.get('q', '').strip()

    if tabla:
        qs = qs.filter(tabla_afectada__iexact=tabla)
    if accion:
        qs = qs.filter(accion=accion)
    if desde:
        qs = qs.filter(fecha_accion__date__gte=desde)
    if hasta:
        qs = qs.filter(fecha_accion__date__lte=hasta)
    if busqueda:
        qs = qs.filter(usuario_bd__icontains=busqueda) | qs.filter(rol_activo__icontains=busqueda)

    paginator = Paginator(qs, 25)
    page = request.GET.get('page')
    try:
        registros = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        registros = paginator.page(1)

    tablas_distintas = (
        AuditoriaAccion.objects.values_list('tabla_afectada', flat=True)
        .distinct().order_by('tabla_afectada')
    )

    return render(request, 'citas/auditoria/lista.html', {
        'titulo': 'Auditoría de Acciones',
        'registros': registros,
        'tablas_distintas': tablas_distintas,
        'acciones': ['INSERT', 'UPDATE', 'DELETE', 'SELECT'],
        'tabla': tabla,
        'accion': accion,
        'desde': desde,
        'hasta': hasta,
        'busqueda': busqueda,
        'total_registros': qs.count(),
        'rol': request.session.get('rol_usuario', ''),
    })
