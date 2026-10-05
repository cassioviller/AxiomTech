#!/usr/bin/env python3
"""Checagens do filme (portfolio/filme/film.html), dos clipes de fundo (portfolio/site/video/cena-*) e do trailer de envio (portfolio/filme/saida/).

O texto do trailer segue as mesmas regras de honestidade da página: nenhum número que o
portfólio não sustente, nenhuma ressalva apagada, nada inventado com cara de dado, legendas
que dá para ler (≤ 200 palavras por minuto) e a mesma frase da contabilidade nos três lugares.
Uso: python3 portfolio/tests/check_filme.py [--cenas [passo ...]] [--video [passo ...]]
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
TRAILER = ROOT / "filme" / "saida" / "historia-960.mp4"
CAPA = ROOT / "filme" / "saida" / "historia-960.jpg"
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
     "6 áreas, da proposta ao financeiro; entregas de 22/07 a 14/09/2026. Portal e diário em uso nos galpões.", "", 8),
    ("jul → set/2026", "Diversas obras no sistema.",
     "Lê o desenho, mede e orça. Nos 19 serviços SINAPI conferidos, desvio máximo de 0,25%. Código com assistentes de IA.",
     "", 8.5),
    ("ago/2026", "O celeiro não cabe no caminhão.",
     "B-36: duas caixas, três viagens, 37 decisões registradas. No estudo, o módulo sobe pelo balancim, cabos na vertical.",
     "Projetei, orcei e fiz a proposta.", 8.5),
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
EXIGIDOS = ["Cássio Viller", "No estudo", "Projetei, orcei", "numa cópia", "a carga ainda não foi aplicada",
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


PORTADAS = {"casa": "// ================= CASA (portada da página: casa-viaja, 10 s) =================",
            "icamento": "// ================= IÇAMENTO (portado da página: icamento, 8 s) =================",
            "zip": "// ================= 36 MINUTOS (portado da página: 36min, 10 s) ================="}


def bloco_portado(filme, passo):
    ini = filme.find(PORTADAS[passo])
    if ini < 0:
        return ""
    fim = filme.find("// =================", ini + len(PORTADAS[passo]))
    return filme[ini:fim if fim > 0 else len(filme)]


def checar_portadas(filme, passos):
    """Estilo do filme nas cenas portadas: sem stage(), materiais por P() (exceto o filme translúcido e a textura da planta),
    um só acento ORANGE (+ a linha de cota no zip), nenhum texto pintado (F-18)."""
    for passo in passos:
        b = bloco_portado(filme, passo)
        check(b, f"film.html: falta o bloco {PORTADAS[passo]!r}")
        if not b:
            continue
        for proibido in ("stage(", "fillText", "SUBS", "LEG", "tex("):
            check(proibido not in b, f"cena portada {passo}: sem {proibido} (nenhum texto pintado, nada do maquetes.js)")
        for m in re.finditer(r"new THREE\.MeshStandardMaterial\(\{([^}]*)\}", b):
            check("transparent:true" in m.group(1) or "map:" in m.group(1),
                  f"cena portada {passo}: materiais por P(); só o filme translúcido e a textura da planta são MeshStandardMaterial")
        check(b.count("ORANGE") == (2 if passo == "zip" else 1), f"cena portada {passo}: exatamente 1 acento ORANGE (+ a linha de cota no zip)")
        check(re.search(r"0xE0622A", b, re.I) is None, f"cena portada {passo}: o laranja só entra como ORANGE")
        if passo == "icamento":
            comprimento = re.search(r"var L=([\d.]+),C=", b)
            check(comprimento is not None and float(comprimento.group(1)) <= 8,
                  "módulo do içamento com no máximo 8 m: acima disso o estudo pede pontos intermediários, e a maquete só tem 4 olhais")


LEITURAS = {  # expressão avaliada no film.html?limpo → valor esperado (F-18: as cenas portadas preservam o conteúdo)
    "casa": ("(function(){var st=SC[9],r=[];[.8,4.2,7.4].forEach(function(t){renderCena(9,t);var p=st.truck.position.clone().project(cam);"
             "r.push(Math.abs(p.x)<1&&Math.abs(p.y)<1&&Math.abs(st.truck.position.z)<.05);});renderCena(9,9.8);"
             "var q=st.roof.position.clone().project(cam);r.push(Math.abs(st.roof.position.y-3.67)<.05&&Math.abs(q.x)<1&&Math.abs(q.y)<1);return r;})()",
             [True, True, True, True]),
    "icamento": ("(function(){var st=SC[10];renderCena(10,5);var a=st.cabos.geometry.attributes.position.array,n=0;"
                 "for(var i=0;i<a.length;i+=6){if(Math.abs(a[i]-a[i+3])<1e-6&&Math.abs(a[i+2]-a[i+5])<1e-6&&Math.abs(a[i+1]-a[i+4])<10)n++;}"
                 "return [n,st.mod.position.y>3];})()", [4, True]),
    "zip": ("(function(){var st=SC[11],f=function(){return Math.round(((1-(((st.mm.rotation.z/(2*Math.PI))%1)+1)%1)%1)*60)%60;};"
            "renderCena(11,1.2);var a=f();renderCena(11,8);var b=f();return [a,b,!!st.walls&&st.walls.count>100];})()", [35, 11, True]),
}
ENQUADRAMENTOS = {  # no último quadro do trecho, o assunto inteiro dentro do quadro (F-13; prints de 24/09)
    # escala: as 12 miniaturas e o pé — os cantos da frente do terreno (slab 16 × 11: x = ±8, z = 5,5) com margem embaixo e dos lados
    "escala": ("(function(){renderCena(7,10);return SC[7].minis.every(function(m){var p=m.position.clone();p.y+=1.2;p.project(cam);"
               "return Math.abs(p.x)<.98&&p.y>-.94&&p.y<.98;})&&[-8,8].every(function(x){var p=new THREE.Vector3(x,0,5.5).project(cam);"
               "return Math.abs(p.x)<.98&&p.y>-.94;});})()", True),
    # icamento: a borda direita do cavalo (meia largura 1,2), não o centro, com folga para o recorte a 68 % da página
    "icamento": ("(function(){var st=SC[10];renderCena(10,10);var p=st.cavalo.position.clone();p.x+=1.2;p.project(cam);return p.x<.88&&Math.abs(p.y)<.95;})()", True),
}


def checar_cenas_portadas(passos):
    """Com o Chromium (SwiftShader) no film.html?limpo: a classe .limpo esconde a legenda; cada cena portada existe e responde a renderCena;
    nos passos de ENQUADRAMENTOS, o assunto cabe no último quadro (projeção pela câmera)."""
    import shutil
    from playwright.sync_api import sync_playwright
    from render_clipes import ARGS, PRONTO_COM_PRAZO
    erros = []
    with sync_playwright() as p:
        exe = shutil.which("chromium")
        nav = p.chromium.launch(executable_path=exe, args=ARGS) if exe else p.chromium.launch(args=ARGS)
        pg = nav.new_page(viewport={"width": 1280, "height": 720})
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.goto(FILME.as_uri() + "?limpo")
        pg.wait_for_timeout(2000)
        pg.evaluate(PRONTO_COM_PRAZO)
        check(pg.evaluate("document.documentElement.classList.contains('limpo')"), "?limpo não ligou a classe .limpo")
        check(pg.evaluate("getComputedStyle(document.getElementById('cap')).display") == "none", ".limpo não escondeu a legenda")
        for passo in passos:
            idx = CLIPES[passo][0]
            check(pg.evaluate(f"!!SC[{idx}]"), f"SC[{idx}] ({passo}) não existe")
            if pg.evaluate(f"!!SC[{idx}]") and passo in LEITURAS:
                exp, esperado = LEITURAS[passo]
                achado = pg.evaluate(exp)
                check(achado == esperado, f"cena portada {passo}: conteúdo {achado} ≠ {esperado}")
            if passo in ENQUADRAMENTOS:
                if pg.evaluate(f"!!SC[{idx}]"):
                    exp, esperado = ENQUADRAMENTOS[passo]
                    achado = pg.evaluate(exp)
                    check(achado == esperado, f"enquadramento {passo}: {achado} ≠ {esperado} (assunto fora do quadro no último quadro)")
                else:
                    check(False, f"SC[{idx}] ({passo}) não existe para o enquadramento")
        if set(PORTADAS) <= set(passos):  # o --cenas sem passos também leva o escala: a contagem continua valendo
            check(pg.evaluate("SC.length") == 12, "SC deve ter 12 cenas (9 do filme + 3 portadas)")
        nav.close()
    check(not erros, f"erros de JS no film.html?limpo: {erros}")


def checar_reproducao():
    """corrigir_filme.py aplicado ao film.html do zip reproduz o film.html commitado, byte a byte (F-02)."""
    if not ZIP.exists():
        print("filme-codigo-fonte.zip ausente (fora do git): reprodução pulada")
        return
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["unzip", "-q", "-o", str(ZIP), "-d", tmp], check=True)
        shutil.copy(ROOT / "filme" / "corrigir_filme.py", tmp)
        r = subprocess.run([sys.executable, str(Path(tmp) / "corrigir_filme.py")], capture_output=True, text=True)
        ultima = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "sem mensagem"
        check(r.returncode == 0, f"corrigir_filme.py falhou sobre o zip: {ultima}")
        if r.returncode == 0:
            check((Path(tmp) / "film.html").read_bytes() == FILME.read_bytes(),
                  "corrigir_filme.py não reproduz o film.html commitado a partir do zip (F-02)")


def ffprobe(caminho):
    saida = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height",
                            "-of", "json", str(caminho)], capture_output=True, text=True, check=True).stdout
    return json.loads(saida)


def checar_trailer():
    """Trailer de envio (WhatsApp/LinkedIn), fora do site: só se render.py já rodou. H.264 960×540, 85 s, ≤ 16 MB, moov antes."""
    if not TRAILER.exists():
        print("trailer de envio ausente (python3 portfolio/filme/render.py): pulado")
        return
    info = ffprobe(TRAILER)
    videos = [s for s in info["streams"] if s["codec_type"] == "video"]
    check(len(videos) == 1 and videos[0]["codec_name"] == "h264" and (videos[0]["width"], videos[0]["height"]) == (960, 540),
          f"trailer deve ser H.264 960×540 (achei {videos})")
    check(not [s for s in info["streams"] if s["codec_type"] == "audio"], "o trailer não tem áudio: sem faixa de som")
    total = sum(c[4] for c in CAPITULOS) + FIM
    check(abs(float(info["format"]["duration"]) - total) <= 0.5, f"duração {info['format']['duration']} s ≠ {total} s")
    check(int(info["format"]["size"]) <= 16 * 1024 * 1024, "trailer acima de 16 MB (o WhatsApp não manda como mídia)")
    dados = TRAILER.read_bytes()
    check(0 <= dados.find(b"moov") < dados.find(b"mdat"), "o índice (moov) precisa vir antes dos dados: -movflags +faststart")
    check(CAPA.exists() and tuple(ffprobe(CAPA)["streams"][0][k] for k in ("width", "height")) == (960, 540), "capa do trailer em 960×540")


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


def checar_readme():
    readme = (ROOT / "filme" / "README.md").read_text(encoding="utf-8")
    check("## Como enviar" in readme, "README do filme sem a seção \"Como enviar\"")
    for trecho in ("7º semestre", "CLT ou PJ", "85 s", "sem áudio", "16 MB"):
        check(trecho in readme, f"README do filme: \"Como enviar\" sem {trecho!r}")


def checar_render_clipes():
    """render_clipes.py espera as texturas (PRONTO) com prazo: sem ele, uma textura que nunca resolve trava o render em silêncio."""
    src = (ROOT / "filme" / "render_clipes.py").read_text(encoding="utf-8")
    check("Promise.race([PRONTO" in src and "20000" in src, "render_clipes.py: PRONTO precisa de prazo (Promise.race com 20000 ms)")


def checar_clipes(passos):
    check(set(passos) <= set(CLIPES), f"passos desconhecidos: {sorted(set(passos) - set(CLIPES))}")
    with tempfile.TemporaryDirectory() as tmp:
        soma = sum(checar_clipe(p, Path(tmp)) for p in passos if p in CLIPES)
    if set(passos) == set(CLIPES):
        check(soma <= 8 * 1024 * 1024, f"soma dos clipes {soma / 1024 / 1024:.2f} MB > 8 MB")
        publicados = sorted(subprocess.run(["git", "ls-files", "site/video"], cwd=ROOT, capture_output=True, text=True).stdout.split())
        esperados = sorted(f"site/video/cena-{p}.{e}" for p in CLIPES for e in ("mp4", "webp"))
        check(publicados == esperados, f"git ls-files site/video ≠ os 22 arquivos dos clipes: {publicados}")


def passos_de(opcao):
    """Os passos depois de --cenas/--video, até a próxima opção --: `--cenas --video zip` não dá zip ao --cenas."""
    resto = sys.argv[sys.argv.index(opcao) + 1:]
    fim = next((i for i, a in enumerate(resto) if a.startswith("--")), len(resto))
    return resto[:fim]


def main():
    check(FILME.exists(), "portfolio/filme/film.html não existe")
    if FILME.exists():
        filme = FILME.read_text(encoding="utf-8")
        checar_texto(filme, (SITE / "portfolio.html").read_text(encoding="utf-8"), (SITE / "index.html").read_text(encoding="utf-8"))
        checar_limpo(filme)
        checar_readme()
        checar_render_clipes()
        checar_portadas(filme, list(PORTADAS))  # estático e instantâneo: sempre
        if "--cenas" in sys.argv:  # conteúdo das cenas portadas no Chromium (~20 s)
            passos = passos_de("--cenas") or sorted(set(PORTADAS) | set(ENQUADRAMENTOS))
            conhecidos = set(PORTADAS) | set(ENQUADRAMENTOS)
            check(set(passos) <= conhecidos, f"--cenas: passos desconhecidos: {sorted(set(passos) - conhecidos)}")
            validos = [p for p in passos if p in PORTADAS or p in ENQUADRAMENTOS]
            if validos:  # só os passos conhecidos; um passo errado vira FALHOU, não KeyError
                checar_cenas_portadas(validos)
        checar_reproducao()
    if "--video" in sys.argv:
        checar_clipes(passos_de("--video") or list(CLIPES))
        checar_trailer()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
