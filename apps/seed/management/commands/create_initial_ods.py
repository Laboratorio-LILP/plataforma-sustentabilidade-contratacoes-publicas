"""Cria/atualiza os 17 ODS oficiais da Agenda 2030 ONU.

Idempotente: se um ODS já existe (por ``numero``), apenas atualiza os
campos que estavam vazios. Os ícones oficiais devem ser baixados pelo
time e colocados em ``media/ods/ods-NN.png``; este comando NÃO baixa
imagens externas.
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.normas.models import Ods

ODS_DATA = [
    (1, "Erradicação da pobreza", "#E5243B",
     "Acabar com a pobreza em todas as suas formas, em todos os lugares."),
    (2, "Fome zero e agricultura sustentável", "#DDA63A",
     "Acabar com a fome, alcançar a segurança alimentar e melhoria da nutrição e promover a agricultura sustentável."),
    (3, "Saúde e bem-estar", "#4C9F38",
     "Assegurar uma vida saudável e promover o bem-estar para todas e todos, em todas as idades."),
    (4, "Educação de qualidade", "#C5192D",
     "Assegurar a educação inclusiva e equitativa e de qualidade, e promover oportunidades de aprendizagem ao longo da vida para todas e todos."),
    (5, "Igualdade de gênero", "#FF3A21",
     "Alcançar a igualdade de gênero e empoderar todas as mulheres e meninas."),
    (6, "Água potável e saneamento", "#26BDE2",
     "Assegurar a disponibilidade e gestão sustentável da água e saneamento para todas e todos."),
    (7, "Energia limpa e acessível", "#FCC30B",
     "Assegurar o acesso confiável, sustentável, moderno e a preço acessível à energia para todas e todos."),
    (8, "Trabalho decente e crescimento econômico", "#A21942",
     "Promover o crescimento econômico sustentado, inclusivo e sustentável, emprego pleno e produtivo e trabalho decente para todas e todos."),
    (9, "Indústria, inovação e infraestrutura", "#FD6925",
     "Construir infraestruturas resilientes, promover a industrialização inclusiva e sustentável e fomentar a inovação."),
    (10, "Redução das desigualdades", "#DD1367",
     "Reduzir a desigualdade dentro dos países e entre eles."),
    (11, "Cidades e comunidades sustentáveis", "#FD9D24",
     "Tornar as cidades e os assentamentos humanos inclusivos, seguros, resilientes e sustentáveis."),
    (12, "Consumo e produção responsáveis", "#BF8B2E",
     "Assegurar padrões de produção e de consumo sustentáveis."),
    (13, "Ação contra a mudança global do clima", "#3F7E44",
     "Tomar medidas urgentes para combater a mudança do clima e seus impactos."),
    (14, "Vida na água", "#0A97D9",
     "Conservação e uso sustentável dos oceanos, dos mares e dos recursos marinhos para o desenvolvimento sustentável."),
    (15, "Vida terrestre", "#56C02B",
     "Proteger, recuperar e promover o uso sustentável dos ecossistemas terrestres, gerir de forma sustentável as florestas, combater a desertificação, deter e reverter a degradação da terra e deter a perda de biodiversidade."),
    (16, "Paz, justiça e instituições eficazes", "#00689D",
     "Promover sociedades pacíficas e inclusivas para o desenvolvimento sustentável, proporcionar o acesso à justiça para todos e construir instituições eficazes, responsáveis e inclusivas em todos os níveis."),
    (17, "Parcerias e meios de implementação", "#19486A",
     "Fortalecer os meios de implementação e revitalizar a parceria global para o desenvolvimento sustentável."),
]


class Command(BaseCommand):
    help = "Cria/atualiza os 17 ODS oficiais (idempotente)."

    @transaction.atomic
    def handle(self, *args, **options):
        criados = 0
        atualizados = 0
        for numero, nome, cor, descricao in ODS_DATA:
            obj, created = Ods.objects.get_or_create(
                numero=numero,
                defaults={
                    "nome": nome,
                    "cor_hex": cor,
                    "descricao_curta": descricao,
                },
            )
            if created:
                criados += 1
                continue
            mudou = False
            if not obj.nome:
                obj.nome = nome
                mudou = True
            if not obj.descricao_curta:
                obj.descricao_curta = descricao
                mudou = True
            if obj.cor_hex == "#000000" or not obj.cor_hex:
                obj.cor_hex = cor
                mudou = True
            if mudou:
                obj.save()
                atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"ODS oficiais sincronizados — {criados} criados, {atualizados} atualizados, "
                f"{Ods.objects.count()} total."
            )
        )
