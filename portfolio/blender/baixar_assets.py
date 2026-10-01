#!/usr/bin/env python3
"""Baixa os assets CC0 do Poly Haven listados em assets.json para portfolio/blender/assets/ (fora do git) e grava
assets/indice.json (arquivos, tamanho real do ladrilho em metros, autores) e ASSETS.md (a origem de cada um).
Só biblioteca padrão: roda no Replit e no PC. Confere o md5 de cada arquivo; o que já está em disco não é baixado de novo.

Uso: python portfolio/blender/baixar_assets.py
API: https://github.com/Poly-Haven/Public-API (pede um User-Agent próprio; os assets são CC0).
"""
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI / "assets"
API = "https://api.polyhaven.com"
AGENTE = {"User-Agent": "portfolio-cassio-viller/1.0 (render das cenas do site; github.com/cassioviller/AxiomTech)"}
MAPAS = {"cor": "Diffuse", "normal": "nor_gl", "rugosidade": "Rough", "relevo": "Displacement"}


def api(caminho):
    with urllib.request.urlopen(urllib.request.Request(f"{API}/{caminho}", headers=AGENTE), timeout=60) as r:
        return json.load(r)


def baixar(arquivo, destino):
    """arquivo = {url, md5, size} da API; baixa para destino se ainda não está lá com o md5 certo."""
    if destino.exists() and hashlib.md5(destino.read_bytes()).hexdigest() == arquivo["md5"]:
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(arquivo["url"], headers=AGENTE), timeout=600) as r:
        dados = r.read()
    if hashlib.md5(dados).hexdigest() != arquivo["md5"]:
        sys.exit(f"{arquivo['url']}: md5 diferente do informado pela API")
    destino.write_bytes(dados)
    print(f"  {destino.relative_to(AQUI)} ({len(dados) / 1e6:.1f} MB)", flush=True)


def main():
    man = json.loads((AQUI / "assets.json").read_text(encoding="utf-8"))
    res = man["resolucao"]
    indice, creditos = {"texturas": {}}, []
    h = man["hdri"]
    info = api(f"info/{h['id']}")
    arq = api(f"files/{h['id']}")["hdri"][h["resolucao"]]["hdr"]
    baixar(arq, ASSETS / "hdri" / f"{h['id']}.hdr")
    indice["hdri"] = f"hdri/{h['id']}.hdr"
    creditos.append((h["id"], "céu (HDRI)", info))
    for tipo, i in man["texturas"].items():
        tom = None
        if isinstance(i, dict):  # {"id": …, "tom": "#RRGGBB"}: a textura dá o desenho, o tom dá o matiz e a saturação
            i, tom = i["id"], i.get("tom")
        print(f"{tipo}: {i}", flush=True)
        info, arquivos = api(f"info/{i}"), api(f"files/{i}")
        mapas = {}
        for nome, chave in MAPAS.items():
            if chave in arquivos and res in arquivos[chave]:
                formato = "jpg" if "jpg" in arquivos[chave][res] else "png"
                baixar(arquivos[chave][res][formato], ASSETS / "texturas" / i / f"{nome}.{formato}")
                mapas[nome] = f"texturas/{i}/{nome}.{formato}"
        if "cor" not in mapas:
            sys.exit(f"{i}: sem mapa de cor em {res}")
        dim = info.get("dimensions") or [2000, 2000]  # mm
        indice["texturas"][tipo] = {"id": i, "mapas": mapas, "metros": [dim[0] / 1000, dim[1] / 1000], "tom": tom}
        creditos.append((i, f"textura do tipo `{tipo}`", info))
    (ASSETS / "indice.json").write_text(json.dumps(indice, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    linhas = ["# Assets do render no Blender", "",
              "Todos do [Poly Haven](https://polyhaven.com), licença CC0 (domínio público; uso livre, inclusive comercial).",
              "Gerado por `baixar_assets.py` a partir de `assets.json`; os arquivos ficam em `assets/`, fora do git.", "",
              "| Asset | Uso | Autor(es) |", "|---|---|---|"]
    linhas += [f"| [{i}](https://polyhaven.com/a/{i}) | {uso} | {', '.join(info.get('authors', {}))} |" for i, uso, info in creditos]
    (AQUI / "ASSETS.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print("pronto:", ASSETS)


if __name__ == "__main__":
    main()
