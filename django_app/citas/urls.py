"""
URLs del módulo CITAS
Sistema de Gestión de Citas Médicas

Patrón de URLs para los 4 CRUDs principales:
  /departamentos/          → Lista
  /departamentos/crear/    → Crear
  /departamentos/<pk>/     → Detalle
  /departamentos/<pk>/editar/   → Editar
  /departamentos/<pk>/eliminar/ → Eliminar (Soft delete)
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── MENÚ PRINCIPAL ──────────────────────────────────────
    path('menu/', views.menu_principal, name='menu_principal'),
    path('acceso-denegado/', views.acceso_denegado, name='acceso_denegado'),

    # ── DEPARTAMENTOS ────────────────────────────────────────
    path('departamentos/', views.departamentos_lista, name='departamentos_lista'),
    path('departamentos/crear/', views.departamentos_crear, name='departamentos_crear'),
    path('departamentos/<int:pk>/', views.departamentos_detalle, name='departamentos_detalle'),
    path('departamentos/<int:pk>/editar/', views.departamentos_editar, name='departamentos_editar'),
    path('departamentos/<int:pk>/eliminar/', views.departamentos_eliminar, name='departamentos_eliminar'),

    # ── MUNICIPIOS ───────────────────────────────────────────
    path('municipios/', views.municipios_lista, name='municipios_lista'),
    path('municipios/crear/', views.municipios_crear, name='municipios_crear'),
    path('municipios/<int:pk>/', views.municipios_detalle, name='municipios_detalle'),
    path('municipios/<int:pk>/editar/', views.municipios_editar, name='municipios_editar'),
    path('municipios/<int:pk>/eliminar/', views.municipios_eliminar, name='municipios_eliminar'),

    # ── SEDES ────────────────────────────────────────────────
    path('sedes/', views.sedes_lista, name='sedes_lista'),
    path('sedes/crear/', views.sedes_crear, name='sedes_crear'),
    path('sedes/<int:pk>/', views.sedes_detalle, name='sedes_detalle'),
    path('sedes/<int:pk>/editar/', views.sedes_editar, name='sedes_editar'),
    path('sedes/<int:pk>/eliminar/', views.sedes_eliminar, name='sedes_eliminar'),

    # ── CONSULTORIOS ─────────────────────────────────────────
    path('consultorios/', views.consultorios_lista, name='consultorios_lista'),
    path('consultorios/crear/', views.consultorios_crear, name='consultorios_crear'),
    path('consultorios/<int:pk>/', views.consultorios_detalle, name='consultorios_detalle'),
    path('consultorios/<int:pk>/editar/', views.consultorios_editar, name='consultorios_editar'),
    path('consultorios/<int:pk>/eliminar/', views.consultorios_eliminar, name='consultorios_eliminar'),

    # ── ESPECIALIDADES ───────────────────────────────────────
    path('especialidades/', views.especialidades_lista, name='especialidades_lista'),
    path('especialidades/crear/', views.especialidades_crear, name='especialidades_crear'),
    path('especialidades/<int:pk>/', views.especialidades_detalle, name='especialidades_detalle'),
    path('especialidades/<int:pk>/editar/', views.especialidades_editar, name='especialidades_editar'),
    path('especialidades/<int:pk>/eliminar/', views.especialidades_eliminar, name='especialidades_eliminar'),

    # ── MÉDICOS ──────────────────────────────────────────────
    path('medicos/', views.medicos_lista, name='medicos_lista'),
    path('medicos/crear/', views.medicos_crear, name='medicos_crear'),
    path('medicos/<int:pk>/', views.medicos_detalle, name='medicos_detalle'),
    path('medicos/<int:pk>/editar/', views.medicos_editar, name='medicos_editar'),
    path('medicos/<int:pk>/eliminar/', views.medicos_eliminar, name='medicos_eliminar'),

    # ── PACIENTES ────────────────────────────────────────────
    path('pacientes/', views.pacientes_lista, name='pacientes_lista'),
    path('pacientes/crear/', views.pacientes_crear, name='pacientes_crear'),
    path('pacientes/<int:pk>/', views.pacientes_detalle, name='pacientes_detalle'),
    path('pacientes/<int:pk>/editar/', views.pacientes_editar, name='pacientes_editar'),
    path('pacientes/<int:pk>/eliminar/', views.pacientes_eliminar, name='pacientes_eliminar'),

    # ── CITAS MÉDICAS ───────────────────────────────────────
    path('citas/', views.citas_lista, name='citas_lista'),
    path('citas/crear/', views.citas_crear, name='citas_crear'),
    path('citas/<int:pk>/', views.citas_detalle, name='citas_detalle'),
    path('citas/<int:pk>/editar/', views.citas_editar, name='citas_editar'),
    path('citas/<int:pk>/eliminar/', views.citas_eliminar, name='citas_eliminar'),
    path('citas/<int:pk>/cambiar-estado/', views.citas_cambiar_estado, name='citas_cambiar_estado'),

    # ── AUDITORÍA (Fase 4) ───────────────────────────────────
    path('auditoria/', views.auditoria_lista, name='auditoria_lista'),
]
