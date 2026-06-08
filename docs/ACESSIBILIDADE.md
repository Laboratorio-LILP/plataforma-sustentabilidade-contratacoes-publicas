# Acessibilidade — PESCP

Conformidade exigida pelo prompt institucional:

- **eMAG 3.1** (Modelo de Acessibilidade em Governo Eletrônico — Portaria SISP nº 3/2007)
- **WCAG 2.0 nível AA**
- **Lei 13.146/2015** (Lei Brasileira de Inclusão da Pessoa com Deficiência)

## Recursos implementados

### Estrutura semântica

- `<!DOCTYPE html>` HTML5
- `<html lang="pt-BR" dir="ltr">` em todas as páginas (eMAG R1.5)
- `<title>` único e descritivo por página (eMAG R3.2)
- Landmarks: `<header role="banner">`, `<nav role="navigation">`,
  `<main role="main">`, `<footer role="contentinfo">`, `<aside role="region">`
- Hierarquia de cabeçalhos correta — apenas um `<h1>` por página

### Skip-links (eMAG R3.1 / WCAG 2.4.1)

Quatro links visualmente ocultos até receberem foco — saltam para conteúdo,
menu, busca e rodapé. Veja `templates/_partials/_skip_links.html`.

```
Alt+1 → conteúdo principal (#sp-conteudo)
Alt+2 → menu principal (#sp-menu)
Alt+3 → campo de busca (#sp-busca-input)
Alt+4 → rodapé (#sp-rodape)
```

Implementação dupla: `accesskey="1..4"` no HTML + listener `keydown` em `main.js`
porque alguns browsers ignoram `accesskey` em `<main>`/`<nav>`/`<footer>`.

### Foco visível (eMAG R5.4 / WCAG 2.4.7)

Outline 3px amarelo Pantone 123 (`--sp-foco: #FFB800`) com offset 2px, aplicado
globalmente via `*:focus-visible` em `static/css/style.css`.

### Modo alto contraste (WCAG AAA)

Toggle pela barra GovSP. Paleta preto/amarelo aplicada via classe
`body.sp-alto-contraste` em `static/css/sp-design-system.css`. Persistência em
`localStorage` sob chave `sp-a11y:contraste`.

Estratégia: seletor universal com `!important` sobrescreve **qualquer** cor
declarada em componentes. SVGs e imagens são preservados via `:not()`.

### Escala de fonte ajustável

Controles A+/A− na barra GovSP. Aplica classes `sp-fonte-aumentada-1..4` ou
`sp-fonte-diminuida-1..2` no `<html>`, ajustando `font-size` de 87.5% até 150%.
Persistência em `localStorage` sob chave `sp-a11y:fonte-escala`.

### ARIA e atributos

- `aria-current="page"` no item ativo do menu (via context processor)
- `aria-expanded` no botão hambúrguer
- `aria-pressed` no botão de alto contraste
- `aria-label` em links sem texto visível (apenas ícones)
- `aria-labelledby` em sections com cabeçalho
- `role="dialog"` + `aria-modal="true"` apenas no modal de cookies — banner usa
  `role="region"` para não bloquear navegação

### Imagens

- Imagens informativas têm `alt` descritivo
- Imagens decorativas têm `alt=""`
- Ícones SVG inline têm `aria-hidden="true" focusable="false"`
- Ícones com função têm `aria-label` no elemento pai (botão/link)

### Formulários

- `<label for="...">` ou `aria-label` em todos os campos
- `<fieldset>` + `<legend>` em grupos lógicos
- Mensagens de erro com `aria-describedby` (futura iteração)

### JavaScript

- Zero inline event handlers — todo JS via `addEventListener` em `main.js`
- Compatível com CSP `script-src 'self'` (sem `unsafe-inline`)
- Funções defensivas — se um elemento esperado não existir, o módulo retorna
  silenciosamente

### Navegação por teclado

- Tab/Shift+Tab navega todos os elementos focáveis na ordem visual
- Enter ativa links e botões
- Espaço alterna botões toggle
- ESC fecha modal de cookies e menu hambúrguer
- Setas movem em `<select>`

### Tabelas

Quando usadas (ex.: política de cookies), seguem o padrão:

```html
<table class="sp-tabela-cookies">
  <caption class="sr-only">Cookies utilizados pelo portal</caption>
  <thead>
    <tr><th scope="col">Categoria</th>...</tr>
  </thead>
  <tbody>
    <tr><td>Essenciais</td>...</tr>
  </tbody>
</table>
```

## Como auditar

### Local

```bash
make a11y
# Equivalente:
python tools/audit_a11y.py
```

Requer Node 18+ no host (chama `npx pa11y`).

URLs auditadas:
- Home, Critérios (lista), Objetos, ODS, Glossário, Busca
- Sobre, Governança, Metodologia, Parceiros, Contato
- Transparência, Acessibilidade, Política de Privacidade, Política de Cookies,
  Mapa do Site, Fale Conosco

### Lighthouse

Em Chrome DevTools incognito:

1. Abra a página
2. Lighthouse → Acessibilidade → Generate report

Alvo mínimo: **score ≥ 90** na Home e na Lista de Critérios (DoD).

### Manual

Checklist mínimo antes de cada release:

- [ ] Navegação completa por teclado sem mouse
- [ ] Modo alto contraste aplica e persiste entre páginas
- [ ] Aumentar fonte 4× ainda mantém layout funcional
- [ ] Skip-links aparecem ao Tab a partir do topo
- [ ] Atalhos Alt+1..4 funcionam
- [ ] Leitor de tela (NVDA/JAWS/VoiceOver) anuncia título da página e landmarks
- [ ] Foco visível em todos os elementos interativos
- [ ] Banner de cookies não prende o foco do leitor de tela

## Reportar problemas

Encontrou uma barreira de acessibilidade? E-mail:
[lab.sggd@sp.gov.br](mailto:lab.sggd@sp.gov.br) — assunto "PESCP — Acessibilidade".
