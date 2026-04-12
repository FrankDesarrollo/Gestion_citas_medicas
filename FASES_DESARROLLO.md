# Fases de Desarrollo — Sistema de Gestión de Citas Médicas

> Este documento se actualiza cada vez que se completa una fase.
> **Regla:** Antes de iniciar una nueva fase, leer este archivo para
> conocer el estado actual, decisiones de arquitectura y evitar errores.

---

## FASE 1: Corrección de Bugs + Modelos Faltantes ✅ COMPLETADA

### Resumen
Corrección de templates rotos y creación de los 6 modelos Django que no existían
(Oracle ya tenía las 10 tablas, pero Django solo modelaba 4).

---

### Bugs Corregidos

#### Bug 1: `departamentos/detalle.html` inexistente
- **Problema:** La vista `departamentos_detalle` renderizaba `citas/departamentos/detalle.html` pero el archivo no existía → **error 500**.
- **Solución:** Creado el template desde cero con:
  - Detalle completo del departamento (código DANE, nombre, estado, fechas).
  - Tabla de municipios asociados con enlace a detalle de cada uno.
  - Botón de editar (solo si `puede_editar`) y botón "volver a la lista".

#### Bug 2: `municipios/detalle.html` roto
- **Problema:** Usaba `{% for field in object.fields %}` — `object` nunca se pasa en el contexto. Renderizaba vacío.
- **Solución:** Reemplazado por campos explícitos del modelo (`municipio.codigo_dane`, `municipio.nombre_municipio`, etc.). Enlace al departamento padre.

#### Bug 3: `sedes/detalle.html` roto
- **Mismo problema.** Reemplazado por campos explícitos. Incluye tabla de consultorios asociados.

#### Bug 4: `consultorios/detalle.html` roto
- **Mismo problema.** Reemplazado por campos explícitos.

---

### Modelos Creados (6 nuevos)

Todos en `citas/models.py`. Patrón común:

- `managed = False` → Django NO crea/modifica tablas.
- `db_column` en mayúsculas → mapeo exacto a columnas Oracle.
- `save()` sobrescrito → actualiza `fecha_modificacion` automáticamente.
- Soft delete vía campo `activo = 'S'/'N'`.
- `ordering` definido en `Meta` para listas consistentes.

#### 1. `Especialidad` → tabla `ESPECIALIDADES`
- Campos: `id_especialidad`, `codigo_especialidad`, `nombre_especialidad`, `activo`, `fecha_creacion`.
- Sin dependencias. Es tabla maestra simple.
- `__str__`: `"COD - NOMBRE"`

#### 2. `Persona` → tabla `PERSONAS`
- Campos: `id_persona`, `tipo_documento`, `numero_documento`, `primer_nombre`, `segundo_nombre`, `primer_apellido`, `segundo_apellido`, `fecha_nacimiento`, `sexo`, `email`, `telefono`, `id_municipio` (FK → Municipio), `activo`, `fecha_creacion`, `fecha_modificacion`, `usuario_creacion`.
- FK a `Municipio` con `on_delete=SET_NULL` (puede quedar sin municipio).
- `unique_together`: `(tipo_documento, numero_documento)`.
- `__str__`: `"APELLIDOS, NOMBRES"`

#### 3. `Medico` → tabla `MEDICOS`
- Campos: `id_medico`, `id_persona` (OneToOne → Persona), `id_especialidad` (FK → Especialidad), `numero_registro`, `tarifa_consulta`, `activo`, `fecha_creacion`.
- OneToOne a `Persona` (una persona = un médico).
- FK a `Especialidad` con `PROTECT`.
- `numero_registro` es único.
- `__str__`: `"Dr(a). {Persona} - {Especialidad}"`
- `@property nombre_completo`: delega a `Persona.__str__()`.

#### 4. `Paciente` → tabla `PACIENTES`
- Campos: `id_paciente`, `id_persona` (OneToOne → Persona), `numero_historia`, `tipo_afiliacion`, `eps`, `activo`, `fecha_creacion`.
- OneToOne a `Persona`.
- `numero_historia` es único.
- `tipo_afiliacion` choices: CONTRIBUTIVO, SUBSIDIADO, VINCULADO, PARTICULAR.
- `__str__`: `"Persona (HC: numero_historia)"`
- `@property nombre_completo`: delega a `Persona.__str__()`.

#### 5. `CitaMedica` → tabla `CITAS_MEDICAS`
- Campos: `id_cita`, `numero_cita`, `id_paciente` (FK → Paciente), `id_medico` (FK → Medico), `id_consultorio` (FK → Consultorio), `fecha_cita`, `hora_inicio`, `hora_fin`, `estado`, `motivo_consulta`, `observaciones`, `activo`, `fecha_creacion`, `fecha_modificacion`, `usuario_creacion`.
- Estados: PROGRAMADA, CONFIRMADA, ATENDIDA, CANCELADA, NO_ASISTIO.
- Default: `PROGRAMADA`.
- `numero_cita` es único.
- Orden: `-fecha_cita, -hora_inicio` (más recientes primero).
- `__str__`: `"Cita #numero - Paciente con Medico el fecha a las hora_inicio"`

#### 6. `AuditoriaAccion` → tabla `AUDITORIA_ACCIONES`
- Campos: `id_auditoria`, `tabla_afectada`, `accion`, `id_registro`, `usuario_bd`, `rol_activo`, `datos_anteriores`, `datos_nuevos`, `fecha_accion`, `ip_cliente`.
- **Solo lectura** — se llena vía triggers de Oracle (no se crean/actualizan desde Django).
- Acciones: INSERT, UPDATE, DELETE, SELECT.
- Orden: `-fecha_accion` (más recientes primero).

---

### Diagrama de Relaciones Actualizado

```
Municipio ←── Persona ──→ Medico ──→ Especialidad
   │              │         │
   │              │         └──┐
   │              │            │
   │           Paciente        │
   │              │            │
   └── Sede ──→ Consultorio ←─┘
                    │
                    └── CitaMedica ←── Paciente
                          ↑
                       (también apunta a Medico)
```

---

### Archivos Modificados en Fase 1

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `citas/templates/citas/departamentos/detalle.html` | **CREADO** | No existía, causado 500 |
| `citas/templates/citas/municipios/detalle.html` | **REESCRITO** | Bug `object.fields` |
| `citas/templates/citas/sedes/detalle.html` | **REESCRITO** | Bug `object.fields` |
| `citas/templates/citas/consultorios/detalle.html` | **REESCRITO** | Bug `object.fields` |
| `citas/models.py` | **MODIFICADO** | +6 modelos nuevos (+~370 líneas) |

---

### Decisiones de Arquitectura (Fase 1)

1. **`managed = False`** en TODOS los modelos. Las tablas las gestionan exclusivamente los scripts SQL en `sql/`.
2. **Soft delete siempre**: `activo = 'N'` en vez de `DELETE` físico.
3. **`fecha_modificacion` auto-seteado** en `save()` para todos los modelos editables.
4. **`AuditoriaAccion` es read-only**: no tiene `save()` sobrescrito ni formularios de creación.
5. **Persona como tabla base**: `Medico` y `Paciente` usan OneToOne → `Persona` para reutilizar datos personales.
6. **CitaMedica como modelo central**: conecta Paciente + Medico + Consultorio + fecha/hora + estado.

---

### Estado Actual del Proyecto (post-Fase 1)

#### Modelos Django existentes: 10
| # | Modelo | Tabla Oracle | Vistas CRUD | Templates |
|---|--------|-------------|:-----------:|:---------:|
| 1 | Departamento | DEPARTAMENTOS | ✅ | ✅ |
| 2 | Municipio | MUNICIPIOS | ✅ | ✅ |
| 3 | Sede | SEDES | ✅ | ✅ |
| 4 | Consultorio | CONSULTORIOS | ✅ | ✅ |
| 5 | **Especialidad** | ESPECIALIDADES | ❌ | ❌ |
| 6 | **Persona** | PERSONAS | ❌ | ❌ |
| 7 | **Medico** | MEDICOS | ❌ | ❌ |
| 8 | **Paciente** | PACIENTES | ❌ | ❌ |
| 9 | **CitaMedica** | CITAS_MEDICAS | ❌ | ❌ |
| 10 | **AuditoriaAccion** | AUDITORIA_ACCIONES | ❌ (solo lectura) | ❌ |

#### Lo que falta por construir (Fases siguientes)
- **Fase 2:** CRUD completo de Especialidades, Médicos y Pacientes (vistas, URLs, forms, templates).
- **Fase 3:** Módulo de Citas Médicas completo (crear cita, listar, ver, cambiar estado, cancelar).
- **Fase 4:** Mejoras UI/UX (dashboard con datos reales, calendario de citas, crispy-forms, toasts, vista de auditoría).

---

## FASE 2: CRUD de Especialidades, Médicos y Pacientes ✅ COMPLETADA

### Resumen
Implementación completa del CRUD (lista, crear, detalle, editar, eliminar) para
Especialidades, Médicos y Pacientes, con formularios de doble modelo para
Médicos (Persona + Medico) y Pacientes (Persona + Paciente).

---

### Formularios Creados (5 nuevos)

Todos en `citas/forms.py`.

| Formulario | Modelo | Campos | Notas |
|-----------|--------|--------|-------|
| `EspecialidadForm` | Especialidad | codigo_especialidad, nombre_especialidad, activo | Form simple, igual patrón que Departamentos |
| `PersonaForm` | Persona | 14 campos personales | Form base reutilizable para Médico y Paciente |
| `MedicoForm` | Medico | id_especialidad, numero_registro, tarifa_consulta, activo | Se usa junto con PersonaForm |
| `PacienteForm` | Paciente | numero_historia, tipo_afiliacion, eps, activo | Se usa junto con PersonaForm |

**Patrón de formularios dobles (Médico/Paciente):**
- Se usan **dos formularios separados** con `prefix='persona'` y `prefix='medico'` (o `prefix='paciente'`).
- En la vista se validan ambos, se guarda Persona primero (para obtener el PK), luego se asigna `id_persona` al Medico/Paciente.
- Esto respeta la arquitectura de Oracle donde Persona es tabla base y Medico/Paciente son tablas hijas con OneToOne.

---

### Vistas Creadas (15 nuevas: 5 por entidad × 3 entidades)

Todas en `citas/views.py`.

#### Especialidades (5 vistas)
| Vista | URL | Rol requerido | Descripción |
|-------|-----|--------------|-------------|
| `especialidades_lista` | `/especialidades/` | Todos (lectura) | Lista con búsqueda y paginación |
| `especialidades_crear` | `/especialidades/crear/` | administrativo | Crear con usuario_creación automático |
| `especialidades_detalle` | `/especialidades/<pk>/` | Todos | Detalle + lista de médicos en esa especialidad |
| `especialidades_editar` | `/especialidades/<pk>/editar/` | administrativo | Editar especialidad |
| `especialidades_eliminar` | `/especialidades/<pk>/eliminar/` | administrativo | Soft delete, bloquea si tiene médicos activos |

#### Médicos (5 vistas)
| Vista | URL | Rol requerido | Descripción |
|-------|-----|--------------|-------------|
| `medicos_lista` | `/medicos/` | Todos (lectura) | Lista con búsqueda + filtro por especialidad |
| `medicos_crear` | `/medicos/crear/` | administrativo | Crea Persona + Medico en una transacción |
| `medicos_detalle` | `/medicos/<pk>/` | Todos | Detalle de datos personales + profesionales + últimas 10 citas |
| `medicos_editar` | `/medicos/<pk>/editar/` | administrativo | Edita Persona + Medico simultáneamente |
| `medicos_eliminar` | `/medicos/<pk>/eliminar/` | administrativo | Soft delete solo del médico (no de la persona) |

#### Pacientes (5 vistas)
| Vista | URL | Rol requerido | Descripción |
|-------|-----|--------------|-------------|
| `pacientes_lista` | `/pacientes/` | Todos (lectura) | Lista con búsqueda. **Paciente solo ve los suyos** |
| `pacientes_crear` | `/pacientes/crear/` | administrativo | Crea Persona + Paciente en una transacción |
| `pacientes_detalle` | `/pacientes/<pk>/` | Todos | Detalle personal + datos de afiliación + últimas 10 citas |
| `pacientes_editar` | `/pacientes/<pk>/editar/` | administrativo | Edita Persona + Paciente simultáneamente |
| `pacientes_eliminar` | `/pacientes/<pk>/eliminar/` | administrativo | Soft delete del paciente |

**Filtro por rol en pacientes_lista:** Si el rol es `paciente`, se filtra por el `numero_documento` del usuario logueado para que solo vea su propio registro.

---

### URLs Añadidas

En `citas/urls.py`:
- 5 rutas para `/especialidades/...`
- 5 rutas para `/medicos/...`
- 5 rutas para `/pacientes/...`

Total nuevas: **15 rutas**.

---

### Templates Creados (15 archivos)

| Entidad | lista.html | formulario.html | detalle.html | confirmar_eliminar.html |
|---------|-----------|-----------------|-------------|------------------------|
| Especialidades | ✅ | ✅ | ✅ | ✅ |
| Médicos | ✅ (con filtro especialidad) | ✅ (doble form: persona + médico) | ✅ (con citas recientes) | ✅ |
| Pacientes | ✅ | ✅ (doble form: persona + paciente) | ✅ (con citas recientes) | ✅ |

**Características especiales de los templates:**
- `medicos/lista.html`: incluye dropdown de filtro por especialidad.
- `medicos/formulario.html` y `pacientes/formulario.html`: dos secciones card separadas (datos personales + datos específicos).
- `medicos/detalle.html` y `pacientes/detalle.html`: muestran las últimas 10 citas asociadas (preparado para Fase 3).

---

### Sidebar Actualizado

En `base.html` se agregaron 3 nuevos links en la sección "Maestros":
- Especialidades (`bi-heart-pulse`)
- Médicos (`bi-person-badge`)
- Pacientes (`bi-people`)

Se eliminó el link placeholder de "Usuarios" del admin.

---

### Archivos Modificados en Fase 2

| Archivo | Acción | Líneas añadidas aprox. |
|---------|--------|----------------------|
| `citas/forms.py` | +5 forms | ~190 |
| `citas/views.py` | +15 vistas | ~360 |
| `citas/urls.py` | +15 rutas | ~15 |
| `citas/templates/citas/especialidades/` | 4 templates nuevos | ~230 |
| `citas/templates/citas/medicos/` | 4 templates nuevos | ~340 |
| `citas/templates/citas/pacientes/` | 4 templates nuevos | ~370 |
| `gestion_citas/templates/base.html` | Sidebar actualizado | ~12 |

---

### Decisiones de Arquitectura (Fase 2)

1. **Formularios dobles para Médicos/Pacientes**: Se usan `PersonaForm` + `MedicoForm` (o `PacienteForm`) con prefixes distintos. Se guarda primero la Persona para obtener el PK, luego se asigna como FK del Medico/Paciente.
2. **Filtro por rol en pacientes**: `pacientes_lista` filtra automáticamente al paciente logueado por su `numero_documento`.
3. **`select_related`** se usa en todas las queries que cruzan FK para evitar N+1 queries.
4. **Vista detalle con citas**: Las vistas `medicos_detalle` y `pacientes_detalle` ya muestran las últimas 10 citas (preparando el terreno para Fase 3).
5. **Soft delete solo en la tabla hija**: Al eliminar un médico, solo se desactiva `MEDICOS`, no `PERSONAS`. La persona sigue existiendo.

---

### Estado Actual del Proyecto (post-Fase 2)

#### Modelos Django: 10/10 con vistas y templates

| # | Modelo | Vistas CRUD | Templates | Notas |
|---|--------|:-----------:|:---------:|-------|
| 1 | Departamento | ✅ | ✅ | |
| 2 | Municipio | ✅ | ✅ | |
| 3 | Sede | ✅ | ✅ | |
| 4 | Consultorio | ✅ | ✅ | |
| 5 | Especialidad | ✅ | ✅ | Nuevo en Fase 2 |
| 6 | Persona | ✅ (vía Médico/Paciente) | ✅ (vía form doble) | |
| 7 | Medico | ✅ | ✅ | Nuevo en Fase 2 |
| 8 | Paciente | ✅ | ✅ | Nuevo en Fase 2 |
| 9 | CitaMedica | ❌ | ❌ | Pendiente Fase 3 |
| 10 | AuditoriaAccion | ❌ (solo lectura) | ❌ | Pendiente Fase 4 |

#### Lo que falta por construir
- **Fase 3:** Módulo de Citas Médicas completo (crear cita, listar, ver, cambiar estado, cancelar).
- **Fase 4:** Mejoras UI/UX (dashboard con datos reales, calendario de citas, crispy-forms, toasts, vista de auditoría).

---

## FASE 3: Módulo de Citas Médicas ✅ COMPLETADA

### Resumen
Implementación completa del módulo de Citas Médicas: crear cita, listar con
filtros por rol/estado/fecha, ver detalle, editar, cancelar (soft delete),
y **cambio de estado controlado** con máquina de estados.

---

### Formularios Creados (2 nuevos)

Todos en `citas/forms.py`.

| Formulario | Modelo | Campos | Notas |
|-----------|--------|--------|-------|
| `CitaMedicaForm` | CitaMedica | id_paciente, id_medico, id_consultorio, fecha_cita, hora_inicio, hora_fin, motivo_consulta, estado | Formulario completo para crear/editar |
| `CitaEstadoForm` | CitaMedica | estado, observaciones | Formulario mínimo solo para cambiar estado |

**Características de CitaMedicaForm:**
- `id_paciente` queryset: solo pacientes activos, ordenados por apellido.
- `id_medico` queryset: solo médicos activos, con `select_related` a persona y especialidad.
- `id_consultorio` queryset: solo consultorios activos, con `select_related` a sede.
- Validación de formato de hora (HH:MM mínimo 5 caracteres).
- En crear: el estado se fuerza a `PROGRAMADA` y el `numero_cita` se auto-genera.

---

### Máquina de Estados de Citas

Implementada en `views.py` como diccionario `ESTADOS_TRANSICION`:

```
PROGRAMADA  →  CONFIRMADA, CANCELADA
CONFIRMADA  →  ATENDIDA, CANCELADA, NO_ASISTIO
ATENDIDA    →  (terminal)
CANCELADA   →  (terminal)
NO_ASISTIO  →  (terminal)
```

- Solo los estados listados como destino son válidos desde el estado actual.
- La vista `citas_cambiar_estado` valida contra esta tabla antes de guardar.
- Si un estado es terminal (ATENDIDA, CANCELADA, NO_ASISTIO), no permite más cambios.

---

### Vistas Creadas (6 nuevas)

| Vista | URL | Rol requerido | Descripción |
|-------|-----|--------------|-------------|
| `citas_lista` | `/citas/` | Todos | Lista con filtros por **estado**, **fecha** y **texto**. **Paciente solo ve las suyas, médico solo las suyas.** |
| `citas_crear` | `/citas/crear/` | administrativo, auxiliar_medico | Crea cita con numero auto-generado (`CITA-YYYYMMDD-XXXX`), estado = PROGRAMADA |
| `citas_detalle` | `/citas/<pk>/` | Todos | Detalle completo: paciente, médico, consultorio, motivo, observaciones, transiciones posibles |
| `citas_editar` | `/citas/<pk>/editar/` | administrativo | Edita todos los campos de la cita |
| `citas_eliminar` | `/citas/<pk>/eliminar/` | administrativo | Soft delete: pone `activo='N'` y `estado='CANCELADA'` |
| `citas_cambiar_estado` | `/citas/<pk>/cambiar-estado/` | administrativo, medico | Cambia el estado validando la máquina de estados |

**Función auxiliar `_generar_numero_cita()`:**
- Formato: `CITA-YYYYMMDD-XXXX` (ej: `CITA-20250411-0003`).
- Cuenta las citas del día actual y asigna el siguiente correlativo.

**Filtros por rol en `citas_lista`:**
- `paciente`: filtra por su `numero_documento` → busca Persona → Paciente → citas.
- `medico`: filtra por su `numero_documento` → busca Persona → Medico → citas.
- `administrativo` / `auxiliar_medico`: ven todas las citas activas.

---

### URLs Añadidas (6 nuevas)

En `citas/urls.py`:
- `GET/POST /citas/` — lista con filtros
- `GET/POST /citas/crear/` — crear
- `GET /citas/<pk>/` — detalle
- `GET/POST /citas/<pk>/editar/` — editar
- `POST /citas/<pk>/eliminar/` — cancelar
- `GET/POST /citas/<pk>/cambiar-estado/` — cambiar estado

---

### Templates Creados (5 archivos)

| Template | Descripción |
|----------|-------------|
| `lista.html` | Tabla con filtros de estado (dropdown), fecha (date picker) y búsqueda. Badges de estado con colores diferenciados. Botones: ver, editar, cambiar estado, cancelar. |
| `formulario.html` | Formulario con 3 secciones visuales: participante (paciente, médico, consultorio), fecha/hora, motivo. Estado solo visible en modo edición. |
| `detalle.html` | Vista de 2 columnas: info de cita + participantes. Links a detalle de paciente, médico. Muestra motivo y observaciones. Sección de transiciones de estado disponibles. |
| `confirmar_eliminar.html` | Confirmación de cancelación con datos clave de la cita. |
| `cambiar_estado.html` | Muestra estado actual, transiciones permitidas como badges, y formulario con selector de nuevo estado + observaciones. |

---

### Sidebar Actualizado

En `base.html`, el link "Citas Médicas" dejó de ser placeholder:
- Ahora apunta a `{% url 'citas_lista' %}` con clase `active` cuando se está en la ruta.
- Se eliminó el badge "Pronto".

---

### Archivos Modificados en Fase 3

| Archivo | Acción | Líneas añadidas aprox. |
|---------|--------|----------------------|
| `citas/forms.py` | +2 forms | ~100 |
| `citas/views.py` | +6 vistas + helpers | ~230 |
| `citas/urls.py` | +6 rutas | ~8 |
| `citas/templates/citas/citas_medicas/lista.html` | **CREADO** | ~110 |
| `citas/templates/citas/citas_medicas/formulario.html` | **CREADO** | ~90 |
| `citas/templates/citas/citas_medicas/detalle.html` | **CREADO** | ~120 |
| `citas/templates/citas/citas_medicas/confirmar_eliminar.html` | **CREADO** | ~30 |
| `citas/templates/citas/citas_medicas/cambiar_estado.html` | **CREADO** | ~80 |
| `gestion_citas/templates/base.html` | Link activado | ~3 |

---

### Decisiones de Arquitectura (Fase 3)

1. **Máquina de estados**: `ESTADOS_TRANSICION` dict controla qué transiciones son válidas. No se permite saltar estados (ej: PROGRAMADA → ATENDIDA directamente).
2. **Auto-generación de numero_cita**: Formato `CITA-YYYYMMDD-XXXX` con correlativo diario. Se genera en la vista `citas_crear`, no en el form.
3. **Filtro por rol estricto**: paciente y médico solo ven sus propias citas, identificado por `numero_documento` del usuario Django → Persona → Paciente/Medico.
4. **Soft delete doble**: al cancelar una cita se pone `activo='N'` Y `estado='CANCELADA'` para que no aparezca en listas normales y quede clara su intención.
5. **`auxiliar_medico` puede crear citas** pero no editar ni eliminar (solo administrativo).
6. **`medico` puede cambiar estado** pero no crear ni editar citas (eso es del administrativo/auxiliar).

---

### Estado Actual del Proyecto (post-Fase 3)

#### Modelos Django: 10/10 — TODOS con vistas y templates

| # | Modelo | Vistas CRUD | Templates | Estado |
|---|--------|:-----------:|:---------:|--------|
| 1 | Departamento | ✅ | ✅ | Completo |
| 2 | Municipio | ✅ | ✅ | Completo |
| 3 | Sede | ✅ | ✅ | Completo |
| 4 | Consultorio | ✅ | ✅ | Completo |
| 5 | Especialidad | ✅ | ✅ | Completo |
| 6 | Persona | ✅ (vía Med/Pac) | ✅ (vía form doble) | Completo |
| 7 | Medico | ✅ | ✅ | Completo |
| 8 | Paciente | ✅ | ✅ | Completo |
| 9 | CitaMedica | ✅ (+ cambiar estado) | ✅ (+ cambiar estado) | **Completo** |
| 10 | AuditoriaAccion | ❌ (solo lectura) | ❌ | Pendiente Fase 4 |

#### Lo que falta por construir
- **Fase 4:** Mejoras UI/UX (dashboard con datos reales, vista de auditoría, crispy-forms, toasts de notificación).

---

## FASE 4: Mejoras UI/UX + Auditoría + Infra local ✅ COMPLETADA

### Resumen
Dashboard con datos reales, vista de auditoría (solo lectura) con filtros,
migración de alertas a toasts de Bootstrap 5, integración de
`django-crispy-forms` + `crispy-bootstrap5`, y habilitación de un entorno
de desarrollo sin Oracle mediante un fallback a SQLite.

Además se limpiaron los bugs de arranque heredados de fases previas
(cx_Oracle vs oracledb en Python 3.14, `threaded=True` removido,
`TEMPLATES.DIRS` incompleto, bloque `{% block contenido %}` duplicado en
`base.html`, formato `H:i` sobre un `DateField`).

---

### Credenciales de desarrollo

> **Solo para el entorno local con SQLite.** Estos usuarios viven en la BD
> SQLite `db_dev.sqlite3` y NO deben replicarse en Oracle producción.

| Rol | Usuario | Contraseña | Uso |
|-----|---------|-----------|-----|
| superadmin (Django) | `admin` | `Admin2024#` | Acceso a `/admin/` y CRUD total |
| Administrativo | `administrativo` | `Adm2024#` | CRUD completo módulo citas |
| Médico | `medico` | `Med2024#` | Lectura + cambio de estado |
| Auxiliar médico | `auxiliar` | `Aux2024#` | Lectura + crear citas |
| Paciente | `paciente` | `Pac2024#` | Solo sus datos |

El rol se asigna automáticamente en `login` según el `numero_documento`
de la persona asociada. El superusuario `admin` se loguea con rol
`administrativo` por defecto si no tiene persona vinculada.

#### Arranque del entorno (Windows)

```bash
# Dependencias
py -m pip install -r django_app/requirements.txt

# Modo SQLite (no requiere Oracle instalado)
cd django_app
set USE_SQLITE=1
py manage.py migrate
py seed_dev.py          # carga datos demo idempotentes
py manage.py runserver 127.0.0.1:8000
```

Luego abrir http://127.0.0.1:8000/ → redirige a `/login/`.

---

### Dashboard con datos reales

Reescrita `menu_principal` en `citas/views.py` para calcular y pasar al
template:

- **KPI cards principales** (top): `total_citas`, `total_pacientes`,
  `total_medicos`, `total_especialidades` — todos filtrando por `activo='S'`.
- **Breakdown de citas por estado**: dict `citas_por_estado` con las 5
  claves (PROGRAMADA, CONFIRMADA, ATENDIDA, CANCELADA, NO_ASISTIO).
- **Agenda de hoy**: queryset filtrado por `fecha_cita=timezone.localdate()`
  con `select_related` hacia paciente/medico/consultorio/especialidad/sede
  para evitar N+1.
- **Próximas citas**: top 5 de citas futuras (`fecha_cita__gt=hoy`) con
  estado `PROGRAMADA` o `CONFIRMADA`, ordenadas por fecha/hora.
- **Mini KPIs geográficos** (bottom): departamentos, municipios, sedes,
  consultorios — conteo rápido para visibilidad de catálogos maestros.

El template `citas/templates/citas/menu.html` fue reescrito con secciones
claras usando Bootstrap grid, badges de color por estado e iconos
`bi-*`.

---

### Vista de auditoría (solo lectura)

Nueva vista `auditoria_lista` (solo rol `administrativo`) en
`citas/views.py:1355+`. Permite consultar `AUDITORIA_ACCIONES` con filtros:

- `tabla` (dropdown dinámico con `distinct`)
- `accion` (INSERT / UPDATE / DELETE / SELECT)
- Rango de fechas `desde` / `hasta` (filtro por `fecha_accion__date`)
- Búsqueda libre sobre `usuario_bd` o `rol_activo`
- Paginación de 25 en 25

Template: `citas/templates/citas/auditoria/lista.html` — tabla con badges
por tipo de acción, estado vacío explicativo ("en desarrollo SQLite esta
tabla solo se llena con triggers de Oracle"), y pagination con
preservación de filtros vía query string.

URL: `/auditoria/` (nombre `auditoria_lista`).
Link en sidebar activado dentro de `base.html` (antes era placeholder).

> **Importante:** Esta tabla se llena **exclusivamente por triggers de
> Oracle** en producción. En SQLite de desarrollo queda vacía, lo cual es
> correcto: validamos la UI, no la captura.

---

### Toasts de Bootstrap 5

Se eliminó la `div.alert` de `base.html` y se sustituyó por un contenedor
fijo `toast-container position-fixed top-0 end-0 p-3`. El loop sobre
`messages` elige el fondo del toast según `message.tags`:

- `success` → `bg-success`
- `error` → `bg-danger`
- `warning` → `bg-warning`
- cualquier otro → `bg-info`

Los toasts se inicializan con un JS mínimo al final del `<body>`:

```javascript
document.querySelectorAll('.toast').forEach(t => {
    bootstrap.Toast.getOrCreateInstance(t).show();
});
```

Beneficio: las confirmaciones de CRUD ya no bloquean el layout ni
requieren scroll; se apilan en la esquina superior derecha y se auto-
descartan.

---

### django-crispy-forms + crispy-bootstrap5

Integración mínima y pragmática — sólo donde realmente simplifica.
Razón: los formularios principales (`citas_medicas/formulario.html`,
`medicos/formulario.html`, `pacientes/formulario.html`) ya tenían
layouts manuales en dos columnas con iconos, separadores y widgets
con clases Bootstrap embebidas; reemplazarlos por `{{ form|crispy }}`
habría borrado el diseño.

Aplicado en: **`citas/templates/citas/citas_medicas/cambiar_estado.html`**
— formulario simple de 2 campos (estado + observaciones) donde crispy
aporta labels, errores y spacing sin repetir markup.

Configuración en `gestion_citas/settings.py`:

```python
INSTALLED_APPS += ['crispy_forms', 'crispy_bootstrap5']
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
```

Versiones pinneadas (compatibles con Django 4.2):

```
django-crispy-forms==2.1
crispy-bootstrap5==0.7
```

> ⚠️ La última `crispy-bootstrap5` arrastra Django 6.x; por eso se
> ancla `0.7`.

---

### Fallback SQLite — arquitectura dev/prod

**Problema:** Oracle XE no siempre está disponible en la máquina del dev,
y `cx_Oracle` 8.x no tiene wheel para Python 3.14.

**Solución:** Variable de entorno `USE_SQLITE=1`. Cuando está presente:

1. `gestion_citas/__init__.py` **siempre** registra el shim
   `cx_Oracle = oracledb` (Django 4.2 lo importa por nombre).
2. `gestion_citas/settings.py` elige SQLite si `USE_SQLITE=1`, Oracle si no:
   ```python
   USE_SQLITE = os.environ.get('USE_SQLITE') == '1'
   if USE_SQLITE:
       DATABASES = {'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db_dev.sqlite3',
       }}
   else:
       DATABASES = { ... Oracle config ... }
   ```
3. `citas/models.py` expone un flag:
   ```python
   _DJANGO_MANAGED = os.environ.get('USE_SQLITE') == '1'
   ```
   y reemplaza `managed = False` por `managed = _DJANGO_MANAGED` en
   **los 10 modelos**. Así:
   - En Oracle (prod): tablas gestionadas por los scripts SQL (`managed=False`).
   - En SQLite (dev): `migrate` las crea automáticamente (`managed=True`).

Esto mantiene la arquitectura original intacta y permite trabajar sin
Oracle. **El switch es por variable de entorno, no por código en git.**

---

### Script de seed (`seed_dev.py`)

Nuevo archivo `django_app/seed_dev.py`, idempotente (no duplica datos en
ejecuciones sucesivas). Carga:

- 4 usuarios Django (uno por rol) con las contraseñas listadas arriba
- 2 departamentos + 3 municipios + 2 sedes + 3 consultorios
- 4 especialidades
- 3 médicos (con Persona asociada) y 4 pacientes (con Persona asociada)
- 6 citas cubriendo los 5 estados posibles + una para hoy (para ver la
  agenda funcionando en el dashboard)

Uso: `USE_SQLITE=1 py seed_dev.py`.

---

### Dependencias (cambios respecto a fases previas)

`requirements.txt` actualizado:

```
Django==4.2.11
oracledb>=3.0           # reemplaza cx_Oracle (Py 3.14 compat)
Pillow>=11.0
python-decouple==3.8
django-crispy-forms==2.1
crispy-bootstrap5==0.7
whitenoise==6.6.0
```

Eliminados / migrados:

- `cx_Oracle==8.3.0` → reemplazado por shim sobre `oracledb`.
- `OPTIONS.threaded=True` removido de `DATABASES['default']` (deprecado en `oracledb`).

Shim en `gestion_citas/__init__.py`:

```python
import sys
import oracledb
oracledb.version = "8.3.0"
sys.modules["cx_Oracle"] = oracledb
```

---

### Bugs de arranque corregidos en Fase 4

| Bug | Archivo | Fix |
|-----|---------|-----|
| `TemplateDoesNotExist: base.html` | `gestion_citas/settings.py` | Añadido `BASE_DIR / 'gestion_citas' / 'templates'` a `TEMPLATES.DIRS` |
| `TemplateSyntaxError: 'block contenido' appears more than once` | `gestion_citas/templates/base.html` | Bloque duplicado dentro de `{% if/else %}` → hoisteado fuera del condicional |
| `TypeError: date filter H:i on DateField` | `citas/templates/citas/citas_medicas/detalle.html:90` | Cambiado `|date:"d/m/Y H:i"` → `|date:"d/m/Y"` sobre `fecha_creacion` |
| `cx_Oracle 8.3.0` no carga en Py 3.14 (falta `pkg_resources`) | `requirements.txt` + `gestion_citas/__init__.py` | Migrado a `oracledb>=3.0` + shim |
| `OPTIONS.threaded=True` rechazado por `oracledb` | `gestion_citas/settings.py` | Removido el kwarg |

---

### Archivos Modificados / Creados en Fase 4

| Archivo | Acción | Nota |
|---------|--------|------|
| `gestion_citas/__init__.py` | **CREADO** | Shim cx_Oracle → oracledb |
| `gestion_citas/settings.py` | **MODIFICADO** | SQLite fallback + crispy + TEMPLATES.DIRS + quitar threaded |
| `gestion_citas/templates/base.html` | **MODIFICADO** | Toasts, bloque contenido hoisteado, link auditoría |
| `citas/models.py` | **MODIFICADO** | `_DJANGO_MANAGED` flag en 10 modelos |
| `citas/views.py` | **MODIFICADO** | `menu_principal` reescrito + nuevo `auditoria_lista` |
| `citas/urls.py` | **MODIFICADO** | `+ path('auditoria/', ...)` |
| `citas/templates/citas/menu.html` | **REESCRITO** | Dashboard con datos reales |
| `citas/templates/citas/auditoria/lista.html` | **CREADO** | Vista de auditoría con filtros |
| `citas/templates/citas/citas_medicas/detalle.html` | **FIX** | Formato de fecha |
| `citas/templates/citas/citas_medicas/cambiar_estado.html` | **MODIFICADO** | Crispy-forms aplicado |
| `requirements.txt` | **MODIFICADO** | Deps actualizadas |
| `seed_dev.py` | **CREADO** | Datos demo idempotentes |

---

### Decisiones de Arquitectura (Fase 4)

1. **Dev y prod comparten el código, se diferencian por env var.** Nada de
   branches paralelos, nada de `settings_dev.py`. El flag `USE_SQLITE`
   controla tanto el engine como `managed` en los modelos.
2. **Crispy mínimo, no global.** Se aplica donde reduce código real.
   Reemplazar los forms grandes rompería su diseño.
3. **Auditoría es read-only por contrato.** La vista no tiene URLs de
   crear/editar/eliminar. Solo lista + filtros. Los registros los produce
   Oracle vía triggers.
4. **Toasts no bloqueantes** elegidos sobre alerts porque el flujo CRUD
   redirige mucho y los alerts empujaban el contenido.
5. **Shim de cx_Oracle** en lugar de actualizar Django o instalar Py < 3.14
   en la máquina del dev: la dependencia real es `oracledb`, y Django 4.2
   solo mira el **nombre** `cx_Oracle` — esto nos deja libres de migrar a
   Django 5 cuando queramos, sin tocar el shim.

---

### Estado Actual del Proyecto (post-Fase 4)

#### Modelos Django: 10/10 con vistas, templates y UX pulida

| # | Modelo | Vistas CRUD | Templates | Dashboard | Notas |
|---|--------|:-----------:|:---------:|:---------:|-------|
| 1 | Departamento | ✅ | ✅ | ✅ | |
| 2 | Municipio | ✅ | ✅ | ✅ | |
| 3 | Sede | ✅ | ✅ | ✅ | |
| 4 | Consultorio | ✅ | ✅ | ✅ | |
| 5 | Especialidad | ✅ | ✅ | ✅ | |
| 6 | Persona | ✅ (vía Med/Pac) | ✅ (vía form doble) | — | |
| 7 | Medico | ✅ | ✅ | ✅ | |
| 8 | Paciente | ✅ | ✅ | ✅ | |
| 9 | CitaMedica | ✅ + máquina de estados | ✅ | ✅ (agenda + próximas) | |
| 10 | AuditoriaAccion | ✅ (solo lectura) | ✅ | — | **Nuevo en Fase 4** |

#### Funcionalidades operativas end-to-end

- Login con rol dinámico (4 roles)
- CRUD completo de 9 entidades
- Máquina de estados de citas
- Dashboard con KPIs, agenda y próximas citas
- Auditoría filtrable
- Toasts de feedback en todo el sistema
- Entorno local sin Oracle (SQLite fallback)
- Seed de datos demo idempotente

---

### Próximos pasos sugeridos (fuera de Fase 4)

- Calendario visual de citas (FullCalendar) en `/citas/calendario/`.
- Exportación de auditoría a CSV/XLSX.
- Reportes (citas por médico/mes, tasas de NO_ASISTIO, ocupación por consultorio).
- Conexión real contra Oracle XE en una VM y validación de triggers.

