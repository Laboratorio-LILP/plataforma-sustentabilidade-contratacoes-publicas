# Plataforma Estadual de Sustentabilidade em Contratações Públicas (PESCP)

> Projeto 6 do Portfólio 2026 do **Laboratório de Inovação em Logística Pública (LILP)**,
> da Secretaria de Gestão e Governo Digital (SGGD), Governo do Estado de São Paulo.

A PESCP é um instrumento digital e consultivo que apoia servidores públicos paulistas na
**integração sistemática de critérios de sustentabilidade** em aquisições de bens,
contratações de serviços e obras, em conformidade com a Lei 14.133/2021 (artigos 5º e 11, IV)
e alinhada aos 17 Objetivos de Desenvolvimento Sustentável (ODS) da Agenda 2030 da ONU.

O conteúdo é atomizado a partir do **Guia Nacional de Contratações Sustentáveis 2024 da AGU**,
do **Guia de Compras Públicas Sustentáveis 2025 da PMSP** e de materiais complementares
produzidos em parceria com USP, UNESP, UNICAMP e PNUD.

---

## Setup rápido (Docker)

Pré-requisitos: Docker e Docker Compose v2.

```bash
git clone <url> pescp
cd pescp
cp .env.example .env
make setup           # cópia .env + build + migrate + seed inicial (ODS + páginas placeholder)
make superuser       # cria usuário admin interativamente
```

Acesse:

- Portal público: <http://localhost:8002/>
- Admin Django:  <http://localhost:8002/admin/>

### Comandos do Makefile

```bash
make help            # lista todos os comandos disponíveis
make up              # sobe containers
make down            # derruba containers
make logs            # tail logs
make shell           # Django shell
make migrate         # roda migrations
make seed FILE=seeds/pescp_seed_v1.xlsx   # importa planilha de critérios
make seed-ods        # cria os 17 ODS (idempotente)
make seed-pages      # cria páginas institucionais placeholder
make test            # roda pytest
make test-cov        # roda com cobertura
make lint            # ruff check
make a11y            # auditoria WCAG 2.0 AA com pa11y (requer Node 18+ no host)
make clean           # derruba containers e remove volumes
```

---

## Stack

| Camada               | Tecnologia                                    |
| -------------------- | --------------------------------------------- |
| Backend              | Django 5.1 (Python 3.11)                      |
| Banco                | PostgreSQL 15-alpine (banco isolado)          |
| Templates            | Django Templates (sem framework JS)           |
| CSS                  | CSS vanilla em duas camadas (`.sp-*` + util)  |
| JS                   | Vanilla em IIFE única (CSP `script-src 'self'`) |
| Estáticos            | Whitenoise (compressed manifest em prod)      |
| Servidor             | Gunicorn (prod) / runserver (dev)             |
| Versionamento        | django-simple-history                         |
| Import XLSX          | openpyxl + django-import-export               |
| Export PDF           | WeasyPrint                                    |
| Export DOCX          | python-docx                                   |
| Acessibilidade       | eMAG 3.1 + WCAG 2.0 AA                        |

---

## Estrutura do projeto

```
pescp/
├── docker/                     # Dockerfile, compose dev e prod
├── docs/                       # ARCHITECTURE, MODELO_DE_DADOS, IMPORTACAO_SEED, etc.
├── pescp/                      # Django project (settings, urls, wsgi)
├── apps/
│   ├── core/                   # Tag, helpers, templatetags
│   ├── normas/                 # Ods, NormaLegal, SeloCertificacao
│   ├── criterios/              # Criterio, ObjetoContratual + views, urls, search, facets
│   ├── pilotos/                # PilotoLicitacao, AvaliacaoImpacto (Admin-only na v1.0)
│   ├── conteudo/               # PaginaInstitucional, TermoGlossario, DocumentoApoio
│   ├── exportacao/             # PDF (WeasyPrint), DOCX (python-docx)
│   └── seed/                   # management commands: import_pescp_seed, create_initial_*
├── templates/                  # base, partials, páginas
├── static/                     # css, js, imagens
├── seeds/                      # planilhas XLSX (apenas template versionado)
├── tests/                      # conftest, fixtures
├── tools/                      # gerar_seed_template.py, audit_a11y.py
├── manage.py
├── pyproject.toml
├── Makefile
├── .env.example
└── README.md
```

---

## Documentação

| Documento | Tema |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Decisões de arquitetura, módulos, dependências |
| [`docs/MODELO_DE_DADOS.md`](docs/MODELO_DE_DADOS.md) | ER diagram + descrição de cada entidade |
| [`docs/IMPORTACAO_SEED.md`](docs/IMPORTACAO_SEED.md) | Schema da planilha XLSX e regras do importador |
| [`docs/IDENTIDADE_VISUAL.md`](docs/IDENTIDADE_VISUAL.md) | Paleta GESP, tipografia, logotipos, assinatura tríplice |
| [`docs/ACESSIBILIDADE.md`](docs/ACESSIBILIDADE.md) | Conformidade eMAG 3.1 e WCAG 2.0 AA, checklist de auditoria |
| [`docs/LGPD_E_LAI.md`](docs/LGPD_E_LAI.md) | Banner de cookies, política de privacidade, transparência |
| [`docs/DEPLOY.md`](docs/DEPLOY.md) | Instruções para produção (Caddy/Nginx, gunicorn) |
| [`docs/ROADMAP_V2.md`](docs/ROADMAP_V2.md) | O que NÃO foi implementado na v1.0 (escopo fechado) |
| [`docs/QUESTIONS.md`](docs/QUESTIONS.md) | Perguntas em aberto para o LILP |

---

## Definition of Done — v1.0

Os itens abaixo devem estar verdadeiros para considerar a v1.0 pronta para review.
Veja seção 14 do prompt institucional original para a lista completa.

- [x] `docker compose up` sobe `postgres` + `web` sem erro
- [x] `migrate` cria todas as tabelas (sem `managed=False`)
- [x] `create_initial_ods` cria os 17 ODS
- [x] `create_initial_pages` cria páginas institucionais e legais placeholder
- [x] `import_pescp_seed --file=...` é idempotente e transacional
- [x] Home, Lista de Critérios, Detalhe, ODS, Objetos, Fases, Glossário, Busca funcionam
- [x] Botões Copiar Providência / Exportar PDF / Exportar DOCX disponíveis
- [x] Admin permite criar, editar, publicar e arquivar critério
- [x] Alto contraste e escala de fonte persistem entre páginas
- [x] CSP estrita em produção (`script-src 'self'`)
- [x] eMAG 3.1 e WCAG 2.0 AA — skip-links Alt+1..4, foco visível, ARIA roles
- [x] Versionamento via `django-simple-history` em Criterio/NormaLegal/PaginaInstitucional

---

## Licença

MIT. Veja [`LICENSE`](LICENSE).
