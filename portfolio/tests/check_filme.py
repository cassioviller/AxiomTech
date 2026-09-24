#!/usr/bin/env python3
"""Checagens do filme (portfolio/filme/film.html) e do vídeo gerado (portfolio/site/video/).

O texto do trailer segue as mesmas regras de honestidade da página: nenhum número que o
portfólio não sustente, nenhuma ressalva apagada, nada inventado com cara de dado, legendas
que dá para ler (≤ 200 palavras por minuto) e a mesma frase da contabilidade nos três lugares.
Uso: python3 portfolio/tests/check_filme.py
"""
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # portfolio/
FILME = ROOT / "filme" / "film.html"
SITE = ROOT / "site"
VIDEO = SITE / "video" / "historia.mp4"
CAPA = SITE / "video" / "historia.jpg"
FALHAS = []

sys.path.insert(0, str(ROOT / "filme"))
from render_clipes import CLIPES, FPS, psnr, quadros  # noqa: E402  (a tabela do mapa é a fonte da verdade)

VIDEO_DIR = SITE / "video"
ZIP = ROOT.parent / "filme-codigo-fonte.zip"

FRASE_CONTABILIDADE = "Comecei pela contabilidade, não pela obra."
# (kicker, frase ≤ 7 palavras, apoio, ressalva, duração do capítulo em segundos) — na ordem do filme
CAPITULOS = [
    ("Cássio Viller · portfólio", "Número sem origem custa caro na obra.",
     "Nove capítulos, de 2017 a 2026. Cada número tem origem: medido, derivado ou a confirmar.", "", 10.5),
    ("2017 → 2024", FRASE_CONTABILIDADE,
     "Escritório contábil da família desde 2017. Na UNIFEI, fiscal do DCE (2022) e diretor de vendas da InLoco Jr.", "", 8),
    ("fev/2025 → mar/2026", "Mas vi o dado digitado cinco vezes.",
     "Meio período, em paralelo: produção na V Alves (CLT) e estágio na Estruturas do Vale, onde nasceu o SIGE.", "", 8),
    ("mar → set/2026", "Na VEKS, toda conta repetida virou ferramenta.",
     "PJ, 6 meses, cumprido até o fim, com a V Alves até julho. Calculadora de parede e classificador de caixa.", "", 8),
    ("mai → set/2026", "O SIGE ganhou versão nova.",
     "Cerca de 50 módulos em 6 áreas; entregas de 22/07 a 14/09/2026. Portal e diário em uso nos galpões.", "", 8),
    ("jul → set/2026", "13 obras no sistema, 11 com proposta.",
     "Lê o desenho, mede e orça. Nos 19 serviços SINAPI conferidos, desvio máximo de 0,25%. Código com assistentes de IA.",
     "A gestão de obra deste sistema ainda não rodou em obra real.", 8.5),
    ("ago/2026", "O celeiro não cabe no caminhão.",
     "B-36: duas caixas, três viagens, 37 decisões registradas. No estudo, o módulo sobe pelo balancim, cabos na vertical.",
     "Pré-dimensionado, sujeito à revisão do engenheiro responsável.", 8.5),
    ("ago → set/2026", "23 dias de diário só no WhatsApp.",
     "Depois de 11/08, o diário saiu do sistema; 28 atividades prontas apareciam atrasadas nos dois galpões.",
     "Recuperação lida numa cópia; no sistema em uso, a carga ainda não foi aplicada.", 8.5),
    ("set/2026", "Proposta assinável em 36 minutos.",
     "Medidos: 11:35 → 12:11, ampliação de unidade de saúde, 26 ambientes, 328 m². À mão, cerca de 2 dias úteis (estimativa).", "", 9),
]
ORDEM = [5, 0, 1, 6, 3, 7, 8, 2, 4]  # cenas: abertura, escritório, duas construtoras, VEKS, SIGE, restaurante, celeiro, WhatsApp, 36 min
FIM = 8  # segundos do cartão final
# tabela da abertura: só quantidades que o portfólio sustenta, cada uma com a origem certa
TABELA = [["Área de projeção (UPA)", "328", "m²", "medido"], ["Ambientes", "26", "un", "medido"],
          ["Placa de gesso por m²", "2,11", "m²", "derivado"], ["Montante por m²", "2,91", "m", "derivado"],
          ["Aço da casa 8 × 6 m", "541", "kg", "derivado"], ["Pé-direito", "—", "m", "a confirmar"]]
PROIBIDOS = ["26 anos", "155.000", "150.500", "Cassio", "orçadas", "perdidos", "389,04", "422,04", "11.480", "9,90",
             "a obra digitava", "no centavo",
             # rodada 4: nada no quadro que o portfólio não sustente (o clipe não tem legenda para ressalvar)
             "OUTRO DADO", "barras de 3 m", "LICENCIADO", "COMPRAS", "756", "CONSTRUIR E DEMOLIR", "ESC 1:"]
EXIGIDOS = ["Cássio Viller", "No estudo", "Pré-dimensionado", "numa cópia", "a carga ainda não foi aplicada",
            "MESMO DADO", "PLANO DE CORTE", "EM USO", "DESENHO", "PLANTA"]
ANDARES = ["PROPOSTA", "OBRA", "CRONOGRAMA", "DIÁRIO", "MEDIÇÃO", "COBRANÇA", "CAIXA", "PORTAL DO CLIENTE"]  # = #sige .flow do portfólio
WPM_MAX = 200  # leitura confortável; o apoio fica visível em ~76% do capítulo


def check(cond, msg):
    if not cond:
        FALHAS.append(msg)


def limpo(fragmento):
    fragmento = re.sub(r"<(script|style)\b.*?</\1>", " ", fragmento, flags=re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragmento)).split())


def numeros(texto):
    return set(re.findall(r"\d+(?:[.,]\d+)*", texto))


def js_str(s):
    return s.replace("\\'", "'")


def capitulos_do_filme(filme):
    bloco = re.search(r"var CAPS=\[\n(.*?)\]\];", filme, re.S)
    if not bloco:
        return []
    caps = []
    for linha in (bloco.group(1) + "]").splitlines():
        m = re.match(r"^\s*\['((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)','((?:[^'\\]|\\.)*)',(.*),'((?:[^'\\]|\\.)*)'\],?$", linha)
        if m:
            caps.append((js_str(m.group(1)), js_str(m.group(2)), js_str(m.group(3)), js_str(m.group(5))))
    return caps


CODIGO = re.compile(r"#[0-9A-Fa-f]{3,8}\b|\dpx|monospace|sans-serif|rgba?\(")


def texto_do_filme(filme):
    """Tudo o que pode aparecer na tela: HTML visível + todo texto literal do script (legendas, tabela,
    post-its, placas, calendário), menos cores e fontes."""
    script = "\n".join(re.findall(r"<script>(.*?)</script>", filme, re.S))
    literais = [js_str(x) for x in re.findall(r"'((?:[^'\\]|\\.)*)'", script) if not CODIGO.search(x)]
    corpo = filme[filme.index("<body"):]
    return limpo(corpo) + " " + " ".join(literais)


def checar_texto(filme, portfolio, historia):
    caps = capitulos_do_filme(filme)
    check([c[:4] for c in CAPITULOS] == caps, f"legendas do filme diferentes do roteiro corrigido: {caps[:2]}…")
    ordem = re.search(r"var ORDER=\[([\d,]+)\], DUR=\[([\d.,]+)\], ENDD=(\d+);", filme)
    check(ordem is not None, "falta a linha ORDER/DUR/ENDD")
    if ordem:
        check([int(x) for x in ordem.group(1).split(",")] == ORDEM, f"ordem das cenas deve ser {ORDEM} (cronológica)")
        check([float(x) for x in ordem.group(2).split(",")] == [c[4] for c in CAPITULOS], "durações dos capítulos diferentes do roteiro")
        check(int(ordem.group(3)) == FIM, f"cartão final com {FIM} s")
    for kicker, frase, apoio, _ressalva, dur in CAPITULOS:
        check(len(frase.split()) <= 7, f"frase com mais de 7 palavras: {frase!r}")
        wpm = len(apoio.split()) / (0.76 * dur) * 60
        check(wpm <= WPM_MAX, f"apoio rápido demais para ler ({wpm:.0f} palavras/min): {apoio[:40]!r}…")
    rows = re.search(r"var rows=(\[.*?\]\]);", filme, re.S)
    check(rows is not None and json.loads(rows.group(1).replace("'", '"')) == TABELA, "tabela da abertura diferente da tabela sustentada pelo portfólio")
    t = texto_do_filme(filme)
    for p in PROIBIDOS:
        check(p not in t, f"texto proibido no filme: {p!r}")
    for e in EXIGIDOS:
        check(e in t, f"texto obrigatório ausente no filme: {e!r}")
    extras = numeros(t) - numeros(limpo(portfolio[portfolio.index("<body"):]))
    check(not extras, f"números no filme que o portfólio não sustenta: {sorted(extras)}")
    for nome, pagina in (("index.html", historia), ("portfolio.html", portfolio)):
        check(FRASE_CONTABILIDADE.rstrip(".") in limpo(pagina), f"{nome} sem a frase da contabilidade")
        check("centavo, não na parede" not in pagina, f"{nome} ainda usa a frase do centavo")
    # SIGE: 8 andares com os nomes do fluxo do portfólio, sem numerais; placa "EM USO"
    flow = re.search(r'<div class="flow"[^>]*>(.*?)</div>', portfolio[portfolio.index('id="sige"'):], re.S)
    check(flow is not None and [limpo(s).upper() for s in re.findall(r"<span[^>]*>(.*?)</span>", flow.group(1))] == ANDARES,
          "os andares do SIGE no filme têm de ser os <span> de #sige .flow do portfólio")
    names = re.search(r"var names=\[([^\]]*)\];", filme)
    check(names is not None and [js_str(x) for x in re.findall(r"'((?:[^'\\]|\\.)*)'", names.group(1))] == ANDARES,
          f"var names do SIGE ≠ {ANDARES}")
    sige = filme[filme.index("CENA 4 · prédio SIGE"):filme.index("CENA 6 · 36 minutos")]
    check("padStart" not in sige, "SIGE: sem numeral nos andares (7 numerados leem-se como 7 áreas; o site diz 6)")
    check("st.cam=[[0,[7,1.6,10],[0,1.4,0]],[7.5,[7,9.8,10],[0,8.8,0]],[10,[12.5,10,17.5],[0,5.4,0]]];" in sige,
          "SIGE: chaves de câmera do 8º andar")
    check("if(r*7+k<31)" in filme, "escritório: calendário com até 31 dias")
    rua = filme[filme.index("CENA 2 · duas construtoras"):filme.index("CENA 3 · WhatsApp")]
    check("c.fillText('MESMO DADO',20,120);" in rua and "moveTo(16,106)" not in rua, "rua: os 5 cartões dizem MESMO DADO, sem risco")
    check("m.rotation.z=i==4?Math.sin(t*9)*.08*cl(t-7.2):0" in rua, "rua: o 5º cartão continua tremendo")


def checar_limpo(filme):
    """film.html?limpo: nenhum DOM por cima do canvas; renderCena(i, t) puro; o trailer (ORDER, renderAt) intacto."""
    check(".limpo #cap,.limpo #hud,.limpo #num,.limpo #cover,.limpo #end,.limpo .tag,.limpo .bar,.limpo .scrim,.limpo #prog,"
          ".limpo #wipe,.limpo #fade,.limpo .vig{display:none!important}" in filme, "film.html: falta a regra .limpo")
    check("if(/[?&]limpo\\b/.test(location.search))document.documentElement.classList.add('limpo');" in filme,
          "film.html: a flag ?limpo liga a classe no <html>")
    check("window.renderCena=function(i,t){" in filme, "film.html: falta window.renderCena(i, t)")
    check("var PRONTOS=[];" in filme and "window.PRONTO=Promise.all(PRONTOS);" in filme, "film.html: falta PRONTOS/PRONTO")
    check("DURSC[9]=10;DURSC[10]=8;DURSC[11]=10;" in filme, "film.html: durações das cenas portadas (casa 10 s, içamento 8 s, zip 10 s)")
    check("cam.setViewOffset(1280,720,-230,-20,1280,720)" in filme, "film.html: o viewOffset da composição fica")
    check("var ORDER=[5,0,1,6,3,7,8,2,4]" in filme and "window.renderAt=function(T)" in filme, "film.html: o trailer não muda")


def checar_reproducao():
    """corrigir_filme.py aplicado ao film.html do zip reproduz o film.html commitado, byte a byte (F-02)."""
    if not ZIP.exists():
        print("filme-codigo-fonte.zip ausente (fora do git): reprodução pulada")
        return
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["unzip", "-q", "-o", str(ZIP), "-d", tmp], check=True)
        shutil.copy(ROOT / "filme" / "corrigir_filme.py", tmp)
        subprocess.run([sys.executable, str(Path(tmp) / "corrigir_filme.py")], check=True, capture_output=True)
        check((Path(tmp) / "film.html").read_bytes() == FILME.read_bytes(),
              "corrigir_filme.py não reproduz o film.html commitado a partir do zip (F-02)")


def ffprobe(caminho):
    saida = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height",
                            "-of", "json", str(caminho)], capture_output=True, text=True, check=True).stdout
    return json.loads(saida)


def checar_video():
    """Só roda depois do render (Task 3): vídeo leve, sem áudio, com a duração do filme, e capa."""
    check(VIDEO.exists(), "falta portfolio/site/video/historia.mp4 (rode python3 portfolio/filme/render.py)")
    check(CAPA.exists(), "falta portfolio/site/video/historia.jpg (capa do vídeo)")
    if not VIDEO.exists():
        return
    info = ffprobe(VIDEO)
    videos = [s for s in info["streams"] if s["codec_type"] == "video"]
    check(len(videos) == 1 and videos[0]["codec_name"] == "h264" and (videos[0]["width"], videos[0]["height"]) == (960, 540),
          f"vídeo deve ser H.264 960×540 (achei {videos})")
    check(not [s for s in info["streams"] if s["codec_type"] == "audio"], "o filme não tem áudio: sem faixa de som")
    total = sum(c[4] for c in CAPITULOS) + FIM
    check(abs(float(info["format"]["duration"]) - total) <= 0.5, f"duração {info['format']['duration']} s ≠ {total} s")
    check(int(info["format"]["size"]) <= 12 * 1024 * 1024, "vídeo acima de 12 MB")
    dados = VIDEO.read_bytes()
    check(0 <= dados.find(b"moov") < dados.find(b"mdat"), "o índice (moov) precisa vir antes dos dados: -movflags +faststart")
    if CAPA.exists():
        capa = ffprobe(CAPA)["streams"][0]
        check((capa["width"], capa["height"]) == (960, 540), "capa do vídeo em 960×540")


def ffprobe_json(caminho, entradas):
    return json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", entradas, "-of", "json", str(caminho)],
                                     capture_output=True, text=True, check=True).stdout)


def quadros_chave(mp4):
    saida = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-skip_frame", "nokey", "-show_entries", "frame=pts_time",
                            "-of", "csv=p=0", str(mp4)], capture_output=True, text=True, check=True).stdout
    return [float(x.strip(", ")) for x in saida.split() if x.strip(", ")]


def tipos_de_quadro(mp4):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "frame=pict_type", "-of", "csv=p=0", str(mp4)],
                          capture_output=True, text=True, check=True).stdout.replace(",", "").split()


def luma(arquivo):
    """(YAVG, YDIF) por quadro, pelo filtro signalstats (serve para MP4 e para o pôster WebP, que tem 1 quadro)."""
    saida = subprocess.run(["ffprobe", "-v", "error", "-f", "lavfi", "-i", f"movie={arquivo},signalstats", "-show_entries",
                            "frame_tags=lavfi.signalstats.YAVG,lavfi.signalstats.YDIF", "-of", "csv=p=0"],
                           capture_output=True, text=True, check=True).stdout
    return [tuple(float(x) for x in l.strip(",").split(",")) for l in saida.splitlines() if l.strip(",")]


def quadro(mp4, n, destino):
    destino.unlink(missing_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", f"select='eq(n,{n})'", "-vframes", "1", "-update", "1",
                    str(destino)], check=True)
    check(destino.exists(), f"{mp4.name}: não tem o quadro {n}")


def checar_clipe(passo, tmp):
    """Um clipe publicado: H.264 High ≤ 3.1, 960×540, 24 fps, sem áudio, moov antes, GOP ≤ 4, sem B-frames, ≤ 0,9 MB,
    plano contínuo parado nas pontas, pôster = último quadro. Devolve o tamanho em bytes (0 se faltar)."""
    _sc, _t0, _t1, dur = CLIPES[passo]
    mp4, webp = VIDEO_DIR / f"cena-{passo}.mp4", VIDEO_DIR / f"cena-{passo}.webp"
    check(mp4.exists() and webp.exists(), f"falta {mp4.name} ou {webp.name} (rode python3 portfolio/filme/render_clipes.py --so {passo})")
    if not (mp4.exists() and webp.exists()):
        return 0
    info = ffprobe_json(mp4, "format=duration,size:stream=codec_type,codec_name,profile,level,width,height,pix_fmt,r_frame_rate")
    v = [s for s in info["streams"] if s["codec_type"] == "video"]
    check(len(v) == 1 and v[0]["codec_name"] == "h264" and v[0]["profile"] == "High" and int(v[0]["level"]) <= 31, f"{passo}: H.264 High ≤ 3.1 ({v})")
    check(v and (v[0]["width"], v[0]["height"], v[0]["pix_fmt"], v[0]["r_frame_rate"]) == (960, 540, "yuv420p", "24/1"), f"{passo}: 960×540 yuv420p 24 fps")
    check(not [s for s in info["streams"] if s["codec_type"] == "audio"], f"{passo}: sem faixa de áudio")
    check(abs(float(info["format"]["duration"]) - dur) <= 1 / FPS + 1e-3, f"{passo}: duração {info['format']['duration']} s ≠ {dur} s")
    dados = mp4.read_bytes()
    check(0 <= dados.find(b"moov") < dados.find(b"mdat"), f"{passo}: moov antes de mdat (+faststart)")
    tamanho = int(info["format"]["size"])
    check(tamanho <= 0.9 * 1024 * 1024, f"{passo}: {tamanho / 1024:.0f} KB > 0,9 MB")
    kf = quadros_chave(mp4)
    check(bool(kf) and max(b - a for a, b in zip(kf, kf[1:] + [float(info["format"]["duration"])])) <= 4 / FPS + 1e-3,
          f"{passo}: quadro-chave a cada ≤ 4 quadros (até o fim do clipe)")
    check("B" not in tipos_de_quadro(mp4), f"{passo}: sem B-frames")
    y = luma(mp4)
    check(all(40 <= a <= 235 for a, _ in y), f"{passo}: luma média fora de 40..235 em algum quadro")
    check(all(abs(b[0] - a[0]) <= 20 for a, b in zip(y, y[1:])), f"{passo}: salto de luma > 20 entre quadros consecutivos")
    for i in range(0, len(y), FPS):
        check(sum(1 for _, d in y[i:i + FPS] if d >= 25.5) <= 3, f"{passo}: mais de 3 mudanças ≥ 10 % no segundo {i // FPS}")
    n = quadros(passo)
    for a, b in ((0, int(round(0.3 * FPS))), (n - int(round(0.5 * FPS)), n - 1)):
        fa, fb = tmp / f"{passo}-{a}.png", tmp / f"{passo}-{b}.png"
        quadro(mp4, a, fa)
        quadro(mp4, b, fb)
        check(psnr(fa, fb) >= 35, f"{passo}: os quadros {a} e {b} deveriam ser iguais (o clipe começa e termina parado)")
    p = ffprobe_json(webp, "stream=width,height")["streams"][0]
    check((p["width"], p["height"]) == (960, 540) and webp.stat().st_size <= 60 * 1024, f"{passo}: pôster 960×540 ≤ 60 KB")
    check(psnr(webp, tmp / f"{passo}-{n - 1}.png") >= 40, f"{passo}: pôster ≠ último quadro do clipe (PSNR < 40 dB)")
    yp = luma(webp)
    check(yp and 40 <= yp[0][0] <= 235, f"{passo}: pôster em branco ou preto")
    return tamanho


def checar_clipes(passos):
    check(set(passos) <= set(CLIPES), f"passos desconhecidos: {sorted(set(passos) - set(CLIPES))}")
    with tempfile.TemporaryDirectory() as tmp:
        soma = sum(checar_clipe(p, Path(tmp)) for p in passos if p in CLIPES)
    if set(passos) == set(CLIPES):
        check(soma <= 8 * 1024 * 1024, f"soma dos clipes {soma / 1024 / 1024:.2f} MB > 8 MB")


def main():
    check(FILME.exists(), "portfolio/filme/film.html não existe")
    if FILME.exists():
        filme = FILME.read_text(encoding="utf-8")
        checar_texto(filme, (SITE / "portfolio.html").read_text(encoding="utf-8"), (SITE / "index.html").read_text(encoding="utf-8"))
        checar_limpo(filme)
        checar_reproducao()
    if "--video" in sys.argv:
        passos = [a for a in sys.argv[sys.argv.index("--video") + 1:] if not a.startswith("--")]
        checar_clipes(passos or list(CLIPES))
        checar_video()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
