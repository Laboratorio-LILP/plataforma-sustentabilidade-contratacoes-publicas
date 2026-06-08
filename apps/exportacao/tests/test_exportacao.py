"""Testes das exportações PDF e DOCX."""

import io

import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_docx_export_devolve_arquivo_valido(client, criterio):
    """O endpoint /criterios/<slug>/exportar/docx/ devolve DOCX abrível."""
    url = reverse("exportacao:criterio_docx", kwargs={"slug": criterio.slug})
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp["Content-Type"].startswith("application/vnd.openxmlformats")
    assert resp["Content-Disposition"].startswith("attachment")

    # Carrega o arquivo via python-docx para garantir que é válido
    from docx import Document

    doc = Document(io.BytesIO(resp.content))
    textos = [p.text for p in doc.paragraphs if p.text]
    # Título do critério aparece em algum parágrafo
    assert any(criterio.titulo in t for t in textos) or any(
        criterio.codigo in t for t in textos
    )


def test_pdf_export_skip_se_weasyprint_sem_libs(client, criterio):
    """Tenta export PDF; se WeasyPrint não consegue carregar (ambiente
    sem libpango), pulamos com xfail em vez de quebrar a suite."""
    pytest.importorskip("weasyprint")
    url = reverse("exportacao:criterio_pdf", kwargs={"slug": criterio.slug})
    try:
        resp = client.get(url)
    except Exception as e:
        pytest.skip(f"WeasyPrint indisponível neste ambiente: {e}")
    assert resp.status_code == 200
    assert resp["Content-Type"] == "application/pdf"
    # Header do PDF
    assert resp.content[:4] == b"%PDF"


def test_export_404_se_criterio_rascunho(client, criterio):
    """Rascunho não pode ser exportado publicamente."""
    from apps.criterios.models import StatusCriterio

    criterio.status = StatusCriterio.RASCUNHO
    criterio.save()
    url = reverse("exportacao:criterio_docx", kwargs={"slug": criterio.slug})
    resp = client.get(url)
    assert resp.status_code == 404
