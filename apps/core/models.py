"""Models de uso transversal do PESCP.

Por enquanto, apenas a entidade Tag (palavras-chave livres usadas pelos
critérios). Helpers e mixins reaproveitáveis (TimestampedModel,
SlugFromNameModel) também vivem aqui — assim apps específicos importam
de um lugar só.
"""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify


def gerar_slug(value: str, maxlen: int = 80) -> str:
    """Gera slug ASCII a partir de um valor, truncando em ``maxlen``."""
    return slugify(value)[:maxlen]


class TimestampedModel(models.Model):
    """Mixin com timestamps padrão. Abstract — não cria tabela própria."""

    created = models.DateTimeField("Criado em", auto_now_add=True)
    updated = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        abstract = True


class Tag(TimestampedModel):
    """Palavra-chave livre. Usada para indexação adicional dos Critérios.

    Não substitui ObjetoContratual nem ODS — serve para sinalizar conexões
    transversais (ex.: "Logística Reversa", "Pequeno Porte", "Marca Regional").
    """

    nome = models.CharField("Nome", max_length=80, unique=True)
    slug = models.SlugField("Slug", max_length=80, unique=True, blank=True)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["nome"]

    def __str__(self) -> str:
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = gerar_slug(self.nome)
        super().save(*args, **kwargs)
