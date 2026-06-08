"""Settings de desenvolvimento — DEBUG=True, sem CSP estrita."""

from .base import *  # noqa: F401,F403
from .base import DEBUG, INSTALLED_APPS, MIDDLEWARE  # noqa: F401

DEBUG = True

# Em dev, permitimos o host vazio para uso atrás de runserver
ALLOWED_HOSTS = ["*"]

# Email no console em dev
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Storage local em vez de manifest comprimido — facilita debug de estáticos
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# CSRF mais permissivo em dev (runserver atende em http://localhost)
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
