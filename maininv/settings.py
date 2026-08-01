
import os
import sys
from pathlib import Path
from django.contrib.messages import constants as messages

# 1. GESTIÓN DE RUTAS (DESARROLLO VS EJECUTABLE)
BASE_DIR = Path(__file__).resolve().parent.parent

# Detectar si estamos en PyInstaller
IS_FROZEN = getattr(sys, 'frozen', False)

if IS_FROZEN:
    # Ruta interna (donde están los archivos comprimidos/extraídos: plantillas, estáticos)
    BASE_DIR_INTERNAL = Path(sys._MEIPASS)
    # Ruta externa (donde reside el .exe físicamente: base de datos, logs, media)
    BASE_DIR_EXTERNAL = Path(os.path.dirname(sys.executable))
else:
    BASE_DIR_INTERNAL = BASE_DIR
    BASE_DIR_EXTERNAL = BASE_DIR

# 2. SEGURIDAD
SECRET_KEY = 'django-insecure-^n(*t8l^sply8h-@xl-b9knqfs9c8aw(hpvmmoi7-f@p(+h^$&'
DEBUG = True  # Cambiar a False en producción final
ALLOWED_HOSTS = ['*', '0.0.0.0', 'localhost', '127.0.0.1']

# Configuración de Cookies para compatibilidad local
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['https://swift-pears-agree.loca.lt']

# 3. DEFINICIÓN DE APLICACIONES
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Apps del sistema
    'home', 'login', 'dashboard', 'productos', 'categorias',
    'unidades', 'proveedores', 'dependencias', 'directores',
    'entradas', 'salidas', 'estadisticas',
    'manuales', 'procedimientos', 'baselegal', 'formularios', 'protocolos',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'maininv.middleware.LoginRequiredMiddleware', 
]

ROOT_URLCONF = 'maininv.urls'

# 4. TEMPLATES (Búsqueda interna)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR_INTERNAL, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'maininv.wsgi.application'

# 5. BASE DE DATOS (Búsqueda externa junto al .exe)
DATABASES = {
    'default': {
'ENGINE': 'django.db.backends.sqlite3',
        'NAME': Path(sys.executable).parent / 'consejobd.sqlite3' if getattr(sys, 'frozen', False) else BASE_DIR / 'consejobd.sqlite3',    }
}

DATABASES = {
    'default': { # Esta sería 'concejosd'
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'concejosd.sqlite3',
    },
    'old': { # Esta sería 'concejosdold'
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'concejosdold.sqlite3',
    }
}



# 6. LOCALIZACIÓN
LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_L10N = True
USE_TZ = True
USE_THOUSAND_SEPARATOR = True 
DECIMAL_SEPARATOR = ',' 
THOUSAND_SEPARATOR = '.'

# 7. ARCHIVOS ESTÁTICOS Y MEDIA
STATIC_URL = '/static/'
# Si tienes una carpeta de estáticos en la raíz de tu proyecto:
STATICFILES_DIRS = [BASE_DIR / "static"]
# Los estáticos se sirven desde la carpeta interna en el EXE
STATICFILES_DIRS = [os.path.join(BASE_DIR_INTERNAL, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR_EXTERNAL, 'static_root')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR_EXTERNAL, 'media')

# 8. LOGS (Guardados en la carpeta externa junto al .exe)
LOG_FILE = os.path.join(BASE_DIR_EXTERNAL, 'app_errors.log')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# 9. OTROS
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-dark',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}




"""
Django settings for maininv project.

Generated by 'django-admin startproject' using Django 5.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/

from pathlib import Path
from django.contrib.messages import constants as messages

from dotenv import load_dotenv
import os
import sys

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# print(BASE_DIR)

# Detectar si estamos en PyInstaller
IS_FROZEN = getattr(sys, 'frozen', False)
if IS_FROZEN:
    # Ruta temporal de PyInstaller
    BASE_DIR_INTERNAL = Path(sys._MEIPASS) 
else:
    BASE_DIR_INTERNAL = BASE_DIR

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^n(*t8l^sply8h-@xl-b9knqfs9c8aw(hpvmmoi7-f@p(+h^$&'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SAMESITE = 'None'

ALLOWED_HOSTS = ['*', '0.0.0.0', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://swift-pears-agree.loca.lt',]

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-dark',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'home',
    'login',
    'dashboard',
    'productos',
    'categorias',
    'unidades',
    'almacenes',
    'proveedores',
    'clientes',
    'administrativos',
    'vendedores',
    'cobradores',
    'entradas',
    'salidas',
    'estadisticas', # Must be here
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Tu middleware (asegúrate de que la ruta sea correcta)
    'maininv.middleware.LoginRequiredMiddleware', 
]

ROOT_URLCONF = 'maininv.urls'

# =================================================================
# 1. CONFIGURACIÓN DE TEMPLATES (Para localizar plantillas HTML)
# =================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR_INTERNAL, 'templates')], # Usar la ruta interna
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'maininv.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# Detectar si estamos en el .exe o en desarrollo
# Busca esto en tu settings.py y reemplázalo:
if getattr(sys, 'frozen', False):
    # Si es el .exe, usamos la carpeta donde reside el ejecutable físicamente
    BASE_DIR_EXE = os.path.dirname(sys.executable)
else:
    # Si es desarrollo, usamos la carpeta del proyecto
    BASE_DIR_EXE = BASE_DIR

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR_EXE, 'invbolivar.sqlite3'),
    }
}
# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-ve'

TIME_ZONE = 'America/Caracas'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# 1. Necesario para activar los separadores
USE_THOUSAND_SEPARATOR = True 

# 2. Define el carácter del separador decimal (la coma)
DECIMAL_SEPARATOR = ',' 

# 3. Define el carácter del separador de miles (el punto)
THOUSAND_SEPARATOR = '.'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# settings.py (Verificado y Correcto)

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static_root'

# 🚨 NUEVA CONFIGURACIÓN PARA ARCHIVOS MEDIA (Imágenes) 🚨
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# STATICFILES_DIRS: Dónde Django busca estáticos en DESARROLLO.
# Esto incluye la carpeta 'static' en la raíz de tu proyecto.
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Ajusta la ruta a tu carpeta principal de estáticos
]

# 4. Configuración de archivos de medios (Opcional, pero recomendado)
# Si tu proyecto maneja archivos subidos por usuarios (imágenes de productos, etc.)

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        # Con esto, todas las llamadas a caché se ignorarán.
    }
}

# =================================================================
# CONFIGURACIÓN DE CORREO ELECTRÓNICO (EMAIL)
# =================================================================

# Backend de correo (si usas un servidor SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Por ejemplo, para Gmail:
EMAIL_HOST = 'smtp.gmail.com' 
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# MANEJO DE ERRORES DE REGISTROS
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR', # 🛑 SOLO grabará mensajes de nivel ERROR o superior
            'class': 'logging.FileHandler',
            'filename': 'app_errors.log', # 👈 RUTA DONDE SE GUARDA EL LOG
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        '': { # Logger raíz: captura todos los logs
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'django': { # Logs internos de Django
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Al final del archivo añade esto para que Django sepa a dónde ir
LOGIN_URL = 'login'

"""
