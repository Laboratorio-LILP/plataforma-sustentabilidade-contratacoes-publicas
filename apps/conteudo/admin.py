from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import DocumentoApoio, PaginaInstitucional, TermoGlossario


@admin.register(PaginaInstitucional)
class PaginaInstitucionalAdmin(SimpleHistoryAdmin):
    list_display = ("titulo", "slug", "ordem", "publicada", "updated")
    list_filter = ("publicada",)
    search_fields = ("titulo", "slug", "conteudo")
    list_editable = ("ordem", "publicada")
    readonly_fields = ("slug",)
    fieldsets = (
        ("Identificação", {"fields": ("titulo", "slug", "ordem", "publicada")}),
        ("SEO", {"fields": ("meta_description",)}),
        ("Conteúdo", {"fields": ("conteudo",)}),
    )


@admin.register(TermoGlossario)
class TermoGlossarioAdmin(admin.ModelAdmin):
    list_display = ("termo", "sigla", "updated")
    search_fields = ("termo", "sigla", "definicao")
    autocomplete_fields = ("normas_relacionadas",)
    readonly_fields = ("slug",)


@admin.register(DocumentoApoio)
class DocumentoApoioAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "objeto_contratual", "extensao", "tamanho_bytes", "created")
    list_filter = ("tipo", "objeto_contratual")
    search_fields = ("titulo", "descricao")
    autocomplete_fields = ("objeto_contratual",)
    readonly_fields = ("tamanho_bytes", "extensao", "created", "updated")
