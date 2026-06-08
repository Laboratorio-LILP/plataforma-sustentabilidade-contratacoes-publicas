# Importação de seed — `import_pescp_seed`

O importador `import_pescp_seed` carrega o conteúdo da PESCP a partir de uma
planilha XLSX produzida pelo time do LILP em conjunto com parceiros acadêmicos
(USP, UNESP, UNICAMP, PNUD).

## Uso

```bash
# Importação simples
make seed FILE=seeds/pescp_seed_v1.xlsx

# Equivalente:
docker compose exec web python manage.py import_pescp_seed \
    --file=seeds/pescp_seed_v1.xlsx

# Validação sem persistir
docker compose exec web python manage.py import_pescp_seed \
    --file=seeds/pescp_seed_v1.xlsx --dry-run

# Atualizar registros existentes (default: apenas criar novos)
docker compose exec web python manage.py import_pescp_seed \
    --file=seeds/pescp_seed_v1.xlsx --update-existing
```

## Garantias

- **Idempotente.** Re-rodar não duplica registros — usa `slug` (ou `codigo` em
  Criterio) como chave natural.
- **Transacional.** Em caso de erro, faz rollback de toda a importação.
- **Logging claro.** Cada aba reporta criados/atualizados/pulados/erros.
- **Ordem de processamento.** Garantida para resolver dependências:
  `ODS → NormaLegal → SeloCertificacao → Tag → ObjetoContratual → Criterio →
   PaginaInstitucional → TermoGlossario`.

> **Importante:** o importador **não cria os 17 ODS**. Eles devem existir antes,
> via `python manage.py create_initial_ods`. Isso é parte do `make setup`.

## Estrutura da planilha

A planilha XLSX tem **7 abas**. Cada uma tem cabeçalho na linha 1. Linhas
totalmente vazias são puladas. Use `seeds/pescp_seed_template.xlsx` como base
(gerado por `python tools/gerar_seed_template.py`).

### Aba `objetos_contratuais`

| Coluna                | Obrigatório? | Descrição |
|-----------------------|:------------:|-----------|
| `nome`                | ✓            | Nome legível, ex.: "Pilhas e Baterias" |
| `slug`                | ✓            | Identificador URL, ex.: "pilhas-e-baterias" |
| `descricao`           |              | Texto curto |
| `supercategoria_slug` |              | Slug do parent (deve existir nesta mesma aba) |
| `ordem`               |              | Inteiro para ordenar |

Profundidade máxima esperada: 2 níveis (supercategoria → categoria).

### Aba `normas_legais`

| Coluna             | Obrigatório? | Notas |
|--------------------|:------------:|-------|
| `titulo_curto`     | ✓            | "Lei 14.133/2021" |
| `titulo_completo`  | ✓            | "Lei nº 14.133, de 1º de abril de 2021..." |
| `slug`             | ✓            | "lei-14133-2021" |
| `tipo`             |              | Valor de `NormaLegal.Tipo` (default `LEI_FEDERAL`) |
| `esfera`           |              | `FEDERAL`/`ESTADUAL`/`MUNICIPAL`/`INTERNACIONAL` |
| `numero`           |              | "14.133/2021" |
| `data_publicacao`  |              | YYYY-MM-DD ou DD/MM/YYYY |
| `link_oficial`     |              | URL no DOU, Planalto, doe.sp.gov.br |
| `ementa`           |              | Texto longo |

### Aba `selos_certificacao`

| Coluna         | Obrigatório? |
|----------------|:------------:|
| `nome`         | ✓            |
| `slug`         | ✓            |
| `tipo`         |              | `NACIONAL`/`INTERNACIONAL`/`SETORIAL` |
| `descricao`    |              |
| `link_oficial` |              |

### Aba `tags`

| Coluna  | Obrigatório? |
|---------|:------------:|
| `nome`  | ✓            |
| `slug`  | ✓            |

### Aba `criterios` (principal)

| Coluna                       | Obrigatório? | Notas |
|------------------------------|:------------:|-------|
| `codigo`                     | ✓            | Formato `CRIT-AAAA-NNN`. Único. |
| `titulo`                     | ✓            |       |
| `slug`                       |              | Auto-gerado se vazio |
| `objeto_contratual_slug`     | ✓            | Deve existir na aba `objetos_contratuais` |
| `tipo_contratacao`           |              | Valor de `TipoContratacao` (default `BENS`) |
| `fase_processo`              |              | Valor de `FaseProcesso` (default `TR_PB`) |
| `nivel_ambicao`              |              | `BASICO`/`INTERMEDIARIO`/`AVANCADO` (default `BASICO`) |
| `texto_providencia`          |              | Rich text (HTML simples) |
| `determinacoes_principais`   |              | Rich text |
| `justificativa_tecnica`      |              | Rich text |
| `metodo_verificacao`         |              | Rich text |
| `precaucoes`                 |              | Rich text |
| `ods_numeros`                |              | Inteiros separados por `;` — ex.: `7;12;15` |
| `normas_slugs`               |              | Slugs separados por `;` |
| `selos_slugs`                |              | Slugs separados por `;` |
| `tags_slugs`                 |              | Slugs separados por `;` |
| `fonte`                      |              | Ex.: "Guia AGU 2024 — item 27" |
| `status`                     |              | `RASCUNHO`/`PUBLICADO`/`ARQUIVADO` (default `RASCUNHO`) |

> Critérios referenciando ODS/normas/selos/tags inexistentes não são bloqueados —
> o critério é criado, mas o erro é logado para revisão posterior.

### Aba `paginas_institucionais`

| Coluna     | Obrigatório? |
|------------|:------------:|
| `titulo`   | ✓            |
| `slug`     | ✓            |
| `conteudo` |              | HTML sanitizado |
| `ordem`    |              | Inteiro |
| `publicada`|              | 1/0/true/false/sim/não |

### Aba `glossario`

| Coluna      | Obrigatório? |
|-------------|:------------:|
| `termo`     | ✓            |
| `slug`      | ✓            |
| `sigla`     |              | Ex.: "ETP", "LCC", "LR" |
| `definicao` | ✓            |

## Estratégia de erros

- Erros de **validação** (slug inexistente, valor de choice inválido) são logados
  por linha com número da planilha — a importação continua.
- Erros **fatais** (arquivo inexistente, aba sem cabeçalho) abortam toda a transação.
- `--dry-run` força rollback ao final via `_DryRunRollback` interno, mesmo se a
  importação não teve erros — útil para validar antes de persistir.

## Iteração e atualização

Para atualizar conteúdo já importado:

```bash
make seed FILE=seeds/pescp_seed_v1.1.xlsx --update-existing
```

> Use `--update-existing` apenas em ambientes controlados. Em produção,
> prefira editar pelo Admin Django (que mantém histórico via simple-history).
