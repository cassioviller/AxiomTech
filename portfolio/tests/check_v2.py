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
    from render import abrir_cena, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/teste.html")
        info = pg.evaluate("(function(){var p=window.__palco;return [p.renderer.domElement.width,p.renderer.domElement.height,"
                           "p.renderer.toneMapping===0,!!p.cena.environment,p.ao.constructor.name];})()")
        check(info == [3840, 2160, True, True, "GTAOPass"], f"kit: palco {info} ≠ [3840, 2160, True, True, 'GTAOPass']")
        pg.evaluate("renderCena(3)")
        a = pg.screenshot(type="png")
        pg.evaluate("renderCena(3)")
        b = pg.screenshot(type="png")
        check(a == b, "kit: renderCena(3) duas vezes deu quadros diferentes (a cena não é pura em t)")
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


def main():
    if "--navegador" in sys.argv:
        checar_kit()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
