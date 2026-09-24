#!/usr/bin/env python3
"""Checagens da página principal, site/index.html (a história na linha do tempo).

Estático: roteiro exato dos 17 capítulos, datas e ordem cronológica, ressalvas,
números (só os que o portfólio, site/portfolio.html, já sustenta), links para o
caso completo, marcação acessível e CSS. Com --navegador: o Chromium headless
abre tests/historia_teste.html em tempo real e confere a troca de cenas; depois,
com os clipes de verdade e o servidor com Range, a carga sob demanda, o seek pela
rolagem, o 404, movimento reduzido ligado no meio, economia de dados, foco,
composição e desempenho.
Uso: python3 portfolio/tests/check_historia.py [--navegador] [--origem URL] [--gravar-baseline]
"""
import base64
import contextlib
import html
import json
import os
import re
import socket
import struct
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]  # portfolio/
sys.path.insert(0, str(ROOT / "filme"))
from render_clipes import CLIPES  # noqa: E402  (mapa capítulo → cena → trecho: a fonte da verdade)

LONGAS = {"casa", "icamento", "zip"}  # capítulos de 200 svh (10 s, 8 s e 10 s de clipe, mas com mais a dizer)
FOCO = {"obra": "alto", "casa": "alto", "whatsapp": "alto", "icamento": "alto"}  # assunto encostado no alto / no pé do quadro 16:9
SITE = ROOT / "site"
PAGINA = SITE / "index.html"
PORTFOLIO = SITE / "portfolio.html"
FALHAS = []


def cap(passo, tag, data, frase, ressalva, fundo, caso):
    """data: None ou (texto visível, [datetime, ...]); fundo: None, ("img", arquivo, largura, altura),
    ("ano", texto) ou ("clipe", duração em s); caso: None ou (âncora, texto do link)."""
    return {"passo": passo, "tag": tag, "data": data, "frase": frase, "ressalva": ressalva, "fundo": fundo, "caso": caso}


ROTEIRO = [
    cap("tese", "h1", None,
        "Um número sem origem custa caro na obra.",
        "Cássio Viller, estudante de Engenharia Civil (7º semestre), mira orçamento, planejamento e custos.",
        ("img", "o-quantitativos.webp", 1040, 1000), None),
    cap("origem", "h2", ("2017 → 2024", ["2017", "2024"]),
        "Comecei pela contabilidade, não pela obra.",
        "Escritório contábil da família desde 2017; na UNIFEI, fiscal do DCE em 2022 e diretor de vendas da InLoco Jr. de 2023 a 2024.",
        ("clipe", 8), ("curriculo", "Ver no currículo: contabilidade e UNIFEI →")),
    cap("mudanca", "h2", ("2025", ["2025"]),
        "Em 2025, mudei de cidade e de curso.",
        "Cruzeiro do Sul (EAD), morando em São José dos Campos: hoje no 7º semestre, faltam 3. Sistemas de Informação na PUC, em paralelo.",
        ("ano", "2025"), ("curriculo", "Ver no currículo: formação →")),
    cap("obra", "h2", ("fev/2025 → mar/2026", ["2025-02", "2026-03"]),
        "Mas na obra, vi a mesma informação digitada cinco vezes.",
        "V Alves (gerente de produção, CLT meio período) e Estruturas do Vale (estágio, meio período), em paralelo. No estágio nasceu o SIGE.",
        ("clipe", 8), ("curriculo", "Ver no currículo: V Alves e Estruturas do Vale →")),
    cap("veks", "h2", ("mar/2026 → set/2026", ["2026-03", "2026-09"]),
        "Em março de 2026, entrei na VEKS Engenharia.",
        "PJ, contrato de 6 meses cumprido até o fim; a V Alves, em meio período, seguiu até julho.",
        ("clipe", 8), ("obra", "Ver o caso completo: obras na VEKS →")),
    cap("ferramentas", "h2", ("mar → abr/2026", ["2026-03", "2026-04"]),
        "Toda conta repetida virou ferramenta.",
        "Nos primeiros meses na VEKS: a calculadora de parede em LSF e drywall e o classificador do fluxo de caixa.",
        ("clipe", 8), ("ferramentas", "Ver as ferramentas: calculadora e classificador →")),
    cap("sige", "h2", ("mai → set/2026", ["2026-05", "2026-09"]),
        "De maio a setembro, o SIGE ganhou versão nova.",
        "Cerca de 50 módulos em 6 áreas, entregas registradas de 22/07 a 14/09/2026; código escrito com assistente de IA, sob a minha direção.",
        ("clipe", 8), ("sige", "Ver o caso completo: SIGE →")),
    cap("galpoes", "h2", ("jun/2026", ["2026-06-08"]),
        "Em junho, começou a obra que testaria o SIGE.",
        "Dois galpões e 22 baias numa fazenda, em Light Steel Frame: a obra real do portal do cliente e do diário.",
        ("ano", "22 baias"), ("obra", "Ver o caso completo: galpões e baias →")),
    cap("escala", "h2", ("jul → set/2026", ["2026-07-09", "2026-09-21"]),
        "13 obras no sistema, até R$ 24,5 milhões.",
        "11 com proposta; a menor, R$ 29 mil. A gestão de obra deste sistema ainda não rodou numa obra real.",
        ("clipe", 8.5), ("sistema", "Ver o caso completo: sistema de orçamento →")),
    cap("precisao", "h2", ("jul → set/2026", ["2026-07-09", "2026-09-21"]),
        "Desvio máximo de 0,25% nos 19 serviços conferidos.",
        "Serviço a serviço, contra a tabela SINAPI da Caixa; acima de 1% de desvio, a importação é recusada.",
        ("img", "o-orcamento.webp", 1040, 1080), ("sistema", "Ver o caso completo: conferência SINAPI →")),
    cap("casa", "h2", ("ago/2026", ["2026-08"]),
        "O celeiro não cabe inteiro no caminhão.",
        "B-36, pré-dimensionado e sujeito à revisão do engenheiro responsável: duas caixas, três viagens, 37 decisões registradas.",
        ("clipe", 10), ("modular", "Ver o caso completo: celeiro B-36 →")),
    cap("icamento", "h2", ("ago/2026", ["2026-08"]),
        "No estudo, o módulo sobe pelo balancim, cabos na vertical.",
        "Estudo 3D de agosto: com os cabos na vertical, a parede não é comprimida. Balancim de içamento e guindaste da classe certa viraram itens de regra no orçamento.",
        ("clipe", 8), ("modular", "Ver o caso completo: casas modulares →")),
    cap("whatsapp", "h2", ("ago/2026", ["2026-08-11"]),
        "Depois de 11/08, o diário saiu do sistema.",
        "42 diários lançados até ali; os 23 dias seguintes ficaram só no grupo de WhatsApp, e 28 atividades prontas apareciam como atrasadas.",
        ("clipe", 8), ("sige", "Ver o caso completo: o diário no WhatsApp →")),
    cap("recuperado", "h2", ("set/2026", ["2026-09"]),
        "Recuperado, o diário mostrou 44,7% de avanço.",
        "Antes, 27,6%; planejado para 07/09, 60,8%. Lido numa cópia do sistema; no sistema em uso, a carga ainda não foi aplicada.",
        ("clipe", 8), ("sige", "Ver o caso completo: diários recuperados →")),
    cap("zip", "h2", ("set/2026", ["2026-09"]),
        "Em setembro, uma proposta assinável em 36 minutos.",
        "Medidos: 11:35 → 12:11, numa ampliação de unidade de saúde com 26 ambientes e 328 m². À mão, cerca de 2 dias úteis (estimativa).",
        ("clipe", 10), ("orcamento", "Ver o caso completo: 36 minutos →")),
    cap("metodo", "h2", None,
        "Construí o jeito de o número não sumir.",
        "De 2017 a 2026: contabilidade, obra e sistemas. Idealizei e dirigi; o código foi escrito com assistentes de IA, e as regras e a revisão são minhas.",
        ("img", "o-proposta.webp", 885, 1060), None),
    cap("convite", "h2", None,
        "Faltam 3 semestres para o diploma. Não falta obra feita.",
        "Você me manda o pacote do projeto; eu devolvo levantamento, orçamento com faixa e proposta no seu modelo.",
        None, None),
]

RESSALVAS = ["estimativa", "ainda não rodou", "nos 19 serviços conferidos", "cópia do sistema", "assistentes de IA",
             "em paralelo", "pré-dimensionado", "sujeito à revisão do engenheiro responsável",
             "no sistema em uso, a carga ainda não foi aplicada"]
PROIBIDOS = ["3,40"]
PALAVRAS_CHAVE = ["quantitativos", "SINAPI", "BDI", "cronograma físico-financeiro", "curva S", "medição", "cotação"]
WHATSAPP = "https://wa.me/5512982071116"
CURRICULO = "curriculo-cassio-viller.pdf"


def check(cond, msg):
    if not cond:
        FALHAS.append(msg)


def limpo(fragmento):
    """Texto visível de um trecho de HTML, com entidades resolvidas e espaços normalizados."""
    fragmento = re.sub(r"<(script|style)\b.*?</\1>", " ", fragmento, flags=re.S)
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragmento)).split())


def corpo(pagina):
    return pagina[pagina.index("<body"):pagina.index("</body>")]


def numeros(texto):
    return set(re.findall(r"\d+(?:[.,]\d+)*", texto))


MESES = "jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez"
# Datas que o Cássio confirmou na conversa de 23/09/2026 (linha do tempo) e que o portfólio não traz por extenso.
# Registros do SIGE (22/07 a 14/09/2026), início da obra dos galpões (jun/2026) e arquivos das casas modulares (ago/2026).
DATAS_CONFIRMADAS = {"22/07", "14/09/2026", "abr/2026", "jun/2026", "ago/2026"}


def datas(texto):
    """Datas inteiras do texto (dd/mm, dd/mm/aaaa, mmm/aaaa), em minúsculas — nunca pedaços como '22' e '07'."""
    return set(re.findall(r"\b\d{1,2}/\d{2}(?:/\d{4})?\b", texto)) | set(re.findall(rf"\b(?:{MESES})/\d{{4}}\b", texto.lower()))


def atributos(tag):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))


def cenas(pagina):
    """(classes, id, passo, html interno) de cada <section class="cena…">."""
    return re.findall(r'<section class="(cena(?: longa)?)" id="([a-z0-9]+)" data-passo="([a-z0-9]+)">(.*?)</section>', pagina, flags=re.S)


def data_iso(dt):
    """'2025' → '2025-01-01'; '2026-08' → '2026-08-01' (para comparar datas de precisões diferentes)."""
    partes = dt.split("-")
    return "-".join(partes + ["01"] * (3 - len(partes)))


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def contraste(a, b):
    la, lb = (0.2126 * _lin(x[0]) + 0.7152 * _lin(x[1]) + 0.0722 * _lin(x[2]) for x in (a, b))
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def checar_fundo(passo, i, fundo, miolo):
    figs = re.findall(r"<figure ([^>]*)>(.*?)</figure>", miolo, re.S)
    if fundo is None:
        check(not figs, f"cena {passo}: não deveria ter figura de fundo")
        return
    check(len(figs) == 1, f"cena {passo}: esperava 1 figura de fundo, achei {len(figs)}")
    if not figs:
        return
    fa, fmiolo = atributos(figs[0][0]), figs[0][1]
    tipo = fundo[0]
    classe = {"img": "fundo", "ano": "fundo tipo", "clipe": "fundo clipe"}[tipo]
    if tipo == "clipe" and passo in FOCO:
        classe += " foco-" + FOCO[passo]
    check(fa.get("class") == classe, f"cena {passo}: classe da figura {fa.get('class')!r}, esperava {classe!r}")
    check(fa.get("aria-hidden") == "true", f"cena {passo}: figura de fundo sem aria-hidden=\"true\"")
    check(fa.get("data-passo") == passo, f"cena {passo}: figura com data-passo {fa.get('data-passo')!r}")
    check("data-cena" not in fa, f"cena {passo}: data-cena {fa.get('data-cena')!r} não entra mais na figura")
    check(not re.search(r"<(a|button|input|select|textarea)\b", fmiolo), f"cena {passo}: nada focável dentro da figura aria-hidden")
    if tipo == "ano":
        check(f'<span class="ano">{fundo[1]}</span>' in fmiolo and "<img" not in fmiolo,
              f"cena {passo}: fundo tipográfico deve ser só <span class=\"ano\">{fundo[1]}</span>")
        return
    check(limpo(fmiolo) == "", f"cena {passo}: nenhum nó de texto dentro da figura (só o .ano dos fundos tipográficos)")
    if tipo == "img":
        arquivo, largura, altura, src = fundo[1], fundo[2], fundo[3], f"img/{fundo[1]}"
    else:
        dur = fundo[1]
        arquivo, largura, altura, src = f"cena-{passo}.webp", 960, 540, f"video/cena-{passo}.webp"
        check(fa.get("data-dur") == f"{dur:g}" and fa.get("data-clipe") == f"video/cena-{passo}.mp4",
              f"cena {passo}: figure de clipe com data-dur=\"{dur:g}\" e data-clipe=\"video/cena-{passo}.mp4\"")
        check(CLIPES.get(passo, (0, 0, 0, None))[3] == dur, f"cena {passo}: duração {dur} ≠ CLIPES de render_clipes.py")
        v = re.search(r"<video ([^>]*)></video>", fmiolo)
        check(v is not None and v.group(1) == 'muted playsinline preload="none" disableremoteplayback width="960" height="540"',
              f"cena {passo}: <video muted playsinline preload=\"none\" disableremoteplayback width=\"960\" height=\"540\"></video>, nada mais")
        for proibido in ("<canvas", "<source", "<track", 'class="hud"', "data-relogio", "data-legenda", "title=", "tabindex"):
            check(proibido not in fmiolo, f"cena {passo}: {proibido} não entra na figura de clipe")
        mp4 = SITE / "video" / f"cena-{passo}.mp4"
        if mp4.exists():
            real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(mp4)],
                                        capture_output=True, text=True, check=True).stdout)
            check(abs(real - dur) <= 0.05, f"cena {passo}: data-dur {dur} ≠ duração real {real:.3f} s")
    imgs = re.findall(r"<img ([^>]*)>", fmiolo)
    check(len(imgs) == 1, f"cena {passo}: esperava 1 <img> na figura")
    if imgs:
        ia = atributos(imgs[0])
        check(ia.get("src") == src, f"cena {passo}: imagem {ia.get('src')!r}, esperava {src}")
        check((SITE / src).exists(), f"cena {passo}: {src} não existe")
        check(ia.get("alt") == "", f"cena {passo}: imagem decorativa precisa de alt=\"\"")
        check(ia.get("width") == str(largura) and ia.get("height") == str(altura), f"cena {passo}: width/height devem ser {largura}×{altura}")
        if i == 1:
            check(ia.get("fetchpriority") == "high" and "loading" not in ia, "cena 1: imagem com fetchpriority=\"high\" e sem loading")
        elif tipo == "clipe":  # pôster sem lazy: pronto para o crossfade e para os caminhos só-pôster (a figure fica hidden até a cena)
            check(imgs[0] == f'src="{src}" alt="" width="960" height="540"',
                  f"cena {passo}: pôster exatamente <img src=\"{src}\" alt=\"\" width=\"960\" height=\"540\"> (sem loading, sem fetchpriority)")
        else:
            check(ia.get("loading") == "lazy" and "fetchpriority" not in ia, f"cena {passo}: imagem com loading=\"lazy\" e sem fetchpriority")


def checar_marcacao(pagina, portfolio):
    cs = cenas(pagina)
    check(len(cs) == len(ROTEIRO), f"esperava {len(ROTEIRO)} cenas, achei {len(cs)}")
    ancoras = set(re.findall(r'\bid="([^"]+)"', portfolio))
    nomes_caso = {}
    for i, (c, achado) in enumerate(zip(ROTEIRO, cs), start=1):
        classes, ident, passo_html, miolo = achado
        passo = c["passo"]
        check(ident == passo and passo_html == passo, f"cena {i}: id/data-passo {ident!r}/{passo_html!r}, esperava {passo!r}")
        longa = passo in LONGAS
        check((classes == "cena longa") == longa, f"cena {passo}: a classe 'longa' vai só em casa, icamento e zip")
        m = re.search(r'<(h[12]) class="frase" tabindex="-1">(.*?)</\1>', miolo, re.S)
        check(m is not None and m.group(1) == c["tag"], f"cena {passo}: a frase deve ser <{c['tag']} class=\"frase\" tabindex=\"-1\">")
        if m:
            check(limpo(m.group(2)) == c["frase"], f"cena {passo}: frase {limpo(m.group(2))!r} ≠ roteiro {c['frase']!r}")
        r = re.search(r'<p class="ressalva">(.*?)</p>', miolo, re.S)
        check(r is not None and limpo(r.group(1)) == c["ressalva"], f"cena {passo}: ressalva diferente do roteiro")
        tx = re.search(r'<div class="texto"([^>]*)>', miolo)
        check(tx is not None and "aria-hidden" not in tx.group(1), f"cena {passo}: <div class=\"texto\"> ausente ou com aria-hidden")
        d = re.search(r'<p class="data">(.*?)</p>', miolo, re.S)
        if c["data"] is None:
            check(d is None, f"cena {passo}: moldura não leva data")
        else:
            texto, datas = c["data"]
            check(d is not None and limpo(d.group(1)) == texto, f"cena {passo}: data visível deve ser {texto!r}")
            if d:
                check(re.findall(r'<time datetime="([\d-]+)">', d.group(1)) == datas, f"cena {passo}: <time datetime> devem ser {datas}")
        k = re.search(r'<p class="caso"><a href="portfolio\.html#([a-z]+)">(.*?)</a></p>', miolo, re.S)
        if c["caso"] is None:
            check('class="caso"' not in miolo, f"cena {passo}: moldura não leva link de caso")
        else:
            ancora, nome = c["caso"]
            check(k is not None and k.group(1) == ancora and limpo(k.group(2)) == nome,
                  f"cena {passo}: link do caso deve ser portfolio.html#{ancora} com o texto {nome!r}")
            check(ancora in ancoras, f"cena {passo}: a âncora #{ancora} não existe no portfolio.html")
            check(nome not in nomes_caso, f"cena {passo}: nome de link repetido {nome!r}")
            nomes_caso[nome] = ancora
        checar_fundo(passo, i, c["fundo"], miolo)
    clipes = {c["passo"]: c["fundo"][1] for c in ROTEIRO if c["fundo"] and c["fundo"][0] == "clipe"}
    check(clipes == {p: v[3] for p, v in CLIPES.items()}, f"ROTEIRO e CLIPES divergem: {clipes} × {CLIPES}")
    check(CLIPES["veks"][2] == CLIPES["ferramentas"][1] and CLIPES["whatsapp"][2] == CLIPES["recuperado"][1] == 3.0,
          "cenas partilhadas: veks.t1 == ferramentas.t0 e whatsapp.t1 == recuperado.t0 == 3,0")
    check(not {4, 5, 8} & {v[0] for v in CLIPES.values()}, "as cenas 36 min do filme (SC4), abertura (SC5) e celeiro (SC8) nunca vão à página")
    check(all(v[1] < v[2] for v in CLIPES.values()), "cada trecho anda para a frente (t0 < t1)")
    for proibido in ("<canvas", 'class="hud"', "data-relogio", "data-legenda", "data-cena", "<track", "<source"):
        check(proibido not in corpo(pagina), f"index.html não tem mais {proibido}")  # só a marcação: o CSS tem --data-cena
    check(re.search(r"<video [^>]*\bsrc=", pagina) is None, "nenhum <video> com src no HTML (o JS atribui na hora de carregar)")
    datadas = [data_iso(c["data"][1][0]) for c in ROTEIRO if c["data"]]
    check(datadas == sorted(datadas), f"capítulos fora da ordem cronológica: {datadas}")
    check('<main id="historia" class="historia">' in pagina, "falta <main id=\"historia\" class=\"historia\">")
    check('<div class="palco" aria-hidden="true"></div>' in pagina, "falta o palco vazio com aria-hidden")
    primeiro = re.search(r"<a ([^>]*)>", corpo(pagina))
    check(primeiro is not None and 'class="pular"' in primeiro.group(1) and 'href="#tese"' in primeiro.group(1),
          "o primeiro link da página deve ser o 'Pular para o texto' (href=\"#tese\")")
    barra = re.search(r'<header class="barra">(.*?)</header>', pagina, re.S)
    check(barra is not None, "falta <header class=\"barra\">")
    if barra:
        tb = limpo(barra.group(1))
        for trecho in ("Cássio Viller", "7º semestre de Eng. Civil", "orçamento, planejamento e custos", "CLT ou PJ"):
            check(trecho in tb, f"barra sem {trecho!r}")
        check(f'href="{CURRICULO}"' in barra.group(1) and f'href="{WHATSAPP}' in barra.group(1), "barra sem currículo ou WhatsApp")
    ultima = cs[-1][3] if cs else ""
    for alvo in (WHATSAPP, "portfolio.html", CURRICULO):
        check(f'href="{alvo}' in ultima, f"cena final sem link para {alvo}")
    ficha = re.search(r'<section class="ficha"[^>]*>(.*?)</section>', pagina, re.S)
    check(ficha is not None, "falta a ficha (<section class=\"ficha\">)")
    if ficha:
        for p in PALAVRAS_CHAVE:
            check(p in limpo(ficha.group(1)), f"ficha sem a palavra-chave {p!r}")


def checar_texto(pagina, portfolio):
    for c in ROTEIRO:
        check(len(c["frase"].split()) <= 10, f"cena {c['passo']}: frase com {len(c['frase'].split())} palavras (máx. 10)")
        check(0 < len(c["ressalva"].split()) <= 30, f"cena {c['passo']}: ressalva com {len(c['ressalva'].split())} palavras (1 a 30)")
    mas = sum(1 for c in ROTEIRO for w in re.findall(r"\w+", c["frase"].lower()) if w == "mas")
    check(mas == 1, f"\"mas\" deve aparecer uma vez só entre as frases grandes (achei {mas})")
    t = limpo(corpo(pagina))
    extras = numeros(t) - numeros(limpo(corpo(portfolio)))
    check(not extras, f"números que o portfólio não sustenta: {sorted(extras)}")
    base_datas = limpo(corpo(portfolio)).lower() + " " + (" ".join(CURRICULO_TXT.read_text(encoding="utf-8").split()).lower() if CURRICULO_TXT.exists() else "")
    datas_novas = sorted({d for d in datas(t) if d not in base_datas and d not in DATAS_CONFIRMADAS})
    check(not datas_novas, f"datas que nem o portfólio, nem o currículo, nem a linha do tempo confirmada sustentam: {datas_novas}")
    for r in RESSALVAS:
        check(r in t, f"ressalva ausente: {r!r}")
    for p in PROIBIDOS:
        check(p not in t, f"texto proibido na página: {p!r}")
    check(t.lower().count("você") == 1, "\"você\" deve aparecer uma vez só, no convite final")
    check("centavo, não na parede" not in portfolio, "portfolio.html ainda abre com a frase do centavo (agora é a da contabilidade)")


def bloco_css(css, inicio):
    """Conteúdo de um bloco @media, contando chaves."""
    i = css.find(inicio)
    if i < 0:
        return ""
    j, n = i + len(inicio), 1
    while j < len(css) and n:
        n += {"{": 1, "}": -1}.get(css[j], 0)
        j += 1
    return css[i + len(inicio):j - 1]


def checar_css(pagina):
    css = "\n".join(re.findall(r"<style>(.*?)</style>", pagina, re.S))
    check("dvh" not in css, "não usar dvh: a altura pula com a barra do Safari")
    for n in ("100", "200"):
        check(css.count(f"{n}svh") > 0 and css.count(f"{n}vh") >= css.count(f"{n}svh"),
              f"cada {n}svh precisa de um {n}vh antes, como fallback")
    check(".palco{display:none}" in css, "o palco precisa começar escondido (modo empilhado)")
    regra = re.search(r"\.js-historia \.historia\{([^}]*)\}", css)
    check(regra is not None and "background:var(--tinta)" in regra.group(1),
          "no modo cenas o fundo da história é tinta: sem faixa clara quando a barra do navegador recolhe (svh < lvh)")
    check(".cena{scroll-margin-top:9rem}" in css, "o título do capítulo não pode ficar atrás da barra ao chegar por salto")
    check(re.search(r"\.js-historia \.palco\{display:block;position:sticky;top:var\(--barra,0px\);height:calc\(100vh - var\(--barra,0px\)\);"
                    r"margin-bottom:calc\(-100vh \+ var\(--barra,0px\)\);", css) is not None,
          "modo cenas: o palco gruda abaixo da barra fixa (top:var(--barra,0px)) e perde a altura dela (base em vh)")
    m = re.search(r"--scrim:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", css)
    check(m is not None, "falta --scrim: rgba(...)")
    if not m:
        return
    r, g, b, a = int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4))
    fundo = tuple(round(255 * (1 - a) + c * a) for c in (r, g, b))  # pior caso: pixel branco sob a faixa
    for var in ("--texto-cena", "--ressalva-cena", "--data-cena"):
        cor = re.search(var + r":\s*#([0-9A-Fa-f]{6})", css)
        check(cor is not None, f"falta {var}")
        if cor:
            rgb = tuple(int(cor.group(1)[i:i + 2], 16) for i in (0, 2, 4))
            cr = contraste(rgb, fundo)
            check(cr >= 4.5, f"{var} sobre a faixa: {cr:.2f}:1 no pior caso (mín. 4,5)")
    relogio = re.search(r"--relogio:\s*#([0-9A-Fa-f]{6})", css)
    check(relogio is not None and contraste(tuple(int(relogio.group(1)[i:i + 2], 16) for i in (0, 2, 4)), fundo) >= 3.0,
          "--relogio, o .ano dos fundos tipográficos (texto grande, negrito), sobre a faixa: mínimo 3:1 no pior caso")
    check(re.search(r"(^|[}\n])\.fundo video\{display:none\}", css) is not None, "modo empilhado: a regra .fundo video{display:none} (a do movimento reduzido não vale por ela)")
    pv = re.search(r"\.js-historia \.palco \.fundo video\{([^}]*)\}", css)
    check(pv is not None and all(x in pv.group(1) for x in ("display:block", "object-fit:cover", "object-position:68% 50%", "opacity:0", "transition:opacity .4s")),
          "modo cenas: o vídeo cobre o palco (object-fit:cover; object-position:68% 50%), começa invisível e aparece em .4s")
    check(re.search(r"video[^{}]*\{[^}]*filter", css) is None, "sem filter em seletor com video (a paleta do filme fica como está)")
    check(".js-historia .palco .fundo.viva video{opacity:1}" in css
          and re.search(r"\.js-historia \.palco \.fundo\.viva img\{visibility:hidden;transition:visibility 0s \.4s\}", css) is not None,
          "a imagem só some (.viva) quando há quadro pronto, e só depois do fade de .4s do vídeo (crossfade, sem piscar o palco escuro)")
    check(re.search(r"\.js-historia \.palco \.fundo img\{[^}]*filter:brightness\(\.6\) saturate\(\.85\)", css) is not None,
          "as fotos dos capítulos sem clipe mantêm brightness(.6) saturate(.85)")
    check(".js-historia .palco .fundo.clipe img{filter:none;object-position:68% 50%}" in css, "o pôster do clipe fica igual ao vídeo: sem filtro e com o mesmo recorte 68% 50% (crossfade entre dois quadros iguais)")
    check(".js-historia .cena.longa .texto{position:sticky;top:max(28vh,calc(var(--barra,0px) + 8px))}" in css,
          "capítulos longos: a faixa fixa nunca fica atrás da barra (28vh ou a barra + 8 px, o maior)")
    suporta = bloco_css(css, "@supports (height:100svh){")
    check(".js-historia .palco{height:calc(100svh - var(--barra,0px));margin-bottom:calc(-100svh + var(--barra,0px))}" in suporta
          and ".js-historia .cena.longa .texto{top:max(28svh,calc(var(--barra,0px) + 8px))}" in suporta,
          "as versões svh do palco e da faixa longa vivem num @supports (height:100svh): com var() dentro, uma svh inválida anularia a vh")
    check(".js-historia .palco .fundo.foco-alto video,.js-historia .palco .fundo.foco-alto img{object-position:68% 0%}" in css
          and ".js-historia .palco .fundo.foco-baixo video,.js-historia .palco .fundo.foco-baixo img{object-position:68% 100%}" in css,
          "foco vertical por clipe: .foco-alto recorta pelo pé e .foco-baixo pelo alto (janela mais larga que 16:9); vídeo e pôster iguais")
    reduzido = bloco_css(css, "@media (prefers-reduced-motion: reduce){")
    check(".js-historia .palco .fundo video{display:none}" in reduzido and ".js-historia .palco .fundo.viva img{visibility:visible}" in reduzido,
          "movimento reduzido em tempo real: o CSS esconde o vídeo e mostra a imagem sem JS")
    larga = bloco_css(css, "@media (min-width:900px) and (orientation:landscape){")
    check(".js-historia .cena{justify-content:flex-start}" in larga and ".js-historia .texto{max-width:min(620px,48vw);margin-left:max(24px,6vw);text-align:left}" in larga,
          "tela larga: a faixa de texto vai para a esquerda, como no filme")
    check(".js-historia .palco .fundo.tipo{justify-content:flex-end;padding:0 4vw 3vh 0}" in larga,
          "tela larga: o marco tipográfico (.ano) vai para a direita, longe da faixa de texto à esquerda")
    check(".js-historia .palco .fundo.tipo .ano{font-size:clamp(5rem,13vw,20rem)}" in larga, "tela larga: o marco tipográfico cabe à direita da faixa (13vw) sem passar por baixo dela")
    paisagem = bloco_css(css, "@media (orientation:landscape) and (max-height:520px){")
    check(".js-historia .texto{max-width:min(560px,54vw);margin-left:16px;text-align:left;padding:12px 16px}" in paisagem
          and ".js-historia .frase{font-size:clamp(1.4rem,6.5vh,2.4rem);margin:0}" in paisagem
          and ".js-historia .palco .fundo.tipo{justify-content:flex-end;padding:0 4vw 3vh 0}" in paisagem
          and ".js-historia .palco .fundo.tipo .ano{font-size:clamp(4rem,11vw,20rem)}" in paisagem,
          "celular deitado (≤ 520 px de altura): faixa à esquerda, mais estreita e com o título menor, para o clipe continuar à mostra")
    for sumido in (".hud", ".pausa", "canvas"):
        check(sumido not in css, f"CSS sem {sumido}")
    check("#E0622A" in (ROOT / "DESIGN.md").read_text(encoding="utf-8"), "DESIGN.md: a paleta dos clipes (#EFE6D6 / #1B1714 / #E0622A) fica registrada")


def checar_scripts(pagina):
    tags = re.findall(r"<script ([^>]*)></script>", pagina)
    nomes = [atributos(t).get("src") for t in tags]
    check(nomes == ["clipes.js", "historia.js"], f"scripts devem ser clipes.js e historia.js, nessa ordem; achei {nomes}")
    check(all(" defer" in " " + t for t in tags), "os scripts precisam de defer")
    check("<script>" not in pagina, "sem script inline")


CURRICULO_TXT = ROOT / "curriculo" / "curriculo-cassio-viller.txt"
# (trecho da história, trecho do currículo em PDF): as datas precisam bater nos dois
DATAS_CV = [("fev/2025 → mar/2026", "02/2025 – 07/2026"), ("fev/2025 → mar/2026", "04/2025 – 03/2026"),
            ("mar/2026 → set/2026", "03/2026 – 09/2026"), ("de 2023 a 2024", "03/2023 – 12/2024"),
            ("DCE em 2022", "DCE UNIFEI (2022)")]


def checar_curriculo(pagina):
    check(CURRICULO_TXT.exists(), "portfolio/curriculo/curriculo-cassio-viller.txt não existe (gerado pelo build.sh)")
    if not CURRICULO_TXT.exists():
        return
    cv = " ".join(CURRICULO_TXT.read_text(encoding="utf-8").split())
    t = limpo(corpo(pagina))
    for na_pagina, no_cv in DATAS_CV:
        check(na_pagina in t and no_cv in cv, f"datas da história e do currículo divergem: {na_pagina!r} × {no_cv!r}")


MARCOS = {"tese": "Início", "origem": "Contabilidade e UNIFEI", "mudanca": "Mudança para São José dos Campos",
          "obra": "Entrada na obra", "veks": "VEKS Engenharia", "ferramentas": "Ferramentas", "sige": "SIGE, versão atual",
          "galpoes": "Obra dos galpões", "escala": "Sistema de orçamento", "precisao": "Conferência SINAPI",
          "casa": "Celeiro B-36", "icamento": "Içamento do módulo", "whatsapp": "Diário no WhatsApp",
          "recuperado": "Diários recuperados", "zip": "36 minutos", "metodo": "O método", "convite": "Convite"}


def checar_regua(pagina):
    barra = re.search(r'<header class="barra">(.*?)</header>', pagina, re.S)
    nav = re.search(r'<nav class="regua" aria-label="Linha do tempo">(.*?)</nav>', barra.group(1) if barra else "", re.S)
    check(nav is not None, "a régua (<nav class=\"regua\" aria-label=\"Linha do tempo\">) precisa estar dentro da barra")
    if not nav:
        return
    links = re.findall(r'<li><a href="#([a-z0-9]+)"([^>]*)>(.*?)</a></li>', nav.group(1), re.S)
    check([l[0] for l in links] == [c["passo"] for c in ROTEIRO], "a régua precisa de um link por capítulo, na ordem do roteiro")
    for (passo, extra, miolo), c in zip(links, ROTEIRO):
        esperado = (c["data"][0] + " " if c["data"] else "") + MARCOS[passo]
        check(limpo(miolo) == esperado, f"régua {passo}: nome acessível {limpo(miolo)!r}, esperava {esperado!r}")
        if c["data"]:
            check(f'<time datetime="{c["data"][1][0]}">' in miolo, f"régua {passo}: falta <time datetime=\"{c['data'][1][0]}\">")
    atuais = [l[0] for l in links if 'aria-current="step"' in l[1]]
    check(atuais == ["tese"], f"no HTML, só o primeiro marco tem aria-current=\"step\" (achei {atuais})")
    check("aria-live" not in pagina, "a régua não anuncia troca de capítulo (sem aria-live)")
    css = "\n".join(re.findall(r"<style>(.*?)</style>", pagina, re.S))
    check(re.search(r"\.regua a\{[^}]*min-width:28px", css) is not None, "cada marco da régua precisa de pelo menos 28 px de largura (alvo de toque)")
    check(re.search(r"\.regua ol\{[^}]*overflow-x:auto", css) is not None, "quando não couber, a régua rola sozinha — nunca a página")
    check(".regua a:focus-visible{outline-offset:-3px}" in css, "o anel de foco da régua fica por dentro do marco (a lista rolável cortaria o anel de fora)")


PORTA = 5056
PORTA_CDP = 9333


@contextlib.contextmanager
def servidor(porta, com_range=True):
    """Servidor estático em portfolio/: servir.py (com Range → 206) ou, para o teste negativo, o http.server puro."""
    base = [sys.executable, str(ROOT / "servir.py")] if com_range else [sys.executable, "-m", "http.server"]
    srv = subprocess.Popen(base + [str(porta), "--bind", "127.0.0.1", "--directory", str(ROOT)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", porta), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.05)
        yield
    finally:
        srv.terminate()
        srv.wait()


def checar_servidor():
    """servir.py responde 206 com Content-Range a um pedido com Range: sem isso o Chrome ignora todo seek no vídeo."""
    check((ROOT / "servir.py").exists(), "portfolio/servir.py não existe")
    if not (ROOT / "servir.py").exists():
        return
    with servidor(PORTA):
        req = urllib.request.Request(f"http://127.0.0.1:{PORTA}/site/index.html", headers={"Range": "bytes=0-99"})
        with urllib.request.urlopen(req) as r:
            check(r.status == 206 and r.headers.get("Content-Range", "").startswith("bytes 0-99/") and len(r.read()) == 100,
                  "servir.py: Range: bytes=0-99 deve responder 206, Content-Range e exatamente 100 bytes")
        with urllib.request.urlopen(f"http://127.0.0.1:{PORTA}/site/index.html") as r:
            check(r.status == 200 and r.headers.get("Accept-Ranges") == "bytes", "servir.py: sem Range, 200 com Accept-Ranges: bytes")


BASELINE = ROOT / "tests" / "baseline.json"


def metrica(ws, nome):
    return next(m["value"] for m in ws.comando("Performance.getMetrics")["metrics"] if m["name"] == nome)


def medir_desempenho(ws):
    """Segundos de TaskDuration numa rolagem completa, capítulo a capítulo (0,6 s em cada), com a página já carregada."""
    ws.comando("Performance.enable")
    antes = metrica(ws, "TaskDuration")
    n = ws.avaliar("document.querySelectorAll('.cena[data-passo]').length")
    for i in range(n):
        ws.avaliar(f"(function(){{var r=document.querySelectorAll('.cena[data-passo]')[{i}].getBoundingClientRect();"
                   "window.scrollTo(0,scrollY+r.top+r.height/2-innerHeight/2);})()")
        time.sleep(0.6)
    return metrica(ws, "TaskDuration") - antes


def gravar_baseline():
    """Linha de base da página de hoje (maquetes WebGL por SwiftShader): F-17 compara a página com clipes a 2× isto."""
    base = {"alturaMain": {}}
    for largura in (390, 1280):
        with chromium(largura, ("--enable-unsafe-swiftshader",)) as ws:
            ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/site/index.html")
            time.sleep(2.5)
            if largura == 390:
                base["taskDuration"] = round(medir_desempenho(ws), 3)
            base["alturaMain"][str(largura)] = ws.avaliar("document.getElementById('historia').offsetHeight")
    BASELINE.write_text(json.dumps(base, indent=1) + "\n", encoding="utf-8")
    print("baseline:", base)


def checar_js():
    caminho = SITE / "historia.js"
    check(caminho.exists(), "portfolio/site/historia.js não existe")
    if not caminho.exists():
        return
    js = re.sub(r"//[^\n]*", "", caminho.read_text(encoding="utf-8"))  # comentários não contam
    for proibido in ("scrollTo", "scrollBy", "scrollIntoView", "preventDefault", "'wheel'", "'touchmove'", "aria-live", "__maquete", "'maquete'", "*0.999"):
        check(proibido not in js, f"historia.js não pode usar {proibido}")
    check("fps" not in js.lower() and "matar" not in js, "historia.js não duplica a guarda de desempenho do maquetes.js")
    for exigido in ("'--barra'", "ResizeObserver", "'resize'", ".barra"):
        check(exigido in js, f"historia.js precisa de {exigido}: mede a barra fixa (e toda mudança de altura dela) para o palco começar abaixo dela")


def checar_clipes_js():
    caminho = SITE / "clipes.js"
    check(caminho.exists(), "portfolio/site/clipes.js não existe")
    if not caminho.exists():
        return
    js = re.sub(r"//[^\n]*", "", caminho.read_text(encoding="utf-8"))  # comentários não contam
    for proibido in ("play(", "autoplay", "loop", "fastSeek", "requestAnimationFrame", "fetch(", "createObjectURL",
                     "scrollTo", "scrollBy", "scrollIntoView", "preventDefault", "'wheel'", "'touchmove'", "aria-live"):
        check(proibido not in js, f"clipes.js não pode usar {proibido}")
    for exigido in ("canPlayType", "'seeked'", "seekable", "rootMargin:'600px", "preload='auto'", ".load()", "removeAttribute('src')",
                    "prefers-reduced-motion: reduce", "'change'", "saveData", "clipes=nao", "readyState", "'load'",
                    "TETO=250", "LENTOS=3", "VOO=600", "MAXIMO=2", "fig.__clipe=api", "'progress'", "'canplay'", "'emptied'", "networkState", "esperados",
                    "ESPERA_RANGE=1500", "temRange", "desde", "||!temRange()", "Math.min(Math.round(t*FPS),ultimo)"):
        check(exigido in js, f"clipes.js precisa de {exigido}")
    check("(Math.min(Math.round(t*FPS),ultimo)+0.5)/FPS" in js, "clipes.js: seek quantizado ao quadro e nunca além do último, (min(round(t·24), round(dur·24)−1)+0,5)/24")
    check("v.currentTime=" in js and js.count("currentTime=") == 1, "clipes.js: o tempo do vídeo só muda por currentTime, num lugar só")


def checar_maquetes_js():
    js = (SITE / "maquetes.js").read_text(encoding="utf-8")
    check("dur:sc.dur" in js, "maquetes.js precisa expor a duração da cena em fig.__maquete.dur")
    check("cenaIcamento" not in js and "'icamento'" not in js,
          "maquetes.js: a cena do içamento vive só no film.html (SC[10], clipe cena-icamento); a página não roda mais WebGL na história")
    check('data-cena="icamento"' not in PORTFOLIO.read_text(encoding="utf-8"), "portfolio.html não tem maquete do içamento")
    check("var CENAS={'36min':cena36,'casa-viaja':cenaCasa};" in js, "CENAS do maquetes.js: só 36min e casa-viaja")


def checar_readme():
    """O README do portfólio explica o servidor com Range e como gerar os clipes (F-16)."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for trecho in ("servir.py", "206", "render_clipes.py", "--origem", "clipes.js", "foco-alto", "--barra"):
        check(trecho in readme, f"README do portfólio sem {trecho!r}")


class WS:
    """Cliente WebSocket mínimo (mensagens de texto) para falar com o Chromium pelo DevTools Protocol."""

    def __init__(self, url):
        u = urlparse(url)
        self.s = socket.create_connection((u.hostname, u.port), timeout=60)
        chave = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\n"
                        f"Connection: Upgrade\r\nSec-WebSocket-Key: {chave}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        resposta = b""
        while b"\r\n\r\n" not in resposta:
            resposta += self.s.recv(1)
        if b" 101 " not in resposta.split(b"\r\n")[0]:
            raise RuntimeError(f"WebSocket recusado: {resposta[:80]!r}")
        self.n = 0

    def _ler(self, n):
        b = b""
        while len(b) < n:
            parte = self.s.recv(n - len(b))
            if not parte:
                raise RuntimeError("a conexão com o Chromium caiu")
            b += parte
        return b

    def _receber(self):
        texto = b""
        while True:
            b1, b2 = self._ler(2)
            n = b2 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._ler(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._ler(8))[0]
            texto += self._ler(n)
            if b1 & 0x80:
                return json.loads(texto)

    def comando(self, metodo, **params):
        self.n += 1
        dados = json.dumps({"id": self.n, "method": metodo, "params": params}).encode()
        n = len(dados)
        if n < 126:
            cab = bytes([0x81, 0x80 | n])
        elif n < 65536:
            cab = bytes([0x81, 0x80 | 126]) + struct.pack(">H", n)
        else:
            cab = bytes([0x81, 0x80 | 127]) + struct.pack(">Q", n)
        mascara = os.urandom(4)
        self.s.sendall(cab + mascara + bytes(b ^ mascara[i % 4] for i, b in enumerate(dados)))
        while True:
            msg = self._receber()
            if msg.get("id") == self.n:
                return msg.get("result", {})

    def avaliar(self, expressao):
        r = self.comando("Runtime.evaluate", expression=expressao, returnByValue=True)
        return r.get("result", {}).get("value")


@contextlib.contextmanager
def chromium(largura, extra=(), altura=800, com_range=True):
    """servir.py (Range) em portfolio/ + Chromium headless em tempo real, controlado pelo DevTools Protocol.
    Não usar --virtual-time-budget: nele quase não há quadros, e sem quadros nem o IntersectionObserver nem o scroll disparam."""
    with servidor(PORTA, com_range):
        nav = subprocess.Popen(["chromium", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                                f"--window-size={largura},{altura}", f"--remote-debugging-port={PORTA_CDP}", *extra, "about:blank"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            alvos = []
            for _ in range(100):
                try:
                    alvos = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORTA_CDP}/json/list"))
                    break
                except OSError:
                    time.sleep(0.1)
            paginas = [a for a in alvos if a.get("type") == "page"]
            if not paginas:
                raise RuntimeError("o Chromium não abriu a porta do DevTools")
            ws = WS(paginas[0]["webSocketDebuggerUrl"])
            # o headless impõe janela mínima de ~500×657; o override garante exatamente largura × altura
            ws.comando("Emulation.setDeviceMetricsOverride", width=largura, height=altura, deviceScaleFactor=1, mobile=False)
            yield ws
        finally:
            nav.terminate()
            nav.wait()


def navegador(largura=390, extra=()):
    """Roda o harness e devolve as linhas do <pre id="resultado"> (espera até 150 s pelo FIM)."""
    with chromium(largura, extra) as ws:
        ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/tests/historia_teste.html")
        prazo = time.time() + 150
        texto = ""
        while time.time() < prazo:
            texto = ws.avaliar("(document.getElementById('resultado')||{}).textContent||''") or ""
            if texto.endswith("FIM"):
                break
            time.sleep(0.5)
    return texto.splitlines()


def checar_navegador():
    clipes = [c["passo"] for c in ROTEIRO if c["fundo"] and c["fundo"][0] == "clipe"]
    normal = navegador(390)
    check("FIM" in normal, f"390 px: o harness não terminou — últimas linhas {normal[-3:]}")
    for linha in ("reduzido=false", "js-historia=true", "overflow-x=false", "inicio ativa=tese", "salto ativa=tese clipes=-",
                  "reversao-48 ativa=casa", "reversao-95 ativa=precisao"):
        check(linha in normal, f"390 px: faltou {linha!r}")
    for c in ROTEIRO:
        passo = c["passo"]
        fundo = passo if c["fundo"] else "nenhum"
        maq = passo if passo in clipes else "-"
        esperado = f"cena {passo} ativa={passo} fundo={fundo} clipes={maq}"
        check(esperado in normal, f"390 px: esperava {esperado!r}")
        inicio = c["data"][0].split("→")[0].strip() if c["data"] else ""
        rotulo = (inicio if re.search(r"\d", inicio) else inicio + "/" + c["data"][0].split("/")[-1].strip()) if c["data"] else "2017–2026"
        check(f"regua {passo}=#{passo} n=1 data={rotulo}" in normal,
              f"390 px: na cena {passo}, o marco ativo da régua deve ser #{passo} (e só ele), com a data {rotulo!r} à direita")
        if passo in clipes:
            check(f"img {passo}=visible" in normal, f"390 px: sem WebGL, a imagem de reserva da cena {passo} precisa ficar visível")
    estreito = navegador(320)
    check("FIM" in estreito, "320 px: o harness não terminou")
    check("overflow-x=false" in estreito, "320 px: a página rola na horizontal")
    reduzido = navegador(390, ("--disable-3d-apis", "--force-prefers-reduced-motion"))
    check("reduzido=true" in reduzido, "o Chromium não aplicou --force-prefers-reduced-motion")
    check("salto-regua foco=veks ativa=veks abaixo-da-barra=true" in normal,
          "390 px: saltar pela régua leva o foco ao título do capítulo, abaixo da barra, e ativa a cena")
    for linha in ("js-historia=false", "palco-filhos=0", f"frases-visiveis={len(ROTEIRO)}", "overflow-x=false",
                  "salto-regua foco=veks ativa=null abaixo-da-barra=true"):
        check(linha in reduzido, f"movimento reduzido: faltou {linha!r}")
    texto_normal = "\n".join(normal)
    check(re.search(r"^seek-tardio zip=\d", texto_normal, re.M) is not None,
          "clipes.js que chega depois da rolagem: o clipe precisa ser sincronizado (e congelado), sem limite de tentativas")
    check("progresso=0 0.5 1 0" in normal, "Historia.progresso fora do esperado (0 no topo, 0,5 no meio, 1 no fim, 0 sem altura)")
    for passo in clipes:
        for chave, alvo in (("seek", 500), ("seek25", 250)):
            m = re.search(rf"^{chave} {passo}=([\d.]+)$", texto_normal, re.M)
            check(m is not None and abs(float(m.group(1)) - alvo) <= 20,
                  f"{chave} {passo}: esperava ≈{alvo} (dur 1000), achei {m.group(1) if m else 'nada'}")


def checar_ficha_a_vista():
    """O palco é sticky com margin-bottom:-100vh: não pode passar do fim da história e cobrir a ficha no fim da página."""
    ver = ("(function(sel){var r=document.querySelector(sel).getBoundingClientRect();"
           "var topo=Math.max(r.top,0),base=Math.min(r.bottom,innerHeight);if(base<=topo)return 'fora';"
           "var e=document.elementFromPoint(innerWidth/2,(topo+base)/2);"
           "return e&&e.closest(sel)?'visivel':(e&&e.closest('.palco')?'coberto pelo palco':'coberto por '+(e&&e.tagName));})")
    for largura in (390, 1280):
        with chromium(largura, ("--disable-3d-apis",)) as ws:
            ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/site/index.html")
            time.sleep(1.5)
            ws.avaliar("window.scrollTo(0,document.documentElement.scrollHeight)")
            time.sleep(1)
            ficha = ws.avaliar(ver + "('.ficha')")
        check(ficha == "visivel", f"{largura} px: no fim da página, a ficha precisa estar à vista ({ficha})")


# ---------- clipes de verdade (F-08, F-09, F-10, F-11, F-13, F-17): espiões injetados antes da navegação e leituras da página ----------
ESPIAO = (
    "window.__plays=0;window.__erros=[];window.__lcp='';window.__cls=0;"
    "var _play=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__plays++;return _play.apply(this,arguments);};"
    "addEventListener('error',function(e){__erros.push(String(e.message));});"
    "addEventListener('unhandledrejection',function(e){__erros.push('promise: '+String(e.reason));});"
    "var _ce=console.error;console.error=function(){__erros.push(String(arguments[0]));return _ce.apply(console,arguments);};"
    "new PerformanceObserver(function(l){l.getEntries().forEach(function(e){__lcp=(e.element&&e.element.tagName||'?')+' '+(e.url||'');});})"
    ".observe({type:'largest-contentful-paint',buffered:true});"
    "new PerformanceObserver(function(l){l.getEntries().forEach(function(e){if(!e.hadRecentInput)__cls+=e.value;});})"
    ".observe({type:'layout-shift',buffered:true});"
    "window.__vivas=0;new MutationObserver(function(ms){ms.forEach(function(m){if(m.target.classList&&m.target.classList.contains('viva'))window.__vivas++;});})"
    ".observe(document,{attributes:true,attributeFilter:['class'],subtree:true});")  # document: o documentElement ainda é null aqui
# troca o clipe do whatsapp por um arquivo que não existe (404) antes de o clipes.js rodar: o leitor tem de ver o pôster
TROCA_404 = ("window.__troca='tarde';new MutationObserver(function(ms,o){var f=document.querySelector('figure.clipe[data-passo=\"whatsapp\"]');"
             "if(f){f.dataset.clipe='video/nao-existe.mp4';window.__troca=f.__clipe?'tarde':'antes';o.disconnect();}})"
             ".observe(document,{childList:true,subtree:true});")
LER_CLIPES = (
    "JSON.stringify((function(){var figs=[].slice.call(document.querySelectorAll('figure.clipe'));"
    "var res=performance.getEntriesByType('resource'),nav=performance.getEntriesByType('navigation')[0];"
    "var mp4=res.filter(function(e){return /\\.mp4/.test(e.name);});"
    "function passos(f){return f.map(function(x){return x.dataset.passo;});}"
    "return {mp4:mp4.length,pedidos404:res.filter(function(e){return /nao-existe\\.mp4/.test(e.name);}).length,"
    "mp4AntesDoLoad:mp4.filter(function(e){return e.startTime<nav.loadEventStart;}).length,"
    "three:res.filter(function(e){return /three/i.test(e.name);}).length,"
    "comDados:passos(figs.filter(function(f){return f.querySelector('video').readyState>0;})),"
    "comSrc:passos(figs.filter(function(f){return f.querySelector('video').hasAttribute('src');})),"
    "vivas:passos(figs.filter(function(f){return f.classList.contains('viva');})),"
    "pausados:figs.every(function(f){return f.querySelector('video').paused;}),plays:window.__plays||0,erros:window.__erros||[],"
    "ativa:(window.Historia||{}).ativa,jsHistoria:document.documentElement.classList.contains('js-historia')};})())")


VAZIO_CLIPES = {"mp4": 0, "pedidos404": 0, "mp4AntesDoLoad": 0, "three": 0, "comDados": [], "comSrc": [], "vivas": [], "pausados": False,
                "plays": 0, "erros": ["exceção ao ler o estado dos clipes"], "ativa": None, "jsHistoria": False}
VAZIO_CLIPE = {"viva": False, "frozen": False, "dur": None, "ready": -1, "seekEnd": -1, "t": -1, "img": "?", "video": "?", "opacidade": "?", "src": None, "paused": None}


def ler_clipes(ws):
    """Resumo dos clipes da página: requisições .mp4 (e se alguma veio antes do load), vídeos com dados/src, .viva, play(), erros."""
    bruto = ws.avaliar(LER_CLIPES)
    check(bruto is not None, "a página lançou uma exceção ao ler o estado dos clipes (LER_CLIPES não devolveu nada)")
    return json.loads(bruto) if bruto else dict(VAZIO_CLIPES)


def ler_clipe(ws, passo):
    """Estado de uma figure de clipe: .viva, API, readyState, seekable, currentTime, visibilidade da imagem e do vídeo."""
    bruto = ws.avaliar(
        "JSON.stringify((function(p){var f=document.querySelector('figure.clipe[data-passo=\"'+p+'\"]'),v=f.querySelector('video'),a=f.__clipe;"
        "return {viva:f.classList.contains('viva'),frozen:!!a&&a.frozen===true,dur:a?a.dur:null,ready:v.readyState,"
        "seekEnd:v.seekable.length?v.seekable.end(0):-1,t:v.currentTime,img:getComputedStyle(f.querySelector('img')).visibility,"
        "video:getComputedStyle(v).display,opacidade:getComputedStyle(v).opacity,src:v.getAttribute('src'),paused:v.paused};})("
        + json.dumps(passo) + "))")
    check(bruto is not None, f"a página lançou uma exceção ao ler o clipe {passo}")
    return json.loads(bruto) if bruto else dict(VAZIO_CLIPE)


def esperar(ws, expressao, prazo):
    """Avalia `expressao` a cada 0,25 s até dar verdadeiro ou o prazo (s) acabar; devolve o último valor."""
    fim = time.time() + prazo
    while True:
        valor = ws.avaliar(expressao)
        if valor or time.time() >= fim:
            return valor
        time.sleep(0.25)


def navegar(ws, caminho="site/index.html"):
    """Abre a página e espera o load da janela (o clipes.js só carrega depois dele) e o historia.js."""
    ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/{caminho}")
    check(esperar(ws, "document.readyState==='complete'&&!!window.Historia", 15), f"{caminho}: a página não carregou em 15 s")
    time.sleep(0.5)


def rolar_ate(ws, passo, fracao):
    """Rola até o progresso `fracao` da cena (0: o topo cruza o meio da tela; 1: o fim cruza) — o mesmo progresso() do historia.js."""
    ws.avaliar(f"(function(){{var r=document.getElementById('{passo}').getBoundingClientRect();"
               f"window.scrollTo(0,scrollY+r.top+r.height*{fracao}-innerHeight/2);}})()")


def quadro(t, dur):
    """O quantizador do clipes.js: o meio do quadro mais próximo a 24 fps, nunca além do último quadro do clipe."""
    return (min(int(t * 24 + 0.5), int(round(dur * 24)) - 1) + 0.5) / 24


VIDEO_ICAMENTO = "document.querySelector('figure.clipe[data-passo=\"icamento\"] video')"


def checar_clipe_real():
    """Servidor com Range e clipes de verdade (F-08): nada baixa antes do load; a 40 % do içamento o clipe carrega, busca o
    quadro do progresso e só então a imagem some; seeks a cada rAF chegam; nunca play(); no máximo 2 vídeos com dados numa
    rolagem rápida; 404 e ?clipes=nao ficam no pôster; sem Range, nenhuma .viva e nenhum erro."""
    dur = CLIPES["icamento"][3]
    with chromium(390, altura=844) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO + TROCA_404)
        navegar(ws)
        time.sleep(1)
        e = ler_clipes(ws)
        check(e["jsHistoria"] and e["ativa"] == "tese", f"modo cenas na tese (js-historia={e['jsHistoria']}, ativa={e['ativa']})")
        check(e["mp4AntesDoLoad"] == 0 and e["three"] == 0,
              f"nenhum .mp4 antes do load nem three.js ({e['mp4AntesDoLoad']} mp4 antes do load, {e['three']} three)")
        check(len(e["comDados"]) <= 2, f"em scrollY=0, no máximo 2 vídeos com dados (achei {e['comDados']})")
        troca = ws.avaliar("window.__troca")
        check(troca == "antes", f"o espião do 404 precisa trocar data-clipe antes de o clipes.js rodar (__troca={troca!r})")
        # 40 % do içamento: carrega, busca o quadro do progresso e mostra o vídeo
        rolar_ate(ws, "icamento", 0.4)
        pronto = esperar(ws, "(function(){var f=document.querySelector('figure.clipe[data-passo=\"icamento\"]');"
                             "return f.classList.contains('viva')&&!!f.__clipe&&f.__clipe.frozen===true;})()", 25)
        time.sleep(0.6)  # a transição de opacidade do vídeo dura .4 s
        c = ler_clipe(ws, "icamento")
        check(pronto, f"a 40 % do içamento, .viva e __clipe.frozen em ≤ 25 s (estado: {c})")
        check(c["ready"] >= 2 and c["seekEnd"] >= dur - 0.5, f"içamento: readyState {c['ready']} (≥ 2) e seekable até {c['seekEnd']} (≥ {dur - 0.5})")
        check(abs(c["t"] - quadro(0.4 * dur, dur)) <= 0.15, f"içamento a 40 %: currentTime {c['t']:.3f} ≠ quadro(0,4·{dur}) = {quadro(0.4 * dur, dur):.3f}")
        check(c["img"] == "hidden" and c["opacidade"] == "1",
              f"com quadro pronto, a imagem some e o vídeo aparece (img {c['img']}, opacity {c['opacidade']})")
        rolar_ate(ws, "icamento", 0.75)
        alvo = quadro(0.75 * dur, dur)
        esperar(ws, f"Math.abs({VIDEO_ICAMENTO}.currentTime-{alvo})<=0.15", 3)
        c = ler_clipe(ws, "icamento")
        check(abs(c["t"] - alvo) <= 0.15, f"içamento a 75 %: currentTime {c['t']:.3f} ≠ {alvo:.3f}")
        rolar_ate(ws, "icamento", 1.0)  # o fim da cena pede o último quadro, nunca além da duração
        alvo = quadro(dur, dur)
        esperar(ws, f"Math.abs({VIDEO_ICAMENTO}.currentTime-{alvo})<=0.15", 3)
        c = ler_clipe(ws, "icamento")
        check(abs(c["t"] - alvo) <= 0.15 and c["t"] < dur, f"içamento a 100 %: currentTime {c['t']:.3f} ≠ último quadro {alvo:.3f} (nunca ≥ dur={dur})")
        # 30 seeks, um por rAF: intervalo entre seeked consecutivos (um seek em voo por vez; com pedido pendente, é a latência)
        ws.avaliar("window.__medida=null;(function(){var f=document.querySelector('figure.clipe[data-passo=\"icamento\"]'),v=f.querySelector('video'),"
                   "a=f.__clipe,ini=performance.now(),n=0,lat=[];function s(){var t=performance.now();lat.push(t-ini);ini=t;}v.addEventListener('seeked',s);"
                   "(function passo(){if(n>=30){setTimeout(function(){v.removeEventListener('seeked',s);lat.sort(function(x,y){return x-y;});"
                   "window.__medida={n:lat.length,mediana:lat.length?lat[lat.length>>1]:-1,t:v.currentTime};},700);return;}"
                   "a.seek(1+n*0.2);n++;requestAnimationFrame(passo);})();})()")
        m = json.loads(esperar(ws, "window.__medida&&JSON.stringify(window.__medida)", 10) or "null") or {}  # "null" é verdadeiro: espera o objeto
        check(m.get("n", 0) >= 20 and 0 <= m.get("mediana", -1) <= 40,
              f"30 seeks um por rAF: {m.get('n')} seeked (≥ 20), mediana {m.get('mediana')} ms (≤ 40) — GOP curto e seek por currentTime")
        check(abs(m.get("t", -1) - quadro(1 + 29 * 0.2, dur)) <= 0.15, f"o último pedido vence: currentTime {m.get('t')} ≠ {quadro(1 + 29 * 0.2, dur):.3f}")
        t1 = ws.avaliar(VIDEO_ICAMENTO + ".currentTime")
        time.sleep(2)
        t2 = ws.avaliar(VIDEO_ICAMENTO + ".currentTime")
        check(t1 == t2, f"parado 2 s, o clipe não anda sozinho ({t1} → {t2})")
        e = ler_clipes(ws)
        check(e["plays"] == 0 and e["pausados"], f"play() nunca é chamado ({e['plays']}) e todo vídeo fica pausado ({e['pausados']})")
        # rolagem rápida por três capítulos de clipe seguidos: nunca mais de 2 vídeos com dados
        for passo in ("veks", "ferramentas", "sige", "whatsapp", "recuperado", "zip"):
            rolar_ate(ws, passo, 0.5)
            time.sleep(0.35)
            e = ler_clipes(ws)
            check(len(e["comDados"]) <= 2, f"parada em {passo}: {e['comDados']} vídeos com dados (máx. 2)")
        # 404: o clipe do whatsapp não existe no servidor — pôster, sem .viva, sem src, sem erro não tratado
        rolar_ate(ws, "whatsapp", 0.5)
        esperar(ws, "(function(){var f=document.querySelector('figure.clipe[data-passo=\"whatsapp\"]');return !!f.__clipe&&f.__clipe.morto===true;})()", 5)
        c, e = ler_clipe(ws, "whatsapp"), ler_clipes(ws)
        check(e["pedidos404"] >= 1, f"o clipe trocado para 404 tem de ter sido pedido ({e['pedidos404']} pedidos a nao-existe.mp4)")
        check(not c["viva"] and c["img"] == "visible" and c["src"] is None and c["ready"] == 0,
              f"clipe inexistente (404): fica o pôster, sem .viva e sem src (estado: {c})")
        check(e["erros"] == [], f"console limpo com um clipe em 404: {e['erros']}")
        # ?clipes=nao na mesma página: nenhum vídeo, pôster visível, API presente (o historia.js continua chamando seek)
        navegar(ws, "site/index.html?clipes=nao")
        rolar_ate(ws, "icamento", 0.4)
        time.sleep(3)
        c, e = ler_clipe(ws, "icamento"), ler_clipes(ws)
        check(e["mp4"] == 0 and e["comSrc"] == [] and e["jsHistoria"],
              f"?clipes=nao: zero .mp4 e modo cenas (achei {e['mp4']} mp4, src em {e['comSrc']}, js-historia={e['jsHistoria']})")
        check(c["img"] == "visible" and not c["viva"] and c["dur"] == dur and c["frozen"], f"?clipes=nao: pôster visível e API com dur={dur} (estado: {c})")
    # origem publicada sem Range (o http.server puro): a página não pode quebrar — pôster e texto, console limpo
    with chromium(390, altura=844, com_range=False) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        time.sleep(5)  # tempo de sobra para metadados → seekable [0,0] → congelar() → descarregar()
        c, e = ler_clipe(ws, "icamento"), ler_clipes(ws)
        check(e["vivas"] == [] and c["img"] == "visible" and c["src"] is None and c["ready"] == 0,
              f"servidor sem Range: nenhuma .viva, pôster visível, vídeo descarregado (estado: {c}, vivas {e['vivas']})")
        check(ws.avaliar("window.__vivas") == 0, f"servidor sem Range: .viva nunca pode aparecer, nem por instantes (apareceu {ws.avaliar('window.__vivas')}×)")
        check(e["erros"] == [], f"servidor sem Range: console limpo ({e['erros']})")


def checar_reduzido_real():
    """Movimento reduzido (F-09): na carga, empilhado, nenhum clipe e o vídeo sem display; ligado no meio da história, todo
    vídeo descarrega em ≤ 1 s e o pôster volta pelo CSS; nada novo baixa; ao desligar, o clipe ativo recarrega em ≤ 2 s."""
    with chromium(390, ("--force-prefers-reduced-motion",), altura=844) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        time.sleep(3)
        c, e = ler_clipe(ws, "icamento"), ler_clipes(ws)
        check(not e["jsHistoria"] and e["mp4"] == 0 and c["video"] == "none" and c["img"] == "visible",
              f"movimento reduzido na carga: empilhado, zero .mp4, vídeo display:none (js-historia={e['jsHistoria']}, mp4={e['mp4']}, video={c['video']}, img={c['img']})")
    with chromium(390, altura=844) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        check(esperar(ws, "document.querySelector('figure.clipe[data-passo=\"icamento\"]').classList.contains('viva')", 25),
              "içamento .viva antes de ligar o movimento reduzido")
        ws.comando("Emulation.setEmulatedMedia", features=[{"name": "prefers-reduced-motion", "value": "reduce"}])
        descarregou = esperar(ws, "[].every.call(document.querySelectorAll('figure.clipe video'),function(v){return !v.hasAttribute('src')&&v.readyState===0;})", 1)
        c = ler_clipe(ws, "icamento")
        check(descarregou, f"movimento reduzido ligado no meio: todo vídeo sem src e readyState 0 em ≤ 1 s (içamento: {c})")
        check(c["video"] == "none" and c["img"] == "visible",
              f"movimento reduzido ligado no meio: o CSS esconde o vídeo e mostra a imagem (video {c['video']}, img {c['img']})")
        antes = ler_clipes(ws)["mp4"]
        rolar_ate(ws, "zip", 0.4)
        time.sleep(1)
        rolar_ate(ws, "casa", 0.4)
        time.sleep(1)
        e = ler_clipes(ws)
        check(e["mp4"] == antes and e["comSrc"] == [],
              f"com movimento reduzido ligado, nenhum clipe novo baixa em 2 s de rolagem ({antes} → {e['mp4']}, src em {e['comSrc']})")
        ws.comando("Emulation.setEmulatedMedia", features=[{"name": "prefers-reduced-motion", "value": "no-preference"}])
        voltou = esperar(ws, "document.querySelector('figure.clipe[data-passo=\"casa\"] video').readyState>=1", 2)
        c, e = ler_clipe(ws, "casa"), ler_clipes(ws)
        check(voltou and e["ativa"] == "casa", f"ao desligar o movimento reduzido, o clipe ativo (casa) recarrega em ≤ 2 s (readyState {c['ready']}, ativa {e['ativa']!r})")


def checar_evicao():
    """Despejo pelo navegador (WebKit sob pressão de memória esvazia o vídeo e mantém o src; simulado reatribuindo o mesmo src com
    preload='none'): depois de .viva, o clipe da cena ativa recarrega sozinho; despejado antes dos metadados (rede lenta emulada
    pelo CDP), também recarrega — o 'emptied' do nosso próprio load() não é confundido com o do navegador."""
    with chromium(390, altura=844) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        check(esperar(ws, "document.querySelector('figure.clipe[data-passo=\"icamento\"]').classList.contains('viva')", 25), "içamento .viva antes do despejo")
        ws.avaliar(VIDEO_ICAMENTO + ".preload='none';" + VIDEO_ICAMENTO + ".setAttribute('src'," + VIDEO_ICAMENTO + ".getAttribute('src'))")  # o navegador "esvaziou" o vídeo (o WebKit mantém o src)
        voltou = esperar(ws, "(function(){var f=document.querySelector('figure.clipe[data-passo=\"icamento\"]');"
                             "return f.classList.contains('viva')&&!!f.querySelector('video').getAttribute('src');})()", 3)
        c = ler_clipe(ws, "icamento")
        check(voltou, f"despejado depois de .viva, o clipe ativo recarrega e volta a .viva em ≤ 3 s (estado: {c})")
        # despejo ANTES dos metadados: com a rede a 20 KB/s os metadados demoram ~1,7 s; o src já está atribuído e readyState ainda é 0
        # o salto até o içamento às vezes carrega a casa de passagem (e a FOLGA a mantém): longe dela primeiro, e sem cache, para os dados não voltarem de graça
        rolar_ate(ws, "zip", 0.5)
        check(esperar(ws, "!document.querySelector('figure.clipe[data-passo=\"casa\"] video').getAttribute('src')", 3), "a casa descarrega antes do despejo com rede lenta")
        ws.comando("Network.enable")
        ws.comando("Network.setCacheDisabled", cacheDisabled=True)
        # 20 KB/s: o Chromium só demuxa depois de completar blocos de 32 KB, por isso readyState fica 0 por ~1,7 s mesmo com o moov de ~2 KB — não "corrigir" a taxa para cima
        ws.comando("Network.emulateNetworkConditions", offline=False, latency=0, downloadThroughput=20480, uploadThroughput=-1)
        rolar_ate(ws, "casa", 0.4)
        esperar(ws, "!!document.querySelector('figure.clipe[data-passo=\"casa\"] video').getAttribute('src')", 5)
        antes = ler_clipe(ws, "casa")
        check(antes["src"] is not None and antes["ready"] == 0, f"o despejo tem de acontecer antes dos metadados (src {antes['src']!r}, readyState {antes['ready']})")
        # o WebKit esvazia sem tirar o src: o mesmo src reatribuído com preload='none' esvazia o elemento e não baixa nada sozinho
        ws.avaliar("(function(){var v=document.querySelector('figure.clipe[data-passo=\"casa\"] video');v.preload='none';v.setAttribute('src',v.getAttribute('src'));})()")
        ws.comando("Network.emulateNetworkConditions", offline=False, latency=0, downloadThroughput=-1, uploadThroughput=-1)
        voltou = esperar(ws, "document.querySelector('figure.clipe[data-passo=\"casa\"]').classList.contains('viva')", 5)
        check(voltou, f"despejado antes dos metadados, o clipe ativo recarrega e chega a .viva em ≤ 5 s (estado: {ler_clipe(ws, 'casa')})")
        e = ler_clipes(ws)
        check(len(e["comDados"]) <= 2 and e["erros"] == [], f"depois dos despejos: ≤ 2 vídeos com dados ({e['comDados']}) e console limpo ({e['erros']})")


def checar_dados():
    """Economia de dados e rede lenta (F-10): o modo cenas fica, mas nenhum clipe baixa; em 3g baixa."""
    for conexao, baixa in (("{saveData:true,effectiveType:'4g'}", False), ("{saveData:false,effectiveType:'2g'}", False),
                           ("{saveData:false,effectiveType:'3g'}", True)):
        with chromium(390, altura=844) as ws:
            ws.comando("Page.enable")
            ws.comando("Page.addScriptToEvaluateOnNewDocument",
                       source=ESPIAO + f"Object.defineProperty(navigator,'connection',{{value:{conexao},configurable:true}});")
            navegar(ws)
            rolar_ate(ws, "icamento", 0.4)
            if baixa:
                esperar(ws, "performance.getEntriesByType('resource').some(function(e){return /\\.mp4/.test(e.name);})", 10)
            else:
                time.sleep(3)
            c, e = ler_clipe(ws, "icamento"), ler_clipes(ws)
            check(e["jsHistoria"], f"navigator.connection={conexao}: o modo cenas continua (js-historia={e['jsHistoria']})")
            check((e["mp4"] > 0) == baixa, f"navigator.connection={conexao}: esperava {'algum' if baixa else 'nenhum'} .mp4, achei {e['mp4']}")
            if not baixa:
                check(c["img"] == "visible" and not c["viva"], f"navigator.connection={conexao}: fica o pôster (estado: {c})")


def checar_foco():
    """Tab a partir de "Pular para o texto", 60 vezes (F-11): o foco nunca entra no palco nem num <video>, mesmo com clipe carregado."""
    with chromium(390, altura=844) as ws:
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        check(esperar(ws, "document.querySelector('figure.clipe[data-passo=\"icamento\"]').classList.contains('viva')", 25), "içamento .viva antes do Tab (o teste vale com clipe carregado)")
        ws.avaliar("document.querySelector('a.pular').focus({preventScroll:true})")
        caminho = []
        for _ in range(60):
            for tipo in ("keyDown", "keyUp"):
                ws.comando("Input.dispatchKeyEvent", type=tipo, key="Tab", code="Tab", windowsVirtualKeyCode=9, nativeVirtualKeyCode=9)
            # os links da régua e dos casos não têm classe nem id: o href (até 40 caracteres) os distingue
            caminho.append(ws.avaliar("(function(){var e=document.activeElement;return (e.closest&&e.closest('.palco')?'PALCO ':'')+e.tagName+"
                                      "(e.classList&&e.classList.length?'.'+e.classList[0]:'')+(e.id?'#'+e.id:'')+"
                                      "(e.getAttribute('href')?' '+e.getAttribute('href').slice(0,40):'');})()"))
        check(len(set(caminho)) >= 10, f"o Tab do DevTools tem de percorrer a página (foco só em {sorted(set(caminho))})")
        errados = [x for x in caminho if x.startswith("PALCO") or x.startswith("VIDEO")]
        check(not errados, f"o foco entrou no palco ou num vídeo: {errados}")


def checar_layout():
    """Composição (F-13): em tela larga a faixa de texto termina antes de 54 % da largura; no celular a faixa de cada capítulo
    curto deixa clipe à mostra; o comprimento da história (#historia) é o da linha de base."""
    base = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else None
    check(base is not None, "tests/baseline.json não existe (python3 portfolio/tests/check_historia.py --gravar-baseline, antes da mudança)")
    for largura, altura in ((1366, 768), (1920, 1080)):
        with chromium(largura, altura=altura) as ws:
            navegar(ws)
            for passo in ("sige", "zip"):
                rolar_ate(ws, passo, 0.5)
                time.sleep(0.8)
                topo = json.loads(ws.avaliar("JSON.stringify((function(){var b=document.querySelector('.barra').getBoundingClientRect(),"
                                             "f=document.querySelector('.palco figure.ativo').getBoundingClientRect();return {barra:b.bottom,fundo:f.top};})())"))
                check(abs(topo["fundo"] - topo["barra"]) <= 1, f"{largura}×{altura}: o fundo ativo começa em {topo['fundo']:.1f} px, e o pé da barra está em {topo['barra']:.1f} px (têm de coincidir: nem vão nem sobreposição)")
                r = json.loads(ws.avaliar(f"JSON.stringify((function(){{var r=document.querySelector('#{passo} .texto').getBoundingClientRect();return {{w:r.width,direita:r.right/innerWidth}};}})())"))
                check(r["w"] > 0 and r["direita"] <= 0.54, f"{largura}×{altura}: a faixa de texto de {passo} termina em {r['direita']:.2f} da largura (máx. 0,54; largura {r['w']:.0f})")
    curtos = [c["passo"] for c in ROTEIRO if c["fundo"] and c["fundo"][0] == "clipe" and c["passo"] not in LONGAS]
    with chromium(390, altura=844) as ws:
        navegar(ws)
        vao = json.loads(ws.avaliar("JSON.stringify((function(){var b=document.querySelector('.barra').getBoundingClientRect(),"
                                    "f=document.querySelector('.palco figure.ativo').getBoundingClientRect();return {barra:b.bottom,fundo:f.top,scroll:scrollY};})())"))
        check(vao["scroll"] == 0 and abs(vao["fundo"] - vao["barra"]) <= 1,
              f"390×844 em scrollY=0: o fundo da tese tem de encostar no pé da barra (barra {vao['barra']:.1f}, fundo {vao['fundo']:.1f}, scrollY {vao['scroll']}): sem vão, sem sobreposição")
        for passo in curtos:
            rolar_ate(ws, passo, 0.5)
            time.sleep(0.5)
            topo = json.loads(ws.avaliar("JSON.stringify((function(){var b=document.querySelector('.barra').getBoundingClientRect(),"
                                         "f=document.querySelector('.palco figure.ativo').getBoundingClientRect();return {barra:b.bottom,fundo:f.top};})())"))
            check(abs(topo["fundo"] - topo["barra"]) <= 1, f"390×844 em {passo}: o fundo começa em {topo['fundo']:.1f} px, e o pé da barra está em {topo['barra']:.1f} px (têm de coincidir)")
            r = json.loads(ws.avaliar(f"JSON.stringify((function(){{var r=document.querySelector('#{passo} .texto').getBoundingClientRect();"
                                      f"return {{w:r.width,h:r.height/innerHeight,cima:r.top/innerHeight,baixo:1-r.bottom/innerHeight}};}})())"))
            check(r["w"] > 0 and r["h"] <= 0.75, f"390×844: a faixa de {passo} ocupa {r['h']:.0%} da altura (máx. 75 %)")
            check(max(r["cima"], r["baixo"]) >= 0.1, f"390×844: a faixa de {passo} não deixa 10 % de clipe à mostra acima ou abaixo ({r})")
    with chromium(700, altura=900) as ws:  # as fontes web chegam depois da primeira medida, e a barra quebra em mais linhas ao estreitar: --barra acompanha
        navegar(ws)
        MEDIDA = ("JSON.stringify({barra:document.querySelector('.barra').getBoundingClientRect().height,"
                  "var:parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--barra'))})")
        m = json.loads(ws.avaliar(MEDIDA))
        check(abs(m["barra"] - m["var"]) <= 1, f"700 px, depois do load (fontes já trocadas): --barra ({m['var']}) ≠ altura da barra ({m['barra']:.2f})")
        ws.comando("Emulation.setDeviceMetricsOverride", width=500, height=900, deviceScaleFactor=1, mobile=False)
        time.sleep(0.6)
        m = json.loads(ws.avaliar(MEDIDA))
        check(abs(m["barra"] - m["var"]) <= 1, f"depois de estreitar a janela para 500 px, --barra ({m['var']}) ≠ altura da barra ({m['barra']:.2f})")
    with chromium(2560, altura=1080) as ws:  # 21:9: o palco recorta ~40 % da altura do 16:9; o foco por clipe mantém o assunto
        navegar(ws)
        for passo, esperado in (("obra", "68% 0%"), ("escala", "68% 50%"), ("sige", "68% 50%")):
            rolar_ate(ws, passo, 0.5)
            time.sleep(0.5)
            pos = ws.avaliar(f"getComputedStyle(document.querySelector('figure.clipe[data-passo=\"{passo}\"] video')).objectPosition")
            check(pos == esperado, f"2560×1080: object-position de {passo} é {pos!r}, esperava {esperado!r}")
    with chromium(844, altura=390) as ws:  # celular deitado
        navegar(ws)
        for passo in ("sige", "icamento"):
            rolar_ate(ws, passo, 0.5)
            time.sleep(0.8)
            r = json.loads(ws.avaliar(f"JSON.stringify((function(){{var r=document.querySelector('#{passo} .texto').getBoundingClientRect();"
                                      f"return {{w:r.width,direita:r.right/innerWidth,h:r.height/innerHeight}};}})())"))
            check(r["w"] > 0 and r["direita"] <= 0.62, f"844×390: a faixa de {passo} termina em {r['direita']:.2f} da largura (máx. 0,62; largura {r['w']:.0f})")
            check(r["h"] <= 0.92, f"844×390: a faixa de {passo} ocupa {r['h']:.0%} da altura (máx. 92 %)")
    alturas = {}
    for largura in (390, 1280):
        with chromium(largura) as ws:  # a altura padrão (800) é a da linha de base
            navegar(ws)
            alturas[str(largura)] = ws.avaliar("document.getElementById('historia').offsetHeight")
    if base:
        for largura, altura in alturas.items():
            check(abs(altura - base["alturaMain"][largura]) <= 2, f"{largura} px: #historia mede {altura} px, linha de base {base['alturaMain'][largura]} (± 2)")


def checar_desempenho():
    """Desempenho (F-17): LCP é a foto da tese ou o H1, nunca um vídeo; CLS ≤ 0,01; TaskDuration de uma rolagem completa
    ≤ 2× a linha de base gravada antes da mudança (mesmas flags: a base tinha as maquetes WebGL por SwiftShader)."""
    base = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else None
    with chromium(390, ("--enable-unsafe-swiftshader",)) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        time.sleep(1.5)
        tarefa = medir_desempenho(ws)
        time.sleep(1)
        lcp, cls = ws.avaliar("window.__lcp"), ws.avaliar("window.__cls")
    check(lcp.startswith("H1") or (lcp.startswith("IMG") and lcp.endswith("o-quantitativos.webp")),
          f"o LCP é a foto da tese ou o H1, nunca um vídeo (achei {lcp!r})")
    check(cls <= 0.01, f"CLS da história: {cls} (máx. 0,01)")
    if base:
        check(tarefa <= 2 * base["taskDuration"], f"TaskDuration da rolagem completa: {tarefa:.2f} s, linha de base {base['taskDuration']} s (máx. 2×)")


def checar_sem_trailer(pagina):
    """O trailer saiu da página (F-14): nada aponta para ele; o convite tem 3 botões."""
    for trecho in ('class="filme"', 'id="filme"', 'href="#filme"', "transcricao", "Assistir ao filme", "A história em 85 segundos",
                   "Transcrição do filme", "historia.mp4", "historia.jpg"):
        check(trecho not in pagina, f"o trailer saiu da página: ainda há {trecho!r}")
    ultima = cenas(pagina)[-1][3] if cenas(pagina) else ""
    check(ultima.count('<a class="btn') == 3, "o convite tem exatamente 3 botões")
    check(not (SITE / "video" / "historia.mp4").exists() and not (SITE / "video" / "historia.jpg").exists(), "site/video/historia.* saem do site")


NOTA = ('<p class="nota">As cenas ao fundo da história são dioramas em 3D feitos para este portfólio; '
        'as telas e fotos reais estão no portfólio completo.</p>')


def checar_nota(pagina):
    ficha = re.search(r'<section class="ficha"[^>]*>(.*?)</section>', pagina, re.S)
    check(ficha is not None and NOTA in ficha.group(1) and ficha.group(1).index(NOTA) > ficha.group(1).index("faltam 3 · CLT ou PJ"),
          "a linha de crédito dos dioramas fica na ficha, depois de \"Engenharia Civil, 7º semestre…\"")


def checar_origem(url):
    """Na origem publicada, cada clipe tem de responder 206 a um Range (sem isso a página cai no pôster, por construção)."""
    for passo in CLIPES:
        req = urllib.request.Request(f"{url.rstrip('/')}/video/cena-{passo}.mp4", headers={"Range": "bytes=0-99"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                check(r.status == 206 and "Content-Range" in r.headers, f"{url}: cena-{passo}.mp4 respondeu {r.status} a Range (esperava 206)")
        except OSError as e:
            check(False, f"{url}: cena-{passo}.mp4 não respondeu ({e})")


def main():
    if "--gravar-baseline" in sys.argv:
        gravar_baseline()
        return
    check(PAGINA.exists(), "portfolio/site/index.html (a história) não existe")
    if PAGINA.exists():
        pagina = PAGINA.read_text(encoding="utf-8")
        portfolio = PORTFOLIO.read_text(encoding="utf-8")
        checar_marcacao(pagina, portfolio)
        checar_texto(pagina, portfolio)
        checar_css(pagina)
        checar_scripts(pagina)
        checar_curriculo(pagina)
        checar_regua(pagina)
        checar_sem_trailer(pagina)
        checar_nota(pagina)
        checar_js()
        checar_clipes_js()
        checar_maquetes_js()
        checar_readme()
        checar_servidor()
        if "--navegador" in sys.argv:
            checar_navegador()
            checar_ficha_a_vista()
            checar_clipe_real()
            checar_reduzido_real()
            checar_evicao()
            checar_dados()
            checar_foco()
            checar_layout()
            checar_desempenho()
    if "--origem" in sys.argv:
        i = sys.argv.index("--origem") + 1
        if i >= len(sys.argv) or sys.argv[i].startswith("--"):
            sys.exit("--origem pede a URL da origem publicada, por exemplo: --origem https://exemplo.com")
        checar_origem(sys.argv[i])
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
