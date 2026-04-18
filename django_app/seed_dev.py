"""
Semilla de datos de desarrollo (SQLite fallback).
Ejecutar con:
    USE_SQLITE=1 py seed_dev.py
Idempotente: limpia y recarga los datos cada vez.
"""
import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_citas.settings')
os.environ.setdefault('USE_SQLITE', '1')
django.setup()

from django.contrib.auth.models import User
from citas.models import (
    Departamento, Municipio, Sede, Consultorio,
    Especialidad, Persona, Medico, Paciente, CitaMedica,
)

USUARIO = 'seed'

print('>> Limpiando datos previos...')
CitaMedica.objects.all().delete()
Medico.objects.all().delete()
Paciente.objects.all().delete()
Persona.objects.all().delete()
Especialidad.objects.all().delete()
Consultorio.objects.all().delete()
Sede.objects.all().delete()
Municipio.objects.all().delete()
Departamento.objects.all().delete()

# ============================================================
# USUARIOS POR ROL (todos con password demo)
# ============================================================
print('>> Creando usuarios por rol...')
demo_users = [
    ('medico', 'Med2024#', 'Carlos', 'Ramirez'),
    ('paciente', 'Pac2024#', 'Maria', 'Lopez'),
    ('administrativo', 'Adm2024#', 'Ana', 'Torres'),
    ('auxiliar', 'Aux2024#', 'Luis', 'Gomez'),
]
for username, pwd, fn, ln in demo_users:
    u, _ = User.objects.get_or_create(
        username=username,
        defaults={'first_name': fn, 'last_name': ln, 'email': f'{username}@citas.local'},
    )
    u.set_password(pwd)
    u.is_active = True
    u.save()

# ============================================================
# DEPARTAMENTOS + MUNICIPIOS
# ============================================================
print('>> Creando geografia...')
antioquia = Departamento.objects.create(
    codigo_dane='05', nombre_departamento='Antioquia', usuario_creacion=USUARIO,
)
cundinamarca = Departamento.objects.create(
    codigo_dane='25', nombre_departamento='Cundinamarca', usuario_creacion=USUARIO,
)

medellin = Municipio.objects.create(
    codigo_dane='05001', nombre_municipio='Medellin',
    id_departamento=antioquia, usuario_creacion=USUARIO,
)
envigado = Municipio.objects.create(
    codigo_dane='05266', nombre_municipio='Envigado',
    id_departamento=antioquia, usuario_creacion=USUARIO,
)
bogota = Municipio.objects.create(
    codigo_dane='25001', nombre_municipio='Bogota DC',
    id_departamento=cundinamarca, usuario_creacion=USUARIO,
)

# ============================================================
# SEDES + CONSULTORIOS
# ============================================================
print('>> Creando sedes y consultorios...')
sede_norte = Sede.objects.create(
    codigo_sede='SED-N01', nombre_sede='Sede Norte',
    direccion='Calle 50 # 20-30', telefono='6044440001',
    email='norte@citas.local', id_municipio=medellin,
    usuario_creacion=USUARIO,
)
sede_sur = Sede.objects.create(
    codigo_sede='SED-S01', nombre_sede='Sede Sur',
    direccion='Carrera 43A # 5-15', telefono='6044440002',
    email='sur@citas.local', id_municipio=envigado,
    usuario_creacion=USUARIO,
)

c1 = Consultorio.objects.create(
    codigo_consultorio='C101', nombre_consultorio='Consultorio 101',
    numero_piso=1, capacidad=1, id_sede=sede_norte, usuario_creacion=USUARIO,
)
c2 = Consultorio.objects.create(
    codigo_consultorio='C102', nombre_consultorio='Consultorio 102',
    numero_piso=1, capacidad=1, id_sede=sede_norte, usuario_creacion=USUARIO,
)
c3 = Consultorio.objects.create(
    codigo_consultorio='C201', nombre_consultorio='Consultorio 201',
    numero_piso=2, capacidad=2, id_sede=sede_sur, usuario_creacion=USUARIO,
)

# ============================================================
# ESPECIALIDADES
# ============================================================
print('>> Creando especialidades...')
esp_general = Especialidad.objects.create(codigo_especialidad='MG', nombre_especialidad='Medicina General')
esp_pediatria = Especialidad.objects.create(codigo_especialidad='PED', nombre_especialidad='Pediatria')
esp_cardio = Especialidad.objects.create(codigo_especialidad='CAR', nombre_especialidad='Cardiologia')
esp_derma = Especialidad.objects.create(codigo_especialidad='DER', nombre_especialidad='Dermatologia')

# ============================================================
# MEDICOS (Persona + Medico)
# ============================================================
print('>> Creando medicos...')
def crear_medico(doc, nombres, apellidos, especialidad, registro, tarifa, muni):
    pn, sn = (nombres.split() + [None])[:2]
    pa, sa = (apellidos.split() + [None])[:2]
    p = Persona.objects.create(
        tipo_documento='CC', numero_documento=doc,
        primer_nombre=pn, segundo_nombre=sn,
        primer_apellido=pa, segundo_apellido=sa,
        fecha_nacimiento=date(1980, 5, 15), sexo='M',
        email=f'{doc}@citas.local', telefono='3001112233',
        id_municipio=muni, usuario_creacion=USUARIO,
    )
    return Medico.objects.create(
        id_persona=p, id_especialidad=especialidad,
        numero_registro=registro, tarifa_consulta=tarifa,
    )

med1 = crear_medico('111111', 'Carlos Andres', 'Ramirez Diaz', esp_general, 'RM-0001', 80000, medellin)
med2 = crear_medico('222222', 'Laura Sofia', 'Perez Mora', esp_pediatria, 'RM-0002', 95000, medellin)
med3 = crear_medico('333333', 'Juan Pablo', 'Vargas Ruiz', esp_cardio, 'RM-0003', 150000, envigado)

# ============================================================
# PACIENTES (Persona + Paciente)
# ============================================================
print('>> Creando pacientes...')
def crear_paciente(doc, nombres, apellidos, historia, eps, tipo_afil, muni):
    pn, sn = (nombres.split() + [None])[:2]
    pa, sa = (apellidos.split() + [None])[:2]
    p = Persona.objects.create(
        tipo_documento='CC', numero_documento=doc,
        primer_nombre=pn, segundo_nombre=sn,
        primer_apellido=pa, segundo_apellido=sa,
        fecha_nacimiento=date(1995, 8, 10), sexo='F',
        email=f'{doc}@citas.local', telefono='3009998877',
        id_municipio=muni, usuario_creacion=USUARIO,
    )
    return Paciente.objects.create(
        id_persona=p, numero_historia=historia,
        tipo_afiliacion=tipo_afil, eps=eps,
    )

pac1 = crear_paciente('901001', 'Maria Fernanda', 'Lopez Garcia', 'HC-0001', 'Sura', 'CONTRIBUTIVO', medellin)
pac2 = crear_paciente('901002', 'Santiago', 'Mejia Osorio', 'HC-0002', 'Sanitas', 'CONTRIBUTIVO', medellin)
pac3 = crear_paciente('901003', 'Valentina', 'Castro Salazar', 'HC-0003', 'Nueva EPS', 'SUBSIDIADO', envigado)
pac4 = crear_paciente('901004', 'Diego', 'Ortega Villa', 'HC-0004', 'Coomeva', 'PARTICULAR', bogota)

# ============================================================
# CITAS (varios estados y fechas)
# ============================================================
print('>> Creando citas medicas...')
hoy = date.today()
citas_data = [
    (pac1, med1, c1, hoy + timedelta(days=1), '08:00', '08:30', 'PROGRAMADA', 'Control general'),
    (pac2, med2, c2, hoy + timedelta(days=2), '09:00', '09:30', 'CONFIRMADA', 'Revision pediatrica'),
    (pac3, med3, c3, hoy - timedelta(days=3), '10:00', '10:45', 'ATENDIDA', 'Dolor toracico'),
    (pac4, med1, c1, hoy - timedelta(days=7), '11:00', '11:30', 'CANCELADA', 'Chequeo'),
    (pac1, med3, c3, hoy - timedelta(days=14), '15:00', '15:30', 'NO_ASISTIO', 'Seguimiento'),
    (pac2, med1, c2, hoy + timedelta(days=5), '14:00', '14:30', 'PROGRAMADA', 'Consulta general'),
]
for i, (pac, med, cons, f, hi, hf, est, motivo) in enumerate(citas_data, start=1):
    CitaMedica.objects.create(
        numero_cita=f'CITA-{f.strftime("%Y%m%d")}-{i:04d}',
        id_paciente=pac, id_medico=med, id_consultorio=cons,
        fecha_cita=f, hora_inicio=hi, hora_fin=hf,
        estado=est, motivo_consulta=motivo,
        usuario_creacion=USUARIO,
    )

# ============================================================
# RESUMEN
# ============================================================
print()
print('=' * 60)
print('SEED COMPLETADO')
print('=' * 60)
print(f'  Usuarios auth    : {User.objects.count()}')
print(f'  Departamentos    : {Departamento.objects.count()}')
print(f'  Municipios       : {Municipio.objects.count()}')
print(f'  Sedes            : {Sede.objects.count()}')
print(f'  Consultorios     : {Consultorio.objects.count()}')
print(f'  Especialidades   : {Especialidad.objects.count()}')
print(f'  Personas         : {Persona.objects.count()}')
print(f'  Medicos          : {Medico.objects.count()}')
print(f'  Pacientes        : {Paciente.objects.count()}')
print(f'  Citas Medicas    : {CitaMedica.objects.count()}')
print('=' * 60)
