from django.urls import path
from . import views

app_name = 'permisos'

urlpatterns = [
    # Matriz rol × módulo (Fase 3 — Milton implementa los templates)
    path('', views.permisos_matriz, name='matriz'),
    path('usuario/<int:usuario_id>/', views.permisos_usuario_detalle, name='usuario_detalle'),
    path('usuario/<int:usuario_id>/reset/', views.permisos_usuario_reset, name='usuario_reset'),
]
