"""Filtros facetados para a listagem de critérios.

Cada faceta é definida como uma tupla ``(querystring_key, model_lookup,
options_callable)``. A view chama ``aplicar_facetas(queryset, request)``
para devolver queryset filtrado + descrição das facetas ativas para o
template renderizar o sidebar com contagens.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django.db.models import Count, QuerySet

from apps.normas.models import NormaLegal, Ods, SeloCertificacao

from .models import Criterio, FaseProcesso, NivelAmbicao, ObjetoContratual, TipoContratacao


@dataclass
class FacetOpcao:
    """Uma opção dentro de uma faceta (ex.: "ODS 7", 23 critérios)."""

    valor: str
    rotulo: str
    contagem: int
    ativa: bool


@dataclass
class Faceta:
    """Faceta exibida no sidebar do listing."""

    chave: str  # querystring key (ex.: "ods")
    rotulo: str
    opcoes: list[FacetOpcao]

    @property
    def tem_opcoes(self) -> bool:
        return any(o.contagem > 0 for o in self.opcoes)


def _selecionados(request, chave: str) -> set[str]:
    return set(request.GET.getlist(chave))


def construir_facetas(queryset: QuerySet[Criterio], request) -> list[Faceta]:
    """Constrói lista de facetas a partir do queryset BASE (sem filtros).

    Estratégia: contagem é feita sobre o queryset já filtrado por OUTROS
    parâmetros (mas não pela própria faceta), o que dá o "drill-down"
    natural. Para v1.0, simplificamos contando sobre o queryset filtrado
    completo — é menos preciso mas suficiente para o volume esperado.
    """
    facetas: list[Faceta] = []

    # Objeto contratual
    sel = _selecionados(request, "objeto")
    objetos = (
        ObjetoContratual.objects.filter(criterios__in=queryset, ativo=True)
        .annotate(n=Count("criterios", distinct=True))
        .order_by("nome")
    )
    facetas.append(
        Faceta(
            chave="objeto",
            rotulo="Objeto Contratual",
            opcoes=[
                FacetOpcao(o.slug, str(o), o.n, o.slug in sel) for o in objetos if o.n > 0
            ],
        )
    )

    # ODS
    sel = _selecionados(request, "ods")
    ods_qs = Ods.objects.filter(criterios__in=queryset).annotate(n=Count("criterios", distinct=True)).order_by("numero")
    facetas.append(
        Faceta(
            chave="ods",
            rotulo="ODS",
            opcoes=[FacetOpcao(str(o.numero), str(o), o.n, str(o.numero) in sel) for o in ods_qs if o.n > 0],
        )
    )

    # Fase do processo
    sel = _selecionados(request, "fase")
    contagens_fase = {
        v: queryset.filter(fase_processo=v).count() for v, _ in FaseProcesso.choices
    }
    facetas.append(
        Faceta(
            chave="fase",
            rotulo="Fase do Processo",
            opcoes=[
                FacetOpcao(v, l, contagens_fase[v], v in sel) for v, l in FaseProcesso.choices
            ],
        )
    )

    # Nível de ambição
    sel = _selecionados(request, "nivel")
    contagens_nivel = {
        v: queryset.filter(nivel_ambicao=v).count() for v, _ in NivelAmbicao.choices
    }
    facetas.append(
        Faceta(
            chave="nivel",
            rotulo="Nível de Ambição",
            opcoes=[
                FacetOpcao(v, l, contagens_nivel[v], v in sel) for v, l in NivelAmbicao.choices
            ],
        )
    )

    # Tipo de contratação
    sel = _selecionados(request, "tipo")
    contagens_tipo = {
        v: queryset.filter(tipo_contratacao=v).count() for v, _ in TipoContratacao.choices
    }
    facetas.append(
        Faceta(
            chave="tipo",
            rotulo="Tipo de Contratação",
            opcoes=[
                FacetOpcao(v, l, contagens_tipo[v], v in sel) for v, l in TipoContratacao.choices
            ],
        )
    )

    # Selos
    sel = _selecionados(request, "selo")
    selos_qs = (
        SeloCertificacao.objects.filter(criterios__in=queryset)
        .annotate(n=Count("criterios", distinct=True))
        .order_by("nome")
    )
    facetas.append(
        Faceta(
            chave="selo",
            rotulo="Selos de Certificação",
            opcoes=[FacetOpcao(s.slug, s.nome, s.n, s.slug in sel) for s in selos_qs if s.n > 0],
        )
    )

    return facetas


def aplicar_facetas(queryset: QuerySet[Criterio], request) -> QuerySet[Criterio]:
    """Aplica filtros facetados da querystring ao queryset.

    Combina filtros com AND entre facetas e OR dentro da mesma faceta
    (ex.: ods=7&ods=12 retorna critérios que tocam ODS 7 OU 12, e ao
    cruzar com fase=ETP, devolve critérios desse subconjunto que estão
    na fase ETP).
    """
    objetos = request.GET.getlist("objeto")
    if objetos:
        queryset = queryset.filter(objeto_contratual__slug__in=objetos)

    ods_nums: Iterable[str] = request.GET.getlist("ods")
    if ods_nums:
        ods_int = [int(n) for n in ods_nums if str(n).isdigit()]
        if ods_int:
            queryset = queryset.filter(ods__numero__in=ods_int)

    fases = request.GET.getlist("fase")
    if fases:
        queryset = queryset.filter(fase_processo__in=fases)

    niveis = request.GET.getlist("nivel")
    if niveis:
        queryset = queryset.filter(nivel_ambicao__in=niveis)

    tipos = request.GET.getlist("tipo")
    if tipos:
        queryset = queryset.filter(tipo_contratacao__in=tipos)

    selos = request.GET.getlist("selo")
    if selos:
        queryset = queryset.filter(selos__slug__in=selos)

    return queryset.distinct()
