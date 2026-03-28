# 📚 DOCUMENTACIÓN TÉCNICA COMPLETA
## Sistema de Gestión de Citas Médicas
### Oracle XE 18c + Django MVT (Python)
### Materia: Electiva I, II, III y IV

---

## 📋 TABLA DE CONTENIDOS

1. [Arquitectura del Sistema](#1-arquitectura-del-sistema)
2. [Estructura del Proyecto](#2-estructura-del-proyecto)
3. [Modelo de Datos](#3-modelo-de-datos)
4. [Instalación y Configuración](#4-instalación-y-configuración)
5. [Configuración Oracle XE 18c](#5-configuración-oracle-xe-18c)
6. [Gestión de Roles y Privilegios](#6-gestión-de-roles-y-privilegios)
7. [Arquitectura MVT en Django](#7-arquitectura-mvt-en-django)
8. [Flujo de Autenticación por Rol](#8-flujo-de-autenticación-por-rol)
9. [Guía de Laboratorio para Estudiantes DBA](#9-guía-de-laboratorio-para-estudiantes-dba)
10. [Administración desde pgAdmin](#10-administración-desde-pgadmin)
11. [Importación de Archivos CSV](#11-importación-de-archivos-csv)
12. [Comandos de Administración](#12-comandos-de-administración)

---

## 1. ARQUITECTURA DEL SISTEMA

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE CITAS MÉDICAS                     │
│                                                                 │
│   BROWSER ──► Django (MVT) ──► Oracle XE 18c (XEPDB1)          │
│                                                                 │
│   ┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│   │  TEMPLATES  │  │  VIEWS   │  │  MODELS  │  │  ORACLE  │   │
│   │   (HTML)    │◄─│ (Python) │◄─│ (Python) │◄─│  Tables  │   │
│   │  La "T"     │  │ La "V"   │  │  La "M"  │  │          │   │
│   └─────────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                                 │
│   ROLES DE BD:  medico │ paciente │ administrativo │ auxiliar   │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes Principales

| Componente      | Tecnología        | Versión  | Propósito                          |
|-----------------|-------------------|----------|------------------------------------|
| Base de Datos   | Oracle XE         | 18c      | Almacenamiento y seguridad de datos|
| Backend         | Python / Django   | 4.2 LTS  | Lógica de negocio y API            |
| Frontend        | HTML / Bootstrap  | 5.3      | Interfaz de usuario                |
| ORM             | Django ORM        | 4.2      | Mapeo objeto-relacional a Oracle   |
| Conector Oracle | cx_Oracle         | 8.3      | Driver de conexión Python→Oracle   |

---

## 2. ESTRUCTURA DEL PROYECTO

```
gestion_citas/
│
├── sql/                              ← Scripts SQL para Oracle XE 18c
│   ├── 01_crear_tablespace_usuarios.sql   → Tablespace, usuarios, roles
│   ├── 02_crear_tablas.sql               → DDL: Todas las tablas
│   ├── 03_asignar_privilegios.sql        → GRANT por rol y tabla
│   ├── 04_datos_iniciales.sql            → INSERT de datos semilla
│   └── 05_triggers_auditoria.sql         → Triggers + consultas DBA
│
├── csv/                              ← Archivos para poblar tablas
│   ├── departamentos.csv
│   ├── municipios.csv
│   ├── sedes.csv
│   └── consultorios.csv
│
└── django_app/                       ← Proyecto Django
    ├── requirements.txt              → Dependencias Python
    ├── manage.py                     → Utilidad de Django
    │
    ├── gestion_citas/                → Paquete principal del proyecto
    │   ├── settings.py               → Configuración (BD, apps, etc.)
    │   ├── urls.py                   → URLs raíz del proyecto
    │   └── templates/
    │       └── base.html             → Template base con sidebar/navbar
    │
    ├── citas/                        → App: CRUDs de maestros
    │   ├── models.py                 → Modelos: Departamento, Municipio, Sede, Consultorio
    │   ├── views.py                  → Vistas CRUD completas
    │   ├── forms.py                  → Formularios con validación
    │   ├── urls.py                   → Rutas del módulo
    │   ├── decorators.py             → Control de acceso por rol
    │   ├── middleware.py             → Verificación de rol en sesión
    │   ├── context_processors.py    → Variables globales para templates
    │   └── templates/citas/
    │       ├── menu.html             → Dashboard principal
    │       ├── acceso_denegado.html  → Página 403
    │       ├── departamentos/        → Templates CRUD departamentos
    │       ├── municipios/           → Templates CRUD municipios
    │       ├── sedes/                → Templates CRUD sedes
    │       └── consultorios/         → Templates CRUD consultorios
    │
    └── usuarios/                     → App: Autenticación
        ├── views.py                  → Login con selección de ROL
        ├── urls.py                   → /login/ y /logout/
        └── templates/usuarios/
            └── login.html            → Formulario de login con rol
```

---

## 3. MODELO DE DATOS

### Diagrama Entidad-Relación (Tablas Principales)

```
DEPARTAMENTOS              MUNICIPIOS
┌──────────────────┐      ┌──────────────────────┐
│ PK id_departamento│◄──── │ PK id_municipio       │
│    codigo_dane   │      │    codigo_dane        │
│    nombre_dep... │      │    nombre_municipio   │
│    activo        │      │ FK id_departamento    │
│    fecha_creacion│      │    activo             │
└──────────────────┘      └───────────┬──────────┘
                                      │
                              ┌───────┘
                              ▼
                          SEDES
                    ┌──────────────────────┐
                    │ PK id_sede           │
                    │    codigo_sede       │
                    │    nombre_sede       │
                    │    direccion         │
                    │    telefono          │
                    │    email             │
                    │ FK id_municipio      │
                    │    activo            │
                    └──────────┬───────────┘
                               │
                       ┌───────┘
                       ▼
                   CONSULTORIOS
             ┌──────────────────────┐
             │ PK id_consultorio    │
             │    codigo_consultor  │
             │    nombre_consultor  │
             │    numero_piso       │
             │    capacidad         │
             │ FK id_sede           │
             │    activo            │
             └──────────────────────┘
```

### Tablas de Auditoría y Seguridad

```
AUDITORIA_ACCIONES
┌────────────────────────────┐
│ PK id_auditoria            │
│    tabla_afectada          │
│    accion (INSERT/UPDATE..)│
│    id_registro             │
│    usuario_bd              │
│    datos_anteriores        │
│    datos_nuevos            │
│    fecha_accion            │
└────────────────────────────┘
```

---

## 4. INSTALACIÓN Y CONFIGURACIÓN

### Requisitos Previos

```bash
# Software necesario:
- Python 3.10 o superior
- Oracle XE 18c instalado y en ejecución
- Oracle Instant Client (para cx_Oracle)
- pip (gestor de paquetes Python)
- Git (opcional)
```

### Paso 1: Clonar o descomprimir el proyecto

```bash
# Crear directorio de trabajo
mkdir ~/citas_medicas
cd ~/citas_medicas

# Descomprimir el archivo del proyecto
unzip gestion_citas.zip
cd django_app
```

### Paso 2: Crear entorno virtual Python

```bash
# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno

Editar `gestion_citas/settings.py` y ajustar:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:1521/XEPDB1',  # ← Ajustar si Oracle está en otro host/puerto
        'USER': 'app_citas',
        'PASSWORD': 'Citas2024#',         # ← Cambiar según su instalación
    }
}
```

### Paso 5: Crear directorio de logs

```bash
mkdir logs
```

### Paso 6: Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

### Paso 7: Crear superusuario Django (para el admin)

```bash
python manage.py createsuperuser
```

Luego en el admin (`/admin/`) crear los usuarios del sistema:
- `admin_citas` → para rol `administrativo`
- `dr_garcia` → para rol `medico`
- `pac_lopez` → para rol `paciente`
- `aux_torres` → para rol `auxiliar_medico`

---

## 5. CONFIGURACIÓN ORACLE XE 18c

### Orden de Ejecución de Scripts SQL

```
PASO 1: Conectar como SYSDBA a la PDB XEPDB1
        sqlplus sys/password@localhost:1521/XEPDB1 as sysdba

PASO 2: Ejecutar 01_crear_tablespace_usuarios.sql
        → Crea tablespace, usuarios y roles

PASO 3: Conectar como APP_CITAS
        sqlplus app_citas/Citas2024#@localhost:1521/XEPDB1

PASO 4: Ejecutar 02_crear_tablas.sql
        → Crea todas las tablas del sistema

PASO 5: Conectar como SYSDBA nuevamente
        → Ejecutar 03_asignar_privilegios.sql
        → Crea sinónimos públicos y otorga permisos

PASO 6: Conectar como APP_CITAS
        → Ejecutar 04_datos_iniciales.sql
        → Inserta datos de prueba

PASO 7: Ejecutar 05_triggers_auditoria.sql
        → Crea triggers de auditoría
```

### Verificar Conexión a Oracle desde Python

```python
import cx_Oracle

# Probar conexión básica
conn = cx_Oracle.connect(
    user="app_citas",
    password="Citas2024#",
    dsn="localhost:1521/XEPDB1"
)
print("Conexión exitosa:", conn.version)
conn.close()
```

---

## 6. GESTIÓN DE ROLES Y PRIVILEGIOS

### Matriz Completa de Privilegios

| Tabla Oracle        | ROL_MEDICO | ROL_PACIENTE | ROL_ADMINISTRATIVO | ROL_AUXILIAR_MEDICO |
|---------------------|:----------:|:------------:|:------------------:|:-------------------:|
| DEPARTAMENTOS       | SELECT     | SELECT       | ALL (CRUD)         | SELECT              |
| MUNICIPIOS          | SELECT     | SELECT       | ALL (CRUD)         | SELECT              |
| SEDES               | SELECT     | SELECT       | ALL (CRUD)         | SELECT              |
| CONSULTORIOS        | SELECT     | SELECT       | ALL (CRUD)         | SELECT              |
| ESPECIALIDADES      | SELECT     | –            | ALL (CRUD)         | SELECT              |
| PERSONAS            | SELECT     | SELECT       | ALL (CRUD)         | SELECT, INSERT      |
| MEDICOS             | SELECT     | SELECT       | ALL (CRUD)         | SELECT              |
| PACIENTES           | SELECT     | SELECT*      | ALL (CRUD)         | SELECT, INSERT      |
| CITAS_MEDICAS       | SEL, UPD   | SELECT*      | ALL (CRUD)         | SEL, INS, UPD       |
| AUDITORIA_ACCIONES  | –          | –            | SELECT             | –                   |

*Solo puede ver sus propios registros (filtrado en la aplicación)

### Cómo Consultar Privilegios desde SQL Developer / pgAdmin

```sql
-- 1. Ver todos los privilegios sobre tablas del esquema
SELECT grantee, table_name, privilege
FROM all_tab_privs
WHERE table_schema = 'APP_CITAS'
ORDER BY grantee, table_name;

-- 2. Ver qué puede hacer un rol específico
SELECT table_name, privilege
FROM all_tab_privs
WHERE grantee = 'ROL_ADMINISTRATIVO'
ORDER BY table_name, privilege;

-- 3. Ver herencia de privilegios usuario→rol→tabla
SELECT rp.grantee AS usuario,
       rp.granted_role,
       tp.table_name,
       tp.privilege
FROM dba_role_privs rp
JOIN dba_tab_privs tp ON rp.granted_role = tp.grantee
WHERE rp.grantee = 'USR_MEDICO'
ORDER BY tp.table_name;
```

---

## 7. ARQUITECTURA MVT EN DJANGO

### ¿Qué es MVT?

Django usa el patrón **MVT (Model-View-Template)**, análogo al MVC tradicional:

```
MVC Clásico    ↔    Django MVT
───────────────────────────────
Model          ↔    Model    (models.py)
Controller     ↔    View     (views.py)
View           ↔    Template (archivos .html)
```

### Flujo de una Petición HTTP

```
1. Usuario hace clic en "Lista de Departamentos"
                    │
                    ▼
2. Browser envía: GET /departamentos/
                    │
                    ▼
3. Django urls.py busca la URL y llama a:
   departamentos_lista(request)  [views.py]
                    │
                    ▼
4. La Vista consulta el Modelo:
   Departamento.objects.all()  [models.py]
                    │
                    ▼
5. El Modelo ejecuta en Oracle:
   SELECT * FROM DEPARTAMENTOS  [Oracle XE 18c]
                    │
                    ▼
6. La Vista pasa los datos al Template:
   render(request, 'departamentos/lista.html', {'departamentos': qs})
                    │
                    ▼
7. El Template genera HTML con los datos
                    │
                    ▼
8. Browser muestra la tabla de departamentos
```

### El Modelo en Django ≡ Tabla en Oracle

```python
# models.py                          ↔    SQL en Oracle
class Departamento(models.Model):
    codigo_dane = models.CharField()  ↔  CODIGO_DANE VARCHAR2(2)
    nombre_departamento = ...         ↔  NOMBRE_DEPARTAMENTO VARCHAR2(100)

    class Meta:
        db_table = 'DEPARTAMENTOS'   # ← Nombre exacto de la tabla Oracle
        managed = False              # ← Django NO crea/modifica la tabla
```

### Operaciones ORM ↔ SQL Oracle

```python
# Django ORM                         ↔    SQL Oracle equivalente

# Consultar todos
Departamento.objects.all()           → SELECT * FROM DEPARTAMENTOS

# Filtrar activos
Departamento.objects.filter(activo='S')
                                     → SELECT * FROM DEPARTAMENTOS
                                       WHERE ACTIVO = 'S'

# Insertar
dep = Departamento(codigo_dane='99', ...)
dep.save()                           → INSERT INTO DEPARTAMENTOS (...) VALUES (...)

# Actualizar
dep.nombre_departamento = 'NUEVO'
dep.save()                           → UPDATE DEPARTAMENTOS SET ... WHERE ID = ...

# Eliminar físico (no usamos esto, preferimos soft delete)
dep.delete()                         → DELETE FROM DEPARTAMENTOS WHERE ID = ...

# JOIN con ForeignKey
Municipio.objects.select_related('id_departamento').all()
                                     → SELECT m.*, d.* FROM MUNICIPIOS m
                                       JOIN DEPARTAMENTOS d ON m.ID_DEPARTAMENTO = d.ID_DEPARTAMENTO
```

---

## 8. FLUJO DE AUTENTICACIÓN POR ROL

### Diagrama del Proceso

```
┌─────────────────────────────────────────────────────────┐
│                   PANTALLA DE LOGIN                      │
│                                                         │
│  Usuario: [admin_citas    ]                             │
│  Password: [••••••••••••  ]                             │
│  Rol:      [Administrativo ▼]  ← CAMPO OBLIGATORIO      │
│                                                         │
│              [  INGRESAR  ]                             │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │ Django auth.authenticate()   │
         │ Verifica user/password en BD │
         └──────────────────────────────┘
                        │
              ┌─────────┴──────────┐
              │ ¿Autenticado?      │
              └─────────┬──────────┘
                 NO ◄───┤───► SI
                        │
                        ▼
         ┌──────────────────────────────┐
         │ Guardar en session:          │
         │   rol_usuario = 'administrativo'│
         │   nombre_rol = 'Administrativo' │
         └──────────────────────────────┘
                        │
                        ▼
                  /menu/ (Dashboard)
```

### Verificación de Rol en Cada Vista

```python
# decorators.py
@rol_requerido(['administrativo'])
def departamentos_crear(request):
    # Si el rol NO es 'administrativo' → redirige a /acceso-denegado/
    # Si el rol SÍ es 'administrativo' → ejecuta la vista
    ...
```

---

## 9. GUÍA DE LABORATORIO PARA ESTUDIANTES DBA

### LABORATORIO 1: Explorar la Estructura de la BD

```sql
-- Conectarse como SYSDBA
-- Listar todos los usuarios del sistema
SELECT username, account_status, created
FROM dba_users
WHERE username IN ('APP_CITAS','USR_MEDICO','USR_PACIENTE',
                   'USR_ADMINISTRATIVO','USR_AUXILIAR')
ORDER BY username;

-- Ver los roles existentes
SELECT role FROM dba_roles
WHERE role LIKE 'ROL_%'
ORDER BY role;
```

### LABORATORIO 2: Verificar Matriz de Privilegios

```sql
-- Como SYSDBA: ver qué puede hacer cada rol
SELECT grantee, table_name, privilege
FROM dba_tab_privs
WHERE owner = 'APP_CITAS'
  AND grantee LIKE 'ROL_%'
ORDER BY grantee, table_name, privilege;

-- Pregunta de reflexión:
-- ¿Por qué ROL_PACIENTE solo tiene SELECT?
-- ¿Qué pasaría si intentamos hacer un INSERT con usr_paciente?
```

### LABORATORIO 3: Probar Restricciones de Seguridad

```sql
-- Conectarse como usr_paciente (rol paciente)
CONNECT usr_paciente/Pac2024#@localhost:1521/XEPDB1

-- Esto DEBE funcionar (tiene SELECT):
SELECT * FROM departamentos;

-- Esto DEBE FALLAR con ORA-01031 (no tiene INSERT):
INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('99', 'TEST');
-- Error esperado: ORA-01031: insufficient privileges

-- Esto TAMBIÉN DEBE FALLAR (no tiene DELETE):
DELETE FROM departamentos WHERE codigo_dane = '05';
```

### LABORATORIO 4: Otorgar un Nuevo Privilegio

```sql
-- Como SYSDBA: otorgar INSERT en municipios a rol_auxiliar_medico
GRANT INSERT ON app_citas.municipios TO rol_auxiliar_medico;

-- Verificar que se otorgó
SELECT table_name, privilege
FROM dba_tab_privs
WHERE grantee = 'ROL_AUXILIAR_MEDICO'
  AND table_name = 'MUNICIPIOS';

-- Probar como usr_auxiliar que ahora puede insertar
CONNECT usr_auxiliar/Aux2024#@localhost:1521/XEPDB1
INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('99001', 'MUNICIPIO TEST', 1);
COMMIT;

-- Revocar el privilegio
CONNECT sys/password@localhost:1521/XEPDB1 as sysdba
REVOKE INSERT ON app_citas.municipios FROM rol_auxiliar_medico;
```

### LABORATORIO 5: Revisar la Auditoría

```sql
-- Como administrativo: ver los últimos cambios
CONNECT usr_administrativo/Adm2024#@localhost:1521/XEPDB1

SELECT tabla_afectada, accion, usuario_bd,
       TO_CHAR(fecha_accion, 'DD/MM/YYYY HH24:MI:SS') AS fecha,
       datos_anteriores, datos_nuevos
FROM auditoria_acciones
ORDER BY fecha_accion DESC
FETCH FIRST 20 ROWS ONLY;

-- Estadísticas de actividad por usuario
SELECT usuario_bd, accion, COUNT(*) total
FROM auditoria_acciones
GROUP BY usuario_bd, accion
ORDER BY usuario_bd, accion;
```

### LABORATORIO 6: Bloquear y Desbloquear Usuarios

```sql
-- Como SYSDBA: bloquear el usuario médico
ALTER USER usr_medico ACCOUNT LOCK;

-- Verificar estado
SELECT username, account_status
FROM dba_users WHERE username = 'USR_MEDICO';

-- Desbloquear
ALTER USER usr_medico ACCOUNT UNLOCK;

-- Cambiar contraseña de un usuario
ALTER USER usr_medico IDENTIFIED BY NuevaClave2025#;
```

---

## 10. ADMINISTRACIÓN DESDE PGADMIN

> **Nota:** pgAdmin es una herramienta de administración para PostgreSQL.
> Para Oracle XE 18c, se recomienda usar **Oracle SQL Developer** o **DBeaver**.
> Sin embargo, si el docente usa "pgAdmin" como término genérico, se puede usar
> **DBeaver** (gratuito) que conecta a Oracle igual que pgAdmin a PostgreSQL.

### Configurar DBeaver para Oracle XE 18c

1. Descargar DBeaver Community Edition: https://dbeaver.io/
2. Nueva conexión → Oracle
3. Configurar:
   - Host: `localhost`
   - Puerto: `1521`
   - Database (SID/Service): `XEPDB1`
   - Usuario: `sys` (o el usuario deseado)
   - Contraseña: su contraseña
   - Rol: `SYSDBA`

### Qué Pueden Hacer los Estudiantes-DBA desde la Herramienta

| Tarea                           | SQL a Ejecutar                                     |
|---------------------------------|----------------------------------------------------|
| Ver tablas del esquema          | `SELECT * FROM all_tables WHERE owner='APP_CITAS'` |
| Consultar datos de una tabla    | `SELECT * FROM app_citas.departamentos`            |
| Ver privilegios de un rol       | Consulta en `dba_tab_privs`                        |
| Otorgar permiso                 | `GRANT SELECT ON tabla TO rol_xxx`                 |
| Revocar permiso                 | `REVOKE SELECT ON tabla FROM rol_xxx`              |
| Bloquear usuario                | `ALTER USER usr_xxx ACCOUNT LOCK`                  |
| Ver sesiones activas            | `SELECT * FROM v$session`                          |
| Ver auditoría                   | `SELECT * FROM app_citas.auditoria_acciones`       |
| Ver triggers                    | `SELECT * FROM dba_triggers WHERE owner='APP_CITAS'`|

---

## 11. IMPORTACIÓN DE ARCHIVOS CSV

### Opción 1: SQL*Loader (Oracle nativo)

```bash
# Archivo de control para departamentos
# Crear: departamentos.ctl

OPTIONS (SKIP=1)
LOAD DATA
INFILE 'departamentos.csv'
INTO TABLE app_citas.departamentos
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
TRAILING NULLCOLS
(
  codigo_dane,
  nombre_departamento,
  activo
)

# Ejecutar SQL*Loader
sqlldr userid=app_citas/Citas2024#@XEPDB1 control=departamentos.ctl log=departamentos.log
```

### Opción 2: Script Python para importar CSV

```python
import csv
import cx_Oracle

conn = cx_Oracle.connect('app_citas/Citas2024#@localhost:1521/XEPDB1')
cursor = conn.cursor()

with open('departamentos.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        cursor.execute("""
            INSERT INTO departamentos (codigo_dane, nombre_departamento, activo)
            VALUES (:1, :2, :3)
        """, (row['codigo_dane'], row['nombre_departamento'], row['activo']))

conn.commit()
cursor.close()
conn.close()
print("Importación completada")
```

### Opción 3: Desde Oracle SQL Developer

1. Abrir SQL Developer
2. Conectar con usuario `app_citas`
3. Clic derecho sobre la tabla → `Import Data`
4. Seleccionar el archivo CSV
5. Mapear columnas
6. Ejecutar

---

## 12. COMANDOS DE ADMINISTRACIÓN

### Comandos Django (desde el directorio django_app/)

```bash
# Iniciar servidor de desarrollo
python manage.py runserver

# Iniciar en una IP/Puerto específico
python manage.py runserver 0.0.0.0:8000

# Crear superusuario para el admin de Django
python manage.py createsuperuser

# Ver las migraciones (no aplicamos porque managed=False)
python manage.py showmigrations

# Verificar configuración
python manage.py check

# Shell interactivo de Django
python manage.py shell

# En el shell: probar la conexión a Oracle
from citas.models import Departamento
print(Departamento.objects.count())
```

### Comandos SQL útiles para el DBA

```sql
-- Ver todos los objetos del esquema APP_CITAS
SELECT object_name, object_type, status
FROM dba_objects
WHERE owner = 'APP_CITAS'
ORDER BY object_type, object_name;

-- Verificar espacio del tablespace
SELECT tablespace_name,
       ROUND(SUM(bytes)/1024/1024, 2) AS mb_usados
FROM dba_segments
WHERE tablespace_name = 'TBS_CITAS_MEDICAS'
GROUP BY tablespace_name;

-- Ver conexiones activas
SELECT username, status, osuser, machine, program
FROM v$session
WHERE username IS NOT NULL
ORDER BY username;

-- Matar una sesión problemática
-- ALTER SYSTEM KILL SESSION 'SID,SERIAL#';

-- Recompilar un trigger inválido
ALTER TRIGGER app_citas.trg_auditoria_departamentos COMPILE;
```

---

## GLOSARIO DE TÉRMINOS

| Término         | Definición                                                              |
|-----------------|-------------------------------------------------------------------------|
| PDB             | Pluggable Database: base de datos contenida en Oracle 18c+              |
| XEPDB1          | Nombre de la PDB por defecto en Oracle XE 18c                           |
| Tablespace      | Unidad lógica de almacenamiento en Oracle                               |
| Rol             | Conjunto de privilegios agrupados con un nombre                         |
| Privilegio      | Permiso para realizar una acción (SELECT, INSERT, UPDATE, DELETE)       |
| Sinónimo        | Alias para referenciar un objeto sin el prefijo del esquema             |
| Trigger         | Código PL/SQL que se ejecuta automáticamente ante un evento             |
| Soft Delete     | Desactivar un registro cambiando ACTIVO='N' en vez de borrarlo          |
| ORM             | Object-Relational Mapping: abstracción de la BD en objetos Python        |
| MVT             | Model-View-Template: patrón arquitectónico de Django                    |
| Middleware      | Código que intercepta todas las peticiones HTTP en Django               |
| Decorator       | Función Python que modifica el comportamiento de otra función           |
| Session         | Datos temporales guardados en el servidor por usuario autenticado       |
| SYSDBA          | Rol de máximo privilegio en Oracle (equivalente a root en Linux)        |
| DBA             | Database Administrator: administrador de base de datos                  |

---

*Documento generado para uso académico - Materia Electiva I, II, III y IV*
*Sistema de Gestión de Citas Médicas con Oracle XE 18c + Django MVT*
