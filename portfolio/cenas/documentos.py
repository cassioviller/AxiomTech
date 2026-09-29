#!/usr/bin/env python3
"""Prepara os documentos reais das cenas e da página do site v2: recorta cada fonte do manifesto (documentos.json)
para portfolio/site/docs/<id>.webp, grava o recorte do destaque para o celular (<id>-recorte.webp) e as coordenadas
em site/docs/destaques.json. Só aceita fontes já revisadas (LIBERADOS): sem nome de cliente nem endereço legíveis.

Fontes: caminho relativo a portfolio/ (site/img/…); zip:<arquivo.zip na raiz do repositório>!<membro>;
pdf:<arquivo.zip na raiz>!<membro.pdf>#<página> (rasterizada a 200 dpi com pdftoppm). Os zips não estão no git.

Uso: python3 portfolio/cenas/documentos.py
"""
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent            # portfolio/
REPO = RAIZ.parent            # a raiz do repositório, onde ficam os zips
MANIFESTO = AQUI / "documentos.json"
DOCS = RAIZ / "site" / "docs"
# fontes revisadas à mão (25/09 e 29/09): prints do site já anonimizados; a obra de demonstração do sistema da VEKS
# (cliente fictício "Família Demo"); os documentos do B-36 (sem cliente); a proposta dos 36 min já publicada no site
LIBERADOS = {
    "site/img/p-portal.webp", "site/img/p-fotos.webp", "site/img/p-diario-portal.webp",
    "zip:saida.zip!saida/manual-do-app/prints/diretor-projetos-1-orcamento.png",
    "zip:saida.zip!saida/manual-do-app/prints/diretor-projetos-1-planta.png",
    "zip:casas pre moldadas (1).zip!B36-como-viaja-e-une.png",
    "zip:casas pre moldadas (1).zip!prancha-transporte-tiltup-gambrel.png",
    "pdf:casas pre moldadas (1).zip!b36-atas-decisoes-plano-de-acoes.pdf#1",
    "site/img/o-proposta.webp",
}
TEMP = Path(tempfile.mkdtemp(prefix="documentos-"))


def carregar(fonte):
    """Devolve o caminho de um arquivo de imagem para a fonte: extrai do zip e, se for PDF, rasteriza a página."""
    if not fonte.startswith(("zip:", "pdf:")):
        return RAIZ / fonte
    tipo, resto = fonte.split(":", 1)
    arquivo, membro = resto.split("!", 1)
    pagina = 1
    if tipo == "pdf":
        membro, pagina = membro.rsplit("#", 1)
        pagina = int(pagina)
    zp = REPO / arquivo
    if not zp.exists():
        sys.exit(f"{fonte}: {arquivo} não está na raiz do repositório (os zips ficam fora do git; pedir ao Cássio)")
    with zipfile.ZipFile(zp) as z:
        z.extract(membro, TEMP)
    extraido = TEMP / membro
    if tipo == "zip":
        return extraido
    saida = TEMP / f"{Path(membro).stem}-p{pagina}"
    subprocess.run(["pdftoppm", "-r", "200", "-png", "-f", str(pagina), "-l", str(pagina), "-singlefile", str(extraido), str(saida)], check=True)
    return saida.with_suffix(".png")


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
            sys.exit(f"{i}: fonte {d['fonte']} não está em LIBERADOS (revisar à mão e liberar)")
        fonte = carregar(d["fonte"])
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
