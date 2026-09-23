#!/usr/bin/env python3
"""Checagens da página historia.html (a história em cenas).

Estático: roteiro exato, ressalvas, números (só os que o index.html já sustenta),
marcação acessível e CSS. Com --navegador (a partir da Task 2): o Chromium headless
abre tests/historia_teste.html e confere a troca de cenas.
Uso: python3 portfolio/tests/check_historia.py [--navegador]
"""
import html
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # portfolio/
SITE = ROOT / "site"
PAGINA = SITE / "historia.html"
FALHAS = []

# (passo, tag da frase, frase, ressalva, imagem de fundo, largura, altura, cena 3D do maquetes.js)
ROTEIRO = [
    ("tese", "h1", "Um número sem origem custa caro na obra.",
     "Cássio Viller, estudante de Engenharia Civil (7º semestre), mira orçamento, planejamento e custos.",
     "o-quantitativos.webp", 1040, 1000, None),
    ("origem", "h2", "Comecei no centavo, não na parede.",
     "Folha, notas e balancete no escritório da família, desde 2017.",
     None, 0, 0, None),
    ("obra", "h2", "Mas na obra, vi a mesma informação digitada cinco vezes.",
     "VEKS Engenharia, V Alves e Estruturas do Vale, entre 2025 e 2026.",
     "p-fotos.webp", 1600, 1353, None),
    ("zip", "h2", "Do zip à proposta assinável em 36 minutos.",
     "Medidos: 11:35 → 12:11, numa ampliação de unidade de saúde com 26 ambientes e 328 m². À mão, cerca de 2 dias úteis (estimativa).",
     "upa-plan-grey.webp", 1400, 440, "36min"),
    ("escala", "h2", "13 obras no sistema, até R$ 24,5 milhões.",
     "11 com proposta; a menor, R$ 29 mil. A gestão de obra deste sistema ainda não rodou numa obra real.",
     "s1.webp", 1000, 728, None),
    ("precisao", "h2", "Desvio máximo de 0,25% nos 19 serviços conferidos.",
     "Serviço a serviço, contra a tabela SINAPI da Caixa; acima de 1% de desvio, a importação é recusada.",
     "o-orcamento.webp", 1040, 1080, None),
    ("sige", "h2", "Numa obra real, 23 diários estavam só no WhatsApp.",
     "No SIGE, que concebi: recuperados, levam a obra de 27,6% para 44,7% concluído, contra 60,8% planejado — lido numa cópia do sistema.",
     "p-diario-portal.webp", 1600, 1193, None),
    ("casa", "h2", "O celeiro não cabe inteiro no caminhão.",
     "B-36: vai em duas caixas, em três viagens, com 37 decisões registradas.",
     "m1.webp", 900, 562, "casa-viaja"),
    ("metodo", "h2", "Construí o jeito de o número não sumir.",
     "Idealizei e dirigi os sistemas; o código foi escrito com assistentes de IA, e as regras, os testes e a revisão são meus.",
     "o-proposta.webp", 885, 1060, None),
    ("convite", "h2", "Faltam 3 semestres para o diploma. Não falta obra feita.",
     "Você me manda o pacote do projeto; eu devolvo levantamento, orçamento com faixa e proposta no seu modelo.",
     None, 0, 0, None),
]

RESSALVAS = ["estimativa", "ainda não rodou", "nos 19 serviços conferidos", "cópia do sistema", "assistentes de IA"]
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


def atributos(tag):
    return dict(re.findall(r'([\w-]+)="([^"]*)"', tag))


def cenas(pagina):
    """(classes, id, passo, html interno) de cada <section class="cena…">."""
    return re.findall(r'<section class="(cena(?: longa)?)" id="(c\d+)" data-passo="([a-z0-9]+)">(.*?)</section>', pagina, flags=re.S)


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def contraste(a, b):
    la, lb = (0.2126 * _lin(x[0]) + 0.7152 * _lin(x[1]) + 0.0722 * _lin(x[2]) for x in (a, b))
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def checar_marcacao(pagina):
    cs = cenas(pagina)
    check(len(cs) == len(ROTEIRO), f"esperava {len(ROTEIRO)} cenas, achei {len(cs)}")
    for i, (esperado, achado) in enumerate(zip(ROTEIRO, cs), start=1):
        passo, tag, frase, ressalva, imagem, largura, altura, maquete = esperado
        classes, ident, passo_html, miolo = achado
        check(ident == f"c{i}", f"cena {i}: id {ident!r}, esperava 'c{i}'")
        check(passo_html == passo, f"cena {i}: data-passo {passo_html!r}, esperava {passo!r}")
        check((classes == "cena longa") == bool(maquete), f"cena {passo}: a classe 'longa' vai só nas cenas de maquete")
        m = re.search(r'<(h[12]) class="frase">(.*?)</\1>', miolo, re.S)
        check(m is not None and m.group(1) == tag, f"cena {passo}: a frase deve ser <{tag} class=\"frase\">")
        if m:
            check(limpo(m.group(2)) == frase, f"cena {passo}: frase {limpo(m.group(2))!r} ≠ roteiro {frase!r}")
        r = re.search(r'<p class="ressalva">(.*?)</p>', miolo, re.S)
        check(r is not None and limpo(r.group(1)) == ressalva, f"cena {passo}: ressalva diferente do roteiro")
        tx = re.search(r'<div class="texto"([^>]*)>', miolo)
        check(tx is not None and "aria-hidden" not in tx.group(1), f"cena {passo}: <div class=\"texto\"> ausente ou com aria-hidden")
        figs = re.findall(r"<figure ([^>]*)>(.*?)</figure>", miolo, re.S)
        if imagem is None:
            check(not figs, f"cena {passo}: não deveria ter figura de fundo")
            continue
        check(len(figs) == 1, f"cena {passo}: esperava 1 figura de fundo, achei {len(figs)}")
        if not figs:
            continue
        fa, fmiolo = atributos(figs[0][0]), figs[0][1]
        check(fa.get("aria-hidden") == "true", f"cena {passo}: figura de fundo sem aria-hidden=\"true\"")
        check(fa.get("data-passo") == passo, f"cena {passo}: figura com data-passo {fa.get('data-passo')!r}")
        check(fa.get("class") == ("fundo maquete" if maquete else "fundo"), f"cena {passo}: classe da figura {fa.get('class')!r}")
        check(fa.get("data-cena") == maquete, f"cena {passo}: data-cena {fa.get('data-cena')!r}, esperava {maquete!r}")
        check(not re.search(r"<(a|button|input|select|textarea)\b", fmiolo), f"cena {passo}: nada focável dentro da figura aria-hidden")
        imgs = re.findall(r"<img ([^>]*)>", fmiolo)
        check(len(imgs) == 1, f"cena {passo}: esperava 1 <img> na figura")
        if imgs:
            ia = atributos(imgs[0])
            check(ia.get("src") == f"img/{imagem}", f"cena {passo}: imagem {ia.get('src')!r}, esperava img/{imagem}")
            check((SITE / "img" / imagem).exists(), f"cena {passo}: img/{imagem} não existe")
            check(ia.get("alt") == "", f"cena {passo}: imagem decorativa precisa de alt=\"\"")
            check(ia.get("width") == str(largura) and ia.get("height") == str(altura),
                  f"cena {passo}: width/height devem ser {largura}×{altura}")
            if i == 1:
                check(ia.get("fetchpriority") == "high" and "loading" not in ia, "cena 1: imagem com fetchpriority=\"high\" e sem loading")
            else:
                check(ia.get("loading") == "lazy" and "fetchpriority" not in ia, f"cena {passo}: imagem com loading=\"lazy\" e sem fetchpriority")
        if maquete:
            check("<canvas></canvas>" in fmiolo, f"cena {passo}: maquete sem <canvas>")
            check("<b data-relogio></b>" in fmiolo and "<span data-legenda></span>" in fmiolo,
                  f"cena {passo}: maquete sem HUD (data-relogio e data-legenda)")
    check('<main id="historia" class="historia">' in pagina, "falta <main id=\"historia\" class=\"historia\">")
    check('<div class="palco" aria-hidden="true"></div>' in pagina, "falta o palco vazio com aria-hidden")
    primeiro = re.search(r"<a ([^>]*)>", corpo(pagina))
    check(primeiro is not None and 'class="pular"' in primeiro.group(1), "o primeiro link da página deve ser o 'Pular para o texto'")
    barra = re.search(r'<header class="barra">(.*?)</header>', pagina, re.S)
    check(barra is not None, "falta <header class=\"barra\">")
    if barra:
        tb = barra.group(1)
        check("Cássio Viller" in limpo(tb) and "Orçamento, planejamento e custos" in limpo(tb), "barra sem nome ou cargo-alvo")
        check(f'href="{CURRICULO}"' in tb and f'href="{WHATSAPP}' in tb, "barra sem currículo ou WhatsApp")
    ultima = cs[-1][3] if cs else ""
    for alvo in (WHATSAPP, "index.html", CURRICULO):
        check(f'href="{alvo}' in ultima, f"cena final sem link para {alvo}")
    ficha = re.search(r'<section class="ficha"[^>]*>(.*?)</section>', pagina, re.S)
    check(ficha is not None, "falta a ficha (<section class=\"ficha\">)")
    if ficha:
        for p in PALAVRAS_CHAVE:
            check(p in limpo(ficha.group(1)), f"ficha sem a palavra-chave {p!r}")


def checar_texto(pagina, index):
    for passo, _tag, frase, ressalva, *_resto in ROTEIRO:
        check(len(frase.split()) <= 10, f"cena {passo}: frase com {len(frase.split())} palavras (máx. 10)")
        check(0 < len(ressalva.split()) <= 30, f"cena {passo}: ressalva com {len(ressalva.split())} palavras (1 a 30)")
    t = limpo(corpo(pagina))
    extras = numeros(t) - numeros(limpo(corpo(index)))
    check(not extras, f"números que o index.html não sustenta: {sorted(extras)}")
    for r in RESSALVAS:
        check(r in t, f"ressalva ausente: {r!r}")
    check(t.lower().count("você") == 1, "\"você\" deve aparecer uma vez só, no convite final")


def checar_css(pagina):
    css = "\n".join(re.findall(r"<style>(.*?)</style>", pagina, re.S))
    check("dvh" not in css, "não usar dvh: a altura pula com a barra do Safari")
    for n in ("100", "200"):
        check(css.count(f"{n}svh") > 0 and css.count(f"{n}vh") >= css.count(f"{n}svh"),
              f"cada {n}svh precisa de um {n}vh antes, como fallback")
    check(".palco{display:none}" in css, "o palco precisa começar escondido (modo empilhado)")
    check(".fundo .pausa{display:none!important}" in css, "o botão de pausa da maquete não pode ficar focável dentro do fundo aria-hidden")
    m = re.search(r"--scrim:\s*rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)", css)
    check(m is not None, "falta --scrim: rgba(...)")
    if not m:
        return
    r, g, b, a = int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4))
    fundo = tuple(round(255 * (1 - a) + c * a) for c in (r, g, b))  # pior caso: pixel branco sob a faixa
    for var in ("--texto-cena", "--ressalva-cena"):
        cor = re.search(var + r":\s*#([0-9A-Fa-f]{6})", css)
        check(cor is not None, f"falta {var}")
        if cor:
            rgb = tuple(int(cor.group(1)[i:i + 2], 16) for i in (0, 2, 4))
            cr = contraste(rgb, fundo)
            check(cr >= 4.5, f"{var} sobre a faixa: {cr:.2f}:1 no pior caso (mín. 4,5)")


def checar_scripts(pagina):
    tags = re.findall(r"<script ([^>]*)></script>", pagina)
    nomes = [atributos(t).get("src") for t in tags]
    check(nomes == ["maquetes.js", "historia.js"], f"scripts devem ser maquetes.js e historia.js, nessa ordem; achei {nomes}")
    check(all(" defer" in " " + t for t in tags), "os scripts precisam de defer")
    check("<script>" not in pagina, "sem script inline")


def main():
    check(PAGINA.exists(), "portfolio/site/historia.html não existe")
    if PAGINA.exists():
        pagina = PAGINA.read_text(encoding="utf-8")
        index = (SITE / "index.html").read_text(encoding="utf-8")
        checar_marcacao(pagina)
        checar_texto(pagina, index)
        checar_css(pagina)
        checar_scripts(pagina)
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
