"""Gerador de PDF de fichas de critério via WeasyPrint.

Estratégia: renderiza ``exportacao/criterio_pdf.html`` com o critério no
contexto, aplica CSS de impressão dedicado e devolve bytes do PDF.
WeasyPrint suporta HTML5 + CSS Paged Media (PSS-3), o que cobre
cabeçalhos/rodapés repetidos, numeração de página e quebras de seção.
"""

from __future__ import annotations

from io import BytesIO

from django.conf import settings
from django.template.loader import render_to_string

# Import preguiçoso para que falhas no ambiente (libpango ausente) não
# quebrem o import do módulo — só falham na chamada real.
def _weasyprint():
    from weasyprint import CSS, HTML

    return HTML, CSS


def gerar_pdf_criterio(criterio, base_url: str | None = None) -> bytes:
    """Renderiza a ficha do critério em PDF e devolve bytes."""
    html_string = render_to_string(
        "exportacao/criterio_pdf.html",
        {
            "criterio": criterio,
            "pescp": settings.PESCP,
            "public_url": settings.PESCP.get("PUBLIC_URL", ""),
        },
    )
    HTML, _CSS = _weasyprint()
    buffer = BytesIO()
    HTML(string=html_string, base_url=base_url or settings.PESCP.get("PUBLIC_URL", "")).write_pdf(buffer)
    return buffer.getvalue()
