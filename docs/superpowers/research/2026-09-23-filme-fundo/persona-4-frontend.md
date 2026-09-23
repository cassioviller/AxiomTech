# Persona 4 — Tiago (rodada 4): um clipe MP4 por cena, movido pela rolagem

*dev front-end de scrollytelling, sem build, celular primeiro*

Li o `00-contexto.md` inteiro, o meu parecer da rodada 3, `site/historia.js` (111 linhas), `site/maquetes.js` (274), o CSS do modo cenas (`site/index.html:64-123`), a marcação das 17 cenas (`:161-343`), `filme/film.html` (estrutura, `renderAt`, `setViewOffset`), `filme/render.py`, `tests/check_historia.py` (669 linhas), `tests/historia_teste.html` e `tests/check_filme.py`. Além de ler, **medi**: encodei 8 trechos do mestre `filme/saida/historia-1280.mp4` com os parâmetros candidatos, contei quadros-chave com `ffprobe`, e rodei no Chromium 152 headless daqui (`/repl/tools/bin/chromium`) um teste de seek real por `currentTime` — que revelou uma armadilha que teria quebrado o `checar_clipe_real` e, pior, a página no ar (§2.4).

A decisão do Cássio não se reabre; este parecer decide o *como*.

## 1. O que vejo (file:linha)

- **`historia.js` já tem o contrato certo e quase não muda.** `sincronizar()` (`historia.js:41-51`) só age na figura ativa com classe `maquete`, lê `f.__maquete.{dur,seek}` e chama `api.seek(progresso*dur*0.999)` a cada `scroll`+rAF (`:104-108`); `ativar()` (`:74-91`) troca `.ativo`, faz `hidden=false` + `resize` ao entrar e `hidden=true` 650 ms depois de sair (`:70-73`). Nada disso sabe o que é WebGL. Para o vídeo, muda **só o nome da classe e da propriedade** (4 linhas: `:35, :43, :44, :79`).
- **`maquetes.js` faz três coisas que o vídeo substitui**: carregar sob demanda a 600 px (`perto`, `:269-273`), montar o renderizador (`stage`, `:22-43`; `montar`, `:238-267`), e a guarda de fps + `matar()` (`:253, :257`). O contrato exposto é `fig.__maquete={frozen,dur,seek(x){t=x;frozen=true}}` (`:258`). O `.viva` (`:254`) é o que esconde a imagem de reserva no CSS (`index.html:105-106`). `portfolio.html:452, :802, :1082` usa o mesmo arquivo com duas figuras soltas no fluxo — **não se toca em `maquetes.js`**.
- **HUD**: cada figura de maquete traz `<div class="hud"><b data-relogio></b><span data-legenda></span></div>` (`index.html:265, :279, :313`); `montar()` escreve `sc.num`/`sc.leg` nele a cada quadro (`maquetes.js:250-251`). Só a `36min` tem número (`api.num='11:35'…'12:11'`, `:90-91`); a `icamento` devolve `''` (`:229`) e a `casa` só números de legenda (`3,8 t`, `6,00 m`, `59,5 m²`) que a página não mostra por texto. O CSS do HUD e três checagens dependem disso (`index.html:107-110`; `check_historia.py:208, :319-323`).
- **CSS do modo cenas**: `.palco .fundo canvas{…opacity:0}` / `.viva canvas{opacity:1}` / `.viva img{visibility:hidden}` (`index.html:104-106`) é exatamente o par que o vídeo precisa, trocando `canvas` por `video`. O `img` do palco leva `filter:brightness(.6) saturate(.85)` (`:103`). Modo empilhado: `.fundo canvas,.fundo .hud{display:none}` (`:70`). A regra `.fundo .pausa{display:none!important}` (`:71`) e o `@media (prefers-reduced-motion)` que desliga só transições (`:123`) também são do desenho antigo.
- **`film.html`**: `renderAt(T)` (`:317-339`) é puro em T, mas mistura o diorama com o DOM de legenda; o k é derivado de `T` e `START[]`, e a **varredura de transição (`#wipe`) cobre o quadro em T∈[fronteira−0,5 s, fronteira+0,5 s]** (`:323`), o `#fade` cobre o início (`:322`). Sem uma flag "limpo", o pôster tirado em `T=START[k]` sai **em branco** — testei: um WebP de 960×540 nesse instante tem 1 064 bytes (é o bege `#EFE6D6` da varredura). A câmera tem `cam.setViewOffset(1280,720,-230,-20,1280,720)` (`:76`): o assunto fica em ≈(870, 380) px, isto é, **68 % × 53 %** do quadro — é esse o `object-position` correto para o recorte em pé.
- **`render.py`**: Playwright com o Chromium do sistema, `renderAt(i/30)` → JPEG q92 por pipe → mestre crf 20 → web `scale=960:540 crf 26`. ~13 min para 2 550 quadros ⇒ **≈0,3 s por quadro**. O mesmo pipeline serve para os clipes; só muda quem escolhe a cena e o instante.
- **`check_historia.py`**: `ROTEIRO` com tipos `img/ano/maquete/None` (`:32-107`); `checar_fundo` (`:173-208`) exige `<canvas></canvas>` + HUD nas maquetes; `checar_marcacao` (`:220-221`) amarra `cena longa` ao tipo `maquete`; `checar_css` checa HUD/`.pausa` (`:304, :319-323`); `checar_scripts` = `["maquetes.js","historia.js"]` (`:326-331`); `checar_js` proíbe `fps`/`matar` em `historia.js` (`:434`); `checar_maquetes_js` (`:437-443`) continua valendo para o portfólio; o harness cria `__maquete` falso `{dur:1000}` (`historia_teste.html:27`) e roda com `--disable-3d-apis` (`:537`); `checar_maquete_real` (`:591-615`) usa SwiftShader; `checar_filme`/`checar_fim_do_palco` (`:392-419, :618-639`) saem, mas a checagem da ficha à vista (`:634-639`) fica (F-07). **O `chromium()` do harness serve os arquivos com `python3 -m http.server` (`:510`), que não responde a `Range`** — ver §2.4.

## 2. O que a pesquisa e as medições dizem

### 2.1 Encode: GOP curto, sem B-frames, 24 fps (medido aqui)
Trecho de 8,5 s do restaurante, `scale=960:540`, `preset slow`, `+faststart`, `-an`:

| variante | bytes | quadros-chave / quadros |
|---|---|---|
| 30 fps, crf 26, g 5 (o do contexto) | 853 495 | 51 / 255 |
| **24 fps, crf 27, g 4** | 797 542 | 51 / 204 |
| 24 fps, crf 28, g 4 | 733 914 | 51 / 204 |
| 24 fps, crf 27, g 3 | 970 505 | 68 / 204 |
| 24 fps, crf 27, g 6 | 601 191 | 34 / 204 |
| 24 fps, crf 27, g 4, `-bf 0` | 807 903 | 51 / 204 |
| 24 fps, crf 27, g 4, `-tune animation` | 774 539 | 51 / 204 |

Variância entre cenas (8 s, crf 28, g 4, `-bf 0`): escritório 915 618 · celeiro 933 638 · WhatsApp 911 017 · rua 865 816 (crf 27) · SIGE 892 641 (crf 27) · VEKS 787 978 (crf 27) · 36 min 822 312 (crf 27). Ou seja: **≈0,9 MB por 8 s** nas cenas pesadas; um clipe de 10 s chega a ≈1,15 MB. `-bf 0` custa 1 % e garante que todo quadro depende só de quadros *anteriores* (um I + até 3 P para chegar a qualquer instante); com B-frames o decodificador precisa do P *seguinte* também. A literatura converge: muffinman.io recomenda `keyint=10:scenecut=0` para MP4 e mostra o preço (keyframe a cada 5 quadros = 845 KB contra 146 KB a cada 100, ~5×); Yoann Gueny mostra que o intervalo padrão de 72 quadros do Media Encoder trava a rolagem e que "1 é o melhor, mas o peso sobe muito". `-sc_threshold 0` é o que impede o x264 de inserir I-frames extras nos cortes e desalinhar o GOP.

### 2.2 Seek: `currentTime`, um em voo por vez, `seeked` como confirmação
- `fastSeek()` existe no Safari (desde o 8) e no Firefox (31), **não existe no Chrome** (caniuse; confirmado aqui: `'fastSeek' in HTMLMediaElement.prototype === false`). E o MDN é explícito: ele troca precisão por velocidade — com GOP de 4 quadros a "precisão" de um seek já é 3 quadros, então `fastSeek` não compra nada. Decisão: só `currentTime`.
- `requestVideoFrameCallback` (Safari 15.4+, Chrome 83+, Firefox 132+) entrega `mediaTime`/`presentedFrames` quando um quadro vai ao compositor. **Medido**: no headless sem servidor `Range` ele disparou 1 vez e nunca mais; com servidor `Range`, disparou 26 vezes em 40 seeks pausados (GOP 4) — dispara, mas *não a cada seek*, e o Video.js precisou de fallback por ele falhar no Safari com DRM. Decisão: `seeked` é a confirmação; rVFC não entra.
- **Medido com servidor `Range`, Chromium headless, decodificação por software** (40 seeks de 0,2 s em 0,2 s, esperando cada `seeked`): GOP 4 → mediana **11 ms**, máx. 18 ms; GOP 250 → mediana **77 ms**, máx. 114 ms. Rajada de 30 seeks disparados um por rAF sem esperar: GOP 4 completou **29 de 30**; GOP 250 completou **3 de 30** (o navegador engole os intermediários e o quadro "salta"). Isto é a prova, no Chromium, de que o GOP curto é o que faz o quadro seguir a rolagem — e dá um teste automatizável que discrimina um encode errado (§3.6).
- Apple QA1820 (AVPlayer) documenta o mesmo princípio para o iOS: nunca empilhar seeks — só emitir o próximo quando o anterior completou, guardando o último pedido ("seek coalescing"). É o que `seek()` de `clipes.js` faz (§3.2).

### 2.3 Carregamento: `preload="none"` no HTML, `load()` a 600 px; blob, não
- web.dev "Lazy loading video": marcação `preload="none"` + `poster` + `muted playsinline`, IntersectionObserver liga o carregamento ao aproximar. ImageKit acrescenta o motivo do `preload="none"`: sem ele "Firefox e Safari frequentemente carregavam vídeos curtos inteiros mesmo bem abaixo da dobra".
- Carregar por `fetch`+`blob` (para "ter o arquivo inteiro e buscável") **está vetado**: no iOS 15 o `src=blob:` recarregava o blob sem parar e estourava a memória (Apple Developer Forums 693447), e o WebKit 232076 registra iOS sem tocar vídeo de `blob`/`data:`. Basta `+faststart` (o `moov` antes do `mdat`: medido, `moov@36 mdat@3044`) e um servidor com `Range`.
- `prefers-reduced-motion`: `<video autoplay muted>` toca em todos os navegadores mesmo com a preferência ligada (WHATWG #11605: "Right now, in all browsers `<video autoplay muted>` will auto play even if the user has indicated they prefer reduced motion"); o padrão de Scott O'Hara é `matchMedia('(prefers-reduced-motion)')`, checar no load e ouvir `change`. Aqui o vídeo nunca toca sozinho (o tempo é a rolagem), mas a preferência ainda deve tirar o movimento — e o CSS resolve a troca *instantânea* sem JS (§3.5).

### 2.4 A armadilha: sem `Range`, o Chrome ignora o seek em silêncio
Medido três vezes, com MP4 e com WebM VP9, com e sem `--disable-gpu`, com SwiftShader: servido pelo `http.server` do Python (sem `Accept-Ranges`), o Chromium reporta `readyState 4`, **`seekable=[0,0]`**, dispara `seeked` normalmente… e **`currentTime` continua 0** depois de `currentTime=2`, `=4.5`, `=6`. `play()` avança (0,30 s), mas seek nenhum é honrado. Com um servidor que responde `206`/`Content-Range` (escrevi um de 20 linhas para o teste): `seekable=[0,8.5]`, `currentTime` obedece, e vêm os números do §2.2. Consequências: (a) o `chromium()` do `check_historia.py` **não serve** para testar clipe de verdade sem um servidor com `Range`; (b) **a hospedagem precisa responder `Range`** — vira checagem (`P4-13`); (c) `clipes.js` **checa `seekable`** depois de `loadedmetadata` e, se vier vazio, fica no pôster em vez de "funcionar" sem mexer (§3.2).

## 3. Decisões

### 3.1 Marcação: a `<figure class="fundo clipe">`
```html
<section class="cena longa" id="zip" data-passo="zip">
  <figure class="fundo clipe" data-passo="zip" data-dur="10" aria-hidden="true">
    <video muted playsinline preload="none" disableremoteplayback width="960" height="540"
           src="video/cena-zip.mp4"></video>
    <img src="video/cena-zip.webp" alt="" width="960" height="540" loading="lazy">
  </figure>
  <div class="texto">…</div>
</section>
```
- **Classe `fundo clipe`** (não `maquete`: é vídeo, e `maquete` continua sendo o nome do WebGL no portfólio). `data-passo` como hoje; **`data-dur`** com a duração do clipe em segundos (a mesma que o `render_clipes.py` usou), para que `__clipe.dur` exista **antes** de o vídeo carregar — `historia.js` não fica esperando os 200 ms de `:45-47`. O teste confere `data-dur` contra o `ffprobe` do arquivo (±0,05 s).
- **`<video>`**: exatamente `muted playsinline preload="none" disableremoteplayback width="960" height="540" src="video/cena-<passo>.mp4"`. **Sem** `autoplay`, `loop`, `controls`, `poster` (o pôster é o `<img>`: um download só, `loading="lazy"`, e funciona no modo empilhado e sem JS, onde `video{display:none}`). `disableremoteplayback` evita o AirPlay/Cast tomar um vídeo mudo de fundo. `src` **no próprio `<video>`, sem `<source>`**: é o que permite descarregar (`removeAttribute('src'); load()`) e recarregar (`src=…; load()`) sem mexer no DOM (§3.2); um formato só, não há o que negociar. Não é focável (sem `controls`), então R-13 fica como está.
- **`<img>` de reserva**: `video/cena-<passo>.webp`, `alt=""`, `width="960" height="540"`, `loading="lazy"` (todas as cenas de clipe estão depois do 1º capítulo). Pôster de verdade pesa ≈20 KB (medido: 19 570 e 21 862 bytes em q75).
- **HUD sai.** Decisão, não opção: (1) o único número que o HUD mostrava — o relógio 11:35→12:11 — já está **pintado na cena** do filme (relógio analógico, ponteiros de 11:35 a 12:11) e **escrito na ressalva** da página ("Medidos: 11:35 → 12:11"); (2) manter um `[data-relogio]` sincronizado por `seek` exigiria uma função `t→texto` por clipe em JS, isto é, conteúdo duplicado fora do HTML (R-12) e um segundo número na tela para o teste sustentar; (3) a `icamento` já era HUD vazio. Somem: os 3 `<div class="hud">`, o CSS `:107-110` e `:70` (a parte `.hud`), e as checagens `check_historia.py:208, :319-323`. A variável `--relogio` fica (a usa `.fundo.tipo .ano`, `:122`).
- **`cena longa`** continua **só** nas três ex-maquetes (`casa`, `icamento`, `zip`): o clipe de 8–10 s cabe em 100vh de rolagem (≈700 px no celular ⇒ 24 fps × 8 s = 192 quadros ⇒ ~3,6 px por quadro), e os capítulos curtos não mudam de altura. `checar_marcacao:220-221` passa a amarrar `longa` a uma lista explícita `LONGAS={"casa","icamento","zip"}`, não ao tipo.
- Quais capítulos viram clipe é da persona 2; a marcação e o teste não dependem disso (`ROTEIRO` diz `("clipe", dur)` por capítulo). Contagem provável: 6 cenas do filme + 3 ex-maquetes = 9 clipes (10 se WhatsApp entrar duas vezes).

### 3.2 JS: `clipes.js` no lugar de `maquetes.js` na história
**Scripts da história**: exatamente `["clipes.js","historia.js"]`, ambos `defer`, nessa ordem (`clipes.js` instala `__clipe` no DOMContentLoaded; `historia.js` chama `seek` a partir daí). `maquetes.js` fica intocado e só no `portfolio.html` (`checar_maquetes_js` continua rodando sobre ele).

**Contrato**: `fig.__clipe = {dur, seek(t), frozen}` — o mesmo formato, novo nome; `historia.js` muda 4 linhas (`'maquete'`→`'clipe'` em `:35, :43, :79`; `__maquete`→`__clipe` em `:44`) e os comentários. `frozen` vira `true` no primeiro `seek` (como hoje) e o harness continua lendo `__clipe.t`.

**Esqueleto de `clipes.js`** (~90 linhas; o que importa está aqui):
```js
(function(){
'use strict';
var figs=[].slice.call(document.querySelectorAll('.palco figure.clipe, figure.clipe'));
if(!figs.length||!('IntersectionObserver' in window))return;
var v0=document.createElement('video');
// ?clipes=nao simula um navegador sem H.264 (harness); economia de dados também fica no pôster
var PODE=!/clipes=nao/.test(location.search)&&v0.canPlayType('video/mp4; codecs="avc1.64001F"')!==''
  &&!(navigator.connection&&(navigator.connection.saveData||/2g/.test(navigator.connection.effectiveType||'')));
var reduzir=matchMedia('(prefers-reduced-motion: reduce)');
var LIMIAR=1/48, TETO=250, LENTOS=3, VOO=600; // s entre seeks que valem; ms de seek lento; seguidos; ms sem 'seeked' = seek perdido

figs.forEach(function(fig){
  var v=fig.querySelector('video'),src=v.getAttribute('src'),dur=parseFloat(fig.dataset.dur)||0;
  var alvo=0,emVoo=0,pendente=false,pronto=false,vivo=false,morto=false,lentos=0;
  var api={dur:dur,frozen:false,seek:function(t){alvo=t;api.frozen=true;pedir();}};
  fig.__clipe=api;
  if(!PODE||!dur)return; // fica a imagem
  function pedir(){
    if(!pronto||morto||fig.hidden||reduzir.matches)return;
    var agora=performance.now();
    if(emVoo&&agora-emVoo<VOO){pendente=true;return;}          // um seek em voo por vez: o último pedido vence
    if(vivo&&Math.abs(v.currentTime-alvo)<LIMIAR)return;         // já está no quadro
    emVoo=agora;pendente=false;v.currentTime=alvo;
  }
  v.addEventListener('seeked',function(){
    var levou=performance.now()-emVoo;emVoo=0;
    if(!vivo){vivo=true;fig.classList.add('viva');}             // só agora a imagem some: há um quadro pronto
    if(levou>TETO&&noBuffer(alvo)){if(++lentos>=LENTOS)return congelar();}else lentos=0; // plano B: aparelho não dá conta
    if(pendente)pedir();
  });
  function noBuffer(t){for(var i=0;i<v.buffered.length;i++)if(t>=v.buffered.start(i)&&t<=v.buffered.end(i))return true;return false;}
  function congelar(){morto=true;vivo=false;fig.classList.remove('viva');}
  function carregar(){
    if(pronto||morto)return;
    if(!v.getAttribute('src'))v.setAttribute('src',src);
    v.addEventListener('loadedmetadata',function(){
      if(!v.seekable.length||v.seekable.end(0)<dur-0.5){congelar();return;} // servidor sem Range: não dá para buscar
    },{once:true});
    v.addEventListener('canplay',function(){pronto=true;pedir();},{once:true});
    v.addEventListener('error',congelar,{once:true});
    v.preload='auto';v.load();
  }
  function descarregar(){if(!pronto)return;pronto=false;vivo=false;fig.classList.remove('viva');v.removeAttribute('src');v.load();}
  new IntersectionObserver(function(es){es[0].isIntersecting?carregar():descarregar();},{rootMargin:'600px 0px'}).observe(fig.closest('.cena')||fig);
  reduzir.addEventListener('change',function(){if(reduzir.matches){vivo=false;fig.classList.remove('viva');}else pedir();});
});
})();
```
Pontos que a implementação deve manter (cada um vira requisito):
- **Seek**: `currentTime` só (sem `fastSeek`, sem `play()` — o clipe **nunca** toca); um seek em voo, o último pedido vence (`pendente`); ignora diferença < 1/48 s (metade de um quadro a 24 fps); se `seeked` não vier em 600 ms, o próximo pedido passa (Safari às vezes engole o evento — a alternativa seria travar para sempre). Não há rAF próprio: quem cadencia é o `scroll`+rAF do `historia.js`.
- **Sem piscar**: a imagem só some (`.viva`) no **primeiro `seeked`**, isto é, quando o vídeo já tem o quadro do progresso atual apresentado; `canplay`/`loadeddata` não bastam (o quadro pronto seria o 0, não o do scroll). A troca é um crossfade de 0,4 s no CSS.
- **Observado é a `.cena`, não a figura**: a figura mora no `.palco` sticky (sempre "perto" de tudo); a distância que interessa é a da seção no fluxo. `rootMargin 600px` para entrar; ao sair da mesma faixa, **descarrega** (`removeAttribute('src'); load()`): no máximo 2–3 clipes decodificáveis por vez, o que protege o limite de elementos de mídia ativos do iOS. Voltar custa zero de rede se o host mandar `Cache-Control` (checar).
- **`hidden` das figuras inativas** continua sendo do `historia.js`; `pedir()` não faz nada em figura `hidden`, e um `video` com `display:none` não ocupa o decodificador. Não há laço de render, logo **não há "pausa fora de vista" a fazer nem guarda de fps**: `matar()` vira `congelar()` (§ plano B), disparado por dado real (3 seeks seguidos > 250 ms *com o alvo já no `buffered`* — se o alvo não estava carregado, a demora é rede, não aparelho, e não conta).
- **Reduced motion**: (1) `historia.js` já sai antes de montar o palco (`:26`), então na carga a página fica empilhada e o vídeo `display:none`; (2) para a **mudança em tempo real**, o CSS (§3.5) esconde o `video` e devolve a imagem *no mesmo instante* sem JS, e o listener `change` só para de pedir seeks (economia) e volta quando desliga.
- **`?clipes=nao`** força o caminho "não sei tocar H.264" (mesmo código que `canPlayType()===''`): é o que o harness usa para testar que a imagem fica visível e o `__clipe` falso manda.

### 3.3 Encode: parâmetros definitivos
```
ffmpeg -y -loglevel error -f image2pipe -framerate 24 -vcodec mjpeg -i - -an \
  -vf scale=960:540 -c:v libx264 -preset slow -crf 28 \
  -g 4 -keyint_min 4 -sc_threshold 0 -bf 0 \
  -pix_fmt yuv420p -profile:v high -level 3.1 -movflags +faststart \
  site/video/cena-<passo>.mp4
```
- **960×540, 24 fps, crf 28, GOP 4 (≤ 5, como decidido), sem B-frames, `scenecut` desligado**, `yuv420p` + High@3.1 (o que todo iPhone decodifica por hardware; 3.1 cobre 1280×720@30, sobra para 960×540@24), `+faststart`. `-tune` não (3 % de ganho não paga a mudança de aparência entre clipes). Render em 1280×720 e `scale` para 960×540, como o `render.py`.
- **Pôster**: `ffmpeg -i quadro.jpg -vf scale=960:540 -c:v libwebp -q:v 75 site/video/cena-<passo>.webp` (≈20 KB).
- **Tetos** (medidos em §2.1): clipe de **8 a 10 s**; **≤ 1,2 MB por clipe**; **≤ 10 MB somando todos os MP4** (com 9–10 clipes); pôster ≤ 60 KB. Se um clipe passar de 1,2 MB, `render_clipes.py` reencoda o mestre daquele clipe com `crf 29`, depois `30`, antes de falhar — automático, sem reabrir a decisão. Nota honesta: quem rola a história inteira num celular baixa ~9 MB (contra 2,67 MB do trailer); é o preço da decisão, mitigado pelo carregamento por proximidade, pelo descarregamento e pelo `saveData`/2g → só pôster.
- **Como o teste checa o GOP** (`check_filme.py --video`, por clipe):
```python
pts=[float(x) for x in run(["ffprobe","-v","error","-select_streams","v","-skip_frame","nokey",
      "-show_entries","frame=pts_time","-of","csv=p=0",mp4]).split()]   # só quadros-chave
tipos=run(["ffprobe","-v","error","-select_streams","v","-show_entries","frame=pict_type","-of","csv=p=0",mp4]).split()
check(max(b-a for a,b in zip(pts,pts[1:]))<=4/24+1e-3, "quadro-chave a cada ≤ 4 quadros")
check("B" not in tipos, "sem B-frames")
check(len(pts)>=len(tipos)/4-1, "quadros-chave ≥ 1/4 dos quadros")
```
(medido no clipe do celeiro: 48 chaves em 192 quadros, `gap max 0.1667` = 4/24, `47 I + 1 I, + 144 P`, zero B.) Mais: `codec h264`, `profile High`, `level ≤ 31`, `960×540`, `yuv420p`, `r_frame_rate 24/1`, duração 8–10,5 s e igual ao `data-dur`, `moov` antes de `mdat` (índice no arquivo), tamanho ≤ 1,2 MB, soma ≤ 10 MB, pôster 960×540 existente ≤ 60 KB e **não em branco** (desvio-padrão dos pixels > 8, para pegar o quadro da varredura — `python3 -c` com o `ffmpeg -f rawvideo` ou `signalstats`).

### 3.4 `render_clipes.py`
- Mesmo motor do `render.py` (Playwright + Chromium do sistema, `ARGS` iguais, JPEG q92 por pipe), **sem tocar** em `render.py`, `historia.mp4` nem `historia.jpg`. Saídas: `site/video/cena-<passo>.mp4`, `site/video/cena-<passo>.webp` e o mestre `filme/saida/clipes/cena-<passo>-1280.mp4` (crf 18, ignorado pelo git), de onde saem as reencodagens de crf sem re-renderizar.
- **`film.html` ganha duas coisas pequenas**: (1) a flag `?limpo` — no `<script>`, `if(/limpo/.test(location.search))document.documentElement.classList.add('limpo')`, com `.limpo #cap,.limpo #hud,.limpo #num,.limpo #cover,.limpo #end,.limpo .tag,.limpo .bar,.limpo .scrim,.limpo #prog,.limpo #wipe,.limpo #fade,.limpo .vig{display:none!important}` — o `renderAt` continua escrevendo nos elementos, só não aparecem; (2) **`window.renderCena(i, t)`**: mostra `SC[i]`, restaura `sun.position`, `st.run(t)`, `camAt(st,t,T)` com `T=t*DUR/10` e `R.render` — o clipe não depende de `ORDER`/`START`, e as **3 cenas portadas das maquetes entram como `SC[9..11]` sem entrar em `ORDER`**, então o trailer (que continua no projeto) não muda. Todo tempo local `t` continua 0..10 (é o que `st.run` e `st.cam` esperam); a duração real em segundos é o que estica.
- **Tabela única** `CLIPES = {"origem": (0, 8.0), "obra": (1, 8.0), "ferramentas": (6, 8.0), "sige": (3, 8.0), "escala": (7, 8.5), "whatsapp": (2, 8.5), "casa": (9, 10.0), "icamento": (10, 10.0), "zip": (11, 10.0)}` — `passo → (índice em SC, segundos)`; é importada por `check_historia.py` para conferir que todo capítulo `("clipe", dur)` do `ROTEIRO` existe aqui com a mesma duração. Os índices/pares finais são da persona 2; o formato não muda.
- Por clipe: `n=round(dur*24)`; para `i` em `0..n-1`: `renderCena(k, 10*i/n)` → screenshot JPEG → pipe. **Pôster em `t = 0,55·dur`** (o assunto já montado, sem ser o último quadro): o pôster serve o modo empilhado/reduzido, onde é a única imagem; no modo cenas ele raramente aparece (o clipe carrega a 600 px) e, quando aparece, a troca é crossfade.
- **Tempo**: 9 clipes × ~9 s × 24 fps ≈ 1 950 quadros × 0,3 s ≈ **10 min** (10 clipes ≈ 11 min); o encode `preset slow` de 8 s leva ~5 s por clipe. `--so <passo>` renderiza um clipe só (para iterar numa cena).
- **9:16, se a persona 2 pedir**: não agora. Hoje o recorte é CSS (`object-fit:cover; object-position:68% 53%` — §1); num viewport 390×700 o `cover` mostra a faixa 52–84 % da largura, onde está o assunto. Se for pedido: `?limpo&retrato` faz `R.setSize(540,960,false); cam.aspect=9/16; cam.clearViewOffset(); cam.fov=50; cam.updateProjectionMatrix()` e o `<canvas>` 540×960; sai `cena-<passo>-retrato.mp4` e `clipes.js` escolhe o `src` na carga por `matchMedia('(orientation: portrait)')` (o atributo `media` em `<source>` de vídeo não existe mais na spec). Dobra o render e o peso publicado — por isso só sob pedido.

### 3.5 CSS
Substitui `index.html:104-110` e ajusta `:70-71`:
```css
/* modo empilhado: o clipe não existe; fica a imagem */
.fundo video{display:none}
/* modo cenas: o vídeo cobre o palco e recebe o mesmo filtro da foto; a imagem só some quando há quadro pronto (.viva) */
.js-historia .palco .fundo video{display:block;position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:68% 53%;filter:brightness(.6) saturate(.85);opacity:0;transition:opacity .4s}
.js-historia .palco .fundo.viva video{opacity:1}
.js-historia .palco .fundo.viva img{visibility:hidden}
@media (prefers-reduced-motion: reduce){
  .js-historia .palco .fundo,.js-historia .palco .fundo video{transition:none}
  .js-historia .palco .fundo video{display:none}          /* mudança em tempo real: some na hora, sem JS */
  .js-historia .palco .fundo.viva img{visibility:visible}
}
```
- **Filtro igual ao da foto** (`brightness(.6) saturate(.85)`): o contraste do texto continua vindo só da faixa `--scrim` (R-14, `checar_css`), e o clipe escurecido não compete com a frase. `filter` em `<video>` custa uma passada de composição por quadro; em 960×540 é barato, e some se der problema (o teste não o exige no vídeo).
- `object-fit:cover` + `object-position:68% 53%` (assunto do `setViewOffset`). Nada de `100dvh`; `100vh`/`100svh` do `.palco` e das `.cena` não mudam; o `overflow:clip` do `<main>` (`:99`) **continua** — é ele que corta o palco sticky no fim da história (F-07), e a ficha agora vem logo depois do `</main>`.
- Somem `.fundo canvas`/`.hud`/`.pausa` das regras `:70-71` e o bloco `:104-110`; `--relogio` fica.
- **CLS/LCP**: o 1º capítulo (`tese`) continua foto com `fetchpriority=high` + preload (`:17`); nenhum clipe está na primeira dobra e todo `<video>`/`<img>` tem `width`/`height`, então **o LCP não muda e o CLS continua 0**. O que muda no orçamento inicial: `clipes.js` (~4 KB) no lugar de `maquetes.js` (~19 KB) e nenhum `import()` de three.js (≈650 KB) na história.

### 3.6 Testes
**`check_historia.py`**
- `ROTEIRO`: tipo novo `("clipe", dur)` nos capítulos que viram clipe (`casa`, `icamento`, `zip` deixam de ser `"maquete"`); docstring de `cap()` atualizada. Constante `LONGAS={"casa","icamento","zip"}`; `checar_marcacao:220-221` passa a usar `passo in LONGAS`.
- `checar_fundo` para `"clipe"`: classe exata `fundo clipe`; `data-dur` = `dur`; sem `data-cena`; 1 `<video>` com atributos exatamente `muted`, `playsinline`, `preload="none"`, `disableremoteplayback`, `width="960"`, `height="540"`, `src="video/cena-<passo>.mp4"` e **sem** `autoplay|loop|controls|poster|<source>`; 1 `<img src="video/cena-<passo>.webp" alt="" width="960" height="540" loading="lazy">`; os dois arquivos existem; `ffprobe` do MP4 = `data-dur` ±0,05; **nada de `<canvas>`, `.hud`, `data-relogio`** em lugar nenhum de `index.html`. Importa `CLIPES` de `filme/render_clipes.py` e confere `passo` presente e `dur` igual.
- `checar_css`: tira `:304` (`.pausa`) e `:319-323` (HUD); exige `.fundo video{display:none}`, a regra `.js-historia .palco .fundo video{…object-fit:cover…}`, `.viva img{visibility:hidden}`, o bloco `@media (prefers-reduced-motion: reduce)` com `video{display:none}`, e que `filter:brightness(.6) saturate(.85)` esteja na regra da `img` (como hoje). Continua: sem `dvh`, `svh` com `vh` antes, `.palco{display:none}`, tinta, `scroll-margin`, contraste do `--scrim`.
- `checar_scripts`: `["clipes.js","historia.js"]`, `defer`, sem inline.
- `checar_js` (`historia.js`): lista de proibidos igual (`fps`/`matar` continuam proibidos), mais `__maquete` e `'maquete'` (o nome antigo não pode sobrar). **Novo `checar_clipes_js`**: proíbe `play(`, `autoplay`, `fastSeek`, `requestAnimationFrame`, `scrollTo|scrollBy|scrollIntoView|preventDefault|'wheel'|'touchmove'`, `createObjectURL`/`fetch(`; exige `canPlayType`, `'seeked'`, `seekable`, `rootMargin:'600px`, `preload='auto'`, `.load()`, `removeAttribute('src')`, `prefers-reduced-motion: reduce` + `'change'`, `saveData`, `clipes=nao`, `250` e `3` como constantes do plano B (`TETO=250`, `LENTOS=3`).
- `checar_maquetes_js` fica (é do portfólio); ganha a checagem de que `portfolio.html` continua com `<script src="maquetes.js" defer>` e as duas `figure.maquete` (`36min`, `casa-viaja`).
- **Harness `historia_teste.html`**: abre `../site/index.html?clipes=nao`; `figure.maquete`→`figure.clipe`, `__maquete`→`__clipe` (falso `{dur:1000,t:null,seek}`), `maquetesVisiveis`→`clipesVisiveis` (`.palco .clipe:not([hidden])`); a linha `img P=visible` continua (agora significa "sem H.264, a reserva fica"); `seek≈500/seek25≈250`, `progresso`, reversão, `seek-tardio zip`, 320 px, salto pela régua, reduzido (`js-historia=false`, `palco-filhos=0`, 17 frases) — todos iguais. `--disable-3d-apis` pode ficar (inócuo) — decisão: fica, para o harness não depender de nada de mídia.
- **`checar_maquete_real` vira `checar_clipe_real`**: sobe um servidor **com `Range`** (a classe `H` do §2.4, ~20 linhas no próprio `check_historia.py`, no lugar de `http.server` dentro de `chromium()` — o harness não se importa e o clipe precisa), abre `site/index.html` sem flags de 3D, rola até 40 % da cena `icamento` e espera ≤ 25 s por `fig.classList.contains('viva') && __clipe.frozen`; lê `video.readyState>=2`, `video.seekable.end(0)>=dur-0.5`, `|video.currentTime − 0.4·dur·0.999| ≤ 0.15`; rola a 75 % e confere que `currentTime` mudou para ≈0,75·dur; confere `img` `visibility:hidden` e `video` `opacity:1`; `window.__erros` vazio (espião igual ao de hoje, filtrando `clipes:`). **Mais a prova do GOP no navegador**: injeta 30 seeks (um por rAF, sem esperar) no clipe carregado e exige **≥ 20 `seeked`** e mediana de latência ≤ 40 ms — com GOP 250 medi 3/30 e 77 ms; com GOP 4, 29/30 e 11 ms. E o negativo: `?clipes=nao` na mesma página real → nenhum request `.mp4` em `performance.getEntriesByType('resource')`, `img` visível.
- `checar_reduzido_real` (novo, barato): Chromium com `--force-prefers-reduced-motion` em `site/index.html` real → zero requests `.mp4`, `getComputedStyle(video).display==='none'`.
- `checar_filme` e `checar_fim_do_palco` **saem**; a parte da ficha vira `checar_ficha_a_vista()` (390 e 1280 px: rola ao fim, `.ficha` `visivel` e não coberta pelo palco — F-07) e `checar_marcacao` ganha: sem `<section class="filme">`, sem `href="#filme"`, sem `video/historia.mp4` no HTML; `checar_texto:280-281` perde a exceção da duração do vídeo.

**`check_filme.py --video`**: deixa de checar `historia.mp4`/`historia.jpg` e passa a iterar `site/video/cena-*.mp4` com as checagens do §3.3, exigindo que o conjunto de `cena-*.mp4` seja exatamente o conjunto de capítulos `"clipe"` do `ROTEIRO` (nem arquivo órfão, nem capítulo sem arquivo). A checagem de texto (`CAPS` × `CAPITULOS`, literais × `portfolio.html`) continua igual — o `film.html` com `SC[9..11]` novos entra nela de graça (todo literal do script é lido).

### 3.7 Risco iPhone: o que fica provado aqui e o que não
**Provado no Chromium headless (e vale para Chrome Android, mesmo motor)**: seek por `currentTime` obedece com servidor `Range`; GOP 4 dá seeks de ~11 ms por software e 29/30 numa rajada; `seeked` dispara por seek; `canplay` chega com `preload="none"`+`load()`; a troca imagem→vídeo só no primeiro `seeked`; `?clipes=nao` e reduced-motion ficam no pôster sem baixar nada.

**Em aberto (precisa de um iPhone)**: (1) latência real do decodificador de hardware do iOS num seek pausado com GOP 4 — a literatura diz que o Safari "recria os delta frames" e é o navegador que melhor se comporta (muffinman), mas ninguém mediu *este* encode; (2) se o iOS honra `preload='auto'`+`load()` sem gesto para vídeo `muted playsinline` (os guias de lazy-load contam com isso; a doc antiga da Apple dizia que o iOS ignora `preload` em rede celular — se ignorar, `canplay` não vem e a página **fica no pôster**, que é o comportamento degradado desejado, não um erro); (3) quantos `<video>` com `src` o Safari mantém decodificáveis — o descarregamento fora dos 600 px limita a 2–3; (4) `seeked` engolido — coberto pelo `VOO=600 ms`.

**Plano B (barato, já no código)**: 3 seeks seguidos > 250 ms *com o alvo no `buffered`* → `congelar()`: a figura volta ao pôster e não pede mais seeks; a página continua inteira (texto + imagem), sem laço rodando. Plano C, se o iPhone mostrar que nem isso basta: `clipes.js` trata `navigator.maxTouchPoints>1 && /iPhone/.test(navigator.userAgent)` como `PODE=false` — uma linha, sem mudar marcação.

## 4. Requisitos para o plano e como verificar

- **P4-01 (MUST)** — Cada capítulo de clipe tem exatamente a `<figure class="fundo clipe" data-passo data-dur aria-hidden="true">` do §3.1: `<video muted playsinline preload="none" disableremoteplayback width="960" height="540" src="video/cena-<passo>.mp4">` (sem `autoplay|loop|controls|poster|<source>`) + `<img src="video/cena-<passo>.webp" alt="" width="960" height="540" loading="lazy">`; nada de `<canvas>`, `.hud`, `data-relogio`, `data-legenda`, `data-cena` em `index.html`. *Verificar*: `checar_fundo` tipo `"clipe"` + `grep -c 'data-relogio\|<canvas\|class="hud"' site/index.html` = 0.
- **P4-02 (MUST)** — `data-dur` = duração do MP4 (`ffprobe`, ±0,05 s) = `CLIPES[passo][1]` de `render_clipes.py` = `ROTEIRO`. *Verificar*: `checar_fundo` importa `CLIPES` e roda `ffprobe`.
- **P4-03 (MUST)** — Scripts da história: exatamente `["clipes.js","historia.js"]`, `defer`, sem inline; `portfolio.html` continua com `maquetes.js` e as duas `figure.maquete`, e `maquetes.js` não muda. *Verificar*: `checar_scripts`; `git diff --stat` do commit não toca `site/maquetes.js`; `checar_maquetes_js` estendido.
- **P4-04 (MUST)** — Contrato `fig.__clipe={dur,seek,frozen}`; `historia.js` muda só `maquete→clipe`/`__maquete→__clipe` (4 linhas + comentários) e continua sem `scrollTo|scrollBy|scrollIntoView|preventDefault|'wheel'|'touchmove'|aria-live|fps|matar|__maquete`. *Verificar*: `checar_js`; `check_historia.py --navegador` com o harness renomeado passa (`seek≈500`, `seek25≈250`, `seek-tardio zip`, reversões, régua, 320 px, reduzido).
- **P4-05 (MUST)** — `clipes.js` seeka só por `currentTime`, um em voo por vez com o último pedido vencendo, ignora Δ < 1/48 s, libera após 600 ms sem `seeked`, nunca chama `play()`, `fastSeek`, rAF próprio, `fetch`/`createObjectURL`. *Verificar*: `checar_clipes_js` (proibidos/exigidos do §3.6).
- **P4-06 (MUST)** — A imagem de reserva só some (`.viva`) depois do primeiro `seeked` do clipe; antes disso e em `congelar()`/reduced-motion ela está visível. *Verificar*: `checar_clipe_real` (`img visibility:hidden` só com `viva`), harness `img P=visible` com `?clipes=nao`.
- **P4-07 (MUST)** — Carregamento: `preload="none"` no HTML; `clipes.js` observa a **`.cena`** com `rootMargin:'600px 0px'`, carrega com `preload='auto'`+`load()` ao entrar e descarrega (`removeAttribute('src')`+`load()`) ao sair; sem H.264 (`canPlayType`), com `?clipes=nao`, com `saveData`/2g ou sem `seekable` completo, não carrega/não seeka. *Verificar*: `checar_clipes_js`; `checar_clipe_real` negativo (zero `.mp4` em `performance.getEntriesByType('resource')` com `?clipes=nao`).
- **P4-08 (MUST)** — Reduced motion: na carga, empilhado e `video{display:none}` (já é do `historia.js:26`); em tempo real, o `@media (prefers-reduced-motion: reduce)` esconde o `video` e mostra a `img` sem JS, e `clipes.js` ouve `change` para parar/voltar. *Verificar*: `checar_css` (bloco `@media` com `video{display:none}` e `.viva img{visibility:visible}`), `checar_reduzido_real` (zero `.mp4`, `display none`), `grep "'change'" site/clipes.js`.
- **P4-09 (MUST)** — Plano B: 3 seeks seguidos > 250 ms com o alvo em `buffered` → `congelar()` daquela figura (pôster, sem mais seeks); `seekable` vazio/incompleto ou `error` → `congelar()`. *Verificar*: constantes `TETO=250`, `LENTOS=3` presentes; teste unitário no harness real: monkeypatch de `performance.now` não é viável — cobrir com o negativo de `seekable` (servidor sem `Range` no `chromium()` antigo: `viva` **nunca** aparece e `img` fica visível).
- **P4-10 (MUST)** — Encode por clipe: H.264 High ≤ 3.1, 960×540, 24 fps, `yuv420p`, GOP ≤ 4 quadros (gap máx. entre chaves ≤ 4/24 s), zero B-frames, `+faststart` (`moov` antes de `mdat`), 8–10,5 s, ≤ 1,2 MB; soma dos `cena-*.mp4` ≤ 10 MB; pôster WebP 960×540 ≤ 60 KB e não em branco; conjunto de arquivos = conjunto de capítulos `"clipe"`. *Verificar*: `check_filme.py --video` (§3.3).
- **P4-11 (MUST)** — `render_clipes.py` não escreve em `site/video/historia.*`, não altera `render.py`; `film.html` ganha só `?limpo` e `window.renderCena(i,t)`; as cenas portadas das maquetes são `SC[9..11]` fora de `ORDER` (o trailer não muda: `check_filme.py` sem `--video` continua verde e `renderAt` intacto). *Verificar*: `git diff` de `film.html` restrito a esses blocos; `python3 check_filme.py`.
- **P4-12 (MUST)** — CSS do §3.5: `.fundo video{display:none}` no empilhado; no palco `video` absoluto, `object-fit:cover`, `object-position:68% 53%`, `filter` igual ao da foto, `opacity` por `.viva`; `overflow:clip` do `<main>` mantido; sem `dvh`. *Verificar*: `checar_css`; `checar_ficha_a_vista` (F-07) em 390 e 1280 px.
- **P4-13 (MUST)** — O servidor que publica `site/video/` responde a `Range` (`206`, `Accept-Ranges: bytes`) — sem isso o Chrome ignora todo seek (§2.4). *Verificar*: `check_site.py`/deploy: `curl -sI -H 'Range: bytes=0-1' <url>/video/cena-zip.mp4 | grep -i '206\|accept-ranges'`; e o `chromium()` de teste passa a servir com `Range`.
- **P4-14 (SHOULD)** — `checar_clipe_real` prova o GOP no navegador: 30 seeks um por rAF → ≥ 20 `seeked`, mediana ≤ 40 ms (limiares folgados: GOP 4 deu 29/30 e 11 ms; GOP 250, 3/30 e 77 ms). *Verificar*: o próprio teste; reencodar um clipe com `-g 250` deve fazê-lo falhar.
- **P4-15 (SHOULD)** — Peso inicial: nenhum `.mp4` nem `three.module.js` é requisitado antes de a cena de clipe mais próxima entrar nos 600 px; LCP continua a foto da `tese`. *Verificar*: no `checar_clipe_real`, ler `performance.getEntriesByType('resource')` logo após o load em `scrollY=0`: zero `.mp4`, zero `three`.
- **P4-16 (COULD)** — `--so <passo>` no `render_clipes.py` e reencode automático crf 28→30 quando o clipe passa de 1,2 MB. *Verificar*: rodar `--so zip` gera só `cena-zip.*`.

## 5. Riscos e armadilhas

- **Servidor sem `Range`** é o pior, porque é silencioso: tudo "carrega", `seeked` dispara, e a cena fica parada no quadro 0 — no teste local (`http.server`) e potencialmente no host. Por isso `clipes.js` lê `seekable` e o teste/deploy exigem `206`.
- **Pôster tirado na varredura**: qualquer instante a ±0,5 s de uma fronteira de `START[]` sai bege; com `?limpo` a varredura some, mas o pôster em `0,55·dur` é a garantia, e o teste rejeita imagem sem variância.
- **Trocar a imagem em `canplay`/`loadeddata`** (o padrão dos guias) mostra o quadro 0 antes do quadro do scroll: pisca. A troca é no primeiro `seeked`.
- **Empilhar seeks** (um `currentTime=` por rAF sem controle) faz o navegador descartar os intermediários — no GOP 250 medi 3 de 30; mesmo com GOP 4, uma rajada no iOS pode enfileirar. Um em voo, último vence.
- **rVFC como "quadro apresentado"**: não dispara a cada seek pausado (26 de 40 aqui) — usá-lo como gatilho da troca deixaria a imagem presa às vezes.
- **`filter` no `<video>`** custa composição por quadro em GPU fraca; se um Android de entrada gaguejar, tirar o `filter` do vídeo e deixar só a `--scrim` (o contraste do texto não depende do filtro).
- **Memória do iOS** com 9–10 `<video>`: mitigado pelo descarregamento fora dos 600 px; se ainda faltar, reduzir a faixa de descarga para 300 px — nunca deixar todos com `src` carregado.
- **`data-dur` divergente** do arquivo (reencode com outra duração) faz o `0.999·dur` seekar além do fim: o teste amarra `data-dur` ↔ `ffprobe` ↔ `CLIPES`.
- **`casa` em 10 s**: hoje a maquete conta 36 s (3 viagens + telhado); comprimir é decisão de conteúdo da persona 2/3. O teto de 10 s é técnico (peso e quadros por px); se a persona 2 precisar de 12 s, o teto sobe para 1,4 MB nesse clipe e nada mais muda.
- **Chrome Android ≠ Safari iOS**: o headless prova o Chrome; o Safari tem `fastSeek`, rVFC (15.4+), e comportamento de `preload` próprio. O caminho degradado (pôster) é o mesmo em todos, então o pior caso é "sem movimento", não "quebrado".

## 6. Fontes

- [muffinman.io — Scrubbing videos using JavaScript](https://muffinman.io/blog/scrubbing-videos-using-javascript/) — `keyint=10:scenecut=0`, Safari "recria os delta frames", 845 KB (keyframe a cada 5) × 146 KB (a cada 100).
- [Yoann Gueny — The secrets for an optimized scroll-based HTML5 video](https://blog.yoanngueny.com/the-secrets-for-an-optimized-scroll-based-html5-video/) — intervalo de keyframe 72 (padrão do Media Encoder) trava; "1 é o melhor, mas o peso sobe muito"; só seekar quando |Δt| > 0,1 s.
- [Abhishek Ghosh — Playing with video scrubbing animations on the web](https://www.ghosh.dev/posts/playing-with-video-scrubbing-animations-on-the-web/) — no celular, sem encode para seek rápido, "nenhum quadro atualiza enquanto a rolagem está em movimento".
- [Apple Technical Q&A QA1820 — smooth scrubbing with seekToTime](https://developer.apple.com/library/content/qa/qa1820/_index.html) — não empilhar seeks; emitir o próximo só quando o anterior completar, com tolerância zero para precisão.
- [MDN — HTMLMediaElement.fastSeek()](https://developer.mozilla.org/en-US/docs/Web/API/HTMLMediaElement/fastSeek) — "If you need to seek with precision, you should set currentTime instead"; disponibilidade limitada.
- [caniuse — HTMLMediaElement.fastSeek](https://caniuse.com/mdn-api_htmlmediaelement_fastseek) — Chrome não suporta; Safari 8+, iOS 8+, Firefox 31+.
- [web.dev — Perform efficient per-video-frame operations (rVFC)](https://web.dev/articles/requestvideoframecallback-rvfc) — `mediaTime`/`presentedFrames`; Chrome 83+, Firefox 132+, Safari 15.4+.
- [caniuse — requestVideoFrameCallback](https://caniuse.com/mdn-api_htmlvideoelement_requestvideoframecallback) — Safari/iOS 15.4 (2022-03-14).
- [video.js PR #7854 — No requestVideoFrameCallback on Safari with DRM](https://github.com/videojs/video.js/pull/7854) — rVFC quebrado no Safari em certos casos; fallback por rAF.
- [web.dev — Lazy loading video](https://web.dev/articles/lazy-loading-video) — `preload="none"` + `poster` + `muted loop playsinline`, IntersectionObserver liga o carregamento.
- [ImageKit — A comprehensive guide to lazy loading HTML videos](https://imagekit.io/blog/lazy-loading-html-videos/) — sem `preload="none"`, "Firefox e Safari frequentemente carregavam vídeos curtos inteiros"; `load()` sobrepõe o `preload="none"`.
- [Apple Developer Forums 693447 — iOS 15 Safari blob url on video.src causes memory leak](https://developer.apple.com/forums/thread/693447) — blob como `src` recarrega sem parar e estoura memória (iOS 15.0–15.3).
- [WebKit bug 232076 — Safari on iOS cannot play a video from data uri or blob](https://bugs.webkit.org/show_bug.cgi?id=232076).
- [WHATWG html #11605 — A way to make autoplay respect prefers-reduced-motion](https://github.com/whatwg/html/issues/11605) — "in all browsers `<video autoplay muted>` will auto play even if the user has indicated they prefer reduced motion".
- [Scott O'Hara — Reduced motion auto-playing videos and background animations](https://www.scottohara.me/note/2019/07/12/reduced-motion-video.html) — `matchMedia('(prefers-reduced-motion)')`, checar no load, `addListener` para mudança.
- [Smashing Magazine — Respecting users' motion preferences](https://www.smashingmagazine.com/2021/10/respecting-users-motion-preferences/) — `matchMedia` + `addEventListener('change')`.
- [MDN — HTMLMediaElement: seeked event](https://developer.mozilla.org/docs/Web/API/HTMLMediaElement/seeked_event) — dispara quando o seek completa e `seeking` volta a `false`.
- Medições locais (23/09/2026, Chromium 152.0.7977.64 headless, ffmpeg 6.1.2, SwiftShader): tabela do §2.1; §2.2 (latências e rajada); §2.4 (`seekable=[0,0]` sem `Range`); tamanhos de pôster.
