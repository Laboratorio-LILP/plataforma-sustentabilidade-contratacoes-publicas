"""URLs do app criterios — namespace ``criterios``.

Inclui a home porque ela é apresentação dos critérios. O slug "/buscar/"
fica nesse app, e não em um app dedicado de busca, porque a busca é
sobre o domínio de critérios — não há nada mais a buscar na v1.0.
"""

from django.urls import path

from . import views

app_name = "criterios"

urlpatterns = [
    path("", views.home, name="home"),
    path("criterios/", views.criterio_list, name="list"),
    path("criterios/<slug:slug>/", views.criterio_detail, name="criterio_detail"),
    path("objetos/", views.objeto_list, name="objeto_list"),
    path("objetos/<slug:slug>/", views.objeto_detail, name="objeto_detail"),
    path("ods/", views.ods_list, name="ods_list"),
    path("ods/<int:numero>/", views.ods_detail, name="ods_detail"),
    path("fases/<slug:slug>/", views.fase_detail, name="fase_detail"),
    path("buscar/", views.buscar, name="buscar"),
    path("glossario/", views.glossario, name="glossario"),
]
