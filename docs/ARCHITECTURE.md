# Arquitetura — PESCP v1.0

## Princípios

1. **Banco isolado.** A PESCP usa PostgreSQL próprio (`pescp_pgdata`), não compartilha
   schema com a BDLP nem qualquer outro projeto do LILP.
2. **Migrations idiomáticas.** Todos os models têm migrations Django nativas. Não use
   `Meta: managed = False` — esse padrão é específico da BDLP por causa do schema legado
   Nou-Rau e **não se aplica** aqui.
3. **Dependências mínimas.** Apenas o que está no `pyproject.toml`. Não introduza cache
   distribuído (Redis), message broker (Celery) ou observability stack na v1.0.
4. **CSP estrita.** `script-src 'self'`, zero inline handlers. `main.js` é IIFE única que
   usa exclusivamente `addEventListener`.
5. **Escopo fechado.** O que não está escrito no prompt institucional original ou nesta
   documentação não deve ser implementado na v1.0. Itens fora de escopo entram em
   `docs/ROADMAP_V2.md`.

## Apps Django

```
apps/
├── core/        # Tag, mixins (TimestampedModel), context processor, templatetags
├── normas/      # Ods, NormaLegal (+ history), SeloCertificacao
├── criterios/   # Criterio (+ history), ObjetoContratual + views/urls/search/facets
├── pilotos/     # PilotoLicitacao, AvaliacaoImpacto (Admin-only na v1.0)
├── conteudo/    # PaginaInstitucional (+ history), TermoGlossario, DocumentoApoio
├── exportacao/  # WeasyPrint (PDF) + python-docx (DOCX)
└── seed/        # management commands de carga inicial e import XLSX
```

Cada app tem seu `apps.py` com `default_auto_field = BigAutoField` e seu
`migrations/__init__.py`. O `INSTALLED_APPS` usa nomes pontuados (`apps.core`,
`apps.normas`, etc.).

## Settings

Divididos em três módulos sob `pescp/settings/`:

- **`base.py`** — configurações compartilhadas (apps, middleware, banco, i18n, estáticos).
- **`dev.py`** — `DEBUG=True`, `ALLOWED_HOSTS=["*"]`, e-mail no console, sem CSP.
- **`prod.py`** — `DEBUG=False`, HSTS, SSL redirect, CSP via django-csp, `X_FRAME_OPTIONS=DENY`.

O `DJANGO_SETTINGS_MODULE` padrão em dev é `pescp.settings.dev`. Em produção, o
`docker-compose.prod.yml` sobrescreve para `pescp.settings.prod`.

## Banco de dados

PostgreSQL 15 com duas extensões pré-instaladas (`docker/postgres/init/01-extensions.sql`):

- `unaccent` — busca tolerante a acentuação.
- `pg_trgm` — similaridade aproximada (reservado para v2.0).

A busca textual usa o dicionário `portuguese` do Postgres FTS (`SearchVector(... config='portuguese')`)
com pesos A/B/C/D em `Criterio.search_vector`. O vetor é recalculado no `save()` do model.

Índices materiais:

- `pescp_crit_search_gin` (GIN sobre `search_vector`) — busca textual.
- `criterio_status_idx` (B-tree sobre `status, objeto_contratual`) — listagens.
- `criterio_fase_nivel_idx` — combinação comum em filtros.

## Versionamento de conteúdo

`django-simple-history` está habilitado nas três entidades cujo conteúdo pode mudar
ao longo do tempo e cuja história precisa ser auditável:

- `Criterio` — qualquer edição de texto da providência, justificativa etc.
- `NormaLegal` — quando uma norma é revogada ou alterada por outra.
- `PaginaInstitucional` — para audit trail das páginas legais.

`HistoryRequestMiddleware` captura o usuário responsável pela alteração quando
o save vem do Admin.

## Pipeline de busca + filtros

```
GET /criterios/?q=alcalina&objeto=pilhas-e-baterias&ods=12&fase=TR_PB
                │              │                      │       │
                │              └──────┬───────────────┘       │
                │                     ▼                       │
              SearchQuery          aplicar_facetas      filtra fase
              (Postgres FTS)       (intersection)       (AND com restantes)
                     │                  │                       │
                     └──────────────────┴───────────────────────┘
                                        │
                                  queryset.distinct()
                                        │
                                Paginator (20/pg)
                                        │
                              construir_facetas — recálculo dos
                                contadores para o sidebar
```

## Exportação PDF/DOCX

| Formato | Lib          | Template                                         |
| ------- | ------------ | ------------------------------------------------ |
| PDF     | WeasyPrint   | `apps/exportacao/templates/exportacao/criterio_pdf.html` (CSS Paged Media) |
| DOCX    | python-docx  | Construção programática em `apps/exportacao/docx_gen.py` (Verdana 10pt) |

Endpoints:

- `GET /criterios/<slug>/exportar/pdf/`
- `GET /criterios/<slug>/exportar/docx/`

Ambos retornam 404 se o critério não estiver `PUBLICADO`.

## Identidade visual

Toda a paleta GESP v1.6 está em CSS custom properties em `static/css/style.css`. Os
componentes específicos da reforma de identidade (header, menu, rodapé, faixas, banner)
estão em `static/css/sp-design-system.css` e usam prefixo `.sp-`. A ordem de carregamento
em `base.html` é `sp-design-system.css` antes de `style.css` para que regras de página
tenham precedência em conflito.

Tipografia: Roboto via Google Fonts com `preconnect` e `display=swap`; fallback Verdana
(definido pelo Manual GESP v1.6 para uso documental).

## Acessibilidade

Implementação detalhada em [`ACESSIBILIDADE.md`](ACESSIBILIDADE.md).

Resumo:
- Skip-links Alt+1..4 (eMAG R3.1)
- Modo alto contraste WCAG AAA (preto/amarelo) com persistência em `localStorage`
- Escala de fonte 87.5%–150% com persistência
- Foco visível 3px amarelo Pantone 123
- HTML5 semântico + ARIA landmarks (`role="banner|main|navigation|contentinfo"`)
- Auditoria automatizada via `make a11y` (pa11y, requer Node 18+ no host)

## LGPD e LAI

Implementação detalhada em [`LGPD_E_LAI.md`](LGPD_E_LAI.md).

- Banner LGPD não-modal (role="region") com 3 categorias: essenciais, funcionalidades, analytics.
- Modal de personalização (role="dialog" aria-modal="true").
- Persistência da escolha em `localStorage` sob chave `sp-lgpd-consent` com versão da política.
- Banner LAI na home apontando para `/transparencia/`.
- 6 páginas legais com aviso amarelo "versão inicial — pendente de validação jurídica".

## Pilotos (Admin-only)

Na v1.0, `PilotoLicitacao` e `AvaliacaoImpacto` são gerenciados exclusivamente pelo Django
Admin. O campo `publicar_pagina` existe no modelo mas **permanece False em todos os
registros** — a publicação pública de pilotos é v2.0.

## Considerações para v2.0

Veja [`ROADMAP_V2.md`](ROADMAP_V2.md) para a lista completa do que NÃO foi implementado
e o motivo. As decisões de URL e de modelo da v1.0 foram tomadas pensando na evolução:

- `Criterio.get_absolute_url()` usa slug — URLs estáveis para deeplinking em editais.
- Models isolam `User` atrás de `get_user_model()` — facilita migração para auth federada gov.br.
- API REST pública não existe na v1.0 mas pode ser servida em `/api/v1/...` sem
  conflito com as rotas atuais.
