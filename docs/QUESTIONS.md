# Perguntas em aberto para o LILP

Conforme orientação do prompt institucional (seção 17): "Se algo não estiver
escrito e for indispensável, registre como pergunta em `docs/QUESTIONS.md` em
vez de inventar".

## 1. Logos institucionais em SVG vetorial

**Status atual**: usei os PNGs reaproveitados do repositório BDLP em
`static/img/logos/governo-sp/`, `static/img/logos/sggd/` e `static/img/logos/lilp/`.

**Pergunta**: vocês têm SVGs vetoriais oficiais dos três logotipos (Governo SP
horizontal, SGGD, LILP) que seguem o Manual GESP v1.6? Em caso positivo, qual o
fluxo para receber os arquivos finais? Em caso negativo, devo encomendar a
vetorização ou usar PNGs definitivamente para a v1.0?

## 2. Ícones oficiais dos 17 ODS

**Status atual**: o `create_initial_ods` cria os 17 registros com nome, descrição e
cor oficial da ONU, mas o campo `icone` fica vazio. O detalhe da ODS exibe apenas
o número estilizado.

**Pergunta**: vocês podem subir os 17 ícones oficiais da ONU em PNG/SVG para
`media/ods/ods-NN.png`, ou prefere que eu baixe da fonte oficial? Há
licenciamento a respeitar (a ONU permite uso institucional sem retoque).

## 3. Categorias de objetos contratuais — taxonomia completa

**Status atual**: o modelo `ObjetoContratual` aceita hierarquia de 2 níveis, mas
a taxonomia completa virá pela planilha de seed.

**Pergunta**: vocês têm a lista canônica das ~40 categorias do Guia AGU 2024 já
mapeada para o paradigma da PESCP, ou parte do trabalho dos parceiros acadêmicos
é justamente essa categorização?

## 4. Estrutura de valor estimado/homologado em pilotos

**Status atual**: `PilotoLicitacao.valor_estimado` e `valor_homologado` são
`DecimalField(14, 2)` — suporta até R$ 999.999.999.999,99.

**Pergunta**: faz sentido manter campo separado para diferença de valor por
critério (economia LCC estimada já cobre isso em `AvaliacaoImpacto`)? Ou
gostaríamos de capturar economia por critério aplicado em uma tabela auxiliar?

## 5. Quem pode publicar / arquivar critério

**Status atual**: qualquer usuário staff com permissão de Criterio.change pode
chamar a ação "Publicar selecionados" no Admin.

**Pergunta**: precisamos de um fluxo editorial multinível (autor → revisor →
publicador)? Se sim, será na v1.0 ou v2.0? O prompt indica explicitamente "sem
fluxo editorial multinível" mas registro a pergunta para confirmar.

## 6. Validação jurídica das páginas legais

**Status atual**: as 6 páginas legais (transparência, acessibilidade, política
de privacidade, política de cookies, mapa do site, fale conosco) são criadas
por `create_initial_pages` com conteúdo placeholder marcado como
"[CONTEÚDO PROVISÓRIO — AGUARDA VALIDAÇÃO]".

**Pergunta**: a validação jurídica ficará por conta da PGE-SP? Há previsão de
ciclo de revisão antes do lançamento de junho/2026?

## 7. SEI vs PNCP — qual identificador usar em pilotos

**Status atual**: `PilotoLicitacao` tem `numero_processo_sei` e `numero_edital`,
mas não tem `numero_pncp`.

**Pergunta**: o PNCP (Portal Nacional de Contratações Públicas, Lei 14.133/2021)
gera um número universal. Devo adicionar `numero_pncp` ao modelo desde a v1.0
para futura integração?

## 8. Multilíngue — escopo do EN em v2.0

**Status atual**: PT-BR único na v1.0; EN registrado no roadmap.

**Pergunta**: o EN será apenas das páginas institucionais ou também dos
critérios? A tradução técnica dos critérios é trabalho significativo
(80% do volume textual da plataforma).

## 9. CONAB, CADTERC, BEC integrações

**Status atual**: nenhuma integração ativa na v1.0; roadmap menciona BEC-SP e
CADTERC.

**Pergunta**: existe convênio formalizado SGGD ↔ Prodesp para acesso programático
a esses sistemas? Em caso negativo, o esforço de integração será da Prodesp ou
do LILP?

## 10. Telemetria e métricas de uso

**Status atual**: zero telemetria na v1.0 (analytics opt-in mas inativo).

**Pergunta**: o LILP precisa de alguma métrica básica desde o lançamento (número
de visitas, critérios mais consultados, exportações por dia)? Em caso positivo,
podemos usar Matomo self-hosted respeitando LGPD (sem cookies, IP truncado).
