"""
URLs principales del proyecto
Sistema de Gestión de Citas Médicas
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin de Django (solo para desarrollo)
    path('admin/', admin.site.urls),

    # Autenticación (login, logout)
    path('', include('usuarios.urls')),

    # Módulo principal de citas (menú + CRUDs)
    path('', include('citas.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Personalizar el admin de Django
admin.site.site_header = 'Sistema de Gestión de Citas Médicas'
admin.site.site_title = 'Citas Médicas Admin'
admin.site.index_title = 'Panel de Administración'
