FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependências de sistema:
#   libpq-dev, gcc           — psycopg2
#   libpango/cairo/gdk-pixbuf — WeasyPrint
#   libxml2/libxslt          — lxml (transitivo)
#   shared-mime-info         — mime detection do WeasyPrint
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        libxml2 \
        libxslt1.1 \
        shared-mime-info \
        fonts-dejavu-core \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
RUN pip install --no-cache-dir \
        "django>=5.1,<6.0" \
        "psycopg2-binary>=2.9" \
        "gunicorn>=22.0" \
        "django-environ>=0.11" \
        "django-csp>=3.8,<4.0" \
        "django-simple-history>=3.7" \
        "django-import-export>=4.0" \
        "openpyxl>=3.1" \
        "weasyprint>=62" \
        "python-docx>=1.1" \
        "whitenoise>=6.7" \
        "Pillow>=10.0" \
        "ruff>=0.8" \
        "pytest>=8.0" \
        "pytest-django>=4.9" \
        "pytest-cov>=5.0" \
        "factory-boy>=3.3"

COPY . /app/

EXPOSE 8000

# Comando default em dev é runserver com auto-reload via volume bind.
# Em produção docker-compose.prod.yml sobrescreve com gunicorn.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
