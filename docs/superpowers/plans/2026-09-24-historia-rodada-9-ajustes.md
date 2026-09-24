# Rodada 9 — ajustes da história depois dos prints e da revisão · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir o que os prints de 24/09/2026 (https://claude.ai/artifact/AfNihqpe9eP2TRuNPzzrPB) e o `/code-review high` com as 5 personas apontaram na história em cenas: a barra fixa cobrindo o alto de cada cena, o recorte vertical em janelas mais largas que 16:9, os marcos tipográficos atrás da faixa, o celular deitado, a robustez do `clipes.js` em WebKit/Safari, o fim do clipe, os testes que passam sem provar, a cena morta do `maquetes.js` e dois reenquadramentos.

**Architecture:** Nada de novo entra na página além de CSS, de ~20 linhas no `clipes.js` e de 6 no `historia.js`; cada mudança de comportamento chega com um teste que falha antes (estático em `check_historia.py`, ou real no Chromium headless pelo CDP que o arquivo já traz). O filme só muda em duas chaves de câmera (e um nome de objeto), reproduzidas pelo `corrigir_filme.py` e conferidas por projeção no `check_filme.py --cenas`. Os clipes só são re-renderizados onde a câmera mudou (`escala`, `icamento`).

**Tech Stack:** HTML/CSS/JS sem build; Python 3 (`check_historia.py` com CDP próprio, `check_filme.py` com Playwright + Chromium do sistema, `render_clipes.py` com ffmpeg); three.js r128 no `film.html`.

**Spec:** não há spec nova. Valem, como autoridade, o spec da rodada 8 (`docs/superpowers/specs/2026-09-23-filme-fundo-design.md`, F-01…F-18 e as emendas da revisão final: pôsteres sem `loading="lazy"`, crossfade real) e a seção **Achados** abaixo, que é o requisito desta rodada. Onde este plano muda um literal do spec, ele diz qual e por quê.

## Achados (o requisito desta rodada)

Dos prints (celular 390×844 e desktop 1366×768, pelo endereço público do Replit, Range em 206):

- **P-1** A `.barra` (nome, cargo, botões e régua) é `position:sticky;top:0` e o `.palco` também começa em `top:0`: o alto de cada cena fica atrás da barra — ~90 px no desktop, ~170 px no celular (20 % da tela). É o que corta o cartão de cima em `obra`, o módulo no ar em `casa` e o topo do celular em `whatsapp`.
- **P-2** Com o palco menor que 16:9 (depois de P-1, ou em janelas 2:1 e 21:9), o `object-fit:cover` com `object-position:68% 50%` recorta igual em cima e embaixo; em `obra`, `casa`, `whatsapp` e `icamento` o assunto encosta no alto do quadro; em `escala` as 12 miniaturas encostam no pé.
- **P-3** Na tela larga a faixa de texto foi para a esquerda (rodada 8) e os marcos tipográficos "2025" e "22 baias" (`.fundo.tipo .ano`, alinhados à esquerda) ficaram atrás dela.
- **P-4** Celular deitado (844×390): a faixa centrada de 960 px cobre o clipe inteiro e pode passar da altura da tela (achado da revisão final, "declined to judge" por ser das rodadas 6–7).
- **P-5** Seis capítulos sem cena 3D (`tese`, `mudanca`, `galpoes`, `precisao`, `metodo`, `convite`) — tratado no plano irmão `2026-09-24-historia-cenas-novas.md`, não aqui.

Do `/code-review high` (achados ainda abertos depois da passada pós-merge):

- **R-1** `clipes.js`: um `emptied` do navegador **antes** de `loadedmetadata` é confundido com o `emptied` do nosso próprio `load()` (a heurística `meta || src diferente`) e a figura fica com a vaga ocupada sem dados até sair da faixa.
- **R-2** `clipes.js`: um `seeked` com `readyState<2` depois do primeiro `loadeddata` (Safari, trecho ainda não baixado) só é refeito na próxima rolagem.
- **R-3** `clipes.js`: a decisão "sem Range → pôster" é tomada só em `loadedmetadata`; um navegador que preenche `seekable` mais tarde (o iPhone, em aberto no spec) seria congelado no pôster numa origem boa.
- **R-4** `clipes.js`/`historia.js`: `quadro()` passa meio quadro além do fim e o `*0.999` do `historia.js` tenta compensar do outro lado; o fim do clipe deve ser limitado num lugar só.
- **R-5** `render_clipes.py`: `pagina.evaluate("PRONTO")` sem prazo trava em silêncio se uma textura nunca resolver.
- **R-6** Testes: `".fundo video{display:none}" in css` passa vacuamente (casa com a regra do movimento reduzido); `__troca` olha `window.Historia` e não `f.__clipe`; o teste do 404 não prova que houve pedido em 404; mensagens sem o valor medido; a precondição "clipe carregado" do teste de foco é descartada; `checar_layout` passa com caixa de largura zero; `sleep` fixo onde dá para sondar; exceção de JS derruba `ler_clipes` com traceback; parêntese dobrado na mensagem do `--relogio`; `--disable-3d-apis` inócuo; `--origem` sem URL dá `IndexError`; docstring do `check_filme.py` ("e do clipes"); `checar_reproducao` engole a mensagem do `corrigir_filme.py`.
- **R-7** `maquetes.js`: `cenaIcamento` (linhas 195–233 e a chave em `CENAS`) é código morto — nenhuma página tem `data-cena="icamento"`; o classificador de permissões bloqueou o subagente que ia apagá-la, então a remoção fica explícita aqui (executar este plano é a aprovação).
- **R-8** Enquadramento: em `escala` as 12 miniaturas saem pela borda de baixo (prints e revisão da Task 7); em `icamento` o cavalo da carreta (o acento) fica numa fatia de ~60 px na borda direita do pôster (revisão da Task 5).

Fora do escopo, com o porquê: CLS de 0,005 do `#tese` (dentro do limite 0,01, anterior aos clipes; corrigir exigiria script antes da primeira pintura, contra "scripts exatamente clipes.js e historia.js, defer"); nova tentativa depois de erro de rede (no Chrome, 404 e queda de rede dão o mesmo `error.code` 4 — sem sinal fiável, a tentativa só repetiria o 404); pôster = último quadro (decisão 2 do spec, roteirista); alternância claro/escuro entre foto e clipe (decisão 4 do spec; some com o plano irmão).

## Global Constraints

- Branch novo `historia-rodada-9` a partir de `main` (700798e ou posterior), um commit por tarefa, terminando em `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Nunca `git add -A`: há `film (1).html` e zips do usuário soltos na raiz. Ao fim, merge local em `main` (autorização do Cássio de 24/09: "pode continuar até o final, tem total aprovação").
- **Nenhuma frase da página muda.** "você" continua 1×; o convite continua com exatamente 3 `<a class="btn`.
- Figure de clipe: `<figure class="fundo clipe[ foco-alto| foco-baixo]" data-passo="X" data-dur="D" data-clipe="video/cena-X.mp4" aria-hidden="true">` com `<video muted playsinline preload="none" disableremoteplayback width="960" height="540"></video>` e `<img src="video/cena-X.webp" alt="" width="960" height="540">` (sem `loading`, sem `fetchpriority`); sem `src` no vídeo no HTML; sem `autoplay|loop|controls|poster|tabindex|<source>|<track>|<canvas>|.hud|data-cena`. Scripts exatamente `["clipes.js","historia.js"]`, `defer`, sem inline. `maquetes.js` continua só no `portfolio.html`.
- `clipes.js`: só `currentTime`, quantizado ao quadro e **nunca além do último quadro** (`(min(round(t·24), round(dur·24)−1)+0,5)/24`); um seek em voo por vez; o último pedido vence; libera após 600 ms sem `seeked`; nunca `play()`, `fastSeek`, rAF, `fetch`, `createObjectURL`, `'scroll'`; nunca seek com `readyState<1`; carga só depois do `load` da janela e a 600 px da `.cena`; no máximo 2 `<video>` com dados (os 2 mais perto do centro); sem H.264, `?clipes=nao`, `saveData`, `effectiveType` ∈ {slow-2g, 2g} ou movimento reduzido: só o pôster; `.viva` só com quadro pronto (`readyState≥2`); `TETO=250`, `LENTOS=3`, `VOO=600`, `MAXIMO=2`, `FOLGA=100`, **`ESPERA_RANGE=1500`** (novo).
- CSS: sem `filter` em seletor com `video`; `object-fit:cover`; `object-position:68% 50%` por padrão, `68% 0%` em `.foco-alto`, `68% 100%` em `.foco-baixo` (vídeo e pôster iguais); fotos mantêm `brightness(.6) saturate(.85)`; `100vh` antes de `100svh`, nunca `dvh`; `.palco{display:none}` no empilhado; `overflow:clip` no `<main>`; contraste `--scrim` ≥ 4,5; **o palco gruda em `top:var(--barra,0px)` com altura `100svh − var(--barra,0px)`** (novo; o `.fundo` continua `inset:0`); ≥ 900 px em paisagem a faixa vai à esquerda (`max-width:min(620px,48vw)`); **paisagem com ≤ 520 px de altura: faixa à esquerda com `max-width:min(560px,54vw)` e `margin-left:16px`** (novo); comprimento do `<main>` inalterado (± 2 px da `tests/baseline.json`).
- Servidor com Range (`portfolio/servir.py`) no `run` do `.replit` e no `chromium()` dos testes. Sem build nem dependência nova.
- Render: `scale=960:540`, 24 fps, `libx264 -preset slow -crf 28 -g 4 -keyint_min 4 -sc_threshold 0 -bf 0 -pix_fmt yuv420p -profile:v high -level 3.1 -movflags +faststart -an`; ≤ 0,9 MB por clipe, ≤ 8 MB na soma dos 11; pontas paradas (PSNR ≥ 35 dB nos 0,3 s iniciais e 0,5 s finais); pôster = último quadro (PSNR ≥ 40 dB). `corrigir_filme.py` reproduz o `film.html` a partir do zip byte a byte.

## Review Focus

1. **Janela 21:9 (2560×1080):** o palco recorta ~40 % da altura do 16:9; em `obra` o cartão de cima e em `escala` as miniaturas de baixo têm de continuar no quadro — teste em `checar_layout` (Task 2): `object-position` computado de `obra` = `68% 0%`, de `escala` = `68% 100%`, de `sige` = `68% 50%`.
2. **Barra que quebra em mais linhas ao estreitar a janela** (tablet em pé, 500–700 px): `--barra` tem de acompanhar — teste em `checar_layout` (Task 1): depois de `Emulation.setDeviceMetricsOverride` para 500 px, `--barra` = altura da `.barra` (± 1 px).
3. **Despejo pelo navegador antes dos metadados** (WebKit sob pressão de memória, simulado de fora reatribuindo o mesmo `src` com `preload='none'`): a figura tem de recarregar sem esperar sair da faixa — `checar_evicao` (Task 5).
4. **Origem sem Range num navegador que preenche `seekable` tarde:** com `ESPERA_RANGE` o pôster continua sendo o destino em ≤ 1,5 s + metadados — o bloco "sem Range" de `checar_clipe_real` (espera de 5 s) continua a passar (Task 6).
5. **Celular deitado (844×390):** a faixa termina antes de 62 % da largura e ocupa ≤ 92 % da altura em `sige` e em `icamento` — `checar_layout` (Task 4).

## File Structure

- Modify `portfolio/site/index.html` — CSS do palco (`--barra`, focos, `.tipo` na tela larga, paisagem) e 5 classes de figure (Tasks 1–4).
- Modify `portfolio/site/historia.js` — mede `--barra` (Task 1); `seek(progresso·dur)` sem `*0.999` (Task 7).
- Modify `portfolio/site/clipes.js` — `esperados`/`recarregar()`, `'progress'` (Task 5); `conferirRange()` com `ESPERA_RANGE` (Task 6); `quadro()` por figura (Task 7).
- Modify `portfolio/site/maquetes.js` — sai `cenaIcamento` (Task 10).
- Modify `portfolio/filme/film.html`, `portfolio/filme/corrigir_filme.py` — `st.cam` de `escala` e `icamento`, `st.cavalo` (Task 11).
- Modify `portfolio/filme/render_clipes.py` — `PRONTO` com prazo (Task 8).
- Modify `portfolio/tests/check_historia.py` — `FOCO`, `checar_css`, `checar_js`, `checar_clipes_js`, `checar_fundo`, `checar_layout`, `checar_evicao`, `checar_clipe_real`, higiene (Tasks 1–7, 9).
- Modify `portfolio/tests/check_filme.py` — `checar_render_clipes`, `ENQUADRAMENTOS`, higiene (Tasks 8, 9, 11).
- Modify `portfolio/site/video/cena-escala.{mp4,webp}`, `cena-icamento.{mp4,webp}` — re-render (Task 11).
- Modify `portfolio/revisao/CHANGELOG.md`, `ANDAMENTO.md`, `portfolio/README.md`, `portfolio/DESIGN.md` (Task 12).

---

### Task 0: Branch

- [ ] **Step 1: Criar o branch a partir de main**

```bash
cd /home/runner/workspace && git checkout main && git status --short && git checkout -b historia-rodada-9 && git log --oneline -1
```
Expected: `git status` só com `?? "film (1).html"`; o branch novo aponta para o mesmo commit de `main`.

---

### Task 1: O palco começa abaixo da barra (`--barra`)

**Files:**
- Modify: `portfolio/site/index.html` (regra `.js-historia .palco .fundo{…}`)
- Modify: `portfolio/site/historia.js` (depois de `document.documentElement.classList.add('js-historia');`)
- Modify: `portfolio/tests/check_historia.py` (`checar_css`, `checar_js`, `checar_layout`)

**Interfaces:**
- Produces: a variável CSS `--barra` (px) no `<html>`, sempre igual à altura corrente da `.barra` (nome + cargo + botões + régua); Tasks 2 e 4 dependem dela.

- [ ] **Step 1: Testes estáticos que falham**

Em `checar_css`, logo depois da checagem `".cena{scroll-margin-top:9rem}"`:

```python
    check(re.search(r"\.js-historia \.palco\{display:block;position:sticky;top:var\(--barra,0px\);height:calc\(100vh - var\(--barra,0px\)\);"
                    r"height:calc\(100svh - var\(--barra,0px\)\);margin-bottom:calc\(-100vh \+ var\(--barra,0px\)\);margin-bottom:calc\(-100svh \+ var\(--barra,0px\)\);", css) is not None,
          "modo cenas: o palco gruda abaixo da barra fixa (top:var(--barra,0px)) e perde a altura dela; sem isso a barra cobre o alto de cada cena")
```

Em `checar_js`, no fim da função:

```python
    for exigido in ("'--barra'", "ResizeObserver", "'resize'", ".barra"):
        check(exigido in js, f"historia.js precisa de {exigido}: mede a barra fixa (e toda mudança de altura dela) para o palco começar abaixo dela")
```

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head`
Expected: `FALHOU:` com "o palco gruda abaixo da barra fixa" e "historia.js precisa de '--barra'".

- [ ] **Step 3: CSS e JS**

`index.html`: trocar
`.js-historia .palco{display:block;position:sticky;top:0;height:100vh;height:100svh;margin-bottom:-100vh;margin-bottom:-100svh;overflow:hidden;background:var(--tinta)}`
por
`.js-historia .palco{display:block;position:sticky;top:var(--barra,0px);height:calc(100vh - var(--barra,0px));height:calc(100svh - var(--barra,0px));margin-bottom:calc(-100vh + var(--barra,0px));margin-bottom:calc(-100svh + var(--barra,0px));overflow:hidden;background:var(--tinta)}`
(o `.fundo` continua `inset:0`: o palco já nasce abaixo da barra antes de grudar, então o recuo tem de estar no próprio palco — senão a primeira tela ganha um vão de uma barra e a LCP muda; altura e `margin-bottom` mudam juntos para o comprimento de `#historia` não mudar)

`historia.js`: logo depois de `document.documentElement.classList.add('js-historia');` acrescentar:

```js
// a barra (nome, cargo, botões e régua) é sticky no topo: --barra é a altura dela, para o fundo do palco começar abaixo
var barra=document.querySelector('.barra');
function medirBarra(){if(barra)document.documentElement.style.setProperty('--barra',barra.getBoundingClientRect().height.toFixed(2)+'px');} // sem arredondar: o palco grudado tem de medir o mesmo que em fluxo (senão a LCP oscila entre a tese e o pôster seguinte)
medirBarra();
if(barra&&'ResizeObserver' in window)new ResizeObserver(medirBarra).observe(barra); // fontes que chegam depois, quebra de linha, janela: qualquer mudança de altura
else{addEventListener('resize',function(){clearTimeout(medirBarra.t);medirBarra.t=setTimeout(medirBarra,150);});if(document.fonts)document.fonts.addEventListener('loadingdone',medirBarra);}
```

- [ ] **Step 4: Teste real**

Em `checar_layout`, dentro do laço `for largura, altura in ((1366, 768), (1920, 1080)):`, depois de `time.sleep(0.8)` e antes de ler `direita`:

```python
                topo = json.loads(ws.avaliar("JSON.stringify((function(){var b=document.querySelector('.barra').getBoundingClientRect(),"
                                             "f=document.querySelector('.palco figure.ativo').getBoundingClientRect();return {barra:b.bottom,fundo:f.top};})())"))
                check(abs(topo["fundo"] - topo["barra"]) <= 1, f"{largura}×{altura}: o fundo ativo começa em {topo['fundo']:.1f} px, e o pé da barra está em {topo['barra']:.1f} px (têm de coincidir: nem vão nem sobreposição)")
```

No bloco `with chromium(390, altura=844) as ws:`, logo depois de `navegar(ws)` (ainda em `scrollY=0`, antes de qualquer rolagem):

```python
        vao = json.loads(ws.avaliar("JSON.stringify((function(){var b=document.querySelector('.barra').getBoundingClientRect(),"
                                    "f=document.querySelector('.palco figure.ativo').getBoundingClientRect();return {barra:b.bottom,fundo:f.top,scroll:scrollY};})())"))
        check(vao["scroll"] == 0 and abs(vao["fundo"] - vao["barra"]) <= 1,
              f"390×844 em scrollY=0: o fundo da tese tem de encostar no pé da barra (barra {vao['barra']:.1f}, fundo {vao['fundo']:.1f}, scrollY {vao['scroll']}): sem vão, sem sobreposição")
```

e, dentro do laço `for passo in curtos:`, depois de `time.sleep(0.5)`:

```python
            topo = json.loads(ws.avaliar("JSON.stringify((function(){var b=document.querySelector('.barra').getBoundingClientRect(),"
                                         "f=document.querySelector('.palco figure.ativo').getBoundingClientRect();return {barra:b.bottom,fundo:f.top};})())"))
            check(abs(topo["fundo"] - topo["barra"]) <= 1, f"390×844 em {passo}: o fundo começa em {topo['fundo']:.1f} px, e o pé da barra está em {topo['barra']:.1f} px (têm de coincidir)")
```

Antes de `alturas = {}`:

```python
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
```

- [ ] **Step 5: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3`
Expected: `OK` e `OK` (o `--navegador` leva ~3 min). Se `#historia` sair da linha de base (± 2 px), a causa é outra: `--barra` não muda o comprimento da história.

- [ ] **Step 6: Olhar**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && python3 - <<'EOF'
import sys, time, base64
sys.path.insert(0, 'portfolio/tests'); import check_historia as ch
S='/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad'
for largura, altura, passo, nome in ((390, 844, 'icamento', 'fone'), (1366, 768, 'obra', 'larga')):
    with ch.chromium(largura, ("--enable-unsafe-swiftshader",), altura=altura) as ws:
        ws.comando("Page.navigate", url=f"http://127.0.0.1:{ch.PORTA}/site/index.html"); time.sleep(2.5)
        ws.avaliar(f"(function(){{var r=document.getElementById('{passo}').getBoundingClientRect();window.scrollTo(0,scrollY+r.top+r.height*.5-innerHeight/2);}})()")
        time.sleep(5)
        open(f"{S}/barra-{nome}.png","wb").write(base64.b64decode(ws.comando("Page.captureScreenshot", format="png")["data"]))
EOF
```
Abrir `barra-fone.png` e `barra-larga.png` com a ferramenta Read. Expected: a cena começa logo abaixo da régua, não atrás da barra; no desktop o cartão "MESMO DADO" de cima aparece inteiro (ainda pode faltar o foco da Task 2 em janelas mais largas).

- [ ] **Step 7: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/index.html portfolio/site/historia.js portfolio/tests/check_historia.py && git commit -m "História: o fundo do palco começa abaixo da barra fixa (--barra medida pelo historia.js)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Foco vertical por clipe (`foco-alto`, `foco-baixo`)

**Files:**
- Modify: `portfolio/site/index.html` (5 figures; CSS depois de `.js-historia .palco .fundo.clipe img{…}`)
- Modify: `portfolio/tests/check_historia.py` (`FOCO`, `checar_fundo`, `checar_css`, `checar_layout`)

**Interfaces:**
- Consumes: `--barra` (Task 1): é ela que torna o palco mais baixo que 16:9 e faz o recorte vertical existir.
- Produces: `FOCO = {"obra": "alto", "casa": "alto", "whatsapp": "alto", "icamento": "alto", "escala": "baixo"}` (o plano irmão não acrescenta focos; cenas novas ficam a 50 %).

- [ ] **Step 1: Testes estáticos que falham**

Em `check_historia.py`, logo depois de `LONGAS = …`:

```python
FOCO = {"obra": "alto", "casa": "alto", "whatsapp": "alto", "icamento": "alto", "escala": "baixo"}  # assunto encostado no alto / no pé do quadro 16:9
```

Em `checar_fundo`, depois de `classe = {"img": "fundo", "ano": "fundo tipo", "clipe": "fundo clipe"}[tipo]`:

```python
    if tipo == "clipe" and passo in FOCO:
        classe += " foco-" + FOCO[passo]
```

Em `checar_css`, depois da checagem de `.fundo.clipe img{filter:none;object-position:68% 50%}`:

```python
    check(".js-historia .palco .fundo.foco-alto video,.js-historia .palco .fundo.foco-alto img{object-position:68% 0%}" in css
          and ".js-historia .palco .fundo.foco-baixo video,.js-historia .palco .fundo.foco-baixo img{object-position:68% 100%}" in css,
          "foco vertical por clipe: .foco-alto recorta pelo pé e .foco-baixo pelo alto (janela mais larga que 16:9); vídeo e pôster iguais")
```

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head`
Expected: `FALHOU:` com `cena obra: classe da figura 'fundo clipe', esperava 'fundo clipe foco-alto'` (e casa, whatsapp, icamento, escala) e "foco vertical por clipe".

- [ ] **Step 3: Marcação e CSS**

Nas figures de `obra`, `casa`, `whatsapp` e `icamento`: `class="fundo clipe"` → `class="fundo clipe foco-alto"`; em `escala`: `class="fundo clipe foco-baixo"`. Nada mais muda nessas linhas.

CSS, logo depois de `.js-historia .palco .fundo.clipe img{filter:none;object-position:68% 50%}`:

```css
/* quando a janela é mais larga que 16:9 (o palco perde a altura da barra), o recorte vertical favorece o lado onde está o assunto */
.js-historia .palco .fundo.foco-alto video,.js-historia .palco .fundo.foco-alto img{object-position:68% 0%}
.js-historia .palco .fundo.foco-baixo video,.js-historia .palco .fundo.foco-baixo img{object-position:68% 100%}
```

- [ ] **Step 4: Teste real (21:9)**

Em `checar_layout`, antes de `alturas = {}`:

```python
    with chromium(2560, altura=1080) as ws:  # 21:9: o palco recorta ~40 % da altura do 16:9; o foco por clipe mantém o assunto
        navegar(ws)
        for passo, esperado in (("obra", "68% 0%"), ("escala", "68% 100%"), ("sige", "68% 50%")):
            rolar_ate(ws, passo, 0.5)
            time.sleep(0.5)
            pos = ws.avaliar(f"getComputedStyle(document.querySelector('figure.clipe[data-passo=\"{passo}\"] video')).objectPosition")
            check(pos == esperado, f"2560×1080: object-position de {passo} é {pos!r}, esperava {esperado!r}")
```

- [ ] **Step 5: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3`
Expected: `OK`, `OK`.

- [ ] **Step 6: Olhar**

Repetir o script do Step 6 da Task 1 trocando `(390, 844, 'icamento', 'fone'), (1366, 768, 'obra', 'larga')` por `(1366, 768, 'casa', 'casa'), (1366, 768, 'escala', 'escala'), (2560, 1080, 'obra', 'ultra')` e o prefixo `barra-` por `foco-`. Abrir os três PNG. Expected: `casa` com o módulo no ar inteiro; `escala` com as 12 miniaturas inteiras no pé; `obra` a 21:9 com os cartões no alto e o chão cortado (não o contrário).

- [ ] **Step 7: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/index.html portfolio/tests/check_historia.py && git commit -m "História: foco vertical por clipe (foco-alto em obra, casa, whatsapp e icamento; foco-baixo em escala)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Marcos tipográficos na tela larga

**Files:**
- Modify: `portfolio/site/index.html` (bloco `@media (min-width:900px) and (orientation:landscape){…}`)
- Modify: `portfolio/tests/check_historia.py` (`checar_css`)

- [ ] **Step 1: Teste estático que falha**

Em `checar_css`, logo depois da checagem `"tela larga: a faixa de texto vai para a esquerda, como no filme"`:

```python
    check(".js-historia .palco .fundo.tipo{justify-content:flex-end;padding:0 4vw 3vh 0}" in larga,
          "tela larga: o marco tipográfico (.ano) vai para a direita, longe da faixa de texto à esquerda")
```

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -5`
Expected: `FALHOU:` com "o marco tipográfico (.ano) vai para a direita".

- [ ] **Step 3: CSS**

No bloco `@media (min-width:900px) and (orientation:landscape){…}`, antes do `}` final, acrescentar `.js-historia .palco .fundo.tipo{justify-content:flex-end;padding:0 4vw 3vh 0}`.

- [ ] **Step 4: Ver passar e olhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py`
Expected: `OK`. Capturar `galpoes` a 1366×768 (script do Step 6 da Task 1, `(1366, 768, 'galpoes', 'tipo')`, prefixo `tipo-`) e abrir: "22 baias" inteiro à direita, sem a faixa por cima.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/index.html portfolio/tests/check_historia.py && git commit -m "História: na tela larga o marco tipográfico vai para a direita, longe da faixa

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Celular deitado

**Files:**
- Modify: `portfolio/site/index.html` (bloco `@media` novo, depois do bloco de tela larga)
- Modify: `portfolio/tests/check_historia.py` (`checar_css`, `checar_layout`)

- [ ] **Step 1: Testes que falham**

Em `checar_css`, depois das checagens do bloco `larga`:

```python
    paisagem = bloco_css(css, "@media (orientation:landscape) and (max-height:520px){")
    check(".js-historia .texto{max-width:min(560px,54vw);margin-left:16px;text-align:left;padding:12px 16px}" in paisagem
          and ".js-historia .frase{font-size:clamp(1.4rem,6.5vh,2.4rem);margin:0}" in paisagem,
          "celular deitado (≤ 520 px de altura): faixa à esquerda, mais estreita e com o título menor, para o clipe continuar à mostra")
```

Em `checar_layout`, antes de `alturas = {}`:

```python
    with chromium(844, altura=390) as ws:  # celular deitado
        navegar(ws)
        for passo in ("sige", "icamento"):
            rolar_ate(ws, passo, 0.5)
            time.sleep(0.8)
            r = json.loads(ws.avaliar(f"JSON.stringify((function(){{var r=document.querySelector('#{passo} .texto').getBoundingClientRect();"
                                      f"return {{w:r.width,direita:r.right/innerWidth,h:r.height/innerHeight}};}})())"))
            check(r["w"] > 0 and r["direita"] <= 0.62, f"844×390: a faixa de {passo} termina em {r['direita']:.2f} da largura (máx. 0,62; largura {r['w']:.0f})")
            check(r["h"] <= 0.92, f"844×390: a faixa de {passo} ocupa {r['h']:.0%} da altura (máx. 92 %)")
```

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -5`
Expected: `FALHOU:` com "celular deitado".

- [ ] **Step 3: CSS**

Depois do bloco `@media (min-width:900px) and (orientation:landscape){…}` (o bloco de paisagem baixa vem depois para vencer em empate):

```css
/* celular deitado (≤ 520 px de altura): faixa à esquerda, estreita e com o título menor, para o clipe continuar à mostra */
@media (orientation:landscape) and (max-height:520px){.js-historia .cena{justify-content:flex-start;padding:calc(var(--barra,0px) + 12px) 16px 24px}.js-historia .texto{max-width:min(560px,54vw);margin-left:16px;text-align:left;padding:12px 16px}.js-historia .frase{font-size:clamp(1.4rem,6.5vh,2.4rem);margin:0}.js-historia .ressalva{margin:8px 0 0;font-size:.78rem}.js-historia .cta{justify-content:flex-start;margin-top:12px}.js-historia .cena.longa .texto{top:calc(var(--barra,0px) + 8px)}}
```

- [ ] **Step 4: Ver passar e olhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3`
Expected: `OK`, `OK`. Capturar `icamento` a 844×390 (script do Step 6 da Task 1, `(844, 390, 'icamento', 'deitado')`, prefixo `paisagem-`) e abrir: faixa à esquerda, o módulo no balancim visível à direita, nada cortado embaixo.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/index.html portfolio/tests/check_historia.py && git commit -m "História: celular deitado com a faixa à esquerda e menor (o clipe continua à mostra)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: `clipes.js` — despejo pelo navegador (antes ou depois dos metadados) e `seeked` sem quadro

**Files:**
- Modify: `portfolio/site/clipes.js`
- Modify: `portfolio/tests/check_historia.py` (`checar_clipes_js`, `checar_evicao` novo, `main`)

**Interfaces:**
- Consumes: o contrato `fig.__clipe = {dur, frozen, seek, descarregar, pronto, morto, perto, dist, carregar}` (inalterado).
- Produces: `esperados` (contador dos `emptied` que o nosso próprio `load()` enfileira) e `recarregar()`; a variável `meta` sai.

Fundamento (HTML, algoritmo de carga do media element): `load()` **enfileira** um `emptied` só quando `networkState !== NETWORK_EMPTY (0)`, e antes disso **descarta** as tarefas pendentes do elemento (inclusive um `emptied` ainda não disparado do `load()` anterior). Logo, depois de cada `load()` nosso há **no máximo um** `emptied` nosso a caminho: `esperados` é atribuído (1 ou 0), nunca incrementado; no `loadedmetadata` zera (o `emptied` nosso já chegou ou foi descartado). Qualquer `emptied` fora da conta é do navegador.

- [ ] **Step 1: Testes que falham**

Em `checar_clipes_js`, na tupla `exigido`, acrescentar `"'progress'"`, `"'emptied'"`, `"networkState"`, `"esperados"`.

Depois de `checar_reduzido_real` (antes de `checar_dados`):

```python
def checar_evicao():
    """Despejo pelo navegador (WebKit sob pressão de memória, simulado de fora reatribuindo o mesmo src com preload='none'): depois de
    .viva, o clipe da cena ativa recarrega sozinho; despejado antes dos metadados (rede lenta emulada pelo CDP), também
    recarrega — o 'emptied' do nosso próprio load() não é confundido com o do navegador."""
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
        # despejo ANTES dos metadados: com a rede a 20 KB/s os metadados demoram ~1 s; o src já está atribuído e readyState ainda é 0.
        # Antes: descarregar casa (ir ao zip até ela ficar sem src) e desligar o cache, senão casa pode já estar carregada (FOLGA) ou vir do cache
        rolar_ate(ws, "zip", 0.5)
        esperar(ws, "!document.querySelector('figure.clipe[data-passo=\"casa\"] video').hasAttribute('src')", 5)
        ws.comando("Network.enable")
        ws.comando("Network.setCacheDisabled", cacheDisabled=True)
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
```

Em `main()`, chamar `checar_evicao()` logo depois de `checar_reduzido_real()`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -6`
Expected: `FALHOU:` com `clipes.js precisa de 'progress'`, `'emptied'` já existe (não falha), `networkState`, `esperados`.

- [ ] **Step 3: `clipes.js`**

Na linha das variáveis por figura, trocar
`var alvo=-1,pedido=-1,emVoo=0,vivo=false,lentos=0,tinha=false,ligado=false,meta=false; // meta: já houve 'loadedmetadata' desde o último carregar()`
por
`var alvo=-1,pedido=-1,emVoo=0,vivo=false,lentos=0,tinha=false,ligado=false,esperados=0; // esperados: 'emptied' que os nossos load() ainda vão disparar`

Trocar `carregar` e `descarregar` por:

```js
  function recarregar(){esperados=v.networkState!==0?1:0;v.load();}     // load() descarta o 'emptied' pendente do load() anterior e enfileira no máximo um (só se networkState ≠ EMPTY)
  function carregar(){
    if(api.pronto||api.morto||reduzir.matches)return;
    if(todas.filter(function(a){return a.pronto;}).length>=MAXIMO)return;  // trava de segurança: arrumar() já desocupou a vaga antes de chamar
    api.pronto=true;
    v.setAttribute('src',src);v.preload='auto';recarregar();
  }
  function descarregar(){
    if(!api.pronto)return;
    api.pronto=false;pedido=-1;emVoo=0;viver(false);v.removeAttribute('src');recarregar();
  }
```

Trocar o ouvinte de `loadedmetadata` por:

```js
  v.addEventListener('loadedmetadata',function(){
    esperados=0;                                                          // todo 'emptied' nosso já chegou (ou foi descartado por um load() seguinte)
    if(!v.seekable.length||v.seekable.end(0)<dur-0.5){congelar();return;} // servidor sem Range: não dá para buscar; fica o pôster
    pedir();
  });
```

Depois do ouvinte de `loadeddata`, acrescentar:

```js
  v.addEventListener('progress',function(){if(!vivo&&alvo>=0&&!emVoo&&v.readyState>=2)pedir();}); // Safari: 'seeked' sem quadro e os dados chegam depois
```

Trocar o ouvinte de `emptied` por:

```js
  v.addEventListener('emptied',function(){                                  // WebKit sob pressão de memória esvazia o vídeo sozinho
    if(esperados>0){esperados--;return;}                                    // este veio do nosso load() (carregar/descarregar), não é despejo
    if(v.readyState!==0||!api.pronto)return;
    viver(false);api.pronto=false;pedido=-1;emVoo=0;v.removeAttribute('src');arrumar(); // foi o navegador: libera a vaga (sem src, nem o WebKit recarrega sozinho) e recarrega quando voltar a estar entre os mais perto
  });
```

Conferir que `meta` não aparece mais em lugar nenhum: `grep -n 'meta' portfolio/site/clipes.js` só pode devolver `loadedmetadata`.

- [ ] **Step 4: Medir a conta dos `emptied` (prova do fundamento)**

```bash
cd /home/runner/workspace && python3 - <<'EOF'
import sys, time, json
sys.path.insert(0, 'portfolio/tests'); import check_historia as ch
with ch.chromium(390, altura=844) as ws:
    ch.navegar(ws)
    ws.avaliar("window.__emp=[];[].forEach.call(document.querySelectorAll('figure.clipe video'),function(v,i){v.addEventListener('emptied',function(){__emp.push(v.parentNode.dataset.passo+':'+v.networkState);});});")
    ch.rolar_ate(ws, "icamento", 0.4); time.sleep(3)
    ch.rolar_ate(ws, "zip", 0.5); time.sleep(2)      # o içamento sai da faixa: descarregar()
    ch.rolar_ate(ws, "icamento", 0.4); time.sleep(3)  # volta: carregar()
    print("emptied vistos:", ws.avaliar("JSON.stringify(window.__emp)"))
    print("estado:", ch.ler_clipe(ws, "icamento"))
EOF
```
Expected: cada `carregar()` e cada `descarregar()` aparece com exatamente um `emptied` (nunca dois seguidos da mesma figura sem um `loadedmetadata` no meio), e o içamento termina `viva: True` com `src`. Se um `carregar()` mostrar dois `emptied`, o `setAttribute('src')` também enfileirou um: nesse caso contar também ele (`esperados++` antes do `setAttribute` quando `v.networkState!==0`) e repetir a medição. Registrar o resultado no relatório.

- [ ] **Step 5: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3`
Expected: `OK`, `OK` (com `checar_evicao` dentro).

- [ ] **Step 6: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/clipes.js portfolio/tests/check_historia.py && git commit -m "clipes.js: o despejo pelo navegador é reconhecido pela conta dos emptied nossos (antes ou depois dos metadados); progress refaz o seek sem quadro

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: `clipes.js` — `seekable` tardio (`ESPERA_RANGE`)

**Files:**
- Modify: `portfolio/site/clipes.js`
- Modify: `portfolio/tests/check_historia.py` (`checar_clipes_js`)

- [ ] **Step 1: Testes que falham**

Em `checar_clipes_js`, acrescentar `"ESPERA_RANGE=1500"`, `"temRange"`, `"desde"` e `"||!temRange()"` à tupla `exigido`.

Em `ESPIAO`, acrescentar um contador de `.viva` que nunca zera (para provar que sem Range a classe **nunca** apareceu, não só que não está lá no fim):
```python
    "window.__vivas=0;new MutationObserver(function(ms){ms.forEach(function(m){if(m.target.classList&&m.target.classList.contains('viva'))window.__vivas++;});})"
    ".observe(document,{attributes:true,attributeFilter:['class'],subtree:true});"  # document, não documentElement: quando o espião roda ainda não há <html>
```
e no bloco "sem Range" de `checar_clipe_real`, depois da leitura `c, e = …`, acrescentar:
```python
        check(ws.avaliar("window.__vivas") == 0, f"servidor sem Range: .viva nunca pode aparecer, nem por instantes (apareceu {ws.avaliar('window.__vivas')}×)")
```

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -4`
Expected: `FALHOU:` com `clipes.js precisa de ESPERA_RANGE=1500`.

- [ ] **Step 3: `clipes.js`**

Na linha das constantes, trocar `var FPS=24,TETO=250,LENTOS=3,VOO=600,MAXIMO=2,FOLGA=100;` por `var FPS=24,TETO=250,LENTOS=3,VOO=600,MAXIMO=2,FOLGA=100,ESPERA_RANGE=1500;` e acrescentar ao comentário da linha `; ms de espera por um seekable completo antes de congelar`.

Trocar o ouvinte de `loadedmetadata` (Task 5) por:

```js
  function temRange(){return v.seekable.length>0&&v.seekable.end(0)>=dur-0.5;}
  function conferirRange(ini){                                              // sem Range o Chrome diz seekable [0,0] (um seek cai no quadro 0);
    if(!api.pronto||ini!==desde)return;                                     // o Safari pode preencher seekable só depois: espera ESPERA_RANGE antes de desistir;
    if(temRange()){pedir();return;}                                         // a cadeia morre se a figura descarregou ou recarregou (desde mudou)
    if(performance.now()-ini>ESPERA_RANGE){congelar();return;}
    setTimeout(function(){conferirRange(ini);},250);
  }
  v.addEventListener('loadedmetadata',function(){esperados=0;conferirRange(desde=performance.now());});
```

Na linha das variáveis por figura, acrescentar `desde=0` (`…,esperados=0,desde=0;`), e em `recarregar()` zerar: `function recarregar(){desde=0;esperados=v.networkState!==0?1:0;v.load();}`.

Em `pedir()`, a primeira guarda ganha `||!temRange()`:
`if(!api.pronto||api.morto||reduzir.matches||alvo<0||v.readyState<1||!temRange())return;   // nunca antes dos metadados nem sem seekable completo: o alvo fica guardado`
(sem isso, `loadeddata`/`progress` fazem um seek durante a espera, o Chrome sem Range o leva ao quadro 0 e a figura fica `.viva` no quadro errado por 1,5 s).

No ouvinte de `progress` (Task 5), tirar o `!emVoo` — `pedir()` já aplica o prazo `VOO` a um seek perdido: `v.addEventListener('progress',function(){if(!vivo&&alvo>=0&&v.readyState>=2)pedir();});`

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3`
Expected: `OK`, `OK`. O bloco "sem Range" de `checar_clipe_real` (espera de 5 s) continua a passar: congela em ≤ 1,5 s + metadados.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/clipes.js portfolio/tests/check_historia.py && git commit -m "clipes.js: espera até 1,5 s por um seekable completo antes de congelar no pôster (Safari preenche seekable tarde)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: O fim do clipe limitado num lugar só

**Files:**
- Modify: `portfolio/site/clipes.js` (`quadro` por figura)
- Modify: `portfolio/site/historia.js` (`sincronizar`)
- Modify: `portfolio/tests/check_historia.py` (`quadro`, `checar_clipe_real`, `checar_clipes_js`, `checar_js`)

- [ ] **Step 1: Testes que falham**

Trocar a função `quadro` do `check_historia.py` por:

```python
def quadro(t, dur):
    """O quantizador do clipes.js: o meio do quadro mais próximo a 24 fps, nunca além do último quadro do clipe."""
    return (min(int(t * 24 + 0.5), int(round(dur * 24)) - 1) + 0.5) / 24
```

Em `checar_clipe_real`, trocar `quadro(0.4 * dur)` por `quadro(0.4 * dur, dur)` (duas vezes na mesma linha), `quadro(0.75 * dur)` por `quadro(0.75 * dur, dur)`, e as duas ocorrências de `quadro(1 + 29 * 0.2)` por `quadro(1 + 29 * 0.2, dur)`. Depois do bloco do 75 % (a checagem `içamento a 75 %`), acrescentar:

```python
        rolar_ate(ws, "icamento", 1.0)  # o fim da cena pede o último quadro, nunca além da duração
        alvo = quadro(dur, dur)
        esperar(ws, f"Math.abs({VIDEO_ICAMENTO}.currentTime-{alvo})<=0.15", 3)
        c = ler_clipe(ws, "icamento")
        check(abs(c["t"] - alvo) <= 0.15 and c["t"] < dur, f"içamento a 100 %: currentTime {c['t']:.3f} ≠ último quadro {alvo:.3f} (nunca ≥ dur={dur})")
```

Em `checar_clipes_js`, acrescentar `"Math.min(Math.round(t*FPS),ultimo)"` à tupla `exigido`. Em `checar_js`, acrescentar `"*0.999"` à tupla `proibido`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -5`
Expected: `FALHOU:` com `clipes.js precisa de Math.min(Math.round(t*FPS),ultimo)` e `historia.js não pode usar *0.999`.

- [ ] **Step 3: JS**

`clipes.js`: apagar a linha `function quadro(t){return (Math.round(t*FPS)+0.5)/FPS;}` do topo. Dentro de `figs.forEach`, logo depois da linha `var alvo=-1,pedido=-1,…,esperados=0;`, acrescentar:

```js
  var ultimo=Math.round(dur*FPS)-1;                                         // índice do último quadro: o fim da cena pede este quadro, nunca além
  function quadro(t){return (Math.min(Math.round(t*FPS),ultimo)+0.5)/FPS;}
```

`historia.js`: trocar `api.seek(progresso(r.top,r.height,innerHeight)*api.dur*0.999);` por `api.seek(progresso(r.top,r.height,innerHeight)*api.dur);` (o `clipes.js` limita ao último quadro).

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3`
Expected: `OK`, `OK`. No harness, `seek {passo}=500` e `seek25 {passo}=250` (tolerância ± 20 já existente).

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/clipes.js portfolio/site/historia.js portfolio/tests/check_historia.py && git commit -m "clipes.js: o quantizador nunca passa do último quadro; historia.js pede progresso·dur sem o 0,999

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: `PRONTO` com prazo no render

**Files:**
- Modify: `portfolio/filme/render_clipes.py` (`main`)
- Modify: `portfolio/tests/check_filme.py` (`checar_cenas_portadas`, `checar_render_clipes` novo, `main`)

- [ ] **Step 1: Teste que falha**

Em `check_filme.py`, depois de `checar_readme`:

```python
def checar_render_clipes():
    """render_clipes.py espera as texturas (PRONTO) com prazo: sem ele, uma textura que nunca resolve trava o render em silêncio."""
    src = (ROOT / "filme" / "render_clipes.py").read_text(encoding="utf-8")
    check("Promise.race([PRONTO" in src and "20000" in src, "render_clipes.py: PRONTO precisa de prazo (Promise.race com 20000 ms)")
```

Em `main()`, chamar `checar_render_clipes()` logo depois de `checar_readme()`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py 2>&1 | head -4`
Expected: `FALHOU:` com "PRONTO precisa de prazo".

- [ ] **Step 3: O prazo**

Em `render_clipes.py`, logo antes de `def main():`:

```python
PRONTO_COM_PRAZO = ("Promise.race([PRONTO, new Promise(function(_, falha){setTimeout(function(){"
                    "falha(new Error('PRONTO: 20 s sem resolver (textura das cenas portadas?)'));}, 20000);})])")
```

e em `main()` trocar `pagina.evaluate("PRONTO")  # texturas das cenas portadas (a planta real) carregadas` por `pagina.evaluate(PRONTO_COM_PRAZO)  # texturas das cenas portadas (a planta real): com prazo, para o render nunca travar em silêncio`.

Em `check_filme.py`, `checar_cenas_portadas`: `from render_clipes import ARGS` → `from render_clipes import ARGS, PRONTO_COM_PRAZO`, e `pg.evaluate("PRONTO")` → `pg.evaluate(PRONTO_COM_PRAZO)`.

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py && python3 portfolio/tests/check_filme.py --cenas icamento`
Expected: `OK`, `OK`.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/render_clipes.py portfolio/tests/check_filme.py && git commit -m "render_clipes.py: PRONTO com prazo de 20 s (o render falha alto em vez de travar)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: Higiene dos testes

**Files:**
- Modify: `portfolio/tests/check_historia.py`
- Modify: `portfolio/tests/check_filme.py`

Cada item abaixo é uma troca exata. Nenhum limiar muda.

- [ ] **Step 1: `check_historia.py`**

(a) Em `checar_css`, trocar `check(".fundo video{display:none}" in css, "modo empilhado: o vídeo não existe, fica a imagem")` por:
```python
    check(re.search(r"(^|[}\n])\.fundo video\{display:none\}", css) is not None, "modo empilhado: a regra .fundo video{display:none} (a do movimento reduzido não vale por ela)")
```

(b) Em `TROCA_404`, trocar `window.__troca=window.Historia?'tarde':'antes'` por `window.__troca=f.__clipe?'tarde':'antes'` (é o `clipes.js` que lê `data-clipe`, não o `historia.js`).

(c) Em `LER_CLIPES`, depois de `"mp4:mp4.length,` acrescentar `pedidos404:res.filter(function(e){return /nao-existe\\.mp4/.test(e.name);}).length,`. Em `checar_clipe_real`, o bloco do 404 passa a:
```python
        rolar_ate(ws, "whatsapp", 0.5)
        esperar(ws, "(function(){var f=document.querySelector('figure.clipe[data-passo=\"whatsapp\"]');return !!f.__clipe&&f.__clipe.morto===true;})()", 5)
        c, e = ler_clipe(ws, "whatsapp"), ler_clipes(ws)
        check(e["pedidos404"] >= 1, f"o clipe trocado para 404 tem de ter sido pedido ({e['pedidos404']} pedidos a nao-existe.mp4)")
        check(not c["viva"] and c["img"] == "visible" and c["src"] is None and c["ready"] == 0,
              f"clipe inexistente (404): fica o pôster, sem .viva e sem src (estado: {c})")
        check(e["erros"] == [], f"console limpo com um clipe em 404: {e['erros']}")
```

(d) Mensagens com o valor medido:
- `check(ws.avaliar("window.__troca") == "antes", "o espião do 404 precisa trocar data-clipe antes de o clipes.js rodar")` → `troca = ws.avaliar("window.__troca")` na linha anterior e `check(troca == "antes", f"o espião do 404 precisa trocar data-clipe antes de o clipes.js rodar (__troca={troca!r})")`.
- Em `checar_reduzido_real`: `check(voltou and ler_clipes(ws)["ativa"] == "casa", "ao desligar o movimento reduzido, o clipe ativo (casa) recarrega em ≤ 2 s")` → `c, e = ler_clipe(ws, "casa"), ler_clipes(ws)` e `check(voltou and e["ativa"] == "casa", f"ao desligar o movimento reduzido, o clipe ativo (casa) recarrega em ≤ 2 s (readyState {c['ready']}, ativa {e['ativa']!r})")`.
- Em `checar_dados`: `check(e["jsHistoria"], f"navigator.connection={conexao}: o modo cenas continua")` → `check(e["jsHistoria"], f"navigator.connection={conexao}: o modo cenas continua (js-historia={e['jsHistoria']})")`.

(e) Em `checar_foco`: `esperar(ws, "document.querySelector('figure.clipe[data-passo=\"icamento\"]').classList.contains('viva')", 25)` → `check(esperar(ws, "document.querySelector('figure.clipe[data-passo=\"icamento\"]').classList.contains('viva')", 25), "içamento .viva antes do Tab (o teste vale com clipe carregado)")`.

(f) Em `checar_layout`, no laço das telas largas: `direita = ws.avaliar(f"document.querySelector('#{passo} .texto').getBoundingClientRect().right/innerWidth")` → `r = json.loads(ws.avaliar(f"JSON.stringify((function(){{var r=document.querySelector('#{passo} .texto').getBoundingClientRect();return {{w:r.width,direita:r.right/innerWidth}};}})())"))` e `check(direita <= 0.54, …)` → `check(r["w"] > 0 and r["direita"] <= 0.54, f"{largura}×{altura}: a faixa de texto de {passo} termina em {r['direita']:.2f} da largura (máx. 0,54; largura {r['w']:.0f})")`. No bloco 390×844, o JSON ganha `w:r.width,` e a primeira checagem vira `check(r["w"] > 0 and r["h"] <= 0.75, …)`.

(g) Mensagem do `--relogio`: `"--relogio (o .ano dos fundos tipográficos) (texto grande, negrito) sobre a faixa: mínimo 3:1 no pior caso"` → `"--relogio, o .ano dos fundos tipográficos (texto grande, negrito), sobre a faixa: mínimo 3:1 no pior caso"`.

(h) `def navegador(largura=390, extra=("--disable-3d-apis",)):` → `def navegador(largura=390, extra=()):` (a página não roda mais WebGL).

(i) Em `main()`:
```python
    if "--origem" in sys.argv:
        i = sys.argv.index("--origem") + 1
        if i >= len(sys.argv) or sys.argv[i].startswith("--"):
            sys.exit("--origem pede a URL da origem publicada, por exemplo: --origem https://exemplo.com")
        checar_origem(sys.argv[i])
```

(j) `ler_clipes` e `ler_clipe` sem traceback quando a página lança:
```python
VAZIO_CLIPES = {"mp4": 0, "pedidos404": 0, "mp4AntesDoLoad": 0, "three": 0, "comDados": [], "comSrc": [], "vivas": [], "pausados": False,
                "plays": 0, "erros": ["exceção ao ler o estado dos clipes"], "ativa": None, "jsHistoria": False}
VAZIO_CLIPE = {"viva": False, "frozen": False, "dur": None, "ready": -1, "seekEnd": -1, "t": -1, "img": "?", "video": "?", "opacidade": "?", "src": None, "paused": None}


def ler_clipes(ws):
    """Resumo dos clipes da página: requisições .mp4 (e se alguma veio antes do load), vídeos com dados/src, .viva, play(), erros."""
    bruto = ws.avaliar(LER_CLIPES)
    check(bruto is not None, "a página lançou uma exceção ao ler o estado dos clipes (LER_CLIPES não devolveu nada)")
    return json.loads(bruto) if bruto else dict(VAZIO_CLIPES)
```
e em `ler_clipe`, o `return json.loads(ws.avaliar(…))` vira `bruto = ws.avaliar(…)` + `check(bruto is not None, f"a página lançou uma exceção ao ler o clipe {passo}")` + `return json.loads(bruto) if bruto else dict(VAZIO_CLIPE)`.

- [ ] **Step 2: `check_filme.py`**

(k) Docstring, linha 2: `"""Checagens do filme (portfolio/filme/film.html) e do clipes (portfolio/site/video/cena-*) e trailer de envio (portfolio/filme/saida/).` → `"""Checagens do filme (portfolio/filme/film.html), dos clipes de fundo (portfolio/site/video/cena-*) e do trailer de envio (portfolio/filme/saida/).`

(l) `checar_reproducao`: trocar `subprocess.run([sys.executable, str(Path(tmp) / "corrigir_filme.py")], check=True, capture_output=True)` e a checagem seguinte por:
```python
        r = subprocess.run([sys.executable, str(Path(tmp) / "corrigir_filme.py")], capture_output=True, text=True)
        ultima = r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "sem mensagem"
        check(r.returncode == 0, f"corrigir_filme.py falhou sobre o zip: {ultima}")
        if r.returncode == 0:
            check((Path(tmp) / "film.html").read_bytes() == FILME.read_bytes(),
                  "corrigir_filme.py não reproduz o film.html commitado a partir do zip (F-02)")
```

- [ ] **Step 3: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3 && python3 portfolio/tests/check_historia.py --origem 2>&1 | tail -1`
Expected: `OK`, `OK`, `OK`, e a última linha `--origem pede a URL da origem publicada…` (saída 1).

- [ ] **Step 4: Commit**

```bash
cd /home/runner/workspace && git add portfolio/tests/check_historia.py portfolio/tests/check_filme.py && git commit -m "Testes: checagens que não passam sem provar (regra do vídeo ancorada, 404 pedido de verdade, precondições em check, caixas com largura), mensagens com o valor medido, --origem sem URL, exceção de JS vira FALHOU

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: `maquetes.js` sem a cena morta do içamento

**Files:**
- Modify: `portfolio/site/maquetes.js` (apagar `function cenaIcamento(fig){…}` e a chave `'icamento'` de `CENAS`)
- Modify: `portfolio/tests/check_historia.py` (`checar_maquetes_js`)

- [ ] **Step 1: Teste que falha**

Trocar `checar_maquetes_js` por:

```python
def checar_maquetes_js():
    js = (SITE / "maquetes.js").read_text(encoding="utf-8")
    check("dur:sc.dur" in js, "maquetes.js precisa expor a duração da cena em fig.__maquete.dur")
    check("cenaIcamento" not in js and "'icamento'" not in js,
          "maquetes.js: a cena do içamento vive só no film.html (SC[10], clipe cena-icamento); a página não roda mais WebGL na história")
    check('data-cena="icamento"' not in PORTFOLIO.read_text(encoding="utf-8"), "portfolio.html não tem maquete do içamento")
    check("var CENAS={'36min':cena36,'casa-viaja':cenaCasa};" in js, "CENAS do maquetes.js: só 36min e casa-viaja")
```

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -4`
Expected: `FALHOU:` com "a cena do içamento vive só no film.html" e "CENAS do maquetes.js".

- [ ] **Step 3: Apagar**

Em `maquetes.js`, apagar os dois comentários de cabeçalho da cena (`// ---------- CENA: o módulo sobe pelo balancim …` e `// Com o balancim, os cabos descem verticais…`) e da linha `function cenaIcamento(fig){` até a linha que fecha essa função (a última `}` antes de `var CENAS=`), inclusive; trocar `var CENAS={'36min':cena36,'casa-viaja':cenaCasa,'icamento':cenaIcamento};` por `var CENAS={'36min':cena36,'casa-viaja':cenaCasa};`. Conferir: `grep -n "cenaIcamento\|'icamento'" portfolio/site/maquetes.js` não devolve nada; `grep -c "function cena" portfolio/site/maquetes.js` devolve 2.

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_site.py`
Expected: `OK`, `OK`. Abrir `portfolio.html` no Chromium (`python3 portfolio/tests/check_site.py` já cobre a marcação; para ver: `curl -s http://127.0.0.1:5000/portfolio.html | grep -c 'data-cena'` → `2`).

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/maquetes.js portfolio/tests/check_historia.py && git commit -m "maquetes.js: sai a cena do içamento, que só vive no film.html; CENAS fica com 36min e casa-viaja

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 11: Reenquadramento de `escala` (miniaturas) e `icamento` (o cavalo)

**Files:**
- Modify: `portfolio/filme/film.html` (`st.cam` de `SC[7]`; `st.cavalo` e `st.cam` de `SC[10]`)
- Modify: `portfolio/filme/corrigir_filme.py` (`TROCAS_RODADA_9` novo; `CENA_ICAMENTO`)
- Modify: `portfolio/tests/check_filme.py` (`ENQUADRAMENTOS`, `checar_cenas_portadas`)
- Modify: `portfolio/site/video/cena-escala.mp4`, `cena-escala.webp`, `cena-icamento.mp4`, `cena-icamento.webp` (re-render)

**Interfaces:**
- Consumes: `renderCena(i, t)`, `cam`, `SC[7].minis` (12 grupos), `SC[10]` (bloco portado).
- Produces: `SC[10].cavalo` (a caixa laranja do cavalo da carreta); `ENQUADRAMENTOS = {passo: (expressão, esperado)}` avaliado no `--cenas`.

Nota: `SC[7]` também é a cena do trailer (`render.py`); o trailer de envio não é regenerado por este plano (fica no `saida/`, fora do git). Quem quiser o trailer com a câmera nova roda `python3 portfolio/filme/render.py`.

- [ ] **Step 1: Testes que falham**

Em `check_filme.py`, depois de `LEITURAS = {…}`:

```python
ENQUADRAMENTOS = {  # no último quadro do trecho, o assunto inteiro dentro do quadro (F-13; prints de 24/09)
    "escala": ("(function(){renderCena(7,10);return SC[7].minis.every(function(m){var p=m.position.clone();p.y+=1.2;p.project(cam);"
               "return Math.abs(p.x)<.98&&p.y>-.94&&p.y<.98;});})()", True),
    "icamento": ("(function(){var st=SC[10];renderCena(10,10);var p=st.cavalo.position.clone();p.project(cam);return p.x<.9&&Math.abs(p.y)<.95;})()", True),
}
```

Em `checar_cenas_portadas`, dentro do `for passo in passos:` depois do bloco `if pg.evaluate(f"!!SC[{idx}]"):`, acrescentar:

```python
            if passo in ENQUADRAMENTOS:
                exp, esperado = ENQUADRAMENTOS[passo]
                achado = pg.evaluate(exp)
                check(achado == esperado, f"enquadramento {passo}: {achado} ≠ {esperado} (assunto fora do quadro no último quadro)")
```

e, antes do `for`, permitir `escala` no `--cenas`: em `main()`, `check(set(passos) <= set(PORTADAS), …)` vira `check(set(passos) <= set(PORTADAS) | set(ENQUADRAMENTOS), …)` e `validos = [p for p in passos if p in PORTADAS or p in ENQUADRAMENTOS]`; dentro do laço de `checar_cenas_portadas`, a leitura de `LEITURAS[passo]` passa a `if passo in LEITURAS:`. Sem `--cenas` (lista vazia), `passos_de("--cenas") or list(PORTADAS)` vira `passos_de("--cenas") or sorted(set(PORTADAS) | set(ENQUADRAMENTOS))`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --cenas escala icamento 2>&1 | tail -4`
Expected: `FALHOU:` com `enquadramento escala: False ≠ True` e `enquadramento icamento` (ou `st.cavalo` indefinido — `TypeError` no evaluate conta como falha: se aparecer traceback, é o sinal esperado antes do Step 3).

- [ ] **Step 3: `film.html`**

`SC[7]` (restaurante): trocar
`st.cam=[[0,[7,8.5,13],[0,1.2,0]],[5,[1,10,14.5],[0,1,0]],[10,[-3,15.5,19.5],[0,.6,-3]]];`
por
`st.cam=[[0,[7,8.5,13],[0,1.2,0]],[5,[1,10,14.5],[0,1,0]],[10,[-2,18.5,23],[0,.4,-2.6]]];`

`SC[10]` (içamento, bloco portado): trocar `box(2.4,2.6,C+.4,ORANGE,XC+L/2+1.9,1.5,0,g);` por `st.cavalo=box(2.4,2.6,C+.4,ORANGE,XC+L/2+1.9,1.5,0,g);` e o `st.cam` por
`st.cam=[[0,[24,13,24],[6,3.5,0]],[3.3,[21,16,22],[5,6.5,0]],[6.6,[-4,17,26],[-3,6.5,0]],[10,[-19,12,24],[-2,3,0]]];`

`corrigir_filme.py`: em `CENA_ICAMENTO`, as mesmas duas trocas (a string tem de ficar idêntica ao bloco do `film.html`); e, depois de `TROCAS_RODADA_4`, acrescentar

```python
# Rodada 9: reenquadramento do restaurante (as 12 miniaturas inteiras no último quadro)
TROCAS_RODADA_9 = [
    ("st.cam=[[0,[7,8.5,13],[0,1.2,0]],[5,[1,10,14.5],[0,1,0]],[10,[-3,15.5,19.5],[0,.6,-3]]];",
     "st.cam=[[0,[7,8.5,13],[0,1.2,0]],[5,[1,10,14.5],[0,1,0]],[10,[-2,18.5,23],[0,.4,-2.6]]];"),
]
```

e em `main()`, depois do laço de `TROCAS_RODADA_4`:

```python
    for velho, novo in TROCAS_RODADA_9:
        assert s.count(velho) == 1, f"trecho da rodada 9 não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
```

- [ ] **Step 4: Ver passar o enquadramento; ajustar só `st.cam` se preciso**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --cenas escala icamento 2>&1 | tail -3`
Expected: `OK`. Se `enquadramento escala` falhar, afastar a última chave (`[-2,18.5,23]` → `[-2,20,25]`) e repetir; se `icamento` falhar, mover o alvo da última chave em x (`[-2,3,0]` → `[0,3,0]`). Nunca mexer nos tempos nem em `st.run`. Cada ajuste vai também para `corrigir_filme.py`.

- [ ] **Step 5: Re-render dos dois clipes**

Run: `cd /home/runner/workspace && python3 portfolio/filme/render_clipes.py --so escala && python3 portfolio/filme/render_clipes.py --so icamento && python3 portfolio/tests/check_filme.py --video escala icamento`
Expected: `escala: 204 quadros`, `escala: NNN KB (crf 28|29|30)` com NNN ≤ 921, idem `icamento: 192 quadros`, e `OK`.

- [ ] **Step 6: Olhar os pôsteres**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && magick portfolio/site/video/cena-escala.webp portfolio/site/video/cena-icamento.webp -resize 60% +append $S/reenquadrados.png
```
Abrir `reenquadrados.png`. Expected: `escala` com o restaurante e as 12 miniaturas inteiras, com margem no pé; `icamento` com o módulo no radier e o cavalo laranja inteiro à direita, não cortado.

- [ ] **Step 7: Suíte inteira e commit**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_historia.py`
Expected: `OK`, `OK` (a soma dos 11 continua ≤ 8 MB; `checar_reproducao` = reproduz).

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/filme/corrigir_filme.py portfolio/tests/check_filme.py portfolio/site/video/cena-escala.mp4 portfolio/site/video/cena-escala.webp portfolio/site/video/cena-icamento.mp4 portfolio/site/video/cena-icamento.webp && git commit -m "Filme: escala termina com as 12 miniaturas inteiras e icamento com o cavalo no quadro; enquadramento conferido por projeção no --cenas; clipes regerados

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 12: Docs da rodada 9

**Files:**
- Modify: `portfolio/revisao/CHANGELOG.md`, `ANDAMENTO.md`, `portfolio/README.md`, `portfolio/DESIGN.md`, `portfolio/tests/check_historia.py` (`checar_readme`)

- [ ] **Step 1: Teste que falha**

Em `checar_readme` (`check_historia.py`), acrescentar `"foco-alto"` e `"--barra"` à tupla de trechos exigidos do README.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -3`
Expected: `FALHOU:` com `README do portfólio sem 'foco-alto'`.

- [ ] **Step 3: Documentos**

`portfolio/README.md`, na seção "## Usar", depois da linha "Gerar os clipes de fundo…":

```
- Clipe com o assunto encostado no alto ou no pé do 16:9: classe `foco-alto` / `foco-baixo` na `figure.clipe` (recorte vertical em janelas mais largas que 16:9). O fundo do palco começa em `--barra` (altura da barra fixa, medida pelo `historia.js`).
```

`portfolio/DESIGN.md`, no fim da seção "## 2. Paleta de cores e papéis" (depois da linha dos clipes): `- **Palco**: começa abaixo da barra fixa (`--barra`, px, medida em tempo real); recorte vertical `68% 0%` (`foco-alto`), `68% 100%` (`foco-baixo`) ou `68% 50%`; em celular deitado a faixa vai à esquerda com `max-width:min(560px,58vw)`.`

`portfolio/revisao/CHANGELOG.md`, no fim:

```markdown

---

# Rodada 9 — ajustes depois dos prints e da revisão, 24/09/2026

- Prints dos 17 capítulos (celular e desktop, pelo endereço público): https://claude.ai/artifact/AfNihqpe9eP2TRuNPzzrPB. Plano: `docs/superpowers/plans/2026-09-24-historia-rodada-9-ajustes.md`.
- Página: o fundo do palco começa abaixo da barra fixa (`--barra`, medida pelo `historia.js` na carga e no `resize`); foco vertical por clipe (`foco-alto` em obra, casa, whatsapp e içamento; `foco-baixo` em escala); marco tipográfico à direita na tela larga; celular deitado com a faixa à esquerda e menor.
- `clipes.js`: despejo pelo navegador reconhecido pela conta dos `emptied` nossos (antes ou depois dos metadados); `progress` refaz o seek que chegou sem quadro; espera de até 1,5 s por um `seekable` completo antes de congelar; o quantizador nunca passa do último quadro (o `historia.js` deixou o `0,999`).
- Filme: `escala` termina com as 12 miniaturas inteiras e `icamento` com o cavalo no quadro (câmeras; clipes regerados; enquadramento conferido por projeção no `--cenas`). `render_clipes.py` espera `PRONTO` com prazo.
- `maquetes.js`: sai a cena morta do içamento. Testes: checagens que passavam sem provar foram amarradas (regra do vídeo ancorada, 404 pedido de verdade, precondições em `check`, caixas com largura), mensagens com o valor medido, `--origem` sem URL avisa, exceção de JS vira `FALHOU`.
```

`ANDAMENTO.md`, no fim:

```markdown

## Estado em 24/09/2026 — rodada 9 (ajustes dos prints e da revisão) CONCLUÍDA
- Branch `historia-rodada-9` integrado em `main`; plano `docs/superpowers/plans/2026-09-24-historia-rodada-9-ajustes.md` (12 tarefas); changelog rodada 9.
- Conferir tudo: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_filme.py --cenas && python3 portfolio/tests/check_site.py`.
- Próximo: o plano irmão `2026-09-24-historia-cenas-novas.md` (cinco cenas novas: mudança, galpões, precisão, método, convite); depois push, deploy, `--origem`, iPhone real.
```

- [ ] **Step 4: Ver passar e commit**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_filme.py && python3 portfolio/tests/check_site.py`
Expected: `OK`, `OK`, `OK`.

```bash
cd /home/runner/workspace && git add portfolio/README.md portfolio/DESIGN.md portfolio/revisao/CHANGELOG.md ANDAMENTO.md portfolio/tests/check_historia.py && git commit -m "Changelog da rodada 9: barra, focos, paisagem, clipes.js, reenquadramentos; README e DESIGN.md

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Self-review

- **Cobertura dos achados:** P-1 → Task 1; P-2 → Task 2; P-3 → Task 3; P-4 → Task 4; R-1/R-2 → Task 5; R-3 → Task 6; R-4 → Task 7; R-5 → Task 8; R-6 → Task 9; R-7 → Task 10; R-8 → Task 11; docs → Task 12. P-5 no plano irmão.
- **Nomes consistentes:** `--barra` (Tasks 1, 2, 4, 12); `FOCO`, `foco-alto`, `foco-baixo` (Tasks 2, 12); `esperados`, `recarregar`, `conferirRange`, `temRange`, `ESPERA_RANGE` (Tasks 5, 6); `ultimo`, `quadro(t, dur)` (Task 7); `PRONTO_COM_PRAZO` (Task 8); `pedidos404`, `VAZIO_CLIPES`, `VAZIO_CLIPE` (Task 9); `st.cavalo`, `ENQUADRAMENTOS`, `TROCAS_RODADA_9` (Task 11).
- **Review Focus:** 1 → Task 2 Step 4; 2 → Task 1 Step 4; 3 → Task 5 Step 1; 4 → Task 6 (bloco sem Range já existente); 5 → Task 4 Step 1.
- **Ordem importa:** Task 5 antes da 6 (a 6 reescreve o `loadedmetadata` da 5); Task 7 depois da 5 (a linha das variáveis por figura). Task 11 depois da 2 (o foco de `escala` e a câmera nova se somam; o teste 21:9 da Task 2 lê só o CSS).
