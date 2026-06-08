"""Views de exportação: PDF e DOCX de uma ficha de critério.

Mantemos a rota sob ``/criterios/<slug>/exportar/<formato>/`` para que
o usuário sempre veja a URL canônica da ficha antes de baixar.
"""

from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from apps.criterios.models import Criterio, StatusCriterio

from .docx_gen import gerar_docx_criterio
from .pdf import gerar_pdf_criterio


@require_GET
def exportar_pdf(request: HttpRequest, slug: str) -> HttpResponse:
    criterio = get_object_or_404(
        Criterio.objects.prefetch_related("ods", "normas", "selos"),
        slug=slug,
        status=StatusCriterio.PUBLICADO,
    )
    pdf_bytes = gerar_pdf_criterio(criterio, base_url=request.build_absolute_uri("/"))
    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{criterio.codigo}.pdf"'
    return resp


@require_GET
def exportar_docx(request: HttpRequest, slug: str) -> HttpResponse:
    criterio = get_object_or_404(
        Criterio.objects.prefetch_related("ods", "normas", "selos"),
        slug=slug,
        status=StatusCriterio.PUBLICADO,
    )
    docx_bytes = gerar_docx_criterio(criterio)
    resp = HttpResponse(
        docx_bytes,
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    resp["Content-Disposition"] = f'attachment; filename="{criterio.codigo}.docx"'
    return resp
