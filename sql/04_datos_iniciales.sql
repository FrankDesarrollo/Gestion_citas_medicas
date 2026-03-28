-- ============================================================
-- SCRIPT 04: DATOS INICIALES (SEED DATA)
-- Sistema de Gestión de Citas Médicas
-- Oracle XE 18c - Esquema: APP_CITAS
-- ============================================================
-- Ejecutar como: app_citas
-- ============================================================

-- ============================================================
-- DEPARTAMENTOS (10 registros)
-- ============================================================
INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('05', 'ANTIOQUIA');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('11', 'BOGOTÁ D.C.');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('08', 'ATLÁNTICO');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('13', 'BOLÍVAR');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('17', 'CALDAS');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('19', 'CAUCA');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('27', 'CHOCÓ');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('68', 'SANTANDER');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('76', 'VALLE DEL CAUCA');

INSERT INTO departamentos (codigo_dane, nombre_departamento)
VALUES ('73', 'TOLIMA');

-- ============================================================
-- MUNICIPIOS (10 registros)
-- ============================================================
INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('05001', 'MEDELLÍN', 1);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('11001', 'BOGOTÁ D.C.', 2);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('08001', 'BARRANQUILLA', 3);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('13001', 'CARTAGENA DE INDIAS', 4);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('17001', 'MANIZALES', 5);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('19001', 'POPAYÁN', 6);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('68001', 'BUCARAMANGA', 8);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('76001', 'CALI', 9);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('73001', 'IBAGUÉ', 10);

INSERT INTO municipios (codigo_dane, nombre_municipio, id_departamento)
VALUES ('05002', 'ABEJORRAL', 1);

-- ============================================================
-- SEDES (6 registros)
-- ============================================================
INSERT INTO sedes (codigo_sede, nombre_sede, direccion, telefono, email, id_municipio)
VALUES ('SED001', 'SEDE PRINCIPAL BOGOTÁ', 'Cra. 15 # 90-12', '6014568900', 'sede.bogota@clinica.com', 2);

INSERT INTO sedes (codigo_sede, nombre_sede, direccion, telefono, email, id_municipio)
VALUES ('SED002', 'SEDE NORTE MEDELLÍN', 'Cll. 30 # 65-40 El Poblado', '6044521100', 'sede.medellin@clinica.com', 1);

INSERT INTO sedes (codigo_sede, nombre_sede, direccion, telefono, email, id_municipio)
VALUES ('SED003', 'SEDE ATLÁNTICO', 'Cra. 53 # 68-120 El Prado', '6055623300', 'sede.barranquilla@clinica.com', 3);

INSERT INTO sedes (codigo_sede, nombre_sede, direccion, telefono, email, id_municipio)
VALUES ('SED004', 'SEDE CALI SUR', 'Av. 6 Norte # 30-11', '6024789900', 'sede.cali@clinica.com', 8);

INSERT INTO sedes (codigo_sede, nombre_sede, direccion, telefono, email, id_municipio)
VALUES ('SED005', 'SEDE BUCARAMANGA', 'Cll. 45 # 27-60 Cabecera', '6077891100', 'sede.bucaramanga@clinica.com', 7);

INSERT INTO sedes (codigo_sede, nombre_sede, direccion, telefono, email, id_municipio)
VALUES ('SED006', 'SEDE IBAGUÉ CENTRO', 'Cra. 4 # 13-30 Centro', '6082345600', 'sede.ibague@clinica.com', 9);

-- ============================================================
-- CONSULTORIOS (8 registros)
-- ============================================================
INSERT INTO consultorios (codigo_consultorio, nombre_consultorio, numero_piso, capacidad, id_sede)
VALUES ('CON001', 'CONSULTORIO MEDICINA GENERAL 101', 1, 1, 1);

INSERT INTO consultorios (codigo_consultorio, nombre_consultorio, numero_piso, capacidad, id_sede)
VALUES ('CON002', 'CONSULTORIO CARDIOLOGÍA 201', 2, 1, 1);

INSERT INTO consultorios (codigo_consultorio, nombre_consultorio, numero_piso, capacidad, id_sede)
VALUES ('CON003', 'CONSULTORIO PEDIATRÍA 102', 1, 2, 1);

INSERT INTO consultorios (codigo_consultorio, nombre_consultorio, numero_piso, capacidad, id_sede)
VALUES ('CON004', 'CONSULTORIO MEDICINA GENERAL 101', 1, 1, 2);

INSERT INTO consultorios (codigo_consultorio, nombre_consultorio, numero_piso, capacidad, id_sede)
VALUES ('CON005', 'CONSULTORIO GINECOLOGÍA 301', 3, 1, 2);

INSERT INTO consultorios (codigo_consultorio, nombre_consultorio, numero_piso, capacidad, id_sede)
VALUES ('CON006', 'CONSULTORIO ORTOPEDIA 202', 2, 1, 3);

INSERT INTO consultorios (codigo_consultorio, nombre_consultorio, numero_piso, capacidad, id_sede)
VALUES ('CON007', 'CONSULTORIO DERMATOLOGÍA 103', 1, 1, 4);

INSERT INTO consultorios (codigo_consultorio, nombre_consultorio, numero_piso, capacidad, id_sede)
VALUES ('CON008', 'SALA DE PROCEDIMIENTOS 401', 4, 3, 5);

-- ============================================================
-- ESPECIALIDADES
-- ============================================================
INSERT INTO especialidades (codigo_especialidad, nombre_especialidad)
VALUES ('MG', 'MEDICINA GENERAL');
INSERT INTO especialidades (codigo_especialidad, nombre_especialidad)
VALUES ('CARD', 'CARDIOLOGÍA');
INSERT INTO especialidades (codigo_especialidad, nombre_especialidad)
VALUES ('PED', 'PEDIATRÍA');
INSERT INTO especialidades (codigo_especialidad, nombre_especialidad)
VALUES ('GIN', 'GINECOLOGÍA');
INSERT INTO especialidades (codigo_especialidad, nombre_especialidad)
VALUES ('ORT', 'ORTOPEDIA');

COMMIT;

-- ============================================================
-- VERIFICACIÓN DE DATOS INSERTADOS
-- ============================================================
SELECT 'DEPARTAMENTOS' tabla, COUNT(*) registros FROM departamentos
UNION ALL
SELECT 'MUNICIPIOS', COUNT(*) FROM municipios
UNION ALL
SELECT 'SEDES', COUNT(*) FROM sedes
UNION ALL
SELECT 'CONSULTORIOS', COUNT(*) FROM consultorios
UNION ALL
SELECT 'ESPECIALIDADES', COUNT(*) FROM especialidades;

-- FIN SCRIPT 04
