import os
import json
from pathlib import Path
import pymysql

pymysql.install_as_MySQLdb()

# 🔹 Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔹 Cargar configuración desde archivo JSON
datajson = {}
urlpa = os.path.join(BASE_DIR, "confi.json")
with open(urlpa, encoding="utf-8") as fh:
    datajson = json.load(fh)

# 🔹 Clave secreta de Django
SECRET_KEY = datajson["SECRET_KEY"]

# 🔹 Modo de depuración (cambiar a False en producción)
DEBUG = True

# 🔹 Hosts permitidos
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "modatours.com.pe",
    "christian-tong.github.io",
    "moda-tours-client-73mk8cbqn-christian-axell-tong-cruzs-projects.vercel.app",
    "djangomoda-master-production.up.railway.app",
]

# 🔹 Orígenes permitidos para CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://modatours.com.pe",
    "https://moda-tours-client-73mk8cbqn-christian-axell-tong-cruzs-projects.vercel.app",
    "https://djangomoda-master-production.up.railway.app",
]

# 🔹 Configuración de CORS
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
    "corsheaders",  # 🔹 Middleware para CORS
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # 🔹 Colocar CORS antes de cualquier otro middleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# 🔹 Configuración de CORS
CORS_ALLOW_ALL_ORIGINS = (
    True  # 🚀 Permitir todas las solicitudes (desactívalo en producción)
)
CORS_ALLOW_CREDENTIALS = True  # Permitir cookies y autenticación
CORS_ALLOW_HEADERS = ["*"]  # Permitir todos los encabezados
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]  # Métodos permitidos

# 🔹 Base de Datos
DATABASES = datajson.get("contabo", {})

# 🔹 Configuración de plantillas
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
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

# 🔹 Aplicación WSGI
WSGI_APPLICATION = "django_moda.wsgi.application"

# 🔹 Validaciones de contraseñas
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# 🔹 Configuración de idioma y zona horaria
LANGUAGE_CODE = "es-PE"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# 🔹 Configuración de archivos estáticos
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static_cdn")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media_cdn")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# 🔹 Configuración de usuario y autenticación
AUTH_USER_MODEL = "sistema.Usuario"
SESSION_COOKIE_AGE = 28800  # Expira en 8 horas
LOGIN_URL = "/account/login"

# 🔹 Paginación
NUM_PAGINATE = 20
