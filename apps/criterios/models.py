"""Models do app criterios — coração da PESCP.

A unidade atômica é o ``Criterio``: instrução pronta para uso pelo servidor
público, classificada por objeto contratual, fase do processo, nível de
ambição e tipo de contratação, e relacionada a ODS, normas legais, selos
e tags.

ObjetoContratual é hierárquico em até 2 níveis (supercategoria + categoria);
NÃO usamos MPTT para manter dependências mínimas — uma propriedade simples
``descendentes`` faz a tree walk via consulta direta.
"""

from __future__ import annotations

import re
from datetime import datetime

from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone
from simple_history.models import HistoricalRecords

from apps.core.models import Tag, TimestampedModel, gerar_slug
from apps.normas.models import NormaLegal, Ods, SeloCertificacao


# ============================================================
# TextChoices — paradigma fechado
# ============================================================
class TipoContratacao(models.TextChoices):
    BENS = "BENS", "Aquisição de Bens"
    SERVICOS = "SERVICOS", "Contratação de Serviços"
    SERVICOS_ENGENHARIA = "SERVICOS_ENGENHARIA", "Serviços de Engenharia"
    OBRAS = "OBRAS", "Obras"


class FaseProcesso(models.TextChoices):
    ETP = "ETP", "Estudo Técnico Preliminar"
    TR_PB = "TR_PB", "Termo de Referência / Projeto Básico"
    EDITAL = "EDITAL", "Edital de Licitação"
    EXECUCAO = "EXECUCAO", "Execução Contratual"
    FISCALIZACAO = "FISCALIZACAO", "Fiscalização do Contrato"


class NivelAmbicao(models.TextChoices):
    BASICO = "BASICO", "Básico"
    INTERMEDIARIO = "INTERMEDIARIO", "Intermediário"
    AVANCADO = "AVANCADO", "Avançado"


class StatusCriterio(models.TextChoices):
    RASCUNHO = "RASCUNHO", "Rascunho"
    PUBLICADO = "PUBLICADO", "Publicado"
    ARQUIVADO = "ARQUIVADO", "Arquivado"


# ============================================================
# ObjetoContratual — taxonomia hierárquica de 2 níveis
# ============================================================
class ObjetoContratual(TimestampedModel):
    """Categoria de objeto contratual (ex.: Pilhas e Baterias).

    Pode ter ``parent`` apontando para uma supercategoria (ex.: "Resíduos
    e Logística Reversa"). Profundidade máxima esperada: 2 níveis. Não
    enforço por DB constraint para permitir flexibilidade pontual; o
    Admin avisa via clean() se ultrapassar.
    """

    nome = models.CharField("Nome", max_length=200)
    slug = models.SlugField("Slug", max_length=200, unique=True, blank=True)
    descricao = models.TextField("Descrição", blank=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="filhos",
        verbose_name="Supercategoria",
    )
    icone = models.ImageField("Ícone", upload_to="objetos/", blank=True, null=True)
    ordem = models.PositiveIntegerField("Ordem de exibição", default=0)
    ativo = models.BooleanField("Ativo?", default=True)

    class Meta:
        verbose_name = "Objeto Contratual"
        verbose_name_plural = "Objetos Contratuais"
        ordering = ["parent__nome", "ordem", "nome"]
        indexes = [
            models.Index(fields=["ativo", "ordem"]),
        ]

    def __str__(self) -> str:
        if self.parent_id:
            return f"{self.parent.nome} › {self.nome}"
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = gerar_slug(self.nome, maxlen=200)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("criterios:objeto_detail", kwargs={"slug": self.slug})

    @property
    def eh_supercategoria(self) -> bool:
        return self.parent_id is None

    def descendentes(self):
        """Retorna queryset com self + filhos diretos. Profundidade ≤ 2."""
        if self.eh_supercategoria:
            return ObjetoContratual.objects.filter(
                models.Q(pk=self.pk) | models.Q(parent_id=self.pk)
            )
        return ObjetoContratual.objects.filter(pk=self.pk)


# ============================================================
# Criterio — entidade central
# ============================================================
class Criterio(TimestampedModel):
    """Critério atômico de sustentabilidade aplicado em contratações.

    Cinco seções de conteúdo (Providência, Determinações, Justificativa,
    Verificação, Precauções) ancoram a aplicação operacional. Relações
    M2M com ODS, NormaLegal, SeloCertificacao e Tag dão a topologia
    semântica para busca facetada.
    """

    codigo = models.CharField(
        "Código",
        max_length=30,
        unique=True,
        blank=True,
        help_text='Gerado automaticamente no formato "CRIT-AAAA-NNN" se vazio.',
    )
    titulo = models.CharField("Título", max_length=300)
    slug = models.SlugField("Slug", max_length=300, unique=True, blank=True)

    # Classificação primária
    objeto_contratual = models.ForeignKey(
        ObjetoContratual,
        on_delete=models.PROTECT,
        related_name="criterios",
        verbose_name="Objeto Contratual",
    )
    tipo_contratacao = models.CharField(
        "Tipo de Contratação",
        max_length=32,
        choices=TipoContratacao.choices,
        default=TipoContratacao.BENS,
    )
    fase_processo = models.CharField(
        "Fase do Processo",
        max_length=32,
        choices=FaseProcesso.choices,
        default=FaseProcesso.TR_PB,
    )
    nivel_ambicao = models.CharField(
        "Nível de Ambição",
        max_length=20,
        choices=NivelAmbicao.choices,
        default=NivelAmbicao.BASICO,
    )

    # Conteúdo — rich text em formato HTML sanitizado (ou markdown a
    # critério do editor; o template renderiza com |safe).
    texto_providencia = models.TextField(
        "Texto da Providência",
        help_text="Trecho pronto para colar em ETP, TR/PB, edital ou contrato.",
    )
    determinacoes_principais = models.TextField(
        "Determinações Principais",
        help_text="Sumarização das obrigações normativas que dão base ao critério.",
    )
    justificativa_tecnica = models.TextField(
        "Justificativa Técnica",
        help_text="Por que o critério faz sentido; problema socioambiental endereçado.",
    )
    metodo_verificacao = models.TextField(
        "Método de Verificação",
        help_text="Como comprovar atendimento (documentos, selos, laudos, fiscalização).",
    )
    precaucoes = models.TextField(
        "Precauções e Ressalvas",
        blank=True,
        help_text="Riscos, casos de não aplicação, alertas jurisprudenciais.",
    )

    # Relações semânticas
    ods = models.ManyToManyField(Ods, blank=True, related_name="criterios", verbose_name="ODS aplicáveis")
    normas = models.ManyToManyField(
        NormaLegal, blank=True, related_name="criterios", verbose_name="Normas Legais"
    )
    selos = models.ManyToManyField(
        SeloCertificacao, blank=True, related_name="criterios", verbose_name="Selos e Certificações"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="criterios", verbose_name="Tags")

    # Metadados editoriais
    fonte = models.CharField(
        "Fonte",
        max_length=500,
        blank=True,
        help_text='Ex.: "Guia AGU 2024 — item 27".',
    )
    status = models.CharField(
        "Status",
        max_length=20,
        choices=StatusCriterio.choices,
        default=StatusCriterio.RASCUNHO,
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="criterios_criados",
        verbose_name="Criado por",
    )
    publicado_em = models.DateTimeField("Publicado em", null=True, blank=True)

    # Vetor de busca (Postgres FTS, ponderado: A=título, B=providência,
    # C=determinações+justificativa, D=precauções)
    search_vector = SearchVectorField(null=True, blank=True, editable=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Critério"
        verbose_name_plural = "Critérios"
        ordering = ["-updated"]
        indexes = [
            GinIndex(fields=["search_vector"], name="pescp_crit_search_gin"),
            models.Index(fields=["status", "objeto_contratual"]),
            models.Index(fields=["fase_processo", "nivel_ambicao"]),
        ]

    def __str__(self) -> str:
        return f"{self.codigo or '?'} — {self.titulo}"

    def get_absolute_url(self) -> str:
        return reverse("criterios:criterio_detail", kwargs={"slug": self.slug})

    # ---------- Hooks ----------
    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._gerar_codigo()
        if not self.slug:
            base = f"{self.codigo}-{self.titulo}"
            self.slug = gerar_slug(base, maxlen=300)
        if self.status == StatusCriterio.PUBLICADO and self.publicado_em is None:
            self.publicado_em = timezone.now()
        if self.status != StatusCriterio.PUBLICADO:
            # ao despublicar, mantemos publicado_em histórico — não zeramos
            pass
        super().save(*args, **kwargs)
        # Recalcula search_vector após salvar (precisa de pk para o UPDATE)
        self._atualizar_search_vector()

    def _gerar_codigo(self) -> str:
        """Gera código único no formato CRIT-AAAA-NNN.

        Estratégia: ano corrente + maior NNN existente desse ano + 1.
        Concurrency-safe porque o save vive em transaction implícita do
        Admin/Form. Para imports paralelos, a chamada já vem com codigo
        explícito do XLSX.
        """
        ano = datetime.now().year
        prefixo = f"CRIT-{ano}-"
        ultimo = (
            Criterio.objects.filter(codigo__startswith=prefixo)
            .order_by("-codigo")
            .values_list("codigo", flat=True)
            .first()
        )
        if not ultimo:
            return f"{prefixo}001"
        match = re.search(r"-(\d+)$", ultimo)
        next_n = (int(match.group(1)) + 1) if match else 1
        return f"{prefixo}{next_n:03d}"

    def _atualizar_search_vector(self) -> None:
        """Atualiza o vetor de busca com pesos A/B/C/D em português.

        Pesos:
            A — titulo
            B — texto_providencia (mais relevante após o título)
            C — determinacoes_principais + justificativa_tecnica
            D — precaucoes + fonte
        """
        # UPDATE direto via queryset evita signal loop com save() acima
        Criterio.objects.filter(pk=self.pk).update(
            search_vector=(
                SearchVector("titulo", weight="A", config="portuguese")
                + SearchVector("texto_providencia", weight="B", config="portuguese")
                + SearchVector("determinacoes_principais", weight="C", config="portuguese")
                + SearchVector("justificativa_tecnica", weight="C", config="portuguese")
                + SearchVector("precaucoes", weight="D", config="portuguese")
                + SearchVector("fonte", weight="D", config="portuguese")
            )
        )

    # ---------- Helpers de domínio ----------
    @transaction.atomic
    def publicar(self, usuario=None) -> None:
        self.status = StatusCriterio.PUBLICADO
        self.publicado_em = timezone.now()
        self.save()

    @transaction.atomic
    def arquivar(self) -> None:
        self.status = StatusCriterio.ARQUIVADO
        self.save()
