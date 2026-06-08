"""Smoke tests das views públicas — GET 200 + presença de marcadores."""

import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


def test_home_get_200(client, db_inicial, criterio):
    resp = client.get(reverse("criterios:home"))
    assert resp.status_code == 200
    assert b"PESCP" in resp.content
    # Banner LAI presente
    assert b"Acesso \xc3\xa0 Informa\xc3\xa7\xc3\xa3o" in resp.content


def test_criterio_list_get_200(client, criterio):
    resp = client.get(reverse("criterios:list"))
    assert resp.status_code == 200
    assert criterio.titulo.encode() in resp.content


def test_criterio_list_filtro_facetado(client, criterio, objeto):
    """?objeto=<slug> deve filtrar pelo slug do objeto."""
    resp = client.get(reverse("criterios:list"), {"objeto": objeto.slug})
    assert resp.status_code == 200
    assert criterio.titulo.encode() in resp.content


def test_criterio_detail_get_200(client, criterio):
    resp = client.get(criterio.get_absolute_url())
    assert resp.status_code == 200
    assert criterio.titulo.encode() in resp.content
    # Botões de export presentes
    assert b"Exportar PDF" in resp.content
    assert b"Exportar DOCX" in resp.content


def test_objeto_list_get_200(client, objeto):
    resp = client.get(reverse("criterios:objeto_list"))
    assert resp.status_code == 200


def test_objeto_detail_get_200(client, criterio, objeto):
    resp = client.get(objeto.get_absolute_url())
    assert resp.status_code == 200
    assert objeto.nome.encode() in resp.content


def test_ods_list_get_200(client, db_inicial):
    """Roda create_initial_ods e pega a página."""
    resp = client.get(reverse("criterios:ods_list"))
    assert resp.status_code == 200
    assert b"17" in resp.content  # algum ODS exibido


def test_ods_detail_get_200(client, db_inicial):
    resp = client.get(reverse("criterios:ods_detail", kwargs={"numero": 7}))
    assert resp.status_code == 200


def test_fase_detail_get_200(client, criterio):
    resp = client.get(reverse("criterios:fase_detail", kwargs={"slug": "tr-pb"}))
    assert resp.status_code == 200


def test_fase_detail_404_slug_invalido(client):
    resp = client.get(reverse("criterios:fase_detail", kwargs={"slug": "inexistente"}))
    assert resp.status_code == 404


def test_buscar_sem_query_get_200(client):
    resp = client.get(reverse("criterios:buscar"))
    assert resp.status_code == 200


def test_buscar_com_query_encontra(client, criterio):
    resp = client.get(reverse("criterios:buscar"), {"q": "exemplo"})
    assert resp.status_code == 200


def test_glossario_get_200(client, termo_glossario):
    resp = client.get(reverse("criterios:glossario"))
    assert resp.status_code == 200
    assert b"ETP" in resp.content


def test_pagina_institucional_get_200(client, pagina_institucional):
    resp = client.get("/sobre/")
    assert resp.status_code == 200
    assert b"Sobre a PESCP" in resp.content


def test_pagina_legal_get_200(client, pagina_legal):
    """Página legal renderiza com aviso amarelo de versão inicial."""
    resp = client.get("/transparencia/")
    assert resp.status_code == 200
    assert b"valida\xc3\xa7\xc3\xa3o" in resp.content.lower() or b"Vers\xc3\xa3o inicial" in resp.content
