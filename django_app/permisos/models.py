"""
MODELOS DE GESTIÓN DE PERMISOS
Sistema de Gestión de Citas Médicas

Tres tablas:
  PERMISOS_MODULOS     — módulos protegibles del sistema
  PERMISOS_ROL         — matriz rol × módulo con 4 flags CRUD
  PERMISOS_USUARIO     — override por usuario individual (null = hereda del rol)
"""

import os
from django.db import models
from django.contrib.auth.models import User

_DJANGO_MANAGED = os.environ.get('USE_SQLITE') == '1'

ROL_CHOICES = [
    ('administrativo', 'Administrativo'),
    ('medico', 'Médico'),
    ('paciente', 'Paciente'),
    ('auxiliar_medico', 'Auxiliar Médico'),
]


class Modulo(models.Model):
    """Módulos protegibles: departamentos, citas, médicos, etc."""
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código',
        db_column='CODIGO',
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre',
        db_column='NOMBRE',
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO',
    )

    class Meta:
        db_table = 'PERMISOS_MODULOS'
        managed = _DJANGO_MANAGED
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PermisoRol(models.Model):
    """Matriz rol × módulo con 4 flags CRUD."""
    rol = models.CharField(
        max_length=30,
        choices=ROL_CHOICES,
        verbose_name='Rol',
        db_column='ROL',
    )
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        verbose_name='Módulo',
        db_column='ID_MODULO',
        related_name='permisos_rol',
    )
    puede_ver = models.BooleanField(default=False, verbose_name='Ver', db_column='PUEDE_VER')
    puede_crear = models.BooleanField(default=False, verbose_name='Crear', db_column='PUEDE_CREAR')
    puede_editar = models.BooleanField(default=False, verbose_name='Editar', db_column='PUEDE_EDITAR')
    puede_eliminar = models.BooleanField(default=False, verbose_name='Eliminar', db_column='PUEDE_ELIMINAR')

    class Meta:
        db_table = 'PERMISOS_ROL'
        managed = _DJANGO_MANAGED
        verbose_name = 'Permiso por Rol'
        verbose_name_plural = 'Permisos por Rol'
        unique_together = ('rol', 'modulo')
        ordering = ['rol', 'modulo__nombre']

    def __str__(self):
        return f"{self.get_rol_display()} → {self.modulo}"


class PermisoUsuario(models.Model):
    """Override por usuario individual. null = hereda el permiso del rol."""
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        db_column='ID_USUARIO',
        related_name='permisos_usuario',
    )
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        verbose_name='Módulo',
        db_column='ID_MODULO',
        related_name='permisos_usuario',
    )
    # null = hereda del rol; True/False = override explícito
    puede_ver = models.BooleanField(null=True, blank=True, verbose_name='Ver', db_column='PUEDE_VER')
    puede_crear = models.BooleanField(null=True, blank=True, verbose_name='Crear', db_column='PUEDE_CREAR')
    puede_editar = models.BooleanField(null=True, blank=True, verbose_name='Editar', db_column='PUEDE_EDITAR')
    puede_eliminar = models.BooleanField(null=True, blank=True, verbose_name='Eliminar', db_column='PUEDE_ELIMINAR')

    class Meta:
        db_table = 'PERMISOS_USUARIO'
        managed = _DJANGO_MANAGED
        verbose_name = 'Permiso por Usuario'
        verbose_name_plural = 'Permisos por Usuario'
        unique_together = ('usuario', 'modulo')
        ordering = ['usuario__username', 'modulo__nombre']

    def __str__(self):
        return f"{self.usuario.username} → {self.modulo}"
