"""URLs do projeto PESCP — orquestra apps públicos e o Admin."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Apps públicos — ordem do mais específico para o mais genérico
    path("", include("apps.criterios.urls")),
    path("", include("apps.exportacao.urls")),
    path("", include("apps.conteudo.urls")),  # páginas institucionais e legais
]

# Servir media em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Branding institucional do Admin
admin.site.site_header = "PESCP — Administração"
admin.site.site_title = "PESCP — Admin"
admin.site.index_title = "Plataforma Estadual de Sustentabilidade em Contratações Públicas"
