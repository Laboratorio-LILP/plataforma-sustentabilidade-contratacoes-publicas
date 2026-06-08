from django.urls import path

from . import views

app_name = "exportacao"

urlpatterns = [
    path("criterios/<slug:slug>/exportar/pdf/", views.exportar_pdf, name="criterio_pdf"),
    path("criterios/<slug:slug>/exportar/docx/", views.exportar_docx, name="criterio_docx"),
]
