"""Configurações compartilhadas entre dev e prod.

Reflete as exigências do prompt institucional do LILP/SGGD:
- Banco isolado (PostgreSQL próprio, sem `managed = False`)
- django-simple-history para versionamento de Criterio/NormaLegal/PaginaInstitucional
- django-csp para Content-Security-Policy
- whitenoise para estáticos em produção
- Internacionalização pt-BR / America/Sao_Paulo
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

# ============================================================
# Núcleo
# ============================================================
SECRET_KEY = env("DJANGO_SECRET_KEY", default="insecure-dev-key-change-in-production")
DEBUG = env("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# ============================================================
# Apps
# ============================================================
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "simple_history",
    "import_export",
]

LOCAL_APPS = [
    "apps.core",
    "apps.normas",
    "apps.criterios",
    "apps.pilotos",
    "apps.conteudo",
    "apps.exportacao",
    "apps.seed",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ============================================================
# Middleware
# ============================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # django-simple-history captura o usuário em saves
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "pescp.urls"

# ============================================================
# Templates
# ============================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.site_context",
            ],
        },
    },
]

WSGI_APPLICATION = "pescp.wsgi.application"

# ============================================================
# Banco — Postgres dedicado, schema próprio (migrations idiomáticas)
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="pescp"),
        "USER": env("POSTGRES_USER", default="pescp"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="changeme_pescp_2026"),
        "HOST": env("POSTGRES_HOST", default="localhost"),
        "PORT": env("POSTGRES_PORT", default="5432"),
        "CONN_MAX_AGE": 60,
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# Internacionalização
# ============================================================
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# ============================================================
# Estáticos e mídia
# ============================================================
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# ============================================================
# Auth — usa User padrão; isolamos atrás de get_user_model() em apps
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "admin:login"

# ============================================================
# Configuração do projeto PESCP
# ============================================================
PESCP = {
    # URL pública canônica (usada em PDFs/DOCX e meta tags)
    "PUBLIC_URL": env("PESCP_PUBLIC_URL", default="http://localhost:8000"),
    # Contato institucional exibido em aviso de versão e rodapé
    "CONTATO_EMAIL": env("PESCP_CONTATO_EMAIL", default="lab.sggd@sp.gov.br"),
    # Versão da política de privacidade/cookies (incrementar invalida consents)
    "POLITICA_VERSAO": 1,
    # Paginação padrão da listagem de critérios
    "CRITERIOS_POR_PAGINA": 20,
    # Versão da plataforma exibida no aviso "v1.0 — em validação"
    "VERSAO_ROTULO": "1.0",
    "VERSAO_DATA": "junho/2026",
}

# Cache local em memória (sem distribuir — escopo v1.0)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "pescp-default",
    }
}

# Logging — formato simples; em prod usa STDOUT (containers)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django.db.backends": {"level": "WARNING", "propagate": True},
        "apps": {"level": "INFO", "propagate": True},
    },
}
