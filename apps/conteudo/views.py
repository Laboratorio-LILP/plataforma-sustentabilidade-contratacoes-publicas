"""Views do app conteudo: páginas institucionais e legais.

Padrão: cada slug de PaginaInstitucional renderiza ``pagina_institucional.html``;
slugs específicos da família "legal" usam um template diferente que adiciona
o aviso amarelo "versão inicial — pendente de validação jurídica".
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import PaginaInstitucional

LEGAL_SLUGS = {
    "transparencia",
    "acessibilidade",
    "politica-de-privacidade",
    "politica-de-cookies",
    "mapa-do-site",
    "fale-conosco",
}

TEMPLATES_FIXOS = {
    "sobre": "conteudo/sobre.html",
    "governanca": "conteudo/governanca.html",
    "metodologia": "conteudo/metodologia.html",
    "parceiros": "conteudo/parceiros.html",
    "contato": "conteudo/contato.html",
}


def pagina(request: HttpRequest, slug: str) -> HttpResponse:
    """Renderiza qualquer página institucional ou legal pelo slug."""
    if slug in TEMPLATES_FIXOS:
        return render(request, TEMPLATES_FIXOS[slug])

    pagina_obj = get_object_or_404(PaginaInstitucional, slug=slug, publicada=True)

    template_nome = "conteudo/pagina_legal.html" if slug in LEGAL_SLUGS else "conteudo/pagina_institucional.html"

    return render(
        request,
        template_nome,
        {
            "pagina": pagina_obj,
            "is_legal": slug in LEGAL_SLUGS,
        },
    )
