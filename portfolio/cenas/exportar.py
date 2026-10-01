#!/usr/bin/env python3
"""Exporta uma cena do site v2 para o Blender: geometria, materiais (com o tipo do kit), a pose de cada malha e da
câmera em cada quadro do vídeo (os mesmos tempos do render.py). Não desenha nada (window.poseCena), então leva segundos
e roda igual no Replit e no PC.

Uso: python3 portfolio/cenas/exportar.py --so modulares
Saída: portfolio/cenas/saida/export/<caso>/cena.json (+ os PNGs das texturas pintadas em canvas); fora do git.
Depois: blender -b -P portfolio/blender/montar.py -- --caso modulares   (ver portfolio/blender/LEIA-ME.md)
"""
import base64
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from render import CENAS, FPS, SAIDA, PRONTO_COM_PRAZO, navegador, quadros, servidor, tempo_local  # noqa: E402


def exportar(nav, base, caso):
    arquivo, dur = CENAS[caso]
    pg = nav.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
    pg.set_default_timeout(300000)
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.goto(f"{base}/cenas/{arquivo}")
    pg.wait_for_function("typeof window.poseCena === 'function' && !!window.PRONTO", timeout=120000)
    pg.evaluate(PRONTO_COM_PRAZO)
    pg.add_script_tag(content=(AQUI / "exportar.js").read_text(encoding="utf-8"))
    tempos = [tempo_local(k / FPS, dur) for k in range(quadros(dur))]
    dados = pg.evaluate("t => window.exportarCena(t)", tempos)
    if erros:
        sys.exit(f"{caso}: erro de JavaScript: {'; '.join(erros)}")
    pg.close()
    pasta = SAIDA / "export" / caso
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, url in dados.pop("canvases").items():
        (pasta / f"{nome}.png").write_bytes(base64.b64decode(url.split(",", 1)[1]))
    dados["meta"].update(caso=caso, fps=FPS, duracao=dur)
    destino = pasta / "cena.json"
    destino.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    animados = sum(1 for i in dados["itens"] if i["animado"])
    print(f"{caso}: {len(dados['itens'])} malhas ({animados} animadas), {len(dados['geometrias'])} geometrias, "
          f"{len(dados['materiais'])} materiais, {len(dados['arvores'])} árvores, {dados['meta']['quadros']} quadros "
          f"→ {destino} ({destino.stat().st_size / 1e6:.1f} MB)", flush=True)


def main():
    i = sys.argv.index("--so") + 1 if "--so" in sys.argv else 0
    if i and (i >= len(sys.argv) or sys.argv[i] not in CENAS):
        sys.exit(f"--so pede um caso de CENAS: {', '.join(CENAS)}")
    with servidor() as base, navegador() as nav:
        for caso in ([sys.argv[i]] if i else list(CENAS)):
            exportar(nav, base, caso)


if __name__ == "__main__":
    main()
