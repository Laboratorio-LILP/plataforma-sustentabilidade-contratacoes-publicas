from django.contrib import admin

from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "updated")
    search_fields = ("nome",)
    prepopulated_fields = {"slug": ("nome",)}
    ordering = ("nome",)
