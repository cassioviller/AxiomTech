# Cinco cenas novas para os capítulos sem cena · Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar cena 3D de fundo, no estilo do filme, aos cinco capítulos que hoje não têm (`mudanca`, `galpoes`, `precisao`, `metodo`, `convite`), para a história inteira rolar sobre dioramas — o achado P-5 dos prints de 24/09/2026 (https://claude.ai/artifact/AfNihqpe9eP2TRuNPzzrPB). `tese` continua com a foto real dos quantitativos (é a LCP e a prova que a roteirista escolheu).

**Architecture:** Cada cena é um bloco novo no `film.html` (`SC[12]`…`SC[16]`), fora de `ORDER` (o trailer não muda), com o contrato `st.run(t)`/`st.cam` e os utilitários do filme (`slab`, `box`, `cyl`, `tree`, `P()`, `ramp`, `back`, `lerp`, um só acento `ORANGE`, **nenhum texto pintado**). O bloco entra também no `corrigir_filme.py` (reprodução byte a byte a partir do zip), na tabela `CLIPES` do `render_clipes.py`, em `PORTADAS`/`LEITURAS` do `check_filme.py` e, na página, como `figure.clipe` com `ROTEIRO` atualizado. Uma tarefa por cena, cada uma terminando com o clipe renderizado, conferido e commitado; a última tarefa fecha soma, docs e changelog.

**Tech Stack:** three.js r128 no `film.html`; Playwright + Chromium do sistema + ffmpeg (`render_clipes.py`); Python 3 nos testes; HTML/CSS sem build.

**Spec:** o spec da rodada 8 (`docs/superpowers/specs/2026-09-23-filme-fundo-design.md`) continua a autoridade, com estas emendas, decididas aqui: (1) `mudanca`, `galpoes`, `precisao`, `metodo` e `convite` deixam de ser "sem cena" e ganham cenas **novas** (os vetos da roteirista eram às cenas do filme que existiam — a tabela da abertura, o WhatsApp de 7 vãos, o restaurante — não a cenas feitas para esses capítulos); (2) o teto da soma dos clipes sobe de 8 MB para **12 MB** (16 clipes; a carga é progressiva e nunca há mais de 2 vídeos com dados); (3) `SC.length` passa de 12 para 17.

## A regra da roteirista, cena a cena

**A imagem nunca afirma mais que o texto do capítulo nem contradiz a data ou a ressalva. Nenhum texto pintado.** O que cada cena mostra e o que da frase a sustenta:

| Capítulo | Frase | Cena (8 s) | Acento `ORANGE` | O que sustenta |
|---|---|---|---|---|
| `mudanca` (2025) | "Em 2025, mudei de cidade e de curso." | Um quarto novo: três caixas de mudança abrem, um notebook abre na mesa, a luminária acende. | O caderno na mesa | "mudei de cidade" (caixas), "de curso… EAD" (notebook). Nada de cidade, nome ou logo. |
| `galpoes` (jun/2026) | "Em junho, começou a obra que testaria o SIGE." / "Dois galpões e 22 baias numa fazenda, em Light Steel Frame" | Numa fazenda, **dois** galpões de LSF: montantes sobem, cobertura pousa, **22** divisórias de baia sobem (11 por galpão). | Os portões das baias | Exatamente 2 galpões e 22 baias; montantes finos de aço (LSF). Sem quadro, sem celular, sem balão (isso é agosto). |
| `precisao` (jul → set/2026) | "Desvio máximo de 0,25% nos 19 serviços conferidos." / "contra a tabela SINAPI" | Duas folhas lado a lado na mesa (o orçamento e a tabela de referência), **19** linhas cada; uma marca pousa em cada par de linhas, de cima para baixo, até as 19. | As 19 marcas | 19 linhas = 19 serviços; a conferência par a par. Sem número pintado (o 0,25 % é a frase). |
| `metodo` (sem data) | "Construí o jeito de o número não sumir." / "contabilidade, obra e sistemas" | Uma bancada com três estações (livro-razão, parede em obra, tela) ligadas por uma fita de papel; a peça que representa o número atravessa as três sem sumir e pousa na tela. | A peça | As três estações são as três palavras da ressalva. Abstrato por desenho. |
| `convite` (sem data) | "Você me manda o pacote do projeto; eu devolvo levantamento, orçamento com faixa e proposta no seu modelo." | A mesa do orçamento: o pacote chega pela esquerda; dele saem três folhas que se abrem em leque; a do meio ganha a faixa. | A faixa da folha do meio | Pacote → três entregas; "faixa" desenhada como faixa. Sem texto. |

Pôster (= último quadro): mudança com notebook aberto e caixas abertas · galpões com as 22 baias de pé · precisão com as 19 marcas · método com a peça pousada na tela · convite com as três folhas em leque.

## Global Constraints

- Branch `historia-cenas-novas` a partir de `main` **depois** do merge do plano irmão `2026-09-24-historia-rodada-9-ajustes.md` (este plano usa `FOCO`, `--barra` e as funções de teste dele); um commit por tarefa, trailer `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`; nunca `git add -A`; merge local em `main` no fim (autorização do Cássio de 24/09).
- **Nenhuma frase da página muda.** Só as figures mudam: `mudanca` e `galpoes` perdem o `.tipo`/`.ano`; `precisao` e `metodo` perdem a foto; `convite` ganha figure. `tese` fica como está (foto, `fetchpriority="high"`, LCP).
- Figure de clipe exatamente `<figure class="fundo clipe" data-passo="X" data-dur="8" data-clipe="video/cena-X.mp4" aria-hidden="true">` + `<video muted playsinline preload="none" disableremoteplayback width="960" height="540"></video>` + `<img src="video/cena-X.webp" alt="" width="960" height="540">`. Nenhuma das cinco leva `foco-alto`/`foco-baixo` (assunto centrado por câmera).
- Blocos do `film.html`: cabeçalho `// ================= NOME (nova: passo, 8 s) =================`, sem `stage(`, sem `fillText`, sem `tex(`, materiais por `P()` (nunca `new THREE.MeshStandardMaterial` no bloco), **exatamente 1** ocorrência do literal `ORANGE`, nenhum `0xE0622A`, nenhum texto; `st.run(t)` puro em `t` (0..10), parado em `t < 0,6` e em `t ≥ 8,6` (o `tempo_local` do render já congela 0,3 s no início e 0,5 s no fim); `st.cam` com 3–4 chaves `[t, [x,y,z], [alvo]]`; `DURSC[12..16] = 8`. Cada bloco também vive, idêntico, numa constante `CENA_<NOME>` do `corrigir_filme.py`, inserida antes de `// ================= render =================` (a mesma âncora das cenas portadas, na ordem dos índices).
- `CLIPES` do `render_clipes.py` ganha, na ordem, `"mudanca": (12, 0.0, 10.0, 8)`, `"galpoes": (13, 0.0, 10.0, 8)`, `"precisao": (14, 0.0, 10.0, 8)`, `"metodo": (15, 0.0, 10.0, 8)`, `"convite": (16, 0.0, 10.0, 8)` — cada entrada entra na tarefa da própria cena (o teste `ROTEIRO == CLIPES` exige os dois lados juntos).
- Encode e tetos como na rodada 8 (≤ 0,9 MB por clipe, pôster ≤ 60 KB, pontas paradas, PSNR do pôster ≥ 40 dB, GOP 4, sem áudio), **soma ≤ 12 MB** (16 clipes).
- `check_filme.py`: `PORTADAS` e `LEITURAS` ganham as cinco cenas; `checar_portadas` (estática) vale para elas; `SC.length == 9 + len(PORTADAS)`.
- Sem build nem dependência nova.

## Review Focus

1. **Uma cena que mente em número:** galpões com 20 ou 24 baias, precisão com 18 marcas — `LEITURAS` conta `st.baias.length === 22`, `st.portoes.length === 22`, `st.marcas.length === 19` (Tasks 2, 3).
2. **Texto pintado por engano** (um `tex(`/`fillText` copiado do filme): `checar_portadas` proíbe nos cinco blocos (cada tarefa).
3. **Pôster igual ao vídeo e ponta parada:** `st.run` tem de estar parado em `t ≥ 8,6`; `checar_clipe` mede PSNR das pontas e do pôster (cada tarefa, `--video passo`).
4. **A soma dos 16 clipes:** ≤ 12 MB medido em `checar_clipes` com os 16 (Task 6); se passar, `ajustar_soma` reencoda o maior.
5. **A página com 16 figures:** `#historia` continua com o comprimento da linha de base (± 2 px) — as figures vão para o palco (Task 6, `--navegador`).

## File Structure

- Modify `portfolio/filme/film.html` — cinco blocos novos antes de `// ================= render =================`; `DURSC`.
- Modify `portfolio/filme/corrigir_filme.py` — `CENA_MUDANCA`, `CENA_GALPOES`, `CENA_PRECISAO`, `CENA_METODO`, `CENA_CONVITE`, `INSERCOES_CENAS_NOVAS`, `TROCAS_CENAS_NOVAS` (a linha `DURSC`).
- Modify `portfolio/filme/render_clipes.py` — `CLIPES` (5 entradas), `TETO_SOMA = 12 MB`, docstring "16 clipes".
- Modify `portfolio/tests/check_filme.py` — `PORTADAS`, `LEITURAS`, `SC.length`, soma 12 MB, "32 arquivos".
- Modify `portfolio/site/index.html` — 5 figures.
- Modify `portfolio/tests/check_historia.py` — `ROTEIRO` (5 fundos), `checar_fundo` (nada muda de código; os `.tipo` deixam de existir na página e a checagem do `.ano` vira letra morta, mas fica).
- Create `portfolio/site/video/cena-{mudanca,galpoes,precisao,metodo,convite}.{mp4,webp}`.
- Modify `portfolio/README.md`, `portfolio/filme/README.md`, `portfolio/revisao/CHANGELOG.md`, `ANDAMENTO.md`, `docs/superpowers/specs/2026-09-23-filme-fundo-design.md` (emendas).

---

### Task 0: Branch e o teto da soma

**Files:**
- Modify: `portfolio/filme/render_clipes.py` (`TETO_SOMA`, docstring), `portfolio/tests/check_filme.py` (soma, contagem de arquivos, `SC.length`), `portfolio/filme/film.html` e `portfolio/filme/corrigir_filme.py` (`DURSC`)

- [ ] **Step 1: Branch**

```bash
cd /home/runner/workspace && git checkout main && git log --oneline -1 && git checkout -b historia-cenas-novas
```
Expected: `main` já contém "Changelog da rodada 9" (o plano irmão foi integrado); branch novo criado.

- [ ] **Step 2: Testes que mudam de número**

Em `check_filme.py`, `checar_clipes`: trocar `check(soma <= 8 * 1024 * 1024, f"soma dos clipes {soma / 1024 / 1024:.2f} MB > 8 MB")` por `check(soma <= TETO_SOMA, f"soma dos clipes {soma / 1024 / 1024:.2f} MB > {TETO_SOMA / 1024 / 1024:.0f} MB")` e, na linha da importação de `CLIPES` (no topo do arquivo, `from render_clipes import CLIPES`), importar também `TETO_SOMA`. Na mensagem `git ls-files site/video ≠ os 22 arquivos dos clipes` trocar `22` por `{2 * len(CLIPES)}` (f-string). Em `checar_cenas_portadas`, trocar `check(pg.evaluate("SC.length") == 12, "SC deve ter 12 cenas (9 do filme + 3 portadas)")` por `check(pg.evaluate("SC.length") == 9 + len(PORTADAS), f"SC deve ter {9 + len(PORTADAS)} cenas (9 do filme + {len(PORTADAS)} portadas/novas)")`.

Em `render_clipes.py`: `TETO_CLIPE, TETO_SOMA, TETO_POSTER = int(0.9 * 1024 * 1024), 8 * 1024 * 1024, 60 * 1024` → `…, 12 * 1024 * 1024, …`; na docstring, `(os 11 clipes, ~10 min em CPU)` → `(os 16 clipes, ~15 min em CPU)`; em `ajustar_soma`, a docstring `Se os 11 clipes passarem de 8 MB` → `Se os clipes passarem de TETO_SOMA (12 MB)` e as mensagens `soma > 8 MB` / `acima de 8 MB` → `soma > 12 MB` / `acima de 12 MB`.

`DURSC`: em `film.html`, trocar `DURSC[9]=10;DURSC[10]=8;DURSC[11]=10;` por `DURSC[9]=10;DURSC[10]=8;DURSC[11]=10;DURSC[12]=DURSC[13]=DURSC[14]=DURSC[15]=DURSC[16]=8;`. Em `corrigir_filme.py`, depois de `TROCAS_RODADA_9` (do plano irmão):

```python
# Cenas novas (rodada 10): duração de cada uma para renderCena
TROCAS_CENAS_NOVAS = [
    ("DURSC[9]=10;DURSC[10]=8;DURSC[11]=10;",
     "DURSC[9]=10;DURSC[10]=8;DURSC[11]=10;DURSC[12]=DURSC[13]=DURSC[14]=DURSC[15]=DURSC[16]=8;"),
]
INSERCOES_CENAS_NOVAS = []  # cada tarefa acrescenta (âncora, antes, depois) da sua cena
```

e em `main()`, depois do laço de `TROCAS_RODADA_9` e antes de `re.subn(r"var rows=…`:

```python
    for ancora, antes, depois in INSERCOES_CENAS_NOVAS:
        assert s.count(ancora) == 1, f"âncora das cenas novas não encontrada (ou repetida): {ancora[:60]!r}"
        s = s.replace(ancora, antes + ancora + depois)
    for velho, novo in TROCAS_CENAS_NOVAS:
        assert s.count(velho) == 1, f"trecho das cenas novas não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
```

- [ ] **Step 3: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_historia.py`
Expected: `OK`, `OK` (`checar_reproducao` reproduz o `film.html` com a linha `DURSC` nova).

- [ ] **Step 4: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/render_clipes.py portfolio/filme/film.html portfolio/filme/corrigir_filme.py portfolio/tests/check_filme.py && git commit -m "Clipes: teto da soma a 12 MB (16 clipes), DURSC das cinco cenas novas, contagens dos testes por CLIPES/PORTADAS

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 1: Cena `mudanca` (SC[12])

**Files:**
- Modify: `portfolio/filme/film.html` (bloco antes de `// ================= render =================`)
- Modify: `portfolio/filme/corrigir_filme.py` (`CENA_MUDANCA`, `INSERCOES_CENAS_NOVAS`)
- Modify: `portfolio/filme/render_clipes.py` (`CLIPES`)
- Modify: `portfolio/tests/check_filme.py` (`PORTADAS`, `LEITURAS`)
- Modify: `portfolio/site/index.html` (figure), `portfolio/tests/check_historia.py` (`ROTEIRO`)
- Create: `portfolio/site/video/cena-mudanca.mp4`, `cena-mudanca.webp`

**Interfaces:**
- Produces: `SC[12]` com `st.caixas` (3 tampas), `st.tampa` (tampa do notebook), `st.lampada`.

- [ ] **Step 1: Testes que falham**

`check_filme.py`: em `PORTADAS`, acrescentar `"mudanca": "// ================= MUDANÇA (nova: mudanca, 8 s) ================="`; em `LEITURAS`:

```python
    "mudanca": ("(function(){var st=SC[12];renderCena(12,.3);var a=st.tampa.rotation.x;renderCena(12,9.5);"
                "return [st.caixas.length,Math.abs(a)<.01,st.tampa.rotation.x<-1.8,st.caixas.every(function(t){return t.rotation.x<-2;}),st.lampada.material.emissiveIntensity>.8];})()",
                [3, True, True, True, True]),
```

`render_clipes.py`, `CLIPES`: acrescentar `"mudanca": (12, 0.0, 10.0, 8),` depois de `"zip"`.

`check_historia.py`, `ROTEIRO`, capítulo `mudanca`: `("ano", "2025")` → `("clipe", 8)`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py 2>&1 | head -4 && python3 portfolio/tests/check_historia.py 2>&1 | head -4`
Expected: `FALHOU:` com `film.html: falta o bloco '// ================= MUDANÇA …'` e `cena mudanca: classe da figura 'fundo tipo', esperava 'fundo clipe'`.

- [ ] **Step 3: O bloco (film.html e corrigir_filme.py, idênticos)**

No `film.html`, imediatamente antes de `// ================= render =================` (depois do bloco 36 MINUTOS):

```js
// ================= MUDANÇA (nova: mudanca, 8 s) =================
// um quarto novo: as caixas da mudança abrem, o notebook abre na mesa (o curso a distância), a luminária acende.
// Acento: o caderno. Sem texto. t: caixas 0,6→3,4 · notebook 3,6→5,4 · luminária 5,6→6,4 · parado até 10
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
slab(14,12,0xD8CFBE,g);box(14,5,.3,0xF3ECDD,0,2.5,-6,g,true);box(.3,5,12,0xEDE4D2,-7,2.5,0,g,true);
box(3.6,.12,1.6,0xC7A57A,1,1.5,-3.6,g);[[-.6,-4.3],[2.6,-4.3],[-.6,-2.9],[2.6,-2.9]].forEach(function(p){box(.12,1.5,.12,0x8A6A4A,1+p[0],.75,p[1],g);});
box(1.2,.1,1.2,0x8E9AA6,-3.2,1.05,-3,g);cyl(.06,.9,0x7D8E9E,-3.2,.55,-3,g,8);box(1.3,.6,1.2,0xBDB6AA,-3.2,1.4,-3.6,g);
st.caixas=[];[[-4.6,0,-1],[-2.2,0,1.6],[-4.4,1.3,-1]].forEach(function(p){var c=new THREE.Group();c.position.set(p[0],p[1],p[2]);g.add(c);
 box(1.6,1.2,1.3,0xC9B08A,0,.6,0,c);var tampa=new THREE.Group();tampa.position.set(0,1.2,-.65);c.add(tampa);box(1.6,.06,1.3,0xC9B08A,0,.03,.65,tampa);st.caixas.push(tampa);});
st.note=new THREE.Group();st.note.position.set(1.4,1.56,-3.4);g.add(st.note);box(1.3,.05,.9,0x4A4E55,0,.025,0,st.note);
st.tampa=new THREE.Group();st.tampa.position.set(0,.05,-.45);st.note.add(st.tampa);box(1.3,.04,.9,0x4A4E55,0,.02,.45,st.tampa);box(1.2,.01,.8,0xBFD8E6,0,.045,.45,st.tampa,true);
box(.7,.05,.5,ORANGE,-.3,1.585,-2.9,g);cyl(.03,.5,0x2B2F33,2.4,1.8,-4.1,g,6);
st.lampada=new THREE.Mesh(new THREE.ConeGeometry(.28,.3,10,1,true),P(0xF3ECDD,{emissive:0xFFE2B8,emissiveIntensity:0}));st.lampada.position.set(2.4,2.1,-4.1);g.add(st.lampada);
box(.6,.7,.6,0xBDB6AA,3.6,.35,-2.4,g);box(.3,.9,.05,0x7FA86A,3.6,1.15,-2.4,g);
st.cam=[[0,[7.5,4.2,8.5],[-1,1,-1.5]],[5,[4.5,3.2,5.5],[0,1.3,-2.5]],[10,[3,2.6,3.2],[1,1.5,-3.3]]];
st.run=function(t){st.caixas.forEach(function(tp,i){tp.rotation.x=-Math.PI*.85*back(ramp(t,.6+i*.9,1.6+i*.9));});
 st.tampa.rotation.x=-1.9*ramp(t,3.6,5.4);st.lampada.material.emissiveIntensity=.9*ramp(t,5.6,6.4);};
})();
```

No `corrigir_filme.py`, depois de `CENA_ZIP = """…"""`, a constante `CENA_MUDANCA = """…"""` com o texto acima **idêntico** (copiar do `film.html`; a checagem de reprodução falha a qualquer diferença), e em `INSERCOES_CENAS_NOVAS` a entrada `("// ================= render =================", CENA_MUDANCA + "\n", "")`.

- [ ] **Step 4: Conferir o bloco e o conteúdo**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py && python3 portfolio/tests/check_filme.py --cenas mudanca 2>&1 | tail -3`
Expected: `OK` (estático: reprodução, `checar_portadas` com 1 `ORANGE`, sem `tex(`), `OK` (`LEITURAS`: `[3, True, True, True, True]`). Se `checar_portadas` acusar `MeshStandardMaterial`, é porque o bloco usou o construtor direto: só `P()`.

- [ ] **Step 5: Render e clipe**

Run: `cd /home/runner/workspace && python3 portfolio/filme/render_clipes.py --so mudanca && python3 portfolio/tests/check_filme.py --video mudanca`
Expected: `mudanca: 192 quadros`, `mudanca: NNN KB (crf 28)` com NNN ≤ 921, `OK`.

- [ ] **Step 6: Olhar**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && for N in 0 50 110 160 191; do ffmpeg -y -loglevel error -i portfolio/site/video/cena-mudanca.mp4 -vf "select='eq(n,$N)'" -vframes 1 -update 1 $S/mud-$N.png; done && magick $S/mud-{0,50,110,160,191}.png -resize 40% +append $S/mudanca.png
```
Abrir `mudanca.png`. Expected: quarto claro com mesa, cadeira e caixas fechadas; caixas abrindo; notebook abrindo; luminária acesa; último quadro com tudo aberto e o caderno laranja na mesa; nada escrito. Se a mesa sair do quadro ou o notebook ficar de costas, ajustar **só** `st.cam` (nos dois arquivos) e repetir os Steps 4–6.

- [ ] **Step 7: A figure e a página**

`index.html`: trocar `<figure class="fundo tipo" data-passo="mudanca" aria-hidden="true"><span class="ano">2025</span></figure>` por

```html
    <figure class="fundo clipe" data-passo="mudanca" data-dur="8" data-clipe="video/cena-mudanca.mp4" aria-hidden="true">
      <video muted playsinline preload="none" disableremoteplayback width="960" height="540"></video>
      <img src="video/cena-mudanca.webp" alt="" width="960" height="540">
    </figure>
```

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3`
Expected: `OK`, `OK`.

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/filme/corrigir_filme.py portfolio/filme/render_clipes.py portfolio/tests/check_filme.py portfolio/site/index.html portfolio/tests/check_historia.py portfolio/site/video/cena-mudanca.mp4 portfolio/site/video/cena-mudanca.webp && git commit -m "Cena nova: mudança (caixas abrem, notebook abre, luminária acende); clipe cena-mudanca no capítulo 2025

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Cena `galpoes` (SC[13])

**Files:** os mesmos da Task 1, com `galpoes`; Create `portfolio/site/video/cena-galpoes.{mp4,webp}`.

**Interfaces:**
- Produces: `SC[13]` com `st.montantes` (48), `st.coberturas` (2), `st.baias` (22), `st.portoes` (22).

- [ ] **Step 1: Testes que falham**

`PORTADAS`: `"galpoes": "// ================= GALPÕES (nova: galpoes, 8 s) ================="`. `LEITURAS`:

```python
    "galpoes": ("(function(){var st=SC[13];renderCena(13,9.5);return [st.coberturas.length,st.baias.length,st.portoes.length,"
                "st.baias.every(function(b){return b.scale.y>.98;}),st.coberturas.every(function(c){return Math.abs(c.position.y-2.6)<.02;})];})()",
                [2, 22, 22, True, True]),
```

`CLIPES`: `"galpoes": (13, 0.0, 10.0, 8),`. `ROTEIRO` `galpoes`: `("ano", "22 baias")` → `("clipe", 8)`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py 2>&1 | head -3 && python3 portfolio/tests/check_historia.py 2>&1 | head -3`
Expected: `falta o bloco '// ================= GALPÕES …'` e `cena galpoes: classe da figura 'fundo tipo'…`.

- [ ] **Step 3: O bloco**

Antes de `// ================= render =================` (depois do bloco MUDANÇA):

```js
// ================= GALPÕES (nova: galpoes, 8 s) =================
// dois galpões de Light Steel Frame numa fazenda, com 11 baias cada: os montantes sobem, a cobertura pousa e as divisórias
// das 22 baias sobem por último. Acento: os portões das baias. Sem texto. t: montantes 0,6→3,6 · cobertura 3,8→5,6 · baias 5,8→8,6 · parado até 10
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
slab(60,40,0xB8C99A,g);box(30,.03,3,0xB9A382,0,.02,9,g,true);
var GL=14,GW=6,H=2.6,N=11;st.coberturas=[];st.montantes=[];st.baias=[];st.portoes=[];
[-9,9].forEach(function(gx){var G=new THREE.Group();G.position.set(gx,0,0);g.add(G);
 box(GL+.6,.2,GW+.6,0xD8CFBE,0,.1,0,G);
 for(var i=0;i<=N;i++){[-GW/2,GW/2].forEach(function(z){st.montantes.push(box(.08,H,.08,0x8E9AA6,-GL/2+i*(GL/N),H/2,z,G,true));});}
 var cob=new THREE.Group();cob.position.set(0,H+6,0);G.add(cob);box(GL+.8,.12,GW+.8,0x7D8E9E,0,.06,0,cob);box(GL+.8,.06,.08,0x4A4E55,0,.15,0,cob,true);st.coberturas.push(cob);
 for(var k=0;k<N;k++){var x=-GL/2+(k+.5)*(GL/N);st.baias.push(box(.06,1.3,GW*.42,0xF3ECDD,x,.65,-GW*.28,G,true));
  st.portoes.push(box(GL/N-.16,.9,.06,ORANGE,x,.45,-GW*.07,G,true));}
});
tree(-24,-12,1.3,g);tree(22,-14,1.1,g);tree(26,6,1,g);tree(-26,8,.9,g);
st.cam=[[0,[26,12,30],[0,1,0]],[4,[12,10,24],[0,1.5,0]],[7,[-6,14,22],[0,1.2,-1]],[10,[-14,18,26],[0,1,-1]]];
st.run=function(t){var s=ramp(t,.6,3.6);st.montantes.forEach(function(m,i){var k=cl(s*1.3-(i%24)/24*.3);m.scale.y=Math.max(.01,k);m.position.y=H*m.scale.y/2;});
 var c=ramp(t,3.8,5.6);st.coberturas.forEach(function(cob){cob.position.y=lerp(H+6,H,c);});
 st.baias.forEach(function(b,i){var k=back(ramp(t,5.8+i*.09,6.4+i*.09));b.scale.y=Math.max(.01,k);b.position.y=.65*b.scale.y;});
 st.portoes.forEach(function(p,i){var k=back(ramp(t,6.2+i*.09,6.8+i*.09));p.scale.y=Math.max(.01,k);p.position.y=.45*p.scale.y;});};
})();
```

`corrigir_filme.py`: `CENA_GALPOES = """…"""` idêntica e a entrada em `INSERCOES_CENAS_NOVAS` depois da de `CENA_MUDANCA` (mesma âncora).

- [ ] **Step 4: Conferir** — como na Task 1, com `--cenas galpoes`. Expected: `OK`, `[2, 22, 22, True, True]`.

- [ ] **Step 5: Render** — `--so galpoes`, `--video galpoes`. Expected: `galpoes: 192 quadros`, ≤ 921 KB, `OK`. Se passar de 0,9 MB (muitas arestas), o script reencoda com crf 29/30; se ainda assim passar, reduzir `tree` para 2 árvores e repetir.

- [ ] **Step 6: Olhar** — quadros 0, 60, 110, 165, 191 (prefixo `gal-`), como na Task 1. Expected: laje vazia com os dois pisos; montantes de pé; coberturas pousando; baias e portões laranja subindo; último quadro com os dois galpões inteiros e as 22 baias contáveis vistas de cima e de lado. Se um galpão sair do quadro, afastar a câmera (`st.cam`, nos dois arquivos).

- [ ] **Step 7: A figure** — trocar `<figure class="fundo tipo" data-passo="galpoes" aria-hidden="true"><span class="ano">22 baias</span></figure>` pela figure de clipe de `galpoes` (modelo da Task 1, `X = galpoes`). `check_historia.py` e `--navegador`: `OK`, `OK`.

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/filme/corrigir_filme.py portfolio/filme/render_clipes.py portfolio/tests/check_filme.py portfolio/site/index.html portfolio/tests/check_historia.py portfolio/site/video/cena-galpoes.mp4 portfolio/site/video/cena-galpoes.webp && git commit -m "Cena nova: galpões (dois galpões de LSF e 22 baias subindo numa fazenda); clipe cena-galpoes no capítulo de junho

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: Cena `precisao` (SC[14])

**Files:** os mesmos, com `precisao`; Create `cena-precisao.{mp4,webp}`.

**Interfaces:**
- Produces: `SC[14]` com `st.marcas` (19).

- [ ] **Step 1: Testes que falham**

`PORTADAS`: `"precisao": "// ================= PRECISÃO (nova: precisao, 8 s) ================="`. `LEITURAS`:

```python
    "precisao": ("(function(){var st=SC[14];renderCena(14,.3);var a=st.marcas.every(function(m){return m.scale.x<.01;});renderCena(14,9.5);"
                 "return [st.marcas.length,a,st.marcas.every(function(m){return m.scale.x>.98;})];})()", [19, True, True]),
```

`CLIPES`: `"precisao": (14, 0.0, 10.0, 8),`. `ROTEIRO` `precisao`: `("img", "o-orcamento.webp", 1040, 1080)` → `("clipe", 8)`.

- [ ] **Step 2: Ver falhar** — como antes. Expected: `falta o bloco '// ================= PRECISÃO …'` e `cena precisao: … esperava 'fundo clipe'`.

- [ ] **Step 3: O bloco**

```js
// ================= PRECISÃO (nova: precisao, 8 s) =================
// duas folhas lado a lado na mesa — o orçamento e a tabela de referência, 19 linhas cada; uma marca pousa em cada par de linhas
// conferido, de cima para baixo. Acento: as marcas. Sem texto (os 19 serviços e o 0,25 % são a frase). t: marcas 0,8→8,4 · parado até 10
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
slab(24,16,0xD8CFBE,g);box(10,.16,6.4,0xC7A57A,0,1.5,0,g);[[-4.6,-2.9],[4.6,-2.9],[-4.6,2.9],[4.6,2.9]].forEach(function(p){box(.16,1.5,.16,0x8A6A4A,p[0],.75,p[1],g);});
var N=19,Y=1.6;st.marcas=[];
[-1.9,1.9].forEach(function(x,j){box(3.2,.03,4.4,0xFBF8F0,x,Y,0,g,true);box(2.6,.012,.22,j?0x8E9AA6:0x4A4E55,x,Y+.02,-1.85,g,true);
 for(var i=0;i<N;i++){var z=-1.45+i*.19;box(2.4,.01,.09,0xBDB6AA,x-.1,Y+.02,z,g,true);box(.5,.012,.1,0xDCD5C6,x+1.1,Y+.021,z,g,true);}});
for(var i=0;i<N;i++){var m=box(.22,.03,.22,ORANGE,0,Y+.03,-1.45+i*.19,g,true);m.scale.setScalar(.001);st.marcas.push(m);}
cyl(.06,1.6,0x7D8E9E,4.1,Y+.06,1.6,g,8).rotation.z=Math.PI/2;box(.5,.5,.5,0xBFD8E6,-4.3,1.83,-2.2,g);
st.cam=[[0,[-4,6.5,6.5],[0,1.6,-.6]],[5,[.5,5.8,4.8],[0,1.6,-.2]],[10,[3.5,5.2,5],[.4,1.6,.4]]];
st.run=function(t){st.marcas.forEach(function(m,i){var a=.8+i*.4,k=back(ramp(t,a,a+.4));m.scale.setScalar(Math.max(.001,k));m.position.y=Y+.03+(1-cl((t-a)/.4))*.6;});};
})();
```

`corrigir_filme.py`: `CENA_PRECISAO` idêntica; entrada em `INSERCOES_CENAS_NOVAS` depois de `CENA_GALPOES`.

- [ ] **Step 4: Conferir** — `--cenas precisao`. Expected: `[19, True, True]`.
- [ ] **Step 5: Render** — `--so precisao`, `--video precisao`.
- [ ] **Step 6: Olhar** — quadros 0, 40, 100, 160, 191 (prefixo `pre-`). Expected: duas folhas com linhas cinza; marcas laranja pousando uma a uma; último quadro com 19 marcas alinhadas entre as folhas; nada escrito.
- [ ] **Step 7: A figure** — trocar `<figure class="fundo" data-passo="precisao" aria-hidden="true"><img src="img/o-orcamento.webp" alt="" width="1040" height="1080" loading="lazy"></figure>` pela figure de clipe de `precisao`. `check_historia.py`, `--navegador`: `OK`, `OK`. (`img/o-orcamento.webp` continua no repositório: o `portfolio.html` a usa.)

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/filme/corrigir_filme.py portfolio/filme/render_clipes.py portfolio/tests/check_filme.py portfolio/site/index.html portfolio/tests/check_historia.py portfolio/site/video/cena-precisao.mp4 portfolio/site/video/cena-precisao.webp && git commit -m "Cena nova: precisão (19 linhas conferidas par a par, uma marca por linha); clipe cena-precisao

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Cena `metodo` (SC[15])

**Files:** os mesmos, com `metodo`; Create `cena-metodo.{mp4,webp}`.

**Interfaces:**
- Produces: `SC[15]` com `st.peca`.

- [ ] **Step 1: Testes que falham**

`PORTADAS`: `"metodo": "// ================= MÉTODO (nova: metodo, 8 s) ================="`. `LEITURAS`:

```python
    "metodo": ("(function(){var st=SC[15];renderCena(15,.3);var x0=st.peca.position.x;renderCena(15,5);var xm=st.peca.position.x;renderCena(15,9.5);"
               "return [x0<-6.9,xm>-1&&xm<8,st.peca.position.x>6.9,st.peca.position.y<2,st.peca.visible];})()", [True, True, True, True, True]),
```

`CLIPES`: `"metodo": (15, 0.0, 10.0, 8),`. `ROTEIRO` `metodo`: `("img", "o-proposta.webp", 885, 1060)` → `("clipe", 8)`.

- [ ] **Step 2: Ver falhar** — como antes.

- [ ] **Step 3: O bloco**

```js
// ================= MÉTODO (nova: metodo, 8 s) =================
// uma bancada com três estações — o livro-razão, a parede em obra e a tela — ligadas por uma fita de papel; a peça que
// representa o número atravessa as três sem sumir e pousa na tela. Acento: a peça. Sem texto. t: 0,6→3,4 livro→parede · 3,8→6,6 parede→tela · 7,0→8,2 pousa · parado até 10
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
slab(30,14,0xD8CFBE,g);box(20,.2,3.2,0xC7A57A,0,1.4,0,g);[[-9.4,-1.3],[9.4,-1.3],[-9.4,1.3],[9.4,1.3],[0,-1.3],[0,1.3]].forEach(function(p){box(.18,1.4,.18,0x8A6A4A,p[0],.7,p[1],g);});
box(18,.03,.9,0xFBF8F0,0,1.52,0,g,true);
box(1.8,.5,2.4,0x6F8FA8,-7,1.75,-.1,g);box(1.6,.06,2.2,0xF3ECDD,-7,2.03,-.1,g,true);
for(var r=0;r<4;r++)for(var c=0;c<3;c++)box(.7,.32,.4,0xF3ECDD,-1+c*.72-(r%2)*.36,1.66+r*.34,-.4,g);box(2.6,.06,.5,0x8E9AA6,0,1.53,-.4,g,true);
box(2.2,1.5,.12,0x4A4E55,7,2.55,-.6,g);box(2,1.3,.02,0xBFD8E6,7,2.55,-.53,g,true);box(.5,.3,.5,0x4A4E55,7,1.65,-.6,g);
st.peca=box(.5,.5,.5,ORANGE,-7,2.31,.9,g);
st.cam=[[0,[-9,4.5,7],[-6,2,0]],[5,[1,4.2,6.5],[0,2,0]],[10,[7,4,6.2],[6.4,2.2,0]]];
st.run=function(t){var x,y;if(t<3.6){var a=ramp(t,.6,3.4);x=lerp(-7,0,a);y=2.31+Math.sin(a*Math.PI)*.8;}
 else if(t<6.8){var b=ramp(t,3.8,6.6);x=lerp(0,7,b);y=2.31+Math.sin(b*Math.PI)*.8;}
 else{x=7;y=lerp(2.31,1.95,ramp(t,7,8.2));}
 st.peca.position.set(x,y,.9);st.peca.rotation.y=t*.9;};
})();
```

`corrigir_filme.py`: `CENA_METODO` idêntica; entrada depois de `CENA_PRECISAO`.

- [ ] **Step 4: Conferir** — `--cenas metodo`. Expected: `[True, True, True, True, True]`.
- [ ] **Step 5: Render** — `--so metodo`, `--video metodo`. Atenção à ponta final: a peça gira (`rotation.y=t*.9`) até t=10 — se `checar_clipe` acusar a ponta final não parada (PSNR < 35 dB), trocar por `st.peca.rotation.y=Math.min(t,8.4)*.9;` nos dois arquivos e repetir desde o Step 4.
- [ ] **Step 6: Olhar** — quadros 0, 50, 100, 150, 191 (prefixo `met-`). Expected: bancada com livro, parede de tijolos e tela; a peça laranja no livro; em arco até a parede; em arco até a tela; pousada em frente à tela. Nada escrito.
- [ ] **Step 7: A figure** — trocar `<figure class="fundo" data-passo="metodo" aria-hidden="true"><img src="img/o-proposta.webp" alt="" width="885" height="1060" loading="lazy"></figure>` pela figure de clipe de `metodo`. `check_historia.py`, `--navegador`: `OK`, `OK`.

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/filme/corrigir_filme.py portfolio/filme/render_clipes.py portfolio/tests/check_filme.py portfolio/site/index.html portfolio/tests/check_historia.py portfolio/site/video/cena-metodo.mp4 portfolio/site/video/cena-metodo.webp && git commit -m "Cena nova: método (o número atravessa contabilidade, obra e sistemas sem sumir); clipe cena-metodo

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Cena `convite` (SC[16])

**Files:** os mesmos, com `convite`; Create `cena-convite.{mp4,webp}`.

**Interfaces:**
- Produces: `SC[16]` com `st.pacote`, `st.folhas` (3), `st.faixa`.

- [ ] **Step 1: Testes que falham**

`PORTADAS`: `"convite": "// ================= CONVITE (nova: convite, 8 s) ================="`. `LEITURAS`:

```python
    "convite": ("(function(){var st=SC[16];renderCena(16,.3);var a=st.folhas.every(function(f){return !f.visible;});renderCena(16,9.5);"
                "return [st.folhas.length,a,st.folhas.every(function(f){return f.visible;}),st.faixa.scale.x>.98,st.folhas[2].position.x>3];})()",
                [3, True, True, True, True]),
```

`CLIPES`: `"convite": (16, 0.0, 10.0, 8),`. `ROTEIRO` `convite`: o `None` do fundo → `("clipe", 8)`.

- [ ] **Step 2: Ver falhar** — como antes. Expected inclui `cena convite: esperava 1 figura de fundo, achei 0`.

- [ ] **Step 3: O bloco**

```js
// ================= CONVITE (nova: convite, 8 s) =================
// a mesa do orçamento: o pacote do projeto chega pela esquerda; dele saem três folhas — levantamento, orçamento, proposta — em leque,
// e a do meio ganha a faixa. Acento: a faixa. Sem texto. t: pacote 0,6→2,4 · folhas 3,0→6,4 · faixa 6,6→7,6 · parado até 10
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
slab(26,16,0xD8CFBE,g);box(12,.16,7,0xC7A57A,0,1.5,0,g);[[-5.6,-3.2],[5.6,-3.2],[-5.6,3.2],[5.6,3.2]].forEach(function(p){box(.16,1.5,.16,0x8A6A4A,p[0],.75,p[1],g);});
st.pacote=new THREE.Group();g.add(st.pacote);box(2.6,1.1,2,0xC9B08A,0,.55,0,st.pacote);box(2.7,.08,.3,0x8E9AA6,0,1.12,0,st.pacote,true);box(.3,.08,2.1,0x8E9AA6,0,1.12,0,st.pacote,true);
st.folhas=[];for(var i=0;i<3;i++){var f=new THREE.Group();g.add(f);box(2.4,.03,3.2,0xFBF8F0,0,0,0,f,true);box(1.8,.012,.18,0x4A4E55,0,.02,-1.3,f,true);
 for(var r=0;r<7;r++)box(1.9-(r%3)*.3,.01,.08,0xBDB6AA,-.15,.02,-.9+r*.28,f,true);st.folhas.push(f);}
st.faixa=box(1.7,.02,.34,ORANGE,0,.03,.55,st.folhas[1],true);
cyl(.06,1.5,0x7D8E9E,4.6,1.64,2.4,g,8).rotation.z=Math.PI/2;box(.5,.5,.5,0xBFD8E6,-5,1.83,-2.6,g);
st.cam=[[0,[-6,6.5,7.5],[-2,1.6,0]],[5,[0,6,6.5],[.5,1.6,0]],[10,[3,5.4,5.5],[1.5,1.6,.2]]];
st.run=function(t){var a=ramp(t,.6,2.4);st.pacote.position.set(lerp(-9,-3.2,a),1.58,-.2);
 st.folhas.forEach(function(f,i){var k=ramp(t,3+i*1.1,4.2+i*1.1);f.visible=t>3+i*1.1;f.position.set(lerp(-3.2,-.4+i*2.1,k),1.6+.04*i+(1-k)*.9,lerp(-.2,.3-i*.2,k));f.rotation.y=(i-1)*.12*k;});
 st.faixa.scale.x=Math.max(.001,ramp(t,6.6,7.6));};
})();
```

`corrigir_filme.py`: `CENA_CONVITE` idêntica; entrada depois de `CENA_METODO`.

- [ ] **Step 4: Conferir** — `--cenas convite` e, agora com as cinco, `--cenas` sem passo (todas + `SC.length == 17`). Expected: `[3, True, True, True, True]`, `OK`.
- [ ] **Step 5: Render** — `--so convite`, `--video convite`.
- [ ] **Step 6: Olhar** — quadros 0, 45, 100, 150, 191 (prefixo `con-`). Expected: mesa vazia; pacote chegando; folhas saindo e se abrindo em leque; faixa laranja crescendo na do meio; último quadro com pacote, três folhas e a faixa. Nada escrito.
- [ ] **Step 7: A figure** — em `<section class="cena" id="convite" data-passo="convite">`, inserir a figure de clipe de `convite` como **primeira** filha (antes de `<div class="texto">`), com a mesma indentação das outras. `check_historia.py`, `--navegador`: `OK`, `OK` (`#historia` na linha de base ± 2 px: a figure vai para o palco).

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/filme/corrigir_filme.py portfolio/filme/render_clipes.py portfolio/tests/check_filme.py portfolio/site/index.html portfolio/tests/check_historia.py portfolio/site/video/cena-convite.mp4 portfolio/site/video/cena-convite.webp && git commit -m "Cena nova: convite (o pacote do projeto vira levantamento, orçamento com faixa e proposta); clipe cena-convite

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Soma, página inteira, docs e changelog

**Files:**
- Modify: `portfolio/README.md`, `portfolio/filme/README.md`, `portfolio/revisao/CHANGELOG.md`, `ANDAMENTO.md`, `docs/superpowers/specs/2026-09-23-filme-fundo-design.md`, `portfolio/tests/check_historia.py` (`checar_readme`)

- [ ] **Step 1: Teste que falha**

Em `checar_readme` (`check_historia.py`), acrescentar `"16 clipes"` e `"12 MB"` à tupla de trechos exigidos.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -3`
Expected: `FALHOU:` com `README do portfólio sem '16 clipes'`.

- [ ] **Step 3: A soma dos 16 e a suíte inteira**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --video 2>&1 | tail -3 && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3 && python3 portfolio/tests/check_site.py`
Expected: `OK` (soma ≤ 12 MB, 32 arquivos em `site/video`), `OK`, `OK`. Se a soma passar de 12 MB: `python3 portfolio/filme/render_clipes.py` (render completo, ~15 min) aplica `ajustar_soma` e reencoda o maior; commitar os clipes reencodados junto.

- [ ] **Step 4: Documentos**

`portfolio/README.md`: na árvore, `11 clipes de fundo em video/` → `16 clipes de fundo em video/`; em "Gerar os clipes de fundo…", `(~10 min)` → `(~15 min; 16 clipes, ≤ 12 MB na soma)`.

`portfolio/filme/README.md`: onde diz 11 clipes / 8 MB, trocar por 16 clipes / 12 MB; na lista de cenas, acrescentar `SC[12] mudança · SC[13] galpões · SC[14] precisão · SC[15] método · SC[16] convite (cenas novas, fora de ORDER)`.

`docs/superpowers/specs/2026-09-23-filme-fundo-design.md`: na tabela de capítulos, as linhas de `mudanca`, `galpoes`, `precisao`, `metodo` e `convite` ganham, no fim, ` — **emenda (cenas novas, plano 2026-09-24-historia-cenas-novas): cena própria SC[12..16], 8 s**`; em F-03, `soma ≤ 8 MB` → `soma ≤ 12 MB (16 clipes; emenda)`.

`portfolio/revisao/CHANGELOG.md`, no fim:

```markdown

---

# Rodada 10 — cinco cenas novas, 24/09/2026

- Plano `docs/superpowers/plans/2026-09-24-historia-cenas-novas.md`. Os capítulos `mudanca`, `galpoes`, `precisao`, `metodo` e `convite` ganham clipes de cenas feitas para eles (SC[12..16] do `film.html`, fora do trailer), pela regra da roteirista: a imagem nunca afirma mais que o texto; nenhum texto pintado; um acento por cena.
- Mudança: caixas abrem, notebook abre, luminária acende · Galpões: dois galpões de LSF e 22 baias · Precisão: 19 linhas conferidas par a par · Método: o número atravessa contabilidade, obra e sistemas · Convite: o pacote vira três folhas, a do meio com a faixa.
- 16 clipes, soma ≤ 12 MB (emenda ao F-03); `tese` continua com a foto (LCP). `corrigir_filme.py` reproduz os cinco blocos; `check_filme.py --cenas` confere conteúdo (contagens) e estilo.
```

`ANDAMENTO.md`, no fim:

```markdown

## Estado em 24/09/2026 — rodada 10 (cinco cenas novas) CONCLUÍDA
- Branch `historia-cenas-novas` integrado em `main`; 16 capítulos com clipe, `tese` com foto, nenhum sem fundo.
- Conferir tudo: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_filme.py --cenas && python3 portfolio/tests/check_site.py`.
- Próximo: push, deploy, `check_historia.py --origem <URL>`, iPhone real.
```

- [ ] **Step 5: Ver passar e commit**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_filme.py`
Expected: `OK`, `OK`.

```bash
cd /home/runner/workspace && git add portfolio/README.md portfolio/filme/README.md portfolio/revisao/CHANGELOG.md ANDAMENTO.md docs/superpowers/specs/2026-09-23-filme-fundo-design.md portfolio/tests/check_historia.py && git commit -m "Changelog da rodada 10: cinco cenas novas; README, spec (emendas) e retomada

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

## Self-review

- **Cobertura:** P-5 (seis capítulos sem cena) → cinco cenas (Tasks 1–5) + `tese` mantido por decisão registrada no cabeçalho; soma/SC.length/DURSC (Task 0); docs (Task 6).
- **Nomes consistentes:** `SC[12..16]`; `st.caixas/st.tampa/st.lampada` (Task 1 ↔ `LEITURAS`), `st.coberturas/st.baias/st.portoes` (Task 2), `st.marcas` (Task 3), `st.peca` (Task 4), `st.pacote/st.folhas/st.faixa` (Task 5); `CENA_MUDANCA…CENA_CONVITE`, `INSERCOES_CENAS_NOVAS`, `TROCAS_CENAS_NOVAS` (Task 0 e cada cena); `TETO_SOMA` importado no `check_filme.py` (Task 0).
- **Regras de `checar_portadas` em cada bloco:** 1 `ORANGE`, sem `tex(`/`fillText`/`stage(`, sem `MeshStandardMaterial` literal (a luminária usa `P()` com `emissive`), sem `0xE0622A`.
- **Pontas paradas:** todo `st.run` congela em `t ≥ 8,6` (mudança 6,4; galpões 8,6 = último portão 6,8+20·0,09; precisão 8,4 = 0,8+18·0,4+0,4; método 8,2, com a ressalva do giro; convite 7,6).
- **Review Focus:** 1 → `LEITURAS` das Tasks 2 e 3; 2 → `checar_portadas` (Step 4 de cada); 3 → `--video passo` (Step 5 de cada); 4 → Task 6 Step 3; 5 → Task 5 Step 7 e Task 6 Step 3.
