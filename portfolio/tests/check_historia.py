#!/usr/bin/env python3
"""Checagens da página principal, site/index.html (a história na linha do tempo).

Estático: roteiro exato dos 17 capítulos, datas e ordem cronológica, ressalvas,
números (só os que o portfólio, site/portfolio.html, já sustenta), links para o
caso completo, marcação acessível e CSS. Com --navegador: o Chromium headless
abre tests/historia_teste.html em tempo real e confere a troca de cenas.
Uso: python3 portfolio/tests/check_historia.py [--navegador]
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
SITE = ROOT / "site"
PAGINA = SITE / "index.html"
PORTFOLIO = SITE / "portfolio.html"
FALHAS = []


def cap(passo, tag, data, frase, ressalva, fundo, caso):
    """data: None ou (texto visível, [datetime, ...]); fundo: None, ("img", arquivo, largura, altura),
    ("ano", texto) ou ("maquete", cena 3D, arquivo reserva, largura, altura); caso: None ou (âncora, texto do link)."""
    return {"passo": passo, "tag": tag, "data": data, "frase": frase, "ressalva": ressalva, "fundo": fundo, "caso": caso}


ROTEIRO = [
    cap("tese", "h1", None,
        "Um número sem origem custa caro na obra.",
        "Cássio Viller, estudante de Engenharia Civil (7º semestre), mira orçamento, planejamento e custos.",
        ("img", "o-quantitativos.webp", 1040, 1000), None),
    cap("origem", "h2", ("2017 → 2024", ["2017", "2024"]),
        "Comecei pela contabilidade, não pela obra.",
        "Escritório contábil da família desde 2017; na UNIFEI, fiscal do DCE em 2022 e diretor de vendas da InLoco Jr. de 2023 a 2024.",
        ("ano", "2017"), ("curriculo", "Ver no currículo: contabilidade e UNIFEI →")),
    cap("mudanca", "h2", ("2025", ["2025"]),
        "Em 2025, mudei de cidade e de curso.",
        "Cruzeiro do Sul (EAD), morando em São José dos Campos: hoje no 7º semestre, faltam 3. Sistemas de Informação na PUC, em paralelo.",
        ("ano", "2025"), ("curriculo", "Ver no currículo: formação →")),
    cap("obra", "h2", ("fev/2025 → mar/2026", ["2025-02", "2026-03"]),
        "Mas na obra, vi a mesma informação digitada cinco vezes.",
        "V Alves (gerente de produção, CLT meio período) e Estruturas do Vale (estágio, meio período), em paralelo. No estágio nasceu o SIGE.",
        ("ano", "5×"), ("curriculo", "Ver no currículo: V Alves e Estruturas do Vale →")),
    cap("veks", "h2", ("mar/2026 → set/2026", ["2026-03", "2026-09"]),
        "Em março de 2026, entrei na VEKS Engenharia.",
        "PJ, contrato de 6 meses cumprido até o fim; a V Alves, em meio período, seguiu até julho.",
        ("ano", "2026"), ("obra", "Ver o caso completo: obras na VEKS →")),
    cap("ferramentas", "h2", ("mar → abr/2026", ["2026-03", "2026-04"]),
        "Toda conta repetida virou ferramenta.",
        "Nos primeiros meses na VEKS: a calculadora de parede em LSF e drywall e o classificador do fluxo de caixa.",
        ("ano", "3ª"), ("ferramentas", "Ver as ferramentas: calculadora e classificador →")),
    cap("sige", "h2", ("mai → set/2026", ["2026-05", "2026-09"]),
        "De maio a setembro, o SIGE ganhou versão nova.",
        "Cerca de 50 módulos em 6 áreas, entregas registradas de 22/07 a 14/09/2026; código escrito com assistente de IA, sob a minha direção.",
        ("img", "c-aprovacao.webp", 1100, 467), ("sige", "Ver o caso completo: SIGE →")),
    cap("galpoes", "h2", ("jun/2026", ["2026-06-08"]),
        "Em junho, começou a obra que testaria o SIGE.",
        "Dois galpões e 22 baias numa fazenda, em Light Steel Frame: a obra real do portal do cliente e do diário.",
        ("ano", "22 baias"), ("obra", "Ver o caso completo: galpões e baias →")),
    cap("escala", "h2", ("jul → set/2026", ["2026-07-09", "2026-09-21"]),
        "13 obras no sistema, até R$ 24,5 milhões.",
        "11 com proposta; a menor, R$ 29 mil. A gestão de obra deste sistema ainda não rodou numa obra real.",
        ("img", "s1.webp", 1000, 728), ("sistema", "Ver o caso completo: sistema de orçamento →")),
    cap("precisao", "h2", ("jul → set/2026", ["2026-07-09", "2026-09-21"]),
        "Desvio máximo de 0,25% nos 19 serviços conferidos.",
        "Serviço a serviço, contra a tabela SINAPI da Caixa; acima de 1% de desvio, a importação é recusada.",
        ("img", "o-orcamento.webp", 1040, 1080), ("sistema", "Ver o caso completo: conferência SINAPI →")),
    cap("casa", "h2", ("ago/2026", ["2026-08"]),
        "O celeiro não cabe inteiro no caminhão.",
        "B-36, pré-dimensionado e sujeito à revisão do engenheiro responsável: duas caixas, três viagens, 37 decisões registradas.",
        ("maquete", "casa-viaja", "m1.webp", 900, 562), ("modular", "Ver o caso completo: celeiro B-36 →")),
    cap("icamento", "h2", ("ago/2026", ["2026-08"]),
        "No estudo, o módulo sobe pelo balancim, cabos na vertical.",
        "Estudo 3D de agosto: com os cabos na vertical, a parede não é comprimida. Balancim de içamento e guindaste da classe certa viraram itens de regra no orçamento.",
        ("maquete", "icamento", "m2.webp", 900, 562), ("modular", "Ver o caso completo: casas modulares →")),
    cap("whatsapp", "h2", ("ago/2026", ["2026-08-11"]),
        "Depois de 11/08, o diário saiu do sistema.",
        "42 diários lançados até ali; os 23 dias seguintes ficaram só no grupo de WhatsApp, e 28 atividades prontas apareciam como atrasadas.",
        ("img", "p-fotos.webp", 1600, 1353), ("sige", "Ver o caso completo: o diário no WhatsApp →")),
    cap("recuperado", "h2", ("set/2026", ["2026-09"]),
        "Recuperado, o diário mostrou 44,7% de avanço.",
        "Antes, 27,6%; planejado para 07/09, 60,8%. Lido numa cópia do sistema; no sistema em uso, a carga ainda não foi aplicada.",
        ("img", "p-diario-portal.webp", 1600, 1193), ("sige", "Ver o caso completo: diários recuperados →")),
    cap("zip", "h2", ("set/2026", ["2026-09"]),
        "Em setembro, uma proposta assinável em 36 minutos.",
        "Medidos: 11:35 → 12:11, numa ampliação de unidade de saúde com 26 ambientes e 328 m². À mão, cerca de 2 dias úteis (estimativa).",
        ("maquete", "36min", "upa-plan-grey.webp", 1400, 440), ("orcamento", "Ver o caso completo: 36 minutos →")),
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
    classe = {"img": "fundo", "ano": "fundo tipo", "maquete": "fundo maquete"}[tipo]
    check(fa.get("class") == classe, f"cena {passo}: classe da figura {fa.get('class')!r}, esperava {classe!r}")
    check(fa.get("aria-hidden") == "true", f"cena {passo}: figura de fundo sem aria-hidden=\"true\"")
    check(fa.get("data-passo") == passo, f"cena {passo}: figura com data-passo {fa.get('data-passo')!r}")
    check(fa.get("data-cena") == (fundo[1] if tipo == "maquete" else None), f"cena {passo}: data-cena {fa.get('data-cena')!r}")
    check(not re.search(r"<(a|button|input|select|textarea)\b", fmiolo), f"cena {passo}: nada focável dentro da figura aria-hidden")
    if tipo == "ano":
        check(f'<span class="ano">{fundo[1]}</span>' in fmiolo and "<img" not in fmiolo,
              f"cena {passo}: fundo tipográfico deve ser só <span class=\"ano\">{fundo[1]}</span>")
        return
    arquivo, largura, altura = (fundo[1], fundo[2], fundo[3]) if tipo == "img" else (fundo[2], fundo[3], fundo[4])
    imgs = re.findall(r"<img ([^>]*)>", fmiolo)
    check(len(imgs) == 1, f"cena {passo}: esperava 1 <img> na figura")
    if imgs:
        ia = atributos(imgs[0])
        check(ia.get("src") == f"img/{arquivo}", f"cena {passo}: imagem {ia.get('src')!r}, esperava img/{arquivo}")
        check((SITE / "img" / arquivo).exists(), f"cena {passo}: img/{arquivo} não existe")
        check(ia.get("alt") == "", f"cena {passo}: imagem decorativa precisa de alt=\"\"")
        check(ia.get("width") == str(largura) and ia.get("height") == str(altura), f"cena {passo}: width/height devem ser {largura}×{altura}")
        if i == 1:
            check(ia.get("fetchpriority") == "high" and "loading" not in ia, "cena 1: imagem com fetchpriority=\"high\" e sem loading")
        else:
            check(ia.get("loading") == "lazy" and "fetchpriority" not in ia, f"cena {passo}: imagem com loading=\"lazy\" e sem fetchpriority")
    if tipo == "maquete":
        check("<canvas></canvas>" in fmiolo, f"cena {passo}: maquete sem <canvas>")
        check("<b data-relogio></b>" in fmiolo and "<span data-legenda></span>" in fmiolo, f"cena {passo}: maquete sem HUD")


def checar_marcacao(pagina, portfolio):
    cs = cenas(pagina)
    check(len(cs) == len(ROTEIRO), f"esperava {len(ROTEIRO)} cenas, achei {len(cs)}")
    ancoras = set(re.findall(r'\bid="([^"]+)"', portfolio))
    nomes_caso = {}
    for i, (c, achado) in enumerate(zip(ROTEIRO, cs), start=1):
        classes, ident, passo_html, miolo = achado
        passo = c["passo"]
        check(ident == passo and passo_html == passo, f"cena {i}: id/data-passo {ident!r}/{passo_html!r}, esperava {passo!r}")
        longa = c["fundo"] is not None and c["fundo"][0] == "maquete"
        check((classes == "cena longa") == longa, f"cena {passo}: a classe 'longa' vai só nas cenas de maquete")
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


def checar_css(pagina):
    css = "\n".join(re.findall(r"<style>(.*?)</style>", pagina, re.S))
    check("dvh" not in css, "não usar dvh: a altura pula com a barra do Safari")
    for n in ("100", "200"):
        check(css.count(f"{n}svh") > 0 and css.count(f"{n}vh") >= css.count(f"{n}svh"),
              f"cada {n}svh precisa de um {n}vh antes, como fallback")
    check(".palco{display:none}" in css, "o palco precisa começar escondido (modo empilhado)")
    check(".js-historia .historia{max-width:none;padding:0;position:relative;background:var(--tinta)}" in css,
          "no modo cenas o fundo da história é tinta: sem faixa clara quando a barra do navegador recolhe (svh < lvh)")
    check(".fundo .pausa{display:none!important}" in css, "o botão de pausa da maquete não pode ficar focável dentro do fundo aria-hidden")
    check(".cena{scroll-margin-top:9rem}" in css, "o título do capítulo não pode ficar atrás da barra ao chegar por salto")
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
          "relógio da maquete (texto grande, negrito) sobre a faixa: mínimo 3:1 no pior caso")
    check(re.search(r"\.hud b\{[^}]*background:var\(--scrim\)", css) is not None, "o relógio da maquete fica sobre a faixa escura")
    check(".js-historia .palco .hud b:empty{display:none}" in css, "sem número no relógio (içamento), a faixa do relógio some")


def checar_scripts(pagina):
    tags = re.findall(r"<script ([^>]*)></script>", pagina)
    nomes = [atributos(t).get("src") for t in tags]
    check(nomes == ["maquetes.js", "historia.js"], f"scripts devem ser maquetes.js e historia.js, nessa ordem; achei {nomes}")
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


def checar_js():
    caminho = SITE / "historia.js"
    check(caminho.exists(), "portfolio/site/historia.js não existe")
    if not caminho.exists():
        return
    js = re.sub(r"//[^\n]*", "", caminho.read_text(encoding="utf-8"))  # comentários não contam
    for proibido in ("scrollTo", "scrollBy", "scrollIntoView", "preventDefault", "'wheel'", "'touchmove'", "aria-live"):
        check(proibido not in js, f"historia.js não pode usar {proibido}")
    check("fps" not in js.lower() and "matar" not in js, "historia.js não duplica a guarda de desempenho do maquetes.js")


def checar_maquetes_js():
    js = (SITE / "maquetes.js").read_text(encoding="utf-8")
    check("dur:sc.dur" in js, "maquetes.js precisa expor a duração da cena em fig.__maquete.dur")
    comprimento = re.search(r"function cenaIcamento\(fig\)\{.*?var DUR=16,L=([\d.]+)", js, re.S)
    check(comprimento is not None and float(comprimento.group(1)) <= 8,
          "módulo do içamento com no máximo 8 m: acima disso o estudo pede pontos intermediários, e a maquete só tem 4 olhais")
    check("'icamento':cenaIcamento" in js, "maquetes.js precisa registrar a cena 3D do içamento em CENAS")


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
def chromium(largura, extra=()):
    """Servidor estático em portfolio/ + Chromium headless em tempo real, controlado pelo DevTools Protocol.
    Não usar --virtual-time-budget: nele quase não há quadros, e sem quadros nem o IntersectionObserver nem o scroll disparam."""
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORTA), "--bind", "127.0.0.1", "--directory", str(ROOT)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    nav = subprocess.Popen(["chromium", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                            f"--window-size={largura},800", f"--remote-debugging-port={PORTA_CDP}", *extra, "about:blank"],
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
        # o headless impõe janela mínima de ~500×657; o override garante exatamente largura × 800
        ws.comando("Emulation.setDeviceMetricsOverride", width=largura, height=800, deviceScaleFactor=1, mobile=False)
        yield ws
    finally:
        nav.terminate()
        nav.wait()
        srv.terminate()
        srv.wait()


def navegador(largura=390, extra=("--disable-3d-apis",)):
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
    maquetes = [c["passo"] for c in ROTEIRO if c["fundo"] and c["fundo"][0] == "maquete"]
    normal = navegador(390)
    check("FIM" in normal, f"390 px: o harness não terminou — últimas linhas {normal[-3:]}")
    for linha in ("reduzido=false", "js-historia=true", "overflow-x=false", "inicio ativa=tese", "salto ativa=tese maquetes=-",
                  "reversao-48 ativa=casa", "reversao-95 ativa=precisao"):
        check(linha in normal, f"390 px: faltou {linha!r}")
    for c in ROTEIRO:
        passo = c["passo"]
        fundo = passo if c["fundo"] else "nenhum"
        maq = passo if passo in maquetes else "-"
        esperado = f"cena {passo} ativa={passo} fundo={fundo} maquetes={maq}"
        check(esperado in normal, f"390 px: esperava {esperado!r}")
        inicio = c["data"][0].split("→")[0].strip() if c["data"] else ""
        rotulo = (inicio if re.search(r"\d", inicio) else inicio + "/" + c["data"][0].split("/")[-1].strip()) if c["data"] else "2017–2026"
        check(f"regua {passo}=#{passo} n=1 data={rotulo}" in normal,
              f"390 px: na cena {passo}, o marco ativo da régua deve ser #{passo} (e só ele), com a data {rotulo!r} à direita")
        if passo in maquetes:
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
          "three.js que chega depois da rolagem: a maquete precisa ser sincronizada (e congelada), sem limite de tentativas")
    check("progresso=0 0.5 1 0" in normal, "Historia.progresso fora do esperado (0 no topo, 0,5 no meio, 1 no fim, 0 sem altura)")
    for passo in maquetes:
        for chave, alvo in (("seek", 500), ("seek25", 250)):
            m = re.search(rf"^{chave} {passo}=([\d.]+)$", texto_normal, re.M)
            check(m is not None and abs(float(m.group(1)) - alvo) <= 20,
                  f"{chave} {passo}: esperava ≈{alvo} (dur 1000), achei {m.group(1) if m else 'nada'}")


def checar_maquete_real():
    """Com WebGL de verdade (SwiftShader): a cena do içamento monta sem erro, expõe a API e segue o scroll."""
    espiao = ("window.__erros=[];addEventListener('error',function(e){__erros.push(String(e.message));});"
              "var avisar=console.warn;console.warn=function(){var m=String(arguments[0]);"
              "if(/^maquete|three\\.js/.test(m))__erros.push(m+' '+String(arguments[1]));return avisar.apply(console,arguments);};")
    ler = ("JSON.stringify((function(){var f=document.querySelector('figure[data-cena=\"icamento\"]'),a=f&&f.__maquete;"
           "return {api:!!a&&typeof a.frozen==='boolean',dur:a?a.dur:null,congelada:!!a&&a.frozen===true,erros:window.__erros};})())")
    estado = {}
    with chromium(390, ("--enable-unsafe-swiftshader",)) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=espiao)
        ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/site/index.html")
        time.sleep(2)
        ws.avaliar("(function(){var r=document.getElementById('icamento').getBoundingClientRect();"
                   "window.scrollTo(0,scrollY+r.top+r.height*.4-innerHeight/2);})()")
        prazo = time.time() + 25
        while time.time() < prazo:
            estado = json.loads(ws.avaliar(ler) or "{}")
            if estado.get("congelada") or estado.get("erros"):
                break
            time.sleep(0.5)
    check(estado.get("api") is True, f"com WebGL, a maquete do içamento precisa montar e expor a API (estado: {estado})")
    check(estado.get("dur") == 16, f"a cena do içamento dura 16 s (achei {estado.get('dur')})")
    check(estado.get("congelada") is True, "a maquete do içamento segue o scroll (seek congela o tempo)")
    check(not estado.get("erros"), f"erros ao montar a maquete: {estado.get('erros')}")


def main():
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
        checar_js()
        checar_maquetes_js()
        if "--navegador" in sys.argv:
            checar_navegador()
            checar_maquete_real()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
