#!/usr/bin/env python3
"""Checagens do site v2 (piloto): kit das cenas, documentos, cena do caso SIGE, vídeo e página.

Uso: python3 portfolio/tests/check_v2.py              (estático: documentos, texto, marcação)
     python3 portfolio/tests/check_v2.py --navegador  (+ kit, cena e página no Chromium, via servidor local)
     python3 portfolio/tests/check_v2.py --video      (+ vídeo publicado)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]  # portfolio/
SITE = RAIZ / "site"
CENAS_DIR = RAIZ / "cenas"
sys.path.insert(0, str(CENAS_DIR))
FALHAS = []


def check(cond, msg):
    if not cond:
        FALHAS.append(msg)


def checar_kit():
    """teste.html no Chromium: renderer 2× (3840×2160), sem tone mapping, com ambiente; renderCena determinístico;
    a oclusão (GTAO) escurece o canto parede-piso; nenhum erro de JS."""
    from render import abrir_cena, capturar, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/teste.html")
        info = pg.evaluate("(function(){var p=window.__palco;return [p.renderer.domElement.width,p.renderer.domElement.height,"
                           "p.renderer.toneMapping===0,!!p.cena.environment,p.ao.constructor.name];})()")
        check(info == [3840, 2160, True, True, "GTAOPass"], f"kit: palco {info} ≠ [3840, 2160, True, True, 'GTAOPass']")
        # a captura lê o buffer do WebGL (render.capturar), não o compositor: o 1º pg.screenshot depois de carregar saía vazio
        pg.evaluate("renderCena(3)")
        a = capturar(pg)
        pg.evaluate("renderCena(3)")
        b = capturar(pg)
        check(a == b, "kit: renderCena(3) duas vezes deu quadros diferentes (a cena não é pura em t)")
        pg.evaluate("renderCena(4)")
        check(capturar(pg) != a and len(a) > 100000, "kit: a captura não muda com t (não está lendo o render)")
        # o canto parede-piso (0; 0,05; -1,95) projetado em pixels; média de luminância 24×24 com e sem GTAO
        px = pg.evaluate("(function(){var v=new (window.__palco.THREE.Vector3)(0,.05,-1.95).project(window.__palco.camera);"
                         "return [Math.round((v.x+1)/2*1920),Math.round((1-v.y)/2*1080)];})()")
        lum = []
        for ligado in ("true", "false"):
            pg.evaluate(f"window.__palco.ao.enabled={ligado};renderCena(3)")
            lum.append(pg.evaluate(
                "(function(x,y){var c=document.createElement('canvas');c.width=24;c.height=24;var g=c.getContext('2d');"
                "var s=window.__palco.renderer.domElement;g.drawImage(s,(x-12)*2,(y-12)*2,48,48,0,0,24,24);"
                "var d=g.getImageData(0,0,24,24).data,t=0;for(var i=0;i<d.length;i+=4)t+=(d[i]+d[i+1]+d[i+2])/3;return t/(d.length/4);})"
                f"({px[0]},{px[1]})"))
        check(lum[0] <= lum[1] - 3, f"kit: o GTAO não escureceu o canto (com {lum[0]:.1f}, sem {lum[1]:.1f})")
        check(not erros, f"kit: erros de JS em teste.html: {erros}")


def ffprobe(arquivo):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(arquivo)],
                       capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def checar_render():
    """render.py com a cena de teste: 1 s → 24 quadros 1920×1080; encode web H.264 High 4.0, sem áudio;
    pontas paradas (os dois primeiros quadros iguais); o pôster é o último quadro (PSNR ≥ 40 dB)."""
    import render
    with tempfile.TemporaryDirectory() as tmp, render.servidor() as base, render.navegador() as nav:
        tmp = Path(tmp)
        pg, erros = render.abrir_cena(nav, f"{base}/cenas/teste.html")
        mestre, web, cartaz = tmp / "teste-mestre.mp4", tmp / "teste.mp4", tmp / "teste.webp"
        render.renderizar(pg, 1.0, mestre)
        render.encode_web(mestre, web, render.CRF)
        render.poster(web, 1.0, cartaz)
        info = ffprobe(web)
        v = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
        a = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
        check(len(v) == 1 and (v[0]["width"], v[0]["height"]) == (1920, 1080), f"render: vídeo {v and (v[0]['width'], v[0]['height'])} ≠ 1920×1080")
        check(v and v[0].get("nb_frames") == "24", f"render: {v and v[0].get('nb_frames')} quadros em 1 s, esperava 24")
        check(v and v[0].get("profile") == "High" and v[0].get("level") == 40, f"render: perfil {v and (v[0].get('profile'), v[0].get('level'))} ≠ High 4.0")
        check(not a, "render: o vídeo tem trilha de áudio")
        q0, q1 = tmp / "q0.png", tmp / "q1.png"
        for n, f in ((0, q0), (1, q1)):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mestre), "-vf", f"select='eq(n,{n})'", "-vframes", "1", str(f)], check=True)
        check(render.psnr(q0, q1) >= 50, "render: o início não está parado (quadros 0 e 1 diferentes)")
        check(cartaz.exists() and cartaz.stat().st_size <= render.TETO_POSTER, "render: pôster ausente ou acima do teto")
        check(not erros, f"render: erros de JS: {erros}")


DOCS = SITE / "docs"


def dims(arquivo):
    r = subprocess.run(["magick", "identify", "-format", "%w %h", str(arquivo)], capture_output=True, text=True)
    return tuple(int(x) for x in r.stdout.split()) if r.returncode == 0 else None


def checar_documentos():
    """site/docs: só o que o manifesto lista, vindo só de fontes liberadas (já anonimizadas); dimensões conferem;
    o destaque cai dentro da imagem e dentro do recorte."""
    from documentos import LIBERADOS, MANIFESTO
    man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    check((DOCS / "destaques.json").exists(), "documentos: site/docs/destaques.json ausente (rodar documentos.py)")
    if not (DOCS / "destaques.json").exists():
        return
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))
    esperados = {f"{i}.webp" for i in man} | {f"{i}-recorte.webp" for i, d in man.items() if d.get("recorte")} | {"destaques.json"}
    achados = {p.name for p in DOCS.iterdir()}
    check(achados == esperados, f"documentos: site/docs tem {sorted(achados ^ esperados)} fora do manifesto (ou falta)")
    for i, d in man.items():
        check(d["fonte"] in LIBERADOS, f"documentos: {i} vem de {d['fonte']}, fora das fontes anonimizadas liberadas")
        x, y, w, h = d["corte"]
        check(dims(DOCS / f"{i}.webp") == (w, h), f"documentos: {i}.webp {dims(DOCS / f'{i}.webp')} ≠ corte {w}×{h}")
        check(dest.get(i, {}).get("largura") == w and dest[i].get("altura") == h, f"documentos: destaques.json de {i} sem as dimensões do corte")
        if d.get("destaque"):
            dx, dy, dw, dh = d["destaque"]
            check(0 <= dx and 0 <= dy and dx + dw <= w and dy + dh <= h, f"documentos: destaque de {i} fora da imagem")
            check(dest[i]["destaque"] == d["destaque"], f"documentos: destaques.json de {i} ≠ manifesto")
        if d.get("recorte"):
            rx, ry, rw, rh = d["recorte"]
            check(dims(DOCS / f"{i}-recorte.webp") == (rw, rh), f"documentos: recorte de {i} com dimensões erradas")
            if d.get("destaque"):
                check(rx <= dx and ry <= dy and dx + dw <= rx + rw and dy + dh <= ry + rh, f"documentos: o recorte de {i} não contém o destaque")
    check(set(man) >= {"sige-portal", "sige-fotos", "sige-rdo"}, "documentos: o caso SIGE pede sige-portal, sige-fotos e sige-rdo")


def main():
    checar_documentos()
    if "--navegador" in sys.argv:
        checar_kit()
        checar_render()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
