"""Configuración del cuadro de mando.

Todo lo que cambia entre el equipo local y Railway llega por variables de entorno
(ver `.env.example`). No hay datos sensibles en este archivo.
"""

import os
from pathlib import Path

import dj_database_url
import plotly
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(nombre, defecto=False):
    return os.environ.get(nombre, str(defecto)).strip().lower() in {
        "1",
        "true",
        "si",
        "yes",
    }


def env_lista(nombre, defecto=""):
    return [x.strip() for x in os.environ.get(nombre, defecto).split(",") if x.strip()]


DEBUG = env_bool("DJANGO_DEBUG", False)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or (
    "clave-solo-para-desarrollo" if DEBUG else None
)
if not SECRET_KEY:
    raise ImproperlyConfigured("Define DJANGO_SECRET_KEY (o DJANGO_DEBUG=1 en local).")

ALLOWED_HOSTS = env_lista("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1")
CSRF_TRUSTED_ORIGINS = env_lista("DJANGO_CSRF_TRUSTED_ORIGINS")
# Railway expone el dominio público en esta variable.
_dominio_railway = os.environ.get("RAILWAY_PUBLIC_DOMAIN")
if _dominio_railway:
    ALLOWED_HOSTS.append(_dominio_railway)
    CSRF_TRUSTED_ORIGINS.append(f"https://{_dominio_railway}")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    # Una aplicación por área; `core` guarda lo compartido (catálogos, motor de KPI, cargas).
    "apps.core",
    "apps.proyectos",
    "apps.logistica",
    "apps.prestamos",
    "apps.rrhh",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.navegacion",
            ],
        },
    }
]

# --- Base de datos: PostgreSQL siempre -------------------------------------------------
if os.environ.get("DATABASE_URL"):
    # Railway (o cualquier servidor): una sola URL.
    DATABASES = {
        "default": dj_database_url.config(conn_max_age=600, conn_health_checks=True)
    }
else:
    # Local: PostgreSQL embebido que levanta `scripts/pg_local.py` (socket Unix en .pgdata).
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("PGDATABASE", "cuadro_mando"),
            "USER": os.environ.get("PGUSER", "postgres"),
            "HOST": os.environ.get("PGHOST", str(BASE_DIR / ".pgdata")),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "resumen"
LOGOUT_REDIRECT_URL = "login"

# --- Archivos estáticos ----------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
    # plotly.min.js viaja dentro del paquete plotly: se sirve como /static/plotly/plotly.min.js
    ("plotly", Path(plotly.__file__).parent / "package_data"),
]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# --- Seguridad en producción -----------------------------------------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("DJANGO_SSL_REDIRECT", True)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 3600

# --- API ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}

# --- Reglas de negocio ajustables sin tocar el código ----------------------------------
CUADRO_MANDO = {
    "IGV": 0.18,
    # Componentes de `Categoria.componente` que se consideran costo de obra en el valor ganado.
    "COMPONENTES_OBRA": ["01", "02", "05"],
    "HORA_ENTRADA": "08:00",
    "TOLERANCIA_MINUTOS": 10,
    "DIAS_ANTICIPACION_PAGO": 4,
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
}
