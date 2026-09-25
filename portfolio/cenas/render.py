#!/usr/bin/env python3
"""Renderiza as cenas do site v2 (portfolio/cenas/<arquivo>.html) em vídeo 1920×1080 e pôster.
Cada cena é um módulo que expõe window.renderCena(t) (t = tempo local 0..10) e window.PRONTO (texturas prontas).
As cenas importam módulos ES: file:// não serve, então portfolio/ é servido com Range numa porta local.

Uso: python3 portfolio/cenas/render.py --so sige
Saídas: portfolio/cenas/saida/<caso>-mestre.mp4  mestre 1920×1080 crf 16 (ignorado pelo git)
        portfolio/site/video/v2-<caso>.mp4       1920×1080, 24 fps, H.264 High 4.0, GOP 4, sem áudio
        portfolio/site/video/v2-<caso>.webp      pôster = último quadro
"""
import re
import shutil
import subprocess
import sys
import threading
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent  # portfolio/cenas
RAIZ = AQUI.parent                      # portfolio
SAIDA = AQUI / "saida"
WEB = RAIZ / "site" / "video"
sys.path.insert(0, str(RAIZ))
from servir import ComRange  # noqa: E402

LARGURA, ALTURA = 1920, 1080
ARGS = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"]
PRONTO_COM_PRAZO = ("Promise.race([window.PRONTO, new Promise(function(_, falha){setTimeout(function(){"
                    "falha(new Error('PRONTO: 30 s sem resolver (textura de documento?)'));}, 30000);})])")


class SemRange(SimpleHTTPRequestHandler):
    """Servidor sem Range (HTTP 200 sempre): o caso do Safari numa hospedagem simples."""
    def log_message(self, *_):
        pass


@contextmanager
def servidor(com_range=True):
    """portfolio/ servido numa porta livre, numa thread; devolve a URL base (sem barra final)."""
    classe = ComRange if com_range else SemRange
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(classe, directory=str(RAIZ)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{srv.server_address[1]}"
    finally:
        srv.shutdown()
        srv.server_close()


@contextmanager
def navegador():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = shutil.which("chromium")  # no Replit o Chromium do Playwright não roda: usa o do sistema
        nav = p.chromium.launch(executable_path=exe, args=ARGS) if exe else p.chromium.launch(args=ARGS)
        try:
            yield nav
        finally:
            nav.close()


def abrir_cena(nav, url):
    """Página 1920×1080 (escala 1) com a cena carregada e as texturas prontas; devolve (página, lista de erros de JS)."""
    pg = nav.new_page(viewport={"width": LARGURA, "height": ALTURA}, device_scale_factor=1)
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    pg.goto(url)
    pg.wait_for_function("typeof window.renderCena === 'function' && !!window.PRONTO", timeout=60000)
    pg.evaluate(PRONTO_COM_PRAZO)
    return pg, erros
