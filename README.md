# Sistema de Gestión de Citas Médicas

Aplicación web completa para la gestión de citas médicas en instituciones de salud. Desarrollada con **Django 4.2** (patrón MVT) y **Oracle XE 18c** como base de datos.

---

## 🚀 Estado del Proyecto

| Fase | Descripción | Estado |
|------|------------|--------|
| **Fase 1** | Corrección de bugs + 6 modelos nuevos | ✅ Completada |
| **Fase 2** | CRUD de Especialidades, Médicos y Pacientes | ✅ Completada |
| **Fase 3** | Módulo completo de Citas Médicas con máquina de estados | ✅ Completada |
| **Fase 4** | Mejoras UI/UX (dashboard, auditoría, toasts) | ⏳ Pendiente |

Ver `FASES_DESARROLLO.md` para documentación detallada de cada fase.

---

## 📋 Requisitos

- Python 3.10+
- Oracle XE 18c instalado y en ejecución
- Oracle Instant Client (para cx_Oracle/oracledb)
- pip

---

## ⚡ Instalación Rápida

```bash
# 1. Clonar y entrar al proyecto
cd django_app

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos en gestion_citas/settings.py
#    (host, puerto, credenciales de Oracle)

# 5. Crear directorio de logs
mkdir logs

# 6. Crear superusuario Django
python manage.py createsuperuser

# 7. Ejecutar scripts SQL en Oracle (en orden 01-07)
#    Ver DOCUMENTACION_TECNICA.md para detalles

# 8. Iniciar servidor
python manage.py runserver
```

---

## 🔐 Credenciales de Acceso

| Rol | Usuario Django | Rol en Login | Permisos |
|-----|---------------|-------------|----------|
| **Administrativo** | `admin` (crear con `createsuperuser`) | Administrativo | CRUD completo en todo |
| **Médico** | Crear como superusuario o desde admin Django | Médico | Ver citas propias, cambiar estado |
| **Paciente** | Crear como superusuario o desde admin Django | Paciente | Solo ver sus propios datos |
| **Auxiliar Médico** | Crear como superusuario o desde admin Django | Auxiliar Médico | Crear citas, ver catálogos |

> El login requiere: **usuario + contraseña + rol**. Las credenciales son las de Django (`auth.User`).

---

## 🏗️ Arquitectura

```
┌─────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  TEMPLATES  │◄───│  VIEWS   │◄───│  MODELS  │◄───│  ORACLE  │
│   (HTML)    │    │ (Python) │    │ (Python) │    │  XE 18c  │
└─────────────┘    └──────────┘    └──────────┘    └──────────┘
```

- **Patrón:** Django MVT (Model-View-Template)
- **DB:** Oracle XE 18c con roles y privilegios por tabla
- **Seguridad:** Roles de BD (medico, paciente, administrativo, auxiliar_medico)
- **Auditoría:** Triggers de Oracle que registran INSERT/UPDATE/DELETE

---

## 📦 Módulos Implementados

### Maestros (CRUD completo)
- 🗺️ Departamentos y Municipios
- 🏢 Sedes y Consultorios
- 💊 Especialidades Médicas
- 👨‍️ Médicos (con datos de Persona)
- 🧑‍⚕️ Pacientes (con datos de Persona)

### Citas Médicas
- 📅 Crear, listar, editar y cancelar citas
- 🔄 Cambio de estado controlado (máquina de estados)
- 🔍 Filtros por fecha, estado y búsqueda textual
- 👁️ Vista de detalle con participantes y transiciones

---

## 📂 Estructura del Proyecto

```
gestion_citas/
├── sql/                          # Scripts Oracle (01-07)
├── csv/                          # Datos semilla
├── django_app/
│   ├── citas/                    # App principal
│   │   ├── models.py             # 10 modelos Django
│   │   ├── views.py              # 40+ vistas
│   │   ├── forms.py              # 10 formularios
│   │   ├── urls.py               # 36 rutas
│   │   └── templates/citas/      # 35+ templates HTML
│   ├── usuarios/                 # App de autenticación
│   └── gestion_citas/            # Configuración del proyecto
├── FASES_DESARROLLO.md           # Bitácora de desarrollo
└── DOCUMENTACION_TECNICA.md      # Documentación completa
```

---

## 📚 Documentación

| Archivo | Contenido |
|---------|-----------|
| `FASES_DESARROLLO.md` | Bitácora de cada fase: bugs, modelos, vistas, decisiones |
| `DOCUMENTACION_TECNICA.md` | Guía completa: arquitectura, SQL, roles, laboratorio |
| `QWEN.md` | Contexto para agentes de desarrollo |

---

## 🛠️ Comandos Útiles

```bash
python manage.py runserver              # Servidor de desarrollo
python manage.py createsuperuser        # Crear admin Django
python manage.py check                  # Verificar configuración
python manage.py shell                  # Shell interactivo
```

---

*Materia: Electiva I, II, III y IV — Sistema de Gestión de Citas Médicas*
