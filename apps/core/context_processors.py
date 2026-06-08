"""Context processors globais.

Disponibilizam para todos os templates:
- current_url_name: para destacar item ativo do menu (aria-current="page")
- site_year: rodapé
- pescp_versao / pescp_data: aviso de versão 1.0 (visível no topo)
- pescp_contato_email: e-mail do LILP exibido em vários lugares
- counts agregados (critérios publicados, objetos, ODS) para a Home
"""

from __future__ import annotations

from datetime import datetime

from django.conf import settings


def site_context(request):
    current_url_name = ""
    if getattr(request, "resolver_match", None):
        current_url_name = request.resolver_match.url_name or ""
        if request.resolver_match.namespace:
            current_url_name = f"{request.resolver_match.namespace}:{request.resolver_match.url_name}"

    cfg = getattr(settings, "PESCP", {})

    contexto = {
        "current_url_name": current_url_name,
        "site_year": datetime.now().year,
        "pescp_versao": cfg.get("VERSAO_ROTULO", "1.0"),
        "pescp_data": cfg.get("VERSAO_DATA", "junho/2026"),
        "pescp_contato_email": cfg.get("CONTATO_EMAIL", "lab.sggd@sp.gov.br"),
        "pescp_public_url": cfg.get("PUBLIC_URL", "http://localhost:8000"),
    }

    # Contagens cheap usadas pelos partials de header/home.
    # Importação lazy evita ciclos no boot e quebra de migration.
    try:
        from apps.criterios.models import Criterio, ObjetoContratual
        from apps.normas.models import Ods

        contexto.update(
            {
                "total_criterios": Criterio.objects.filter(status="PUBLICADO").count(),
                "total_objetos": ObjetoContratual.objects.filter(ativo=True).count(),
                "total_ods": Ods.objects.count(),
            }
        )
    except Exception:  # tabelas ainda não criadas (primeiro migrate)
        contexto.update({"total_criterios": 0, "total_objetos": 0, "total_ods": 0})

    return contexto
