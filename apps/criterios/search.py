"""Busca textual em ``Criterio.search_vector`` usando Postgres FTS.

Estratégia: usa SearchQuery(config='portuguese'). Para tolerância a
sufixos comuns ("contratação"/"contratações") confia no stemmer
``portuguese``. Acentos: o dicionário portuguese é case- e accent-aware
(quem buscar "criterio" não acha "critério") — sem unaccent dict, a
gente compensa convertendo a query e os campos para ``unaccent()``
no nível SQL via Coalesce... porém para v1.0 mantemos comportamento
default: usuários da plataforma costumam digitar com acentuação.
"""

from __future__ import annotations

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, QuerySet

from .models import Criterio


def buscar_criterios(queryset: QuerySet[Criterio], query: str) -> QuerySet[Criterio]:
    """Aplica busca textual ao queryset, ordenando por rank.

    Se ``query`` está vazio, devolve o queryset intacto (ordenação default
    do model).
    """
    query = (query or "").strip()
    if not query:
        return queryset

    sq = SearchQuery(query, config="portuguese", search_type="websearch")
    return (
        queryset.filter(search_vector=sq)
        .annotate(rank=SearchRank(F("search_vector"), sq))
        .order_by("-rank", "-updated")
    )
