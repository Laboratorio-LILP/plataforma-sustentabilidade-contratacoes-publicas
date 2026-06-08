"""Testes das templatetags pescp_tags."""

import pytest
from django.http import QueryDict
from django.template import Context, Template


pytestmark = pytest.mark.django_db


def _render(template_str, ctx=None):
    return Template("{% load pescp_tags %}" + template_str).render(Context(ctx or {}))


def test_pluralize_pt_singular():
    assert _render('{{ 1|pluralize_pt:"critério" }}') == "critério"


def test_pluralize_pt_plural():
    assert _render('{{ 3|pluralize_pt:"critério" }}') == "critérios"


def test_pluralize_pt_irregular_ao():
    assert _render('{{ 2|pluralize_pt:"contratação" }}') == "contratações"


def test_url_toggle_facet_adiciona(rf):
    request = rf.get("/criterios/")
    contexto = {"request": request}
    rendered = _render('{% url_toggle_facet "ods" 7 %}', contexto)
    assert "ods=7" in rendered


def test_url_toggle_facet_remove(rf):
    request = rf.get("/criterios/?ods=7")
    contexto = {"request": request}
    rendered = _render('{% url_toggle_facet "ods" 7 %}', contexto)
    assert "ods=7" not in rendered


def test_is_facet_active_true():
    qd = QueryDict("ods=7&ods=12")
    rendered = _render(
        '{% if querydict|is_facet_active:"ods=7" %}ATIVA{% endif %}',
        {"querydict": qd},
    )
    assert rendered == "ATIVA"
