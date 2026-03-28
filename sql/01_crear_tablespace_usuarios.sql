-- ============================================================
-- SCRIPT 01: TABLESPACE, USUARIOS Y ROLES
-- Sistema de Gestión de Citas Médicas
-- Oracle XE 18c - Materia: Electiva I, II, III, IV
-- Docente: [Nombre del Docente]
-- ============================================================
-- IMPORTANTE: Ejecutar conectado como SYSDBA en la PDB XEPDB1
-- Conexión: sqlplus sys/password@localhost:1521/XEPDB1 as sysdba
-- ============================================================

-- ============================================================
-- PASO 1: CREAR TABLESPACE DEDICADO AL SISTEMA
-- ============================================================
-- El tablespace es el espacio lógico donde se almacenarán
-- los datos del sistema de gestión de citas médicas.

CREATE TABLESPACE tbs_citas_medicas
    DATAFILE 'tbs_citas_medicas01.dbf'
    SIZE 100M
    AUTOEXTEND ON
    NEXT 10M
    MAXSIZE 500M
    EXTENT MANAGEMENT LOCAL
    SEGMENT SPACE MANAGEMENT AUTO;

-- Verificar creación del tablespace
SELECT tablespace_name, status, contents, extent_management
FROM dba_tablespaces
WHERE tablespace_name = 'TBS_CITAS_MEDICAS';

-- ============================================================
-- PASO 2: CREAR USUARIO PROPIETARIO DEL ESQUEMA (DBA App)
-- Este usuario será el dueño de todas las tablas del sistema
-- ============================================================
CREATE USER app_citas IDENTIFIED BY Citas2024#
    DEFAULT TABLESPACE tbs_citas_medicas
    TEMPORARY TABLESPACE TEMP
    QUOTA UNLIMITED ON tbs_citas_medicas;

-- Privilegios de sistema para el usuario propietario
GRANT CREATE SESSION TO app_citas;
GRANT CREATE TABLE TO app_citas;
GRANT CREATE VIEW TO app_citas;
GRANT CREATE SEQUENCE TO app_citas;
GRANT CREATE PROCEDURE TO app_citas;
GRANT CREATE TRIGGER TO app_citas;
GRANT CREATE SYNONYM TO app_citas;

-- ============================================================
-- PASO 3: CREAR ROLES POR PERFIL DE USUARIO
-- Cada rol representa un tipo de usuario en el sistema
-- ============================================================

-- ROL 1: MÉDICO - Puede consultar y actualizar citas/pacientes
CREATE ROLE rol_medico;

-- ROL 2: PACIENTE - Solo puede consultar su información
CREATE ROLE rol_paciente;

-- ROL 3: ADMINISTRATIVO - Gestión completa de citas y maestros
CREATE ROLE rol_administrativo;

-- ROL 4: AUXILIAR MÉDICO - Consulta y registro limitado
CREATE ROLE rol_auxiliar_medico;

-- Verificar roles creados
SELECT role, created FROM dba_roles
WHERE role IN ('ROL_MEDICO','ROL_PACIENTE','ROL_ADMINISTRATIVO','ROL_AUXILIAR_MEDICO');

-- ============================================================
-- PASO 4: CREAR USUARIOS FINALES DEL SISTEMA
-- Estos usuarios se conectarán desde Django según su perfil
-- ============================================================

-- Usuario con rol MÉDICO
CREATE USER usr_medico IDENTIFIED BY Med2024#
    DEFAULT TABLESPACE tbs_citas_medicas
    TEMPORARY TABLESPACE TEMP
    QUOTA 10M ON tbs_citas_medicas;
GRANT CREATE SESSION TO usr_medico;
GRANT rol_medico TO usr_medico;

-- Usuario con rol PACIENTE
CREATE USER usr_paciente IDENTIFIED BY Pac2024#
    DEFAULT TABLESPACE tbs_citas_medicas
    TEMPORARY TABLESPACE TEMP
    QUOTA 5M ON tbs_citas_medicas;
GRANT CREATE SESSION TO usr_paciente;
GRANT rol_paciente TO usr_paciente;

-- Usuario con rol ADMINISTRATIVO
CREATE USER usr_administrativo IDENTIFIED BY Adm2024#
    DEFAULT TABLESPACE tbs_citas_medicas
    TEMPORARY TABLESPACE TEMP
    QUOTA 20M ON tbs_citas_medicas;
GRANT CREATE SESSION TO usr_administrativo;
GRANT rol_administrativo TO usr_administrativo;

-- Usuario con rol AUXILIAR MÉDICO
CREATE USER usr_auxiliar IDENTIFIED BY Aux2024#
    DEFAULT TABLESPACE tbs_citas_medicas
    TEMPORARY TABLESPACE TEMP
    QUOTA 10M ON tbs_citas_medicas;
GRANT CREATE SESSION TO usr_auxiliar;
GRANT rol_auxiliar_medico TO usr_auxiliar;

-- ============================================================
-- CONSULTA DE VERIFICACIÓN: Ver usuarios y sus roles
-- ============================================================
SELECT grantee, granted_role, admin_option, default_role
FROM dba_role_privs
WHERE grantee IN ('USR_MEDICO','USR_PACIENTE','USR_ADMINISTRATIVO','USR_AUXILIAR')
ORDER BY grantee;

COMMIT;
-- FIN SCRIPT 01
