"""Models de pilotos de licitação.

Na v1.0 são geridos exclusivamente pelo Admin (sem páginas públicas).
O campo ``publicar_pagina`` já existe para futura v2.0 — permanece False
em todos os registros até que curadoria editorial seja desenhada.
"""

from __future__ import annotations

import re
from datetime import datetime

from django.conf import settings
from django.db import models

from apps.core.models import TimestampedModel
from apps.criterios.models import Criterio, ObjetoContratual, TipoContratacao


class PilotoLicitacao(TimestampedModel):
    """Caso piloto de aplicação dos critérios PESCP em uma contratação real.

    Meta institucional: até setembro/2026, 10 pilotos devem estar registrados.
    """

    class Estagio(models.TextChoices):
        PLANEJAMENTO = "PLANEJAMENTO", "Planejamento"
        EDITAL_PUBLICADO = "EDITAL_PUBLICADO", "Edital publicado"
        EM_LICITACAO = "EM_LICITACAO", "Em licitação"
        HOMOLOGADO = "HOMOLOGADO", "Homologado"
        EM_EXECUCAO = "EM_EXECUCAO", "Em execução"
        CONCLUIDO = "CONCLUIDO", "Concluído"
        CANCELADO = "CANCELADO", "Cancelado"

    codigo = models.CharField(
        "Código",
        max_length=30,
        unique=True,
        blank=True,
        help_text='Gerado automaticamente como "PIL-AAAA-NNN" se vazio.',
    )
    titulo = models.CharField("Título descritivo", max_length=300)
    unidade_compradora = models.CharField(
        "Unidade Compradora",
        max_length=300,
        help_text="Secretaria, autarquia, fundação, etc.",
    )
    tipo_contratacao = models.CharField(
        "Tipo de Contratação",
        max_length=32,
        choices=TipoContratacao.choices,
        default=TipoContratacao.BENS,
    )
    objeto_contratual = models.ForeignKey(
        ObjetoContratual,
        on_delete=models.PROTECT,
        related_name="pilotos",
        verbose_name="Objeto Contratual",
    )
    criterios_aplicados = models.ManyToManyField(
        Criterio,
        blank=True,
        related_name="pilotos",
        verbose_name="Critérios aplicados",
    )
    estagio_atual = models.CharField(
        "Estágio atual",
        max_length=32,
        choices=Estagio.choices,
        default=Estagio.PLANEJAMENTO,
    )

    valor_estimado = models.DecimalField(
        "Valor estimado (R$)",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )
    valor_homologado = models.DecimalField(
        "Valor homologado (R$)",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
    )

    data_inicio = models.DateField("Início", null=True, blank=True)
    data_homologacao = models.DateField("Homologação", null=True, blank=True)
    data_conclusao = models.DateField("Conclusão", null=True, blank=True)

    numero_processo_sei = models.CharField("Processo SEI", max_length=50, blank=True)
    numero_edital = models.CharField("Número do Edital", max_length=50, blank=True)
    observacoes = models.TextField("Observações", blank=True)

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pilotos_criados",
        verbose_name="Criado por",
    )

    # Reservado para v2.0 — sempre False na v1.0
    publicar_pagina = models.BooleanField(
        "Publicar página pública (v2.0)",
        default=False,
        help_text="Na v1.0 permanece sempre False — pilotos só visíveis no Admin.",
    )

    class Meta:
        verbose_name = "Piloto de Licitação"
        verbose_name_plural = "Pilotos de Licitação"
        ordering = ["-data_inicio", "-created"]
        indexes = [
            models.Index(fields=["estagio_atual"]),
            models.Index(fields=["tipo_contratacao"]),
        ]

    def __str__(self) -> str:
        return f"{self.codigo or '?'} — {self.titulo}"

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = self._gerar_codigo()
        super().save(*args, **kwargs)

    def _gerar_codigo(self) -> str:
        ano = datetime.now().year
        prefixo = f"PIL-{ano}-"
        ultimo = (
            PilotoLicitacao.objects.filter(codigo__startswith=prefixo)
            .order_by("-codigo")
            .values_list("codigo", flat=True)
            .first()
        )
        if not ultimo:
            return f"{prefixo}001"
        match = re.search(r"-(\d+)$", ultimo)
        next_n = (int(match.group(1)) + 1) if match else 1
        return f"{prefixo}{next_n:03d}"


class AvaliacaoImpacto(TimestampedModel):
    """Avaliação de impacto socioambiental e econômico de um piloto.

    1:1 com PilotoLicitacao — cada piloto pode ter no máximo uma avaliação.
    """

    piloto = models.OneToOneField(
        PilotoLicitacao,
        on_delete=models.CASCADE,
        related_name="avaliacao",
        verbose_name="Piloto",
    )
    economia_lcc_estimada = models.DecimalField(
        "Economia LCC estimada (R$)",
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Life Cycle Cost — economia do ciclo de vida em relação à contratação tradicional.",
    )
    reducao_co2_estimada_ton = models.DecimalField(
        "Redução de CO₂ estimada (toneladas)",
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
    )
    impactos_sociais = models.TextField("Impactos sociais", blank=True)
    impactos_ambientais = models.TextField("Impactos ambientais", blank=True)
    licoes_aprendidas = models.TextField("Lições aprendidas", blank=True)
    recomendacoes_para_proximas_contratacoes = models.TextField(
        "Recomendações para próximas contratações", blank=True
    )
    data_avaliacao = models.DateField("Data da avaliação", null=True, blank=True)

    class Meta:
        verbose_name = "Avaliação de Impacto"
        verbose_name_plural = "Avaliações de Impacto"

    def __str__(self) -> str:
        return f"Avaliação — {self.piloto.codigo}"
