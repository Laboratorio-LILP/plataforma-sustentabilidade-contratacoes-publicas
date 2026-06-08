"""Template tags utilitárias do PESCP.

Mantenha pequeno e focado: filtros de formatação, manipulação leve de URL,
helpers de pluralização. Lógica de domínio fica em views/managers.
"""

from __future__ import annotations

from urllib.parse import urlencode

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


_OBJETO_ICONE_MAP = {
    "residuos-e-logistica-reversa": "icon-cat-residuos",
    "energia": "icon-cat-energia",
    "transporte-e-veiculos": "icon-cat-transporte",
    "construcao-civil-e-engenharia": "icon-cat-construcao",
    "limpeza-higiene-e-conservacao": "icon-cat-limpeza",
    "ti-e-eletroeletronicos": "icon-cat-ti",
    "alimentacao": "icon-cat-alimentacao",
    "madeira-e-produtos-florestais": "icon-cat-madeira",
    "saude": "icon-cat-saude",
    "inclusao-social-e-direitos-humanos": "icon-cat-inclusao",
    "mobiliario-e-escritorio": "icon-cat-mobiliario",
    "insumos-quimicos-e-industriais": "icon-cat-quimicos",
}


@register.simple_tag
def objeto_icone(slug: str) -> str:
    """Devolve o id de símbolo SVG associado ao slug da supercategoria,
    ou ``icon-cat-default`` se o slug não estiver mapeado."""
    return _OBJETO_ICONE_MAP.get(slug, "icon-cat-default")


@register.simple_tag
def norma_link(slug: str, texto: str) -> str:
    """Renderiza link para uma norma legal pelo slug, ou só o texto se a
    norma não existir no banco. Importação tardia para evitar ciclos.

    Uso: ``{% norma_link "lei-14133-2021" "Lei nº 14.133/2021" %}``.
    """
    from apps.normas.models import NormaLegal

    try:
        norma = NormaLegal.objects.only("link_oficial", "titulo_completo").get(slug=slug)
    except NormaLegal.DoesNotExist:
        return escape(texto)
    if not norma.link_oficial:
        return escape(texto)
    return mark_safe(
        f'<a href="{escape(norma.link_oficial)}" target="_blank" rel="noopener noreferrer" '
        f'title="{escape(norma.titulo_completo)} (abre em nova aba)">{escape(texto)}</a>'
    )


@register.filter(name="pluralize_pt")
def pluralize_pt(value, singular: str) -> str:
    """Pluraliza em português simples acrescentando 's' se != 1."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return singular
    if n == 1:
        return singular
    if singular.endswith("ão"):
        # tratamento básico — não cobre todas as exceções, suficiente para nomes comuns
        return singular[:-2] + "ões"
    if singular.endswith("l"):
        return singular[:-1] + "is"
    return singular + "s"


@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs) -> str:
    """Retorna querystring atual mesclada com kwargs.

    Útil para preservar filtros facetados durante paginação:
        <a href="?{% url_replace page=2 %}">Próxima</a>
    """
    request = context["request"]
    params = request.GET.copy()
    for key, value in kwargs.items():
        if value is None or value == "":
            params.pop(key, None)
        else:
            params[key] = value
    return urlencode(params, doseq=True)


@register.simple_tag(takes_context=True)
def url_toggle_facet(context, name: str, value) -> str:
    """Toggle de filtro facetado: adiciona/remove ``name=value`` da query.

    Mantém todos os outros filtros e zera a paginação.
    """
    request = context["request"]
    params = request.GET.copy()
    value_str = str(value)
    valores = params.getlist(name)
    if value_str in valores:
        valores.remove(value_str)
    else:
        valores.append(value_str)
    params.setlist(name, valores)
    params.pop("page", None)
    return urlencode(params, doseq=True)


@register.filter(name="is_facet_active")
def is_facet_active(querydict, lookup: str) -> bool:
    """Retorna True se ``name=value`` está nos filtros ativos.

    Uso: ``{{ request.GET|is_facet_active:"ods=7" }}``.
    """
    if not lookup or "=" not in lookup:
        return False
    name, value = lookup.split("=", 1)
    return value in querydict.getlist(name)


@register.simple_tag
def badge_ods(numero: int) -> str:
    """Renderiza badge mínima de ODS — usado em listagens compactas."""
    return mark_safe(
        f'<span class="sp-badge-ods sp-badge-ods--ods-{int(numero)}" '
        f'aria-label="Objetivo de Desenvolvimento Sustentável {int(numero)}">'
        f"{int(numero)}</span>"
    )
