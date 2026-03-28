"""
PROCESADORES DE CONTEXTO
Sistema de Gestión de Citas Médicas

Los context processors hacen que ciertas variables estén
disponibles en TODOS los templates automáticamente.
"""


def rol_usuario(request):
    """
    Hace disponible el rol del usuario en todos los templates.
    Se usa así en cualquier template:
        {{ rol }}
        {% if rol == 'administrativo' %}...{% endif %}
    """
    return {
        'rol': request.session.get('rol_usuario', ''),
        'nombre_usuario': request.user.get_full_name() if request.user.is_authenticated else '',
        'es_admin': request.session.get('rol_usuario', '') == 'administrativo',
        'es_medico': request.session.get('rol_usuario', '') == 'medico',
        'es_paciente': request.session.get('rol_usuario', '') == 'paciente',
        'es_auxiliar': request.session.get('rol_usuario', '') == 'auxiliar_medico',
    }
