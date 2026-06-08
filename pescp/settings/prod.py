"""Settings de produção — DEBUG=False, headers de segurança e CSP estrita.

Conforme prompt institucional: HSTS preload, SSL redirect, X-Frame-Options
DENY, CSP `script-src 'self'` (zero unsafe-inline porque main.js usa
exclusivamente addEventListener).
"""

from .base import *  # noqa: F401,F403
from .base import MIDDLEWARE  # noqa: F401

DEBUG = False

# Cabeçalhos de segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSP via django-csp — middleware inserido logo após SecurityMiddleware
MIDDLEWARE = MIDDLEWARE.copy()
if "csp.middleware.CSPMiddleware" not in MIDDLEWARE:
    MIDDLEWARE.insert(1, "csp.middleware.CSPMiddleware")

CSP_DEFAULT_SRC = ("'self'",)
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "https://saopaulo.sp.gov.br",
    "https://compras.sp.gov.br",
)
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
# 'unsafe-inline' apenas para style:: trechos pontuais (ex.: hero com bg inline);
# pode endurecer com nonces em iteração futura.
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_SCRIPT_SRC = ("'self'",)
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
