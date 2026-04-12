"""
MODELOS DEL SISTEMA DE CITAS MÉDICAS
Arquitectura MVT - La "M" (Model)
Estos modelos mapean las tablas del esquema APP_CITAS en Oracle XE 18c

IMPORTANTE PARA ESTUDIANTES:
- Cada clase Python = una tabla en Oracle
- Cada atributo = una columna
- Los Meta.db_table define el nombre exacto de la tabla en Oracle
- Los ForeignKey generan las restricciones FK en la BD
"""

import os
from django.db import models
from django.utils import timezone

# En producción Oracle → managed=False (las tablas las gestionan los scripts SQL).
# En dev local con USE_SQLITE=1 → managed=True para que migrate cree las tablas.
_DJANGO_MANAGED = os.environ.get('USE_SQLITE') == '1'


class Departamento(models.Model):
    """
    Mapea la tabla DEPARTAMENTOS del esquema APP_CITAS
    """
    # Django crea automáticamente 'id_departamento' si usamos 'id'
    id_departamento = models.AutoField(
        primary_key=True,
        db_column='ID_DEPARTAMENTO'
    )
    codigo_dane = models.CharField(
        max_length=2,
        unique=True,
        verbose_name='Código DANE',
        db_column='CODIGO_DANE'
    )
    nombre_departamento = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre Departamento',
        db_column='NOMBRE_DEPARTAMENTO'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )
    fecha_modificacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Modificación',
        db_column='FECHA_MODIFICACION'
    )
    usuario_creacion = models.CharField(
        max_length=50,
        verbose_name='Usuario Creación',
        db_column='USUARIO_CREACION'
    )

    class Meta:
        db_table = 'DEPARTAMENTOS'          # Nombre exacto en Oracle
        managed = _DJANGO_MANAGED                      # Django NO crea/modifica la tabla
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        ordering = ['nombre_departamento']

    def __str__(self):
        return f"{self.codigo_dane} - {self.nombre_departamento}"

    def save(self, *args, **kwargs):
        """Sobreescribir save para registrar fecha de modificación"""
        if self.pk:
            self.fecha_modificacion = timezone.now().date()
        super().save(*args, **kwargs)


class Municipio(models.Model):
    """
    Mapea la tabla MUNICIPIOS del esquema APP_CITAS
    """
    id_municipio = models.AutoField(
        primary_key=True,
        db_column='ID_MUNICIPIO'
    )
    codigo_dane = models.CharField(
        max_length=5,
        unique=True,
        verbose_name='Código DANE',
        db_column='CODIGO_DANE'
    )
    nombre_municipio = models.CharField(
        max_length=150,
        verbose_name='Nombre Municipio',
        db_column='NOMBRE_MUNICIPIO'
    )
    # ForeignKey: Relación con DEPARTAMENTOS
    # En Oracle se crea como FK: CONSTRAINT fk_mun_departamento
    id_departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,           # No permite borrar si tiene municipios
        db_column='ID_DEPARTAMENTO',
        verbose_name='Departamento',
        related_name='municipios'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )
    fecha_modificacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Modificación',
        db_column='FECHA_MODIFICACION'
    )
    usuario_creacion = models.CharField(
        max_length=50,
        verbose_name='Usuario Creación',
        db_column='USUARIO_CREACION'
    )

    class Meta:
        db_table = 'MUNICIPIOS'
        managed = _DJANGO_MANAGED
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        ordering = ['nombre_municipio']
        unique_together = [('codigo_dane',)]

    def __str__(self):
        return f"{self.codigo_dane} - {self.nombre_municipio}"

    def save(self, *args, **kwargs):
        if self.pk:
            self.fecha_modificacion = timezone.now().date()
        super().save(*args, **kwargs)


class Sede(models.Model):
    """
    Mapea la tabla SEDES del esquema APP_CITAS
    """
    id_sede = models.AutoField(
        primary_key=True,
        db_column='ID_SEDE'
    )
    codigo_sede = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Código Sede',
        db_column='CODIGO_SEDE'
    )
    nombre_sede = models.CharField(
        max_length=200,
        verbose_name='Nombre Sede',
        db_column='NOMBRE_SEDE'
    )
    direccion = models.CharField(
        max_length=300,
        verbose_name='Dirección',
        db_column='DIRECCION'
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Teléfono',
        db_column='TELEFONO'
    )
    email = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Email',
        db_column='EMAIL'
    )
    # FK hacia MUNICIPIOS
    id_municipio = models.ForeignKey(
        Municipio,
        on_delete=models.PROTECT,
        db_column='ID_MUNICIPIO',
        verbose_name='Municipio',
        related_name='sedes'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )
    fecha_modificacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Modificación',
        db_column='FECHA_MODIFICACION'
    )
    usuario_creacion = models.CharField(
        max_length=50,
        verbose_name='Usuario Creación',
        db_column='USUARIO_CREACION'
    )

    class Meta:
        db_table = 'SEDES'
        managed = _DJANGO_MANAGED
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
        ordering = ['nombre_sede']

    def __str__(self):
        return f"{self.codigo_sede} - {self.nombre_sede}"

    def save(self, *args, **kwargs):
        if self.pk:
            self.fecha_modificacion = timezone.now().date()
        super().save(*args, **kwargs)


class Consultorio(models.Model):
    """
    Mapea la tabla CONSULTORIOS del esquema APP_CITAS
    """
    id_consultorio = models.AutoField(
        primary_key=True,
        db_column='ID_CONSULTORIO'
    )
    codigo_consultorio = models.CharField(
        max_length=10,
        verbose_name='Código Consultorio',
        db_column='CODIGO_CONSULTORIO'
    )
    nombre_consultorio = models.CharField(
        max_length=200,
        verbose_name='Nombre Consultorio',
        db_column='NOMBRE_CONSULTORIO'
    )
    numero_piso = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Número de Piso',
        db_column='NUMERO_PISO'
    )
    capacidad = models.IntegerField(
        default=1,
        verbose_name='Capacidad',
        db_column='CAPACIDAD'
    )
    # FK hacia SEDES
    id_sede = models.ForeignKey(
        Sede,
        on_delete=models.PROTECT,
        db_column='ID_SEDE',
        verbose_name='Sede',
        related_name='consultorios'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )
    fecha_modificacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Modificación',
        db_column='FECHA_MODIFICACION'
    )
    usuario_creacion = models.CharField(
        max_length=50,
        verbose_name='Usuario Creación',
        db_column='USUARIO_CREACION'
    )

    class Meta:
        db_table = 'CONSULTORIOS'
        managed = _DJANGO_MANAGED
        verbose_name = 'Consultorio'
        verbose_name_plural = 'Consultorios'
        ordering = ['id_sede', 'codigo_consultorio']
        unique_together = [('codigo_consultorio', 'id_sede')]

    def __str__(self):
        return f"{self.codigo_consultorio} - {self.nombre_consultorio} ({self.id_sede})"

    def save(self, *args, **kwargs):
        if self.pk:
            self.fecha_modificacion = timezone.now().date()
        super().save(*args, **kwargs)


# ===========================================================
# MODELOS ADICIONALES: Especialidades, Personas, Médicos,
# Pacientes, Citas Médicas y Auditoría
# ===========================================================

class Especialidad(models.Model):
    """
    Mapea la tabla ESPECIALIDADES del esquema APP_CITAS
    """
    id_especialidad = models.AutoField(
        primary_key=True,
        db_column='ID_ESPECIALIDAD'
    )
    codigo_especialidad = models.CharField(
        max_length=10,
        unique=True,
        verbose_name='Código Especialidad',
        db_column='CODIGO_ESPECIALIDAD'
    )
    nombre_especialidad = models.CharField(
        max_length=150,
        verbose_name='Nombre Especialidad',
        db_column='NOMBRE_ESPECIALIDAD'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )

    class Meta:
        db_table = 'ESPECIALIDADES'
        managed = _DJANGO_MANAGED
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        ordering = ['nombre_especialidad']

    def __str__(self):
        return f"{self.codigo_especialidad} - {self.nombre_especialidad}"


class Persona(models.Model):
    """
    Mapea la tabla PERSONAS del esquema APP_CITAS
    Base para médicos y pacientes.
    """
    id_persona = models.AutoField(
        primary_key=True,
        db_column='ID_PERSONA'
    )
    tipo_documento = models.CharField(
        max_length=3,
        verbose_name='Tipo Documento',
        choices=[
            ('CC', 'Cédula de Ciudadanía'),
            ('TI', 'Tarjeta de Identidad'),
            ('CE', 'Cédula de Extranjería'),
            ('PAS', 'Pasaporte'),
            ('RC', 'Registro Civil'),
        ],
        db_column='TIPO_DOCUMENTO'
    )
    numero_documento = models.CharField(
        max_length=20,
        verbose_name='Número Documento',
        db_column='NUMERO_DOCUMENTO'
    )
    primer_nombre = models.CharField(
        max_length=80,
        verbose_name='Primer Nombre',
        db_column='PRIMER_NOMBRE'
    )
    segundo_nombre = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Segundo Nombre',
        db_column='SEGUNDO_NOMBRE'
    )
    primer_apellido = models.CharField(
        max_length=80,
        verbose_name='Primer Apellido',
        db_column='PRIMER_APELLIDO'
    )
    segundo_apellido = models.CharField(
        max_length=80,
        null=True,
        blank=True,
        verbose_name='Segundo Apellido',
        db_column='SEGUNDO_APELLIDO'
    )
    fecha_nacimiento = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Nacimiento',
        db_column='FECHA_NACIMIENTO'
    )
    sexo = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')],
        verbose_name='Sexo',
        db_column='SEXO'
    )
    email = models.EmailField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Email',
        db_column='EMAIL'
    )
    telefono = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Teléfono',
        db_column='TELEFONO'
    )
    id_municipio = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='ID_MUNICIPIO',
        verbose_name='Municipio'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )
    fecha_modificacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Modificación',
        db_column='FECHA_MODIFICACION'
    )
    usuario_creacion = models.CharField(
        max_length=50,
        verbose_name='Usuario Creación',
        db_column='USUARIO_CREACION'
    )

    class Meta:
        db_table = 'PERSONAS'
        managed = _DJANGO_MANAGED
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['primer_apellido', 'primer_nombre']
        unique_together = [('tipo_documento', 'numero_documento')]

    def __str__(self):
        nombre_completo = f"{self.primer_apellido}"
        if self.segundo_apellido:
            nombre_completo += f" {self.segundo_apellido}"
        nombre_completo += f", {self.primer_nombre}"
        if self.segundo_nombre:
            nombre_completo += f" {self.segundo_nombre}"
        return nombre_completo

    def save(self, *args, **kwargs):
        if self.pk:
            self.fecha_modificacion = timezone.now().date()
        super().save(*args, **kwargs)


class Medico(models.Model):
    """
    Mapea la tabla MEDICOS del esquema APP_CITAS
    """
    id_medico = models.AutoField(
        primary_key=True,
        db_column='ID_MEDICO'
    )
    id_persona = models.OneToOneField(
        Persona,
        on_delete=models.PROTECT,
        db_column='ID_PERSONA',
        verbose_name='Persona',
        related_name='medico'
    )
    id_especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.PROTECT,
        db_column='ID_ESPECIALIDAD',
        verbose_name='Especialidad',
        related_name='medicos'
    )
    numero_registro = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Nº Registro Médico',
        db_column='NUMERO_REGISTRO'
    )
    tarifa_consulta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Tarifa Consulta',
        db_column='TARIFA_CONSULTA'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )

    class Meta:
        db_table = 'MEDICOS'
        managed = _DJANGO_MANAGED
        verbose_name = 'Médico'
        verbose_name_plural = 'Médicos'
        ordering = ['id_persona__primer_apellido']

    def __str__(self):
        return f"Dr(a). {self.id_persona} - {self.id_especialidad}"

    @property
    def nombre_completo(self):
        return str(self.id_persona)


class Paciente(models.Model):
    """
    Mapea la tabla PACIENTES del esquema APP_CITAS
    """
    id_paciente = models.AutoField(
        primary_key=True,
        db_column='ID_PACIENTE'
    )
    id_persona = models.OneToOneField(
        Persona,
        on_delete=models.PROTECT,
        db_column='ID_PERSONA',
        verbose_name='Persona',
        related_name='paciente'
    )
    numero_historia = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Nº Historia Clínica',
        db_column='NUMERO_HISTORIA'
    )
    tipo_afiliacion = models.CharField(
        max_length=20,
        default='CONTRIBUTIVO',
        choices=[
            ('CONTRIBUTIVO', 'Contributivo'),
            ('SUBSIDIADO', 'Subsidiado'),
            ('VINCULADO', 'Vinculado'),
            ('PARTICULAR', 'Particular'),
        ],
        verbose_name='Tipo Afiliación',
        db_column='TIPO_AFILIACION'
    )
    eps = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='EPS',
        db_column='EPS'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )

    class Meta:
        db_table = 'PACIENTES'
        managed = _DJANGO_MANAGED
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['id_persona__primer_apellido']

    def __str__(self):
        return f"{self.id_persona} (HC: {self.numero_historia})"

    @property
    def nombre_completo(self):
        return str(self.id_persona)


class CitaMedica(models.Model):
    """
    Mapea la tabla CITAS_MEDICAS del esquema APP_CITAS
    Es el modelo central del sistema.
    """
    ESTADO_CHOICES = [
        ('PROGRAMADA', 'Programada'),
        ('CONFIRMADA', 'Confirmada'),
        ('ATENDIDA', 'Atendida'),
        ('CANCELADA', 'Cancelada'),
        ('NO_ASISTIO', 'No Asistió'),
    ]

    id_cita = models.AutoField(
        primary_key=True,
        db_column='ID_CITA'
    )
    numero_cita = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Nº Cita',
        db_column='NUMERO_CITA'
    )
    id_paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        db_column='ID_PACIENTE',
        verbose_name='Paciente',
        related_name='citas'
    )
    id_medico = models.ForeignKey(
        Medico,
        on_delete=models.PROTECT,
        db_column='ID_MEDICO',
        verbose_name='Médico',
        related_name='citas'
    )
    id_consultorio = models.ForeignKey(
        Consultorio,
        on_delete=models.PROTECT,
        db_column='ID_CONSULTORIO',
        verbose_name='Consultorio',
        related_name='citas'
    )
    fecha_cita = models.DateField(
        verbose_name='Fecha de la Cita',
        db_column='FECHA_CITA'
    )
    hora_inicio = models.CharField(
        max_length=5,
        verbose_name='Hora Inicio',
        db_column='HORA_INICIO'
    )
    hora_fin = models.CharField(
        max_length=5,
        verbose_name='Hora Fin',
        db_column='HORA_FIN'
    )
    estado = models.CharField(
        max_length=20,
        default='PROGRAMADA',
        choices=ESTADO_CHOICES,
        verbose_name='Estado',
        db_column='ESTADO'
    )
    motivo_consulta = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name='Motivo de Consulta',
        db_column='MOTIVO_CONSULTA'
    )
    observaciones = models.TextField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name='Observaciones',
        db_column='OBSERVACIONES'
    )
    activo = models.CharField(
        max_length=1,
        default='S',
        choices=[('S', 'Activo'), ('N', 'Inactivo')],
        verbose_name='Estado',
        db_column='ACTIVO'
    )
    fecha_creacion = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha Creación',
        db_column='FECHA_CREACION'
    )
    fecha_modificacion = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha Modificación',
        db_column='FECHA_MODIFICACION'
    )
    usuario_creacion = models.CharField(
        max_length=50,
        verbose_name='Usuario Creación',
        db_column='USUARIO_CREACION'
    )

    class Meta:
        db_table = 'CITAS_MEDICAS'
        managed = _DJANGO_MANAGED
        verbose_name = 'Cita Médica'
        verbose_name_plural = 'Citas Médicas'
        ordering = ['-fecha_cita', '-hora_inicio']

    def __str__(self):
        return (
            f"Cita #{self.numero_cita} - "
            f"{self.id_paciente} con {self.id_medico} "
            f"el {self.fecha_cita} a las {self.hora_inicio}"
        )

    def save(self, *args, **kwargs):
        if self.pk:
            self.fecha_modificacion = timezone.now().date()
        super().save(*args, **kwargs)


class AuditoriaAccion(models.Model):
    """
    Mapea la tabla AUDITORIA_ACCIONES del esquema APP_CITAS
    Solo lectura — se llena vía triggers de Oracle.
    """
    ACCION_CHOICES = [
        ('INSERT', 'Inserción'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('SELECT', 'Consulta'),
    ]

    id_auditoria = models.AutoField(
        primary_key=True,
        db_column='ID_AUDITORIA'
    )
    tabla_afectada = models.CharField(
        max_length=50,
        verbose_name='Tabla Afectada',
        db_column='TABLA_AFECTADA'
    )
    accion = models.CharField(
        max_length=10,
        choices=ACCION_CHOICES,
        verbose_name='Acción',
        db_column='ACCION'
    )
    id_registro = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='ID Registro',
        db_column='ID_REGISTRO'
    )
    usuario_bd = models.CharField(
        max_length=50,
        verbose_name='Usuario BD',
        db_column='USUARIO_BD'
    )
    rol_activo = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Rol Activo',
        db_column='ROL_ACTIVO'
    )
    datos_anteriores = models.TextField(
        null=True,
        blank=True,
        verbose_name='Datos Anteriores',
        db_column='DATOS_ANTERIORES'
    )
    datos_nuevos = models.TextField(
        null=True,
        blank=True,
        verbose_name='Datos Nuevos',
        db_column='DATOS_NUEVOS'
    )
    fecha_accion = models.DateTimeField(
        verbose_name='Fecha Acción',
        db_column='FECHA_ACCION'
    )
    ip_cliente = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='IP Cliente',
        db_column='IP_CLIENTE'
    )

    class Meta:
        db_table = 'AUDITORIA_ACCIONES'
        managed = _DJANGO_MANAGED
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-fecha_accion']

    def __str__(self):
        return f"{self.accion} en {self.tabla_afectada} por {self.usuario_bd} ({self.fecha_accion})"
