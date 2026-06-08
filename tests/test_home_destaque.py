"""Regressão da home: contagem de critérios na seção 'Objetos contratuais
em destaque' precisa somar self + filhos, pois critérios costumam ser
vinculados às folhas da hierarquia (profundidade máxima = 2)."""

import pytest
from django.urls import reverse

from apps.criterios.models import ObjetoContratual, StatusCriterio
from tests.conftest import CriterioFactory


pytestmark = pytest.mark.django_db


def test_home_contagem_objetos_destaque_inclui_filhos(client):
    super_cat = ObjetoContratual.objects.create(
        nome="Resíduos", slug="residuos", ordem=1, ativo=True
    )
    filho = ObjetoContratual.objects.create(
        nome="Pilhas", slug="pilhas", parent=super_cat, ordem=1, ativo=True
    )
    CriterioFactory(objeto_contratual=filho, status=StatusCriterio.PUBLICADO)
    CriterioFactory(objeto_contratual=filho, status=StatusCriterio.PUBLICADO)
    CriterioFactory(objeto_contratual=filho, status=StatusCriterio.RASCUNHO)

    resp = client.get(reverse("criterios:home"))
    assert resp.status_code == 200
    objetos_super = resp.context["objetos_super"]
    super_card = next(o for o in objetos_super if o.pk == super_cat.pk)
    assert super_card.total == 2


def test_home_contagem_objetos_destaque_inclui_proprios(client):
    """Quando o critério é vinculado direto à supercategoria, conta também."""
    super_cat = ObjetoContratual.objects.create(
        nome="Energia", slug="energia", ordem=2, ativo=True
    )
    CriterioFactory(objeto_contratual=super_cat, status=StatusCriterio.PUBLICADO)

    resp = client.get(reverse("criterios:home"))
    objetos_super = resp.context["objetos_super"]
    super_card = next(o for o in objetos_super if o.pk == super_cat.pk)
    assert super_card.total == 1
