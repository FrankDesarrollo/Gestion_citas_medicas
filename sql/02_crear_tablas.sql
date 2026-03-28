-- ============================================================
-- SCRIPT 02: CREACIÓN DE TABLAS DEL SISTEMA
-- Sistema de Gestión de Citas Médicas
-- Oracle XE 18c - Esquema: APP_CITAS
-- ============================================================
-- Ejecutar conectado como: app_citas
-- Conexión: sqlplus app_citas/Citas2024#@localhost:1521/XEPDB1
-- ============================================================

-- ============================================================
-- TABLA 1: DEPARTAMENTOS
-- Almacena los departamentos del país (Colombia)
-- ============================================================
CREATE TABLE departamentos (
    id_departamento     NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_departamento PRIMARY KEY,
    codigo_dane         VARCHAR2(2)     NOT NULL,
    nombre_departamento VARCHAR2(100)   NOT NULL,
    activo              CHAR(1)         DEFAULT 'S' 
                                        CONSTRAINT ck_dep_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    fecha_modificacion  DATE,
    usuario_creacion    VARCHAR2(50)    DEFAULT USER NOT NULL,
    CONSTRAINT uq_dep_codigo UNIQUE (codigo_dane),
    CONSTRAINT uq_dep_nombre UNIQUE (nombre_departamento)
)
TABLESPACE tbs_citas_medicas;

COMMENT ON TABLE departamentos IS 'Tabla maestra de departamentos del país';
COMMENT ON COLUMN departamentos.codigo_dane IS 'Código DANE del departamento (2 dígitos)';
COMMENT ON COLUMN departamentos.activo IS 'S=Activo, N=Inactivo';

-- ============================================================
-- TABLA 2: MUNICIPIOS
-- Almacena los municipios asociados a cada departamento
-- ============================================================
CREATE TABLE municipios (
    id_municipio        NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_municipio PRIMARY KEY,
    codigo_dane         VARCHAR2(5)     NOT NULL,
    nombre_municipio    VARCHAR2(150)   NOT NULL,
    id_departamento     NUMBER          NOT NULL,
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_mun_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    fecha_modificacion  DATE,
    usuario_creacion    VARCHAR2(50)    DEFAULT USER NOT NULL,
    CONSTRAINT pk_mun_codigo UNIQUE (codigo_dane),
    CONSTRAINT fk_mun_departamento FOREIGN KEY (id_departamento)
        REFERENCES departamentos(id_departamento)
)
TABLESPACE tbs_citas_medicas;

COMMENT ON TABLE municipios IS 'Tabla maestra de municipios del país';
COMMENT ON COLUMN municipios.codigo_dane IS 'Código DANE del municipio (5 dígitos)';

-- ============================================================
-- TABLA 3: SEDES
-- Sedes o instalaciones de la institución médica
-- ============================================================
CREATE TABLE sedes (
    id_sede             NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_sede PRIMARY KEY,
    codigo_sede         VARCHAR2(10)    NOT NULL,
    nombre_sede         VARCHAR2(200)   NOT NULL,
    direccion           VARCHAR2(300)   NOT NULL,
    telefono            VARCHAR2(20),
    email               VARCHAR2(100),
    id_municipio        NUMBER          NOT NULL,
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_sed_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    fecha_modificacion  DATE,
    usuario_creacion    VARCHAR2(50)    DEFAULT USER NOT NULL,
    CONSTRAINT uq_sed_codigo UNIQUE (codigo_sede),
    CONSTRAINT fk_sed_municipio FOREIGN KEY (id_municipio)
        REFERENCES municipios(id_municipio)
)
TABLESPACE tbs_citas_medicas;

COMMENT ON TABLE sedes IS 'Sedes o puntos de atención de la institución médica';

-- ============================================================
-- TABLA 4: CONSULTORIOS
-- Consultorios disponibles en cada sede
-- ============================================================
CREATE TABLE consultorios (
    id_consultorio      NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_consultorio PRIMARY KEY,
    codigo_consultorio  VARCHAR2(10)    NOT NULL,
    nombre_consultorio  VARCHAR2(200)   NOT NULL,
    numero_piso         NUMBER(2),
    capacidad           NUMBER(3)       DEFAULT 1,
    id_sede             NUMBER          NOT NULL,
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_con_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    fecha_modificacion  DATE,
    usuario_creacion    VARCHAR2(50)    DEFAULT USER NOT NULL,
    CONSTRAINT uq_con_codigo UNIQUE (codigo_consultorio, id_sede),
    CONSTRAINT fk_con_sede FOREIGN KEY (id_sede)
        REFERENCES sedes(id_sede)
)
TABLESPACE tbs_citas_medicas;

COMMENT ON TABLE consultorios IS 'Consultorios disponibles en cada sede';
COMMENT ON COLUMN consultorios.capacidad IS 'Capacidad máxima de pacientes simultáneos';

-- ============================================================
-- TABLA 5: ESPECIALIDADES MÉDICAS (Tabla auxiliar)
-- ============================================================
CREATE TABLE especialidades (
    id_especialidad     NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_especialidad PRIMARY KEY,
    codigo_especialidad VARCHAR2(10)    NOT NULL,
    nombre_especialidad VARCHAR2(150)   NOT NULL,
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_esp_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_esp_codigo UNIQUE (codigo_especialidad)
)
TABLESPACE tbs_citas_medicas;

-- ============================================================
-- TABLA 6: PERSONAS (Base para médicos y pacientes)
-- ============================================================
CREATE TABLE personas (
    id_persona          NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_persona PRIMARY KEY,
    tipo_documento      VARCHAR2(3)     NOT NULL
                                        CONSTRAINT ck_per_tipo_doc
                                        CHECK (tipo_documento IN ('CC','TI','CE','PAS','RC')),
    numero_documento    VARCHAR2(20)    NOT NULL,
    primer_nombre       VARCHAR2(80)    NOT NULL,
    segundo_nombre      VARCHAR2(80),
    primer_apellido     VARCHAR2(80)    NOT NULL,
    segundo_apellido    VARCHAR2(80),
    fecha_nacimiento    DATE,
    sexo                CHAR(1)         CONSTRAINT ck_per_sexo CHECK (sexo IN ('M','F','O')),
    email               VARCHAR2(100),
    telefono            VARCHAR2(20),
    id_municipio        NUMBER,
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_per_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    fecha_modificacion  DATE,
    usuario_creacion    VARCHAR2(50)    DEFAULT USER NOT NULL,
    CONSTRAINT uq_per_documento UNIQUE (tipo_documento, numero_documento),
    CONSTRAINT fk_per_municipio FOREIGN KEY (id_municipio)
        REFERENCES municipios(id_municipio)
)
TABLESPACE tbs_citas_medicas;

-- ============================================================
-- TABLA 7: MEDICOS
-- ============================================================
CREATE TABLE medicos (
    id_medico           NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_medico PRIMARY KEY,
    id_persona          NUMBER          NOT NULL,
    id_especialidad     NUMBER          NOT NULL,
    numero_registro     VARCHAR2(20)    NOT NULL,
    tarifa_consulta     NUMBER(12,2),
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_med_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_med_persona UNIQUE (id_persona),
    CONSTRAINT uq_med_registro UNIQUE (numero_registro),
    CONSTRAINT fk_med_persona FOREIGN KEY (id_persona)
        REFERENCES personas(id_persona),
    CONSTRAINT fk_med_especialidad FOREIGN KEY (id_especialidad)
        REFERENCES especialidades(id_especialidad)
)
TABLESPACE tbs_citas_medicas;

-- ============================================================
-- TABLA 8: PACIENTES
-- ============================================================
CREATE TABLE pacientes (
    id_paciente         NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_paciente PRIMARY KEY,
    id_persona          NUMBER          NOT NULL,
    numero_historia     VARCHAR2(20)    NOT NULL,
    tipo_afiliacion     VARCHAR2(20)    DEFAULT 'CONTRIBUTIVO'
                                        CONSTRAINT ck_pac_afiliacion
                                        CHECK (tipo_afiliacion IN ('CONTRIBUTIVO','SUBSIDIADO','VINCULADO','PARTICULAR')),
    eps                 VARCHAR2(100),
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_pac_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    CONSTRAINT uq_pac_persona UNIQUE (id_persona),
    CONSTRAINT uq_pac_historia UNIQUE (numero_historia),
    CONSTRAINT fk_pac_persona FOREIGN KEY (id_persona)
        REFERENCES personas(id_persona)
)
TABLESPACE tbs_citas_medicas;

-- ============================================================
-- TABLA 9: CITAS MÉDICAS
-- ============================================================
CREATE TABLE citas_medicas (
    id_cita             NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_cita PRIMARY KEY,
    numero_cita         VARCHAR2(20)    NOT NULL,
    id_paciente         NUMBER          NOT NULL,
    id_medico           NUMBER          NOT NULL,
    id_consultorio      NUMBER          NOT NULL,
    fecha_cita          DATE            NOT NULL,
    hora_inicio         VARCHAR2(5)     NOT NULL,
    hora_fin            VARCHAR2(5)     NOT NULL,
    estado              VARCHAR2(20)    DEFAULT 'PROGRAMADA'
                                        CONSTRAINT ck_cit_estado
                                        CHECK (estado IN ('PROGRAMADA','CONFIRMADA','ATENDIDA','CANCELADA','NO_ASISTIO')),
    motivo_consulta     VARCHAR2(500),
    observaciones       VARCHAR2(1000),
    activo              CHAR(1)         DEFAULT 'S'
                                        CONSTRAINT ck_cit_activo CHECK (activo IN ('S','N')),
    fecha_creacion      DATE            DEFAULT SYSDATE NOT NULL,
    fecha_modificacion  DATE,
    usuario_creacion    VARCHAR2(50)    DEFAULT USER NOT NULL,
    CONSTRAINT uq_cit_numero UNIQUE (numero_cita),
    CONSTRAINT fk_cit_paciente FOREIGN KEY (id_paciente)
        REFERENCES pacientes(id_paciente),
    CONSTRAINT fk_cit_medico FOREIGN KEY (id_medico)
        REFERENCES medicos(id_medico),
    CONSTRAINT fk_cit_consultorio FOREIGN KEY (id_consultorio)
        REFERENCES consultorios(id_consultorio)
)
TABLESPACE tbs_citas_medicas;

-- ============================================================
-- TABLA 10: AUDITORIA (Registro de cambios por rol)
-- ============================================================
CREATE TABLE auditoria_acciones (
    id_auditoria        NUMBER          GENERATED ALWAYS AS IDENTITY
                                        (START WITH 1 INCREMENT BY 1)
                                        CONSTRAINT pk_auditoria PRIMARY KEY,
    tabla_afectada      VARCHAR2(50)    NOT NULL,
    accion              VARCHAR2(10)    NOT NULL
                                        CONSTRAINT ck_aud_accion
                                        CHECK (accion IN ('INSERT','UPDATE','DELETE','SELECT')),
    id_registro         NUMBER,
    usuario_bd          VARCHAR2(50)    NOT NULL,
    rol_activo          VARCHAR2(50),
    datos_anteriores    VARCHAR2(4000),
    datos_nuevos        VARCHAR2(4000),
    fecha_accion        DATE            DEFAULT SYSDATE NOT NULL,
    ip_cliente          VARCHAR2(50)
)
TABLESPACE tbs_citas_medicas;

COMMENT ON TABLE auditoria_acciones IS 'Registro de auditoría de acciones por rol de usuario';

-- ============================================================
-- CREAR ÍNDICES PARA MEJORAR RENDIMIENTO
-- ============================================================
CREATE INDEX idx_mun_depto ON municipios(id_departamento);
CREATE INDEX idx_sed_mun ON sedes(id_municipio);
CREATE INDEX idx_con_sede ON consultorios(id_sede);
CREATE INDEX idx_cit_paciente ON citas_medicas(id_paciente);
CREATE INDEX idx_cit_medico ON citas_medicas(id_medico);
CREATE INDEX idx_cit_fecha ON citas_medicas(fecha_cita);
CREATE INDEX idx_cit_estado ON citas_medicas(estado);
CREATE INDEX idx_aud_tabla ON auditoria_acciones(tabla_afectada, fecha_accion);

-- ============================================================
-- VERIFICAR TABLAS CREADAS
-- ============================================================
SELECT table_name, num_rows, tablespace_name
FROM user_tables
ORDER BY table_name;

COMMIT;
-- FIN SCRIPT 02
