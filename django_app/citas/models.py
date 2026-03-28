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

from django.db import models
from django.utils import timezone


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
        managed = False                      # Django NO crea/modifica la tabla
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
        managed = False
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
        managed = False
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
        managed = False
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
