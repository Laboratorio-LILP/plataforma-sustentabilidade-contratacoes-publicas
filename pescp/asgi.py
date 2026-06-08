"""ASGI entry-point — placeholder para futura migração assíncrona."""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pescp.settings.dev")

application = get_asgi_application()
