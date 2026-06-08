from django.contrib import admin, messages
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource
from simple_history.admin import SimpleHistoryAdmin

from .models import Criterio, ObjetoContratual, StatusCriterio


class CriterioResource(ModelResource):
    class Meta:
        model = Criterio
        fields = (
            "codigo",
            "titulo",
            "slug",
            "objeto_contratual__slug",
            "tipo_contratacao",
            "fase_processo",
            "nivel_ambicao",
            "texto_providencia",
            "determinacoes_principais",
            "justificativa_tecnica",
            "metodo_verificacao",
            "precaucoes",
            "fonte",
            "status",
        )


@admin.register(ObjetoContratual)
class ObjetoContratualAdmin(admin.ModelAdmin):
    list_display = ("nome", "parent", "ordem", "ativo", "total_criterios")
    list_filter = ("ativo", "parent")
    search_fields = ("nome", "descricao")
    autocomplete_fields = ("parent",)
    readonly_fields = ("slug",)
    list_editable = ("ordem", "ativo")
    ordering = ("parent__nome", "ordem", "nome")

    @admin.display(description="Critérios")
    def total_criterios(self, obj):
        return obj.criterios.count()


@admin.register(Criterio)
class CriterioAdmin(ImportExportMixin, SimpleHistoryAdmin):
    resource_class = CriterioResource

    list_display = (
        "codigo",
        "titulo",
        "objeto_contratual",
        "fase_processo",
        "nivel_ambicao",
        "status",
        "updated",
    )
    list_filter = (
        "status",
        "fase_processo",
        "nivel_ambicao",
        "tipo_contratacao",
        "objeto_contratual",
        "ods",
        "normas",
    )
    search_fields = ("titulo", "codigo", "texto_providencia", "fonte")
    autocomplete_fields = ("objeto_contratual", "ods", "normas", "selos", "tags", "criado_por")
    readonly_fields = ("codigo", "slug", "search_vector", "created", "updated", "publicado_em")
    save_on_top = True

    fieldsets = (
        ("Identificação", {"fields": ("codigo", "titulo", "slug", "status")}),
        (
            "Classificação",
            {
                "fields": (
                    "objeto_contratual",
                    "tipo_contratacao",
                    "fase_processo",
                    "nivel_ambicao",
                )
            },
        ),
        (
            "Conteúdo",
            {
                "fields": (
                    "texto_providencia",
                    "determinacoes_principais",
                    "justificativa_tecnica",
                    "metodo_verificacao",
                    "precaucoes",
                )
            },
        ),
        ("Relações", {"fields": ("ods", "normas", "selos", "tags")}),
        ("Metadados editoriais", {"fields": ("fonte", "criado_por", "publicado_em", "created", "updated")}),
    )

    actions = ("acao_publicar", "acao_arquivar", "acao_rascunho")

    @admin.action(description="Publicar selecionados")
    def acao_publicar(self, request, queryset):
        n = 0
        for c in queryset:
            c.publicar(usuario=request.user)
            n += 1
        self.message_user(request, f"{n} critério(s) publicado(s).", messages.SUCCESS)

    @admin.action(description="Arquivar selecionados")
    def acao_arquivar(self, request, queryset):
        n = 0
        for c in queryset:
            c.arquivar()
            n += 1
        self.message_user(request, f"{n} critério(s) arquivado(s).", messages.SUCCESS)

    @admin.action(description="Voltar para rascunho")
    def acao_rascunho(self, request, queryset):
        n = queryset.update(status=StatusCriterio.RASCUNHO)
        self.message_user(request, f"{n} critério(s) voltados para rascunho.", messages.SUCCESS)
