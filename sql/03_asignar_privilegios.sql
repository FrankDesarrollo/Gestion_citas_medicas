-- ============================================================
-- SCRIPT 03: ASIGNACIÓN DE PRIVILEGIOS POR ROL
-- Sistema de Gestión de Citas Médicas
-- Oracle XE 18c
-- ============================================================
-- OBJETIVO PEDAGÓGICO:
-- Demostrar cómo el DBA controla el acceso a datos según el
-- rol del usuario. Cada rol tendrá permisos diferentes sobre
-- las tablas del sistema.
-- ============================================================
-- Ejecutar como: SYS o APP_CITAS (dueño del esquema)
-- ============================================================

-- ============================================================
-- MATRIZ DE PRIVILEGIOS POR ROL Y TABLA
-- ============================================================
--
-- TABLA              | MEDICO  | PACIENTE | ADMINISTRATIVO | AUXILIAR
-- -------------------|---------|----------|----------------|----------
-- DEPARTAMENTOS      | SELECT  | SELECT   | ALL            | SELECT
-- MUNICIPIOS         | SELECT  | SELECT   | ALL            | SELECT
-- SEDES              | SELECT  | SELECT   | ALL            | SELECT
-- CONSULTORIOS       | SELECT  | SELECT   | ALL            | SELECT
-- ESPECIALIDADES     | SELECT  | -        | ALL            | SELECT
-- PERSONAS           | SELECT  | SELECT*  | ALL            | SELECT,INS
-- MEDICOS            | SELECT  | SELECT   | ALL            | SELECT
-- PACIENTES          | SELECT  | SELECT*  | ALL            | SELECT,INS
-- CITAS_MEDICAS      | SEL,UPD | SELECT*  | ALL            | SEL,INS,UPD
-- AUDITORIA          | -       | -        | SELECT         | -
--
-- * Solo puede ver su propia información (controlado a nivel app)
-- ALL = SELECT, INSERT, UPDATE, DELETE
-- ============================================================

-- ============================================================
-- PRIVILEGIOS PARA ROL_MEDICO
-- Un médico puede consultar catálogos y actualizar citas
-- ============================================================

-- Catálogos maestros (solo lectura)
GRANT SELECT ON app_citas.departamentos TO rol_medico;
GRANT SELECT ON app_citas.municipios TO rol_medico;
GRANT SELECT ON app_citas.sedes TO rol_medico;
GRANT SELECT ON app_citas.consultorios TO rol_medico;
GRANT SELECT ON app_citas.especialidades TO rol_medico;

-- Información de personas y médicos (solo lectura)
GRANT SELECT ON app_citas.personas TO rol_medico;
GRANT SELECT ON app_citas.medicos TO rol_medico;
GRANT SELECT ON app_citas.pacientes TO rol_medico;

-- Citas: puede consultar y actualizar (no crear ni eliminar)
GRANT SELECT ON app_citas.citas_medicas TO rol_medico;
GRANT UPDATE ON app_citas.citas_medicas TO rol_medico;

-- Auditoría: sin acceso
-- (No se otorga ningún privilegio sobre auditoria_acciones)

-- ============================================================
-- PRIVILEGIOS PARA ROL_PACIENTE
-- Un paciente solo puede ver sus propios datos
-- (El filtro de "mis datos" se implementa en la aplicación)
-- ============================================================

-- Catálogos maestros básicos (solo lectura)
GRANT SELECT ON app_citas.departamentos TO rol_paciente;
GRANT SELECT ON app_citas.municipios TO rol_paciente;
GRANT SELECT ON app_citas.sedes TO rol_paciente;
GRANT SELECT ON app_citas.consultorios TO rol_paciente;

-- Sus propios datos
GRANT SELECT ON app_citas.personas TO rol_paciente;
GRANT SELECT ON app_citas.pacientes TO rol_paciente;
GRANT SELECT ON app_citas.medicos TO rol_paciente;
GRANT SELECT ON app_citas.especialidades TO rol_paciente;

-- Solo puede consultar sus citas
GRANT SELECT ON app_citas.citas_medicas TO rol_paciente;

-- ============================================================
-- PRIVILEGIOS PARA ROL_ADMINISTRATIVO
-- Acceso total a tablas maestras y de gestión
-- ============================================================

-- Acceso completo a catálogos maestros
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.departamentos TO rol_administrativo;
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.municipios TO rol_administrativo;
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.sedes TO rol_administrativo;
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.consultorios TO rol_administrativo;
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.especialidades TO rol_administrativo;

-- Acceso completo a personas, médicos y pacientes
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.personas TO rol_administrativo;
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.medicos TO rol_administrativo;
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.pacientes TO rol_administrativo;

-- Acceso completo a citas médicas
GRANT SELECT, INSERT, UPDATE, DELETE ON app_citas.citas_medicas TO rol_administrativo;

-- Acceso de solo lectura a auditoría
GRANT SELECT ON app_citas.auditoria_acciones TO rol_administrativo;

-- ============================================================
-- PRIVILEGIOS PARA ROL_AUXILIAR_MEDICO
-- Puede consultar catálogos, registrar y consultar citas
-- ============================================================

-- Catálogos maestros (solo lectura)
GRANT SELECT ON app_citas.departamentos TO rol_auxiliar_medico;
GRANT SELECT ON app_citas.municipios TO rol_auxiliar_medico;
GRANT SELECT ON app_citas.sedes TO rol_auxiliar_medico;
GRANT SELECT ON app_citas.consultorios TO rol_auxiliar_medico;
GRANT SELECT ON app_citas.especialidades TO rol_auxiliar_medico;

-- Puede registrar nuevas personas y pacientes
GRANT SELECT, INSERT ON app_citas.personas TO rol_auxiliar_medico;
GRANT SELECT, INSERT ON app_citas.pacientes TO rol_auxiliar_medico;
GRANT SELECT ON app_citas.medicos TO rol_auxiliar_medico;

-- Puede crear, consultar y actualizar citas (no eliminar)
GRANT SELECT, INSERT, UPDATE ON app_citas.citas_medicas TO rol_auxiliar_medico;

-- ============================================================
-- CREAR SINÓNIMOS PÚBLICOS (Opcional)
-- Permite a los usuarios referenciar tablas sin el prefijo app_citas
-- ============================================================
CREATE PUBLIC SYNONYM departamentos FOR app_citas.departamentos;
CREATE PUBLIC SYNONYM municipios FOR app_citas.municipios;
CREATE PUBLIC SYNONYM sedes FOR app_citas.sedes;
CREATE PUBLIC SYNONYM consultorios FOR app_citas.consultorios;
CREATE PUBLIC SYNONYM especialidades FOR app_citas.especialidades;
CREATE PUBLIC SYNONYM personas FOR app_citas.personas;
CREATE PUBLIC SYNONYM medicos FOR app_citas.medicos;
CREATE PUBLIC SYNONYM pacientes FOR app_citas.pacientes;
CREATE PUBLIC SYNONYM citas_medicas FOR app_citas.citas_medicas;
CREATE PUBLIC SYNONYM auditoria_acciones FOR app_citas.auditoria_acciones;

-- ============================================================
-- VERIFICACIÓN: Consultar privilegios otorgados por tabla
-- ============================================================
-- Ver todos los privilegios otorgados sobre tablas del esquema
SELECT grantee, table_name, privilege, grantable
FROM all_tab_privs
WHERE table_schema = 'APP_CITAS'
ORDER BY grantee, table_name, privilege;

-- Ver privilegios de un rol específico
-- (Cambiar el nombre del rol según necesidad)
SELECT table_name, privilege
FROM all_tab_privs
WHERE grantee = 'ROL_ADMINISTRATIVO'
ORDER BY table_name;

-- Ver qué privilegios tiene un usuario específico heredados de sus roles
SELECT rp.grantee AS usuario,
       rp.granted_role,
       tp.table_name,
       tp.privilege
FROM dba_role_privs rp
JOIN dba_tab_privs tp ON rp.granted_role = tp.grantee
WHERE rp.grantee IN ('USR_MEDICO','USR_PACIENTE','USR_ADMINISTRATIVO','USR_AUXILIAR')
ORDER BY rp.grantee, tp.table_name;

COMMIT;
-- FIN SCRIPT 03
