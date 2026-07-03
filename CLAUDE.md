# PESCP — Integração da frente para o Claude Code

Plataforma Estadual de Sustentabilidade em Contratações Públicas (PESCP), frente do LILP. Este arquivo é a camada de **Instruções da frente** para o Claude Code; viaja com o repositório.

## Limites de segurança — inegociáveis

Valem integralmente os limites do `LILP/CLAUDE.md` transversal e do ADR-006 da vault (reunião
CTI de 30/06/2026): **sem túneis** ou mecanismos de exposição externa, **sem alterações de
firewall**, **sem PowerShell** em host corporativo, **sem acesso a servidores** — acesso
restrito a TI/PRODESP; a **VPN é a via única** de acesso remoto. Vedado usar IA para contornar
barreiras de segurança. Se algo estiver inacessível, a resposta correta é **parar e registrar
solicitação à equipe de TI** (Felipe/Diego).

## Rito de sessão
O rito transversal vive em `LILP/CLAUDE.md` na árvore OneDrive. **Este clone fica FORA do OneDrive** (ADR-002; Mac é a máquina principal desde 23/06/2026: `~/Desktop/Projetos/Governo/…`), onde o arquivo transversal não é ancestral — leia o rito e o estado direto na vault:
- Vault (Mac): `~/Library/CloudStorage/OneDrive-PRODESP/LILP/SGGD - SEGES - LILP/`
- Rito + teoria: `…/Padrões/Arquitetura de Contexto.md` (+ `LILP/CLAUDE.md`)
- Estado vivo do laboratório: `…/Mapa de Contexto Operacional.md`
- Estado desta frente: seção Frente 5 do Mapa (mapa-semente próprio ainda não existe — pendência).

## O que é
Portal público + admin em **Django 5.1 (Python 3.11) + Postgres 15-alpine**, compose `lilp-pescp` (containers `lilp-pescp-{postgres,web}-1`). Conteúdo atomizado do Guia AGU 2024 e do Guia PMSP 2025. Sem framework JS (JS vanilla em IIFE única; CSP `script-src 'self'`); WhiteNoise; exportação PDF (WeasyPrint) e DOCX (python-docx); versionamento django-simple-history; settings divididos `pescp.settings.{base,dev,prod}`.

## Onde isto roda
- **Clone canônico:** `~/Desktop/Projetos/Governo/plataforma-sustentabilidade-contratacoes-publicas` (fora do OneDrive, ADR-002).
- **Remoto:** `github.com/Laboratorio-LILP/plataforma-sustentabilidade-contratacoes-publicas`.
- **Portas no host:** web `8002→8000` (`PESCP_PORT`); postgres `127.0.0.1:5433→5432` (coexistência com a BDLP: 8000/8080/5432).

## Comandos (do Makefile real)
- `make setup` — 1ª vez: build + espera `pg_isready` + migrate + `create_initial_ods` + `create_initial_pages`.
- `make up` / `down` / `logs` / `shell`; `make superuser`.
- `make seed FILE=seeds/pescp_seed_v1.xlsx` (`import_pescp_seed`, idempotente/transacional); `make seed-ods`; `make seed-pages`.
- `make test` / `test-cov`; `make lint` / `format` / `check`.
- `make a11y` — pa11y WCAG2AA em 12 URLs (requer Node 18+ no HOST).
- `make clean` — **APAGA volumes/banco**. `make prod-up` / `prod-down` (overlay `docker/docker-compose.prod.yml`).

## Gotchas (não tropece)
- **Segredos por env, sem fallback** (alinhado ao repo-modelo BDLP em 02/07/2026): o compose **falha** se `POSTGRES_PASSWORD` e `DJANGO_SECRET_KEY` não estiverem no `.env`. Copie de `.env.example` e defina valores reais.
- `make setup` roda `makemigrations` dentro do container: as migrations são versionadas — revisar e commitar qualquer migration nova gerada.
- Código montado como volume (`..:/app`): edição no host reflete no container, mas dependência nova exige rebuild.
- Web em **loopback** (`127.0.0.1:8002`) desde 02/07/2026, alinhado à convenção LILP (ADR-0008 da BDLP) — o app não é alcançável pela rede local.
- pytest usa `DJANGO_SETTINGS_MODULE=pescp.settings.dev` e `--strict-markers`; ruff line-length 120 (migrations excluídas).
- `seeds/`: só o template e a v1 são versionados. `POSTGRES_PORT` no `.env` é a porta do **HOST** (5433) — dentro do container o Django fala com `postgres:5432`.

## Front
Identidade GESP (`docs/IDENTIDADE_VISUAL.md`); eMAG 3.1 + WCAG 2.0 AA; Linguagem Simples. Alto contraste e escala de fonte persistem entre páginas.

## Docs
`docs/ARCHITECTURE.md`, `MODELO_DE_DADOS.md`, `IMPORTACAO_SEED.md`, `DEPLOY.md`, `ROADMAP_V2.md` (escopo v1 fechado), `QUESTIONS.md`.

## Segredos
Nunca entram em arquivo versionado nem na vault. `.env` é gitignored.
