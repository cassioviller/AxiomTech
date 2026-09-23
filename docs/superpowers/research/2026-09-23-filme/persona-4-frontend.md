# Persona 4 — Tiago (rodada 3)

*dev front-end de scrollytelling e three.js, sem build, celular primeiro*

Li `00-contexto.md`, `film.html` inteiro (347 linhas), `render.py`, `portfolio/site/maquetes.js`, `portfolio/site/historia.js` e `portfolio/tests/check_historia.py`. Conferi o `vendor/three.module.js` (r186: exporta `outputColorSpace`/`SRGBColorSpace`, não tem mais `sRGBEncoding`) e o `portfolio.html`, que **também** usa `maquetes.js` com duas figuras (`36min`, `casa-viaja`) fora de qualquer `.palco`, soltas no fluxo normal da página — achado que muda a arquitetura do Caminho B (ver abaixo).

## Caminho B: dioramas ao vivo com um renderizador

### O que já existe e eu quase perdi
`portfolio/site/maquetes.js` já tem **3 das 9 cenas do filme, portadas e refinadas**, cada uma com o seu próprio `<canvas>`/`WebGLRenderer` (não compartilhado):
- `cena36` ≈ CENA 6 "36 minutos" do filme (planta + relógio), mas lê a planta real (`img/upa-plan.webp`) em vez de canvas procedural — **melhor** que o filme.
- `cenaIcamento` ≈ CELEIRO "balancim" do filme (módulo, olhais, balancim, cabos) — praticamente o mesmo diorama, variáveis quase idênticas (`TOPO`, `AMARELO`/`E8A13C`, torus nos cantos).
- `cenaCasa` ≈ o conceito do CELEIRO/B-36 do filme, só que muito mais desenvolvido (telhado gambrel montado em cena, guindaste articulado, 3 viagens).

Ou seja: **3 dos 9 dioramas do filme já estão live e são melhores que a fonte**. Restam **6 dioramas novos** para portar: escritório 2017, duas construtoras, VEKS/parede LSF, 13 obras/restaurante, prédio SIGE, WhatsApp. Recomendo migrar primeiro os 3 que hoje são só um fundo tipográfico (maior ganho, zero risco de "diorama estilizado vs. captura de tela real"):

| Capítulo (`data-passo`) | Fundo hoje | Diorama do filme | Prioridade |
|---|---|---|---|
| `origem` | `fundo tipo` "2017" | CENA 1 · escritório | **MUST** round 3 |
| `obra` | `fundo tipo` "5×" | CENA 2 · duas construtoras | **MUST** round 3 |
| `ferramentas` | `fundo tipo` "3ª" | VEKS · parede LSF | **MUST** round 3 |
| `escala` | `img` s1.webp (print real) | 13 OBRAS · restaurante | SHOULD, decisão de produto (diorama estilizado substitui print real?) |
| `sige` | `img` c-aprovacao.webp (print real) | CENA 4 · prédio SIGE | SHOULD, mesma ressalva |
| `whatsapp` | `img` p-fotos.webp (print real) | CENA 3 · WhatsApp | SHOULD, mesma ressalva |
| `casa`, `icamento`, `zip` | já são maquetes | — | nada a fazer |

A ABERTURA (tabela de quantitativos) não precisa virar diorama: `tese` já tem `o-quantitativos.webp`, que cobre o mesmo conteúdo.

### Onde mora o canvas e como muda o `montar()`
Hoje cada `figure.maquete` cria seu próprio `THREE.WebGLRenderer` dentro de `stage()` (`portfolio/site/maquetes.js:22-43`). Em `index.html`, todas as `.fundo` (incluindo as `maquete`) já são movidas para dentro de um único `.palco` sticky por `historia.js` (`palco.appendChild(f)`, linha 36), mas **cada uma continua com seu próprio canvas/contexto** — hoje isso é seguro porque só existem 3; com 9, o risco (já levantado no `00-contexto.md`) é real: mobile Safari/Chrome limitam de ~8 a 16 contextos WebGL simultâneos, e cada figura tem sombra 2048×2048 (~16 MB de FBO cada).

Como só **uma** `.fundo.maquete` fica visível por vez em `index.html` (as outras ficam `hidden`, controlado por `ativar()`), a solução certa **para essa página** é a mais simples das duas técnicas documentadas pelo three.js: não é scissor (que serve para várias cenas visíveis *ao mesmo tempo*, com o efeito colateral de "descolar" da rolagem quando o render atrasa), é **um canvas único, trocando qual `Scene`/`camera` ele desenha por frame** — sem scissor, sem mover DOM.

Mudanças concretas:
1. **HTML**: `<div class="palco" aria-hidden="true"><canvas id="palco3d"></canvas></div>` — um único `<canvas>` fixo dentro do `.palco`, criado uma vez (estático no HTML ou criado por `maquetes.js` no primeiro uso). As 9 `<figure class="fundo maquete">` deixam de ter `<canvas></canvas>` próprio (isso muda o contrato hoje checado em `check_historia.py:207` — `check("<canvas></canvas>" in fmiolo, ...)` — precisa ser atualizado junto).
2. **`maquetes.js`**: separar o que `stage()` faz hoje em duas partes:
   - `motor()` — cria o `WebGLRenderer` **uma vez só**, ligado ao canvas do `.palco` (`outputColorSpace`, `toneMapping`, `shadowMap` configurados uma vez).
   - `cenaBase(sky,fogNear,fogFar)` — cria só `Scene`+`camera`+`mat/box/cyl/camKeys` (sem renderer), chamada uma vez por diorama, lazy (na primeira vez que a `IntersectionObserver` de prefetch, hoje `perto` em `maquetes.js:269-273`, aproxima aquele capítulo).
   - **Uma luz só**: um `HemisphereLight` + um `DirectionalLight`/sombra compartilhados entre as 9 cenas, reparentados (`cenaAtiva.S.add(sun)`) a cada troca de capítulo, em vez de 9 sóis com 9 shadow maps. Isso é o ponto que mais economiza GPU (ver Riscos).
   - Um **laço de render único** (`requestAnimationFrame`) que sabe qual `data-passo` está `.ativo` (via `historia.js`/`H.ativa`) e chama `cenaAtual.update(t)` + `R.render(cenaAtual.S, cenaAtual.cam)`.
3. **`historia.js` não muda**: o contrato `fundos[passo].__maquete = {seek, dur, frozen}` (usado em `sincronizar()`, `historia.js:41-51`) continua igual — é exatamente esse desacoplamento que garante que dá para trocar o motor por baixo sem mexer em `historia.js` nem quebrar `check_historia.py`'s testes de navegação (`checar_navegador`, `seek zip=...`, `reversao-48 ativa=casa` etc.).
4. **`portfolio.html` fica como está**: ele usa as mesmas `CENAS['36min']`/`CENAS['casa-viaja']`, mas soltas no fluxo normal (duas figuras podem estar visíveis ao mesmo tempo rolando a página — é o caso de uso que *precisaria* de scissor se crescesse). Como só tem 2 hoje, **não vale a pena** generalizar tudo para scissor nesta rodada — a recomendação é separar apenas o caminho de `index.html` para o motor compartilhado e deixar `portfolio.html` no modelo atual (um `stage()`/renderer por figura), reaproveitando as mesmas funções `CENAS[nome]` de construção de cena (que passam a não criar mais o próprio renderer) atrás de dois "invólucros" diferentes: um por-figura (portfolio.html, comportamento igual a hoje) e um compartilhado (index.html, novo).

### O que descartar do `film.html`
Nada do sistema de legendas do filme entra: `#cap`/`#hud`/`#num`/`#prog`/`#wipe`/`.bar`/`#cover`/`#end` e os `@font-face` com `woff2` locais são só para o vídeo de 1280×720 fixo — a página já tem tudo isso em HTML acessível (`h2.frase`, `p.ressalva`, `p.data`, `.regua`, `data-relogio`/`data-legenda`). O único pedaço realmente reaproveitável é a **geometria e a animação** de cada `st.run(t)`, e — feliz coincidência — o formato de `st.cam` do filme (`[[t,[x,y,z],[tx,ty,tz]], ...]`) é **idêntico** ao formato que `camKeys()` já espera em `maquetes.js:37-41`. O sistema de câmera do filme é mais sofisticado (Catmull-Rom + oscilação "respirando", `camAt()` em `film.html:319-320`) — não recomendo portar isso; `camKeys()` (lerp reto entre keyframes) é mais simples e mais barato, só vai exigir reajustar os keyframes a olho depois de trocar de spline para lerp.

### Tamanho estimado do código
`maquetes.js` tem hoje 235 linhas. Estimativa:
- Refatorar `stage()` em `motor()`+`cenaBase()` e o novo laço compartilhado: **+70 a +100 linhas** (a maior parte é o novo "diretor" que substitui a IntersectionObserver+rAF+guarda de fps por-figura de `montar()` por uma versão que sabe olhar `historia.js`).
- 3 dioramas novos (escritório, duas construtoras, VEKS): **+90 a +130 linhas** (cada um é geometria simples: caixas, cilindros, 1-2 texturas canvas).
- Se entrarem os outros 3 (restaurante, SIGE, WhatsApp): **+90 a +120 linhas** adicionais.
Total razoável: `maquetes.js` cresce de 235 para **~400 linhas (só os 3 MUST) a ~550 linhas (os 9 completos)** — nada que quebre o "sem build": ainda é um único arquivo ES module vendorizado.

### Caminho de migração sem quebrar as 3 maquetes atuais
1. Primeiro PR: só a refatoração `stage()`→`motor()`+`cenaBase()` + laço compartilhado em `index.html`, **sem** adicionar diorama nenhum — as 3 cenas existentes (`36min`, `casa-viaja`, `icamento`) passam a rodar no motor único. `check_historia.py --navegador` já teria que continuar passando integralmente (é o teste que teria de pegar qualquer regressão de `seek`/`dur`/fps-guard).
2. Atualizar `checar_fundo()` em `check_historia.py` (a asserção do `<canvas></canvas>` por figura) para refletir o novo contrato (canvas único no `.palco`).
3. Segundo PR: os 3 dioramas novos (`origem`, `obra`, `ferramentas`), com o texto/ressalva que já existe hoje inalterado.
4. Terceiro PR (decisão de produto): os outros 3, só se a troca "print real → diorama estilizado" for aprovada.

## Caminho C: trailer em vídeo (pipeline sem Playwright)

Aqui não há Playwright, mas `check_historia.py` já tem tudo que falta: a classe `WS` (cliente WebSocket mínimo para o DevTools Protocol, `check_historia.py:401-458`) e o `chromium()` (context manager que sobe um `http.server` em `portfolio/` + Chromium headless com `--enable-unsafe-swiftshader`, usado em `checar_maquete_real()`). O gancho certo é `renderAt(T)` (já determinístico, `film.html:323`) + `Page.captureScreenshot`.

### Onde colocar a fonte do filme
Copiar o `film.html` **corrigido** (com os 8 problemas de conteúdo do `00-contexto.md` já resolvidos) junto com `fonts/` e `three.min.js` para uma pasta dentro de `portfolio/` — por exemplo `portfolio/render/filme/` — porque o `chromium()` de `check_historia.py` já serve `ROOT` = `portfolio/` inteiro; assim dá para importar `chromium`/`WS`/`PORTA` de `check_historia.py` sem editar o arquivo.

### Sequência exata
1. `chromium(1280, ("--enable-unsafe-swiftshader",))` — reaproveita o helper, mas ele fixa `height=800`; **é preciso reemitir** `Emulation.setDeviceMetricsOverride` com `height=720` depois de entrar no `with`, porque `film.html` tem `html,body{width:1280px;height:720px}` fixo.
2. `Page.navigate` para `http://127.0.0.1:{PORTA}/render/filme/film.html`.
3. Esperar ~2 s (as fontes `@font-face` locais precisam baixar; o resto do script de `film.html` é 100% síncrono — nenhuma textura é carregada de arquivo, todas são `CanvasTexture` geradas em memória, então `window.TOTAL` já existe assim que o `<script>` termina).
4. `N = round(TOTAL * 30)` (TOTAL ≈ 85 s ⇒ N ≈ 2550 quadros).
5. Para cada `i`: `ws.avaliar(f"renderAt({i/30})")` (síncrono, já desenha no canvas) e **em seguida** `ws.comando("Page.captureScreenshot", format="jpeg", quality=90)` — **é obrigatório passar `format="jpeg"` explicitamente** (o padrão do CDP é PNG; se cair PNG no `-vcodec mjpeg` do ffmpeg, ele não decodifica). Decodificar `base64.b64decode(shot["data"])` e escrever no `stdin` do ffmpeg.
6. Guardar o quadro `i==0` também como arquivo separado (`poster.jpg`) — é o quadro de capa do `<video poster>`.

### ffmpeg exato
```
ffmpeg -y -loglevel error -f image2pipe -framerate 30 -vcodec mjpeg -i - \
  -c:v libx264 -preset slow -crf 23 -pix_fmt yuv420p \
  -vf scale=960:540 -movflags +faststart \
  cassio-viller-trailer.mp4
```
- `crf 23` + `preset slow`: ponto de equilíbrio qualidade/tamanho recomendado para vídeo web em H.264.
- `-movflags +faststart`: move o `moov atom` para o início do arquivo, essencial para `preload="none"`/tocar antes do download completo.
- `scale=960:540` (540p): mais que suficiente para um "assista em 85 s" embutido numa página que já pesa por causa das 9 dioramas 3D; a fonte fica em 1280×720 (a `R.setPixelRatio(1)` do filme trava o canvas nessa resolução física, então o `deviceScaleFactor` do CDP **não** acelera o render em si — só encolheria o screenshot final. Para render mais rápido de verdade, o ajuste teria que ser nos números `1280,720` dentro do próprio `film.html` — `R.setSize(1280,720,false)`, `cam.setViewOffset(...)` e os `<canvas width height>` —, não no lado do Chromium).

### Onde ficam os arquivos
- `portfolio/site/trailer/cassio-viller-trailer.mp4`
- `portfolio/site/trailer/poster.jpg`
- `portfolio/site/trailer/cassio-viller-trailer.vtt` (legendas — dá para gerar direto do array `CAPS`/`START`/`DUR` que já existe em `film.html:301-314`, sem inventar texto novo)

### HTML do bloco do trailer
```html
<section class="trailer">
  <h2 class="frase">Assista em 85 segundos.</h2>
  <video controls preload="none" playsinline width="1280" height="720"
         poster="trailer/poster.jpg">
    <source src="trailer/cassio-viller-trailer.mp4" type="video/mp4">
    <track kind="captions" srclang="pt-BR" label="Português" src="trailer/cassio-viller-trailer.vtt" default>
    Seu navegador não reproduz vídeo. <a href="trailer/cassio-viller-trailer.mp4">Baixe o vídeo</a>.
  </video>
  <p class="ressalva"><a href="trailer/transcricao.html">Transcrição em texto</a></p>
</section>
```
Sem `autoplay` (o vídeo é mudo — não tem áudio nenhum — e mesmo assim autoplay muted é ruim em página já cheia de scroll-jacking visual); `preload="none"` porque o trailer é conteúdo opcional, abaixo da dobra; `playsinline` evita que o iOS force tela cheia ao tocar; `width`/`height` evitam layout shift, igual ao padrão já cobrado pelo `check_historia.py` para as imagens (`checar_fundo`).

## Caminho A: vale a pena? (curto)

Não. A pesquisa confirma o que o `00-contexto.md` já desconfiava: `currentTime` scrubado via scroll em iOS Safari só fica suave com GOP praticamente all-intra (`-g 10` ou menor), o que anula a compressão H.264 e infla o arquivo várias vezes; sem isso, o vídeo trava/pula ao rolar rápido. E mesmo resolvendo isso, texto gravado no vídeo continua sem alternativa textual para leitor de tela — problema que os Caminhos B (texto sempre em HTML) e C (com `<track>`+transcrição) já resolvem de graça. Não vejo cenário em que A supere B+C aqui.

## O que a pesquisa diz (bullets com fontes)

- Um canvas + um `WebGLRenderer`, trocando qual `Scene` é desenhada, evita o teto de contextos WebGL do navegador (documentado como "por volta de 8" antes de o mais antigo ser descartado) e permite compartilhar recursos entre as cenas virtuais — [gfxfundamentals: threejs-multiple-scenes](https://github.com/gfxfundamentals/threejsfundamentals/blob/master/threejs/lessons/threejs-multiple-scenes.md)
- A técnica de "scissor" (várias cenas visíveis ao mesmo tempo num canvas só) tem como efeito colateral o conteúdo "descolar" da rolagem quando o render atrasa em relação ao scroll — por isso ela serve para `portfolio.html` (várias figuras juntas), não para `index.html` (só uma visível por vez) — [gfxfundamentals: threejs-multiple-scenes](https://github.com/gfxfundamentals/threejsfundamentals/blob/master/threejs/lessons/threejs-multiple-scenes.md), [discourse.threejs.org: rendering multiple scenes](https://discourse.threejs.org/t/rendering-multiple-scenes-on-same-canvas/42131)
- Chrome permite tipicamente até 16 contextos WebGL simultâneos em desktop e 8 em Android antes de descartar o mais antigo; navegadores mobile mais restritos (ex. Firefox mobile antigo) já tiveram limite de 2 — [superchargebrowser.com: WebGL context lost fixes](https://www.superchargebrowser.com/library/fix-chrome-webgl-context-lost/), [bugzilla.mozilla.org #1421481](https://bugzilla.mozilla.org/show_bug.cgi?id=1421481)
- three.js removeu `physicallyCorrectLights`/trocou por `useLegacyLights` no r150, mudou o padrão de `useLegacyLights` para `false` no r155 (afeta intensidade de todas as luzes e decaimento de point/spot) — relevante porque `film.html` (r128) usa intensidades tunadas para o modelo antigo (`DirectionalLight` intensidade `2.3`, `HemisphereLight` `.62`); ao portar para r186, os valores de intensidade das luzes precisam ser reajustados a olho, não só copiados — [three.js release r155](https://github.com/mrdoob/three.js/releases/tag/r155), [PR #24975](https://github.com/mrdoob/three.js/pull/24975)
- `outputEncoding`/`sRGBEncoding`/`texture.encoding` foram substituídos por `outputColorSpace`/`SRGBColorSpace`/`texture.colorSpace` a partir do r152 — todo `R.outputEncoding=THREE.sRGBEncoding` e `paper.encoding=THREE.sRGBEncoding` de `film.html` precisam virar `R.outputColorSpace=THREE.SRGBColorSpace`/`paper.colorSpace=THREE.SRGBColorSpace` (confirmado: `vendor/three.module.js` já não exporta `sRGBEncoding`) — [PR #25756](https://github.com/mrdoob/three.js/pull/25756), [three.js Migration Guide](https://github.com/mrdoob/three.js/wiki/Migration-Guide)
- Para vídeo web em H.264: CRF entre 22 e 24 com preset `medium`/`slow` é o ponto de partida recomendado; `-movflags +faststart` é obrigatório para tocar antes do download completo — [ffmpeg-cookbook.com: compress video](https://ffmpeg-cookbook.com/en/articles/compress-video/), [ffmpeg-cookbook.com: faststart](https://ffmpeg-cookbook.com/en/articles/ffmpeg-faststart-web-playback/), [tulipfilms.ch: CRF 23 + faststart checklist](https://www.tulipfilms.ch/en/post/video-kompression-furs-web)
- Scrub suave por `currentTime` depende de intervalo de keyframe curto (`-g 10` ou menor); sem isso, iOS Safari e outros navegadores travam/pulam ao arrastar rápido — inviabiliza vídeo-como-fundo controlado por scroll sem inflar drasticamente o arquivo — [muffinman.io: scrubbing videos using JavaScript](https://muffinman.io/blog/scrubbing-videos-using-javascript/)
- `preload="none"` é a recomendação para vídeo abaixo da dobra/opcional; poster + `<track kind="captions">` (WebVTT) são as práticas básicas de acessibilidade para vídeo — [mux.com: best practices for video playback](https://www.mux.com/articles/best-practices-for-video-playback-a-complete-guide-2025), [frontendchecklist.io: video accessibility](https://frontendchecklist.io/rules/html/video-accessibility)

## Trechos de código de referência

Formato de câmera idêntico entre o filme e `maquetes.js` (facilita o porte direto dos `st.cam` do filme):
```js
// film.html:122 (CENA 1 · escritório)
st.cam=[[0,[7,6.5,9],[0,1.8,-2]],[5,[4.2,4.2,4.5],[0,2,-2.6]],[10,[1.6,2.9,1.6],[0,2.22,-2.5]]];

// maquetes.js:37-41 — mesmo formato [t,[pos],[alvo]]
function camKeys(K,t,wide){
  var i=0;while(i<K.length-2&&t>K[i+1][0])i++;var a=K[i],b=K[i+1],f=ease((t-a[0])/(b[0]-a[0]));
  ...
  cam.position.set(tx+(px-tx)*wide,ty+(py-ty)*wide,tz+(pz-tz)*wide);cam.lookAt(tx,ty,tz);}
```

Contrato que `historia.js` já cobra de cada maquete e que **não muda** no Caminho B (`historia.js:41-51`):
```js
function sincronizar(){
  var f=H.ativa&&fundos[H.ativa];
  if(!f||!f.classList.contains('maquete'))return;
  var api=f.__maquete;
  if(!api||!api.dur){ if(!aguardando)aguardando=setTimeout(function(){aguardando=0;sincronizar();},200); return; }
  var r=document.querySelector('.cena[data-passo="'+H.ativa+'"]').getBoundingClientRect();
  api.seek(progresso(r.top,r.height,innerHeight)*api.dur*0.999);
}
```

Pipeline de render sem Playwright (esqueleto usando o `chromium()`/`WS` de `check_historia.py`):
```python
import sys, base64, subprocess, time
sys.path.insert(0, "/home/runner/workspace/portfolio/tests")
from check_historia import chromium, PORTA

FPS = 30
ff = subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),
    '-vcodec','mjpeg','-i','-','-c:v','libx264','-preset','slow','-crf','23','-pix_fmt','yuv420p',
    '-vf','scale=960:540','-movflags','+faststart','cassio-viller-trailer.mp4'], stdin=subprocess.PIPE)

with chromium(1280, ("--enable-unsafe-swiftshader",)) as ws:
    ws.comando("Emulation.setDeviceMetricsOverride", width=1280, height=720, deviceScaleFactor=1, mobile=False)
    ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/render/filme/film.html")
    time.sleep(2.5)
    total = ws.avaliar("window.TOTAL")
    n = round(total * FPS)
    for i in range(n):
        ws.avaliar(f"renderAt({i/FPS})")
        shot = ws.comando("Page.captureScreenshot", format="jpeg", quality=90)
        jpg = base64.b64decode(shot["data"])
        if i == 0:
            open("poster.jpg", "wb").write(jpg)
        ff.stdin.write(jpg)
        if i % 150 == 0: print(i, flush=True)
ff.stdin.close(); ff.wait(); print("done")
```

## Requisitos para o plano (P4-01…)

- **P4-01 (MUST)** — Em `index.html`, o `.palco` tem exatamente **um** `<canvas>` compartilhado por todas as `figure.maquete`; nenhuma delas carrega `<canvas></canvas>` próprio no HTML. Testável: `checar_fundo()` em `check_historia.py` passa a checar canvas único no `.palco`, não um por figura.
- **P4-02 (MUST)** — `portfolio.html` mantém o modelo atual (um `WebGLRenderer` por `figure.maquete`), sem alterações de marcação ou comportamento. Testável: com o navegador aberto em `portfolio.html`, rolar até `36min` e `casa-viaja` ficarem visíveis juntos — as duas continuam animando de forma independente.
- **P4-03 (MUST)** — As 9 cenas de `index.html` compartilham **uma** luz direcional com sombra (reparentada via `scene.add(sun)` a cada troca de capítulo); no máximo um shadow map de 2048×2048 fica alocado por vez. Testável: sonda no harness Chromium lendo `renderer.info.memory` depois de visitar 5 capítulos seguidos — a contagem de texturas não cresce a cada capítulo.
- **P4-04 (MUST)** — O contrato público `fundos[passo].__maquete.{seek,dur,frozen}` usado por `historia.js` não muda. Testável: `check_historia.py --navegador` (incluindo `seek zip=...`, `reversao-48 ativa=casa`) passa sem editar `historia.js`.
- **P4-05 (MUST)** — As cenas novas reaproveitam o formato de `camKeys()` (`[t,[pos],[alvo]]`, sem spline); nenhuma `CatmullRomCurve3` entra em `maquetes.js`. Testável: `grep -c CatmullRomCurve3 portfolio/site/maquetes.js` = 0.
- **P4-06 (MUST)** — Nada do sistema de legenda/transição do filme (`#cap`,`#hud`,`#wipe`,`.bar`,`#cover`,`#end`,`#prog`, `@font-face` woff2 locais) entra em `index.html`/`maquetes.js`; a legenda de cada capítulo continua vindo só de `h2.frase`/`p.ressalva`/`p.data`. Testável: nenhuma dessas classes/ids aparece no diff de `index.html`/`maquetes.js`.
- **P4-07 (SHOULD)** — Migração faseada: primeiro PR troca só o motor (3 cenas atuais, 0 dioramas novos); segundo PR adiciona os 3 dioramas que hoje são `fundo tipo` (origem, obra, ferramentas); dioramas que substituiriam prints reais (escala, sige, whatsapp) ficam para decisão de produto à parte. Testável: o PR do segundo passo só toca esses 3 capítulos.
- **P4-08 (MUST, Caminho C)** — O `film.html` usado para renderizar já tem os 8 problemas de conteúdo do `00-contexto.md` corrigidos antes do render (13 obras, R$ 155.000, balancim como estudo, datas do SIGE, dias de WhatsApp, "cinco vezes", 26 anos, frase do capítulo 1). Testável: nenhuma das strings sinalizadas no `00-contexto.md` aparece no `film.html` usado pelo pipeline.
- **P4-09 (MUST, Caminho C)** — O bloco de vídeo publicado tem `preload="none"`, `playsinline`, `width`/`height`, **sem** `autoplay`, e uma faixa `<track kind="captions">` (WebVTT gerada a partir de `CAPS`/`START`/`DUR` do próprio filme) mais um link de transcrição em texto. Testável: inspeção do HTML publicado.
- **P4-10 (SHOULD, Caminho C)** — Antes de rodar os ~2550 quadros completos, fazer um render de amostra (100–150 quadros) para medir segundos-por-quadro reais desta técnica (DevTools Protocol quadro a quadro é mais lento que o `page.screenshot()` do Playwright do `render.py`) e decidir se vale reduzir a resolução interna do `film.html` (editar os `1280,720` de `R.setSize`/`cam.setViewOffset`/`<canvas>`) antes do render final.

## Riscos e armadilhas

- **Luz compartilhada com frustum de sombra desajustado**: cada diorama tem uma "pegada" de tamanho diferente; reaproveitar um único `sun.shadow.camera.left/right/top/bottom` sem reajustar por cena vai gerar sombra cortada ou de baixa resolução em algumas — precisa reconfigurar os 4 números (e `updateProjectionMatrix()`) a cada troca de capítulo, não só reparentar a luz.
- **`Page.captureScreenshot` volta PNG por padrão**: se o pipeline do Caminho C não passar `format:"jpeg"` explicitamente, o ffmpeg (configurado com `-vcodec mjpeg` de entrada) recebe bytes que não sabe decodificar e o pipe trava/corrompe silenciosamente.
- **Pipeline via DevTools Protocol é mais lento que Playwright**: cada quadro faz 2 idas-e-voltas síncronas pelo WebSocket (evaluate + screenshot em base64), contra uma chamada de `page.screenshot()` do Playwright; `render.py` já estima ~20 min via Playwright — o caminho aqui provavelmente é mais lento. Fazer o smoke test (P4-10) antes de prometer um tempo de render.
- **`R.setPixelRatio(1)` no `film.html` trava o canvas em 1280×720 físicos**: mudar o `deviceScaleFactor` do CDP só encolhe o screenshot final, não acelera o SwiftShader (que já rasteriza tudo a 1280×720 antes da captura). Para render mais rápido de verdade, é preciso editar os números fixos dentro do `film.html`.
- **Fps-guard vira "tudo ou nada" com motor compartilhado**: hoje cada maquete decide sozinha (via `frames`/`slow` em `montar()`, `maquetes.js:252-253`) se cai para imagem estática; com um motor único para as 9 cenas de `index.html`, a medição de desempenho passa a valer para a página toda — um capítulo pesado pode "matar" os outros 8 mesmo que fossem leves sozinhos. É uma troca aceitável (mais simples), mas é uma mudança de comportamento que vale confirmar com quem decide o produto, não um bug.
- **Botão de pausa (WCAG 2.2.2)**: `montar()` cria um botão de pausa por figura hoje; ao centralizar o laço de render, o estado `frozen` continua tendo que ser por-capítulo (senão pausar um diorama pausaria a página toda) — a API `fig.__maquete.frozen` deve continuar por figura mesmo com o loop de `requestAnimationFrame` central.
- **Redesenho de `CanvasTexture` por frame**: cenas como escritório (`st.scr.userData.draw`) e WhatsApp (`st.board`) redesenham uma textura 2D a cada frame — replicar esse padrão em 6 cenas novas, todas residentes na mesma sessão (se a decisão for não descartar cenas inativas), soma memória JS (não só GPU) em aparelhos fracos; medir em um Android de entrada antes de decidir se as cenas 2+ capítulos de distância precisam ser descartadas (`geometry.dispose()`/`material.dispose()`/`texture.dispose()`) em vez de mantidas.
- **Os quadros já capturados (`q00.png`…`q09.png`) podem ter vindo do Playwright da sessão original**, não do caminho DevTools Protocol proposto aqui — antes de prometer que a rota CDP funciona, validar com 1 quadro que o WebGL de fato renderiza (e não fica em branco por falta de `--enable-unsafe-swiftshader` ou por CORS ao servir os arquivos).

## Fontes

- [gfxfundamentals: threejs-multiple-scenes.md](https://github.com/gfxfundamentals/threejsfundamentals/blob/master/threejs/lessons/threejs-multiple-scenes.md)
- [discourse.threejs.org: Rendering multiple scenes on same canvas](https://discourse.threejs.org/t/rendering-multiple-scenes-on-same-canvas/42131)
- [pmndrs/react-three-scissor](https://github.com/pmndrs/react-three-scissor)
- [superchargebrowser.com: WebGL Context Lost in Chrome — fixes](https://www.superchargebrowser.com/library/fix-chrome-webgl-context-lost/)
- [bugzilla.mozilla.org #1421481 — mobile WebGL context limit](https://bugzilla.mozilla.org/show_bug.cgi?id=1421481)
- [three.js Release r155 — lighting defaults](https://github.com/mrdoob/three.js/releases/tag/r155)
- [three.js PR #24975 — physicallyCorrectLights → useLegacyLights](https://github.com/mrdoob/three.js/pull/24975)
- [three.js PR #25756 — outputEncoding → outputColorSpace](https://github.com/mrdoob/three.js/pull/25756)
- [three.js Migration Guide (wiki)](https://github.com/mrdoob/three.js/wiki/Migration-Guide)
- [ffmpeg-cookbook.com: Compress Video — CRF, Bitrate, Preset Guide](https://ffmpeg-cookbook.com/en/articles/compress-video/)
- [ffmpeg-cookbook.com: faststart — fix video that won't start until fully downloaded](https://ffmpeg-cookbook.com/en/articles/ffmpeg-faststart-web-playback/)
- [tulipfilms.ch: CRF 23 and +faststart checklist](https://www.tulipfilms.ch/en/post/video-kompression-furs-web)
- [muffinman.io: Scrubbing videos using JavaScript](https://muffinman.io/blog/scrubbing-videos-using-javascript/)
- [MDN: HTMLVideoElement.requestVideoFrameCallback()](https://developer.mozilla.org/docs/Web/API/HTMLVideoElement/requestVideoFrameCallback)
- [mux.com: Best Practices for Video Playback (2025)](https://www.mux.com/articles/best-practices-for-video-playback-a-complete-guide-2025)
- [frontendchecklist.io: Video accessibility (captions)](https://frontendchecklist.io/rules/html/video-accessibility)
