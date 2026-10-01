#!/usr/bin/env python3
"""Renderiza as cenas do site v2 (portfolio/cenas/<arquivo>.html) em vídeo 1920×1080 e pôster.
Cada cena é um módulo que expõe window.renderCena(t) (t = tempo local 0..10) e window.PRONTO (texturas prontas).
As cenas importam módulos ES: file:// não serve, então portfolio/ é servido com Range numa porta local.

Uso: python3 portfolio/cenas/render.py --so sige
     python portfolio/cenas/render.py --gpu --qualidade alta --so modulares   (render local numa GPU; ver RENDER-LOCAL.md)
Saídas: portfolio/cenas/saida/<caso>-mestre.mp4  mestre 1920×1080 crf 16 (ignorado pelo git)
        portfolio/site/video/v2-<caso>.mp4       1920×1080, 24 fps, H.264 High 4.0, GOP 4, sem áudio
        portfolio/site/video/v2-<caso>.webp      pôster = último quadro
"""
import base64
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
ARGS_GPU = ["--ignore-gpu-blocklist", "--enable-gpu", "--enable-webgl", "--disable-gpu-watchdog"]  # Chromium com janela usa a placa (ANGLE/D3D11 no Windows)
GPU_NOME = """(function(){var gl=window.__palco.renderer.getContext(),e=gl.getExtension('WEBGL_debug_renderer_info');
return e?gl.getParameter(e.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER);})()"""
ARGS = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--enable-webgl", "--ignore-gpu-blocklist",
        "--disable-gpu-watchdog"]  # um quadro 3840×2160 com GTAO leva 15-60 s no SwiftShader: sem a flag o vigia mata a GPU (contexto perdido)
CONTEXTO_OK = "(function(){var gl=window.__palco.renderer.getContext();return !gl.isContextLost()&&gl.drawingBufferWidth>0;})()"
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
def navegador(gpu=False):
    """Chromium headless com SwiftShader (CPU, determinístico: o do Replit e dos testes) ou, com gpu=True, Chromium com
    janela na placa de vídeo do computador (o headless pode cair no SwiftShader mesmo com a placa presente)."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = shutil.which("chromium")  # no Replit o Chromium do Playwright não roda: usa o do sistema
        opcoes = {"args": ARGS_GPU, "headless": False} if gpu else {"args": ARGS}
        nav = p.chromium.launch(executable_path=exe, **opcoes) if exe else p.chromium.launch(**opcoes)
        try:
            yield nav
        finally:
            nav.close()


def abrir_cena(nav, url, tentativas=3):
    """Página 1920×1080 (escala 1) com a cena carregada e as texturas prontas; devolve (página, lista de erros de JS).
    Se o contexto WebGL se perder no aquecimento (SwiftShader sob carga), reabre a página, até `tentativas` vezes."""
    for tentativa in range(1, tentativas + 1):
        pg = nav.new_page(viewport={"width": LARGURA, "height": ALTURA}, device_scale_factor=1)
        pg.set_default_timeout(120000)  # no SwiftShader a carga da cena (PMREM, texturas) passa dos 30 s padrão sob carga
        erros = []
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
        pg.goto(url)
        pg.wait_for_function("typeof window.renderCena === 'function' && !!window.PRONTO", timeout=60000)
        pg.evaluate(PRONTO_COM_PRAZO)
        pg.evaluate("renderCena(0)")  # aquecimento: compila os shaders e sobe as texturas; o primeiro quadro nunca vai para o vídeo
        if pg.evaluate(CONTEXTO_OK):
            capturar(pg)
            return pg, erros
        pg.close()
        print(f"aviso: contexto WebGL perdido ao abrir {url} (tentativa {tentativa} de {tentativas}); reabrindo", file=sys.stderr, flush=True)
    sys.exit(f"{url}: contexto WebGL perdido {tentativas} vezes seguidas")


# PNG 1920×1080 lido do framebuffer do WebGL com gl.readPixels (espera o SwiftShader terminar) e reduzido F×F em JS
# (F = largura do buffer / 1920: 2 na qualidade normal, 4 na alta).
# Não usa pg.screenshot nem drawImage do canvas: os dois passam pelo compositor, e sob carga a primeira captura depois
# de carregar saía com o quadro velho (o canvas vazio), o que quebrava o determinismo e as pontas paradas.
CAPTURA = """(function(){var p=window.__palco,r=p.renderer,gl=r.getContext();r.setRenderTarget(null);
var W=gl.drawingBufferWidth,H=gl.drawingBufferHeight,F=W/1920;
if(F!==Math.round(F)||H!==1080*F)throw new Error('buffer '+W+'x'+H+' não é múltiplo inteiro de 1920x1080 (a GPU limitou o tamanho?)');
var buf=new Uint8Array(W*H*4);gl.readPixels(0,0,W,H,gl.RGBA,gl.UNSIGNED_BYTE,buf);
var w=W/F,h=H/F,n=F*F,m=n>>1,g=document.createElement('canvas');g.width=w;g.height=h;var x=g.getContext('2d'),img=x.createImageData(w,h),d=img.data;
for(var y=0;y<h;y++){var o=y*w*4;
  for(var i=0;i<w;i++){var r=m,gg=m,b=m;
    for(var dy=0;dy<F;dy++){var a=((H-1-(F*y+dy))*W+F*i)*4;
      for(var dx=0;dx<F;dx++,a+=4){r+=buf[a];gg+=buf[a+1];b+=buf[a+2];}}
    var q=o+4*i;d[q]=(r/n)|0;d[q+1]=(gg/n)|0;d[q+2]=(b/n)|0;d[q+3]=255;}}
x.putImageData(img,0,0);return g.toDataURL('image/png');})()"""


def capturar(pg):
    """Bytes do PNG 1920×1080 do quadro renderizado por último (renderCena)."""
    if not pg.evaluate(CONTEXTO_OK):
        raise RuntimeError("contexto WebGL perdido durante o render (SwiftShader); o quadro não pode ser capturado")
    return base64.b64decode(pg.evaluate(CAPTURA).split(",", 1)[1])


FPS = 24
INICIO_PARADO, FIM_PARADO = 0.3, 0.5  # s parados no começo e no fim do vídeo
TETO_CLIPE, TETO_POSTER = int(2.5 * 1024 * 1024), 150 * 1024
CRF, CRF_MAX = 26, 36  # a cena com grão (pasto, terra) e GOP 4 pede crf 34 para caber em 2,5 MB; em 36 o portal ainda é legível
CENAS = {  # caso: (arquivo em cenas/, duração do vídeo em s); t da cena vai sempre de 0 a 10
    "abertura": ("abertura.html", 8.0),
    "veks": ("caso-orcamento.html", 10.0),
    "sige": ("caso-sige.html", 10.0),
    "modulares": ("caso-modulares.html", 12.0),
}


def tempo_local(s, dur):
    """Segundo s do vídeo → t da cena (0..10): parado nos primeiros 0,3 s e nos últimos 0,5 s, linear no meio."""
    f = min(1.0, max(0.0, (s - INICIO_PARADO) / (dur - INICIO_PARADO - FIM_PARADO)))
    return 10.0 * f


def quadros(dur):
    return int(round(dur * FPS))


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def psnr(a, b):
    """PSNR médio (dB) entre duas imagens ou dois vídeos do mesmo tamanho; inf se iguais, 0.0 se o ffmpeg não mediu."""
    r = subprocess.run(["ffmpeg", "-i", str(a), "-i", str(b), "-lavfi", "psnr", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"average:(inf|[\d.]+)", r.stderr)
    if r.returncode != 0 or not m:
        return 0.0
    return float("inf") if m.group(1) == "inf" else float(m.group(1))


def renderizar(pg, dur, mestre):
    """Quadro a quadro: renderCena(t) → PNG 1920×1080 do canvas (capturar) → <mestre>-quadros/q0000.png… → ffmpeg (mestre crf 16).
    Os PNGs ficam em disco e um quadro já gravado não é refeito: se a sessão cair no meio (≈ 1 h por cena no Replit),
    rodar de novo retoma de onde parou. A pasta é apagada quando o mestre fica pronto."""
    pasta = mestre.with_name(f"{mestre.stem}-quadros")
    pasta.mkdir(parents=True, exist_ok=True)
    n = quadros(dur)
    feitos = 0
    for k in range(n):
        png = pasta / f"q{k:04d}.png"
        if png.exists() and png.stat().st_size > 0:
            feitos += 1
            continue
        pg.evaluate(f"renderCena({tempo_local(k / FPS, dur)!r})")
        parcial = png.with_suffix(".parcial")
        parcial.write_bytes(capturar(pg))
        parcial.replace(png)  # só aparece com o nome final depois de inteiro em disco
    if feitos:
        print(f"{mestre.name}: {feitos} quadros já estavam em {pasta.name}", flush=True)
    ffmpeg("-framerate", str(FPS), "-i", str(pasta / "q%04d.png"), "-frames:v", str(n),
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", str(mestre))
    shutil.rmtree(pasta)
    print(f"{mestre.name}: {n} quadros", flush=True)


def encode_web(mestre, destino, crf):
    ffmpeg("-i", str(mestre), "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-g", "4", "-keyint_min", "4",
           "-sc_threshold", "0", "-bf", "0", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
           "-movflags", "+faststart", "-an", str(destino))


def poster(mp4, dur, destino):
    """Pôster = último quadro do vídeo publicado: WebP com PSNR ≥ 40 dB e ≤ 150 KB (q75, senão 82, 90)."""
    png = destino.with_name(destino.stem + "-ultimo.png")
    png.unlink(missing_ok=True)
    ffmpeg("-i", str(mp4), "-vf", f"select='eq(n,{quadros(dur) - 1})'", "-vframes", "1", "-update", "1", str(png))
    if not png.exists():
        sys.exit(f"{mp4.name}: sem o quadro {quadros(dur) - 1} (o último) para o pôster")
    for q in (75, 82, 90):
        ffmpeg("-i", str(png), "-c:v", "libwebp", "-quality", str(q), str(destino))
        if psnr(destino, png) >= 40 and destino.stat().st_size <= TETO_POSTER:
            png.unlink()
            return
    sys.exit(f"{mp4.name}: pôster sem PSNR ≥ 40 dB dentro de 150 KB")


def publicar(caso, mestre, dur):
    """Encode web dentro de 2,5 MB (crf 26 → 32) e pôster. Devolve o crf usado."""
    WEB.mkdir(parents=True, exist_ok=True)
    destino = WEB / f"v2-{caso}.mp4"
    for crf in range(CRF, CRF_MAX + 1):
        encode_web(mestre, destino, crf)
        if destino.stat().st_size <= TETO_CLIPE:
            break
    else:
        sys.exit(f"{caso}: acima de 2,5 MB mesmo com crf {CRF_MAX}")
    poster(destino, dur, WEB / f"v2-{caso}.webp")
    print(f"{caso}: {destino.stat().st_size / 1024:.0f} KB (crf {crf})", flush=True)
    return crf


def main():
    i = sys.argv.index("--so") + 1 if "--so" in sys.argv else 0
    if i and (i >= len(sys.argv) or sys.argv[i] not in CENAS):
        sys.exit(f"--so pede um caso de CENAS: {', '.join(CENAS)}")
    casos = [sys.argv[i]] if i else list(CENAS)
    j = sys.argv.index("--qualidade") + 1 if "--qualidade" in sys.argv else 0
    qualidade = sys.argv[j] if j and j < len(sys.argv) else "normal"
    if qualidade not in ("normal", "alta"):
        sys.exit("--qualidade pede normal ou alta")
    gpu = "--gpu" in sys.argv
    sufixo = "" if qualidade == "normal" else f"-{qualidade}"  # quadros de qualidades diferentes nunca se misturam na retomada
    with servidor() as base, navegador(gpu) as nav:
        for caso in casos:
            arquivo, dur = CENAS[caso]
            pg, erros = abrir_cena(nav, f"{base}/cenas/{arquivo}?q={qualidade}")
            if erros:
                sys.exit(f"{caso}: erro de JavaScript ao carregar: {'; '.join(erros)}")
            placa = pg.evaluate(GPU_NOME)
            print(f"{caso}: qualidade {qualidade}, WebGL em {placa}", flush=True)
            if gpu and re.search(r"swiftshader|llvmpipe|software|basic render", placa, re.I):
                sys.exit(f"--gpu: o Chromium não usou a placa de vídeo ({placa}); atualizar o driver ou rodar sem --gpu")
            mestre = SAIDA / f"{caso}{sufixo}-mestre.mp4"
            renderizar(pg, dur, mestre)
            if erros:
                sys.exit(f"{caso}: erro de JavaScript no render: {'; '.join(erros)}")
            publicar(caso, mestre, dur)
            pg.close()
    print("pronto:", WEB)


if __name__ == "__main__":
    main()
