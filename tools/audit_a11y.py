"""Auditoria de acessibilidade WCAG 2.0 AA via pa11y.

Roda pa11y contra as principais URLs públicas da PESCP. Requer Node 18+
e ``npx pa11y`` disponível no host.

Uso:
    python tools/audit_a11y.py
    python tools/audit_a11y.py --host http://localhost:8000
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys

URLS_PADRAO = [
    "/",
    "/criterios/",
    "/objetos/",
    "/ods/",
    "/glossario/",
    "/buscar/",
    "/sobre/",
    "/governanca/",
    "/metodologia/",
    "/parceiros/",
    "/contato/",
    "/transparencia/",
    "/acessibilidade/",
    "/politica-de-privacidade/",
    "/politica-de-cookies/",
    "/mapa-do-site/",
    "/fale-conosco/",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:8000", help="URL base do portal")
    parser.add_argument("--standard", default="WCAG2AA", help="Padrão pa11y (WCAG2A/AA/AAA)")
    args = parser.parse_args()

    if not shutil.which("npx"):
        print("ERRO: npx não encontrado. Instale Node 18+ no host.", file=sys.stderr)
        return 2

    erros_totais = 0
    for caminho in URLS_PADRAO:
        url = f"{args.host.rstrip('/')}{caminho}"
        print()
        print(f"==> {url}")
        cmd = ["npx", "--yes", "pa11y", "--standard", args.standard, url]
        proc = subprocess.run(cmd, check=False)
        if proc.returncode != 0:
            erros_totais += 1

    print()
    print(f"Auditoria concluída — {erros_totais} URLs com problemas reportados.")
    return 0 if erros_totais == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
