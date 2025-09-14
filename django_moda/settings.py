# BACKEND django_moda/settings.py

import os
import json
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
datajson = {}

urlpa = os.path.join(BASE_DIR, "confi.json")
with open(urlpa, encoding="utf-8") as fh:
    datajson = json.load(fh)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = datajson["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "192.168.0.102",
    "modatours.com.pe",
    "cliente-notificaciones-production.up.railway.app",
    "modatours.agency",
]

ORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (
    "https://modatours.colesms.com",
    "https://cliente-notificaciones-production.up.railway.app",
    "https://www.modatours.agency",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://192.168.0.102:3000",
)

# Cookies
SESSION_COOKIE_NAME = "sessionid"
SESSION_COOKIE_DOMAIN = None  # 👈 Necesario para que funcione en localhost
SESSION_COOKIE_SAMESITE = "Lax"  # 👈 mejor que "None" en local
SESSION_COOKIE_SECURE = False  # 👈 True solo en producción HTTPS

CSRF_COOKIE_NAME = "csrftoken"
CSRF_COOKIE_DOMAIN = None
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = False  # 👈 True solo en producción HTTPS

APPEND_SLASH = True

# Application definition
IMPORT_EXPORT_USE_TRANSACTIONS = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_yasg",
    "materializecssform",
    "import_export",
    "apps.sistema",
    "apps.sistema.api.apps.SistemaApiConfig",
    "apps.empresa.api.apps.EmpresaApiConfig",
    "apps.catalogoSunat",
    "apps.persona",
    "apps.empresa",
    "apps.venta",
    "apps.viaje",
    "apps.envio",
    "apps.caja",
    "apps.facturacion",
    "apps.notificaciones",
    "apps.notificaciones.api",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_moda.urls"

# REST Framework Config
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "django_moda.utils.authentication.CsrfExemptSessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {
                "my_templatetag": "templatetags.filtros_plantillas",
            },
        },
    },
]

WSGI_APPLICATION = "django_moda.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite',
    }
}"""
DATABASES = datajson["contabo"]

# DATABASES = DATABASES_local if servir_bd else  DATABASES_produccion
# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "es-PE"

TIME_ZONE = "America/Lima"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static_cdn")
# STATIC_ROOT = os.path.join(BASE_DIR, "static/")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media_cdn")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "sistema.Usuario"

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

SESSION_COOKIE_AGE = 28800  # sesion expira cada 8 horas

LOGIN_URL = "/account/login"

NUM_PAGINATE = 20

# EMAIL

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "christian.tongcruz96@gmail.com"
EMAIL_HOST_PASSWORD = "xtjk dahw gudz veax"
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
