"""
FORMULARIOS DEL SISTEMA DE CITAS MÉDICAS
Arquitectura MVT - Parte del "V" (View)
Los formularios validan los datos antes de guardarlos en Oracle
"""

from django import forms
from .models import (
    Departamento, Municipio, Sede, Consultorio,
    Especialidad, Persona, Medico, Paciente, CitaMedica
)


# ===========================================================
# FORMULARIO: DEPARTAMENTOS
# ===========================================================
class DepartamentoForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Departamentos.
    El campo usuario_creacion se asigna automáticamente en la vista.
    """
    class Meta:
        model = Departamento
        fields = ['codigo_dane', 'nombre_departamento', 'activo']
        widgets = {
            'codigo_dane': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 05',
                'maxlength': '2',
                'style': 'text-transform: uppercase;'
            }),
            'nombre_departamento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: ANTIOQUIA',
                'style': 'text-transform: uppercase;'
            }),
            'activo': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'codigo_dane': 'Código DANE (2 dígitos)',
            'nombre_departamento': 'Nombre del Departamento',
            'activo': 'Estado',
        }

    def clean_codigo_dane(self):
        """Validar que el código DANE sea numérico y tenga 2 dígitos"""
        codigo = self.cleaned_data.get('codigo_dane', '').strip().upper()
        if not codigo.isdigit():
            raise forms.ValidationError('El código DANE debe contener solo dígitos.')
        if len(codigo) != 2:
            raise forms.ValidationError('El código DANE debe tener exactamente 2 dígitos.')
        return codigo

    def clean_nombre_departamento(self):
        return self.cleaned_data.get('nombre_departamento', '').strip().upper()


# ===========================================================
# FORMULARIO: MUNICIPIOS
# ===========================================================
class MunicipioForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Municipios.
    Incluye un selector dinámico de departamentos.
    """
    class Meta:
        model = Municipio
        fields = ['codigo_dane', 'nombre_municipio', 'id_departamento', 'activo']
        widgets = {
            'codigo_dane': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 05001',
                'maxlength': '5',
            }),
            'nombre_municipio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: MEDELLÍN',
                'style': 'text-transform: uppercase;'
            }),
            'id_departamento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'activo': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'codigo_dane': 'Código DANE (5 dígitos)',
            'nombre_municipio': 'Nombre del Municipio',
            'id_departamento': 'Departamento',
            'activo': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar departamentos activos en el selector
        self.fields['id_departamento'].queryset = Departamento.objects.filter(
            activo='S'
        ).order_by('nombre_departamento')
        self.fields['id_departamento'].empty_label = '-- Seleccione un departamento --'

    def clean_codigo_dane(self):
        codigo = self.cleaned_data.get('codigo_dane', '').strip()
        if not codigo.isdigit():
            raise forms.ValidationError('El código DANE debe contener solo dígitos.')
        if len(codigo) != 5:
            raise forms.ValidationError('El código DANE del municipio debe tener 5 dígitos.')
        return codigo

    def clean_nombre_municipio(self):
        return self.cleaned_data.get('nombre_municipio', '').strip().upper()


# ===========================================================
# FORMULARIO: SEDES
# ===========================================================
class SedeForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Sedes de la institución médica.
    """
    class Meta:
        model = Sede
        fields = [
            'codigo_sede', 'nombre_sede', 'direccion',
            'telefono', 'email', 'id_municipio', 'activo'
        ]
        widgets = {
            'codigo_sede': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: SED001',
                'maxlength': '10',
                'style': 'text-transform: uppercase;'
            }),
            'nombre_sede': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: SEDE PRINCIPAL BOGOTÁ',
                'style': 'text-transform: uppercase;'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Cra. 15 # 90-12, Bogotá'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 6014568900',
                'maxlength': '20'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: sede@clinica.com'
            }),
            'id_municipio': forms.Select(attrs={
                'class': 'form-select'
            }),
            'activo': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'codigo_sede': 'Código de Sede',
            'nombre_sede': 'Nombre de la Sede',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'id_municipio': 'Municipio',
            'activo': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_municipio'].queryset = Municipio.objects.filter(
            activo='S'
        ).select_related('id_departamento').order_by('nombre_municipio')
        self.fields['id_municipio'].empty_label = '-- Seleccione un municipio --'
        # Campos no requeridos
        self.fields['telefono'].required = False
        self.fields['email'].required = False

    def clean_codigo_sede(self):
        return self.cleaned_data.get('codigo_sede', '').strip().upper()

    def clean_nombre_sede(self):
        return self.cleaned_data.get('nombre_sede', '').strip().upper()


# ===========================================================
# FORMULARIO: CONSULTORIOS
# ===========================================================
class ConsultorioForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Consultorios.
    Cada consultorio pertenece a una sede específica.
    """
    class Meta:
        model = Consultorio
        fields = [
            'codigo_consultorio', 'nombre_consultorio',
            'numero_piso', 'capacidad', 'id_sede', 'activo'
        ]
        widgets = {
            'codigo_consultorio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CON001',
                'maxlength': '10',
                'style': 'text-transform: uppercase;'
            }),
            'nombre_consultorio': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CONSULTORIO MEDICINA GENERAL 101',
                'style': 'text-transform: uppercase;'
            }),
            'numero_piso': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '20',
                'placeholder': 'Ej: 1'
            }),
            'capacidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '50',
                'placeholder': 'Ej: 1'
            }),
            'id_sede': forms.Select(attrs={
                'class': 'form-select'
            }),
            'activo': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'codigo_consultorio': 'Código del Consultorio',
            'nombre_consultorio': 'Nombre del Consultorio',
            'numero_piso': 'Número de Piso',
            'capacidad': 'Capacidad (pacientes simultáneos)',
            'id_sede': 'Sede',
            'activo': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_sede'].queryset = Sede.objects.filter(
            activo='S'
        ).order_by('nombre_sede')
        self.fields['id_sede'].empty_label = '-- Seleccione una sede --'
        self.fields['numero_piso'].required = False

    def clean_codigo_consultorio(self):
        return self.cleaned_data.get('codigo_consultorio', '').strip().upper()

    def clean_nombre_consultorio(self):
        return self.cleaned_data.get('nombre_consultorio', '').strip().upper()

    def clean_capacidad(self):
        capacidad = self.cleaned_data.get('capacidad')
        if capacidad is not None and capacidad < 1:
            raise forms.ValidationError('La capacidad debe ser al menos 1.')
        return capacidad


# ===========================================================
# FORMULARIO: ESPECIALIDADES
# ===========================================================
class EspecialidadForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Especialidades Médicas.
    """
    class Meta:
        model = Especialidad
        fields = ['codigo_especialidad', 'nombre_especialidad', 'activo']
        widgets = {
            'codigo_especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CARD',
                'maxlength': '10',
                'style': 'text-transform: uppercase;'
            }),
            'nombre_especialidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CARDIOLOGÍA',
                'style': 'text-transform: uppercase;'
            }),
            'activo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'codigo_especialidad': 'Código de Especialidad',
            'nombre_especialidad': 'Nombre de la Especialidad',
            'activo': 'Estado',
        }

    def clean_codigo_especialidad(self):
        return self.cleaned_data.get('codigo_especialidad', '').strip().upper()

    def clean_nombre_especialidad(self):
        return self.cleaned_data.get('nombre_especialidad', '').strip().upper()


# ===========================================================
# FORMULARIO: PERSONA (base para Médico y Paciente)
# ===========================================================
class PersonaForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Personas (datos base).
    Se usa como formulario incrustado dentro de MedicoForm y PacienteForm.
    """
    class Meta:
        model = Persona
        fields = [
            'tipo_documento', 'numero_documento',
            'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido',
            'fecha_nacimiento', 'sexo',
            'email', 'telefono', 'id_municipio', 'activo'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-select'}),
            'numero_documento': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: 1234567890',
                'maxlength': '20'
            }),
            'primer_nombre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Primer nombre',
                'style': 'text-transform: uppercase;'
            }),
            'segundo_nombre': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Segundo nombre (opcional)',
                'style': 'text-transform: uppercase;'
            }),
            'primer_apellido': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Primer apellido',
                'style': 'text-transform: uppercase;'
            }),
            'segundo_apellido': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Segundo apellido (opcional)',
                'style': 'text-transform: uppercase;'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: 3001234567'
            }),
            'id_municipio': forms.Select(attrs={'class': 'form-select'}),
            'activo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'tipo_documento': 'Tipo de Documento',
            'numero_documento': 'Número de Documento',
            'primer_nombre': 'Primer Nombre',
            'segundo_nombre': 'Segundo Nombre',
            'primer_apellido': 'Primer Apellido',
            'segundo_apellido': 'Segundo Apellido',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'sexo': 'Sexo',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'id_municipio': 'Municipio de Residencia',
            'activo': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_municipio'].queryset = Municipio.objects.filter(
            activo='S'
        ).order_by('nombre_municipio')
        self.fields['id_municipio'].empty_label = '-- Seleccione un municipio --'
        self.fields['segundo_nombre'].required = False
        self.fields['segundo_apellido'].required = False
        self.fields['telefono'].required = False
        self.fields['email'].required = False
        self.fields['fecha_nacimiento'].required = False
        self.fields['sexo'].required = False

    def clean_numero_documento(self):
        return self.cleaned_data.get('numero_documento', '').strip()

    def clean_primer_nombre(self):
        return self.cleaned_data.get('primer_nombre', '').strip().upper()

    def clean_segundo_nombre(self):
        val = self.cleaned_data.get('segundo_nombre', '')
        return val.strip().upper() if val else ''

    def clean_primer_apellido(self):
        return self.cleaned_data.get('primer_apellido', '').strip().upper()

    def clean_segundo_apellido(self):
        val = self.cleaned_data.get('segundo_apellido', '')
        return val.strip().upper() if val else ''


# ===========================================================
# FORMULARIO: MÉDICO (incluye datos de Persona inline)
# ===========================================================
class MedicoForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Médicos.
    Incluye campos de la especialidad. La Persona se crea/edita por separado.
    """
    class Meta:
        model = Medico
        fields = ['id_especialidad', 'numero_registro', 'tarifa_consulta', 'activo']
        widgets = {
            'id_especialidad': forms.Select(attrs={'class': 'form-select'}),
            'numero_registro': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: RM-12345',
                'maxlength': '20', 'style': 'text-transform: uppercase;'
            }),
            'tarifa_consulta': forms.NumberInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: 150000.00',
                'min': '0', 'step': '0.01'
            }),
            'activo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'id_especialidad': 'Especialidad',
            'numero_registro': 'Nº Registro Médico',
            'tarifa_consulta': 'Tarifa de Consulta ($)',
            'activo': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_especialidad'].queryset = Especialidad.objects.filter(
            activo='S'
        ).order_by('nombre_especialidad')
        self.fields['id_especialidad'].empty_label = '-- Seleccione una especialidad --'
        self.fields['tarifa_consulta'].required = False


# ===========================================================
# FORMULARIO: PACIENTE (incluye datos de Persona inline)
# ===========================================================
class PacienteForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Pacientes.
    La Persona se crea/edita por separado.
    """
    class Meta:
        model = Paciente
        fields = ['numero_historia', 'tipo_afiliacion', 'eps', 'activo']
        widgets = {
            'numero_historia': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: HC-00001',
                'maxlength': '20', 'style': 'text-transform: uppercase;'
            }),
            'tipo_afiliacion': forms.Select(attrs={'class': 'form-select'}),
            'eps': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: SANITAS'
            }),
            'activo': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'numero_historia': 'Nº Historia Clínica',
            'tipo_afiliacion': 'Tipo de Afiliación',
            'eps': 'EPS',
            'activo': 'Estado',
        }

    def clean_numero_historia(self):
        return self.cleaned_data.get('numero_historia', '').strip().upper()

    def clean_eps(self):
        val = self.cleaned_data.get('eps', '')
        return val.strip().upper() if val else ''


# ===========================================================
# FORMULARIO: CITA MÉDICA
# ===========================================================
class CitaMedicaForm(forms.ModelForm):
    """
    Formulario para Crear y Editar Citas Médicas.
    """
    class Meta:
        model = CitaMedica
        fields = [
            'id_paciente', 'id_medico', 'id_consultorio',
            'fecha_cita', 'hora_inicio', 'hora_fin',
            'motivo_consulta', 'estado'
        ]
        widgets = {
            'id_paciente': forms.Select(attrs={'class': 'form-select'}),
            'id_medico': forms.Select(attrs={'class': 'form-select'}),
            'id_consultorio': forms.Select(attrs={'class': 'form-select'}),
            'fecha_cita': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control', 'type': 'time',
                'placeholder': 'HH:MM'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control', 'type': 'time',
                'placeholder': 'HH:MM'
            }),
            'motivo_consulta': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Describa el motivo de la consulta...'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'id_paciente': 'Paciente',
            'id_medico': 'Médico',
            'id_consultorio': 'Consultorio',
            'fecha_cita': 'Fecha de la Cita',
            'hora_inicio': 'Hora Inicio',
            'hora_fin': 'Hora Fin',
            'motivo_consulta': 'Motivo de Consulta',
            'estado': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo pacientes y médicos activos
        self.fields['id_paciente'].queryset = Paciente.objects.filter(
            activo='S'
        ).select_related('id_persona').order_by('id_persona__primer_apellido')
        self.fields['id_paciente'].empty_label = '-- Seleccione un paciente --'

        self.fields['id_medico'].queryset = Medico.objects.filter(
            activo='S'
        ).select_related('id_persona', 'id_especialidad').order_by(
            'id_persona__primer_apellido'
        )
        self.fields['id_medico'].empty_label = '-- Seleccione un médico --'

        self.fields['id_consultorio'].queryset = Consultorio.objects.filter(
            activo='S'
        ).select_related('id_sede').order_by('id_sede__nombre_sede')
        self.fields['id_consultorio'].empty_label = '-- Seleccione un consultorio --'

    def clean_motivo_consulta(self):
        val = self.cleaned_data.get('motivo_consulta', '')
        return val.strip() if val else ''

    def clean_hora_inicio(self):
        hora = self.cleaned_data.get('hora_inicio', '')
        if hora and len(hora) < 5:
            raise forms.ValidationError('La hora debe tener formato HH:MM (ej: 08:00).')
        return hora

    def clean_hora_fin(self):
        hora = self.cleaned_data.get('hora_fin', '')
        if hora and len(hora) < 5:
            raise forms.ValidationError('La hora debe tener formato HH:MM (ej: 08:30).')
        return hora


# ===========================================================
# FORMULARIO: CAMBIO DE ESTADO DE CITA (para médico/administrativo)
# ===========================================================
class CitaEstadoForm(forms.ModelForm):
    """
    Formulario mínimo solo para cambiar el estado de una cita.
    """
    class Meta:
        model = CitaMedica
        fields = ['estado', 'observaciones']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Observaciones sobre el cambio de estado...'
            }),
        }
        labels = {
            'estado': 'Nuevo Estado',
            'observaciones': 'Observaciones',
        }
