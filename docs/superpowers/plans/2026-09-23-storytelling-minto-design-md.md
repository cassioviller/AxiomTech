# Storytelling Minto + DESIGN.md — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Escrever o `DESIGN.md` do portfólio e reescrever os 10 casos do site em estilo Minto (resultado primeiro, autoria em primeira pessoa), além de revisar as legendas que só descrevem a tela para que digam a decisão. Nenhum número conferido pode mudar.

**Architecture:** O site é um HTML estático único (`portfolio/site/index.html`, com CSS inline). Todo o trabalho é edição de texto e marcação nesse arquivo, mais um arquivo de documentação novo. Um script Python só com biblioteca padrão (`portfolio/tests/check_site.py`) protege os invariantes. Ele compara os números do `<main>` com o commit de referência `2a686cf`, confere que as ressalvas honestas continuam no texto, que as tags estão balanceadas e que cada caso abre pelo resultado.

**Tech Stack:** HTML/CSS estático; Python 3.12, stdlib apenas (não há `pytest` no ambiente); Chromium headless (`chromium`) para a conferência visual; ImageMagick (`magick`) para recortar screenshots.

**Spec:** Não há documento de spec separado. O plano parte de três fontes: a pesquisa de storytelling e design registrada nesta conversa (Minto: resultado → argumentos → provas; leitura rápida; autoria explícita; trade-offs honestos), o `portfolio/revisao/CHANGELOG.md` da rodada 3 (ressalvas que não podem sumir) e o formato de 9 seções do repositório [VoltAgent/awesome-design-md](https://github.com/voltagent/awesome-design-md).

## Global Constraints

- Nenhum número do texto visível de `<main>` pode entrar ou sair. O conjunto de números tem de ser idêntico ao de `2a686cf:portfolio/site/index.html`.
- Ressalvas que têm de continuar no texto, literalmente: `cópia do sistema`, `onde a empresa ligou`, `nos 19 serviços conferidos`, `ligadas empresa por empresa`, `assistentes de IA`, `sujeito à revisão do engenheiro responsável`, `Dados de exemplo do manual`.
- Autoria na Folha 02: as frases em primeira pessoa dizem que o trabalho foi feito **com o sistema** e não omitem que o desenvolvimento foi feito com assistentes de IA.
- Idioma: português do Brasil, no tom atual do site (frases curtas, travessões, sem jargão de marketing).
- Sem CSS novo e sem classes novas: reutilizar `<p><strong>Resultado.</strong>` (casos da Folha 02 e da Folha 04) e `<div><h5>Resultado</h5>` (casos do SIGE).
- `DESIGN.md` fica em `portfolio/DESIGN.md`, **não** em `portfolio/site/`, porque tudo em `site/` é publicado.
- Trabalhar no branch `storytelling-minto`, a partir do `main`, e fazer um commit por tarefa.

## Review Focus

1. **Número que muda ao reescrever.** Quem move uma frase pode digitar "R$ 500 mil" onde estava "R$ 500 mil" com espaço fino, ou arredondar. A pessoa espera o mesmo número de antes. O teste de conjunto de números da Task 1 cobre isso.
2. **Ressalva honesta que some.** Ao encurtar um caso, "cópia do sistema" ou "onde a empresa ligou" podem cair junto, e a pessoa espera continuar vendo o limite do que foi medido. O teste de ressalvas da Task 1 cobre isso.
3. **Autoria exagerada.** "Eu medi a obra inteira" sem dizer que foi com o sistema soa como trabalho manual que não aconteceu. O teste de "com o sistema" da Task 3 cobre isso.
4. **HTML quebrado ao mover blocos.** Um `</div>` a mais faz o `<details>` engolir o caso seguinte, e a pessoa espera cada caso abrir e fechar sozinho. O teste de balanço de tags da Task 1 cobre isso.
5. **Leitura no celular.** Com o resultado no topo, o primeiro caso de cada lista precisa continuar aberto (`<details open>`), senão o recrutador no celular não vê resultado nenhum. O teste de contagem de `<details open>` da Task 1 e as screenshots de 390 px da Task 7 cobrem isso.

---

## File Structure

- **Create** `portfolio/tests/check_site.py`: a checagem única. Cada tarefa acrescenta a sua verificação aqui.
- **Create** `portfolio/DESIGN.md`: a linguagem visual do site no formato awesome-design-md.
- **Modify** `portfolio/site/index.html`: os 10 casos (Folha 02: 3; Folha 03: 4; Folha 04: 3) e 5 legendas.
- **Modify** `portfolio/revisao/CHANGELOG.md`: nova seção "Rodada 4".

Os 10 casos, pelo título do `<h4>`:

| Folha | Casos |
|---|---|
| 02 Sistema de orçamento | "O cliente impôs um teto — e a resposta foi outra casa" · "R$ 24,5 milhões — e nenhuma quantidade no pacote do cliente" · "As regras do cliente viraram regra do sistema" |
| 03 SIGE | "O diário que estava no WhatsApp" · "O cliente confirma que leu" · "Da venda à obra" · "Compras com governança" |
| 04 Casas modulares | "O celeiro não cabe inteiro no caminhão" · "Empilhar encarece, geminar barateia" · "A planta do cliente não cabia no terreno dele" |

---

### Task 1: Script de checagem com os invariantes

**Files:**
- Create: `portfolio/tests/check_site.py`

**Interfaces:**
- Produces: `check(cond: bool, msg: str) -> None`; `casos(html: str) -> dict[str, str]` (título do `<h4>` → HTML interno de `<div class="body">`); a lista global `CASOS_MINTO: list[str]`, que as Tasks 3–5 preenchem; a execução `python3 portfolio/tests/check_site.py`, que sai com 0 e imprime `OK` quando tudo passa.

- [ ] **Step 1: Criar o branch**

```bash
cd /home/runner/workspace && git checkout -b storytelling-minto
```

- [ ] **Step 2: Escrever o script**

```python
#!/usr/bin/env python3
"""Checagens do site do portfólio.

Garante que reescrever texto não muda número conferido, não apaga ressalva
honesta, não quebra o HTML e que cada caso abre pelo resultado (Minto).
Uso: python3 portfolio/tests/check_site.py
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # portfolio/
SITE = ROOT / "site" / "index.html"
BASE = "2a686cf"  # commit de referência dos números conferidos
FALHAS = []

# Casos já reescritos em Minto (título exato do <h4>). As Tasks 3–5 preenchem.
CASOS_MINTO = []

RESSALVAS = [
    "cópia do sistema",
    "onde a empresa ligou",
    "nos 19 serviços conferidos",
    "ligadas empresa por empresa",
    "assistentes de IA",
    "sujeito à revisão do engenheiro responsável",
    "Dados de exemplo do manual",
]


def check(cond, msg):
    if not cond:
        FALHAS.append(msg)


def main_html(html):
    return html[html.index("<main"):html.index("</main>")]


def texto(html):
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def numeros(html):
    return set(re.findall(r"\d+(?:[.,]\d+)*", texto(main_html(html))))


def casos(html):
    """título do <h4> → HTML interno do <div class="body"> de cada caso numerado."""
    out = {}
    for parte in html.split("<details")[1:]:
        if '<span class="n">' not in parte:
            continue
        seg = parte.split("</details>")[0]
        titulo = re.search(r"<h4>(.*?)</h4>", seg).group(1)
        corpo = seg[seg.index('<div class="body">') + len('<div class="body">'):]
        corpo = corpo[:corpo.rindex("</div>")]
        out[titulo] = corpo.strip()
    return out


class Balanco(HTMLParser):
    TAGS = {"div", "details", "figure", "section", "ul", "ol", "main", "summary"}

    def __init__(self):
        super().__init__()
        self.pilha = []
        self.erros = []

    def handle_starttag(self, tag, attrs):
        if tag in self.TAGS:
            self.pilha.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag not in self.TAGS:
            return
        if not self.pilha or self.pilha[-1][0] != tag:
            self.erros.append(f"</{tag}> inesperado na linha {self.getpos()[0]}")
        else:
            self.pilha.pop()


def checar_invariantes(atual, base):
    na, nb = numeros(atual), numeros(base)
    check(na == nb, f"números mudaram — novos: {sorted(na - nb)}; sumiram: {sorted(nb - na)}")
    t = texto(atual)
    for r in RESSALVAS:
        check(r in t, f"ressalva sumiu: {r!r}")
    b = Balanco()
    b.feed(atual)
    check(not b.erros and not b.pilha, f"tags desbalanceadas: {b.erros[:3]} abertas: {b.pilha[:3]}")
    check(atual.count("<details open>") == 3, "o primeiro caso de cada lista precisa continuar <details open> (3 no total)")


def checar_minto(atual):
    cs = casos(atual)
    for titulo in CASOS_MINTO:
        corpo = cs.get(titulo)
        check(corpo is not None, f"caso não encontrado: {titulo!r}")
        if corpo is None:
            continue
        check(
            corpo.startswith("<p><strong>Resultado.</strong>") or corpo.startswith("<div><h5>Resultado</h5>"),
            f"caso não abre pelo resultado: {titulo!r}",
        )


def main():
    atual = SITE.read_text(encoding="utf-8")
    base = subprocess.run(
        ["git", "show", f"{BASE}:portfolio/site/index.html"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    checar_invariantes(atual, base)
    checar_minto(atual)
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Rodar contra o site atual (os invariantes têm de passar desde já)**

Run: `python3 portfolio/tests/check_site.py`
Expected: `OK`

- [ ] **Step 4: Provar que o teste de números morde**

Run: `sed -i 's/R\$ 452.865/R$ 452.866/' portfolio/site/index.html && python3 portfolio/tests/check_site.py; git checkout portfolio/site/index.html`
Expected: `FALHOU:` com `números mudaram — novos: ['452.866']; sumiram: ['452.865']`, e depois o arquivo restaurado.

- [ ] **Step 5: Commit**

```bash
git add portfolio/tests/check_site.py
git commit -m "Checagem do site: números, ressalvas, tags e casos em Minto

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: DESIGN.md do portfólio

**Files:**
- Create: `portfolio/DESIGN.md`
- Modify: `portfolio/tests/check_site.py` (nova função `checar_design`)

**Interfaces:**
- Consumes: `check()` da Task 1.
- Produces: `checar_design(atual: str) -> None`, chamada em `main()`.

- [ ] **Step 1: Escrever o teste que falha**

Em `check_site.py`, acima de `def main():`:

```python
DESIGN = ROOT / "DESIGN.md"
SECOES_DESIGN = [
    "## 1. Tema visual e atmosfera",
    "## 2. Paleta de cores e papéis",
    "## 3. Tipografia",
    "## 4. Componentes",
    "## 5. Layout",
    "## 6. Profundidade e elevação",
    "## 7. Faça e não faça",
    "## 8. Comportamento responsivo",
    "## 9. Guia para agentes",
]


def checar_design(atual):
    check(DESIGN.exists(), "portfolio/DESIGN.md não existe")
    if not DESIGN.exists():
        return
    d = DESIGN.read_text(encoding="utf-8")
    for s in SECOES_DESIGN:
        check(s in d, f"DESIGN.md sem a seção {s!r}")
    raiz = re.findall(r":root[^{]*\{(.*?)\}", atual, flags=re.S)
    for hexa in sorted({h.upper() for bloco in raiz for h in re.findall(r"#[0-9A-Fa-f]{6}", bloco)}):
        check(hexa in d.upper(), f"DESIGN.md não documenta a cor {hexa}")
```

E em `main()`, depois de `checar_minto(atual)`:

```python
    checar_design(atual)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `FALHOU:` com `portfolio/DESIGN.md não existe`

- [ ] **Step 3: Escrever `portfolio/DESIGN.md`**

```markdown
# DESIGN.md — Cássio Viller · portfólio

Linguagem visual do site `portfolio/site/index.html`. Leia antes de mexer em qualquer página, folha de caso ou currículo: a ideia é que tudo pareça saído da mesma prancha.

## 1. Tema visual e atmosfera

**Prancha de obra.** O site se lê como um jogo de folhas de projeto: cada seção é uma "Folha 0X/08" com carimbo, cada número importante ganha uma linha de cota, e as maquetes 3D são a "vista" da folha. Papel fosco, tinta escura, um único acento ferrugem (a cor do aço de obra e da caneta de revisão) e azul-aço para o que é sistema. Sério, técnico, sem gradiente decorativo e sem ilustração genérica — as imagens são sempre telas reais, fotos de obra ou renders do projeto.

## 2. Paleta de cores e papéis

Tokens definidos em `:root`, com tema escuro por `prefers-color-scheme` e por `[data-theme="dark"]`.

| Token | Claro | Escuro | Papel |
|---|---|---|---|
| `--ground` | `#ECEBE6` | `#12171D` | fundo da página (papel) |
| `--surface` | `#FFFFFF` | `#1A2129` | cartões, tabelas, `details` |
| `--surface-2` | `#F5F4F0` | `#202932` | moldura de screenshot, linha de soma |
| `--ink` | `#171F29` | `#E9E7E1` | texto principal, carimbo |
| `--ink-2` | `#3C4652` | `#C4C8CC` | texto corrido |
| `--muted` | `#5B6672` | `#93A0AD` | legendas, rótulos mono |
| `--accent` | `#B5440E` | `#F07A3E` | cota, eyebrow, botão, número em destaque — um por bloco |
| `--accent-ink` | `#FFFFFF` | `#161616` | texto sobre o acento |
| `--steel` / `--steel-panel` | `#2E4763` | `#9DBBD8` | links, faixas de caso (fundo azul-aço) |
| `--steel-soft` | `#DCE4EC` | `#243342` | fundo suave de sistema |
| `--rule` | `#D3D1CA` | `#2E3A47` | fios e bordas |
| `--rule-soft` | `#E4E2DC` | `#26313C` | divisórias internas |
| `--ok` | `#2F7A4A` | `#6BC28A` | coluna "Medido" |
| `--warn` | `#B7791F` | `#E0A54A` | coluna "Ainda falta", pendências |

Nas faixas azul-aço (`.case-banner`, `.savings`), o texto é `#fff`, o secundário é `#D7E1EC` e o eyebrow é `#F2B896`.

## 3. Tipografia

- **Display** — `Barlow Condensed` 500/600/700 (`--display`): `h1`–`h3`, números grandes (`.stats b`, `.timeline b`, HUD da maquete). `h1` em caixa-alta, `clamp(2.8rem,7vw,4.4rem)` no hero; `h2` `clamp(2rem,4.5vw,2.9rem)`; `h3` 1.55rem.
- **Texto** — `IBM Plex Sans` 400/500/600 (`--body`), 16px, `line-height:1.6`; `h4` usa esta família a 1.2rem.
- **Técnico** — `IBM Plex Mono` 400/500 (`--mono`): eyebrow, carimbo, cota, legendas, rótulos `h5` dos casos — sempre pequeno (.68–.82rem), caixa-alta com `letter-spacing` .06–.14em.
- Números tabulares (`font-variant-numeric:tabular-nums`) em toda cifra que se compara.

## 4. Componentes

- **Carimbo** (`.carimbo`): faixa mono com borda de tinta — `Folha 0X/08` invertido, título da folha, data/local. Abre toda seção.
- **Cota** (`.cota`): linha de dimensão em ferrugem entre dois valores, com o intervalo no meio; desenha ao entrar na tela.
- **Três colunas** (`.tres`): O problema · O que fiz · Resultado — a coluna Resultado com fio ferrugem.
- **Stats** (`.stats`, `.stats.s3`): números em display com uma frase de origem embaixo.
- **Linha do tempo** (`.timeline`) com lupa circular (`.lupa`) sobre o relógio.
- **Passo a passo** (`.walk` + `.shot`): screenshot em moldura, legenda com título em display e a decisão que a tela mostra.
- **Casos** (`.stories` > `details`): resumo com número mono, título em display e `+` que gira; corpo em Minto (resultado primeiro).
- **Mais** (`details.mais`): detalhe recolhido com `+`/`−` em ferrugem.
- **Sem maquiagem** (`.honest`): duas colunas, "Medido" (fio verde) e "Ainda falta" (fio âmbar).
- **Maquete** (`.maquete`): canvas three.js sobre imagem de fallback, HUD com relógio em display ferrugem, botão Pausar.
- **Botões** (`.btn`, `.btn.big`, `.btn.ghost`): mono caixa-alta, cantos de 2px.

## 5. Layout

- Grade de duas colunas: trilho fixo de 200px (navegação por folha) + conteúdo até 820px; container de 1180px com 20px de respiro lateral.
- Seções com 56px de padding vertical, separadas por fio `--rule`.
- Blocos de texto limitados a 62–66ch.
- Grades internas de 2–4 colunas com `gap` de 12–22px.

## 6. Profundidade e elevação

Plano, como papel. Profundidade só por fio (1px `--rule`) e troca de superfície (`--ground` → `--surface` → `--surface-2`). Sombra só na lupa da linha do tempo. Cantos de 2px; nada de cartões arredondados ou flutuando.

## 7. Faça e não faça

**Faça**
- Todo número com origem na mesma frase ("medidos: 11h35 → 12h11").
- Resultado primeiro; depois o que fiz; depois a prova.
- Legenda que diz a decisão da tela, não o nome da tela.
- Ressalva honesta visível perto do número que ela limita.
- Um acento ferrugem por bloco.

**Não faça**
- Gradiente, glassmorphism, ícone decorativo, foto de banco.
- Número sem ressalva quando a fonte tem ressalva ("0,25%" sem "nos 19 serviços conferidos").
- Misturar telas do SIGE e do sistema de orçamento no mesmo caso.
- Nome de cliente, e-mail ou margem de obra real em imagem.

## 8. Comportamento responsivo

- ≤959px: o trilho some e entra a barra superior fixa com o botão "Me mande uma obra"; o carimbo do hero some.
- ≤720px: grades viram uma coluna (`.tres`, `.walk`, `.honest`, `.calc`); `.stats` vira 2×2; antes/depois ganha rótulos inline.
- ≤560px: o carimbo quebra em duas linhas.
- `prefers-reduced-motion`: sem maquete 3D (fica a imagem), sem animação da cota, rolagem sem suavização.
- Imagens em WebP, `loading="lazy"`, `alt` descritivo com os números da tela.

## 9. Guia para agentes

Ao criar ou alterar uma seção do portfólio: comece pelo carimbo e pela cota; use só os tokens da seção 2 e as três famílias da seção 3; escreva casos em Minto (resultado → o que fiz → prova), em primeira pessoa e sem mudar número conferido; rode `python3 portfolio/tests/check_site.py` antes de commitar; confira em 1280px e 390px, nos temas claro e escuro.
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add portfolio/DESIGN.md portfolio/tests/check_site.py
git commit -m "DESIGN.md do portfólio no formato awesome-design-md

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Casos da Folha 02 (sistema de orçamento) em Minto

**Files:**
- Modify: `portfolio/site/index.html` (os três `<details>` dentro de `<section id="sistema">`)
- Modify: `portfolio/tests/check_site.py`

**Interfaces:**
- Consumes: `CASOS_MINTO`, `casos()` e `check()` da Task 1.

- [ ] **Step 1: Escrever o teste que falha**

Em `check_site.py`, trocar `CASOS_MINTO = []` por:

```python
CASOS_MINTO = [
    "O cliente impôs um teto — e a resposta foi outra casa",
    "R$ 24,5 milhões — e nenhuma quantidade no pacote do cliente",
    "As regras do cliente viraram regra do sistema",
]
```

E no fim de `checar_minto`:

```python
    check("O que o sistema fez" not in atual, "ainda há 'O que o sistema fez' — a autoria deve ser 'O que fiz'")
    for titulo in CASOS_MINTO[:3]:
        corpo = cs.get(titulo, "")
        check("com o sistema" in corpo, f"caso da Folha 02 sem 'com o sistema' no O que fiz: {titulo!r}")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `FALHOU:` com `caso não abre pelo resultado` ×3 e `ainda há 'O que o sistema fez'`.

- [ ] **Step 3: Reescrever o caso 01 ("O cliente impôs um teto…")**

Substituir as três linhas `<p><strong>Desafio.</strong>…`, `<p><strong>O que o sistema fez.</strong>…` e `<p><strong>Resultado.</strong>…` deste caso por:

```html
        <p><strong>Resultado.</strong> R$ 452.865 e 54 dias de obra, com folga de R$ 47 mil abaixo do teto.</p>
        <p><strong>Desafio.</strong> A casa chegou como croqui à mão, fotografado pelo WhatsApp. Orçada, fechou em R$ 1,18 milhão. O cliente pôs um teto de R$ 500 mil.</p>
        <p><strong>O que fiz.</strong> Mostrei com o sistema, com números, que trocar materiais por opções mais baratas tirava só 15% — não bastava. Então redesenhei a casa que cabia no teto, com 93,5 m² fechados, e recalculei tudo pelas mesmas regras. Precifiquei um a um cada acréscimo que o cliente poderia querer de volta (varanda, garagem, pé-direito maior), para ele escolher com o valor à vista.</p>
```

A linha `<p class="folha-link">…` continua depois delas, sem mudança.

- [ ] **Step 4: Reescrever o caso 02 ("R$ 24,5 milhões…")**

Substituir as três linhas `<p><strong>…` deste caso por:

```html
        <p><strong>Resultado.</strong> Uma proposta de obra completa de R$ 24,5 milhões. Quando a direção mudou o papel da empresa, de construtora para subempreiteira, gerei uma segunda revisão, de R$ 9,6 milhões, e mantive a primeira intacta para comparação.</p>
        <p><strong>Desafio.</strong> Restaurante, plataforma de ônibus e posto de estrada para uma rede de rodovia. O cliente entregou um desenho de 756 MB e documentos de referência, sem uma única quantidade e sem um único preço. O documento mais completo do pacote era a proposta de um concorrente.</p>
        <p><strong>O que fiz.</strong> Medi com o sistema, no próprio desenho, as paredes e as coberturas da obra inteira. Onde o desenho não bastava — o posto, que não vinha desenhado —, montei o projeto a partir da implantação do memorial e o fiz entrar pelo mesmo caminho, declarado como estimativa. Saíram orçamento, prazo e três propostas de tamanhos diferentes.</p>
```

- [ ] **Step 5: Reescrever o caso 03 ("As regras do cliente…")**

Substituir as três linhas `<p><strong>…` deste caso por:

```html
        <p><strong>Resultado.</strong> Uma proposta de R$ 964.917 em três versões, de 4, 11 e 18 páginas, geradas do mesmo dado. A verificação automática levou as menções a informação interna de 71 para 0.</p>
        <p><strong>Desafio.</strong> Fechamentos internos de cinco prédios de um centro logístico, com um documento de contratação cheio de regras sobre o que devia estar dentro do preço por metro quadrado.</p>
        <p><strong>O que fiz.</strong> Fiz com o sistema a leitura das regras do documento do cliente, guardando a frase exata de cada uma, e pus dentro do preço o que ele mandava incluir. Por decisão da direção, trouxe também os 12 itens que o documento deixava por conta do cliente, cada um medido. A proposta passou por cinco refinamentos — uma página por prédio, retirada de dado sensível, vistas 3D, versão compacta e versão curta — e em nenhum deles o preço se moveu um centavo sem decisão.</p>
```

- [ ] **Step 6: Rodar e ver passar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add portfolio/site/index.html portfolio/tests/check_site.py
git commit -m "Folha 02: casos em Minto, resultado primeiro e autoria em primeira pessoa

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: Casos da Folha 03 (SIGE) em Minto

**Files:**
- Modify: `portfolio/site/index.html` (os quatro `<details>` dentro de `<section id="sige">`)
- Modify: `portfolio/tests/check_site.py`

**Interfaces:**
- Consumes: `CASOS_MINTO` e `checar_minto()`, já estendidos na Task 3.

- [ ] **Step 1: Escrever o teste que falha**

Acrescentar ao fim da lista `CASOS_MINTO`:

```python
    "O diário que estava no WhatsApp",
    "O cliente confirma que leu",
    "Da venda à obra",
    "Compras com governança",
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `FALHOU:` com `caso não abre pelo resultado` para os 4 títulos do SIGE.

- [ ] **Step 3: Caso 01 ("O diário que estava no WhatsApp")**

Recortar a linha inteira `<div><h5>Resultado</h5><p>Sem esses 23 dias, …</p></div>` (texto inalterado) e colá-la como **primeira** linha dentro de `<div class="body">` deste caso, antes de `<div><h5>O problema</h5>`. Nada mais muda.

- [ ] **Step 4: Caso 02 ("O cliente confirma que leu")**

Inserir como primeira linha dentro de `<div class="body">`:

```html
        <div><h5>Resultado</h5><p>A confirmação de leitura virou registro: <b>quem, quando, de onde e sobre qual conteúdo</b>, com recibo em PDF — e, se o diário mudar depois, a ciência aparece como "alterado". A ciência mostrada neste site foi feita na cópia do sistema, com um cadastro de exemplo.</p></div>
```

E, no `<div><h5>O que fiz</h5>` do mesmo caso, trocar `O representante do cliente tem uma senha só dele, que vale apenas para aquela obra.` por `Dei ao representante do cliente uma senha só dele, que vale apenas para aquela obra.`

- [ ] **Step 5: Caso 03 ("Da venda à obra")**

Inserir como primeira linha dentro de `<div class="body">`:

```html
        <div><h5>Resultado</h5><p>Aprovar a proposta abre a obra <b>numa só ação</b>, com cliente, itens a medir e custos previstos — sem recadastro. O cronograma vem junto quando já foi revisado; senão, o gestor o confere na primeira abertura.</p></div>
```

E, no `<div><h5>O que fiz</h5>`, trocar `Aprovar a proposta passou a abrir a obra numa só ação.` por `Liguei a aprovação da proposta à abertura da obra.`

- [ ] **Step 6: Caso 04 ("Compras com governança")**

Inserir como primeira linha dentro de `<div class="body">`:

```html
        <div><h5>Resultado</h5><p>Onde o controle está ligado, cada compra responde às três perguntas: <b>quem pediu, quem autorizou e o que chegou</b>. A conta a pagar nasce do recebimento conferido, e a equipe tem um manual ilustrado de 22 passos.</p></div>
```

E, no `<div><h5>O que fiz</h5>`, trocar `Onde o controle está ligado, cada compra passa a seguir um ciclo de 9 etapas, do pedido ao pagamento, e mostra em que etapa está.` por `Desenhei um ciclo de 9 etapas, do pedido ao pagamento, em que cada compra mostra em que etapa está.`

- [ ] **Step 7: Rodar e ver passar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `OK`. O `22` do Resultado do caso 04 já existe no texto, então o conjunto de números não muda.

- [ ] **Step 8: Commit**

```bash
git add portfolio/site/index.html portfolio/tests/check_site.py
git commit -m "Folha 03: casos do SIGE em Minto, resultado primeiro

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Casos da Folha 04 (casas modulares) em Minto

**Files:**
- Modify: `portfolio/site/index.html` (os três `<details>` dentro de `<section id="modular">`)
- Modify: `portfolio/tests/check_site.py`

- [ ] **Step 1: Escrever o teste que falha**

Acrescentar ao fim de `CASOS_MINTO`:

```python
    "O celeiro não cabe inteiro no caminhão",
    "Empilhar encarece, geminar barateia",
    "A planta do cliente não cabia no terreno dele",
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `FALHOU:` com `caso não abre pelo resultado` para os 3 títulos.

- [ ] **Step 3: Caso 01 ("O celeiro não cabe…")**

Inserir como primeira linha dentro de `<div class="body">`:

```html
        <p><strong>Resultado.</strong> <strong>Duas caixas volumétricas com o térreo completo mais o telhado como kit</strong>, em três viagens — a terceira em carreta comum com autorização simples, não em prancha.</p>
```

E, no parágrafo seguinte, trocar `A rota adotada: <strong>duas caixas volumétricas com o térreo completo mais o telhado como kit</strong>, em três viagens — a terceira em carreta comum com autorização simples, não em prancha.` por `Daí a rota acima.`

- [ ] **Step 4: Caso 02 ("Empilhar encarece…")**

Inserir como primeira linha dentro de `<div class="body">`:

```html
        <p><strong>Resultado.</strong> Geminar quatro unidades corta o custo por unidade em cerca de <strong>28%</strong>; empilhar sozinho encarece. Isso definiu como o produto seria oferecido a investidores.</p>
```

E, no parágrafo seguinte, apagar a frase final ` Isso definiu como o produto seria oferecido a investidores.` (com o espaço inicial).

- [ ] **Step 5: Caso 03 ("A planta do cliente…")**

Inserir como primeira linha dentro de `<div class="body">`:

```html
        <p><strong>Resultado.</strong> Antes da obra, mostrei que no lote de 9,50 m cabem <strong>três módulos, não quatro</strong> — nem a planta que o próprio cliente trouxe cabia — e desenhei o A-21 para esse lote.</p>
```

- [ ] **Step 6: Rodar e ver passar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add portfolio/site/index.html portfolio/tests/check_site.py
git commit -m "Folha 04: casos das casas modulares em Minto

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: Legendas que dizem a decisão

**Files:**
- Modify: `portfolio/site/index.html` (galerias de `#sistema` e `#modular`)
- Modify: `portfolio/tests/check_site.py` (nova função `checar_legendas`)

**Interfaces:**
- Produces: `checar_legendas(atual: str) -> None`, chamada em `main()`.

- [ ] **Step 1: Escrever o teste que falha**

Acima de `def main():`:

```python
LEGENDAS = {
    # antiga → nova
    "Rede de restaurantes de rodovia · o prédio medido e desenhado pelo sistema a partir do arquivo do cliente, cobertura em corte":
        "Rede de restaurantes de rodovia · sem nenhuma quantidade no pacote, o prédio foi medido no próprio arquivo do cliente — cobertura em corte",
    "B-36 · celeiro 6 × 6 m com sótão, entregue em duas caixas":
        "B-36 · o celeiro 6 × 6 m não cabe inteiro no caminhão: vai em duas caixas",
    "B-36 · interior com bancada sob a viga da junção":
        "B-36 · a viga da junção ficou aparente — sai mais barato que fechar — e a bancada vai embaixo dela",
    "Kitnet modular 30 m² · layouts validados por código":
        "Kitnet modular 30 m² · cada layout passa pelo validador de colisões antes de ser desenhado",
    "Como cada caixa viaja e como fica depois de unida":
        "Como cada caixa viaja e onde fica a junção depois de unida",
}


def checar_legendas(atual):
    for antiga, nova in LEGENDAS.items():
        check(antiga not in atual, f"legenda antiga ainda no site: {antiga[:50]!r}")
        check(nova in atual, f"legenda nova ausente: {nova[:50]!r}")
```

E em `main()`, depois de `checar_design(atual)`:

```python
    checar_legendas(atual)
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `FALHOU:` com 10 linhas (5 antigas presentes, 5 novas ausentes).

- [ ] **Step 3: Aplicar as trocas**

```bash
cd /home/runner/workspace && python3 - <<'EOF'
import importlib.util
spec = importlib.util.spec_from_file_location("c", "portfolio/tests/check_site.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
p = "portfolio/site/index.html"; s = open(p, encoding="utf-8").read()
for antiga, nova in c.LEGENDAS.items():
    assert s.count(antiga) == 1, antiga
    s = s.replace(antiga, nova)
open(p, "w", encoding="utf-8").write(s)
EOF
```

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 portfolio/tests/check_site.py`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add portfolio/site/index.html portfolio/tests/check_site.py
git commit -m "Legendas das galerias dizem a decisão, não o nome da tela

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Conferência visual, changelog e merge

**Files:**
- Modify: `portfolio/revisao/CHANGELOG.md`

- [ ] **Step 1: Screenshots em 1280 e 390 px**

```bash
S=/tmp/claude-1000/-home-runner-workspace/f9d44ef5-7d41-4ced-9ebe-ca35da9a73fc/scratchpad
cd /home/runner/workspace/portfolio/site && (python3 -m http.server 5055 --bind 127.0.0.1 >/dev/null 2>&1 &) && sleep 1
chromium --headless --no-sandbox --disable-gpu --hide-scrollbars --window-size=1280,20000 --virtual-time-budget=8000 --screenshot=$S/d.png http://127.0.0.1:5055/ 2>/dev/null
chromium --headless --no-sandbox --disable-gpu --hide-scrollbars --window-size=390,30000 --virtual-time-budget=8000 --screenshot=$S/m.png http://127.0.0.1:5055/ 2>/dev/null
pkill -f "http.server 5055"
```

Recortar com `magick $S/m.png -crop 390x2400+0+<y> +repage` nas alturas dos três primeiros casos abertos e ler as imagens.
Expected: em cada lista, o primeiro caso aberto começa por "Resultado." (ou pelo rótulo `RESULTADO`), sem texto sobreposto nem rolagem horizontal.

- [ ] **Step 2: Registrar no changelog**

Acrescentar ao fim de `portfolio/revisao/CHANGELOG.md`:

```markdown

---

# Rodada 4 — storytelling Minto e DESIGN.md, 23/09/2026

- `portfolio/DESIGN.md`: linguagem visual do site no formato awesome-design-md (9 seções, todos os tokens de `:root`).
- 10 casos em Minto (resultado → o que fiz → prova): Folha 02 com "O que fiz" em primeira pessoa e "com o sistema"; Folha 03 com Resultado no topo (casos 02–04 ganharam Resultado a partir de fatos já no site); Folha 04 com Resultado no topo.
- 5 legendas de galeria reescritas para dizer a decisão.
- `portfolio/tests/check_site.py`: números iguais a `2a686cf`, ressalvas presentes, tags balanceadas, casos abrindo pelo resultado, DESIGN.md completo.
```

- [ ] **Step 3: Checagem final e commit**

Run: `python3 portfolio/tests/check_site.py`
Expected: `OK`

```bash
git add portfolio/revisao/CHANGELOG.md
git commit -m "Changelog da rodada 4

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

- [ ] **Step 4: Merge no main**

```bash
git checkout main && git merge --ff-only storytelling-minto && git branch -d storytelling-minto
```

Avisar que o site no ar só muda depois de republicar pelo **Deploy** do Replit.
