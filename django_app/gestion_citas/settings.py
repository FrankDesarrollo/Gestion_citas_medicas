"""
Configuración principal de Django
Sistema de Gestión de Citas Médicas
Arquitectura: MVT (Model - View - Template)
Base de datos: Oracle XE 18c
"""

import os
from pathlib import Path

# ===========================================================
# RUTAS BASE
# ===========================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ===========================================================
# SEGURIDAD
# ===========================================================
# ADVERTENCIA: En producción, esta clave debe ser secreta y
# almacenarse en variable de entorno
SECRET_KEY = 'django-insecure-citas-medicas-2024-electiva-oracle-xe18c'

# En producción cambiar a False
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ===========================================================
# APLICACIONES INSTALADAS
# ===========================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Aplicaciones del proyecto
    'citas',          # App principal del sistema de citas
    'usuarios',       # Gestión de usuarios y autenticación
]

# ===========================================================
# MIDDLEWARE
# ===========================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Archivos estáticos en producción
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Middleware personalizado para verificar roles
    'citas.middleware.RolMiddleware',
]

ROOT_URLCONF = 'gestion_citas.urls'

# ===========================================================
# CONFIGURACIÓN DE TEMPLATES (La "T" del MVT)
# ===========================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Templates globales del proyecto
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # Procesador personalizado para pasar el rol al template
                'citas.context_processors.rol_usuario',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_citas.wsgi.application'

# ===========================================================
# BASE DE DATOS - Oracle XE 18c
# Conexión dinámica según el ROL del usuario que hace login
# ===========================================================
# La conexión principal usa el usuario propietario del esquema.
# Cuando el usuario hace login con un rol, la vista cambia
# la conexión al usuario de BD correspondiente.
#
# USUARIOS DE BD POR ROL:
#   medico          → usr_medico      (SELECT + UPDATE en citas)
#   paciente        → usr_paciente    (SELECT propio)
#   administrativo  → usr_administrativo (CRUD completo)
#   auxiliar_medico → usr_auxiliar    (SELECT + INSERT + UPDATE)
# ===========================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:1521/XEPDB1',  # SID de la PDB en Oracle XE 18c
        'USER': 'app_citas',
        'PASSWORD': 'Citas2024#',
        'OPTIONS': {
            'threaded': True,
        },
        # Esquema propietario de las tablas
        'SCHEMA': 'APP_CITAS',
    }
}

# Configuraciones de conexión adicionales por rol
# Estas se usan en citas/db_router.py para conexión dinámica
DB_CONNECTIONS_POR_ROL = {
    'medico': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:1521/XEPDB1',
        'USER': 'usr_medico',
        'PASSWORD': 'Med2024#',
    },
    'paciente': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:1521/XEPDB1',
        'USER': 'usr_paciente',
        'PASSWORD': 'Pac2024#',
    },
    'administrativo': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:1521/XEPDB1',
        'USER': 'usr_administrativo',
        'PASSWORD': 'Adm2024#',
    },
    'auxiliar_medico': {
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'localhost:1521/XEPDB1',
        'USER': 'usr_auxiliar',
        'PASSWORD': 'Aux2024#',
    },
}

# ===========================================================
# VALIDACIÓN DE CONTRASEÑAS
# ===========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================================================
# INTERNACIONALIZACIÓN
# ===========================================================
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ===========================================================
# ARCHIVOS ESTÁTICOS (CSS, JavaScript, Imágenes)
# ===========================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================================================
# AUTENTICACIÓN
# ===========================================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/menu/'
LOGOUT_REDIRECT_URL = '/login/'

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'auth.User'

# Tiempo de sesión (en segundos): 8 horas
SESSION_COOKIE_AGE = 28800
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ===========================================================
# CLAVE PRIMARIA POR DEFECTO
# ===========================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================================================
# LOGGING (Para depuración y monitoreo)
# ===========================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'gestion_citas.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'citas': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
