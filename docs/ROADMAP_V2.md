# Roadmap v2.0 — o que NÃO foi implementado na v1.0

Este documento existe para registrar disciplina de escopo. Os itens abaixo
**não** estão na v1.0 e **não devem ser implementados** sem decisão explícita
do LILP/SGGD.

## 1. Autenticação federada via gov.br

A v1.0 usa o `User` padrão do Django. Imports atrás de `get_user_model()` em
todos os apps para que a substituição por um modelo customizado em v2.0 seja
indolor.

A v2.0 deve seguir:

- Identidade visual oficial do Governo SP
- Padrões de UX do Portal Único SP.GOV.BR (Decreto Estadual nº 69.056/2024)
- Política de Privacidade atualizada com DPO designado

## 2. Calculadora de Custo do Ciclo de Vida (LCC)

Inspiração: ferramenta da Upphandlingsmyndigheten (Suécia).

Bloqueio na v1.0: requer base de fatores de emissão e curvas de energia
ainda não catalogadas no contexto brasileiro de contratações públicas.

## 3. Pacote de Sustentabilidade / Carrinho de Critérios

Montagem de conjunto de critérios para um objeto específico, exportável como
anexo único integrado ao TR/ETP. Requer autenticação (item 1) e camada de
sessão persistente por usuário.

## 4. API REST pública (DRF)

Para que projetos-irmãos do portfólio LILP possam consumir critérios
programaticamente:

- Projeto 3: Rede Estadual de Compras Públicas de SP
- Projeto 8: Hub de Boas Práticas
- Projeto 12: Gerador de Editais

URLs reservadas: `/api/v1/criterios/`, `/api/v1/objetos/`, `/api/v1/ods/`.

## 5. Versão em inglês

O Manual GESP prevê (página 9). Requer estrutura `i18n` ativa nos templates
(hoje desabilitada para reduzir complexidade da v1.0).

## 6. Páginas públicas de Pilotos

O campo `PilotoLicitacao.publicar_pagina` já existe no modelo, mas é mantido
sempre `False` na v1.0. A v2.0 deve:

- Definir curadoria editorial (quem aprova o que vai a público)
- Construir templates `templates/pilotos/list.html` e `templates/pilotos/detail.html`
- Adicionar rotas em `apps/pilotos/urls.py`

## 7. Assistente guiado

Modelo Anskaffelser (Noruega) — árvore de decisão que conduz o servidor até o
conjunto de critérios pertinente. Inicialmente avaliado para a v1.0 e descartado
porque os critérios PESCP ainda estão sendo populados; árvore de decisão sem
volume de conteúdo é mais ruído que sinal.

## 8. Análise de risco da cadeia de suprimentos

Modelo Hållbarhetskollen (Suécia) — base de dados de risco socioambiental por
categoria de produto e país de origem. Requer parceria internacional ainda
não formalizada.

## 9. Geração assistida por LLM de cláusulas customizadas

Possivelmente migrará para o **Projeto 12 (Gerador de Editais)** do Portfólio
LILP. A PESCP fornecerá os critérios crus via API; a customização por LLM fica
no projeto irmão.

## 10. Integrações ativas

- **BEC-SP** — Bolsa Eletrônica de Compras de SP
- **CADTERC** — Cadastro de Serviços Terceirizados
- **PNCP** — Portal Nacional de Contratações Públicas (Lei 14.133/2021)
- **Portal da Transparência SP**

Todas essas integrações exigem definição de protocolo e termo de cooperação
técnica entre SGGD e órgão central.

## 11. Sistema de comentários / avaliação por servidores

Permitir que servidores marquem critérios como úteis, comentem em fichas e
sugiram melhorias. Requer autenticação (item 1) e moderação editorial.

## 12. Notificações por e-mail

Quando uma norma for revogada, notificar todos os critérios que a referenciam.
Requer integração com SMTP institucional.

## 13. Versão impressa anual

Publicação anual em PDF consolidando todos os critérios. Pode usar o template
de exportação PDF como base. Requer infraestrutura de build offline.

## 14. Dashboard de uso

Para o LILP acompanhar quais critérios são mais consultados/exportados, por
unidade compradora etc. Requer analytics (item LGPD na v1.0 inativo).

---

**Importante**: itens marcados como "fora de escopo" não significam que serão
implementados depois. Cada item entra no Sprint Planning seguinte do Portfólio
2026 (ou no Portfólio 2027) com avaliação custo/benefício própria.
