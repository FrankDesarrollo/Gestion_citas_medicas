"""
Migración de datos: carga los módulos del sistema y los permisos por defecto.
Replica exactamente los permisos hardcoded de citas/decorators.py:
  - administrativo: CRUD completo en todos los módulos
  - medico:         solo lectura
  - paciente:       solo lectura
  - auxiliar_medico: solo lectura
"""

from django.db import migrations


MODULOS = [
    ('departamentos', 'Departamentos'),
    ('municipios',    'Municipios'),
    ('sedes',         'Sedes'),
    ('consultorios',  'Consultorios'),
    ('especialidades', 'Especialidades'),
    ('medicos',       'Médicos'),
    ('pacientes',     'Pacientes'),
    ('citas',         'Citas Médicas'),
    ('auditoria',     'Auditoría'),
]

ROLES = ['administrativo', 'medico', 'paciente', 'auxiliar_medico']


def cargar_datos(apps, schema_editor):
    Modulo = apps.get_model('permisos', 'Modulo')
    PermisoRol = apps.get_model('permisos', 'PermisoRol')

    modulos_creados = {}
    for codigo, nombre in MODULOS:
        m, _ = Modulo.objects.get_or_create(
            codigo=codigo,
            defaults={'nombre': nombre, 'activo': 'S'},
        )
        modulos_creados[codigo] = m

    for modulo in modulos_creados.values():
        for rol in ROLES:
            es_admin = rol == 'administrativo'
            PermisoRol.objects.get_or_create(
                rol=rol,
                modulo=modulo,
                defaults={
                    'puede_ver':      True,
                    'puede_crear':    es_admin,
                    'puede_editar':   es_admin,
                    'puede_eliminar': es_admin,
                },
            )


def revertir_datos(apps, schema_editor):
    Modulo = apps.get_model('permisos', 'Modulo')
    PermisoRol = apps.get_model('permisos', 'PermisoRol')
    PermisoRol.objects.all().delete()
    Modulo.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('permisos', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(cargar_datos, revertir_datos),
    ]
