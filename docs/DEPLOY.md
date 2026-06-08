# Deploy — PESCP

## Visão geral

Em produção, a PESCP roda em três camadas:

1. **Reverse proxy** (Caddy ou Nginx) — terminação TLS, HSTS, compressão.
2. **Gunicorn** — WSGI Python que serve Django.
3. **PostgreSQL 15** — banco de dados, em volume persistente.

Whitenoise serve os estáticos diretamente do Gunicorn (compressed manifest);
não é necessária camada de CDN externa na v1.0.

## Variáveis de ambiente

Use `.env.example` como base. Em produção, **NUNCA** versione o `.env` real.

| Variável                  | Obrigatório | Notas |
|---------------------------|:-----------:|-------|
| `DJANGO_SETTINGS_MODULE`  | ✓           | `pescp.settings.prod` |
| `DJANGO_SECRET_KEY`       | ✓           | Gere com `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DJANGO_DEBUG`            | ✓           | `false` em produção |
| `DJANGO_ALLOWED_HOSTS`    | ✓           | Domínio canônico, ex.: `pescp.sp.gov.br` |
| `POSTGRES_DB`             | ✓           | `pescp` |
| `POSTGRES_USER`           | ✓           | `pescp` |
| `POSTGRES_PASSWORD`       | ✓           | **gere senha forte** |
| `POSTGRES_HOST`           | ✓           | `postgres` (compose) ou IP/hostname |
| `POSTGRES_PORT`           |             | Default `5432` |
| `PESCP_PORT`              |             | Default `8000` |
| `PESCP_PUBLIC_URL`        | ✓           | URL canônica para PDFs/DOCX, ex.: `https://pescp.sp.gov.br` |
| `PESCP_CONTATO_EMAIL`     |             | E-mail exibido em rodapé |

## Subida em produção (Docker Compose)

```bash
# 1. Clonar o repo no servidor
git clone <url> /opt/pescp
cd /opt/pescp

# 2. Configurar .env
cp .env.example .env
nano .env  # ajustar valores reais

# 3. Build e subida
make prod-up
# Equivalente:
docker compose --env-file .env \
    -f docker/docker-compose.yml \
    -f docker/docker-compose.prod.yml \
    up -d --build

# 4. Criar superuser
docker compose exec web python manage.py createsuperuser

# 5. Carregar conteúdo inicial
docker compose exec web python manage.py create_initial_ods
docker compose exec web python manage.py create_initial_pages
docker compose exec web python manage.py import_pescp_seed \
    --file=seeds/pescp_seed_v1.xlsx
```

O `docker-compose.prod.yml` sobrescreve o `command` do serviço `web` para rodar
`collectstatic` + `migrate` + `gunicorn`. Não usa volume bind do código.

## Frontamento (Caddy)

Exemplo mínimo de `Caddyfile` (não incluído no compose v1.0 — fica a critério
da Prodesp / time de infraestrutura):

```
pescp.sp.gov.br {
    reverse_proxy web:8000
    encode gzip zstd
    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Frame-Options "DENY"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
    }
}
```

## Headers de segurança em prod

Definidos em `pescp/settings/prod.py`:

- `SECURE_SSL_REDIRECT = True`
- `SECURE_HSTS_SECONDS = 31_536_000` (1 ano)
- `SECURE_HSTS_INCLUDE_SUBDOMAINS = True`
- `SECURE_HSTS_PRELOAD = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `X_FRAME_OPTIONS = "DENY"`
- `SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"`

CSP via django-csp:

- `default-src 'self'`
- `script-src 'self'` — zero inline porque `main.js` é IIFE única
- `style-src 'self' 'unsafe-inline' https://fonts.googleapis.com`
- `font-src 'self' https://fonts.gstatic.com`
- `img-src 'self' data: https://saopaulo.sp.gov.br https://compras.sp.gov.br`
- `frame-ancestors 'none'`

## Backup

```bash
# Backup do banco
docker compose exec postgres pg_dump -U pescp pescp > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
cat backup.sql | docker compose exec -T postgres psql -U pescp pescp
```

Backups devem ser feitos diariamente em produção. Rotina a definir com a Prodesp.

## Monitoramento

Não há observability stack na v1.0. Para health check básico:

```bash
curl -fs http://localhost:8000/admin/login/ > /dev/null && echo OK || echo FAIL
```

A v2.0 deve adicionar healthcheck endpoint dedicado.

## Atualização

```bash
cd /opt/pescp
git pull
make prod-rebuild
docker compose exec web python manage.py migrate
```

Para mudanças de conteúdo (planilha), apenas:

```bash
docker compose exec web python manage.py import_pescp_seed \
    --file=seeds/pescp_seed_v1.1.xlsx --update-existing
```
