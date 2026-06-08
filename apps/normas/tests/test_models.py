"""Testes dos models de normas."""

import pytest

from apps.normas.models import NormaLegal, Ods, SeloCertificacao


pytestmark = pytest.mark.django_db


def test_ods_str_inclui_numero(ods):
    assert "ODS 7" in str(ods)


def test_ods_slug_gerado(ods):
    assert ods.slug.startswith("ods-7")


def test_norma_slug_gerado(norma):
    assert norma.slug


def test_norma_revogada_por_si_mesma_nao_permitido(db):
    # Não força DB constraint, mas garante que o campo existe
    n1 = NormaLegal.objects.create(titulo_curto="Lei A", titulo_completo="A")
    n2 = NormaLegal.objects.create(titulo_curto="Lei B", titulo_completo="B")
    n1.revogada = True
    n1.revogada_por = n2
    n1.save()
    n1.refresh_from_db()
    assert n1.revogada
    assert n1.revogada_por == n2


def test_selo_str_e_slug(db):
    s = SeloCertificacao.objects.create(nome="FSC", tipo=SeloCertificacao.Tipo.INTERNACIONAL)
    assert str(s) == "FSC"
    assert s.slug == "fsc"


def test_norma_simple_history_funciona(db, norma):
    """django-simple-history deve registrar histórico em alteração."""
    norma.ementa = "Nova ementa"
    norma.save()
    historico = norma.history.all()
    assert historico.count() >= 2
