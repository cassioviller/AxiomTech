# A história na linha do tempo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar a página principal (`portfolio/site/index.html`) na história do Cássio contada **na ordem real da linha do tempo**, de 2017 a set/2026: 17 capítulos datados, uma régua de tempo navegável no cabeçalho, links para o caso completo no portfólio, fundos tipográficos nos capítulos sem imagem e uma terceira maquete 3D (içamento do módulo).

**Architecture:** Mesma base testada da rodada 1: HTML estático que sem JS já é a página empilhada, e `historia.js`, que move os fundos para um palco `sticky` e troca a cena no meio da tela. Nesta rodada entram:
- a `<nav class="regua">` no cabeçalho, com um link por capítulo e exatamente um `aria-current="step"`, que o `historia.js` atualiza em `ativar()` sem observer nem listener novo;
- os fundos tipográficos (`figure.fundo.tipo`);
- a cena `icamento` em `maquetes.js`, com o mesmo `stage()`/`camKeys` das outras.

Tudo é verificado pelo `check_historia.py`: estático, e com `--navegador` pelo harness no Chromium em tempo real, via DevTools Protocol.

**Tech Stack:** HTML/CSS/JS sem build; three.js r186 já vendorizado (`portfolio/site/vendor/`); Python 3.12 só com a biblioteca padrão; Chromium headless (`chromium`) com `--remote-debugging-port`; `python3 -m http.server`; ImageMagick (`magick`) só para ler screenshots.

**Spec:** `docs/superpowers/specs/2026-09-23-historia-linha-do-tempo-design.md`. Ela parte da spec da rodada 1, `docs/superpowers/specs/2026-09-23-historia-scrollytelling-design.md`. A pesquisa das 5 personas está em `docs/superpowers/research/2026-09-23-historia-v2/`.

**Ensaio:** todo o código deste plano foi executado numa cópia descartável antes de ser escrito aqui. Cada teste falhou pelo motivo esperado e depois passou; o conjunto completo com `--navegador` terminou em `OK`.

## Global Constraints

- O texto dos 17 capítulos (frase, apoio, data, fundo e link do caso) é **exatamente** o da tabela "Roteiro" da spec. Ele fica copiado em `ROTEIRO`, no `check_historia.py`, que é a fonte da verdade.
- Nenhum número pode aparecer no texto visível de `index.html` se não existir no texto visível de `portfolio/site/portfolio.html`.
- Estas ressalvas têm de aparecer literalmente: `estimativa`, `ainda não rodou`, `nos 19 serviços conferidos`, `cópia do sistema`, `assistentes de IA`, `em paralelo`, `pré-dimensionado`, `sujeito à revisão do engenheiro responsável`, `no sistema em uso, a carga ainda não foi aplicada`. É proibido usar `3,40`.
- Ordem cronológica estrita pela primeira data de cada capítulo datado. Os capítulos de moldura (`tese`, `metodo`, `convite`) não têm data.
- Frase grande com no máximo 10 palavras e apoio com 1 a 30 palavras. Um único "mas" entre as frases grandes. "Você" só no convite.
- Os links "Ver…" apontam para `portfolio.html#<âncora existente>` e têm nomes únicos.
- As datas da história precisam bater com as do currículo (`portfolio/curriculo/curriculo-cassio-viller.txt`).
- Rolagem 100% nativa: o `historia.js` não usa `scrollTo`, `scrollBy`, `scrollIntoView`, `preventDefault`, `'wheel'`, `'touchmove'` nem `aria-live`. A régua só muda o `scrollLeft` da própria lista.
- Sem dependência nova: os únicos scripts são `maquetes.js` e `historia.js`, com `defer`. O CSS fica inline.
- Contraste no pior caso sobre a faixa `rgba(12,16,21,.78)`: texto, apoio e data ≥ 4,5:1; relógio da maquete (texto grande) ≥ 3:1.
- Trabalhar no branch `historia-scrollytelling`, com um commit por tarefa terminando em `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.

## Review Focus

1. **Zoom de texto a 200% com a barra e a régua.** A barra fica mais alta, e o salto pela régua não pode esconder o título atrás dela. Teste: checagem estática de `scroll-margin-top:9rem` (Task 2), mais conferência manual com zoom de 200% (Task 5, Step 6).
2. **iPhone real (Safari).** O palco `sticky` e a barra `sticky` não podem pular quando a barra de endereço recolhe, e a régua rola na horizontal sem arrastar a página. Teste: conferência manual (Task 5, Step 6), porque não há iPhone no ambiente.
3. **Três maquetes num celular fraco.** Os três contextos WebGL ficam vivos, mas só um renderiza por vez. Teste: o harness confere que só a maquete da cena ativa fica no fluxo (`maquetes=<passo>`, Task 2), mais conferência de memória no DevTools (Task 5, Step 6).
4. **Leitor de tela na régua.** Cada marco é lido como "data + marco", e só um tem `aria-current`. Teste: nomes acessíveis e `aria-current` no HTML (Task 3), marco ativo por cena no harness (Task 3) e VoiceOver manual (Task 5, Step 6).
5. **Captura headless a 1280 px com WebGL.** Ela mostra uma faixa na base das cenas 3D, com pixels **transparentes**, embora o canvas meça 1280×800. É efeito da captura, não da página: não "corrigir". Teste: nota no Expected da Task 5, Step 5.

---

## File Structure

| Arquivo | Responsabilidade |
|---|---|
| `portfolio/site/index.html` | 17 capítulos, barra com status atual e régua, ficha e rodapé; CSS inline dos dois modos |
| `portfolio/site/historia.js` | Modo cenas: palco, troca de cena, maquete ligada ao scroll, régua (`aria-current` e data) e foco no salto |
| `portfolio/site/maquetes.js` | Cena 3D nova `icamento` em `CENAS` |
| `portfolio/tests/check_historia.py` | Roteiro, cronologia, datas contra o currículo, links do caso, régua, contraste, harness e WebGL real |
| `portfolio/tests/historia_teste.html` | Harness: rolagem cena a cena, reversão, three.js atrasado, marco da régua e salto |
| `portfolio/revisao/CHANGELOG.md` | Seção "Rodada 6" |

---

### Task 1: Registrar a troca de páginas (história como principal)

A troca feita a pedido do Cássio (a história virou `index.html` e o portfólio virou `portfolio.html`) está no branch **sem commit**. Esta tarefa só a registra.

**Files:**
- Modify (já modificados no working tree): `portfolio/site/index.html` (a história; antes `historia.html`), `portfolio/site/portfolio.html` (antes `index.html`), `portfolio/tests/check_historia.py`, `portfolio/tests/check_site.py`, `portfolio/tests/historia_teste.html`, `portfolio/DESIGN.md`, `portfolio/README.md`
- Add: spec, pesquisa e plano desta rodada

- [ ] **Step 1: Conferir o estado**

Run: `cd /home/runner/workspace && git branch --show-current && git status --short`
Expected:
- o branch é `historia-scrollytelling`;
- o status mostra a troca (`D portfolio/site/historia.html`, `A portfolio/site/portfolio.html`, `M portfolio/site/index.html`), os testes, `DESIGN.md` e `README.md` modificados, e as pastas novas em `docs/superpowers/`.

- [ ] **Step 2: Rodar as checagens**

Run: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_site.py`
Expected: `OK` e `OK`

- [ ] **Step 3: Commit**

```bash
cd /home/runner/workspace && git add -A portfolio/site portfolio/tests/check_historia.py portfolio/tests/check_site.py portfolio/tests/historia_teste.html portfolio/DESIGN.md portfolio/README.md docs/superpowers/specs/2026-09-23-historia-linha-do-tempo-design.md docs/superpowers/research/2026-09-23-historia-v2 docs/superpowers/plans/2026-09-23-historia-linha-do-tempo.md
git commit -m "História como página principal (index.html); portfólio completo em portfolio.html

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: O roteiro na linha do tempo (17 capítulos)

**Files:**
- Modify (substituição completa): `portfolio/tests/check_historia.py`, `portfolio/tests/historia_teste.html`, `portfolio/site/index.html`
- Sem mudança: `portfolio/site/historia.js`, `portfolio/site/maquetes.js`

**Interfaces:**
- Produces:
  - `ROTEIRO: list[dict]`, montado por `cap(passo, tag, data, frase, ressalva, fundo, caso)`, em que `data` é `(texto, [datetime…])` e `fundo` é `("img", arquivo, l, a)`, `("ano", texto)` ou `("maquete", cena3d, reserva, l, a)`;
  - `checar_curriculo(pagina)`;
  - `id` de cada `<section class="cena">` igual ao `data-passo`;
  - `<p class="data">` com `<time datetime>`, `<p class="caso"><a href="portfolio.html#…">`, `<figure class="fundo tipo"><span class="ano">…</span></figure>`;
  - a figura `data-cena="icamento"` (a cena 3D chega na Task 4; até lá fica a imagem de reserva);
  - o harness usa os `id` `precisao` (e a seção seguinte, `casa`) e `zip`.

- [ ] **Step 1: Substituir `portfolio/tests/check_historia.py`**

```python
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
        "Comecei no centavo, não na parede.",
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
        "O módulo sobe pelo balancim, com os cabos na vertical.",
        "Assim a parede não é comprimida; balancim de içamento e guindaste da classe certa viraram itens de regra no orçamento.",
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
        "De 2017 a 2026: contabilidade, obra e sistemas. Idealizei e dirigi; o código foi escrito com assistentes de IA, e as regras e a revisão são meus.",
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
    for r in RESSALVAS:
        check(r in t, f"ressalva ausente: {r!r}")
    for p in PROIBIDOS:
        check(p not in t, f"texto proibido na página: {p!r}")
    check(t.lower().count("você") == 1, "\"você\" deve aparecer uma vez só, no convite final")


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
        if passo in maquetes:
            check(f"img {passo}=visible" in normal, f"390 px: sem WebGL, a imagem de reserva da cena {passo} precisa ficar visível")
    estreito = navegador(320)
    check("FIM" in estreito, "320 px: o harness não terminou")
    check("overflow-x=false" in estreito, "320 px: a página rola na horizontal")
    reduzido = navegador(390, ("--disable-3d-apis", "--force-prefers-reduced-motion"))
    check("reduzido=true" in reduzido, "o Chromium não aplicou --force-prefers-reduced-motion")
    for linha in ("js-historia=false", "palco-filhos=0", f"frases-visiveis={len(ROTEIRO)}", "overflow-x=false"):
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
        checar_js()
        checar_maquetes_js()
        if "--navegador" in sys.argv:
            checar_navegador()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py`
Expected: `FALHOU:` começando por `esperava 17 cenas, achei 10`

- [ ] **Step 3: Substituir `portfolio/tests/historia_teste.html`**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Teste da história</title>
<style>html,body{margin:0}#f{position:absolute;top:0;left:0;width:100%;height:800px;border:0}#resultado{position:absolute;top:820px;left:0;margin:0}</style>
</head>
<body>
<iframe id="f" src="../site/index.html" title="História"></iframe>
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
function posicionarTopo(w,el,fracao){var r=el.getBoundingClientRect();w.scrollTo(0,Math.round(r.top+w.scrollY-w.innerHeight*fracao));}
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
      centralizar(w,c,.5);await espera(1000);
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
    // borda entre precisao e a cena seguinte (casa): a 48% o meio da tela está em casa; voltando a borda para 95%, está em precisao
    var seguinte=d.getElementById('precisao').nextElementSibling;
    posicionarTopo(w,seguinte,.48);await espera(500);
    log('reversao-48 ativa='+H.ativa);
    posicionarTopo(w,seguinte,.95);await espera(500);
    log('reversao-95 ativa='+H.ativa);
    // three.js que só chega depois de 1 s de rolagem contínua: a maquete ainda precisa ser sincronizada (e congelada)
    var mz=d.querySelector('figure.maquete[data-passo="zip"]');
    if(mz){
      delete mz.__maquete;
      centralizar(w,d.getElementById('zip'),.3);await espera(300);
      for(var k=0;k<30;k++){w.scrollBy(0,2);await espera(33);}
      await espera(300);
      mz.__maquete={dur:1000,t:null,seek:function(x){this.t=x;}};
      await espera(1000);
      log('seek-tardio zip='+tempo(mz));
    }
    centralizar(w,cenas[0],.5);await espera(1000);
    log('salto ativa='+H.ativa+' maquetes='+maquetesVisiveis(d));
    document.getElementById('resultado').textContent=saida.join('\n')+'\nFIM';
  })();
});
})();
</script>
</body>
</html>
```

- [ ] **Step 4: Substituir `portfolio/site/index.html`**

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Cássio Viller — a história</title>
<meta name="description" content="Cássio Viller — orçamento, planejamento e custos. A história na linha do tempo, de 2017 a 2026: contabilidade, obra e os sistemas que dão origem a cada número.">
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
  --tinta:#12171D; --scrim:rgba(12,16,21,.78); --texto-cena:#FFFFFF; --ressalva-cena:#D7E1EC; --data-cena:#F2B896; --relogio:#F07A3E;
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
.cena{scroll-margin-top:9rem}
.data{font-family:var(--mono);font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:0 0 10px}
.caso{margin:14px 0 0;font-family:var(--mono);font-size:.8rem}
.caso a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--accent);padding:4px 0}
.fundo.tipo{display:flex;align-items:center;justify-content:center;min-height:28vh;background:var(--surface);border:1px solid var(--rule);overflow:hidden}
.fundo.tipo .ano{font-family:var(--display);font-weight:700;font-size:clamp(4rem,18vw,9rem);line-height:1;color:var(--accent);opacity:.3;white-space:nowrap}
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
.js-historia .historia{max-width:none;padding:0;position:relative;background:var(--tinta)}
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
.js-historia .data{color:var(--data-cena)}
.js-historia .caso a{color:var(--texto-cena);border-bottom-color:var(--data-cena)}
.js-historia .palco .fundo.tipo{min-height:0;background:var(--tinta);border:0;align-items:flex-end;justify-content:flex-start;padding:0 0 3vh 4vw}
.js-historia .palco .fundo.tipo .ano{font-size:clamp(6rem,26vw,20rem);opacity:.22;color:var(--relogio)}
@media (prefers-reduced-motion: reduce){.js-historia .palco .fundo,.js-historia .palco .fundo canvas{transition:none}}
</style>
</head>
<body>
<a class="pular" href="#tese">Pular para o texto</a>
<header class="barra">
  <a class="nome" href="portfolio.html">Cássio Viller</a>
  <span class="cargo">7º semestre de Eng. Civil · orçamento, planejamento e custos · CLT ou PJ</span>
  <nav class="acoes" aria-label="Contato">
    <a href="curriculo-cassio-viller.pdf" target="_blank" rel="noopener">Currículo (PDF)</a>
    <a class="zap" href="https://wa.me/5512982071116?text=Ol%C3%A1%2C%20C%C3%A1ssio.%20Vi%20seu%20portf%C3%B3lio%20e%20quero%20te%20mandar%20uma%20obra%20para%20or%C3%A7ar." target="_blank" rel="noopener">WhatsApp</a>
  </nav>
</header>

<main id="historia" class="historia">
  <div class="palco" aria-hidden="true"></div>

  <section class="cena" id="tese" data-passo="tese">
    <figure class="fundo" data-passo="tese" aria-hidden="true"><img src="img/o-quantitativos.webp" alt="" width="1040" height="1000" fetchpriority="high"></figure>
    <div class="texto">
      <h1 class="frase" tabindex="-1">Um número sem origem custa caro na obra.</h1>
      <p class="ressalva">Cássio Viller, estudante de Engenharia Civil (7º semestre), mira orçamento, planejamento e custos.</p>
    </div>
  </section>

  <section class="cena" id="origem" data-passo="origem">
    <figure class="fundo tipo" data-passo="origem" aria-hidden="true"><span class="ano">2017</span></figure>
    <div class="texto">
      <p class="data"><time datetime="2017">2017</time> → <time datetime="2024">2024</time></p>
      <h2 class="frase" tabindex="-1">Comecei no centavo, não na parede.</h2>
      <p class="ressalva">Escritório contábil da família desde 2017; na UNIFEI, fiscal do DCE em 2022 e diretor de vendas da InLoco Jr. de 2023 a 2024.</p>
      <p class="caso"><a href="portfolio.html#curriculo">Ver no currículo: contabilidade e UNIFEI →</a></p>
    </div>
  </section>

  <section class="cena" id="mudanca" data-passo="mudanca">
    <figure class="fundo tipo" data-passo="mudanca" aria-hidden="true"><span class="ano">2025</span></figure>
    <div class="texto">
      <p class="data"><time datetime="2025">2025</time></p>
      <h2 class="frase" tabindex="-1">Em 2025, mudei de cidade e de curso.</h2>
      <p class="ressalva">Cruzeiro do Sul (EAD), morando em São José dos Campos: hoje no 7º semestre, faltam 3. Sistemas de Informação na PUC, em paralelo.</p>
      <p class="caso"><a href="portfolio.html#curriculo">Ver no currículo: formação →</a></p>
    </div>
  </section>

  <section class="cena" id="obra" data-passo="obra">
    <figure class="fundo tipo" data-passo="obra" aria-hidden="true"><span class="ano">5×</span></figure>
    <div class="texto">
      <p class="data"><time datetime="2025-02">fev/2025</time> → <time datetime="2026-03">mar/2026</time></p>
      <h2 class="frase" tabindex="-1">Mas na obra, vi a mesma informação digitada cinco vezes.</h2>
      <p class="ressalva">V Alves (gerente de produção, CLT meio período) e Estruturas do Vale (estágio, meio período), em paralelo. No estágio nasceu o SIGE.</p>
      <p class="caso"><a href="portfolio.html#curriculo">Ver no currículo: V Alves e Estruturas do Vale →</a></p>
    </div>
  </section>

  <section class="cena" id="veks" data-passo="veks">
    <figure class="fundo tipo" data-passo="veks" aria-hidden="true"><span class="ano">2026</span></figure>
    <div class="texto">
      <p class="data"><time datetime="2026-03">mar/2026</time> → <time datetime="2026-09">set/2026</time></p>
      <h2 class="frase" tabindex="-1">Em março de 2026, entrei na VEKS Engenharia.</h2>
      <p class="ressalva">PJ, contrato de 6 meses cumprido até o fim; a V Alves, em meio período, seguiu até julho.</p>
      <p class="caso"><a href="portfolio.html#obra">Ver o caso completo: obras na VEKS →</a></p>
    </div>
  </section>

  <section class="cena" id="ferramentas" data-passo="ferramentas">
    <figure class="fundo tipo" data-passo="ferramentas" aria-hidden="true"><span class="ano">3ª</span></figure>
    <div class="texto">
      <p class="data"><time datetime="2026-03">mar</time> → <time datetime="2026-04">abr/2026</time></p>
      <h2 class="frase" tabindex="-1">Toda conta repetida virou ferramenta.</h2>
      <p class="ressalva">Nos primeiros meses na VEKS: a calculadora de parede em LSF e drywall e o classificador do fluxo de caixa.</p>
      <p class="caso"><a href="portfolio.html#ferramentas">Ver as ferramentas: calculadora e classificador →</a></p>
    </div>
  </section>

  <section class="cena" id="sige" data-passo="sige">
    <figure class="fundo" data-passo="sige" aria-hidden="true"><img src="img/c-aprovacao.webp" alt="" width="1100" height="467" loading="lazy"></figure>
    <div class="texto">
      <p class="data"><time datetime="2026-05">mai</time> → <time datetime="2026-09">set/2026</time></p>
      <h2 class="frase" tabindex="-1">De maio a setembro, o SIGE ganhou versão nova.</h2>
      <p class="ressalva">Cerca de 50 módulos em 6 áreas, entregas registradas de 22/07 a 14/09/2026; código escrito com assistente de IA, sob a minha direção.</p>
      <p class="caso"><a href="portfolio.html#sige">Ver o caso completo: SIGE →</a></p>
    </div>
  </section>

  <section class="cena" id="galpoes" data-passo="galpoes">
    <figure class="fundo tipo" data-passo="galpoes" aria-hidden="true"><span class="ano">22 baias</span></figure>
    <div class="texto">
      <p class="data"><time datetime="2026-06-08">jun/2026</time></p>
      <h2 class="frase" tabindex="-1">Em junho, começou a obra que testaria o SIGE.</h2>
      <p class="ressalva">Dois galpões e 22 baias numa fazenda, em Light Steel Frame: a obra real do portal do cliente e do diário.</p>
      <p class="caso"><a href="portfolio.html#obra">Ver o caso completo: galpões e baias →</a></p>
    </div>
  </section>

  <section class="cena" id="escala" data-passo="escala">
    <figure class="fundo" data-passo="escala" aria-hidden="true"><img src="img/s1.webp" alt="" width="1000" height="728" loading="lazy"></figure>
    <div class="texto">
      <p class="data"><time datetime="2026-07-09">jul</time> → <time datetime="2026-09-21">set/2026</time></p>
      <h2 class="frase" tabindex="-1">13 obras no sistema, até R$ 24,5 milhões.</h2>
      <p class="ressalva">11 com proposta; a menor, R$ 29 mil. A gestão de obra deste sistema ainda não rodou numa obra real.</p>
      <p class="caso"><a href="portfolio.html#sistema">Ver o caso completo: sistema de orçamento →</a></p>
    </div>
  </section>

  <section class="cena" id="precisao" data-passo="precisao">
    <figure class="fundo" data-passo="precisao" aria-hidden="true"><img src="img/o-orcamento.webp" alt="" width="1040" height="1080" loading="lazy"></figure>
    <div class="texto">
      <p class="data"><time datetime="2026-07-09">jul</time> → <time datetime="2026-09-21">set/2026</time></p>
      <h2 class="frase" tabindex="-1">Desvio máximo de 0,25% nos 19 serviços conferidos.</h2>
      <p class="ressalva">Serviço a serviço, contra a tabela SINAPI da Caixa; acima de 1% de desvio, a importação é recusada.</p>
      <p class="caso"><a href="portfolio.html#sistema">Ver o caso completo: conferência SINAPI →</a></p>
    </div>
  </section>

  <section class="cena longa" id="casa" data-passo="casa">
    <figure class="fundo maquete" data-passo="casa" data-cena="casa-viaja" aria-hidden="true">
      <canvas></canvas>
      <img src="img/m1.webp" alt="" width="900" height="562" loading="lazy">
      <div class="hud"><b data-relogio></b><span data-legenda></span></div>
    </figure>
    <div class="texto">
      <p class="data"><time datetime="2026-08">ago/2026</time></p>
      <h2 class="frase" tabindex="-1">O celeiro não cabe inteiro no caminhão.</h2>
      <p class="ressalva">B-36, pré-dimensionado e sujeito à revisão do engenheiro responsável: duas caixas, três viagens, 37 decisões registradas.</p>
      <p class="caso"><a href="portfolio.html#modular">Ver o caso completo: celeiro B-36 →</a></p>
    </div>
  </section>

  <section class="cena longa" id="icamento" data-passo="icamento">
    <figure class="fundo maquete" data-passo="icamento" data-cena="icamento" aria-hidden="true">
      <canvas></canvas>
      <img src="img/m2.webp" alt="" width="900" height="562" loading="lazy">
      <div class="hud"><b data-relogio></b><span data-legenda></span></div>
    </figure>
    <div class="texto">
      <p class="data"><time datetime="2026-08">ago/2026</time></p>
      <h2 class="frase" tabindex="-1">O módulo sobe pelo balancim, com os cabos na vertical.</h2>
      <p class="ressalva">Assim a parede não é comprimida; balancim de içamento e guindaste da classe certa viraram itens de regra no orçamento.</p>
      <p class="caso"><a href="portfolio.html#modular">Ver o caso completo: casas modulares →</a></p>
    </div>
  </section>

  <section class="cena" id="whatsapp" data-passo="whatsapp">
    <figure class="fundo" data-passo="whatsapp" aria-hidden="true"><img src="img/p-fotos.webp" alt="" width="1600" height="1353" loading="lazy"></figure>
    <div class="texto">
      <p class="data"><time datetime="2026-08-11">ago/2026</time></p>
      <h2 class="frase" tabindex="-1">Depois de 11/08, o diário saiu do sistema.</h2>
      <p class="ressalva">42 diários lançados até ali; os 23 dias seguintes ficaram só no grupo de WhatsApp, e 28 atividades prontas apareciam como atrasadas.</p>
      <p class="caso"><a href="portfolio.html#sige">Ver o caso completo: o diário no WhatsApp →</a></p>
    </div>
  </section>

  <section class="cena" id="recuperado" data-passo="recuperado">
    <figure class="fundo" data-passo="recuperado" aria-hidden="true"><img src="img/p-diario-portal.webp" alt="" width="1600" height="1193" loading="lazy"></figure>
    <div class="texto">
      <p class="data"><time datetime="2026-09">set/2026</time></p>
      <h2 class="frase" tabindex="-1">Recuperado, o diário mostrou 44,7% de avanço.</h2>
      <p class="ressalva">Antes, 27,6%; planejado para 07/09, 60,8%. Lido numa cópia do sistema; no sistema em uso, a carga ainda não foi aplicada.</p>
      <p class="caso"><a href="portfolio.html#sige">Ver o caso completo: diários recuperados →</a></p>
    </div>
  </section>

  <section class="cena longa" id="zip" data-passo="zip">
    <figure class="fundo maquete" data-passo="zip" data-cena="36min" aria-hidden="true">
      <canvas></canvas>
      <img src="img/upa-plan-grey.webp" alt="" width="1400" height="440" loading="lazy">
      <div class="hud"><b data-relogio></b><span data-legenda></span></div>
    </figure>
    <div class="texto">
      <p class="data"><time datetime="2026-09">set/2026</time></p>
      <h2 class="frase" tabindex="-1">Em setembro, uma proposta assinável em 36 minutos.</h2>
      <p class="ressalva">Medidos: 11:35 → 12:11, numa ampliação de unidade de saúde com 26 ambientes e 328 m². À mão, cerca de 2 dias úteis (estimativa).</p>
      <p class="caso"><a href="portfolio.html#orcamento">Ver o caso completo: 36 minutos →</a></p>
    </div>
  </section>

  <section class="cena" id="metodo" data-passo="metodo">
    <figure class="fundo" data-passo="metodo" aria-hidden="true"><img src="img/o-proposta.webp" alt="" width="885" height="1060" loading="lazy"></figure>
    <div class="texto">
      <h2 class="frase" tabindex="-1">Construí o jeito de o número não sumir.</h2>
      <p class="ressalva">De 2017 a 2026: contabilidade, obra e sistemas. Idealizei e dirigi; o código foi escrito com assistentes de IA, e as regras e a revisão são meus.</p>
    </div>
  </section>

  <section class="cena" id="convite" data-passo="convite">
    <div class="texto">
      <h2 class="frase" tabindex="-1">Faltam 3 semestres para o diploma. Não falta obra feita.</h2>
      <p class="ressalva">Você me manda o pacote do projeto; eu devolvo levantamento, orçamento com faixa e proposta no seu modelo.</p>
      <p class="cta">
        <a class="btn" href="https://wa.me/5512982071116?text=Ol%C3%A1%2C%20C%C3%A1ssio.%20Vi%20seu%20portf%C3%B3lio%20e%20quero%20te%20mandar%20uma%20obra%20para%20or%C3%A7ar." target="_blank" rel="noopener">Me mande uma obra ↗</a>
        <a class="btn fantasma" href="portfolio.html">Ver o portfólio completo</a>
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
  <a href="portfolio.html">Ver o portfólio completo</a>
</footer>
<script src="maquetes.js" defer></script>
<script src="historia.js" defer></script>
</body>
</html>
```

- [ ] **Step 5: Rodar e ver passar (estático)**

Run: `python3 portfolio/tests/check_historia.py`
Expected: `OK`

- [ ] **Step 6: Provar que a checagem de números morde**

Run: `sed -i 's/R\$ 29 mil/R$ 29,9 mil/' portfolio/site/index.html && python3 portfolio/tests/check_historia.py; sed -i 's/R\$ 29,9 mil/R$ 29 mil/' portfolio/site/index.html && python3 portfolio/tests/check_historia.py`
Expected: primeiro `FALHOU:` com `cena escala: ressalva diferente do roteiro` e `números que o portfólio não sustenta: ['29,9']`; depois `OK`.

- [ ] **Step 7: Rodar no navegador**

Run: `python3 portfolio/tests/check_historia.py --navegador`
Expected: `OK`, em cerca de 80 s (três rodadas do Chromium em tempo real).

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add portfolio/tests/check_historia.py portfolio/tests/historia_teste.html portfolio/site/index.html
git commit -m "História: 17 capítulos na linha do tempo, datas, links para o caso e fundos tipográficos

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: A régua de tempo (navegação por capítulo)

**Files:**
- Modify: `portfolio/tests/check_historia.py`, `portfolio/tests/historia_teste.html`, `portfolio/site/index.html` (barra e CSS)
- Modify (substituição completa): `portfolio/site/historia.js`

**Interfaces:**
- Consumes: `ROTEIRO` e o `id` das seções (Task 2).
- Produces:
  - `<nav class="regua" aria-label="Linha do tempo">` com `<ol>` de links `#passo`; o nome acessível é a data mais o marco;
  - `.regua-data`, com `data-padrao="2017–2026"`;
  - em `historia.js`, `marcarRegua(passo)` chamada por `ativar()`;
  - o foco vai ao `.frase` do capítulo depois de clicar em `.regua a` ou `a.pular`.

- [ ] **Step 1: Escrever os testes**

Em `check_historia.py`, antes da linha `PORTA = 5056`:

```python
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
```

Em `main()`, logo depois de `        checar_curriculo(pagina)`:

```python
        checar_regua(pagina)
```

Em `checar_navegador()`, logo depois da linha `        check(esperado in normal, f"390 px: esperava {esperado!r}")`:

```python
        rotulo = c["data"][0].split("→")[0].strip() if c["data"] else "2017–2026"
        check(f"regua {passo}=#{passo} n=1 data={rotulo}" in normal,
              f"390 px: na cena {passo}, o marco ativo da régua deve ser #{passo} (e só ele), com a data {rotulo!r} à direita")
```

Ainda em `checar_navegador()`, trocar a linha

```python
    for linha in ("js-historia=false", "palco-filhos=0", f"frases-visiveis={len(ROTEIRO)}", "overflow-x=false"):
```

por

```python
    check("salto-regua foco=veks ativa=veks abaixo-da-barra=true" in normal,
          "390 px: saltar pela régua leva o foco ao título do capítulo, abaixo da barra, e ativa a cena")
    for linha in ("js-historia=false", "palco-filhos=0", f"frases-visiveis={len(ROTEIRO)}", "overflow-x=false",
                  "salto-regua foco=veks ativa=null abaixo-da-barra=true"):
```

Em `historia_teste.html`, logo depois da linha `      log('cena '+p+' ativa='+H.ativa+' fundo='+(fa?fa.dataset.passo:'nenhum')+' maquetes='+maquetesVisiveis(d));`:

```js
      var rc=d.querySelectorAll('.regua [aria-current="step"]');
      log('regua '+p+'='+(rc[0]?rc[0].getAttribute('href'):'-')+' n='+rc.length+' data='+d.querySelector('.regua-data').textContent);
```

e logo depois da linha `    log('salto ativa='+H.ativa+' maquetes='+maquetesVisiveis(d));`:

```js
    // salto pela régua: o foco vai para o título do capítulo, que fica abaixo da barra
    var marco=d.querySelector('.regua a[href="#veks"]');
    if(marco){marco.click();await espera(900);}
    var foco=d.activeElement,secao=foco&&foco.closest?foco.closest('.cena'):null;
    var abaixo=!!foco&&foco.getBoundingClientRect().top>=d.querySelector('.barra').getBoundingClientRect().bottom;
    log('salto-regua foco='+(secao?secao.id:'-')+' ativa='+H.ativa+' abaixo-da-barra='+abaixo);
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py --navegador`
Expected: `FALHOU:` com `a régua (<nav class="regua" aria-label="Linha do tempo">) precisa estar dentro da barra` e `390 px: o harness não terminou — últimas linhas ['rodando']`. O harness para porque lê `.regua-data`, que ainda não existe. Seguem cerca de 18 linhas de régua e de `salto-regua` ausentes.

- [ ] **Step 3: Pôr a régua na barra**

Em `index.html`, logo antes de `</header>` (depois do `</nav>` das ações):

```html
  <nav class="regua" aria-label="Linha do tempo">
    <span class="regua-ponta" aria-hidden="true">2017</span>
    <ol>
      <li><a href="#tese" aria-current="step"><span class="marco">Início</span></a></li>
      <li><a href="#origem"><time datetime="2017">2017 → 2024</time> <span class="marco">Contabilidade e UNIFEI</span></a></li>
      <li><a href="#mudanca"><time datetime="2025">2025</time> <span class="marco">Mudança para São José dos Campos</span></a></li>
      <li><a href="#obra"><time datetime="2025-02">fev/2025 → mar/2026</time> <span class="marco">Entrada na obra</span></a></li>
      <li><a href="#veks"><time datetime="2026-03">mar/2026 → set/2026</time> <span class="marco">VEKS Engenharia</span></a></li>
      <li><a href="#ferramentas"><time datetime="2026-03">mar → abr/2026</time> <span class="marco">Ferramentas</span></a></li>
      <li><a href="#sige"><time datetime="2026-05">mai → set/2026</time> <span class="marco">SIGE, versão atual</span></a></li>
      <li><a href="#galpoes"><time datetime="2026-06-08">jun/2026</time> <span class="marco">Obra dos galpões</span></a></li>
      <li><a href="#escala"><time datetime="2026-07-09">jul → set/2026</time> <span class="marco">Sistema de orçamento</span></a></li>
      <li><a href="#precisao"><time datetime="2026-07-09">jul → set/2026</time> <span class="marco">Conferência SINAPI</span></a></li>
      <li><a href="#casa"><time datetime="2026-08">ago/2026</time> <span class="marco">Celeiro B-36</span></a></li>
      <li><a href="#icamento"><time datetime="2026-08">ago/2026</time> <span class="marco">Içamento do módulo</span></a></li>
      <li><a href="#whatsapp"><time datetime="2026-08-11">ago/2026</time> <span class="marco">Diário no WhatsApp</span></a></li>
      <li><a href="#recuperado"><time datetime="2026-09">set/2026</time> <span class="marco">Diários recuperados</span></a></li>
      <li><a href="#zip"><time datetime="2026-09">set/2026</time> <span class="marco">36 minutos</span></a></li>
      <li><a href="#metodo"><span class="marco">O método</span></a></li>
      <li><a href="#convite"><span class="marco">Convite</span></a></li>
    </ol>
    <span class="regua-data" aria-hidden="true" data-padrao="2017–2026">2017–2026</span>
  </nav>
```

No `<style>`, logo antes da linha `/* modo empilhado (padrão): sem JS, sem IntersectionObserver ou com movimento reduzido */`:

```css
/* régua de tempo: um marco por capítulo; sem JS é só uma lista de links */
.regua{flex:1 1 100%;display:flex;align-items:center;gap:8px;min-width:0}
.regua ol{list-style:none;margin:0;padding:0;display:flex;flex:1 1 auto;min-width:0;overflow-x:auto;scrollbar-width:none;position:relative}
.regua ol::-webkit-scrollbar{display:none}
.regua li{flex:1 0 28px;display:flex}
.regua a{flex:1;min-width:28px;height:28px;display:flex;align-items:center;justify-content:center;position:relative;color:var(--ink);text-decoration:none}
.regua a::before{content:"";position:absolute;left:0;right:0;top:50%;border-top:2px solid var(--rule)}
.regua a::after{content:"";position:relative;width:2px;height:10px;background:var(--muted)}
.regua a[aria-current="step"]::after{width:12px;height:12px;border-radius:50%;background:var(--accent)}
.regua a:hover::after{background:var(--accent)}
.regua time,.regua .marco{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.regua-ponta,.regua-data{font-family:var(--mono);font-size:.7rem;color:var(--muted);white-space:nowrap}
.regua-data{color:var(--accent);min-width:10ch;text-align:right}
```

- [ ] **Step 4: Substituir `portfolio/site/historia.js`**

```js
// História em cenas: quando a frase cruza o meio da tela, o fundo troca de cena e a régua de tempo marca o capítulo;
// nas cenas de maquete, o tempo da animação 3D é o progresso do scroll dentro da cena.
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

// saltar pela régua (ou pelo "Pular para o texto") leva o foco ao título do capítulo — vale também no modo empilhado
document.addEventListener('click',function(e){
  var a=e.target.closest&&e.target.closest('.regua a[href^="#"], a.pular');
  if(!a)return;
  var alvo=document.getElementById(a.getAttribute('href').slice(1));
  var titulo=alvo&&alvo.querySelector('.frase');
  if(titulo)setTimeout(function(){titulo.focus({preventScroll:true});},0);
});

var cenas=[].slice.call(document.querySelectorAll('.cena[data-passo]'));
var palco=document.querySelector('.palco');
if(!cenas.length||!palco||!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;

// cada fundo vai para o palco fixo; a maquete fica hidden fora da sua cena, para só uma renderizar por vez
var fundos={},esconder={},aguardando=0,pendente=false;
var regua=document.querySelector('.regua'),reguaOl=regua&&regua.querySelector('ol'),reguaData=regua&&regua.querySelector('.regua-data');
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
  if(!api||!api.dur){ // three.js ainda carregando: um só temporizador, repetido enquanto a cena da maquete estiver ativa
    if(!aguardando)aguardando=setTimeout(function(){aguardando=0;sincronizar();},200);
    return;
  }
  var r=document.querySelector('.cena[data-passo="'+H.ativa+'"]').getBoundingClientRect();
  api.seek(progresso(r.top,r.height,innerHeight)*api.dur*0.999);
}
// régua: exatamente um marco com aria-current="step"; a data do capítulo aparece à direita
function marcarRegua(passo){
  if(!regua)return;
  var antes=regua.querySelector('a[aria-current]');
  if(antes)antes.removeAttribute('aria-current');
  var a=regua.querySelector('a[href="#'+passo+'"]');
  if(!a)return;
  a.setAttribute('aria-current','step');
  var t=a.querySelector('time');
  if(reguaData)reguaData.textContent=t?t.textContent.split('→')[0].trim():reguaData.getAttribute('data-padrao'); // só o início: cabe no celular
  var li=a.parentNode;
  reguaOl.scrollLeft=li.offsetLeft-(reguaOl.clientWidth-li.offsetWidth)/2; // centraliza o marco: rola só a régua, nunca a página
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
  marcarRegua(passo);
  sincronizar();
}
function cenaNoCentro(){
  var meio=innerHeight/2;
  for(var i=0;i<cenas.length;i++){var r=cenas[i].getBoundingClientRect();if(r.top<=meio&&r.bottom>meio)return cenas[i];}
  return null;
}

var io=new IntersectionObserver(function(){
  // qualquer entrada ou saída na faixa do meio recalcula a cena: numa pequena volta, quem sai não "entra" de novo
  var c=cenaNoCentro();
  if(c)ativar(c.dataset.passo);
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

Run: `python3 portfolio/tests/check_historia.py --navegador`
Expected: `OK`

- [ ] **Step 6: Commit**

```bash
cd /home/runner/workspace && git add portfolio/tests/check_historia.py portfolio/tests/historia_teste.html portfolio/site/index.html portfolio/site/historia.js
git commit -m "História: régua de tempo no cabeçalho, marco ativo e foco no título ao saltar

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: A terceira maquete — o módulo sobe pelo balancim

**Files:**
- Modify: `portfolio/tests/check_historia.py`, `portfolio/site/maquetes.js`

**Interfaces:**
- Consumes: `stage(fig, céu, névoaPerto, névoaLonge) -> {R,S,cam,sun,mat,box,cyl,camKeys}`, `seg`, `lerp`, `montar()` (existentes); a figura `data-cena="icamento"` (Task 2).
- Produces: `CENAS['icamento'] = cenaIcamento`, que devolve `{dur:16, update(t, wide), num:'', leg}`; `checar_maquete_real()`.

- [ ] **Step 1: Escrever os testes**

Em `checar_maquetes_js()`, depois da checagem de `dur:sc.dur`:

```python
    check("'icamento':cenaIcamento" in js, "maquetes.js precisa registrar a cena 3D do içamento em CENAS")
```

Antes de `def main():`:

```python
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
```

Em `main()`, logo depois de `            checar_navegador()`:

```python
            checar_maquete_real()
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py --navegador`
Expected: `FALHOU:` com `maquetes.js precisa registrar a cena 3D do içamento em CENAS` e `com WebGL, a maquete do içamento precisa montar e expor a API`.

- [ ] **Step 3: Escrever a cena em `portfolio/site/maquetes.js`**

Logo antes da linha `var CENAS={'36min':cena36,'casa-viaja':cenaCasa};`:

```js
// ---------- CENA: o módulo sobe pelo balancim (16 s: sai da carreta, sobe com os cabos na vertical, anda e pousa no radier) ----------
// Com o balancim, os cabos descem verticais: o módulo recebe só tração nos olhais e a parede não é comprimida.
function cenaIcamento(fig){
  var st=stage(fig,0xCFDDEA,30,110),S=st.S,mat=st.mat,box=st.box;
  var DUR=16,L=10,C=3.2,H=2.9,CH=.3,TOPO=6.5,XC=6,XR=-6; // módulo 10 × 3,2 m; carreta em x=6, radier em x=-6
  var AMARELO=0xE8A13C;
  box(160,.6,160,mat(0x8A9A6A),0,-.3,0);                                 // terreno (grande: a borda some na névoa)
  box(L+2,.5,C+1.6,mat(0xB9B4A8),XR,.25,0);                              // radier (topo em y=.5)
  box(L+1,.5,C,mat(0x222831),XC,.55,0);                                  // chassi da carreta
  box(L+1,.4,C+.6,mat(0x3D4A57),XC,1.0,0);                               // prancha (topo em y=1.2)
  box(2.4,2.6,C+.4,mat(0xB5440E),XC+L/2+1.9,1.5,0);                      // cavalo
  var mod=new THREE.Group();S.add(mod);
  box(L,CH,C,mat(0x3D5568),0,CH/2,0,mod);                                // chassi do módulo
  box(L-.1,H-CH,C-.1,mat(0xE9E4DA),0,CH+(H-CH)/2,0,mod);                 // corpo
  box(L+.2,.14,C+.3,mat(0x5B6672),0,H+.07,0,mod);                        // cobertura
  var cx=L/2-.2,cz=C/2+.05,cantos=[[-cx,-cz],[cx,-cz],[-cx,cz],[cx,cz]];
  cantos.forEach(function(c){var o=new THREE.Mesh(new THREE.TorusGeometry(.16,.05,8,20),mat(0xF2B233));o.position.set(c[0],CH+.05,c[1]);mod.add(o);}); // olhais nos 4 cantos do chassi
  var bal=new THREE.Group();S.add(bal);                                  // balancim: quadro de vigas acima do módulo
  box(L,.25,.25,mat(AMARELO),0,0,cz,bal);box(L,.25,.25,mat(AMARELO),0,0,-cz,bal);
  box(.25,.25,C+.1,mat(AMARELO),-cx,0,0,bal);box(.25,.25,C+.1,mat(AMARELO),cx,0,0,bal);
  var gancho=new THREE.Mesh(new THREE.TorusGeometry(.3,.08,8,20),mat(0x333333));S.add(gancho);
  var cabos=new THREE.LineSegments(new THREE.BufferGeometry(),new THREE.LineBasicMaterial({color:0x2A2F35}));cabos.frustumCulled=false;S.add(cabos);
  function v(x,y,z){return new THREE.Vector3(x,y,z);}
  var CAM=[[0,[27,15,27],[4,2,0]],[7,[21,18,24],[2,5,0]],[11,[-3,19,29],[-3,5,0]],[14,[-24,13,24],[-6,1.5,0]],[DUR,[-29,15,29],[-6,1.5,0]]];
  var api={dur:DUR,update:function(t,wide){
    var x=lerp(XC,XR,seg(t,7,11)),y=t<11?lerp(1.2,TOPO,seg(t,3,7)):lerp(TOPO,.5,seg(t,11,14));
    mod.position.set(x,y,0);
    var bY=y+H+2.2,hY=bY+2.6,pts=[];
    bal.position.set(x,bY,0);gancho.position.set(x,hY,0);
    cantos.forEach(function(c){
      pts.push(v(x+c[0],bY,c[1]),v(x+c[0],y+CH+.05,c[1])); // cabo vertical: balancim → olhal
      pts.push(v(x+c[0],bY,c[1]),v(x,hY,0));               // eslinga: balancim → gancho
    });
    pts.push(v(x,hY,0),v(x,hY+30,0));                     // cabo do guindaste
    cabos.geometry.setFromPoints(pts);
    st.camKeys(CAM,t,wide);
    api.num='';
    api.leg=t<11?'Cabos verticais: só tração nos olhais; a parede não é comprimida.':'Balancim de içamento e guindaste da classe certa: itens de regra no orçamento.';
  }};
  return Object.assign(api,st);
}
```

E trocar a linha `var CENAS={'36min':cena36,'casa-viaja':cenaCasa};` por:

```js
var CENAS={'36min':cena36,'casa-viaja':cenaCasa,'icamento':cenaIcamento};
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_site.py`
Expected: `OK` e `OK`. O `check_site.py` garante que o portfólio e as maquetes dele continuam intactos.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/tests/check_historia.py portfolio/site/maquetes.js
git commit -m "maquetes: cena do içamento (balancim, cabos verticais) ligada ao scroll

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Acabamento, conferência visual e changelog

**Files:**
- Modify: `portfolio/tests/check_historia.py`, `portfolio/site/index.html` (CSS do relógio), `portfolio/revisao/CHANGELOG.md`

- [ ] **Step 1: Escrever o teste do relógio**

Em `checar_css()`, logo depois da linha `            check(cr >= 4.5, f"{var} sobre a faixa: {cr:.2f}:1 no pior caso (mín. 4,5)")`:

```python
    relogio = re.search(r"--relogio:\s*#([0-9A-Fa-f]{6})", css)
    check(relogio is not None and contraste(tuple(int(relogio.group(1)[i:i + 2], 16) for i in (0, 2, 4)), fundo) >= 3.0,
          "relógio da maquete (texto grande, negrito) sobre a faixa: mínimo 3:1 no pior caso")
    check(re.search(r"\.hud b\{[^}]*background:var\(--scrim\)", css) is not None, "o relógio da maquete fica sobre a faixa escura")
    check(".js-historia .palco .hud b:empty{display:none}" in css, "sem número no relógio (içamento), a faixa do relógio some")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py`
Expected: `FALHOU:` com `o relógio da maquete fica sobre a faixa escura` e `sem número no relógio (içamento), a faixa do relógio some`.

- [ ] **Step 3: Pôr a faixa atrás do relógio**

Em `index.html`, trocar a linha

```css
.js-historia .palco .hud b{font-family:var(--display);font-weight:700;font-size:clamp(1.8rem,5vw,3rem);line-height:1;color:var(--relogio);font-variant-numeric:tabular-nums}
```

por

```css
.js-historia .palco .hud b{font-family:var(--display);font-weight:700;font-size:clamp(1.8rem,5vw,3rem);line-height:1;color:var(--relogio);font-variant-numeric:tabular-nums;background:var(--scrim);padding:4px 10px;display:inline-block}
.js-historia .palco .hud b:empty{display:none}
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 portfolio/tests/check_historia.py --navegador`
Expected: `OK`

- [ ] **Step 5: Screenshots (celular e desktop, WebGL ligado)**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/f9d44ef5-7d41-4ced-9ebe-ca35da9a73fc/scratchpad python3 - <<'EOF'
import base64, os, sys, time
sys.path.insert(0, "portfolio/tests")
import check_historia as c
S = os.environ["S"]
for largura in (390, 1280):
    for passo in ("tese", "origem", "obra", "sige", "icamento", "whatsapp", "zip", "convite"):
        with c.chromium(largura, ("--enable-unsafe-swiftshader",)) as ws:
            ws.comando("Page.navigate", url=f"http://127.0.0.1:{c.PORTA}/site/index.html")
            time.sleep(1.5)
            ws.avaliar(f"(function(){{var r=document.getElementById('{passo}').getBoundingClientRect();"
                       f"window.scrollTo(0,scrollY+r.top+r.height*.4-innerHeight/2);}})()")
            time.sleep(4)
            png = ws.comando("Page.captureScreenshot", format="png")["data"]
        open(f"{S}/linha-{largura}-{passo}.png", "wb").write(base64.b64decode(png))
print("ok")
EOF
```

Abrir as 16 imagens com a ferramenta Read. Para economizar, junte-as antes com `magick <arquivos> +append -resize 45% <saída>`.
Expected:
- (a) Em todas as cenas, a frase fica centrada na faixa escura, com a data em laranja-claro acima e o "Ver…" abaixo; nada cortado e nenhuma rolagem horizontal.
- (b) Na régua do cabeçalho, o marco ativo aparece como bolinha ferrugem, e à direita fica a data de início do capítulo (`2017`, `fev/2025`, `mai/2026`…; `2017–2026` nas cenas de moldura).
- (c) `origem` e `obra` mostram o fundo tipográfico ("2017", "5×") no canto inferior esquerdo.
- (d) Em `icamento`, aparecem o balancim, os cabos na vertical, o módulo e a carreta. Se a guarda de fps cair, aparece a imagem de reserva.
- (e) Em `zip`, o relógio aparece sobre a faixa escura.
- (f) **A 1280 px, uma faixa na base das cenas 3D é efeito da captura headless** (pixels transparentes; o canvas mede 1280×800). Não mexer.

Se (a) a (e) falhar, corrigir o CSS em `index.html` e rodar de novo `python3 portfolio/tests/check_historia.py --navegador` antes de continuar.

- [ ] **Step 6: Conferências manuais (não dá para automatizar aqui)**

Registrar no changelog (Step 7) o que ficou para o Cássio conferir:
- iPhone real (Safari): o palco não pula quando a barra de endereço recolhe; a régua rola sem arrastar a página.
- Zoom de texto a 200%: saltar pela régua deixa o título visível abaixo da barra.
- VoiceOver ou NVDA: a régua é lida como lista de 17 links "data + marco", com o atual indicado.
- DevTools, Memória: rolar a página toda num celular médio sem travar com as três maquetes.

- [ ] **Step 7: Changelog**

Acrescentar ao fim de `portfolio/revisao/CHANGELOG.md`:

```markdown

---

# Rodada 6 — a história na linha do tempo, 23/09/2026

- Pesquisa com as 5 personas (rodada 2) em `docs/superpowers/research/2026-09-23-historia-v2/`; spec em `docs/superpowers/specs/2026-09-23-historia-linha-do-tempo-design.md`.
- `site/index.html`: 17 capítulos em ordem cronológica, de 2017 a set/2026, cada um com data (`<time>`), frase, ressalva e link "Ver…" para a seção do portfólio; vínculos simultâneos ditos com o tipo de contrato; fundos tipográficos nos capítulos sem imagem; barra com o status atual.
- Régua de tempo no cabeçalho (`nav` + `ol`, um `aria-current="step"`, foco no título ao saltar).
- `site/maquetes.js`: cena `icamento` (o módulo sobe pelo balancim, cabos verticais), ligada ao scroll.
- Relógio da maquete sobre faixa escura (contraste ≥ 3:1).
- `tests/check_historia.py`: cronologia, datas contra o currículo, links únicos, régua, WebGL real do içamento.
- Para o Cássio conferir: iPhone real, zoom 200%, leitor de tela e memória das três maquetes. Em aberto: estágio/júnior; UNIFEI 2020–2024 (currículo) ou 2022–2024 (conversa) — a página não mostra o ano de entrada.
```

- [ ] **Step 8: Checagem final e commit**

Run: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_site.py`
Expected: `OK` e `OK`

```bash
cd /home/runner/workspace && git add portfolio/tests/check_historia.py portfolio/site/index.html portfolio/revisao/CHANGELOG.md
git commit -m "História: relógio da maquete legível; changelog da rodada 6

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```
