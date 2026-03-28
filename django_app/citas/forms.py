"""
FORMULARIOS DEL SISTEMA DE CITAS MÉDICAS
Arquitectura MVT - Parte del "V" (View)
Los formularios validan los datos antes de guardarlos en Oracle
"""

from django import forms
from .models import Departamento, Municipio, Sede, Consultorio


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
