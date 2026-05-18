-- ============================================================
-- SCRIPT 08: TABLAS DE GESTIÓN DE PERMISOS
-- Sistema de Gestión de Citas Médicas
-- Oracle XE 18c - Esquema: APP_CITAS
-- ============================================================
-- Ejecutar conectado como: app_citas
-- Conexión: sqlplus app_citas/Citas2024#@localhost:1521/XEPDB1
-- ============================================================
-- Requisito campus: "Gestión de roles y permisos mediante un
-- formulario donde se controle qué puede ver, crear, editar
-- o eliminar cada usuario dentro del aplicativo."
-- ============================================================

-- ============================================================
-- TABLA 1: PERMISOS_MODULOS
-- Catálogo de módulos protegibles del sistema
-- ============================================================
CREATE TABLE permisos_modulos (
    id                  NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_perm_modulo PRIMARY KEY,
    codigo              VARCHAR2(50)    NOT NULL,
    nombre              VARCHAR2(100)   NOT NULL,
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_pmod_activo CHECK (activo IN ('S','N')),
    CONSTRAINT uq_pmod_codigo UNIQUE (codigo)
)
TABLESPACE tbs_citas_medicas;

COMMENT ON TABLE  permisos_modulos         IS 'Catálogo de módulos protegibles del sistema';
COMMENT ON COLUMN permisos_modulos.codigo  IS 'Clave corta del módulo (citas, pacientes, ...)';
COMMENT ON COLUMN permisos_modulos.activo  IS 'S=Activo, N=Inactivo';

-- ============================================================
-- TABLA 2: PERMISOS_ROL
-- Matriz rol × módulo con 4 flags CRUD
-- ============================================================
CREATE TABLE permisos_rol (
    id                  NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_perm_rol PRIMARY KEY,
    rol                 VARCHAR2(30)    NOT NULL
                                        CONSTRAINT ck_prol_rol CHECK (
                                            rol IN ('administrativo','medico',
                                                    'paciente','auxiliar_medico')
                                        ),
    id_modulo           NUMBER          NOT NULL,
    puede_ver           NUMBER(1)       DEFAULT 0 NOT NULL
                                        CONSTRAINT ck_prol_ver CHECK (puede_ver IN (0,1)),
    puede_crear         NUMBER(1)       DEFAULT 0 NOT NULL
                                        CONSTRAINT ck_prol_crear CHECK (puede_crear IN (0,1)),
    puede_editar        NUMBER(1)       DEFAULT 0 NOT NULL
                                        CONSTRAINT ck_prol_editar CHECK (puede_editar IN (0,1)),
    puede_eliminar      NUMBER(1)       DEFAULT 0 NOT NULL
                                        CONSTRAINT ck_prol_eliminar CHECK (puede_eliminar IN (0,1)),
    CONSTRAINT fk_prol_modulo FOREIGN KEY (id_modulo)
        REFERENCES permisos_modulos(id) ON DELETE CASCADE,
    CONSTRAINT uq_prol_rol_modulo UNIQUE (rol, id_modulo)
)
TABLESPACE tbs_citas_medicas;

COMMENT ON TABLE  permisos_rol              IS 'Permisos CRUD por rol y módulo';
COMMENT ON COLUMN permisos_rol.puede_ver    IS '1=permitido, 0=denegado';
COMMENT ON COLUMN permisos_rol.puede_crear  IS '1=permitido, 0=denegado';
COMMENT ON COLUMN permisos_rol.puede_editar IS '1=permitido, 0=denegado';
COMMENT ON COLUMN permisos_rol.puede_eliminar IS '1=permitido, 0=denegado';

-- ============================================================
-- TABLA 3: PERMISOS_USUARIO
-- Override individual por usuario (NULL = hereda del rol)
-- ============================================================
CREATE TABLE permisos_usuario (
    id                  NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_perm_usuario PRIMARY KEY,
    id_usuario          NUMBER          NOT NULL,
    id_modulo           NUMBER          NOT NULL,
    -- NULL significa "heredar del rol"; 1/0 sobreescribe el permiso del rol
    puede_ver           NUMBER(1)       CONSTRAINT ck_pusr_ver     CHECK (puede_ver     IN (0,1)),
    puede_crear         NUMBER(1)       CONSTRAINT ck_pusr_crear   CHECK (puede_crear   IN (0,1)),
    puede_editar        NUMBER(1)       CONSTRAINT ck_pusr_editar  CHECK (puede_editar  IN (0,1)),
    puede_eliminar      NUMBER(1)       CONSTRAINT ck_pusr_elim    CHECK (puede_eliminar IN (0,1)),
    CONSTRAINT fk_pusr_usuario FOREIGN KEY (id_usuario)
        REFERENCES auth_user(id) ON DELETE CASCADE,
    CONSTRAINT fk_pusr_modulo FOREIGN KEY (id_modulo)
        REFERENCES permisos_modulos(id) ON DELETE CASCADE,
    CONSTRAINT uq_pusr_usuario_modulo UNIQUE (id_usuario, id_modulo)
)
TABLESPACE tbs_citas_medicas;

COMMENT ON TABLE  permisos_usuario             IS 'Override de permisos por usuario individual';
COMMENT ON COLUMN permisos_usuario.puede_ver   IS 'NULL=hereda del rol; 1=forzar permitido; 0=forzar denegado';

-- ============================================================
-- ÍNDICES
-- ============================================================
CREATE INDEX idx_prol_rol     ON permisos_rol(rol);
CREATE INDEX idx_prol_modulo  ON permisos_rol(id_modulo);
CREATE INDEX idx_pusr_usuario ON permisos_usuario(id_usuario);
CREATE INDEX idx_pusr_modulo  ON permisos_usuario(id_modulo);

-- ============================================================
-- DATOS INICIALES: 9 módulos del sistema
-- ============================================================
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('departamentos', 'Departamentos',  'S');
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('municipios',    'Municipios',     'S');
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('sedes',         'Sedes',          'S');
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('consultorios',  'Consultorios',   'S');
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('especialidades','Especialidades', 'S');
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('medicos',       'Médicos',        'S');
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('pacientes',     'Pacientes',      'S');
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('citas',         'Citas Médicas',  'S');
INSERT INTO permisos_modulos (codigo, nombre, activo) VALUES ('auditoria',     'Auditoría',      'S');

-- ============================================================
-- DATOS INICIALES: matriz de permisos por rol
-- Replica los permisos hardcoded de citas/decorators.py
-- administrativo → CRUD completo
-- medico / paciente / auxiliar_medico → solo lectura
-- ============================================================
BEGIN
    FOR m IN (SELECT id FROM permisos_modulos) LOOP
        -- Administrativo: acceso total
        INSERT INTO permisos_rol (rol, id_modulo, puede_ver, puede_crear, puede_editar, puede_eliminar)
        VALUES ('administrativo', m.id, 1, 1, 1, 1);
        -- Médico: solo lectura
        INSERT INTO permisos_rol (rol, id_modulo, puede_ver, puede_crear, puede_editar, puede_eliminar)
        VALUES ('medico', m.id, 1, 0, 0, 0);
        -- Paciente: solo lectura
        INSERT INTO permisos_rol (rol, id_modulo, puede_ver, puede_crear, puede_editar, puede_eliminar)
        VALUES ('paciente', m.id, 1, 0, 0, 0);
        -- Auxiliar médico: solo lectura
        INSERT INTO permisos_rol (rol, id_modulo, puede_ver, puede_crear, puede_editar, puede_eliminar)
        VALUES ('auxiliar_medico', m.id, 1, 0, 0, 0);
    END LOOP;
END;
/

-- ============================================================
-- PRIVILEGIOS SOBRE LAS TABLAS DE PERMISOS
-- Solo administrativo puede modificar; los demás solo leen
-- ============================================================

-- ROL_ADMINISTRATIVO: CRUD completo sobre las 3 tablas de permisos
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.permisos_modulos TO rol_administrativo;
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.permisos_rol     TO rol_administrativo;
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.permisos_usuario TO rol_administrativo;

-- Todos los roles leen la tabla de módulos (necesario para el decorador en capa app)
GRANT SELECT ON app_citas.permisos_modulos TO rol_medico;
GRANT SELECT ON app_citas.permisos_modulos TO rol_paciente;
GRANT SELECT ON app_citas.permisos_modulos TO rol_auxiliar_medico;

-- Todos los roles leen sus propios permisos (necesario para el decorador)
GRANT SELECT ON app_citas.permisos_rol     TO rol_medico;
GRANT SELECT ON app_citas.permisos_rol     TO rol_paciente;
GRANT SELECT ON app_citas.permisos_rol     TO rol_auxiliar_medico;

GRANT SELECT ON app_citas.permisos_usuario TO rol_medico;
GRANT SELECT ON app_citas.permisos_usuario TO rol_paciente;
GRANT SELECT ON app_citas.permisos_usuario TO rol_auxiliar_medico;

-- Sinónimos públicos para acceso sin prefijo de esquema
CREATE PUBLIC SYNONYM permisos_modulos FOR app_citas.permisos_modulos;
CREATE PUBLIC SYNONYM permisos_rol     FOR app_citas.permisos_rol;
CREATE PUBLIC SYNONYM permisos_usuario FOR app_citas.permisos_usuario;

COMMIT;

-- ============================================================
-- VERIFICACIÓN
-- ============================================================
SELECT p.codigo, p.nombre,
       pr.rol,
       pr.puede_ver, pr.puede_crear, pr.puede_editar, pr.puede_eliminar
FROM   permisos_modulos p
JOIN   permisos_rol pr ON pr.id_modulo = p.id
ORDER  BY p.codigo, pr.rol;

-- FIN SCRIPT 08
