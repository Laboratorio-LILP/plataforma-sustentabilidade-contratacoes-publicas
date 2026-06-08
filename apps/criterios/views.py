"""Views do app criterios.

Rotas públicas (todas usam ``base.html`` como layout):
- ``home``                  — landing page institucional
- ``criterio_list``         — listagem de critérios com filtros facetados
- ``criterio_detail``       — ficha completa de um critério
- ``objeto_list``           — árvore de objetos contratuais
- ``objeto_detail``         — critérios de um objeto
- ``ods_list``              — grid de 17 ODS
- ``ods_detail``            — critérios de um ODS
- ``fase_detail``           — critérios de uma fase do processo
- ``buscar``                — busca textual
- ``glossario``             — lista alfabética de termos
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.postgres.search import SearchHeadline, SearchQuery
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.conteudo.models import DocumentoApoio, TermoGlossario
from apps.normas.models import Ods

from .facets import aplicar_facetas, construir_facetas
from .models import Criterio, FaseProcesso, ObjetoContratual, StatusCriterio
from .search import buscar_criterios


def _criterios_publicados():
    return Criterio.objects.filter(status=StatusCriterio.PUBLICADO)


def home(request: HttpRequest) -> HttpResponse:
    """Página inicial — três cards de entrada (Objeto/ODS/Fase) + destaques."""
    # Conta critérios publicados próprios em cada objeto e consolida por
    # supercategoria — critérios costumam ser vinculados às folhas, não
    # ao topo da hierarquia (profundidade máxima = 2).
    objetos_anotados = list(
        ObjetoContratual.objects.filter(ativo=True).annotate(
            criterios_proprios=Count(
                "criterios",
                filter=Q(criterios__status=StatusCriterio.PUBLICADO),
            )
        )
    )
    totais_por_super: dict[int, int] = {}
    filhos_por_super: dict[int, list] = {}
    for o in objetos_anotados:
        chave = o.pk if o.parent_id is None else o.parent_id
        totais_por_super[chave] = totais_por_super.get(chave, 0) + o.criterios_proprios
        if o.parent_id is not None and o.criterios_proprios > 0:
            filhos_por_super.setdefault(o.parent_id, []).append(o)
    objetos_super = sorted(
        (o for o in objetos_anotados if o.parent_id is None),
        key=lambda o: (o.ordem, o.nome),
    )[:8]
    for o in objetos_super:
        o.total = totais_por_super.get(o.pk, 0)
        o.filhos_destaque = sorted(
            filhos_por_super.get(o.pk, []),
            key=lambda f: (-f.criterios_proprios, f.nome),
        )[:3]

    ods_list = Ods.objects.annotate(total=Count("criterios")).order_by("numero")
    criterios_recentes = (
        _criterios_publicados()
        .select_related("objeto_contratual")
        .prefetch_related("ods")
        .order_by("-publicado_em", "-updated")[:6]
    )
    return render(
        request,
        "home.html",
        {
            "objetos_super": objetos_super,
            "ods_list": ods_list,
            "fases": FaseProcesso.choices,
            "criterios_recentes": criterios_recentes,
        },
    )


def criterio_list(request: HttpRequest) -> HttpResponse:
    """Listagem geral com filtros facetados e busca textual.

    Query params reconhecidos: q, objeto, ods, fase, nivel, tipo, selo,
    ordem, page.
    """
    qs = (
        _criterios_publicados()
        .select_related("objeto_contratual")
        .prefetch_related("ods", "normas")
    )
    qs = aplicar_facetas(qs, request)

    query = request.GET.get("q", "").strip()
    if query:
        qs = buscar_criterios(qs, query)

    ordem = request.GET.get("ordem", "")
    if ordem == "titulo":
        qs = qs.order_by("titulo")
    elif ordem == "ambicao":
        # ordem semântica: Avançado → Intermediário → Básico
        from django.db.models import Case, IntegerField, Value, When

        qs = qs.annotate(
            _ord_amb=Case(
                When(nivel_ambicao="AVANCADO", then=Value(0)),
                When(nivel_ambicao="INTERMEDIARIO", then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        ).order_by("_ord_amb", "titulo")
    elif ordem == "publicacao":
        qs = qs.order_by("-publicado_em", "-updated")
    elif not query:
        qs = qs.order_by("-updated")

    facetas = construir_facetas(qs, request) if not query else construir_facetas(_criterios_publicados(), request)

    paginator = Paginator(qs, settings.PESCP.get("CRITERIOS_POR_PAGINA", 20))
    pagina = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "criterios/list.html",
        {
            "criterios": pagina.object_list,
            "page_obj": pagina,
            "paginator": paginator,
            "facetas": facetas,
            "query": query,
            "ordem": ordem,
            "total_resultados": paginator.count,
        },
    )


def criterio_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Ficha completa de um critério publicado."""
    criterio = get_object_or_404(
        Criterio.objects.select_related("objeto_contratual", "criado_por")
        .prefetch_related("ods", "normas", "selos", "tags"),
        slug=slug,
        status=StatusCriterio.PUBLICADO,
    )

    # Critérios relacionados — mesmo objeto contratual, mesmo nível
    relacionados = (
        _criterios_publicados()
        .filter(objeto_contratual=criterio.objeto_contratual)
        .exclude(pk=criterio.pk)
        .select_related("objeto_contratual")
        .order_by("-updated")[:4]
    )

    return render(
        request,
        "criterios/detail.html",
        {
            "criterio": criterio,
            "relacionados": relacionados,
        },
    )


def objeto_list(request: HttpRequest) -> HttpResponse:
    """Árvore de objetos contratuais (supercategorias + filhos).

    Conta critérios publicados próprios em cada objeto e consolida por
    supercategoria — critérios costumam ser vinculados às folhas, não
    ao topo da hierarquia (profundidade máxima = 2).
    """
    todos = list(
        ObjetoContratual.objects.filter(ativo=True).annotate(
            criterios_proprios=Count(
                "criterios",
                filter=Q(criterios__status=StatusCriterio.PUBLICADO),
            )
        )
    )
    totais_por_super: dict[int, int] = {}
    for o in todos:
        chave = o.pk if o.parent_id is None else o.parent_id
        totais_por_super[chave] = totais_por_super.get(chave, 0) + o.criterios_proprios

    supercategorias = list(
        ObjetoContratual.objects.filter(parent__isnull=True, ativo=True)
        .prefetch_related(
            Prefetch(
                "filhos",
                queryset=ObjetoContratual.objects.filter(ativo=True)
                .annotate(
                    total=Count(
                        "criterios",
                        filter=Q(criterios__status=StatusCriterio.PUBLICADO),
                    )
                )
                .order_by("ordem", "nome"),
            )
        )
        .order_by("ordem", "nome")
    )
    for s in supercategorias:
        s.total = totais_por_super.get(s.pk, 0)
    return render(request, "objetos/list.html", {"supercategorias": supercategorias})


def objeto_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Detalhe de um objeto contratual — lista seus critérios e os do filho."""
    objeto = get_object_or_404(ObjetoContratual, slug=slug, ativo=True)
    descendentes = objeto.descendentes()
    qs = (
        _criterios_publicados()
        .filter(objeto_contratual__in=descendentes)
        .select_related("objeto_contratual")
        .prefetch_related("ods")
    )
    qs = aplicar_facetas(qs, request)
    facetas = construir_facetas(qs, request)

    paginator = Paginator(qs, settings.PESCP.get("CRITERIOS_POR_PAGINA", 20))
    pagina = paginator.get_page(request.GET.get("page"))

    documentos = DocumentoApoio.objects.filter(objeto_contratual__in=descendentes).order_by("-created")[:5]

    return render(
        request,
        "objetos/detail.html",
        {
            "objeto": objeto,
            "criterios": pagina.object_list,
            "page_obj": pagina,
            "paginator": paginator,
            "facetas": facetas,
            "total_resultados": paginator.count,
            "documentos": documentos,
        },
    )


def ods_list(request: HttpRequest) -> HttpResponse:
    ods_qs = Ods.objects.annotate(total=Count("criterios", distinct=True)).order_by("numero")
    return render(request, "ods/list.html", {"ods_list": ods_qs})


def ods_detail(request: HttpRequest, numero: int) -> HttpResponse:
    ods = get_object_or_404(Ods, numero=numero)
    qs = (
        _criterios_publicados()
        .filter(ods=ods)
        .select_related("objeto_contratual")
        .prefetch_related("ods")
    )
    qs = aplicar_facetas(qs, request)
    facetas = construir_facetas(qs, request)

    paginator = Paginator(qs, settings.PESCP.get("CRITERIOS_POR_PAGINA", 20))
    pagina = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "ods/detail.html",
        {
            "ods": ods,
            "criterios": pagina.object_list,
            "page_obj": pagina,
            "paginator": paginator,
            "facetas": facetas,
            "total_resultados": paginator.count,
        },
    )


def fase_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Detalhe de uma fase do processo (ETP, TR_PB, EDITAL, etc.).

    O slug corresponde ao value da enum em minúsculas com hifens.
    Ex.: "etp", "tr-pb", "edital", "execucao", "fiscalizacao".
    """
    mapeamento = {
        "etp": ("ETP", "Estudo Técnico Preliminar"),
        "tr-pb": ("TR_PB", "Termo de Referência / Projeto Básico"),
        "edital": ("EDITAL", "Edital de Licitação"),
        "execucao": ("EXECUCAO", "Execução Contratual"),
        "fiscalizacao": ("FISCALIZACAO", "Fiscalização do Contrato"),
    }
    if slug not in mapeamento:
        from django.http import Http404

        raise Http404("Fase do processo não reconhecida.")
    valor, rotulo = mapeamento[slug]

    qs = (
        _criterios_publicados()
        .filter(fase_processo=valor)
        .select_related("objeto_contratual")
        .prefetch_related("ods")
    )
    qs = aplicar_facetas(qs, request)
    facetas = construir_facetas(qs, request)

    paginator = Paginator(qs, settings.PESCP.get("CRITERIOS_POR_PAGINA", 20))
    pagina = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "fases/detail.html",
        {
            "fase_valor": valor,
            "fase_rotulo": rotulo,
            "fase_slug": slug,
            "criterios": pagina.object_list,
            "page_obj": pagina,
            "paginator": paginator,
            "facetas": facetas,
            "total_resultados": paginator.count,
        },
    )


def buscar(request: HttpRequest) -> HttpResponse:
    """Busca textual avançada com snippets via SearchHeadline."""
    query = request.GET.get("q", "").strip()
    if not query:
        return render(request, "criterios/busca.html", {"query": "", "resultados": [], "total": 0})

    qs = _criterios_publicados().select_related("objeto_contratual").prefetch_related("ods")
    sq = SearchQuery(query, config="portuguese", search_type="websearch")
    qs = (
        qs.filter(search_vector=sq)
        .annotate(
            snippet=SearchHeadline(
                "texto_providencia",
                sq,
                config="portuguese",
                start_sel="<mark>",
                stop_sel="</mark>",
                max_words=35,
                min_words=15,
            )
        )
        .order_by("-publicado_em")
    )

    paginator = Paginator(qs, settings.PESCP.get("CRITERIOS_POR_PAGINA", 20))
    pagina = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "criterios/busca.html",
        {
            "query": query,
            "resultados": pagina.object_list,
            "page_obj": pagina,
            "paginator": paginator,
            "total": paginator.count,
        },
    )


def glossario(request: HttpRequest) -> HttpResponse:
    import unicodedata

    def _inicial(termo: str) -> str:
        s = unicodedata.normalize("NFKD", termo).encode("ascii", "ignore").decode("ascii")
        return s[:1].upper() if s else ""

    todos = list(TermoGlossario.objects.prefetch_related("normas_relacionadas").order_by("termo"))
    letras_disponiveis = sorted({_inicial(t.termo) for t in todos if _inicial(t.termo).isalpha()})

    letra = (request.GET.get("letra") or "").strip().upper()[:1]
    if letra and letra.isalpha():
        termos = [t for t in todos if _inicial(t.termo) == letra]
    else:
        termos = todos
        letra = ""

    alfabeto = [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    return render(
        request,
        "conteudo/glossario.html",
        {
            "termos": termos,
            "alfabeto": alfabeto,
            "letras_disponiveis": letras_disponiveis,
            "letra_ativa": letra,
            "total_geral": len(todos),
        },
    )
