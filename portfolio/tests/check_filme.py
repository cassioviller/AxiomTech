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
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # portfolio/
FILME = ROOT / "filme" / "film.html"
SITE = ROOT / "site"
VIDEO = SITE / "video" / "historia.mp4"
CAPA = SITE / "video" / "historia.jpg"
FALHAS = []

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
             "a obra digitava", "no centavo"]
EXIGIDOS = ["Cássio Viller", "No estudo", "Pré-dimensionado", "numa cópia", "a carga ainda não foi aplicada"]
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


def main():
    check(FILME.exists(), "portfolio/filme/film.html não existe")
    if FILME.exists():
        checar_texto(FILME.read_text(encoding="utf-8"), (SITE / "portfolio.html").read_text(encoding="utf-8"),
                     (SITE / "index.html").read_text(encoding="utf-8"))
    if "--video" in sys.argv:
        checar_video()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
