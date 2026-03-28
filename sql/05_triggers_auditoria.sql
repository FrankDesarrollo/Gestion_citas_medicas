-- ============================================================
-- SCRIPT 05: TRIGGERS DE AUDITORÍA Y CONSULTAS DBA
-- Sistema de Gestión de Citas Médicas
-- Oracle XE 18c - Esquema: APP_CITAS
-- ============================================================

-- ============================================================
-- TRIGGER: Auditar cambios en tablas maestras
-- Se dispara en INSERT, UPDATE, DELETE sobre tablas críticas
-- ============================================================

CREATE OR REPLACE TRIGGER trg_auditoria_departamentos
AFTER INSERT OR UPDATE OR DELETE ON app_citas.departamentos
FOR EACH ROW
DECLARE
    v_accion VARCHAR2(10);
    v_datos_ant VARCHAR2(4000);
    v_datos_nue VARCHAR2(4000);
BEGIN
    IF INSERTING THEN
        v_accion := 'INSERT';
        v_datos_nue := 'codigo=' || :NEW.codigo_dane || ', nombre=' || :NEW.nombre_departamento;
    ELSIF UPDATING THEN
        v_accion := 'UPDATE';
        v_datos_ant := 'codigo=' || :OLD.codigo_dane || ', nombre=' || :OLD.nombre_departamento;
        v_datos_nue := 'codigo=' || :NEW.codigo_dane || ', nombre=' || :NEW.nombre_departamento;
    ELSIF DELETING THEN
        v_accion := 'DELETE';
        v_datos_ant := 'codigo=' || :OLD.codigo_dane || ', nombre=' || :OLD.nombre_departamento;
    END IF;

    INSERT INTO app_citas.auditoria_acciones
        (tabla_afectada, accion, id_registro, usuario_bd,
         datos_anteriores, datos_nuevos)
    VALUES
        ('DEPARTAMENTOS', v_accion,
         CASE WHEN DELETING THEN :OLD.id_departamento ELSE :NEW.id_departamento END,
         USER, v_datos_ant, v_datos_nue);
END;
/

-- Trigger para MUNICIPIOS
CREATE OR REPLACE TRIGGER trg_auditoria_municipios
AFTER INSERT OR UPDATE OR DELETE ON app_citas.municipios
FOR EACH ROW
DECLARE
    v_accion VARCHAR2(10);
    v_datos_ant VARCHAR2(4000);
    v_datos_nue VARCHAR2(4000);
BEGIN
    IF INSERTING THEN
        v_accion := 'INSERT';
        v_datos_nue := 'codigo=' || :NEW.codigo_dane || ', nombre=' || :NEW.nombre_municipio;
    ELSIF UPDATING THEN
        v_accion := 'UPDATE';
        v_datos_ant := 'codigo=' || :OLD.codigo_dane || ', nombre=' || :OLD.nombre_municipio;
        v_datos_nue := 'codigo=' || :NEW.codigo_dane || ', nombre=' || :NEW.nombre_municipio;
    ELSIF DELETING THEN
        v_accion := 'DELETE';
        v_datos_ant := 'codigo=' || :OLD.codigo_dane || ', nombre=' || :OLD.nombre_municipio;
    END IF;

    INSERT INTO app_citas.auditoria_acciones
        (tabla_afectada, accion, id_registro, usuario_bd,
         datos_anteriores, datos_nuevos)
    VALUES
        ('MUNICIPIOS', v_accion,
         CASE WHEN DELETING THEN :OLD.id_municipio ELSE :NEW.id_municipio END,
         USER, v_datos_ant, v_datos_nue);
END;
/

-- Trigger para SEDES
CREATE OR REPLACE TRIGGER trg_auditoria_sedes
AFTER INSERT OR UPDATE OR DELETE ON app_citas.sedes
FOR EACH ROW
DECLARE
    v_accion VARCHAR2(10);
BEGIN
    IF INSERTING THEN v_accion := 'INSERT';
    ELSIF UPDATING THEN v_accion := 'UPDATE';
    ELSE v_accion := 'DELETE';
    END IF;

    INSERT INTO app_citas.auditoria_acciones
        (tabla_afectada, accion, id_registro, usuario_bd, datos_nuevos)
    VALUES
        ('SEDES', v_accion,
         CASE WHEN DELETING THEN :OLD.id_sede ELSE :NEW.id_sede END,
         USER,
         CASE WHEN DELETING THEN :OLD.nombre_sede ELSE :NEW.nombre_sede END);
END;
/

-- ============================================================
-- CONSULTAS ÚTILES PARA EL DBA (DESDE PGADMIN / SQL DEVELOPER)
-- ============================================================

-- 1. Ver todos los usuarios de la base de datos y su estado
SELECT username, account_status, created, profile,
       default_tablespace, temporary_tablespace
FROM dba_users
WHERE username IN ('APP_CITAS','USR_MEDICO','USR_PACIENTE',
                   'USR_ADMINISTRATIVO','USR_AUXILIAR')
ORDER BY username;

-- 2. Ver privilegios de sistema por usuario
SELECT grantee, privilege, admin_option
FROM dba_sys_privs
WHERE grantee IN ('APP_CITAS','USR_MEDICO','USR_PACIENTE',
                  'USR_ADMINISTRATIVO','USR_AUXILIAR',
                  'ROL_MEDICO','ROL_PACIENTE',
                  'ROL_ADMINISTRATIVO','ROL_AUXILIAR_MEDICO')
ORDER BY grantee, privilege;

-- 3. Ver privilegios de objeto (tablas) por rol
SELECT grantee, owner, table_name, privilege, grantable
FROM dba_tab_privs
WHERE owner = 'APP_CITAS'
ORDER BY grantee, table_name, privilege;

-- 4. Ver roles asignados a cada usuario
SELECT grantee AS usuario, granted_role, default_role
FROM dba_role_privs
WHERE grantee IN ('USR_MEDICO','USR_PACIENTE',
                  'USR_ADMINISTRATIVO','USR_AUXILIAR')
ORDER BY grantee;

-- 5. Ver sesiones activas en la base de datos
SELECT s.username, s.osuser, s.machine, s.program,
       s.status, s.logon_time, s.sid, s.serial#
FROM v$session s
WHERE s.username IS NOT NULL
  AND s.username IN ('APP_CITAS','USR_MEDICO','USR_PACIENTE',
                     'USR_ADMINISTRATIVO','USR_AUXILIAR')
ORDER BY s.logon_time;

-- 6. Reporte de auditoría: últimas 20 acciones
SELECT a.tabla_afectada, a.accion, a.usuario_bd,
       a.fecha_accion, a.datos_anteriores, a.datos_nuevos
FROM app_citas.auditoria_acciones a
ORDER BY a.fecha_accion DESC
FETCH FIRST 20 ROWS ONLY;

-- 7. Estadísticas de acceso por usuario
SELECT usuario_bd, tabla_afectada, accion, COUNT(*) total
FROM app_citas.auditoria_acciones
GROUP BY usuario_bd, tabla_afectada, accion
ORDER BY usuario_bd, tabla_afectada, accion;

-- 8. Ver espacio utilizado por tablespace
SELECT t.tablespace_name,
       ROUND(SUM(d.bytes)/1024/1024, 2) AS size_mb,
       ROUND(SUM(d.maxbytes)/1024/1024, 2) AS max_mb
FROM dba_tablespaces t
JOIN dba_data_files d ON t.tablespace_name = d.tablespace_name
WHERE t.tablespace_name = 'TBS_CITAS_MEDICAS'
GROUP BY t.tablespace_name;

-- 9. Ver objetos del esquema APP_CITAS
SELECT object_name, object_type, status, created, last_ddl_time
FROM dba_objects
WHERE owner = 'APP_CITAS'
ORDER BY object_type, object_name;

-- 10. Verificar triggers activos
SELECT trigger_name, trigger_type, triggering_event,
       table_name, status
FROM dba_triggers
WHERE owner = 'APP_CITAS'
ORDER BY table_name;

-- ============================================================
-- COMANDOS DE MANTENIMIENTO
-- ============================================================

-- Bloquear un usuario (cuando se detecte uso indebido)
-- ALTER USER usr_medico ACCOUNT LOCK;

-- Desbloquear un usuario
-- ALTER USER usr_medico ACCOUNT UNLOCK;

-- Cambiar la contraseña de un usuario
-- ALTER USER usr_medico IDENTIFIED BY NuevaClave2024#;

-- Revocar un privilegio
-- REVOKE UPDATE ON app_citas.citas_medicas FROM rol_medico;

-- Otorgar un privilegio adicional
-- GRANT INSERT ON app_citas.citas_medicas TO rol_auxiliar_medico;

-- Ver intentos fallidos de conexión
SELECT username, failed_attempts, lock_date
FROM dba_users
WHERE failed_attempts > 0;

COMMIT;
-- FIN SCRIPT 05
