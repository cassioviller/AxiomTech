#!/usr/bin/env python3
"""Gera os clipes de fundo da história: um MP4 curto e mudo por capítulo, a partir de film.html?limpo (sem legenda,
HUD, capa nem cartão), mais o pôster WebP (= último quadro). A tabela CLIPES é a fonte da verdade do mapa
capítulo → cena → trecho (spec 2026-09-23-filme-fundo-design.md); check_historia.py e check_filme.py a importam.

Uso: python3 portfolio/filme/render_clipes.py            (os 11 clipes, ~10 min em CPU)
     python3 portfolio/filme/render_clipes.py --so zip   (um clipe só; não confere a soma)
Saídas: portfolio/filme/saida/clipes/cena-<passo>-1280.mp4  mestre 1280×720 (ignorado pelo git)
        portfolio/site/video/cena-<passo>.mp4              960×540, 24 fps, H.264 High 3.1, GOP 4, sem áudio
        portfolio/site/video/cena-<passo>.webp             pôster = último quadro do clipe publicado
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida" / "clipes"
WEB = AQUI.parent / "site" / "video"
FPS = 24
INICIO_PARADO, FIM_PARADO = 0.3, 0.5  # s: o clipe começa e termina parado (o dissolve entre capítulos é entre quadros parados)
TETO_CLIPE, TETO_SOMA, TETO_POSTER = int(0.9 * 1024 * 1024), 8 * 1024 * 1024, 60 * 1024
CRF, CRF_MAX = 28, 30
# passo: (índice em SC, t0, t1, duração em s); t é o tempo local 0..10 da cena (st.run(t)); um trecho contíguo por capítulo
CLIPES = {
    "origem": (0, 0.0, 10.0, 8),
    "obra": (1, 0.0, 10.0, 8),
    "veks": (6, 0.0, 4.7, 8),
    "ferramentas": (6, 4.7, 10.0, 8),
    "sige": (3, 0.0, 10.0, 8),
    "escala": (7, 0.0, 10.0, 8.5),
    "casa": (9, 0.0, 10.0, 10),
    "icamento": (10, 0.0, 10.0, 8),
    "whatsapp": (2, 0.0, 3.0, 8),
    "recuperado": (2, 3.0, 10.0, 8),
    "zip": (11, 0.0, 10.0, 10),
}
ARGS = ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist", "--allow-file-access-from-files"]


def tempo_local(passo, s):
    """Segundo s do clipe → t local da cena: parado nos primeiros 0,3 s e nos últimos 0,5 s, linear no meio."""
    _sc, t0, t1, dur = CLIPES[passo]
    f = min(1.0, max(0.0, (s - INICIO_PARADO) / (dur - INICIO_PARADO - FIM_PARADO)))
    return t0 + (t1 - t0) * f


def quadros(passo):
    return int(round(CLIPES[passo][3] * FPS))


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def psnr(a, b):
    """PSNR médio (dB) entre duas imagens ou dois vídeos do mesmo tamanho; inf se iguais."""
    saida = subprocess.run(["ffmpeg", "-i", str(a), "-i", str(b), "-lavfi", "psnr", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"average:(inf|[\d.]+)", saida)
    return float("inf") if not m or m.group(1) == "inf" else float(m.group(1))


def encode_web(mestre, destino, crf):
    ffmpeg("-i", str(mestre), "-vf", "scale=960:540", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-g", "4", "-keyint_min", "4", "-sc_threshold", "0", "-bf", "0", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-level", "3.1", "-movflags", "+faststart", "-an", str(destino))


def poster(mp4, passo, destino):
    """Pôster = último quadro do clipe publicado: WebP com PSNR ≥ 40 dB em relação a ele e ≤ 60 KB (q75, senão 82, 90)."""
    png = SAIDA / f"ultimo-{passo}.png"
    ffmpeg("-i", str(mp4), "-vf", f"select='eq(n,{quadros(passo) - 1})'", "-vframes", "1", "-update", "1", str(png))
    for q in (75, 82, 90):
        ffmpeg("-i", str(png), "-c:v", "libwebp", "-quality", str(q), str(destino))
        if psnr(destino, png) >= 40 and destino.stat().st_size <= TETO_POSTER:
            return
    sys.exit(f"{passo}: pôster sem PSNR ≥ 40 dB dentro de 60 KB")


def render(pagina, passo):
    """Quadro a quadro pelo Playwright: renderCena(i, t) → JPEG q92 → ffmpeg (mestre 1280×720, 24 fps, crf 18)."""
    sc = CLIPES[passo][0]
    mestre = SAIDA / f"cena-{passo}-1280.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-vcodec", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", str(mestre)], stdin=subprocess.PIPE)
    n = quadros(passo)
    for k in range(n):
        pagina.evaluate(f"renderCena({sc},{tempo_local(passo, k / FPS)!r})")
        ff.stdin.write(pagina.screenshot(type="jpeg", quality=92))
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit(f"{passo}: ffmpeg falhou no mestre")
    print(f"{passo}: {n} quadros", flush=True)
    return mestre


def publicar(passo, mestre):
    """Encode web dentro de 0,9 MB (crf 28, senão 29, 30) e pôster. Devolve o crf usado."""
    destino = WEB / f"cena-{passo}.mp4"
    for crf in range(CRF, CRF_MAX + 1):
        encode_web(mestre, destino, crf)
        if destino.stat().st_size <= TETO_CLIPE:
            break
    else:
        sys.exit(f"{passo}: acima de 0,9 MB mesmo com crf {CRF_MAX}")
    poster(destino, passo, WEB / f"cena-{passo}.webp")
    print(f"{passo}: {destino.stat().st_size / 1024:.0f} KB (crf {crf})", flush=True)
    return crf


def ajustar_soma(crfs):
    """Se os 11 clipes passarem de 8 MB, reencoda o maior com crf +1 (até 30) até caber."""
    while True:
        tamanhos = {p: (WEB / f"cena-{p}.mp4").stat().st_size for p in CLIPES}
        soma = sum(tamanhos.values())
        if soma <= TETO_SOMA:
            print(f"soma dos clipes: {soma / 1024 / 1024:.2f} MB", flush=True)
            return
        maior = max(tamanhos, key=tamanhos.get)
        if crfs[maior] >= CRF_MAX:
            sys.exit(f"soma dos clipes acima de 8 MB mesmo com crf {CRF_MAX} em {maior}")
        crfs[maior] += 1
        encode_web(SAIDA / f"cena-{maior}-1280.mp4", WEB / f"cena-{maior}.mp4", crfs[maior])
        poster(WEB / f"cena-{maior}.mp4", maior, WEB / f"cena-{maior}.webp")
        print(f"soma > 8 MB: {maior} reencodado com crf {crfs[maior]}", flush=True)


def main():
    from playwright.sync_api import sync_playwright
    passos = [sys.argv[sys.argv.index("--so") + 1]] if "--so" in sys.argv else list(CLIPES)
    SAIDA.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    crfs = {}
    with sync_playwright() as p:
        exe = shutil.which("chromium")  # no Replit o Chromium do Playwright não roda (faltam bibliotecas): usa o do sistema
        navegador = p.chromium.launch(executable_path=exe, args=ARGS) if exe else p.chromium.launch(args=ARGS)
        pagina = navegador.new_page(viewport={"width": 1280, "height": 720})
        pagina.goto((AQUI / "film.html").as_uri() + "?limpo")
        pagina.wait_for_timeout(2500)
        pagina.evaluate("PRONTO")  # texturas das cenas portadas (a planta real) carregadas
        for passo in passos:
            crfs[passo] = publicar(passo, render(pagina, passo))
        navegador.close()
    if "--so" not in sys.argv:
        ajustar_soma(crfs)
    print("pronto:", WEB)


if __name__ == "__main__":
    main()
