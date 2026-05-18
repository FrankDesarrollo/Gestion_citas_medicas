from django.contrib import admin
from .models import Modulo, PermisoRol, PermisoUsuario


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo')
    search_fields = ('codigo', 'nombre')
    list_filter = ('activo',)


@admin.register(PermisoRol)
class PermisoRolAdmin(admin.ModelAdmin):
    list_display = ('rol', 'modulo', 'puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar')
    list_filter = ('rol', 'modulo')


@admin.register(PermisoUsuario)
class PermisoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'modulo', 'puede_ver', 'puede_crear', 'puede_editar', 'puede_eliminar')
    list_filter = ('modulo',)
    search_fields = ('usuario__username',)
