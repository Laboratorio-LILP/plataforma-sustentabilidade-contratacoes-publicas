"""Cria/atualiza páginas institucionais e legais com conteúdo placeholder.

Idempotente: identifica páginas por slug. Em rerun, NÃO sobrescreve
conteúdo se já tiver sido editado pelo time (heurística: se o
conteúdo atual difere do placeholder canônico, considera editado).
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.conteudo.models import PaginaInstitucional

AVISO_PROVISORIO = (
    '<div class="sp-aviso sp-aviso--provisorio" role="status">'
    '<strong>[CONTEÚDO PROVISÓRIO — AGUARDA VALIDAÇÃO]</strong> '
    "Esta página está em validação jurídica e editorial pelo LILP/SGGD. "
    "Sua versão final será publicada antes do lançamento oficial v1.0 (junho/2026)."
    "</div>"
)

PAGINAS = [
    # ---------------------------- Institucionais ----------------------------
    (
        "sobre",
        "Sobre a PESCP",
        10,
        f"""{AVISO_PROVISORIO}
<p>A <strong>Plataforma Estadual de Sustentabilidade em Contratações Públicas (PESCP)</strong> é um
instrumento digital e consultivo do Governo do Estado de São Paulo, desenvolvido pelo Laboratório de
Inovação em Logística Pública (LILP), da Secretaria de Gestão e Governo Digital (SGGD).</p>

<p>A PESCP apoia servidores públicos paulistas na integração sistemática de critérios de sustentabilidade
nas aquisições de bens, contratações de serviços e obras, em conformidade com a Lei 14.133/2021,
artigos 5º e 11, IV.</p>

<h2>Origem do conteúdo</h2>
<p>O acervo de critérios é compilado e atomizado a partir do Guia Nacional de Contratações Sustentáveis 2024
da AGU, do Guia de Compras Públicas Sustentáveis 2025 da Prefeitura de São Paulo e de materiais
complementares produzidos em parceria com USP, UNESP, UNICAMP e PNUD.</p>

<h2>Alinhamento com a Agenda 2030</h2>
<p>A estrutura temática da plataforma está organizada pelos 17 Objetivos de Desenvolvimento Sustentável (ODS)
da Agenda 2030 das Nações Unidas, permitindo que cada critério seja conectado às metas globais que ajuda a alcançar.</p>
""",
    ),
    (
        "governanca",
        "Governança",
        20,
        f"""{AVISO_PROVISORIO}
<p>A PESCP é mantida pelo LILP (Laboratório de Inovação em Logística Pública), unidade interna da SGGD,
instituído pela Resolução SGGD nº 38/2024.</p>

<h2>Estrutura de decisão</h2>
<ul>
  <li><strong>Curadoria editorial</strong>: equipe técnica do LILP.</li>
  <li><strong>Validação jurídica</strong>: PGE-SP (a confirmar pós-MVP).</li>
  <li><strong>Conteúdo</strong>: USP, UNESP, UNICAMP, PNUD (parceria institucional).</li>
  <li><strong>Operação técnica</strong>: SGGD/LILP, em integração futura com a Prodesp.</li>
</ul>

<h2>Ciclo de vida do conteúdo</h2>
<p>Critérios passam por três estágios: <em>Rascunho → Publicado → Arquivado</em>. Cada alteração é registrada
em histórico auditável (django-simple-history).</p>
""",
    ),
    (
        "metodologia",
        "Metodologia",
        30,
        f"""{AVISO_PROVISORIO}
<p>A PESCP segue paradigma arquitetural inspirado em quatro plataformas europeias de referência:
Upphandlingsmyndigheten (Suécia), MVI Criteria (Holanda), GPP Criteria Ireland e Anskaffelser (Noruega).</p>

<h2>Estrutura atômica do critério</h2>
<p>Cada critério é uma instrução pronta para uso pelo servidor público, com cinco seções fixas:</p>
<ol>
  <li><strong>Texto da Providência</strong> — trecho copiável para inserção em ETP, TR/PB, edital ou contrato.</li>
  <li><strong>Determinações Principais</strong> — sumarização das obrigações normativas.</li>
  <li><strong>Justificativa Técnica</strong> — problema socioambiental endereçado.</li>
  <li><strong>Método de Verificação</strong> — como comprovar atendimento em fase de execução.</li>
  <li><strong>Precauções e Ressalvas</strong> — riscos, casos de não aplicação, alertas jurisprudenciais.</li>
</ol>

<h2>Classificação multidimensional</h2>
<p>Cada critério é classificado por:</p>
<ul>
  <li><strong>Objeto contratual</strong>: ex. Pilhas e Baterias, Veículos, Limpeza, Lixo Tecnológico.</li>
  <li><strong>Fase do processo</strong>: ETP, TR/PB, Edital, Execução, Fiscalização.</li>
  <li><strong>Nível de ambição</strong>: Básico, Intermediário, Avançado — paradigma sueco.</li>
  <li><strong>Tipo de contratação</strong>: Bens, Serviços, Serviços de Engenharia, Obras.</li>
</ul>
""",
    ),
    (
        "parceiros",
        "Parceiros",
        40,
        f"""{AVISO_PROVISORIO}
<h2>Parceria institucional</h2>
<ul>
  <li><strong>USP — Universidade de São Paulo</strong></li>
  <li><strong>UNESP — Universidade Estadual Paulista</strong></li>
  <li><strong>UNICAMP — Universidade Estadual de Campinas</strong></li>
  <li><strong>PNUD — Programa das Nações Unidas para o Desenvolvimento</strong></li>
</ul>
<p>A parceria fornece curadoria acadêmica do conteúdo e revisão técnica dos critérios. A operação da
plataforma é responsabilidade exclusiva da SGGD/LILP.</p>
""",
    ),
    (
        "contato",
        "Contato",
        50,
        f"""{AVISO_PROVISORIO}
<address>
<p><strong>Laboratório de Inovação em Logística Pública (LILP)</strong></p>
<p>Secretaria de Gestão e Governo Digital — SGGD</p>
<p>Av. Rangel Pestana, 300 — Sé — São Paulo/SP</p>
<p>E-mail institucional: <a href="mailto:lab.sggd@sp.gov.br">lab.sggd@sp.gov.br</a></p>
</address>
""",
    ),

    # ----------------------------- Legais -----------------------------------
    (
        "transparencia",
        "Transparência e Acesso à Informação",
        100,
        f"""{AVISO_PROVISORIO}
<p>Esta página reúne informações de transparência ativa da PESCP, atendendo à Lei nº 12.527/2011 (LAI)
e ao Decreto Federal nº 7.724/2012.</p>

<h2>Quem somos</h2>
<p>A PESCP é projeto do Laboratório de Inovação em Logística Pública (LILP), vinculado à Secretaria de
Gestão e Governo Digital (SGGD) do Estado de São Paulo. Instituído pela Resolução SGGD nº 38/2024.</p>

<h2>Legislação aplicável</h2>
<ul>
  <li><strong>Lei nº 14.133/2021</strong> — Nova Lei de Licitações e Contratos Administrativos.</li>
  <li><strong>Lei nº 12.527/2011</strong> — Lei de Acesso à Informação (LAI).</li>
  <li><strong>Lei nº 13.709/2018</strong> — Lei Geral de Proteção de Dados (LGPD).</li>
  <li><strong>Decreto Estadual nº 67.799/2023</strong> — Estratégia de Governo Digital.</li>
  <li><strong>Decreto Estadual nº 69.056/2024</strong> — Portal único SP.GOV.BR.</li>
  <li><strong>Resolução SGGD nº 38/2024</strong> — Institui o LILP.</li>
</ul>

<h2>Canais oficiais do Governo de SP</h2>
<ul>
  <li><a href="http://www.transparencia.sp.gov.br/" target="_blank" rel="noopener noreferrer">Portal da Transparência</a></li>
  <li><a href="http://www.sic.sp.gov.br/" target="_blank" rel="noopener noreferrer">Sistema de Informações ao Cidadão (SIC)</a></li>
  <li><a href="https://www.ouvidoria.sp.gov.br/" target="_blank" rel="noopener noreferrer">Ouvidoria Geral do Estado</a></li>
</ul>
""",
    ),
    (
        "acessibilidade",
        "Acessibilidade",
        110,
        f"""{AVISO_PROVISORIO}
<p>A PESCP foi desenvolvida em conformidade com o <strong>eMAG 3.1</strong> (Modelo de Acessibilidade em
Governo Eletrônico — Portaria SISP nº 3/2007) e as <strong>WCAG 2.0 nível AA</strong>.</p>

<h2>Recursos disponíveis</h2>
<ul>
  <li><strong>Atalhos de teclado</strong>: <kbd>Alt+1</kbd> conteúdo, <kbd>Alt+2</kbd> menu,
      <kbd>Alt+3</kbd> busca, <kbd>Alt+4</kbd> rodapé.</li>
  <li><strong>Alto contraste</strong>: ativável pela barra superior (preto/amarelo, WCAG AAA).</li>
  <li><strong>Aumentar/diminuir fonte</strong>: ajuste de 87,5% a 150% via barra superior.</li>
  <li><strong>Navegação por teclado completa</strong>: Tab, Shift+Tab, Enter, ESC, setas.</li>
  <li><strong>Foco visível</strong>: 3px amarelo Pantone 123 com offset.</li>
  <li><strong>Leitor de tela</strong>: estrutura semântica HTML5 com landmarks e ARIA.</li>
</ul>

<h2>Reportar problemas</h2>
<p>Encontrou uma barreira de acessibilidade? Escreva para
<a href="mailto:lab.sggd@sp.gov.br">lab.sggd@sp.gov.br</a> com o nome da página e a descrição do problema.</p>
""",
    ),
    (
        "politica-de-privacidade",
        "Política de Privacidade",
        120,
        f"""{AVISO_PROVISORIO}
<p>A PESCP segue a <strong>Lei nº 13.709/2018 (LGPD)</strong> no tratamento de dados pessoais.</p>

<h2>Que dados coletamos</h2>
<p>Na v1.0, a plataforma é integralmente pública e <strong>não coleta dados pessoais</strong> de usuários
visitantes. Cookies estritamente necessários são utilizados apenas para CSRF e funcionamento da sessão.</p>

<h2>Direitos do titular</h2>
<p>Caso uma versão futura adote autenticação federada via gov.br, esta política será atualizada para
descrever em detalhe o tratamento de dados pessoais nos termos da LGPD.</p>

<h2>Encarregado de dados (DPO)</h2>
<p>Designação a ser publicada antes do tratamento de dados pessoais sensíveis. Contato preliminar:
<a href="mailto:lab.sggd@sp.gov.br">lab.sggd@sp.gov.br</a>.</p>
""",
    ),
    (
        "politica-de-cookies",
        "Política de Cookies",
        130,
        f"""{AVISO_PROVISORIO}
<h2>Que cookies usamos</h2>
<table class="sp-tabela-cookies">
  <thead>
    <tr><th>Categoria</th><th>Finalidade</th><th>Bloqueável?</th></tr>
  </thead>
  <tbody>
    <tr><td>Essenciais</td><td>Sessão, CSRF, preferências de acessibilidade</td><td>Não — indispensáveis ao funcionamento.</td></tr>
    <tr><td>Funcionalidades</td><td>Lembrar última seção visitada, filtros recentes</td><td>Sim.</td></tr>
    <tr><td>Análise de uso</td><td>Medição agregada de tráfego (não ativa na v1.0)</td><td>Sim.</td></tr>
  </tbody>
</table>

<h2>Gestão de consentimento</h2>
<p>A escolha do usuário é registrada localmente (<code>localStorage</code> sob a chave
<code>sp-lgpd-consent</code>) com versão da política, timestamp e categorias autorizadas.
Nenhum cookie de análise é disparado antes do consentimento explícito.</p>
""",
    ),
    (
        "mapa-do-site",
        "Mapa do site",
        140,
        f"""{AVISO_PROVISORIO}
<ul class="sp-mapa-site">
  <li><a href="/">Início</a></li>
  <li><a href="/criterios/">Critérios</a>
    <ul>
      <li><a href="/objetos/">Por objeto contratual</a></li>
      <li><a href="/ods/">Por ODS</a></li>
    </ul>
  </li>
  <li><a href="/glossario/">Glossário</a></li>
  <li><a href="/sobre/">Sobre</a></li>
  <li><a href="/governanca/">Governança</a></li>
  <li><a href="/metodologia/">Metodologia</a></li>
  <li><a href="/parceiros/">Parceiros</a></li>
  <li><a href="/contato/">Contato</a></li>
  <li>Legal
    <ul>
      <li><a href="/transparencia/">Transparência</a></li>
      <li><a href="/acessibilidade/">Acessibilidade</a></li>
      <li><a href="/politica-de-privacidade/">Política de Privacidade</a></li>
      <li><a href="/politica-de-cookies/">Política de Cookies</a></li>
      <li><a href="/fale-conosco/">Fale Conosco</a></li>
    </ul>
  </li>
</ul>
""",
    ),
    (
        "fale-conosco",
        "Fale Conosco",
        150,
        f"""{AVISO_PROVISORIO}
<h2>Canais de contato</h2>
<dl class="sp-canais-contato">
  <dt>E-mail institucional</dt>
  <dd><a href="mailto:lab.sggd@sp.gov.br">lab.sggd@sp.gov.br</a></dd>

  <dt>Endereço</dt>
  <dd>Av. Rangel Pestana, 300 — Sé — São Paulo/SP</dd>

  <dt>Ouvidoria Geral do Estado</dt>
  <dd><a href="https://www.ouvidoria.sp.gov.br/" target="_blank" rel="noopener noreferrer">ouvidoria.sp.gov.br</a></dd>

  <dt>Sistema de Informações ao Cidadão (SIC)</dt>
  <dd><a href="http://www.sic.sp.gov.br/" target="_blank" rel="noopener noreferrer">sic.sp.gov.br</a></dd>
</dl>
""",
    ),
]


class Command(BaseCommand):
    help = "Cria/atualiza páginas institucionais e legais com conteúdo placeholder (idempotente)."

    @transaction.atomic
    def handle(self, *args, **options):
        criadas = 0
        atualizadas = 0
        for slug, titulo, ordem, conteudo in PAGINAS:
            obj, created = PaginaInstitucional.objects.get_or_create(
                slug=slug,
                defaults={
                    "titulo": titulo,
                    "ordem": ordem,
                    "conteudo": conteudo,
                    "publicada": True,
                },
            )
            if created:
                criadas += 1
                continue
            # Atualiza ordem e título sempre; conteúdo só se ainda for o placeholder
            mudou = False
            if obj.ordem != ordem:
                obj.ordem = ordem
                mudou = True
            if obj.titulo != titulo:
                obj.titulo = titulo
                mudou = True
            if AVISO_PROVISORIO in obj.conteudo:
                obj.conteudo = conteudo
                mudou = True
            if mudou:
                obj.save()
                atualizadas += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Páginas institucionais sincronizadas — {criadas} criadas, {atualizadas} atualizadas, "
                f"{PaginaInstitucional.objects.count()} total."
            )
        )
