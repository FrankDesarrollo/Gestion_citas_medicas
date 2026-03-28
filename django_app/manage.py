#!/usr/bin/env python
"""
Utilidad de línea de comandos de Django para tareas administrativas.
Uso: python manage.py runserver
"""
import os
import sys


def main():
    """Punto de entrada principal."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_citas.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Activó el entorno virtual? "
            "¿Está Django instalado? (pip install -r requirements.txt)"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
