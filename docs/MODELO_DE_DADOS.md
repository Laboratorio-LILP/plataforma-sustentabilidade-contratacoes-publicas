# Modelo de Dados — PESCP v1.0

## Diagrama ER (Mermaid)

```mermaid
erDiagram
    Ods ||--o{ Criterio_ods : "M2M"
    NormaLegal ||--o{ Criterio_normas : "M2M"
    SeloCertificacao ||--o{ Criterio_selos : "M2M"
    Tag ||--o{ Criterio_tags : "M2M"
    ObjetoContratual ||--o{ Criterio : "FK"
    ObjetoContratual ||--o{ ObjetoContratual : "parent (FK self)"
    Criterio ||--o{ Criterio_ods : ""
    Criterio ||--o{ Criterio_normas : ""
    Criterio ||--o{ Criterio_selos : ""
    Criterio ||--o{ Criterio_tags : ""
    Criterio ||--o{ PilotoLicitacao_criterios : "M2M"
    PilotoLicitacao ||--o| AvaliacaoImpacto : "1:1"
    PilotoLicitacao }o--|| ObjetoContratual : "FK"
    DocumentoApoio }o--|| ObjetoContratual : "FK (opcional)"
    TermoGlossario ||--o{ TermoGlossario_normas : "M2M"
    NormaLegal ||--o{ NormaLegal : "revogada_por (FK self)"

    Ods {
        smallint numero PK
        string nome
        slug slug
        string descricao_curta
        text descricao_longa
        string cor_hex
        image icone
        json metas
    }
    NormaLegal {
        bigint id PK
        string titulo_curto
        string titulo_completo
        slug slug
        string tipo
        string esfera
        string numero
        date data_publicacao
        date data_vigencia
        bool revogada
        fk revogada_por_id
        url link_oficial
        text ementa
    }
    SeloCertificacao {
        bigint id PK
        string nome
        slug slug
        text descricao
        url link_oficial
        image logo
        string tipo
    }
    Tag {
        bigint id PK
        string nome
        slug slug
    }
    ObjetoContratual {
        bigint id PK
        string nome
        slug slug
        text descricao
        fk parent_id
        image icone
        int ordem
        bool ativo
    }
    Criterio {
        bigint id PK
        string codigo UK
        string titulo
        slug slug
        fk objeto_contratual_id
        string tipo_contratacao
        string fase_processo
        string nivel_ambicao
        text texto_providencia
        text determinacoes_principais
        text justificativa_tecnica
        text metodo_verificacao
        text precaucoes
        string fonte
        string status
        fk criado_por_id
        datetime publicado_em
        tsvector search_vector
    }
    PilotoLicitacao {
        bigint id PK
        string codigo UK
        string titulo
        string unidade_compradora
        string tipo_contratacao
        fk objeto_contratual_id
        string estagio_atual
        decimal valor_estimado
        decimal valor_homologado
        date data_inicio
        date data_homologacao
        date data_conclusao
        string numero_processo_sei
        string numero_edital
        text observacoes
        bool publicar_pagina
    }
    AvaliacaoImpacto {
        bigint id PK
        fk piloto_id UK
        decimal economia_lcc_estimada
        decimal reducao_co2_estimada_ton
        text impactos_sociais
        text impactos_ambientais
        text licoes_aprendidas
        text recomendacoes_para_proximas_contratacoes
        date data_avaliacao
    }
    PaginaInstitucional {
        bigint id PK
        string titulo
        slug slug UK
        text conteudo
        int ordem
        bool publicada
        string meta_description
    }
    TermoGlossario {
        bigint id PK
        string termo UK
        slug slug
        text definicao
        string sigla
    }
    DocumentoApoio {
        bigint id PK
        string titulo
        text descricao
        file arquivo
        string tipo
        fk objeto_contratual_id
        int tamanho_bytes
        string extensao
    }
```

## Tabela de modelos

| App        | Modelo                | Versionado | Finalidade |
| ---------- | --------------------- | :--------: | ---------- |
| core       | Tag                   |     —      | Palavras-chave livres para indexação adicional |
| normas     | Ods                   |     —      | 17 ODS oficiais da Agenda 2030 ONU |
| normas     | NormaLegal            |    ✓       | Lei, decreto, IN, resolução, NBR — qualquer norma referenciada |
| normas     | SeloCertificacao      |     —      | INMETRO, FSC, Procel/PBE, ANP, CTF/APP-IBAMA etc. |
| criterios  | ObjetoContratual      |     —      | Taxonomia hierárquica (2 níveis) de objetos contratuais |
| criterios  | Criterio              |    ✓       | Entidade central — instrução pronta para uso pelo servidor |
| pilotos    | PilotoLicitacao       |     —      | Caso piloto de aplicação dos critérios (Admin-only na v1.0) |
| pilotos    | AvaliacaoImpacto      |     —      | Avaliação socioambiental e econômica do piloto |
| conteudo   | PaginaInstitucional   |    ✓       | Páginas estáticas (institucionais + legais) |
| conteudo   | TermoGlossario        |     —      | Termos do glossário |
| conteudo   | DocumentoApoio        |     —      | Arquivos de apoio (modelos de cláusula, planilhas, guias) |

## Choices fechados

- **TipoContratacao**: `BENS`, `SERVICOS`, `SERVICOS_ENGENHARIA`, `OBRAS`
- **FaseProcesso**: `ETP`, `TR_PB`, `EDITAL`, `EXECUCAO`, `FISCALIZACAO`
- **NivelAmbicao**: `BASICO`, `INTERMEDIARIO`, `AVANCADO` (paradigma sueco)
- **StatusCriterio**: `RASCUNHO`, `PUBLICADO`, `ARQUIVADO`
- **NormaLegal.Tipo**: 12 valores (constitucional, lei federal/estadual/municipal, decreto, IN, resolução, portaria, NBR, internacional, outro)
- **NormaLegal.Esfera**: `FEDERAL`, `ESTADUAL`, `MUNICIPAL`, `INTERNACIONAL`
- **SeloCertificacao.Tipo**: `NACIONAL`, `INTERNACIONAL`, `SETORIAL`
- **PilotoLicitacao.Estagio**: `PLANEJAMENTO`, `EDITAL_PUBLICADO`, `EM_LICITACAO`, `HOMOLOGADO`, `EM_EXECUCAO`, `CONCLUIDO`, `CANCELADO`
- **DocumentoApoio.Tipo**: `MODELO_CLAUSULA`, `PLANILHA`, `GUIA`, `RELATORIO_IMPACTO`, `OUTRO`

## Chaves naturais para o seed

| Modelo                | Chave natural |
|-----------------------|---------------|
| Ods                   | `numero` |
| NormaLegal            | `slug` |
| SeloCertificacao      | `slug` |
| Tag                   | `slug` (ou `nome`) |
| ObjetoContratual      | `slug` |
| Criterio              | `codigo` (formato `CRIT-AAAA-NNN`) |
| PaginaInstitucional   | `slug` |
| TermoGlossario        | `slug` |

O importador `import_pescp_seed` usa essas chaves para identificar registros e
fazer upsert idempotente.
