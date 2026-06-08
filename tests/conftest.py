"""Conftest do pytest — factories e fixtures compartilhadas."""

from __future__ import annotations

import factory
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from apps.conteudo.models import PaginaInstitucional, TermoGlossario
from apps.core.models import Tag
from apps.criterios.models import (
    Criterio,
    FaseProcesso,
    NivelAmbicao,
    ObjetoContratual,
    StatusCriterio,
    TipoContratacao,
)
from apps.normas.models import NormaLegal, Ods, SeloCertificacao
from apps.pilotos.models import PilotoLicitacao


User = get_user_model()


@pytest.fixture(autouse=True)
def _media_root(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "media"


@pytest.fixture
def usuario(db):
    return User.objects.create_user(username="bernardo", password="testpass123")


# ---------------------------- Factories ----------------------------
class OdsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ods
        django_get_or_create = ("numero",)

    numero = factory.Sequence(lambda n: n + 1)
    nome = factory.LazyAttribute(lambda o: f"ODS {o.numero}")
    cor_hex = "#0B9247"


class NormaLegalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = NormaLegal

    titulo_curto = factory.Sequence(lambda n: f"Lei {14_000 + n}/2021")
    titulo_completo = factory.LazyAttribute(lambda o: f"{o.titulo_curto} — texto completo")
    tipo = NormaLegal.Tipo.LEI_FEDERAL
    esfera = NormaLegal.Esfera.FEDERAL


class SeloCertificacaoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SeloCertificacao

    nome = factory.Sequence(lambda n: f"Selo {n}")
    tipo = SeloCertificacao.Tipo.NACIONAL


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ("nome",)

    nome = factory.Sequence(lambda n: f"tag-{n}")


class ObjetoContratualFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ObjetoContratual
        django_get_or_create = ("nome",)

    nome = factory.Sequence(lambda n: f"Objeto {n}")
    descricao = factory.Faker("sentence", locale="pt_BR")


class CriterioFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Criterio

    titulo = factory.Sequence(lambda n: f"Critério de exemplo {n}")
    objeto_contratual = factory.SubFactory(ObjetoContratualFactory)
    tipo_contratacao = TipoContratacao.BENS
    fase_processo = FaseProcesso.TR_PB
    nivel_ambicao = NivelAmbicao.BASICO
    texto_providencia = "<p>Exigir que o fornecedor apresente XYZ.</p>"
    determinacoes_principais = "<p>Lei 14.133/2021, art. 5º.</p>"
    justificativa_tecnica = "<p>Reduz impacto ambiental e custo total.</p>"
    metodo_verificacao = "<p>Apresentação de declaração assinada.</p>"
    status = StatusCriterio.PUBLICADO


class PilotoLicitacaoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PilotoLicitacao

    titulo = factory.Sequence(lambda n: f"Piloto {n}")
    unidade_compradora = "Secretaria de Educação"
    tipo_contratacao = TipoContratacao.BENS
    objeto_contratual = factory.SubFactory(ObjetoContratualFactory)


@pytest.fixture
def ods(db):
    return OdsFactory(numero=7, nome="Energia limpa e acessível")


@pytest.fixture
def norma(db):
    return NormaLegalFactory(titulo_curto="Lei 14.133/2021")


@pytest.fixture
def objeto(db):
    return ObjetoContratualFactory(nome="Pilhas e Baterias")


@pytest.fixture
def criterio(db, objeto, ods, norma):
    c = CriterioFactory(objeto_contratual=objeto, status=StatusCriterio.PUBLICADO)
    c.ods.add(ods)
    c.normas.add(norma)
    c.publicar()
    return c


@pytest.fixture
def pagina_institucional(db):
    return PaginaInstitucional.objects.create(
        slug="sobre",
        titulo="Sobre a PESCP",
        conteudo="<p>Conteúdo da página sobre.</p>",
        publicada=True,
    )


@pytest.fixture
def pagina_legal(db):
    return PaginaInstitucional.objects.create(
        slug="transparencia",
        titulo="Transparência",
        conteudo="<p>Transparência ativa.</p>",
        publicada=True,
    )


@pytest.fixture
def termo_glossario(db):
    return TermoGlossario.objects.create(
        termo="Estudo Técnico Preliminar",
        sigla="ETP",
        definicao="Documento que precede a contratação.",
    )


@pytest.fixture
def db_inicial(db):
    """Roda os management commands de seed inicial (ODS + páginas)."""
    call_command("create_initial_ods")
    call_command("create_initial_pages")
