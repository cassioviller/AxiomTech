#!/usr/bin/env python3
"""Rasteriza proposta-modelo.html (A4 a 139 dpi, 1152×1629: a faixa de 720 px do alvo é o RETANGULO do quadro, 1152×720, sem reamostragem) para site/img/o-proposta-modelo.webp, a fonte do documento
"veks-proposta-modelo" em documentos.json. Uso: python3 portfolio/cenas/proposta/proposta.py"""
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from render import navegador  # o Chromium do sistema (o do Playwright não roda no Replit)
DESTINO = AQUI.parent.parent / "site" / "img" / "o-proposta-modelo.webp"

with navegador() as nav:
    pg = nav.new_page(viewport={"width": 1152, "height": 1629}, device_scale_factor=1)
    pg.goto(AQUI.joinpath("proposta-modelo.html").as_uri())
    pg.wait_for_load_state("networkidle")
    pg.evaluate("document.fonts.ready")
    png = AQUI / "proposta-modelo.png"
    pg.screenshot(path=str(png), full_page=False)
subprocess.run(["magick", str(png), "-quality", "92", str(DESTINO)], check=True)
png.unlink()
print(DESTINO, subprocess.check_output(["magick", "identify", "-format", "%wx%h", str(DESTINO)]).decode(), DESTINO.stat().st_size // 1024, "KB")
