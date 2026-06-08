"""URLs do app conteudo — namespace ``conteudo``.

Cada slug institucional ou legal vira uma rota direta no nível raiz para
manter URLs amigáveis ao usuário (``/sobre/``, ``/transparencia/``) em
vez de subdiretório ``/conteudo/sobre/``.
"""

from django.urls import path

from . import views

app_name = "conteudo"

# Slugs institucionais e legais reconhecidos. A view diferencia legal
# para aplicar template com aviso jurídico.
SLUGS_PUBLICOS = [
    # Institucionais (menu superior)
    "sobre",
    "governanca",
    "metodologia",
    "parceiros",
    "contato",
    # Legais (rodapé e barra inferior)
    "transparencia",
    "acessibilidade",
    "politica-de-privacidade",
    "politica-de-cookies",
    "mapa-do-site",
    "fale-conosco",
]


urlpatterns = [
    path(f"{slug}/", views.pagina, {"slug": slug}, name=slug) for slug in SLUGS_PUBLICOS
]
