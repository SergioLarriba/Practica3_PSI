"""
Django settings for mychess project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv
import os 
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Cargar las variables de entorno desde el fichero .env 
load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-qhramw=p-0@-c8sijlz2c_#)vlfwevb1ny5j_-d$8oawo0pdy0'
if 'RENDER' in os.environ:
    SECRET_KEY = os.environ.get('SECRET_KEY')
else: 
    SECRET_KEY = os.environ.get('SECRET_KEY', 
                                default = 'django-insecure-qhramw=p-0@-c8sijlz2c_#)vlfwevb1ny5j_-d$8oawo0pdy0')

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.environ.get('DEBUG')
if 'DEBUG' in os.environ:
    DEBUG = os.environ.get('DEBUG').lower() in ['true', '1', 't']
else: 
    DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = ['localhost', '127.0.0.1'] 

# Application definition

INSTALLED_APPS = [
    'rest_framework', # api rest
    'rest_framework.authtoken', # api rest
    'djoser', # api authentification
    'models', # la aplicacione que yo he creado 
    'corsheaders', # vue -> para el cliente 
    'channels', # para el websocket
    'daphne', # para el websocket
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware', 
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASESS': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

ROOT_URLCONF = 'mychess.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

#Hacemos app asincrona
#WSGI_APPLICATION = 'mychess.wsgi.application'
ASGI_APPLICATION = 'mychess.asgi.application'    #Porque vamos a usar websockets

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Base de datos local 'p3_psi' -> alumnodb, alumnodb
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'p3_psi',
        'USER':'alumnodb', 
        'PASSWORD': 'alumnodb', 
        'HOST': 'localhost', 
        'PORT': '',
    }
}
"""
DATABASES = {}

LOCALPOSTGRES = os.environ.get('LOCALPOSTGRES')

if 'TESTING' in os.environ:
    databaseenv = dj_database_url.parse(LOCALPOSTGRES, conn_max_age=600)
else: 
    databaseenv = dj_database_url.config(conn_max_age=600, default=LOCALPOSTGRES)
    
DATABASES['default'] = databaseenv

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#Aniadido
# http://127.0.0.1:8080/api/v1/users/username 
DJOSER = {
    "USER_ID_FIELD": "username"
}
# Para vue 
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


AUTH_USER_MODEL = 'models.Player'


# Websocket
CHANNEL_LAYERS = { 
    'default': { 
        'BACKEND': 'channels.layers.InMemoryChannelLayer' 
    } 
}