"""WSGI entry-point — gunicorn em produção, runserver em dev."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pescp.settings.dev")

application = get_wsgi_application()
