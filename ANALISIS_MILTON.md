# Análisis del proyecto vs. requisitos del campus
## Gestión de Citas Médicas — rama `Milton-Dev`

> Documento de planificación elaborado por Milton (rol acordado: commits + documentación visual).
> **Equipo:** Frank · Erick · Milton.
> **Repo base:** https://github.com/FrankDesarrollo/Gestion_citas_medicas
> **Rama de trabajo de Milton:** `Milton-Dev`
> **Fecha:** 2026-05-15

---

## 1. Una sola idea primero

**El proyecto cubre 4 de los 5 requisitos del campus.**
Falta UNA cosa: el **formulario de gestión de roles y permisos** (CRUD de permisos dinámicos por rol/usuario). El resto del enunciado (login con 2+ roles, menú, 2 CRUDs) ya está implementado y supera lo pedido.

**Por qué importa:** no toca arquitectura. Es una app nueva (`permisos`) más una refactorización menor del decorador `@rol_requerido` para que lea de BD en vez de listas hardcoded. Ningún CRUD existente se reescribe.

---

## 2. Contexto del proyecto (resumen del agente)

| Capa | Tecnología |
|------|-----------|
| Backend | Django 4.2 LTS (patrón MVT) |
| BD producción | Oracle XE 18c (roles a nivel de BD: `ROL_MEDICO`, `ROL_PACIENTE`, `ROL_ADMINISTRATIVO`, `ROL_AUXILIAR_MEDICO`) |
| BD desarrollo | SQLite (flag `USE_SQLITE=1`, sin tocar código) |
| Frontend | Bootstrap 5.3 + crispy-forms + toasts |
| Driver Oracle | `oracledb` (shim para `cx_Oracle`) |

**Arranque local (Windows):**
```powershell
cd django_app
py -m pip install -r requirements.txt
$env:USE_SQLITE = "1"
py manage.py migrate
py seed_dev.py
py manage.py runserver 127.0.0.1:8000
```
URL: http://127.0.0.1:8000/ → redirige a `/login/`.

---

## 3. Lo que el campus pide (literal)

1. Equipos máximo 3 estudiantes. ✔ (Frank, Erick, Milton).
2. Aplicativo en software de preferencia. ✔ (Django).
3. **Login con mínimo 2 roles** (Admin y otro).
4. **Menú funcional.**
5. **Dos CRUDs completamente funcionales.**
6. **Gestión de roles y permisos mediante un formulario** donde se controle qué puede **ver, crear, editar o eliminar** cada usuario dentro del aplicativo.

---

## 4. Lo que YA tiene el proyecto

### 4.1. Login con roles ✅ (supera el requisito: 4 roles)
- `django_app/usuarios/views.py:25-30` — roles: `administrativo`, `medico`, `paciente`, `auxiliar_medico`.
- Login con **usuario + contraseña + rol** (dropdown).
- Rol persiste en `request.session['rol_usuario']`.
- Middleware (`citas/middleware.py:27-60`) valida rol en cada petición.

**Credenciales demo (SQLite):**
| Rol | Usuario | Contraseña |
|-----|---------|-----------|
| superadmin Django | `admin` | `Admin2024#` |
| Administrativo | `administrativo` | `Adm2024#` |
| Médico | `medico` | `Med2024#` |
| Auxiliar | `auxiliar` | `Aux2024#` |
| Paciente | `paciente` | `Pac2024#` |

### 4.2. Menú funcional ✅
- Dashboard con KPIs reales: total citas, pacientes, médicos, especialidades.
- Agenda del día + próximas 5 citas.
- Breakdown citas por estado (5 estados).
- Sidebar con links activos por sección.
- Archivos: `citas/templates/citas/menu.html`, `gestion_citas/templates/base.html`.

### 4.3. CRUDs ✅ (supera el requisito: 9 CRUDs)
| # | Entidad | Vistas | URL base |
|---|---------|--------|----------|
| 1 | Departamentos | 5 (lista, crear, ver, editar, eliminar) | `/departamentos/` |
| 2 | Municipios | 5 | `/municipios/` |
| 3 | Sedes | 5 | `/sedes/` |
| 4 | Consultorios | 5 | `/consultorios/` |
| 5 | Especialidades | 5 | `/especialidades/` |
| 6 | Médicos | 5 (form doble Persona + Médico) | `/medicos/` |
| 7 | Pacientes | 5 (form doble Persona + Paciente) | `/pacientes/` |
| 8 | **Citas Médicas** | 6 (incluye `cambiar-estado` + máquina de estados) | `/citas/` |
| 9 | Auditoría | 1 read-only con filtros | `/auditoria/` |

### 4.4. Modelos (10) y migración inicial ✅
- `Departamento`, `Municipio`, `Sede`, `Consultorio`, `Especialidad`, `Persona`, `Medico`, `Paciente`, `CitaMedica`, `AuditoriaAccion`.
- Migración `0001_initial.py` ya creada.
- Soft delete (`activo = 'S'/'N'`) en toda la BD.
- Auditoría vía triggers Oracle (`AUDITORIA_ACCIONES`) — en SQLite queda vacía (esperado).

---

## 5. Lo que FALTA (gap real)

### 5.1. Formulario de gestión de roles y permisos ❌
**Único requisito del campus no cubierto.**

**Estado actual:**
- Permisos están **hardcoded** en `citas/decorators.py:48-79` (funciones `puede_crear`, `puede_editar`, `puede_eliminar`).
- Decorador `@rol_requerido(['administrativo'])` lleva una lista fija en cada vista.
- No hay tabla de permisos, ni vista de admin, ni uso de `auth.Group` / `auth.Permission`.

**Lo que pide el campus (interpretación):**
> Formulario donde el administrador, por **rol** o por **usuario**, marca checkboxes:
> - puede VER X módulo
> - puede CREAR en X módulo
> - puede EDITAR en X módulo
> - puede ELIMINAR en X módulo

### 5.2. (Opcional, no exigido) — útil pero no urgente
- Auditoría visible en SQLite (faltan triggers equivalentes; con Oracle ya funciona).
- Calendario visual de citas (FullCalendar).
- Tests automatizados.
- Exportación CSV/XLSX.

---

## 6. Cómo se va a incorporar (diseño técnico)

### 6.1. Nueva app Django: `permisos`
**Ubicación:** `django_app/permisos/`. No toca `citas/` ni `usuarios/`.

### 6.2. Modelo de datos (3 tablas nuevas)

```python
# permisos/models.py

class Modulo(models.Model):
    """Módulos protegibles del sistema: departamentos, citas, médicos..."""
    codigo = models.CharField(max_length=50, unique=True)   # 'citas', 'pacientes'
    nombre = models.CharField(max_length=100)               # 'Citas Médicas'
    activo = models.CharField(max_length=1, default='S')

class PermisoRol(models.Model):
    """Matriz rol × módulo con 4 flags CRUD."""
    rol = models.CharField(max_length=30)        # administrativo, medico, ...
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    puede_ver = models.BooleanField(default=False)
    puede_crear = models.BooleanField(default=False)
    puede_editar = models.BooleanField(default=False)
    puede_eliminar = models.BooleanField(default=False)

    class Meta:
        unique_together = ('rol', 'modulo')

class PermisoUsuario(models.Model):
    """Override por usuario individual (opcional, sobreescribe PermisoRol)."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE)
    puede_ver = models.BooleanField(null=True)       # null = hereda del rol
    puede_crear = models.BooleanField(null=True)
    puede_editar = models.BooleanField(null=True)
    puede_eliminar = models.BooleanField(null=True)
```

### 6.3. Refactor del decorador (mínimo, retrocompatible)
**Archivo:** `citas/decorators.py`.

Antes:
```python
def puede_crear(rol):
    return rol == 'administrativo'
```

Después:
```python
def puede_crear(rol, modulo='general', usuario=None):
    return _consultar_permiso(rol, modulo, 'crear', usuario)
```

`_consultar_permiso` consulta primero `PermisoUsuario` (override), luego `PermisoRol`. Si no hay registro → niega.

**Fallback:** en migración inicial poblar `PermisoRol` con los permisos hardcoded actuales → cero regresión.

### 6.4. UI del formulario de permisos
- `/permisos/` — matriz visual: filas = roles, columnas = módulos, celdas = 4 checkboxes (V/C/E/E).
- `/permisos/usuario/<id>/` — override por usuario individual.
- Solo visible para rol `administrativo`.
- Botón "Restablecer a defaults del rol" por usuario.

---

## 7. Fases de trabajo

### **Fase 0 — Coordinación (todos, 1 día)**
- Mergear `Milton-Dev` y revisar este documento entre los 3.
- Aprobar diseño de tablas de permisos.
- Definir owner por fase.

### **Fase 1 — Base de datos (1-2 días)**
**Owner sugerido: Erick** (o quien tenga más fluidez con Oracle/SQL).
- Crear app `permisos` (`python manage.py startapp permisos`).
- Definir 3 modelos (Modulo, PermisoRol, PermisoUsuario) en `permisos/models.py`.
- Migración `0001_initial` para SQLite.
- Script SQL equivalente para Oracle en `sql/06_permisos.sql` (DDL + GRANTs).
- Data fixture: poblar `Modulo` con las 9 entidades existentes + `PermisoRol` con permisos actuales hardcoded.

### **Fase 2 — Lógica (2-3 días)**
**Owner sugerido: Frank** (autor original del repo, conoce mejor las vistas).
- Refactorizar `citas/decorators.py`:
  - `_consultar_permiso(rol, modulo, accion, usuario)` consulta BD con caché por sesión.
  - `puede_ver/crear/editar/eliminar` reciben `modulo` como argumento.
- Adaptar las 27 vistas de `citas/views.py`: pasar `modulo='citas'`, `'pacientes'`, etc.
- Endpoints CRUD en `permisos/views.py`:
  - `permisos_matriz` (GET/POST, formulario principal)
  - `permisos_usuario_detalle` (override individual)
- URLs en `permisos/urls.py`, registrar en `gestion_citas/urls.py`.
- Tests unitarios mínimos del nuevo decorador.

### **Fase 3 — Interfaz visual (2 días)**
**Owner sugerido: Milton** (yo) — commits + documentación visual.
- Template `permisos/templates/permisos/matriz.html`:
  - Tabla rol × módulo con checkboxes en Bootstrap 5.
  - Guardado AJAX o submit clásico (decidir en review).
- Template `permisos/templates/permisos/usuario_detalle.html`.
- Link en sidebar (`base.html`) solo visible para `administrativo`.
- Toasts de confirmación (ya hay infra en `base.html`).
- README actualizado con sección "Gestión de permisos" + capturas.
- Diagrama ER actualizado en `DOCUMENTACION_TECNICA.md`.

### **Fase 4 — Validación + entrega (1 día)**
**Todos.**
- Probar las 4 acciones CRUD para cada rol contra el nuevo sistema.
- Smoke test con seed: `py seed_dev.py` debe seguir funcionando.
- Verificar regresión en CRUDs existentes (`/citas/`, `/pacientes/`, etc.).
- Merge a `main` con PR firmado por los 3.

---

## 8. Reparto del trabajo

| Fase | Owner | Apoyo | Días |
|------|-------|-------|------|
| 0 — Coordinación | Todos | — | 1 |
| 1 — BD (modelos + migración + SQL) | **Erick** | Frank | 1-2 |
| 2 — Lógica (decorador + CRUD permisos) | **Frank** | Erick | 2-3 |
| 3 — UI (templates + sidebar + docs) | **Milton** | Frank | 2 |
| 4 — Validación + merge | Todos | — | 1 |

**Total estimado:** 7-9 días con holgura.

> **Mi rol acordado (Milton):** commits + documentación visual. Owner de la Fase 3.
> Apoyo a Frank/Erick en revisiones de PR de Fases 1 y 2.

---

## 9. Reglas de colaboración

1. **Nadie hace push directo a `main`.** Cada uno trabaja en su rama (`Frank-Dev`, `Erick-Dev`, `Milton-Dev`).
2. **Avisar por el chat antes de tocar `decorators.py`, `views.py` o `base.html`** (archivos cuello de botella).
3. **Una fase = un PR.** Code review obligatorio entre los 3 antes de merge.
4. **No modificar la arquitectura existente** (MVT, `managed=False`, soft delete, fallback SQLite). Las extensiones se hacen como app nueva o función nueva, no como reescrituras.
5. **Mensaje de commit en español, formato Conventional Commits:** `feat(permisos): ...`, `fix(decorators): ...`, `docs: ...`.

---

## 10. Entregables al final

- [ ] App `permisos` funcional con 3 modelos.
- [ ] Formulario matriz rol × módulo operativo en `/permisos/`.
- [ ] Decorador `@rol_requerido` leyendo de BD (con caché).
- [ ] Migración SQLite + script SQL Oracle.
- [ ] Seed actualizado con permisos por defecto.
- [ ] README.md y DOCUMENTACION_TECNICA.md actualizados.
- [ ] PR fusionado a `main` con los 3 nombres en el historial de commits.

---

*Documento preparado para alineación de equipo. Cualquier cambio de scope se discute en el chat antes de codificar.*
