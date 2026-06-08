.PHONY: help setup up down logs shell migrate makemigrations seed seed-ods seed-pages superuser test test-cov lint format check collectstatic clean rebuild a11y audit-a11y prod-up prod-down

# ============================================================
# PESCP — Atalhos de operação para o time do LILP
# ============================================================

COMPOSE = docker compose --env-file .env -f docker/docker-compose.yml
WEB = $(COMPOSE) exec web

help:  ## Lista comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ---------- Bootstrap ----------
setup:  ## Cópia .env, build, migrate e seed inicial (rotina de primeira execução)
	@test -f .env || cp .env.example .env
	$(COMPOSE) build
	$(COMPOSE) up -d postgres
	@echo "Aguardando postgres ficar saudável..."
	@until $(COMPOSE) exec -T postgres pg_isready -U $$(grep ^POSTGRES_USER .env | cut -d= -f2) > /dev/null 2>&1; do sleep 1; done
	$(COMPOSE) up -d web
	$(WEB) python manage.py makemigrations core normas criterios pilotos conteudo
	$(WEB) python manage.py migrate
	$(WEB) python manage.py create_initial_ods
	$(WEB) python manage.py create_initial_pages
	@echo ""
	@echo "✓ PESCP pronta em http://localhost:8002/"
	@echo "  Para criar superuser:  make superuser"
	@echo "  Para semear critérios: make seed FILE=seeds/pescp_seed_v1.xlsx"
	@echo ""
	@echo "  IMPORTANTE: revise os arquivos apps/*/migrations/0001_initial.py"
	@echo "  gerados e commite no git — eles fazem parte do código-fonte."

# ---------- Ambiente dev ----------
up:  ## Sobe containers em background
	$(COMPOSE) up -d

down:  ## Derruba containers
	$(COMPOSE) down

logs:  ## Tail logs dos containers
	$(COMPOSE) logs -f

shell:  ## Django shell dentro do container web
	$(WEB) python manage.py shell

rebuild:  ## Rebuild imagem web e sobe novamente
	$(COMPOSE) build web
	$(COMPOSE) up -d web

# ---------- Migrations e seed ----------
migrate:  ## Aplica migrations
	$(WEB) python manage.py migrate

makemigrations:  ## Gera migrations a partir dos models
	$(WEB) python manage.py makemigrations

seed:  ## Importa planilha XLSX. Uso: make seed FILE=seeds/pescp_seed_v1.xlsx
	@test -n "$(FILE)" || (echo "FILE não informado. Uso: make seed FILE=seeds/pescp_seed_v1.xlsx"; exit 1)
	$(WEB) python manage.py import_pescp_seed --file=$(FILE)

seed-ods:  ## Cria os 17 ODS oficiais (idempotente)
	$(WEB) python manage.py create_initial_ods

seed-pages:  ## Cria páginas institucionais e legais placeholder (idempotente)
	$(WEB) python manage.py create_initial_pages

superuser:  ## Cria superusuário interativo
	$(WEB) python manage.py createsuperuser

# ---------- Qualidade ----------
test:  ## Roda suite pytest
	$(WEB) python -m pytest

test-cov:  ## Roda suite com cobertura
	$(WEB) python -m pytest --cov=apps --cov-report=term-missing

lint:  ## Lint com ruff
	$(WEB) ruff check .

format:  ## Format com ruff
	$(WEB) ruff format .

check:  ## Roda lint e tests em sequência
	$(MAKE) lint
	$(MAKE) test

# ---------- Auditoria de acessibilidade ----------
A11Y_URLS = \
	http://localhost:8002/ \
	http://localhost:8002/criterios/ \
	http://localhost:8002/objetos/ \
	http://localhost:8002/ods/ \
	http://localhost:8002/glossario/ \
	http://localhost:8002/sobre/ \
	http://localhost:8002/transparencia/ \
	http://localhost:8002/acessibilidade/ \
	http://localhost:8002/politica-de-privacidade/ \
	http://localhost:8002/politica-de-cookies/ \
	http://localhost:8002/mapa-do-site/ \
	http://localhost:8002/fale-conosco/

a11y:  ## Auditoria pa11y WCAG 2.0 AA — requer Node 18+ no host
	@echo "Verificando acessibilidade WCAG 2.0 AA com pa11y..."
	@for url in $(A11Y_URLS); do \
		echo ""; echo "==> $$url"; \
		npx --yes pa11y --standard WCAG2AA "$$url" || true; \
	done

audit-a11y: a11y  ## Alias para 'a11y'

# ---------- Estáticos ----------
collectstatic:  ## Coleta estáticos (whitenoise + manifest)
	$(WEB) python manage.py collectstatic --noinput

# ---------- Limpeza ----------
clean:  ## Derruba containers e remove volumes (CUIDADO: apaga banco)
	$(COMPOSE) down -v --remove-orphans

# ---------- Produção (overlay) ----------
prod-up:  ## Sobe stack de produção (requer docker-compose.prod.yml)
	$(COMPOSE) -f docker/docker-compose.prod.yml up -d --build

prod-down:  ## Derruba stack de produção
	$(COMPOSE) -f docker/docker-compose.prod.yml down
