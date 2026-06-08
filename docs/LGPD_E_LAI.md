# LGPD e LAI — PESCP

## Lei Geral de Proteção de Dados (Lei 13.709/2018)

### Coleta de dados

Na v1.0, a PESCP é **integralmente pública e não coleta dados pessoais** de
visitantes. Cookies estritamente necessários são utilizados apenas para CSRF e
manutenção da sessão.

### Banner de cookies

Implementado em `templates/_partials/_banner_cookies.html`, controlado pelo
módulo `Cookies` em `static/js/main.js`.

Características:

- **Não-modal** (`role="region"`) — não bloqueia navegação por teclado nem leitor de tela.
- **3 categorias**: Essenciais (obrigatórios), Funcionalidades (opt-in),
  Análise de uso (opt-in, não ativo na v1.0).
- **Modal de personalização** (`role="dialog" aria-modal="true"`) abre apenas
  ao clicar "Personalizar".
- **Persistência** em `localStorage` sob chave `sp-lgpd-consent` com:
  ```json
  {
    "versao": 1,
    "timestamp": "2026-05-12T14:32:00.000Z",
    "categorias": {
      "necessarios": true,
      "funcionalidades": true,
      "analytics": false
    }
  }
  ```

> Nenhum cookie de análise é disparado antes do consentimento explícito. Quando
> uma versão futura ativar analytics, o `CONSENT_VERSION` em `main.js` deve ser
> incrementado para reapresentar o banner.

### Encarregado de dados (DPO)

Designação a ser publicada quando houver tratamento de dados pessoais sensíveis
(v2.0+ com autenticação gov.br). Na v1.0, o contato preliminar é
[lab.sggd@sp.gov.br](mailto:lab.sggd@sp.gov.br).

### Página de Política de Privacidade

`/politica-de-privacidade/` — gerada pelo `create_initial_pages` com aviso
amarelo "versão inicial — pendente de validação jurídica".

### Página de Política de Cookies

`/politica-de-cookies/` — tabela das categorias, descrição da gestão de
consentimento.

## Lei de Acesso à Informação (Lei 12.527/2011)

### Banner LAI na home

Implementado em `templates/_partials/_banner_lai.html`, exibido na home logo
após o hero. Borda lateral em `--sp-vermelho`, fundo preto, link para
`/transparencia/`.

> Decreto Federal nº 7.724/2012, art. 7º, exige seção específica de transparência
> ativa acessível a partir da página inicial.

### Página de Transparência

`/transparencia/` — gerada pelo `create_initial_pages`. Cobre:

- Quem somos (LILP/SGGD)
- Legislação aplicável (LAI, LGPD, Lei 14.133/2021 etc.)
- Resolução SGGD nº 38/2024
- Canais oficiais do Governo de SP (Portal da Transparência, SIC, Ouvidoria)

### Outros canais

Links no rodapé apontam para:

- [Portal da Transparência SP](http://www.transparencia.sp.gov.br/)
- [Sistema de Informações ao Cidadão (SIC)](http://www.sic.sp.gov.br/)
- [Ouvidoria Geral do Estado](https://www.ouvidoria.sp.gov.br/)

## Aviso de versão inicial

Em todas as páginas legais e institucionais, um banner amarelo claramente
identifica:

> **Versão inicial:** esta página está em validação jurídica e editorial pelo
> LILP/SGGD. A redação definitiva será publicada antes do lançamento oficial em
> junho/2026.

Implementado via classe `.sp-pagina-legal__aviso` no template
`templates/conteudo/pagina_legal.html`.

## Faixa de aviso de versão (em todas as páginas)

Faixa amarela discreta logo abaixo da barra GovSP, fechável **por sessão**
(não persiste entre sessões — controlado por `sessionStorage`).

> Versão 1.0 (junho/2026) — conteúdo em validação contínua. Sua sugestão é
> bem-vinda: lab.sggd@sp.gov.br

Implementado em `templates/_partials/_aviso_versao_inicial.html` e controlado
pelo módulo `AvisoVersao` em `main.js`.
