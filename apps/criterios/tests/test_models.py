"""Testes dos models centrais de criterios."""

import pytest

from apps.criterios.models import (
    Criterio,
    FaseProcesso,
    NivelAmbicao,
    ObjetoContratual,
    StatusCriterio,
)


pytestmark = pytest.mark.django_db


def test_objeto_slug_e_str(objeto):
    """ObjetoContratual gera slug e __str__ correto."""
    assert objeto.slug
    assert str(objeto) == objeto.nome


def test_objeto_hierarquia(db):
    super_obj = ObjetoContratual.objects.create(nome="Resíduos", descricao="Super")
    filho = ObjetoContratual.objects.create(nome="Pilhas", parent=super_obj)
    assert filho.parent == super_obj
    assert str(filho) == "Resíduos › Pilhas"
    assert super_obj.eh_supercategoria is True
    assert filho.eh_supercategoria is False
    assert super_obj.descendentes().count() == 2


def test_criterio_gera_codigo_automatico(objeto):
    c = Criterio.objects.create(
        titulo="Teste",
        objeto_contratual=objeto,
        texto_providencia="<p>Exigência X</p>",
        determinacoes_principais="<p>Lei Y</p>",
        justificativa_tecnica="<p>Justificativa</p>",
        metodo_verificacao="<p>Verificação</p>",
    )
    assert c.codigo.startswith("CRIT-")
    assert c.codigo.endswith("-001")
    assert c.slug


def test_criterio_codigo_sequencial(objeto):
    Criterio.objects.create(
        titulo="Primeiro",
        objeto_contratual=objeto,
        texto_providencia="x",
        determinacoes_principais="x",
        justificativa_tecnica="x",
        metodo_verificacao="x",
    )
    c2 = Criterio.objects.create(
        titulo="Segundo",
        objeto_contratual=objeto,
        texto_providencia="x",
        determinacoes_principais="x",
        justificativa_tecnica="x",
        metodo_verificacao="x",
    )
    assert c2.codigo.endswith("-002")


def test_criterio_publicar_seta_data(objeto):
    c = Criterio.objects.create(
        titulo="X",
        objeto_contratual=objeto,
        texto_providencia="x",
        determinacoes_principais="x",
        justificativa_tecnica="x",
        metodo_verificacao="x",
    )
    assert c.publicado_em is None
    c.publicar()
    c.refresh_from_db()
    assert c.publicado_em is not None
    assert c.status == StatusCriterio.PUBLICADO


def test_criterio_search_vector_populado(criterio):
    """Após save, search_vector deve estar preenchido."""
    criterio.refresh_from_db()
    assert criterio.search_vector is not None


def test_criterio_busca_acha_por_titulo(objeto, criterio):
    """Busca FTS encontra critério via título com query em português."""
    from apps.criterios.search import buscar_criterios

    qs = Criterio.objects.filter(pk=criterio.pk)
    resultados = list(buscar_criterios(qs, "exemplo"))
    assert criterio in resultados


def test_choices_paradigma_fechado():
    """Garante que as TextChoices têm os valores prometidos no prompt."""
    assert set(dict(FaseProcesso.choices).keys()) == {"ETP", "TR_PB", "EDITAL", "EXECUCAO", "FISCALIZACAO"}
    assert set(dict(NivelAmbicao.choices).keys()) == {"BASICO", "INTERMEDIARIO", "AVANCADO"}
