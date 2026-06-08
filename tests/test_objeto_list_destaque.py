"""Regressão de /objetos/: contagem da supercategoria precisa somar
critérios próprios + dos filhos (mesma estratégia da home — critérios
costumam ser vinculados às folhas da hierarquia)."""

import pytest
from django.urls import reverse

from apps.criterios.models import ObjetoContratual, StatusCriterio
from tests.conftest import CriterioFactory


pytestmark = pytest.mark.django_db


def test_objeto_list_supercategoria_soma_filhos(client):
    super_cat = ObjetoContratual.objects.create(
        nome="Resíduos", slug="residuos", ordem=1, ativo=True
    )
    filho = ObjetoContratual.objects.create(
        nome="Pilhas", slug="pilhas", parent=super_cat, ordem=1, ativo=True
    )
    CriterioFactory(objeto_contratual=filho, status=StatusCriterio.PUBLICADO)
    CriterioFactory(objeto_contratual=filho, status=StatusCriterio.PUBLICADO)
    CriterioFactory(objeto_contratual=filho, status=StatusCriterio.RASCUNHO)

    resp = client.get(reverse("criterios:objeto_list"))
    assert resp.status_code == 200
    supers = resp.context["supercategorias"]
    super_card = next(s for s in supers if s.pk == super_cat.pk)
    assert super_card.total == 2
    # Filho mantém sua contagem própria (só publicados)
    filho_card = next(f for f in super_card.filhos.all() if f.pk == filho.pk)
    assert filho_card.total == 2


def test_objeto_list_supercategoria_soma_proprios(client):
    """Critério vinculado direto à supercategoria também conta."""
    super_cat = ObjetoContratual.objects.create(
        nome="Energia", slug="energia", ordem=2, ativo=True
    )
    CriterioFactory(objeto_contratual=super_cat, status=StatusCriterio.PUBLICADO)

    resp = client.get(reverse("criterios:objeto_list"))
    supers = resp.context["supercategorias"]
    super_card = next(s for s in supers if s.pk == super_cat.pk)
    assert super_card.total == 1


def test_objeto_list_supercategoria_zero_quando_nada_publicado(client):
    """Supercategoria sem critérios publicados (nem self nem filhos) zera."""
    super_cat = ObjetoContratual.objects.create(
        nome="Madeira", slug="madeira", ordem=3, ativo=True
    )
    filho = ObjetoContratual.objects.create(
        nome="Mobiliário", slug="mobiliario", parent=super_cat, ordem=1, ativo=True
    )
    CriterioFactory(objeto_contratual=filho, status=StatusCriterio.RASCUNHO)

    resp = client.get(reverse("criterios:objeto_list"))
    supers = resp.context["supercategorias"]
    super_card = next(s for s in supers if s.pk == super_cat.pk)
    assert super_card.total == 0
