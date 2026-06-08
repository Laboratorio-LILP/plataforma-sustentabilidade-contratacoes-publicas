"""Models de normas: ODS, NormaLegal, SeloCertificacao.

NormaLegal tem versionamento via django-simple-history porque normas são
revogadas/alteradas e a plataforma precisa rastrear quando uma referência
deixou de valer.
"""

from __future__ import annotations

from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from apps.core.models import TimestampedModel, gerar_slug


class Ods(TimestampedModel):
    """Objetivo de Desenvolvimento Sustentável (Agenda 2030 ONU).

    São 17 — populados via management command ``create_initial_ods``.
    Identificados pelo ``numero`` (1 a 17) como chave natural.
    """

    numero = models.PositiveSmallIntegerField("Número (1 a 17)", unique=True)
    nome = models.CharField("Nome", max_length=120)
    slug = models.SlugField("Slug", max_length=120, unique=True, blank=True)
    descricao_curta = models.CharField("Descrição curta", max_length=300, blank=True)
    descricao_longa = models.TextField("Descrição longa", blank=True)
    cor_hex = models.CharField(
        "Cor oficial (#HEX)",
        max_length=7,
        default="#000000",
        help_text="Cor oficial definida pela ONU para o ODS (ex.: #E5243B para ODS 1).",
    )
    icone = models.ImageField(
        "Ícone oficial",
        upload_to="ods/",
        blank=True,
        null=True,
        help_text="Ícone oficial da ONU. Coloque o arquivo em media/ods/.",
    )
    metas = models.JSONField(
        "Metas oficiais",
        default=list,
        blank=True,
        help_text='Lista de strings com as metas (ex.: ["1.1 ...", "1.2 ..."]).',
    )

    class Meta:
        verbose_name = "ODS"
        verbose_name_plural = "ODS (Objetivos de Desenvolvimento Sustentável)"
        ordering = ["numero"]

    def __str__(self) -> str:
        return f"ODS {self.numero} — {self.nome}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = gerar_slug(f"ods-{self.numero}-{self.nome}", maxlen=120)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("criterios:ods_detail", kwargs={"numero": self.numero})


class NormaLegal(TimestampedModel):
    """Norma de qualquer esfera referenciada pelos Critérios.

    O esquema é deliberadamente amplo para acomodar futuras inclusões
    (resoluções CONAMA, portarias INMETRO, NBR ABNT) sem alteração de schema.
    """

    class Tipo(models.TextChoices):
        CONSTITUCIONAL = "CONSTITUCIONAL", "Constitucional"
        LEI_FEDERAL = "LEI_FEDERAL", "Lei Federal"
        LEI_ESTADUAL = "LEI_ESTADUAL", "Lei Estadual"
        LEI_MUNICIPAL = "LEI_MUNICIPAL", "Lei Municipal"
        DECRETO_FEDERAL = "DECRETO_FEDERAL", "Decreto Federal"
        DECRETO_ESTADUAL = "DECRETO_ESTADUAL", "Decreto Estadual"
        DECRETO_MUNICIPAL = "DECRETO_MUNICIPAL", "Decreto Municipal"
        INSTRUCAO_NORMATIVA = "INSTRUCAO_NORMATIVA", "Instrução Normativa"
        RESOLUCAO = "RESOLUCAO", "Resolução"
        PORTARIA = "PORTARIA", "Portaria"
        NBR_ABNT = "NBR_ABNT", "NBR/ABNT"
        INTERNACIONAL = "INTERNACIONAL", "Acordo/Resolução Internacional"
        OUTRO = "OUTRO", "Outro"

    class Esfera(models.TextChoices):
        FEDERAL = "FEDERAL", "Federal"
        ESTADUAL = "ESTADUAL", "Estadual"
        MUNICIPAL = "MUNICIPAL", "Municipal"
        INTERNACIONAL = "INTERNACIONAL", "Internacional"

    titulo_curto = models.CharField(
        "Título curto",
        max_length=200,
        help_text='Ex.: "Lei 14.133/2021"',
    )
    titulo_completo = models.CharField(
        "Título completo",
        max_length=500,
        help_text='Ex.: "Lei nº 14.133, de 1º de abril de 2021..."',
    )
    slug = models.SlugField("Slug", max_length=200, unique=True, blank=True)
    tipo = models.CharField("Tipo", max_length=32, choices=Tipo.choices, default=Tipo.LEI_FEDERAL)
    esfera = models.CharField("Esfera", max_length=16, choices=Esfera.choices, default=Esfera.FEDERAL)
    numero = models.CharField("Número", max_length=50, blank=True)
    data_publicacao = models.DateField("Data de publicação", null=True, blank=True)
    data_vigencia = models.DateField("Data de início de vigência", null=True, blank=True)
    revogada = models.BooleanField("Revogada?", default=False)
    revogada_por = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="normas_revogadas",
        verbose_name="Revogada por",
    )
    link_oficial = models.URLField(
        "Link oficial",
        blank=True,
        help_text="URL no DOU, planalto.gov.br, doe.sp.gov.br, etc.",
    )
    ementa = models.TextField("Ementa", blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Norma Legal"
        verbose_name_plural = "Normas Legais"
        ordering = ["esfera", "titulo_curto"]
        indexes = [
            models.Index(fields=["esfera", "tipo"]),
            models.Index(fields=["revogada"]),
        ]

    def __str__(self) -> str:
        return self.titulo_curto

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = gerar_slug(self.titulo_curto, maxlen=200)
        super().save(*args, **kwargs)


class SeloCertificacao(TimestampedModel):
    """Selo, certificação ou registro de conformidade.

    Exemplos: INMETRO, FSC, Procel/PBE, Selo Inmetro de Eficiência Energética,
    CTF/APP-IBAMA, Registro ANP. Usado pelos Critérios como referência de
    método de verificação.
    """

    class Tipo(models.TextChoices):
        NACIONAL = "NACIONAL", "Nacional"
        INTERNACIONAL = "INTERNACIONAL", "Internacional"
        SETORIAL = "SETORIAL", "Setorial"

    nome = models.CharField("Nome", max_length=200)
    slug = models.SlugField("Slug", max_length=200, unique=True, blank=True)
    descricao = models.TextField("Descrição", blank=True)
    link_oficial = models.URLField("Link oficial", blank=True)
    logo = models.ImageField("Logo", upload_to="selos/", blank=True, null=True)
    tipo = models.CharField("Tipo", max_length=20, choices=Tipo.choices, default=Tipo.NACIONAL)

    class Meta:
        verbose_name = "Selo / Certificação"
        verbose_name_plural = "Selos e Certificações"
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = gerar_slug(self.nome, maxlen=200)
        super().save(*args, **kwargs)
