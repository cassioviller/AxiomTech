# O filme como trailer da história — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trazer o filme do `filme-codigo-fonte.zip` para o projeto com o texto corrigido, gerar o MP4 aqui mesmo e publicá-lo como trailer, só por clique e com transcrição, na página da história. A frase "Comecei no centavo, não na parede." vira "Comecei pela contabilidade, não pela obra." nos três lugares em que aparece.

**Architecture:** O filme passa a morar em `portfolio/filme/`, fora do site publicado, com um script que aplica as correções ao `film.html` original e o `render.py`, que roda com o Chromium do sistema. O vídeo leve sai em `portfolio/site/video/`. Um `check_filme.py` novo aplica ao filme as mesmas regras de honestidade da página: números, ressalvas, legendas legíveis e a frase igual nos três lugares. O `check_historia.py` ganha a checagem da seção do trailer, com a duração tirada do próprio vídeo.

**Tech Stack:** HTML/CSS estático; three.js r128 (só no filme, fora do site); Python 3.12 (stdlib + Playwright para o render); Chromium do sistema; ffmpeg/ffprobe.

**Spec:** `docs/superpowers/specs/2026-09-23-filme-trailer-design.md`. A pesquisa das 5 personas está em `docs/superpowers/research/2026-09-23-filme/`.

**Ensaio:** este plano foi executado do começo ao fim, a partir do próprio texto, num clone descartável do repositório. Os 5 commits saíram como descritos e cada `Expected:` bateu:
- `corrigir_filme.py`, aplicado ao `film.html` do zip, gera um arquivo idêntico ao filme corrigido;
- o render completo levou 12 min 19 s e produziu 85,0 s, H.264 960×540, 2,7 MB;
- cada teste falhou pelo motivo esperado e depois passou;
- a suíte final (`--navegador`) fica verde.

O ensaio achou um bug que já existe no site: o palco cobre a ficha no fim da página (Task 4, Steps 4–5).

## Global Constraints

- Frase da contabilidade, idêntica nos três lugares: **"Comecei pela contabilidade, não pela obra."** A frase "centavo, não na parede" não pode aparecer em nenhum deles.
- As legendas, a ordem (`ORDER=[5,0,1,6,3,7,8,2,4]`) e as durações do filme são as da tabela da spec, copiadas em `CAPITULOS`/`ORDEM` no `check_filme.py`, que é a fonte da verdade. Frase ≤ 7 palavras; apoio ≤ 200 palavras/min.
- Nenhum número no filme que o portfólio não sustente. Proibidos: "26 anos", "155.000", "150.500", "Cassio" (sem acento), "orçadas", "perdidos", "a obra digitava", "no centavo" e as quantidades antigas da tabela.
- Vídeo web: H.264 960×540, sem áudio, `+faststart`, ≤ 12 MB, com duração igual à soma dos capítulos mais o cartão final (85 s). Capa 960×540.
- O trailer só toca por clique (sem `autoplay` nem `loop`) e vem com a transcrição completa das legendas.
- O mestre de 1280×720 fica em `portfolio/filme/saida/`, ignorado pelo git. Nada do filme (`film.html`, `three.min.js`) entra em `portfolio/site/`.
- Trabalhar no branch `historia-scrollytelling`, com um commit por tarefa terminando em `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.

## Review Focus

1. **Celular com dados móveis.** O vídeo não pode baixar sozinho. Teste: `preload="none"` e ausência de `autoplay` (Task 4), mais o tamanho ≤ 12 MB (Task 3).
2. **Leitor de tela.** O vídeo não tem áudio, então a transcrição tem de trazer tudo o que está escrito no filme. Teste: os itens da transcrição têm de ser iguais às legendas, capítulo a capítulo (Task 4).
3. **Filme e página divergindo depois de uma edição.** Teste: `check_filme.py` compara `CAPS` do `film.html` com `CAPITULOS`, e o `check_historia.py` compara a transcrição com `CAPITULOS` (Tasks 2 e 4).
4. **Render parado no meio.** Um mestre incompleto não pode virar o vídeo publicado. Teste: a checagem de duração exige 85 s ± 0,5 (Task 3).
5. **Chegar ao trailer pelo link.** O palco da história é `sticky` com `margin-bottom:-100vh` e, sem corte, cobre por uma tela inteira o que vem depois do `</main>`; hoje isso já esconde a ficha no fim da página. O vídeo tem de estar à vista depois de "Assistir ao filme ↓", e a ficha no fim da página. Teste: `checar_fim_do_palco()` (Task 4).
6. **Adereços pintados nas cenas** (planilha, post-its, placas). Nenhum pode trazer número inventado. Teste: o `check_filme.py` lê todo texto literal do script, menos cores e fontes (Task 2), e a conferência visual dos quadros (Task 3, Step 6).

---

## File Structure

| Arquivo | Responsabilidade |
|---|---|
| `portfolio/filme/film.html`, `three.min.js`, `fonts/` | O filme (do zip), corrigido |
| `portfolio/filme/corrigir_filme.py` | Aplica as correções ao `film.html` do zip |
| `portfolio/filme/render.py` | Quadro a quadro → mestre 1280×720 → versão web 960×540 + capa |
| `portfolio/filme/README.md` | Como editar e gerar |
| `portfolio/tests/check_filme.py` | Legendas, adereços, números, frase da contabilidade; com `--video`, confere o MP4 e a capa |
| `portfolio/site/video/historia.mp4`, `historia.jpg` | Trailer publicado e capa |
| `portfolio/site/index.html`, `portfolio/site/portfolio.html` | Frase da contabilidade; seção do trailer; palco cortado no fim da história |
| `portfolio/tests/check_historia.py` | Frase da contabilidade; seção do trailer; vídeo e ficha à vista depois do palco |
| `.gitignore` | `portfolio/filme/saida/` |

---

### Task 1: A frase da contabilidade

**Files:** Modify `portfolio/tests/check_historia.py`, `portfolio/site/index.html`, `portfolio/site/portfolio.html`

- [ ] **Step 1: Escrever os testes**

Em `check_historia.py`, no `ROTEIRO`, trocar a linha

```python
        "Comecei no centavo, não na parede.",
```

por

```python
        "Comecei pela contabilidade, não pela obra.",
```

Em `checar_texto()`, logo depois da linha `    check(t.lower().count("você") == 1, "\"você\" deve aparecer uma vez só, no convite final")`:

```python
    check("centavo, não na parede" not in portfolio, "portfolio.html ainda abre com a frase do centavo (agora é a da contabilidade)")
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py`
Expected: `FALHOU:` com `cena origem: frase 'Comecei no centavo, não na parede.' ≠ roteiro 'Comecei pela contabilidade, não pela obra.'` e `portfolio.html ainda abre com a frase do centavo…`

- [ ] **Step 3: Trocar a frase**

Em `index.html`, trocar `<h2 class="frase" tabindex="-1">Comecei no centavo, não na parede.</h2>` por `<h2 class="frase" tabindex="-1">Comecei pela contabilidade, não pela obra.</h2>`.
Em `portfolio.html`, trocar `Comecei no centavo, não na parede: folha, notas e balancete` por `Comecei pela contabilidade, não pela obra: folha, notas e balancete`.

- [ ] **Step 4: Rodar e ver passar**

Run: `python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_site.py`
Expected: `OK` e `OK`

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/tests/check_historia.py portfolio/site/index.html portfolio/site/portfolio.html
git commit -m "História e portfólio: \"Comecei pela contabilidade, não pela obra.\"

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: O filme no projeto, com o texto corrigido

**Files:**
- Create: `portfolio/filme/` (a partir do zip), `portfolio/filme/corrigir_filme.py`, `portfolio/tests/check_filme.py`
- Modify (substituição completa): `portfolio/filme/render.py`, `portfolio/filme/README.md`
- Modify: `.gitignore`

**Interfaces:**
- Produces:
  - `check_filme.CAPITULOS: list[tuple[kicker, frase, apoio, ressalva, duração]]`, `check_filme.FRASE_CONTABILIDADE`;
  - `python3 portfolio/tests/check_filme.py [--video]`;
  - `portfolio/filme/render.py [--segundos N]`, que grava `site/video/historia.mp4` e `historia.jpg`.

- [ ] **Step 1: Trazer o filme do zip**

```bash
cd /home/runner/workspace && mkdir -p portfolio/filme && unzip -oq filme-codigo-fonte.zip -d portfolio/filme && ls portfolio/filme portfolio/filme/fonts
```

Expected: `README.md film.html fonts render.py three.min.js`, e as 4 fontes `.woff2`.

- [ ] **Step 2: Escrever `portfolio/tests/check_filme.py`**

```python
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
```

- [ ] **Step 3: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_filme.py`
Expected: `FALHOU:` com `legendas do filme diferentes do roteiro corrigido`, `ordem das cenas deve ser [5, 0, 1, 6, 3, 7, 8, 2, 4] (cronológica)`, `durações dos capítulos diferentes do roteiro`, `tabela da abertura diferente…`, `texto proibido no filme: '26 anos'` (e `'155.000'`, `'150.500'`, `'Cassio'`, `'orçadas'`, `'perdidos'`…), `texto obrigatório ausente no filme: 'No estudo'` e `números no filme que o portfólio não sustenta: [...]`.

- [ ] **Step 4: Escrever e rodar `portfolio/filme/corrigir_filme.py`**

```python
#!/usr/bin/env python3
"""Aplica ao film.html do zip (filme-codigo-fonte.zip) as correções de honestidade da rodada 3.
Uso: python3 portfolio/filme/corrigir_filme.py   (idempotente: falha se o texto esperado não estiver lá)
"""
import re
from pathlib import Path

FILME = Path(__file__).resolve().parent / "film.html"
CAPS = """var ORDER=[5,0,1,6,3,7,8,2,4], DUR=[10.5,8,8,8,8,8.5,8.5,8.5,9], ENDD=8;
// [kicker, frase (≤7 palavras), apoio (≤ 200 palavras/min), hud, ressalva] — mesmas regras de honestidade da página
var CAPS=[
 ['Cássio Viller · portfólio','Número sem origem custa caro na obra.','Nove capítulos, de 2017 a 2026. Cada número tem origem: medido, derivado ou a confirmar.',null,''],
 ['2017 → 2024','Comecei pela contabilidade, não pela obra.','Escritório contábil da família desde 2017. Na UNIFEI, fiscal do DCE (2022) e diretor de vendas da InLoco Jr.',function(t){return['8 anos','de rotina contábil'];},''],
 ['fev/2025 → mar/2026','Mas vi o dado digitado cinco vezes.','Meio período, em paralelo: produção na V Alves (CLT) e estágio na Estruturas do Vale, onde nasceu o SIGE.',function(t){return['5×','o mesmo dado'];},''],
 ['mar → set/2026','Na VEKS, toda conta repetida virou ferramenta.','PJ, 6 meses, cumprido até o fim, com a V Alves até julho. Calculadora de parede e classificador de caixa.',function(t){return['6 meses','contrato PJ cumprido'];},''],
 ['mai → set/2026','O SIGE ganhou versão nova.','Cerca de 50 módulos em 6 áreas; entregas de 22/07 a 14/09/2026. Portal e diário em uso nos galpões.',function(t){return['~'+Math.round(50*ramp(t,1,8.2))+' módulos','em 6 áreas'];},''],
 ['jul → set/2026','13 obras no sistema, 11 com proposta.','Lê o desenho, mede e orça. Nos 19 serviços SINAPI conferidos, desvio máximo de 0,25%. Código com assistentes de IA.',function(t){return t<5?['R$ 24,5 mi','maior proposta']:(t<7.6?['0,25%','desvio máx. vs. SINAPI']:[Math.min(13,1+Math.round(12*ramp(t,6.9,9.2)))+' obras','no sistema']);},'A gestão de obra deste sistema ainda não rodou em obra real.'],
 ['ago/2026','O celeiro não cabe no caminhão.','B-36: duas caixas, três viagens, 37 decisões registradas. No estudo, o módulo sobe pelo balancim, cabos na vertical.',function(t){return['37','decisões registradas'];},'Pré-dimensionado, sujeito à revisão do engenheiro responsável.'],
 ['ago → set/2026','23 dias de diário só no WhatsApp.','Depois de 11/08, o diário saiu do sistema; 28 atividades prontas apareciam atrasadas nos dois galpões.',function(t){var n=Math.round(23*ramp(t,3,8.2));return[n+(n==1?' dia':' dias'),'de diário recuperados'];},'Recuperação lida numa cópia; no sistema em uso, a carga ainda não foi aplicada.'],
 ['set/2026','Proposta assinável em 36 minutos.','Medidos: 11:35 → 12:11, ampliação de unidade de saúde, 26 ambientes, 328 m². À mão, cerca de 2 dias úteis (estimativa).',null,'']];
"""
TABELA = ("var rows=[['Área de projeção (UPA)','328','m²','medido'],['Ambientes','26','un','medido'],"
          "['Placa de gesso por m²','2,11','m²','derivado'],['Montante por m²','2,91','m','derivado'],"
          "['Aço da casa 8 × 6 m','541','kg','derivado'],['Pé-direito','—','m','a confirmar']];")
TROCAS = [
    # nome com acento; sem "26 anos" (o portfólio não traz a idade)
    ('<div class="tag">Cassio Viller · <b>portfólio</b></div>', '<div class="tag">Cássio Viller · <b>portfólio</b></div>'),
    ('  <h1>Cassio Viller</h1>\n  <div class="a">26 anos · São José dos Campos/SP</div>', '  <h1>Cássio Viller</h1>\n  <div class="a">São José dos Campos/SP</div>'),
    ('<h1 id="e2">Cassio Viller<i id="endline"></i></h1>', '<h1 id="e2">Cássio Viller<i id="endline"></i></h1>'),
    ('<div class="l1" id="e3">26 anos · São José dos Campos/SP · orçamento, planejamento e custos</div>',
     '<div class="l1" id="e3">São José dos Campos/SP · orçamento, planejamento e custos</div>'),
    # planilha do escritório: nada de valor inventado; a célula em destaque "não bate" e depois "confere"
    ("c.fillText(k==0?'conta '+(r+1):(hi&&t>6.3&&t<8?'1.284,32':(r*317+k*91+120)+',00'),x+6,y+23);",
     "c.fillText(k==0?'conta '+(r+1):(hi?(t>=8?'confere':(t>6.3?'não bate':'· · ·')):'· · ·'),x+6,y+23);"),
    # post-its: o mesmo dado em cinco lugares, a quinta cópia diverge — sem valor em reais
    ("c.fillStyle=i==4?'#C23B22':'#1E1A17';c.font='bold 44px sans-serif';c.fillText(i==4?'R$ 150.500':'R$ 155.000',20,120);",
     "c.fillStyle=i==4?'#C23B22':'#1E1A17';c.font='bold 34px sans-serif';c.fillText(i==4?'OUTRO DADO':'MESMO DADO',20,120);"),
]


def main():
    s = FILME.read_text(encoding="utf-8")
    for velho, novo in TROCAS:
        assert s.count(velho) == 1, f"trecho não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
    s, n = re.subn(r"var rows=\[.*?\]\];", lambda m: TABELA, s, count=1, flags=re.S)
    assert n == 1, "tabela da abertura não encontrada"
    ini, fim = s.index("// ordem cronológica"), s.index("var NCH=CAPS.length-1;")
    s = s[:ini] + CAPS + s[fim:]
    linhas = s.split("\n")
    sem_legenda_antiga = [l for l in linhas if not l.startswith("st.cap=[")]  # legendas antigas, nunca exibidas
    assert len(linhas) - len(sem_legenda_antiga) == 5, "esperava 5 legendas antigas (st.cap)"
    FILME.write_text("\n".join(sem_legenda_antiga), encoding="utf-8")
    print("film.html corrigido")


if __name__ == "__main__":
    main()
```

Run: `python3 portfolio/filme/corrigir_filme.py`
Expected: `film.html corrigido`

- [ ] **Step 5: Substituir `portfolio/filme/render.py`**

```python
#!/usr/bin/env python3
"""Gera o trailer da história a partir de film.html, quadro a quadro (renderAt), e a versão para a web.

Uso: python3 portfolio/filme/render.py              (filme inteiro, ~13 min em CPU)
     python3 portfolio/filme/render.py --segundos 3 (ensaio curto)
Saídas: portfolio/filme/saida/historia-1280.mp4   mestre 1280×720 (fora do site, ignorado pelo git)
        portfolio/site/video/historia.mp4         960×540, H.264, sem áudio, +faststart
        portfolio/site/video/historia.jpg         capa 960×540 (o quadro da ficha de abertura)
"""
import shutil
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida"
WEB = AQUI.parent / "site" / "video"
FPS = 30
T_CAPA = 3.0  # segundo em que a ficha de abertura (nome, cargo, contato) está inteira na tela
ARGS = ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist", "--allow-file-access-from-files"]


def main():
    segundos = float(sys.argv[sys.argv.index("--segundos") + 1]) if "--segundos" in sys.argv else None
    SAIDA.mkdir(exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    mestre, capa = SAIDA / "historia-1280.mp4", SAIDA / "capa-1280.jpg"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-vcodec", "mjpeg",
                           "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", str(mestre)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        # no Replit o Chromium baixado pelo Playwright não roda (faltam bibliotecas do sistema): usa o do sistema
        exe = shutil.which("chromium")
        navegador = p.chromium.launch(executable_path=exe, args=ARGS) if exe else p.chromium.launch(args=ARGS)
        pagina = navegador.new_page(viewport={"width": 1280, "height": 720})
        pagina.goto((AQUI / "film.html").as_uri())
        pagina.wait_for_timeout(2500)
        total = segundos if segundos is not None else pagina.evaluate("TOTAL")
        n = int(round(total * FPS))
        for i in range(n):
            pagina.evaluate(f"renderAt({i / FPS})")
            ff.stdin.write(pagina.screenshot(type="jpeg", quality=92))
            if i % 300 == 0:
                print(f"{i}/{n}", flush=True)
        pagina.evaluate(f"renderAt({T_CAPA})")
        pagina.screenshot(path=str(capa), type="jpeg", quality=92)
        navegador.close()
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg falhou ao gerar o mestre")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mestre), "-vf", "scale=960:540", "-c:v", "libx264",
                    "-preset", "slow", "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
                    str(WEB / "historia.mp4")], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(capa), "-vf", "scale=960:540", "-q:v", "4",
                    str(WEB / "historia.jpg")], check=True)
    print("pronto:", WEB / "historia.mp4")


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Substituir `portfolio/filme/README.md`**

```markdown
# O filme da história (trailer de 85 s)

Fonte: `filme-codigo-fonte.zip` (v4), corrigido pelas regras de honestidade da página
(spec `docs/superpowers/specs/2026-09-23-filme-trailer-design.md`).

## Arquivos
- `film.html` — 9 dioramas em three.js r128 (`three.min.js`, sem CDN), legendas, capa e cartão final.
  Determinístico: `window.renderAt(T)` desenha o quadro do segundo T.
- `corrigir_filme.py` — aplica as correções ao `film.html` do zip (já aplicadas aqui; só rode sobre o original).
- `render.py` — Playwright chama `renderAt(i/30)` quadro a quadro e manda para o ffmpeg.
- `fonts/` — Barlow Condensed 600/700, IBM Plex Sans 400, IBM Plex Mono 500.

## Como gerar o vídeo (Replit)
    python3 -m pip install --user playwright     # uma vez
    python3 portfolio/filme/render.py            # ~13 min; gera o mestre e a versão web
    python3 portfolio/tests/check_filme.py --video

O Chromium que o Playwright baixa não roda no Replit (faltam bibliotecas do sistema): o
`render.py` usa o Chromium do sistema (`shutil.which("chromium")`). Saídas:
- `portfolio/filme/saida/historia-1280.mp4` — mestre 1280×720 (fora do site, ignorado pelo git)
- `portfolio/site/video/historia.mp4` — 960×540, H.264, sem áudio, `+faststart`
- `portfolio/site/video/historia.jpg` — capa (a ficha de abertura)

## Onde editar
- Textos: `CAPS[]` = [kicker, frase ≤ 7 palavras, apoio, hud(t), ressalva] — e o mesmo texto em
  `CAPITULOS` de `portfolio/tests/check_filme.py` (a checagem compara os dois).
- Ordem e duração: `ORDER`, `DUR`, `ENDD`. Capa: `<div id="cover">`. Cartão final: `<div id="end">`.
- Cada cena: um bloco `(function(){ ... })()` com `st.cam` (chaves de câmera) e `st.run(t)` (t de 0 a 10).
- Depois de editar: `python3 portfolio/tests/check_filme.py` (textos) e renderizar de novo.
```

- [ ] **Step 7: Ignorar o mestre e rodar a checagem**

Acrescentar ao fim do `.gitignore`:

```
# mestre 1280×720 do filme (a versão web fica em portfolio/site/video/)
portfolio/filme/saida/
```

Run: `python3 portfolio/tests/check_filme.py`
Expected: `OK`

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add .gitignore portfolio/filme portfolio/tests/check_filme.py
git commit -m "Filme da história no projeto, com legendas e adereços corrigidos

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Gerar o vídeo (render)

**Files:** Create `portfolio/site/video/historia.mp4`, `portfolio/site/video/historia.jpg`

- [ ] **Step 1: Ver falhar**

Run: `python3 portfolio/tests/check_filme.py --video`
Expected: `FALHOU:` com `falta portfolio/site/video/historia.mp4 (rode python3 portfolio/filme/render.py)` e `falta portfolio/site/video/historia.jpg (capa do vídeo)`

- [ ] **Step 2: Playwright**

Run: `python3 -c "import playwright" 2>/dev/null || python3 -m pip install --user playwright`
Expected: sem erro. **Não** é preciso rodar `playwright install chromium`: o `render.py` usa o Chromium do sistema.

- [ ] **Step 3: Ensaio curto do pipeline**

Run: `python3 portfolio/filme/render.py --segundos 3 && python3 portfolio/tests/check_filme.py --video`
Expected: `pronto: …/portfolio/site/video/historia.mp4`, e a checagem falha **só** na duração (`duração 3.000000 s ≠ 85.0 s`). Isso prova que a checagem pega um render incompleto.

- [ ] **Step 4: Render completo (cerca de 13 min)**

Run: `python3 portfolio/filme/render.py` (em segundo plano, se preciso)
Expected: progresso `0/2550`, `300/2550`, … e `pronto: …/historia.mp4`

- [ ] **Step 5: Ver passar**

Run: `python3 portfolio/tests/check_filme.py --video && ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height -of compact portfolio/site/video/historia.mp4`
Expected: `OK`, e `codec_name=h264|width=960|height=540`, `duration=85.000000` e tamanho de cerca de 2,7 MB (2.677.470 bytes no ensaio).

- [ ] **Step 6: Conferir quadros**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/f9d44ef5-7d41-4ced-9ebe-ca35da9a73fc/scratchpad && for T in 3 7 18 24 40 57 81; do ffmpeg -y -loglevel error -ss $T -i portfolio/site/video/historia.mp4 -frames:v 1 $S/quadro-$T.jpg; done && magick $S/quadro-{3,7,18,24}.jpg -resize 50% +append $S/quadros-a.jpg && magick $S/quadro-{40,57,81}.jpg -resize 50% +append $S/quadros-b.jpg
```

Abrir `quadros-a.jpg` e `quadros-b.jpg` com a ferramenta Read.
Expected:
- capa com **"CÁSSIO VILLER"** e sem "26 anos";
- tabela com 328 · 26 · 2,11 · 2,91 · 541 · — ;
- escritório com "Comecei pela contabilidade, não pela obra.";
- post-its "MESMO DADO" inteiros e "OUTRO DADO" riscado;
- SIGE com kicker `MAI → SET/2026`;
- celeiro com "No estudo…" e a ressalva;
- cartão final sem "26 anos".

- [ ] **Step 7: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/video/historia.mp4 portfolio/site/video/historia.jpg
git commit -m "Trailer da história renderizado (960×540, 85 s, sem áudio)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: O trailer na página, com transcrição

**Files:** Modify `portfolio/tests/check_historia.py`, `portfolio/site/index.html`

**Interfaces:**
- Consumes: `check_filme.CAPITULOS` (Task 2); `site/video/historia.mp4` e `historia.jpg` (Task 3).
- Produces: `<section class="filme" id="filme">`; `duracao_video()`, `checar_filme(pagina)` e `checar_fim_do_palco()` em `check_historia.py`.

- [ ] **Step 1: Escrever os testes**

Em `check_historia.py`, antes da linha `PORTA = 5056`:

```python
VIDEO = SITE / "video" / "historia.mp4"


def duracao_video():
    """Duração real do trailer (ffprobe), ou None se o vídeo ainda não foi gerado."""
    if not VIDEO.exists():
        return None
    saida = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(VIDEO)],
                           capture_output=True, text=True, check=True).stdout
    return float(saida)


def checar_filme(pagina):
    """O trailer fica depois da história, toca só por clique e vem com a transcrição das legendas."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from check_filme import CAPITULOS
    sec = re.search(r'<section class="filme" id="filme" aria-labelledby="filme-titulo">(.*?)</section>', pagina, re.S)
    check(sec is not None, "falta a seção do filme (<section class=\"filme\" id=\"filme\" aria-labelledby=\"filme-titulo\">)")
    if not sec:
        return
    pos = pagina.index('<section class="filme"')
    check(pagina.index("</main>") < pos < pagina.index('<section class="ficha"'), "o filme fica depois da história e antes da ficha")
    s = sec.group(1)
    d = duracao_video()
    titulo = re.search(r'<h2 id="filme-titulo">(.*?)</h2>', s, re.S)
    check(titulo is not None and d is not None and limpo(titulo.group(1)) == f"A história em {round(d)} segundos",
          f"o título do filme diz a duração real do vídeo ({d} s)")
    v = re.search(r"<video ([^>]*)>", s)
    check(v is not None, "falta <video>")
    if v:
        for attr in ("controls", 'preload="none"', 'poster="video/historia.jpg"', 'width="960"', 'height="540"', "playsinline"):
            check(attr in v.group(1), f"<video> sem {attr}")
        check("autoplay" not in v.group(1) and "loop" not in v.group(1), "o filme só toca por clique (sem autoplay nem loop)")
    check('<source src="video/historia.mp4" type="video/mp4">' in s, "falta <source src=\"video/historia.mp4\" type=\"video/mp4\">")
    check("<summary>Transcrição do filme (o vídeo não tem áudio)</summary>" in s, "falta a transcrição do filme")
    itens = [limpo(x) for x in re.findall(r"<li>(.*?)</li>", s, re.S)]
    esperado = [" ".join(p for p in (f"{k} — {f}", a, r) if p) for k, f, a, r, _dur in CAPITULOS]
    check(itens == esperado, "a transcrição precisa repetir as legendas do filme, capítulo por capítulo")
    ultima = cenas(pagina)[-1][3] if cenas(pagina) else ""
    check('href="#filme"' in ultima, "o convite também leva ao filme (href=\"#filme\")")
```

Logo antes de `def main():`:

```python
def checar_fim_do_palco():
    """O palco é sticky com margin-bottom:-100vh: não pode passar do fim da história e cobrir o que vem depois.
    Clica em "Assistir ao filme ↓" e confere o título abaixo da barra e o vídeo à vista; rola até o fim e confere a ficha."""
    ver = ("(function(sel){var r=document.querySelector(sel).getBoundingClientRect();"
           "var topo=Math.max(r.top,0),base=Math.min(r.bottom,innerHeight);if(base<=topo)return 'fora';"
           "var e=document.elementFromPoint(innerWidth/2,(topo+base)/2);"
           "return e&&e.closest(sel)?'visivel':(e&&e.closest('.palco')?'coberto pelo palco':'coberto por '+(e&&e.tagName));})")
    for largura in (390, 1280):
        with chromium(largura, ("--disable-3d-apis",)) as ws:
            ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/site/index.html")
            time.sleep(1.5)
            ws.avaliar("document.querySelector('#convite a[href=\"#filme\"]').click()")
            time.sleep(1)
            filme = ws.avaliar(ver + "('#filme video')")
            titulo = ws.avaliar("document.getElementById('filme-titulo').getBoundingClientRect().top>="
                                "document.querySelector('.barra').getBoundingClientRect().bottom")
            ws.avaliar("window.scrollTo(0,document.documentElement.scrollHeight)")
            time.sleep(1)
            ficha = ws.avaliar(ver + "('.ficha')")
        check(titulo is True, f"{largura} px: depois de \"Assistir ao filme ↓\", o título do filme fica abaixo da barra")
        check(filme == "visivel", f"{largura} px: depois de \"Assistir ao filme ↓\", o vídeo precisa estar à vista ({filme})")
        check(ficha == "visivel", f"{largura} px: no fim da página, a ficha precisa estar à vista ({ficha})")
```

Em `main()`, logo depois de `        checar_regua(pagina)`:

```python
        checar_filme(pagina)
```

e logo depois de `            checar_maquete_real()`:

```python
            checar_fim_do_palco()
```

Em `checar_texto()`, trocar a linha `    extras = numeros(t) - numeros(limpo(corpo(portfolio)))` por:

```python
    d = duracao_video()
    extras = numeros(t) - numeros(limpo(corpo(portfolio))) - ({str(round(d))} if d else set())  # a duração do filme vem do próprio vídeo
```

Em `checar_css()`, a checagem do fundo tinta compara a regra inteira e quebraria com o `overflow:clip` do Step 5. Trocar

```python
    check(".js-historia .historia{max-width:none;padding:0;position:relative;background:var(--tinta)}" in css,
```

por

```python
    regra = re.search(r"\.js-historia \.historia\{([^}]*)\}", css)
    check(regra is not None and "background:var(--tinta)" in regra.group(1),
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python3 portfolio/tests/check_historia.py`
Expected: `FALHOU:` com `falta a seção do filme (<section class="filme" id="filme" aria-labelledby="filme-titulo">)`

- [ ] **Step 3: Pôr o trailer na página**

Em `index.html`, trocar `</main>\n\n<section class="ficha"` pela seção abaixo seguida de `<section class="ficha"`, ou seja, inserir a seção entre `</main>` e a ficha:

```html
<section class="filme" id="filme" aria-labelledby="filme-titulo">
  <h2 id="filme-titulo">A história em 85 segundos</h2>
  <video controls preload="none" playsinline poster="video/historia.jpg" width="960" height="540">
    <source src="video/historia.mp4" type="video/mp4">
  </video>
  <details class="transcricao">
    <summary>Transcrição do filme (o vídeo não tem áudio)</summary>
    <ol>
      <li><b>Cássio Viller · portfólio — Número sem origem custa caro na obra.</b> Nove capítulos, de 2017 a 2026. Cada número tem origem: medido, derivado ou a confirmar.</li>
      <li><b>2017 → 2024 — Comecei pela contabilidade, não pela obra.</b> Escritório contábil da família desde 2017. Na UNIFEI, fiscal do DCE (2022) e diretor de vendas da InLoco Jr.</li>
      <li><b>fev/2025 → mar/2026 — Mas vi o dado digitado cinco vezes.</b> Meio período, em paralelo: produção na V Alves (CLT) e estágio na Estruturas do Vale, onde nasceu o SIGE.</li>
      <li><b>mar → set/2026 — Na VEKS, toda conta repetida virou ferramenta.</b> PJ, 6 meses, cumprido até o fim, com a V Alves até julho. Calculadora de parede e classificador de caixa.</li>
      <li><b>mai → set/2026 — O SIGE ganhou versão nova.</b> Cerca de 50 módulos em 6 áreas; entregas de 22/07 a 14/09/2026. Portal e diário em uso nos galpões.</li>
      <li><b>jul → set/2026 — 13 obras no sistema, 11 com proposta.</b> Lê o desenho, mede e orça. Nos 19 serviços SINAPI conferidos, desvio máximo de 0,25%. Código com assistentes de IA. <em>A gestão de obra deste sistema ainda não rodou em obra real.</em></li>
      <li><b>ago/2026 — O celeiro não cabe no caminhão.</b> B-36: duas caixas, três viagens, 37 decisões registradas. No estudo, o módulo sobe pelo balancim, cabos na vertical. <em>Pré-dimensionado, sujeito à revisão do engenheiro responsável.</em></li>
      <li><b>ago → set/2026 — 23 dias de diário só no WhatsApp.</b> Depois de 11/08, o diário saiu do sistema; 28 atividades prontas apareciam atrasadas nos dois galpões. <em>Recuperação lida numa cópia; no sistema em uso, a carga ainda não foi aplicada.</em></li>
      <li><b>set/2026 — Proposta assinável em 36 minutos.</b> Medidos: 11:35 → 12:11, ampliação de unidade de saúde, 26 ambientes, 328 m². À mão, cerca de 2 dias úteis (estimativa).</li>
    </ol>
  </details>
</section>
```

No `<style>`, logo antes de `/* modo cenas: historia.js liga .js-historia no <html> e leva cada .fundo para o .palco */`:

```css
/* o filme: toca só por clique; a transcrição repete as legendas */
.filme{max-width:880px;margin:0 auto;padding:48px 16px 8px}
.filme h2{font-family:var(--display);font-weight:600;font-size:2rem;line-height:1.05;margin:0 0 14px}
.filme video{display:block;width:100%;height:auto;background:var(--tinta);border:1px solid var(--rule)}
.transcricao{margin:14px 0 0;font-size:.92rem;color:var(--ink-2)}
.transcricao summary{cursor:pointer;font-family:var(--mono);font-size:.8rem;color:var(--ink)}
.transcricao ol{margin:10px 0 0;padding-left:20px;display:grid;gap:8px}
.transcricao b{color:var(--ink)}
```

No convite, logo antes de `        <a class="btn fantasma" href="portfolio.html">Ver o portfólio completo</a>`:

```html
        <a class="btn fantasma" href="#filme">Assistir ao filme ↓</a>
```

- [ ] **Step 4: Rodar e ver o palco cobrir o trailer**

Run: `python3 portfolio/tests/check_historia.py && python3 -c "import sys; sys.path.insert(0, 'portfolio/tests'); import check_historia as c; c.checar_fim_do_palco(); print(c.FALHAS or 'OK')"`
Expected: `OK` (checagem estática) e depois a lista de 6 falhas, 3 em 390 px e 3 em 1280 px: `depois de "Assistir ao filme ↓", o título do filme fica abaixo da barra`, `depois de "Assistir ao filme ↓", o vídeo precisa estar à vista (coberto pelo palco)` e `no fim da página, a ficha precisa estar à vista (coberto pelo palco)`.

- [ ] **Step 5: O palco para no fim da história; o link para abaixo da barra**

Em `index.html`, trocar a linha

```css
.js-historia .historia{max-width:none;padding:0;position:relative;background:var(--tinta)}
```

por

```css
/* overflow:clip corta o palco (sticky, margin-bottom:-100vh) no fim da história: sem ele, o palco cobre o filme e a ficha */
.js-historia .historia{max-width:none;padding:0;position:relative;background:var(--tinta);overflow:clip}
```

`overflow:clip` não cria contêiner de rolagem, então o `sticky` do palco continua funcionando. Em navegadores sem suporte (Safari < 16), a página volta ao comportamento de hoje.

E, como já faz `.cena{scroll-margin-top:9rem}`, trocar

```css
.filme{max-width:880px;margin:0 auto;padding:48px 16px 8px}
```

por

```css
.filme{max-width:880px;margin:0 auto;padding:48px 16px 8px;scroll-margin-top:9rem}
```

- [ ] **Step 6: Rodar e ver passar**

Run: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_site.py`
Expected: `OK`, `OK` e `OK`

- [ ] **Step 7: Commit**

```bash
cd /home/runner/workspace && git add portfolio/tests/check_historia.py portfolio/site/index.html
git commit -m "História: trailer de 85 s (só por clique) com transcrição; o palco não cobre mais o que vem depois

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: Conferência visual e changelog

**Files:** Modify `portfolio/revisao/CHANGELOG.md`

- [ ] **Step 1: Screenshots da seção do trailer**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/f9d44ef5-7d41-4ced-9ebe-ca35da9a73fc/scratchpad python3 - <<'EOF'
import base64, os, sys, time
sys.path.insert(0, "portfolio/tests")
import check_historia as c
S = os.environ["S"]
for largura in (390, 1280):
    with c.chromium(largura, ("--disable-3d-apis",)) as ws:
        ws.comando("Page.navigate", url=f"http://127.0.0.1:{c.PORTA}/site/index.html")
        time.sleep(1.5)
        ws.avaliar("document.querySelector('.transcricao').open=true;document.querySelector('#convite a[href=\"#filme\"]').click()")
        time.sleep(1)
        png = ws.comando("Page.captureScreenshot", format="png")["data"]
    open(f"{S}/trailer-{largura}.png", "wb").write(base64.b64decode(png))
print("ok")
EOF
```

Abrir `trailer-390.png` e `trailer-1280.png` com a ferramenta Read.
Expected:
- o título "A história em 85 segundos", abaixo da barra (a captura é feita depois do clique em "Assistir ao filme ↓");
- o vídeo com a capa (a ficha de abertura) e os controles, sem tocar;
- a transcrição aberta, com os 9 capítulos;
- nada cortado e nenhuma rolagem horizontal.

- [ ] **Step 2: Changelog**

Acrescentar ao fim de `portfolio/revisao/CHANGELOG.md`:

```markdown

---

# Rodada 7 — o filme como trailer da história, 23/09/2026

- Pesquisa das 5 personas (rodada 3) em `docs/superpowers/research/2026-09-23-filme/`; spec em `docs/superpowers/specs/2026-09-23-filme-trailer-design.md`.
- "Comecei pela contabilidade, não pela obra." na história, no portfólio e no filme.
- `portfolio/filme/`: o filme do zip, corrigido por `corrigir_filme.py` — 13 obras no sistema/11 com proposta; SIGE mai → set/2026; balancim como estudo; "só no WhatsApp"; "vi o dado digitado"; nome com acento; sem "26 anos"; tabela da abertura com números do portfólio; post-its e planilha sem valores inventados; legendas antigas removidas; apoio ≤ 200 palavras/min.
- `render.py` roda no Replit com o Chromium do sistema; `site/video/historia.mp4` (960×540, 85 s, sem áudio) e capa.
- Trailer na história, só por clique, com transcrição; "Assistir ao filme ↓" no convite.
- Correção: o palco (sticky, `margin-bottom:-100vh`) cobria por uma tela o que vinha depois da história — a ficha, no fim da página; `overflow:clip` no `<main>` corta o palco onde a história acaba.
- `tests/check_filme.py` (texto do filme e vídeo) e `check_historia.py` (seção do trailer; vídeo e ficha à vista depois do palco).
- Próximo passo (plano separado): dioramas ao vivo como fundo dos capítulos, com um renderizador compartilhado.
- Em aberto (Cássio): idade; UNIFEI 2020 ou 2022; estágio/júnior; versão curta do trailer para o LinkedIn.
```

- [ ] **Step 3: Checagem final e commit**

Run: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_site.py`
Expected: `OK`, `OK` e `OK`

```bash
cd /home/runner/workspace && git add portfolio/revisao/CHANGELOG.md
git commit -m "Changelog da rodada 7: o filme como trailer

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```
