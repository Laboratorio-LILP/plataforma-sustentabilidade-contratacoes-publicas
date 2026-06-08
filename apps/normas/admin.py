from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import NormaLegal, Ods, SeloCertificacao


@admin.register(Ods)
class OdsAdmin(admin.ModelAdmin):
    list_display = ("numero", "nome", "cor_hex", "updated")
    search_fields = ("nome", "descricao_curta")
    ordering = ("numero",)
    readonly_fields = ("slug",)
    fieldsets = (
        ("Identificação", {"fields": ("numero", "nome", "slug", "cor_hex", "icone")}),
        ("Conteúdo", {"fields": ("descricao_curta", "descricao_longa", "metas")}),
    )


@admin.register(NormaLegal)
class NormaLegalAdmin(SimpleHistoryAdmin):
    list_display = ("titulo_curto", "esfera", "tipo", "numero", "data_publicacao", "revogada")
    list_filter = ("esfera", "tipo", "revogada")
    search_fields = ("titulo_curto", "titulo_completo", "numero", "ementa")
    autocomplete_fields = ("revogada_por",)
    readonly_fields = ("slug",)
    date_hierarchy = "data_publicacao"
    fieldsets = (
        ("Identificação", {"fields": ("titulo_curto", "titulo_completo", "slug", "numero")}),
        ("Classificação", {"fields": ("tipo", "esfera")}),
        ("Datas", {"fields": ("data_publicacao", "data_vigencia")}),
        ("Vigência", {"fields": ("revogada", "revogada_por")}),
        ("Conteúdo", {"fields": ("ementa", "link_oficial")}),
    )


@admin.register(SeloCertificacao)
class SeloCertificacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo", "link_oficial", "updated")
    list_filter = ("tipo",)
    search_fields = ("nome", "descricao")
    readonly_fields = ("slug",)
