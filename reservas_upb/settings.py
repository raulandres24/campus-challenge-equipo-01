"""
reservas_upb/settings.py
========================
Configuración principal de Django para el sistema de reservas de salas UPB con MongoDB.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Ruta base del proyecto (raíz del repositorio)
BASE_DIR = Path(__file__).resolve().parent.parent

# Clave secreta para desarrollo y firma de sesiones
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-f#df+-=zv6#nt!vtmsu6j9v1$^2wc@v*hqglzm&$-9uqkvs_wu',
)

# Modo de depuración
DEBUG = True

# Hosts permitidos para servir la aplicación
ALLOWED_HOSTS = ['*']

# Definición de aplicaciones instaladas
INSTALLED_APPS = [
    'django_mongodb_backend',
    'reservas.apps.MongoAdminConfig',
    'reservas.apps.MongoAuthConfig',
    'reservas.apps.MongoContentTypesConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'reservas.apps.ReservasConfig',
]

# Middlewares activos del ciclo de peticiones
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Módulo de enrutamiento principal
ROOT_URLCONF = 'reservas_upb.urls'

# Configuración del motor de plantillas HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Aplicación WSGI
WSGI_APPLICATION = 'reservas_upb.wsgi.application'

# Conexión a Base de Datos MongoDB
DATABASES = {
    "default": {
        "ENGINE": "django_mongodb_backend",
        "HOST": os.environ.get("MONGO_URI", "mongodb://127.0.0.1:27017/?replicaSet=rs0&directConnection=true"),
        "NAME": os.environ.get("MONGO_DB_NAME", "reservas_upb"),
    }
}

# Validadores de contraseñas de autenticación
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

# Internacionalización e idioma (Español / Bolivia)
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/La_Paz'
USE_I18N = True
USE_TZ = True

# Archivos estáticos (CSS, JavaScript, Imágenes)
STATIC_URL = 'static/'

# Configuración de correos en consola
MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}

# Tipo de campo autoincremental por defecto compatible con MongoDB ObjectId
DEFAULT_AUTO_FIELD = "django_mongodb_backend.fields.ObjectIdAutoField"

# Autenticación: un solo inicio de sesión (código + correo + contraseña) contra la base del
# proyecto (reservas/autenticacion.py). El padrón simulado solo se consulta al registrarse
# (reservas/padron.py). ModelBackend queda solo para el sitio /admin/ de Django.
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "reservas.autenticacion.CodigoCorreoBackend",
]

# Redirecciones de autenticación
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

