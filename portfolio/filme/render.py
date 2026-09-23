#!/usr/bin/env python3
"""Gera o trailer da história a partir de film.html, quadro a quadro (renderAt), e a versão para a web.

Uso: python3 portfolio/filme/render.py              (filme inteiro, ~13 min em CPU)
     python3 portfolio/filme/render.py --segundos 3 (ensaio curto)
Saídas: portfolio/filme/saida/historia-1280.mp4   mestre 1280×720 (fora do site, ignorado pelo git)
        portfolio/site/video/historia.mp4         960×540, H.264, sem áudio, +faststart
        portfolio/site/video/historia.jpg         capa 960×540 (o quadro da ficha de abertura)
"""
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida"
WEB = AQUI.parent / "site" / "video"
FPS = 30
T_CAPA = 3.0  # segundo em que a ficha de abertura (nome, cargo, contato) está inteira na tela
ARGS = ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist", "--allow-file-access-from-files"]


def main():
    segundos = float(sys.argv[sys.argv.index("--segundos") + 1]) if "--segundos" in sys.argv else None
    SAIDA.mkdir(exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    mestre, capa = SAIDA / "historia-1280.mp4", SAIDA / "capa-1280.jpg"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-vcodec", "mjpeg",
                           "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", str(mestre)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        # no Replit o Chromium baixado pelo Playwright não roda (faltam bibliotecas do sistema): usa o do sistema
        exe = shutil.which("chromium")
        navegador = p.chromium.launch(executable_path=exe, args=ARGS) if exe else p.chromium.launch(args=ARGS)
        pagina = navegador.new_page(viewport={"width": 1280, "height": 720})
        pagina.goto((AQUI / "film.html").as_uri())
        pagina.wait_for_timeout(2500)
        total = segundos if segundos is not None else pagina.evaluate("TOTAL")
        n = int(round(total * FPS))
        for i in range(n):
            pagina.evaluate(f"renderAt({i / FPS})")
            ff.stdin.write(pagina.screenshot(type="jpeg", quality=92))
            if i % 300 == 0:
                print(f"{i}/{n}", flush=True)
        pagina.evaluate(f"renderAt({T_CAPA})")
        pagina.screenshot(path=str(capa), type="jpeg", quality=92)
        navegador.close()
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg falhou ao gerar o mestre")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mestre), "-vf", "scale=960:540", "-c:v", "libx264",
                    "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
                    str(WEB / "historia.mp4")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(capa), "-vf", "scale=960:540", "-q:v", "4",
                    str(WEB / "historia.jpg")], check=True)
    print("pronto:", WEB / "historia.mp4")


if __name__ == "__main__":
    main()
