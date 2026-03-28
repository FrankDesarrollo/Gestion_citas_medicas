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
]
