# Identidade Visual — PESCP

Base normativa: **Manual GESP v1.6 (Abr/2023)** — Manual de Identidade Visual do
Governo do Estado de São Paulo. As mesmas decisões valem para todos os portais
do LILP/SGGD.

## Paleta

Definida em CSS custom properties em `static/css/style.css` no seletor `:root`.

| Token CSS              | HEX       | Pantone        | Uso |
|------------------------|-----------|----------------|-----|
| `--sp-vermelho`        | `#ED1C24` | 485 C          | Cor primária — bordas accent, CTAs, header underline |
| `--sp-amarelo`         | `#FBB900` | 123 C          | Foco/acessibilidade, indicador de página atual, avisos |
| `--sp-verde`           | `#0B9247` | 347 C          | Sucesso, ODS, nível de ambição |
| `--sp-azul`            | `#034EA2` | 2955 C         | Institucional, links, skip-links |
| `--sp-preto`           | `#000000` | —              | Texto principal, barra GovSP |
| `--sp-branco`          | `#FFFFFF` | —              | Fundo do header, cartões |
| `--sp-cinza-escuro`    | `#808080` | Cinza 50%      | Texto secundário |
| `--sp-cinza-claro`     | `#BFBFBF` | Cinza 25%      | Divisórias, fundos sutis |

Derivados:
- `--sp-azul-escuro: #023A7A` — hover do azul
- `--sp-vermelho-escuro: #C8161D` — hover do vermelho
- `--sp-fundo-claro: #F5F5F5` — fundo de seções alternadas
- `--sp-foco: #FFB800` — outline de foco visível (3px)

## Tipografia

- **Principal**: Roboto (Google Fonts, pesos 400/500/700/900)
- **Fallback de sistema**: Verdana → `system-ui` → Arial
- Carregada via `<link rel="preconnect">` + `<link rel="stylesheet">` em `base.html`
  com `display=swap`

### Escala (em rem, base 16px)

| Nível    | Tamanho |
|----------|---------|
| `h1`     | 36px    |
| `h2`     | 28px    |
| `h3`     | 22px    |
| `h4`     | 18px    |
| corpo    | 16px    |
| legenda  | 14px    |

Line-height do corpo: **1.6**.

## Grid e layout

- 12 colunas, gutter 30px (Manual GESP p. 26)
- Container central: `max-width: 1320px`, `margin-inline: auto`, padding lateral `1.5rem`
- Breakpoints mobile-first:

  | Token CSS    | px      | Dispositivo            |
  |--------------|---------|------------------------|
  | `--bp-xs`    | 576     | mobile                 |
  | `--bp-sm`    | 768     | tablet vertical        |
  | `--bp-md`    | 992     | desktop pequeno        |
  | `--bp-lg`    | 1200    | desktop                |
  | `--bp-xl`    | 1400    | desktop grande         |

## Assinatura institucional tríplice

Conforme Manual GESP v1.6 páginas 22–23 (Padrão para Mais de uma Secretaria),
a assinatura horizontal organiza-se da esquerda para a direita:

```
Secretaria de Gestão e Governo Digital  →  LILP  →  Logo SP Governo do Estado
                                                         (logo principal sempre à direita)
```

Versões a produzir e colocar em `static/img/logos/`:

1. Horizontal positiva — uso prioritário, header.
2. Horizontal negativa — uso em fundos escuros.
3. Vertical positiva — uso secundário, mobile e rodapé.

> **Status atual (v1.0)**: usamos os PNGs reaproveitados da BDLP em
> `static/img/logos/sggd/`, `static/img/logos/lilp/` e `static/img/logos/governo-sp/`.
> A produção dos SVGs vetoriais oficiais é tarefa pendente, registrada em
> `docs/QUESTIONS.md`.

## Componentes visuais específicos da PESCP

### Badge de ODS

Chip colorido com cor oficial do ODS, ícone (opcional) e número:

```html
<span class="sp-badge-ods sp-badge-ods--ods-7"
      style="background-color: #FCC30B;"
      aria-label="ODS 7 — Energia limpa e acessível">7</span>
```

A cor vem de `Ods.cor_hex` no banco (preenchido por `create_initial_ods`).

### Indicador de nível de ambição

Três barras horizontais, com 1/2/3 preenchidas em verde (`--sp-verde`):

```html
<span class="sp-nivel-ambicao sp-nivel-ambicao--avancado">
  <span class="sp-nivel-ambicao__barras">
    <span class="sp-nivel-ambicao__barra"></span>
    <span class="sp-nivel-ambicao__barra"></span>
    <span class="sp-nivel-ambicao__barra"></span>
  </span>
  Avançado
</span>
```

### Card de critério

Veja `templates/criterios/_criterio_card.html`. Título, código, primeira linha
da Providência, badges (objeto, fase, nível), chips de ODS.

### Bloco "Texto pronto"

Caixa com fundo `--sp-fundo-claro`, borda lateral 4px em `--sp-vermelho`, botão
"Copiar" no canto superior direito. Implementado em `templates/criterios/detail.html`.

## Arquitetura CSS em duas camadas

1. **`static/css/sp-design-system.css`** — componentes novos prefixados `.sp-*`.
   Carregado **antes** em `base.html`.
2. **`static/css/style.css`** — paleta, tipografia, utilitários, classes legadas.

Essa ordem garante que regras de página (style.css) tenham precedência em caso
de conflito.

## Decreto correlato

- **Decreto Estadual 69.056/2024** — Portal único SP.GOV.BR. Define a obrigatoriedade
  da barra superior preta e da identidade unificada do GovSP.
- **Decreto Estadual 67.799/2023** — Estratégia de Governo Digital.
- **Resolução SGGD nº 38/2024** — Institui o LILP.
