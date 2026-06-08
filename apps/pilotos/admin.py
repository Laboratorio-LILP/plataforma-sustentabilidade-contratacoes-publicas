from django.contrib import admin

from .models import AvaliacaoImpacto, PilotoLicitacao


class AvaliacaoImpactoInline(admin.StackedInline):
    model = AvaliacaoImpacto
    can_delete = True
    extra = 0
    fieldsets = (
        (
            "Impacto quantitativo",
            {"fields": ("economia_lcc_estimada", "reducao_co2_estimada_ton", "data_avaliacao")},
        ),
        (
            "Impacto qualitativo",
            {"fields": ("impactos_sociais", "impactos_ambientais")},
        ),
        (
            "Lições e recomendações",
            {"fields": ("licoes_aprendidas", "recomendacoes_para_proximas_contratacoes")},
        ),
    )


@admin.register(PilotoLicitacao)
class PilotoLicitacaoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "titulo",
        "unidade_compradora",
        "tipo_contratacao",
        "estagio_atual",
        "valor_homologado",
        "data_inicio",
    )
    list_filter = ("estagio_atual", "tipo_contratacao", "objeto_contratual")
    search_fields = ("titulo", "codigo", "unidade_compradora", "numero_processo_sei", "numero_edital")
    autocomplete_fields = ("objeto_contratual", "criterios_aplicados", "criado_por")
    readonly_fields = ("codigo", "created", "updated")
    date_hierarchy = "data_inicio"
    inlines = [AvaliacaoImpactoInline]

    fieldsets = (
        ("Identificação", {"fields": ("codigo", "titulo", "unidade_compradora")}),
        (
            "Classificação",
            {"fields": ("tipo_contratacao", "objeto_contratual", "criterios_aplicados")},
        ),
        ("Estágio e valores", {"fields": ("estagio_atual", "valor_estimado", "valor_homologado")}),
        (
            "Datas",
            {"fields": ("data_inicio", "data_homologacao", "data_conclusao")},
        ),
        (
            "Referências processuais",
            {"fields": ("numero_processo_sei", "numero_edital")},
        ),
        ("Observações", {"fields": ("observacoes",)}),
        (
            "Metadados",
            {"fields": ("criado_por", "publicar_pagina", "created", "updated")},
        ),
    )


@admin.register(AvaliacaoImpacto)
class AvaliacaoImpactoAdmin(admin.ModelAdmin):
    list_display = ("piloto", "economia_lcc_estimada", "reducao_co2_estimada_ton", "data_avaliacao")
    search_fields = ("piloto__codigo", "piloto__titulo")
    autocomplete_fields = ("piloto",)
    date_hierarchy = "data_avaliacao"
