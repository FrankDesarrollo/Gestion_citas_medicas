# QWEN.md — Context for Future Interactions

## Project Overview

**Project Name:** Gestión de Citas Médicas (Medical Appointment Management System)  
**Type:** Full-stack web application (academic project)  
**Architecture:** Django MVT (Model-View-Template) pattern with Oracle XE 18c as the database backend  
**Purpose:** A medical appointment scheduling system designed for academic use (courses Electiva I–IV). It demonstrates role-based access control, database security (Oracle roles/privileges), audit trails, and the Django MVT pattern.

### Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Backend | Python / Django | 4.2 LTS |
| Database | Oracle XE | 18c |
| Oracle Driver | cx_Oracle / oracledb | 8.3 / 1.4.2 |
| Frontend | HTML / Bootstrap | 5.3 |
| Static Files | WhiteNoise | 6.6.0 |
| Forms | django-crispy-forms | 2.1 |

### Database Roles & Privileges

The system implements fine-grained role-based access control at the Oracle database level:

| Role | Django User | Privileges |
|------|------------|------------|
| `ROL_MEDICO` | `usr_medico` | SELECT on most tables; SELECT + UPDATE on citas |
| `ROL_PACIENTE` | `usr_paciente` | SELECT on own records only |
| `ROL_ADMINISTRATIVO` | `usr_administrativo` | Full CRUD on all tables |
| `ROL_AUXILIAR_MEDICO` | `usr_auxiliar` | SELECT + INSERT + UPDATE on select tables |

---

## Project Structure

```
gestion_citas/
├── sql/                          # Oracle SQL scripts (executed in order)
│   ├── 01_crear_tablespace_usuarios.sql
│   ├── 02_crear_tablas.sql
│   ├── 03_asignar_privilegios.sql
│   ├── 04_datos_iniciales.sql
│   └── 05_triggers_auditoria.sql
│
├── csv/                          # CSV data files for seeding tables
│   ├── departamentos.csv
│   ├── municipios.csv
│   ├── sedes.csv
│   └── consultorios.csv
│
└── django_app/                   # Django project root
    ├── manage.py
    ├── requirements.txt
    │
    ├── gestion_citas/            # Django project settings package
    │   ├── settings.py           # Main configuration (DB, apps, middleware, logging)
    │   └── urls.py               # Root URL configuration
    │
    ├── citas/                    # App: Core CRUDs (departments, municipalities, clinics, offices)
    │   ├── models.py             # Models mapping to Oracle tables
    │   ├── views.py              # CRUD view functions
    │   ├── forms.py              # Django forms with validation
    │   ├── urls.py               # Module-level routes
    │   ├── decorators.py         # Role-based access decorators
    │   ├── middleware.py         # Role verification middleware
    │   ├── context_processors.py # Global template variables
    │   └── templates/citas/      # HTML templates per module
    │
    └── usuarios/                 # App: Authentication
        ├── views.py              # Login/logout with role selection
        ├── urls.py               # /login/ and /logout/
        └── templates/usuarios/   # Login form template
```

---

## Data Model

The core entity hierarchy:

```
DEPARTAMENTOS → MUNICIPIOS → SEDES → CONSULTORIOS
```

Additional tables (defined in SQL scripts):
- `ESPECIALIDADES` (medical specialties)
- `PERSONAS` (people)
- `MEDICOS` (doctors)
- `PACIENTES` (patients)
- `CITAS_MEDICAS` (appointments)
- `AUDITORIA_ACCIONES` (audit log, populated by Oracle triggers)

All Django models use `managed = False`, meaning Django does **not** create or modify tables — they are managed exclusively via the SQL scripts in `sql/`.

---

## Building and Running

### Prerequisites

- Python 3.10+
- Oracle XE 18c installed and running
- Oracle Instant Client (for cx_Oracle/oracledb)
- pip

### Setup

```bash
# 1. Navigate to the Django app directory
cd django_app

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure database connection (edit gestion_citas/settings.py if needed)
#    Default: localhost:1521/XEPDB1, user=app_citas, password=Citas2024#

# 5. Create a logs directory
mkdir logs

# 6. Run the development server
python manage.py runserver

# 7. Create a Django superuser (for /admin/)
python manage.py createsuperuser
```

### Useful Django Commands

```bash
python manage.py runserver              # Start dev server
python manage.py runserver 0.0.0.0:8000 # Specific IP/port
python manage.py createsuperuser        # Create admin user
python manage.py check                  # Verify configuration
python manage.py shell                  # Interactive Django shell
python manage.py showmigrations         # Show migration status
```

### SQL Script Execution Order

Connect to Oracle and run scripts in this exact order:

```sql
-- As SYSDBA:
sqlplus sys/password@localhost:1521/XEPDB1 as sysdba
@01_crear_tablespace_usuarios.sql
@03_asignar_privilegios.sql

-- As APP_CITAS:
sqlplus app_citas/Citas2024#@localhost:1521/XEPDB1
@02_crear_tablas.sql
@04_datos_iniciales.sql

-- Triggers (any user with privileges):
@05_triggers_auditoria.sql
```

---

## Development Conventions

- **Managed=False**: All Django models set `managed = False`. The Oracle schema is the source of truth for table DDL. Django models only provide ORM query access.
- **Soft Deletes**: Tables use an `ACTIVO` flag (`'S'`/`'N'`) instead of physical deletion.
- **Audit Triggers**: Oracle PL/SQL triggers on key tables log changes to `AUDITORIA_ACCIONES`.
- **Role-Based Access**: Views use the `@rol_requerido([...])` decorator to restrict access by role. The `RolMiddleware` verifies the role is present in the session on every request.
- **Dynamic DB Connection**: `settings.py` defines `DB_CONNECTIONS_POR_ROL` — the application can switch to the Oracle user corresponding to the logged-in role.
- **Logging**: Application logs are written to `logs/gestion_citas.log` with both file and console handlers.

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `django_app/gestion_citas/settings.py` | Django configuration: DB, apps, middleware, roles, logging |
| `django_app/citas/models.py` | ORM models for Departamento, Municipio, Sede, Consultorio |
| `django_app/usuarios/views.py` | Login/logout with role validation |
| `django_app/citas/decorators.py` | `@rol_requerido` access control decorator |
| `django_app/citas/middleware.py` | `RolMiddleware` session role verification |
| `sql/01_crear_tablespace_usuarios.sql` | Creates tablespace, Oracle users, and roles |
| `sql/02_crear_tablas.sql` | DDL for all tables |
| `sql/03_asignar_privilegios.sql` | GRANT statements per role |
| `DOCUMENTACION_TECNICA.md` | Complete technical documentation (Spanish, 775+ lines) |

---

## Notes for Future Work

- The project is primarily documented in **Spanish**. The technical documentation (`DOCUMENTACION_TECNICA.md`) is the authoritative reference.
- When adding features, respect the existing MVT pattern and role-based access control.
- Database changes should be made via SQL scripts in `sql/`, not Django migrations (due to `managed = False`).
- The CSV files in `csv/` are intended for bulk data import into Oracle tables.
