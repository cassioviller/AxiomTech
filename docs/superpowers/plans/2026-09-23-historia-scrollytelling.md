# historia.html (scrollytelling) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar `portfolio/site/historia.html`, que conta a história do Cássio em 10 cenas. Cada cena tem uma frase grande no centro da tela; o fundo troca quando a frase cruza o meio da tela, e as duas maquetes 3D andam conforme o scroll.

**Architecture:** O HTML estático já é a página completa e acessível: 10 `<section class="cena">`, cada uma com a sua figura e o seu texto, empilhadas. O `historia.js` (sem biblioteca, IIFE, `defer`) só melhora essa página. Quando há `IntersectionObserver` e o movimento não está reduzido, ele move as figuras para um palco `position: sticky`, liga a classe `js-historia` e troca a cena ativa no meio da tela. Nas cenas de maquete, amarra `fig.__maquete.seek()` ao progresso do scroll. A verificação usa `check_historia.py`, estático e em Python puro, mais um harness que o Chromium headless abre **em tempo real**, controlado pelo DevTools Protocol por um cliente WebSocket mínimo escrito com a biblioteca padrão. Com `--virtual-time-budget`, o Chromium quase não gera quadros: foram medidos 4 `requestAnimationFrame` em 2 s. Sem quadros, o `IntersectionObserver` e o evento de scroll não disparam.

**Tech Stack:** HTML/CSS/JS sem build; three.js já vendorizado em `portfolio/site/vendor/`, carregado pelo `maquetes.js` existente; Python 3.12 só com a biblioteca padrão; Chromium headless (`chromium`) com `--remote-debugging-port`; `python3 -m http.server`; ImageMagick (`magick`) só para inspecionar screenshots.

**Spec:** `docs/superpowers/specs/2026-09-23-historia-scrollytelling-design.md`. A pesquisa das 5 personas que sustenta a spec fica em `docs/superpowers/research/2026-09-23-historia/`.

## Global Constraints

- O texto das 10 cenas é **exatamente** o da tabela "Roteiro" da spec: frase grande, linha de apoio e fundo. Ele é copiado para `ROTEIRO` em `check_historia.py`, e esse script é a fonte da verdade.
- Nenhum número pode aparecer no texto visível de `historia.html` se não existir no texto visível de `portfolio/site/index.html`.
- Estas ressalvas têm de aparecer literalmente: `estimativa`, `ainda não rodou`, `nos 19 serviços conferidos`, `cópia do sistema`, `assistentes de IA`.
- Frase grande com no máximo 10 palavras. Linha de apoio com 1 a 30 palavras. A palavra "você" aparece uma única vez, no convite final.
- Nenhuma dependência nova: os únicos scripts da página são `maquetes.js` e `historia.js`, nessa ordem e com `defer`; não há script inline. O CSS fica inline num `<style>`, como no `index.html`.
- Rolagem 100% nativa: o `historia.js` não usa `scrollTo`, `scrollBy`, `scrollIntoView`, `preventDefault`, `'wheel'` nem `'touchmove'`.
- Alturas de tela usam `height:100vh` seguido de `height:100svh` (e o mesmo para `200vh`/`200svh`). Nunca `dvh`.
- A faixa atrás do texto é `--scrim: rgba(12,16,21,.78)`. O texto da cena é `--texto-cena: #FFFFFF` e a ressalva é `--ressalva-cena: #D7E1EC`. Cada uma dessas cores precisa de contraste ≥ 4,5:1 no pior caso (pixel branco sob a faixa).
- `data-passo` identifica a cena da história. `data-cena` continua sendo só o nome da cena 3D do `maquetes.js` (`36min`, `casa-viaja`).
- `portfolio/site/index.html` **não muda**. O `maquetes.js` muda em uma linha só, para expor `dur` (Task 3).
- Trabalhar no branch `historia-scrollytelling`, criado a partir do HEAD atual (`storytelling-minto`, `c0e1459`), com um commit por tarefa terminando em `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.

## Review Focus

1. **Rolagem rápida que salta várias cenas** (do fim direto ao início). A cena certa fica ativa e nenhuma maquete continua no fluxo. Teste: linha `salto ativa=tese maquetes=-` do harness (Task 2).
2. **Aparelho sem WebGL ou three.js que não carrega.** A imagem de reserva da cena da maquete continua visível. Teste: `img zip=visible` e `img casa=visible` com `--disable-3d-apis` (Task 2).
3. **Celular estreito (320 px).** Nada provoca rolagem horizontal. Teste: rodada do harness a 320 px com `overflow-x=false` (Task 2).
4. **Teclado e leitor de tela.** O primeiro link é "Pular para o texto", nada é focável dentro das figuras `aria-hidden` e o botão de pausa do `maquetes.js` fica escondido. Teste: checagens estáticas (Task 1).
5. **`prefers-reduced-motion: reduce`.** Cenas empilhadas, palco vazio, as 10 frases visíveis. Teste: rodada do harness com `--force-prefers-reduced-motion` (Task 2).

---

## File Structure

| Arquivo | Responsabilidade |
|---|---|
| `portfolio/site/historia.html` (novo) | Marcação das 10 cenas, barra, ficha e rodapé; CSS inline dos dois modos (empilhado e cenas) |
| `portfolio/site/historia.js` (novo) | Modo cenas: move os fundos para o palco, troca a cena ativa e sincroniza a maquete com o scroll |
| `portfolio/site/maquetes.js` (1 linha) | Expõe `dur` na API `fig.__maquete` |
| `portfolio/tests/check_historia.py` (novo) | Checagens estáticas e, com `--navegador`, as do harness (Chromium em tempo real via DevTools Protocol) |
| `portfolio/tests/historia_teste.html` (novo) | Harness: iframe da página, rolagem cena a cena, registro do estado num `<pre>` |
| `portfolio/revisao/CHANGELOG.md` | Seção "Rodada 5" |

---

### Task 1: Página empilhada (HTML + CSS) e checagem estática

**Files:**
- Create: `portfolio/tests/check_historia.py`
- Create: `portfolio/site/historia.html`

**Interfaces:**
- Produces:
  - `ROTEIRO: list[tuple]` em `check_historia.py`, com `(passo, tag, frase, ressalva, imagem|None, largura, altura, maquete|None)`;
  - `check(cond, msg)`, `limpo(html) -> str`, `corpo(html) -> str`, `numeros(texto) -> set[str]`, `atributos(tag) -> dict`, `cenas(html) -> list[tuple[classes, id, passo, miolo]]`, `contraste(rgb, rgb) -> float`;
  - funções `checar_marcacao`, `checar_texto`, `checar_css`, `checar_scripts` e `main()`.
- Marcação que o JS da Task 2 consome:
  - `<div class="palco" aria-hidden="true"></div>`;
  - `<section class="cena[ longa]" id="cN" data-passo="…">`;
  - `<figure class="fundo[ maquete]" data-passo="…" [data-cena="…"] aria-hidden="true">`;
  - `<div class="texto">`;
  - classe `.js-historia` no `<html>`;
  - `.ativo` no `.fundo`.

- [ ] **Step 1: Criar o branch e commitar spec, pesquisa e plano**

```bash
cd /home/runner/workspace && git checkout -b historia-scrollytelling
git add docs/superpowers/specs/2026-09-23-historia-scrollytelling-design.md docs/superpowers/research/2026-09-23-historia docs/superpowers/plans/2026-09-23-historia-scrollytelling.md
git commit -m "Spec, pesquisa das personas e plano da página historia.html

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 2: Escrever `portfolio/tests/check_historia.py`**

```python
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
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py`
Expected: `FALHOU:` com `portfolio/site/historia.html não existe`

- [ ] **Step 4: Escrever `portfolio/site/historia.html`**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Cássio Viller — a história</title>
<meta name="description" content="Cássio Viller — orçamento, planejamento e custos. A história em cenas: da contabilidade à obra e aos sistemas que dão origem a cada número.">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:title" content="Cássio Viller — um número sem origem custa caro na obra">
<meta property="og:description" content="A história em cenas: contabilidade, obra e os sistemas que dão origem a cada número.">
<meta property="og:image" content="og.png">
<meta name="theme-color" content="#12171D">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="preload" as="image" href="img/o-quantitativos.webp" fetchpriority="high">
<style>
:root{
  --ground:#ECEBE6; --surface:#FFFFFF; --ink:#171F29; --ink-2:#3C4652; --muted:#5B6672;
  --accent:#B5440E; --accent-ink:#FFFFFF; --rule:#D3D1CA;
  --tinta:#12171D; --scrim:rgba(12,16,21,.78); --texto-cena:#FFFFFF; --ressalva-cena:#D7E1EC; --relogio:#F07A3E;
  --display:"Barlow Condensed","Arial Narrow",Impact,sans-serif;
  --body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#12171D; --surface:#1A2129; --ink:#E9E7E1; --ink-2:#C4C8CC; --muted:#93A0AD;
    --accent:#F07A3E; --accent-ink:#161616; --rule:#2E3A47;
  }
}
:root[data-theme="dark"]{
  --ground:#12171D; --surface:#1A2129; --ink:#E9E7E1; --ink-2:#C4C8CC; --muted:#93A0AD;
  --accent:#F07A3E; --accent-ink:#161616; --rule:#2E3A47;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--body);font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
img{max-width:100%;height:auto;display:block}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.pular{position:absolute;left:-9999px;top:8px;z-index:50;background:var(--accent);color:var(--accent-ink);padding:10px 14px;font-family:var(--mono);font-size:.8rem;text-decoration:none}
.pular:focus{left:12px}
/* barra: nome, cargo-alvo e contato sempre à mão */
.barra{position:sticky;top:0;z-index:30;display:flex;flex-wrap:wrap;align-items:center;gap:6px 16px;padding:10px 16px;background:var(--ground);border-bottom:1px solid var(--rule);font-family:var(--mono);font-size:.78rem}
.barra .nome{font-family:var(--display);font-weight:700;font-size:1.15rem;letter-spacing:.01em;text-transform:uppercase;color:var(--ink);text-decoration:none}
.barra .cargo{flex:1 1 auto;color:var(--ink-2)}
.barra .acoes{display:flex;flex-wrap:wrap;gap:10px}
.barra .acoes a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--accent);padding:4px 0}
.barra .acoes .zap{background:var(--accent);color:var(--accent-ink);border:0;padding:6px 10px;border-radius:2px}
/* modo empilhado (padrão): sem JS, sem IntersectionObserver ou com movimento reduzido */
.palco{display:none}
.historia{display:block;max-width:880px;margin:0 auto;padding:0 16px}
.cena{padding:40px 0;border-bottom:1px solid var(--rule)}
.fundo{position:relative;margin:0 0 18px}
.fundo img{width:100%;max-height:60vh;object-fit:cover;border:1px solid var(--rule)}
.fundo canvas,.fundo .hud{display:none}
.fundo .pausa{display:none!important}
.frase{font-family:var(--display);font-weight:700;font-size:clamp(2rem,6vw,3.6rem);line-height:1.02;letter-spacing:.005em;margin:0;text-wrap:balance}
.ressalva{font-family:var(--mono);font-size:.86rem;line-height:1.55;color:var(--ink-2);margin:12px 0 0;max-width:62ch}
.cta{display:flex;flex-wrap:wrap;gap:10px;margin:22px 0 0}
.btn{display:inline-block;font-family:var(--mono);font-size:.8rem;letter-spacing:.06em;text-transform:uppercase;text-decoration:none;padding:13px 16px;border-radius:2px;background:var(--accent);color:var(--accent-ink)}
.btn.fantasma{background:transparent;color:var(--ink);box-shadow:inset 0 0 0 1.5px var(--ink)}
.ficha{max-width:880px;margin:0 auto;padding:48px 16px 24px}
.ficha h2{font-family:var(--display);font-weight:600;font-size:2rem;line-height:1.05;margin:0 0 12px}
.ficha p{color:var(--ink-2);max-width:66ch;margin:0 0 10px}
footer{max-width:880px;margin:0 auto;padding:20px 16px 40px;display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;font-family:var(--mono);font-size:.74rem;color:var(--muted);border-top:1px solid var(--rule)}
footer a{color:var(--ink)}
/* modo cenas: historia.js liga .js-historia no <html> e leva cada .fundo para o .palco */
.js-historia .historia{max-width:none;padding:0;position:relative}
.js-historia .palco{display:block;position:sticky;top:0;height:100vh;height:100svh;margin-bottom:-100vh;margin-bottom:-100svh;overflow:hidden;background:var(--tinta)}
.js-historia .palco .fundo{position:absolute;inset:0;margin:0;opacity:0;transition:opacity .6s ease}
.js-historia .palco .fundo.ativo{opacity:1}
.js-historia .palco .fundo img{width:100%;height:100%;max-height:none;object-fit:cover;border:0;filter:brightness(.6) saturate(.85)}
.js-historia .palco .fundo canvas{display:block;position:absolute;inset:0;width:100%;height:100%;opacity:0;transition:opacity .5s}
.js-historia .palco .fundo.viva canvas{opacity:1}
.js-historia .palco .fundo.viva img{visibility:hidden}
.js-historia .palco .hud{display:block;position:absolute;right:16px;bottom:14px}
.js-historia .palco .hud b{font-family:var(--display);font-weight:700;font-size:clamp(1.8rem,5vw,3rem);line-height:1;color:var(--relogio);font-variant-numeric:tabular-nums}
.js-historia .palco .hud [data-legenda]{display:none}
.js-historia .cena{position:relative;z-index:1;min-height:100vh;min-height:100svh;display:flex;align-items:center;justify-content:center;padding:96px 16px;border:0}
.js-historia .cena.longa{min-height:200vh;min-height:200svh;align-items:flex-start}
.js-historia .cena.longa .texto{position:sticky;top:28vh;top:28svh}
.js-historia .texto{max-width:960px;text-align:center;background:var(--scrim);padding:22px 24px}
.js-historia .frase{color:var(--texto-cena);font-size:clamp(2.2rem,7vw,5rem);max-width:18ch;margin:0 auto}
.js-historia .ressalva{color:var(--ressalva-cena);margin:14px auto 0}
.js-historia .cta{justify-content:center}
.js-historia .btn.fantasma{color:var(--texto-cena);box-shadow:inset 0 0 0 1.5px var(--texto-cena)}
@media (prefers-reduced-motion: reduce){.js-historia .palco .fundo,.js-historia .palco .fundo canvas{transition:none}}
</style>
</head>
<body>
<a class="pular" href="#c1">Pular para o texto</a>
<header class="barra">
  <a class="nome" href="index.html">Cássio Viller</a>
  <span class="cargo">Orçamento, planejamento e custos</span>
  <nav class="acoes" aria-label="Contato">
    <a href="curriculo-cassio-viller.pdf" target="_blank" rel="noopener">Currículo (PDF)</a>
    <a class="zap" href="https://wa.me/5512982071116?text=Ol%C3%A1%2C%20C%C3%A1ssio.%20Vi%20seu%20portf%C3%B3lio%20e%20quero%20te%20mandar%20uma%20obra%20para%20or%C3%A7ar." target="_blank" rel="noopener">WhatsApp</a>
  </nav>
</header>

<main id="historia" class="historia">
  <div class="palco" aria-hidden="true"></div>

  <section class="cena" id="c1" data-passo="tese">
    <figure class="fundo" data-passo="tese" aria-hidden="true"><img src="img/o-quantitativos.webp" alt="" width="1040" height="1000" fetchpriority="high"></figure>
    <div class="texto">
      <h1 class="frase">Um número sem origem custa caro na obra.</h1>
      <p class="ressalva">Cássio Viller, estudante de Engenharia Civil (7º semestre), mira orçamento, planejamento e custos.</p>
    </div>
  </section>

  <section class="cena" id="c2" data-passo="origem">
    <div class="texto">
      <h2 class="frase">Comecei no centavo, não na parede.</h2>
      <p class="ressalva">Folha, notas e balancete no escritório da família, desde 2017.</p>
    </div>
  </section>

  <section class="cena" id="c3" data-passo="obra">
    <figure class="fundo" data-passo="obra" aria-hidden="true"><img src="img/p-fotos.webp" alt="" width="1600" height="1353" loading="lazy"></figure>
    <div class="texto">
      <h2 class="frase">Mas na obra, vi a mesma informação digitada cinco vezes.</h2>
      <p class="ressalva">VEKS Engenharia, V Alves e Estruturas do Vale, entre 2025 e 2026.</p>
    </div>
  </section>

  <section class="cena longa" id="c4" data-passo="zip">
    <figure class="fundo maquete" data-passo="zip" data-cena="36min" aria-hidden="true">
      <canvas></canvas>
      <img src="img/upa-plan-grey.webp" alt="" width="1400" height="440" loading="lazy">
      <div class="hud"><b data-relogio></b><span data-legenda></span></div>
    </figure>
    <div class="texto">
      <h2 class="frase">Do zip à proposta assinável em 36 minutos.</h2>
      <p class="ressalva">Medidos: 11:35 → 12:11, numa ampliação de unidade de saúde com 26 ambientes e 328 m². À mão, cerca de 2 dias úteis (estimativa).</p>
    </div>
  </section>

  <section class="cena" id="c5" data-passo="escala">
    <figure class="fundo" data-passo="escala" aria-hidden="true"><img src="img/s1.webp" alt="" width="1000" height="728" loading="lazy"></figure>
    <div class="texto">
      <h2 class="frase">13 obras no sistema, até R$ 24,5 milhões.</h2>
      <p class="ressalva">11 com proposta; a menor, R$ 29 mil. A gestão de obra deste sistema ainda não rodou numa obra real.</p>
    </div>
  </section>

  <section class="cena" id="c6" data-passo="precisao">
    <figure class="fundo" data-passo="precisao" aria-hidden="true"><img src="img/o-orcamento.webp" alt="" width="1040" height="1080" loading="lazy"></figure>
    <div class="texto">
      <h2 class="frase">Desvio máximo de 0,25% nos 19 serviços conferidos.</h2>
      <p class="ressalva">Serviço a serviço, contra a tabela SINAPI da Caixa; acima de 1% de desvio, a importação é recusada.</p>
    </div>
  </section>

  <section class="cena" id="c7" data-passo="sige">
    <figure class="fundo" data-passo="sige" aria-hidden="true"><img src="img/p-diario-portal.webp" alt="" width="1600" height="1193" loading="lazy"></figure>
    <div class="texto">
      <h2 class="frase">Numa obra real, 23 diários estavam só no WhatsApp.</h2>
      <p class="ressalva">No SIGE, que concebi: recuperados, levam a obra de 27,6% para 44,7% concluído, contra 60,8% planejado — lido numa cópia do sistema.</p>
    </div>
  </section>

  <section class="cena longa" id="c8" data-passo="casa">
    <figure class="fundo maquete" data-passo="casa" data-cena="casa-viaja" aria-hidden="true">
      <canvas></canvas>
      <img src="img/m1.webp" alt="" width="900" height="562" loading="lazy">
      <div class="hud"><b data-relogio></b><span data-legenda></span></div>
    </figure>
    <div class="texto">
      <h2 class="frase">O celeiro não cabe inteiro no caminhão.</h2>
      <p class="ressalva">B-36: vai em duas caixas, em três viagens, com 37 decisões registradas.</p>
    </div>
  </section>

  <section class="cena" id="c9" data-passo="metodo">
    <figure class="fundo" data-passo="metodo" aria-hidden="true"><img src="img/o-proposta.webp" alt="" width="885" height="1060" loading="lazy"></figure>
    <div class="texto">
      <h2 class="frase">Construí o jeito de o número não sumir.</h2>
      <p class="ressalva">Idealizei e dirigi os sistemas; o código foi escrito com assistentes de IA, e as regras, os testes e a revisão são meus.</p>
    </div>
  </section>

  <section class="cena" id="c10" data-passo="convite">
    <div class="texto">
      <h2 class="frase">Faltam 3 semestres para o diploma. Não falta obra feita.</h2>
      <p class="ressalva">Você me manda o pacote do projeto; eu devolvo levantamento, orçamento com faixa e proposta no seu modelo.</p>
      <p class="cta">
        <a class="btn" href="https://wa.me/5512982071116?text=Ol%C3%A1%2C%20C%C3%A1ssio.%20Vi%20seu%20portf%C3%B3lio%20e%20quero%20te%20mandar%20uma%20obra%20para%20or%C3%A7ar." target="_blank" rel="noopener">Me mande uma obra ↗</a>
        <a class="btn fantasma" href="index.html">Ver o portfólio completo</a>
        <a class="btn fantasma" href="curriculo-cassio-viller.pdf" target="_blank" rel="noopener">Baixar currículo (PDF)</a>
      </p>
    </div>
  </section>
</main>

<section class="ficha" aria-labelledby="ficha-titulo">
  <h2 id="ficha-titulo">O que faço numa construtora</h2>
  <p>Levantamento de quantitativos no projeto, orçamento com composições SINAPI e BDI, cronograma físico-financeiro com curva S, diário de obra e medição, compras com cotação e quadro de concorrência, fluxo de caixa e custo previsto × realizado.</p>
  <p>Engenharia Civil, 7º semestre, faltam 3 · CLT ou PJ · São José dos Campos/SP, presencial ou remoto.</p>
</section>
<footer>
  <span>Cássio Viller · São José dos Campos/SP</span>
  <a href="index.html">Ver o portfólio completo</a>
</footer>
<script src="maquetes.js" defer></script>
<script src="historia.js" defer></script>
</body>
</html>
```

- [ ] **Step 5: Rodar e ver passar**

Run: `python3 portfolio/tests/check_historia.py`
Expected: `OK`

- [ ] **Step 6: Provar que a checagem de números morde**

Run: `sed -i 's/R\$ 29 mil/R$ 29,9 mil/' portfolio/site/historia.html && python3 portfolio/tests/check_historia.py; sed -i 's/R\$ 29,9 mil/R$ 29 mil/' portfolio/site/historia.html && python3 portfolio/tests/check_historia.py`
Expected: primeiro `FALHOU:` com `cena escala: ressalva diferente do roteiro` e `números que o index.html não sustenta: ['29,9']`; depois `OK`.

- [ ] **Step 7: Commit**

```bash
git add portfolio/tests/check_historia.py portfolio/site/historia.html
git commit -m "historia.html: 10 cenas em modo empilhado e checagem estática

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Modo cenas — `historia.js` troca o fundo no meio da tela (+ harness)

**Files:**
- Create: `portfolio/site/historia.js`
- Create: `portfolio/tests/historia_teste.html`
- Modify: `portfolio/tests/check_historia.py` (novas `checar_js`, `navegador`, `checar_navegador`; `main()` passa a chamá-las)

**Interfaces:**
- Consumes: a marcação da Task 1. `ROTEIRO`, `check`, `SITE` e `ROOT` de `check_historia.py`.
- Produces:
  - `window.Historia = {ativa: string|null}`, sendo `ativa` o `data-passo` da cena ativa;
  - classe `js-historia` no `<html>`, `.ativo` no `.fundo` da cena ativa e `hidden` nas maquetes fora de cena;
  - `chromium(largura, extra) -> WS` (context manager), com `WS.comando(metodo, **params)` e `WS.avaliar(expr)`;
  - `navegador(largura=390, extra=("--disable-3d-apis",)) -> list[str]`, as linhas do `<pre id="resultado">` do harness;
  - o harness aceita `?parar=<passo>`, que interrompe a rolagem nessa cena (usado na Task 4).

- [ ] **Step 1: Escrever o harness `portfolio/tests/historia_teste.html`**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Teste da história</title>
<style>html,body{margin:0}#f{position:absolute;top:0;left:0;width:100%;height:800px;border:0}#resultado{position:absolute;top:820px;left:0;margin:0}</style>
</head>
<body>
<iframe id="f" src="../site/historia.html" title="História"></iframe>
<pre id="resultado">rodando</pre>
<script>
// Harness do Chromium headless: rola o iframe cena a cena e registra o estado em #resultado.
// ?parar=<passo> interrompe no meio dessa cena (para tirar screenshot).
(function(){
'use strict';
var parar=new URLSearchParams(location.search).get('parar');
var f=document.getElementById('f'),saida=[];
function log(s){saida.push(s);}
function espera(ms){return new Promise(function(r){setTimeout(r,ms);});}
function centralizar(w,el,fracao){var r=el.getBoundingClientRect();w.scrollTo(0,Math.round(r.top+w.scrollY+r.height*fracao-w.innerHeight/2));}
function maquetesVisiveis(d){return [].filter.call(d.querySelectorAll('.palco .maquete'),function(m){return !m.hidden;}).map(function(m){return m.dataset.passo;}).join(',')||'-';}
function tempo(m){var t=m.__maquete&&m.__maquete.t;return typeof t==='number'?t.toFixed(1):'null';}
f.addEventListener('load',function(){
  var w=f.contentWindow,d=f.contentDocument;
  // maquete falsa: com --disable-3d-apis o maquetes.js desiste e a API real nunca aparece
  [].forEach.call(d.querySelectorAll('figure.maquete'),function(m){m.__maquete={dur:1000,t:null,seek:function(x){this.t=x;}};});
  (async function(){
    await espera(800);
    var H=w.Historia||{};
    log('reduzido='+w.matchMedia('(prefers-reduced-motion: reduce)').matches);
    log('js-historia='+d.documentElement.classList.contains('js-historia'));
    log('palco-filhos='+d.querySelector('.palco').children.length);
    log('frases-visiveis='+[].filter.call(d.querySelectorAll('.frase'),function(x){return x.offsetHeight>0;}).length);
    log('overflow-x='+(d.documentElement.scrollWidth>d.documentElement.clientWidth));
    log('inicio ativa='+H.ativa);
    if(H.progresso)log('progresso='+[H.progresso(400,1000,800),H.progresso(-100,1000,800),H.progresso(-700,1000,800),H.progresso(0,0,800)].join(' '));
    var cenas=[].slice.call(d.querySelectorAll('.cena[data-passo]'));
    for(var i=0;i<cenas.length;i++){
      var c=cenas[i],p=c.dataset.passo;
      centralizar(w,c,.5);await espera(700);
      if(parar===p)return;
      var fa=d.querySelector('.palco .fundo.ativo');
      log('cena '+p+' ativa='+H.ativa+' fundo='+(fa?fa.dataset.passo:'nenhum')+' maquetes='+maquetesVisiveis(d));
      var m=d.querySelector('figure.maquete[data-passo="'+p+'"]');
      if(m){
        log('img '+p+'='+w.getComputedStyle(m.querySelector('img')).visibility);
        log('seek '+p+'='+tempo(m));
        centralizar(w,c,.25);await espera(300);
        log('seek25 '+p+'='+tempo(m));
      }
    }
    centralizar(w,cenas[0],.5);await espera(900);
    log('salto ativa='+H.ativa+' maquetes='+maquetesVisiveis(d));
    document.getElementById('resultado').textContent=saida.join('\n')+'\nFIM';
  })();
});
})();
</script>
</body>
</html>
```

- [ ] **Step 2: Acrescentar as checagens em `check_historia.py`**

Trocar o bloco de imports do topo por:

```python
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
```

Acima de `def main():`:

```python
PORTA = 5056
PORTA_CDP = 9333


def checar_js():
    caminho = SITE / "historia.js"
    check(caminho.exists(), "portfolio/site/historia.js não existe")
    if not caminho.exists():
        return
    js = re.sub(r"//[^\n]*", "", caminho.read_text(encoding="utf-8"))  # comentários não contam
    for proibido in ("scrollTo", "scrollBy", "scrollIntoView", "preventDefault", "'wheel'", "'touchmove'"):
        check(proibido not in js, f"historia.js não pode usar {proibido} (rolagem nativa)")
    check("fps" not in js.lower() and "matar" not in js, "historia.js não duplica a guarda de desempenho do maquetes.js")


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
    """Roda o harness e devolve as linhas do <pre id="resultado"> (espera até 60 s pelo FIM)."""
    with chromium(largura, extra) as ws:
        ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/tests/historia_teste.html")
        prazo = time.time() + 60
        texto = ""
        while time.time() < prazo:
            texto = ws.avaliar("(document.getElementById('resultado')||{}).textContent||''") or ""
            if texto.endswith("FIM"):
                break
            time.sleep(0.5)
    return texto.splitlines()


def checar_navegador():
    maquetes = {p for p, *_resto, maq in ROTEIRO if maq}
    normal = navegador(390)
    check("FIM" in normal, f"390 px: o harness não terminou — últimas linhas {normal[-3:]}")
    for linha in ("reduzido=false", "js-historia=true", "overflow-x=false", "inicio ativa=tese", "salto ativa=tese maquetes=-"):
        check(linha in normal, f"390 px: faltou {linha!r}")
    for passo, _tag, _frase, _ressalva, imagem, *_resto in ROTEIRO:
        fundo = passo if imagem else "nenhum"
        maq = passo if passo in maquetes else "-"
        esperado = f"cena {passo} ativa={passo} fundo={fundo} maquetes={maq}"
        check(esperado in normal, f"390 px: esperava {esperado!r}")
        if passo in maquetes:
            check(f"img {passo}=visible" in normal, f"390 px: sem WebGL, a imagem de reserva da cena {passo} precisa ficar visível")
    estreito = navegador(320)
    check("FIM" in estreito, "320 px: o harness não terminou")
    check("overflow-x=false" in estreito, "320 px: a página rola na horizontal")
    reduzido = navegador(390, ("--disable-3d-apis", "--force-prefers-reduced-motion"))
    check("reduzido=true" in reduzido, "o Chromium não aplicou --force-prefers-reduced-motion")
    for linha in ("js-historia=false", "palco-filhos=0", "frases-visiveis=10", "overflow-x=false"):
        check(linha in reduzido, f"movimento reduzido: faltou {linha!r}")
```

E em `main()`, logo depois de `checar_scripts(pagina)`:

```python
        checar_js()
        if "--navegador" in sys.argv:
            checar_navegador()
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py --navegador`
Expected: `FALHOU:` com `portfolio/site/historia.js não existe`, `390 px: faltou 'js-historia=true'` e as linhas `cena … ativa=…` ausentes (o `historia.js` ainda não existe).

- [ ] **Step 4: Escrever `portfolio/site/historia.js`**

```js
// História em cenas: quando a frase cruza o meio da tela, o fundo troca de cena.
// Regras: rolagem nativa (o script nunca move a página nem bloqueia o gesto); sem JS, sem
// IntersectionObserver ou com prefers-reduced-motion a página fica empilhada e estática, cada frase com a sua imagem.
(function(){
'use strict';
var H=window.Historia={ativa:null};
var cenas=[].slice.call(document.querySelectorAll('.cena[data-passo]'));
var palco=document.querySelector('.palco');
if(!cenas.length||!palco||!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;

// cada fundo vai para o palco fixo; a maquete fica hidden fora da sua cena, para só uma renderizar por vez
var fundos={},esconder={};
cenas.forEach(function(c){
  var f=c.querySelector('.fundo');
  if(!f)return;
  fundos[c.dataset.passo]=f;
  if(f.classList.contains('maquete'))f.hidden=true;
  palco.appendChild(f);
});
document.documentElement.classList.add('js-historia');

function esconderDepois(passo){
  clearTimeout(esconder[passo]);
  esconder[passo]=setTimeout(function(){if(H.ativa!==passo)fundos[passo].hidden=true;},650);
}
function ativar(passo){
  if(passo===H.ativa)return;
  var antes=H.ativa&&fundos[H.ativa];
  if(antes){
    antes.classList.remove('ativo');
    if(antes.classList.contains('maquete'))esconderDepois(H.ativa);
  }
  H.ativa=passo;
  var f=fundos[passo];
  if(f){
    clearTimeout(esconder[passo]);
    if(f.hidden){f.hidden=false;dispatchEvent(new Event('resize'));} // a maquete remede o canvas ao voltar
    void f.offsetWidth; // aplica o display antes da opacidade, senão não há transição
    f.classList.add('ativo');
  }
}
function cenaNoCentro(){
  var meio=innerHeight/2;
  for(var i=0;i<cenas.length;i++){var r=cenas[i].getBoundingClientRect();if(r.top<=meio&&r.bottom>meio)return cenas[i];}
  return null;
}

var io=new IntersectionObserver(function(es){
  es.forEach(function(e){if(e.isIntersecting)ativar(e.target.dataset.passo);});
},{rootMargin:'-45% 0px -45% 0px',threshold:0});
cenas.forEach(function(c){io.observe(c);});
var inicial=cenaNoCentro();
if(inicial)ativar(inicial.dataset.passo);
})();
```

- [ ] **Step 5: Rodar e ver passar**

Run: `python3 portfolio/tests/check_historia.py --navegador`
Expected: `OK`. Leva cerca de 40 s, porque são três rodadas do Chromium em tempo real, de uns 10 s cada.

- [ ] **Step 6: Commit**

```bash
git add portfolio/site/historia.js portfolio/tests/historia_teste.html portfolio/tests/check_historia.py
git commit -m "historia.js: fundo troca no meio da tela; harness no Chromium headless

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: A maquete 3D anda conforme o scroll

**Files:**
- Modify: `portfolio/site/maquetes.js` (a linha `var api={frozen:false,seek:function(x){t=x;api.frozen=true;}};`)
- Modify: `portfolio/site/historia.js` (substituído pela versão completa abaixo)
- Modify: `portfolio/tests/check_historia.py` (nova `checar_maquetes_js`; novas asserções em `checar_navegador`)

**Interfaces:**
- Consumes: `fundos`, `ativar` e `window.Historia` da Task 2. `fig.__maquete = {frozen, seek(t)}` do `maquetes.js`.
- Produces:
  - `fig.__maquete.dur: number`;
  - `window.Historia.progresso(topo, altura, alturaTela) -> number`, entre 0 e 1: vale 0 quando o topo da cena cruza o meio da tela e 1 quando o fim cruza.

- [ ] **Step 1: Escrever os testes que falham**

Em `check_historia.py`, acima de `def main():`:

```python
def checar_maquetes_js():
    js = (SITE / "maquetes.js").read_text(encoding="utf-8")
    check("dur:sc.dur" in js, "maquetes.js precisa expor a duração da cena em fig.__maquete.dur")
```

No fim de `checar_navegador()`, depois das checagens do modo reduzido:

```python
    check("progresso=0 0.5 1 0" in normal, "Historia.progresso fora do esperado (0 no topo, 0,5 no meio, 1 no fim, 0 sem altura)")
    texto_normal = "\n".join(normal)
    for passo in sorted(maquetes):
        for chave, alvo in (("seek", 500), ("seek25", 250)):
            m = re.search(rf"^{chave} {passo}=([\d.]+)$", texto_normal, re.M)
            check(m is not None and abs(float(m.group(1)) - alvo) <= 20,
                  f"{chave} {passo}: esperava ≈{alvo} (dur 1000), achei {m.group(1) if m else 'nada'}")
```

Em `main()`, depois de `checar_js()`:

```python
        checar_maquetes_js()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py --navegador`
Expected: `FALHOU:` com `maquetes.js precisa expor a duração…`, `Historia.progresso fora do esperado…` e `seek zip: esperava ≈500 (dur 1000), achei nada` (o harness registra `seek zip=null`).

- [ ] **Step 3: Expor `dur` no `maquetes.js`**

Trocar exatamente

```js
  var api={frozen:false,seek:function(x){t=x;api.frozen=true;}}; // seek(): usado nos testes para conferir um quadro exato
```

por

```js
  var api={frozen:false,dur:sc.dur,seek:function(x){t=x;api.frozen=true;}}; // seek(): testes e historia.js (tempo = scroll)
```

- [ ] **Step 4: Substituir `portfolio/site/historia.js` pela versão completa**

```js
// História em cenas: quando a frase cruza o meio da tela, o fundo troca de cena; nas cenas de maquete,
// o tempo da animação 3D é o progresso do scroll dentro da cena.
// Regras: rolagem nativa (o script nunca move a página nem bloqueia o gesto); sem JS, sem
// IntersectionObserver ou com prefers-reduced-motion a página fica empilhada e estática, cada frase com a sua imagem.
(function(){
'use strict';
// progresso 0→1 de uma cena: 0 quando o topo cruza o meio da tela, 1 quando o fim cruza
function progresso(topo,altura,alturaTela){
  if(!(altura>0))return 0;
  return Math.max(0,Math.min(1,(alturaTela/2-topo)/altura));
}
var H=window.Historia={ativa:null,progresso:progresso};
var cenas=[].slice.call(document.querySelectorAll('.cena[data-passo]'));
var palco=document.querySelector('.palco');
if(!cenas.length||!palco||!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;

// cada fundo vai para o palco fixo; a maquete fica hidden fora da sua cena, para só uma renderizar por vez
var fundos={},esconder={},tentativas=0,pendente=false;
cenas.forEach(function(c){
  var f=c.querySelector('.fundo');
  if(!f)return;
  fundos[c.dataset.passo]=f;
  if(f.classList.contains('maquete'))f.hidden=true;
  palco.appendChild(f);
});
document.documentElement.classList.add('js-historia');

// maquete da cena ativa: o relógio da animação segue o scroll (seek congela o tempo), nunca anda sozinho
function sincronizar(){
  var f=H.ativa&&fundos[H.ativa];
  if(!f||!f.classList.contains('maquete'))return;
  var api=f.__maquete;
  if(!api||!api.dur){ // three.js ainda carregando: tenta de novo por até 5 s
    if(tentativas++<25)setTimeout(sincronizar,200);
    return;
  }
  var r=document.querySelector('.cena[data-passo="'+H.ativa+'"]').getBoundingClientRect();
  api.seek(progresso(r.top,r.height,innerHeight)*api.dur*0.999);
}
function esconderDepois(passo){
  clearTimeout(esconder[passo]);
  esconder[passo]=setTimeout(function(){if(H.ativa!==passo)fundos[passo].hidden=true;},650);
}
function ativar(passo){
  if(passo===H.ativa)return;
  var antes=H.ativa&&fundos[H.ativa];
  if(antes){
    antes.classList.remove('ativo');
    if(antes.classList.contains('maquete'))esconderDepois(H.ativa);
  }
  H.ativa=passo;
  var f=fundos[passo];
  if(f){
    clearTimeout(esconder[passo]);
    if(f.hidden){f.hidden=false;dispatchEvent(new Event('resize'));} // a maquete remede o canvas ao voltar
    void f.offsetWidth; // aplica o display antes da opacidade, senão não há transição
    f.classList.add('ativo');
  }
  tentativas=0;
  sincronizar();
}
function cenaNoCentro(){
  var meio=innerHeight/2;
  for(var i=0;i<cenas.length;i++){var r=cenas[i].getBoundingClientRect();if(r.top<=meio&&r.bottom>meio)return cenas[i];}
  return null;
}

var io=new IntersectionObserver(function(es){
  es.forEach(function(e){if(e.isIntersecting)ativar(e.target.dataset.passo);});
},{rootMargin:'-45% 0px -45% 0px',threshold:0});
cenas.forEach(function(c){io.observe(c);});
addEventListener('scroll',function(){
  if(pendente)return;
  pendente=true;
  requestAnimationFrame(function(){pendente=false;sincronizar();});
},{passive:true});
var inicial=cenaNoCentro();
if(inicial)ativar(inicial.dataset.passo);
})();
```

- [ ] **Step 5: Rodar e ver passar**

Run: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_site.py`
Expected: `OK` e `OK`. O `check_site.py` garante que o `index.html` e as maquetes dele continuam intactos.

- [ ] **Step 6: Commit**

```bash
git add portfolio/site/maquetes.js portfolio/site/historia.js portfolio/tests/check_historia.py
git commit -m "historia.js: maquetes 3D seguem o scroll (seek); maquetes.js expõe dur

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Conferência visual e changelog

**Files:**
- Modify: `portfolio/revisao/CHANGELOG.md`

- [ ] **Step 1: Screenshots no celular (390 px) e no desktop (1280 px), com WebGL ligado**

As capturas passam pelo mesmo Chromium em tempo real do `check_historia.py`, que tem janela de tamanho exato e quadros reais.

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/f9d44ef5-7d41-4ced-9ebe-ca35da9a73fc/scratchpad python3 - <<'EOF'
import base64, os, sys, time
sys.path.insert(0, "portfolio/tests")
import check_historia as c
S = os.environ["S"]
# cenas no modo cenas, paradas no meio de cada uma
for largura in (390, 1280):
    for passo in ("tese", "zip", "sige", "convite"):
        with c.chromium(largura, ("--enable-unsafe-swiftshader",)) as ws:
            ws.comando("Page.navigate", url=f"http://127.0.0.1:{c.PORTA}/tests/historia_teste.html?parar={passo}")
            prazo = time.time() + 30
            while time.time() < prazo and not ws.avaliar(
                    f"(function(){{var f=document.getElementById('f');var H=f&&f.contentWindow&&f.contentWindow.Historia;return !!H&&H.ativa==='{passo}';}})()"):
                time.sleep(0.3)
            time.sleep(2)  # crossfade e, na maquete, alguns quadros do three.js
            png = ws.comando("Page.captureScreenshot", format="png")["data"]
        open(f"{S}/historia-{largura}-{passo}.png", "wb").write(base64.b64decode(png))
# página inteira no modo empilhado (movimento reduzido); rola antes para as imagens lazy carregarem
with c.chromium(390, ("--disable-3d-apis", "--force-prefers-reduced-motion")) as ws:
    ws.comando("Page.navigate", url=f"http://127.0.0.1:{c.PORTA}/site/historia.html")
    time.sleep(2)
    altura = int(ws.comando("Page.getLayoutMetrics")["cssContentSize"]["height"])
    for y in range(0, altura, 600):
        ws.avaliar(f"scrollTo(0,{y})")
        time.sleep(0.2)
    ws.avaliar("scrollTo(0,0)")
    time.sleep(1)
    png = ws.comando("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                     clip={"x": 0, "y": 0, "width": 390, "height": altura, "scale": 1})["data"]
open(f"{S}/historia-reduzido.png", "wb").write(base64.b64decode(png))
print("ok", altura)
EOF
```

Abrir as 8 capturas de cena com a ferramenta Read. A captura da página empilhada, de uns 5.400 px de altura, deve ser lida em faixas: `magick $S/historia-reduzido.png -crop 390x1400+0+<y> +repage $S/r-<y>.png`, com y = 0, 1400, 2800 e 4200.
Expected:
- (a) Nas cenas, a frase está centrada sobre a faixa escura, legível, sem corte e sem rolagem horizontal.
- (b) Na cena `zip`, aparece a maquete ou, se a guarda de fps cair, a planta; o relógio fica no canto inferior direito.
- (c) Em `convite`, os três botões aparecem inteiros.
- (d) No modo empilhado, cada frase aparece com a sua imagem, todas carregadas, e depois a ficha e o rodapé.

Se algum item falhar, corrigir o CSS em `historia.html` e rodar de novo `python3 portfolio/tests/check_historia.py --navegador` antes de continuar.

- [ ] **Step 2: Registrar no changelog**

Acrescentar ao fim de `portfolio/revisao/CHANGELOG.md`:

```markdown

---

# Rodada 5 — página historia.html (a história em cenas), 23/09/2026

- Pesquisa com 5 personas (recrutadora, diretor de engenharia, roteirista, dev front-end e acessibilidade/desempenho) em `docs/superpowers/research/2026-09-23-historia/`; spec em `docs/superpowers/specs/2026-09-23-historia-scrollytelling-design.md`.
- `site/historia.html`: 10 cenas (frase ≤ 10 palavras + ressalva), barra fixa com currículo e WhatsApp, ficha com as palavras-chave, rodapé. Sem JS ou com movimento reduzido: cenas empilhadas, cada frase com a sua imagem.
- `site/historia.js`: fundo em palco `sticky`, troca no meio da tela (`IntersectionObserver`), crossfade; maquetes 3D amarradas ao scroll por `seek()`, só uma no fluxo por vez. Rolagem nativa.
- `site/maquetes.js`: a API `fig.__maquete` passa a expor `dur`.
- `tests/check_historia.py` (+ `tests/historia_teste.html` no Chromium headless): roteiro exato, números que o index sustenta, ressalvas, contraste da faixa no pior caso, `aria-hidden`, `svh`, 320 px sem rolagem horizontal, movimento reduzido.
- O `index.html` não mudou. Em aberto (do Cássio): estágio/júnior, link a partir do portfólio, foto `p-fotos.webp`, imagem de prévia própria.
```

- [ ] **Step 3: Checagem final e commit**

Run: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_site.py`
Expected: `OK` e `OK`

```bash
git add portfolio/revisao/CHANGELOG.md
git commit -m "Changelog da rodada 5: historia.html

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```
