import os
import json
from pathlib import Path
import pymysql

pymysql.install_as_MySQLdb()


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
    "modatours.com.pe",
    "christian-tong.github.io/moda-tours-client-v2",
    "djangomoda-master-production.up.railway.app",
    "*",
]

CSRF_TRUSTED_ORIGINS = [
    "http://*",
    "https://djangomoda-master-production.up.railway.app",
]

ORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://christian-tong.github.io",
    "https://moda-tours-client-73mk8cbqn-christian-axell-tong-cruzs-projects.vercel.app",
    "https://modatours.com.pe",
    "https://djangomoda-master-production.up.railway.app",
]

CORS_ALLOW_CREDENTIALS = True  # Permitir credenciales (cookies, tokens, etc.)
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]  # Métodos permitidos
CORS_ALLOW_HEADERS = ["*"]  # Permitir todos los encabezados


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
    "apps.catalogoSunat",
    "apps.persona",
    "apps.empresa",
    "apps.venta",
    "apps.viaje",
    "apps.envio",
    "apps.caja",
    "apps.facturacion",
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
DATABASES = datajson.get("contabo", {})


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
