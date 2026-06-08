"""Models de conteúdo institucional: páginas, glossário, documentos de apoio.

PaginaInstitucional cobre tanto páginas do menu (Sobre, Governança,
Metodologia, Parceiros, Contato) quanto páginas legais (Transparência,
Acessibilidade, Política de Privacidade etc.). A diferenciação é feita
pelo slug — o template render é o mesmo.
"""

from __future__ import annotations

import os

from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords

from apps.core.models import TimestampedModel, gerar_slug
from apps.criterios.models import ObjetoContratual
from apps.normas.models import NormaLegal


class PaginaInstitucional(TimestampedModel):
    """Página estática de conteúdo institucional ou legal.

    Slug é a chave canônica. Páginas legais (transparência, acessibilidade
    etc.) usam slugs específicos que a view ``pagina_legal`` reconhece e
    aplica o cabeçalho com aviso amarelo "versão inicial — pendente de
    validação jurídica".
    """

    titulo = models.CharField("Título", max_length=200)
    slug = models.SlugField("Slug", max_length=200, unique=True, blank=True)
    conteudo = models.TextField(
        "Conteúdo (HTML/markdown)",
        help_text="HTML sanitizado ou markdown. É renderizado com |safe — não exponha campo a usuários externos.",
    )
    ordem = models.PositiveIntegerField("Ordem (menu)", default=0)
    publicada = models.BooleanField("Publicada?", default=True)
    meta_description = models.CharField(
        "Meta description (SEO)", max_length=300, blank=True
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Página institucional"
        verbose_name_plural = "Páginas institucionais"
        ordering = ["ordem", "titulo"]

    def __str__(self) -> str:
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = gerar_slug(self.titulo, maxlen=200)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("conteudo:pagina", kwargs={"slug": self.slug})


class TermoGlossario(TimestampedModel):
    """Termo do glossário — siglas e conceitos que o servidor pode não dominar.

    Exemplos: LCC (Life Cycle Cost), ETP (Estudo Técnico Preliminar),
    Logística Reversa, EMAS, FSC.
    """

    termo = models.CharField("Termo", max_length=200, unique=True)
    slug = models.SlugField("Slug", max_length=200, unique=True, blank=True)
    definicao = models.TextField("Definição")
    sigla = models.CharField("Sigla", max_length=20, blank=True)
    normas_relacionadas = models.ManyToManyField(
        NormaLegal,
        blank=True,
        related_name="termos_glossario",
        verbose_name="Normas relacionadas",
    )

    class Meta:
        verbose_name = "Termo do Glossário"
        verbose_name_plural = "Glossário"
        ordering = ["termo"]

    def __str__(self) -> str:
        return f"{self.sigla + ' — ' if self.sigla else ''}{self.termo}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = gerar_slug(self.termo, maxlen=200)
        super().save(*args, **kwargs)


def _document_upload_path(instance, filename):
    """Mantém uploads sob media/documentos_apoio/ano/arquivo."""
    from datetime import datetime

    return f"documentos_apoio/{datetime.now().year}/{filename}"


class DocumentoApoio(TimestampedModel):
    """Documento auxiliar para download — modelo de cláusula, planilha, guia.

    Relacionável a um objeto contratual para listagem contextual no
    detalhe da categoria.
    """

    class Tipo(models.TextChoices):
        MODELO_CLAUSULA = "MODELO_CLAUSULA", "Modelo de cláusula"
        PLANILHA = "PLANILHA", "Planilha"
        GUIA = "GUIA", "Guia técnico"
        RELATORIO_IMPACTO = "RELATORIO_IMPACTO", "Relatório de impacto"
        OUTRO = "OUTRO", "Outro"

    titulo = models.CharField("Título", max_length=300)
    descricao = models.TextField("Descrição", blank=True)
    arquivo = models.FileField("Arquivo", upload_to=_document_upload_path)
    tipo = models.CharField("Tipo", max_length=32, choices=Tipo.choices, default=Tipo.GUIA)
    objeto_contratual = models.ForeignKey(
        ObjetoContratual,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_apoio",
        verbose_name="Objeto Contratual relacionado",
    )
    tamanho_bytes = models.PositiveIntegerField("Tamanho (bytes)", null=True, blank=True)
    extensao = models.CharField("Extensão", max_length=10, blank=True)

    class Meta:
        verbose_name = "Documento de Apoio"
        verbose_name_plural = "Documentos de Apoio"
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.titulo

    def save(self, *args, **kwargs):
        if self.arquivo and not self.extensao:
            self.extensao = os.path.splitext(self.arquivo.name)[1].lstrip(".").lower()
        if self.arquivo and not self.tamanho_bytes:
            try:
                self.tamanho_bytes = self.arquivo.size
            except (OSError, ValueError):
                self.tamanho_bytes = None
        super().save(*args, **kwargs)
