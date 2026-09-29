#!/usr/bin/env python3
"""Prepara os documentos reais das cenas e da página do site v2: recorta cada fonte do manifesto (documentos.json)
para portfolio/site/docs/<id>.webp, grava o recorte do destaque para o celular (<id>-recorte.webp) e as coordenadas
em site/docs/destaques.json. Só aceita fontes já anonimizadas (LIBERADOS): nome de cliente e endereço borrados.

Uso: python3 portfolio/cenas/documentos.py
"""
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
MANIFESTO = AQUI / "documentos.json"
DOCS = RAIZ / "site" / "docs"
# prints do site já anonimizados (nome do cliente e endereço borrados; conferido em 25/09 no p-portal)
LIBERADOS = {"site/img/p-portal.webp", "site/img/p-fotos.webp", "site/img/p-diario-portal.webp"}


def cortar(fonte, caixa, destino):
    x, y, w, h = caixa
    subprocess.run(["magick", str(fonte), "-crop", f"{w}x{h}+{x}+{y}", "+repage", "-quality", "90", str(destino)], check=True)


def gerar():
    man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    DOCS.mkdir(parents=True, exist_ok=True)
    for velho in DOCS.iterdir():
        velho.unlink()
    destaques = {}
    for i, d in man.items():
        if d["fonte"] not in LIBERADOS:
            sys.exit(f"{i}: fonte {d['fonte']} não está em LIBERADOS (anonimizar antes e liberar à mão)")
        fonte = RAIZ / d["fonte"]
        cortar(fonte, d["corte"], DOCS / f"{i}.webp")
        if d.get("recorte"):
            cx, cy, _, _ = d["corte"]
            rx, ry, rw, rh = d["recorte"]
            cortar(fonte, [cx + rx, cy + ry, rw, rh], DOCS / f"{i}-recorte.webp")
        destaques[i] = {"largura": d["corte"][2], "altura": d["corte"][3], "destaque": d.get("destaque"), "recorte": d.get("recorte")}
    (DOCS / "destaques.json").write_text(json.dumps(destaques, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return destaques


if __name__ == "__main__":
    for k, v in gerar().items():
        print(k, v["largura"], "×", v["altura"])
