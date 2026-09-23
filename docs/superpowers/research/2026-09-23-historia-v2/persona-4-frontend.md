# Persona 4 — Tiago (rodada 2)

## Arquitetura recomendada

Base: o que a rodada 1 pediu (`historia.html` + `historia.js` separados) **não é o que existe hoje**. A história virou a própria `portfolio/site/index.html` (o antigo portfólio virou `portfolio.html`); `historia.js` e `maquetes.js` seguem como arquivos à parte, carregados nessa ordem com `defer`. Toda a arquitetura abaixo parte do código real, não da proposta da rodada 1.

**O que já funciona e não deve ser reconstruído.** `historia.js` já mantém um estado genérico (`window.Historia = {ativa, progresso}`), um único `IntersectionObserver` sobre `.cena[data-passo]` com `rootMargin:'-45% 0px -45% 0px'` para achar a cena no centro da tela, e um único listener de `scroll` (com `requestAnimationFrame`) que chama `sincronizar()` — a mesma função que já lê `fig.__maquete` e chama `seek()`. Isso importa porque **a régua e os links de capítulo da rodada 2 não precisam de nenhum observer ou listener novo**: eles só precisam ler `H.ativa` e se pendurar nas mesmas duas funções que já existem (`ativar(passo)` e `sincronizar()`).

**Régua de tempo — onde ela mora.** Em vez de criar uma segunda barra `position:sticky` (que teria de coordenar seu próprio offset com `.barra` e com `.palco`, os três competindo por `top:0`), a régua entra como **filho estático de `.palco`**, com `position:absolute` e `z-index` acima das camadas `.fundo` — exatamente o mesmo padrão que o HUD do relógio (`.hud`) já usa hoje dentro de cada `.fundo`. Vantagens: (1) `.palco` já é `sticky` e já para de "grudar" sozinho no fim de `main#historia` (o truque `margin-bottom:-100vh` já resolve isso); a régua herda esse comportamento de graça; (2) `historia.js` só faz `palco.appendChild(f)` para os `.fundo` — como a régua não é um `.fundo`, ela nunca é movida ou duplicada por esse código, mesmo sem tocar em `historia.js` na parte de montagem; (3) zero coordenação de altura entre duas barras sticky independentes.

Conteúdo da régua: uma trilha horizontal fina com marcas fixas (2017 · 2022 · 2025 · 2026, a linha do tempo confirmada em `00-contexto.md`), um indicador de progresso (posição = progresso geral da página, não o `progresso()` por-cena que já existe — este é um cálculo novo e simples: `scrollY / (scrollHeight - innerHeight)`), e um rótulo textual da data do capítulo ativo (ex.: "ago/2026"). **Nem toda marca corresponde a um capítulo clicável**: a linha do tempo tem 2022 (UNIFEI/DCE/InLoco Jr.) mas o roteiro atual de 10 cenas não tem nenhum `data-passo` datado em 2022 — a marca de 2022 fica como referência inerte (não un `<a>`) até que exista uma cena para ela; decisão de conteúdo, fora do escopo deste front-end, mas a régua precisa suportar os dois casos (marca com link e marca sem link) sem quebrar.

**Como a régua sabe o capítulo atual.** Não por conta própria. `ativar(passo)` (já existe em `historia.js`) ganha uma linha a mais no fim: atualizar `data-atual` na régua e o texto do rótulo de data, usando um mapa capítulo→data que já pode ser derivado 1:1 da tabela do `00-contexto.md`. `sincronizar()` (já existe, já roda por `rAF` a cada scroll) ganha uma linha a mais: mover o indicador de progresso (`style.transform`) usando o cálculo de progresso geral. Nenhuma das duas funções ganha um observer ou listener novo — só mais um efeito colateral pequeno dentro do que já dispara.

**Hash da URL: opcional, e só com `replaceState`.** Atualizar `location.hash` para refletir o capítulo ativo é debatido, mas viável *desde que* (a) use sempre `history.replaceState` — nunca `pushState`, porque cada capítulo trocando o hash com `pushState` empilha ~10 entradas de histórico numa única rolagem, e o botão "voltar" do usuário fica preso dentro da própria página (anti-padrão clássico de scrollytelling); (b) só dispare na troca de capítulo (dentro de `ativar()`, não a cada frame de `sincronizar()`); (c) nunca dispare no primeiro paint (evita um `replaceState` fantasma antes de qualquer rolagem real). `replaceState` sozinho nunca rola a página nem move foco — por isso não viola "rolagem nativa" —, mas também não é garantido atualizar `:target` de forma confiável entre navegadores; a régua não deve depender de `:target` para saber "qual é o ativo", só do estado já mantido em `H.ativa`.

**Links de capítulo ("ver o caso completo →").** São `<a href="portfolio.html#ancora">` comuns, um por capítulo datado, reaproveitando exatamente as âncoras já publicadas em `00-contexto.md` (`#orcamento`, `#sistema`, `#sige`, `#modular`, `#obra`, `#ferramentas`, `#curriculo`, `#contato`) — sem inventar âncora nova. Vivem dentro do `.texto` de cada `.cena`, perto da `.ressalva`, não na régua. Navegação de página inteira: zero risco de scroll-jacking por definição.

**Deep-link para um capítulo dentro da própria história.** Hoje os `id` das seções são genéricos (`c1`…`c10`); o skip-link (`<a class="pular" href="#c1">`) depende disso. Trocar para `id` semântico igual ao `data-passo` (`id="origem"`, `id="casa"`, `id="icamento"`) é uma renomeação de baixo risco, mas exige atualizar o skip-link junto. Com isso, tanto a régua (para as marcas clicáveis) quanto um link externo (ex.: `portfolio.html` linkando de volta para um capítulo específico) podem apontar para `#icamento` e o navegador rola nativamente até lá — desde que `scroll-margin-top` no alvo compense a soma das alturas de `.barra` + régua. Como a régua vive *dentro* de `.palco` (que é `100vh`/`100svh`, não uma barra fina no fluxo), o offset a compensar na prática é só a altura de `.barra` (a régua não empurra layout, é overlay absoluto) — mas se a régua alguma hora ganhar uma versão "fora do palco" (ex.: no modo empilhado sem JS, como uma lista simples), essa segunda forma não deve reservar `scroll-margin-top` alguma, porque nesse modo não há `sticky` disputando espaço.

**Modo empilhado (sem JS / `prefers-reduced-motion`).** A régua "viva" (indicador que se move, hash que atualiza) não deve existir nesse modo — ela é 100% dependente de `historia.js` rodando. O que precisa sobreviver sem JS é só a **data de cada capítulo em texto plano**, já dentro do `.texto` de cada `.cena` (ex.: um `<p class="ano">2022</p>` antes da frase) — isso é HTML/CSS puro, sempre presente, e é o que dá ao usuário sem JS a mesma informação de "quando" que a régua dá a quem tem JS. `.regua{display:none}` fora de `.js-historia` resolve o resto.

## A terceira maquete (içamento): viabilidade, o que portar, tamanho estimado, como vira CENAS['icamento'] com update(t) e dur

**Viabilidade: alta.** `portfolio/site/vendor/three.module.js` está em `REVISION="186"` (confirmado por `grep` em `three.core.js`) — um salto grande sobre o r128 do estudo (`icamento-3d.html`, three.js via CDN). Mas quase todo o "custo" da migração de API já foi pago: `maquetes.js` já roda em cima do r186 e já resolve, para as duas cenas existentes, exatamente os pontos que mudaram entre r128 e r186:

- **Color management** (r152): `outputEncoding`→`outputColorSpace`, `sRGBEncoding`→`SRGBColorSpace`, `ColorManagement.enabled=true` por padrão. `stage()` em `maquetes.js` não define `outputColorSpace` manualmente porque o padrão do r186 já é `SRGBColorSpace` — e a única textura carregada (`upa-plan-grey.webp` em `cena36`) já seta `tex.colorSpace=THREE.SRGBColorSpace` explicitamente. A cena de içamento não carrega textura nenhuma, então nem esse cuidado é necessário.
- **Luzes fisicamente corretas** (r155, `useLegacyLights` default passa de `true` para `false`, removida de vez até r165): isso muda a intensidade "certa" de `HemisphereLight`/`DirectionalLight`. O estudo original usa `HemisphereLight(...,0.85)` e `DirectionalLight(...,0.9)` — valores calibrados para o modo legado (pré-r155) e escuros demais sob o padrão atual. **Isso não precisa ser portado**: `stage()` já define seu próprio rig de luz (HemisphereLight 1.5, sol DirectionalLight 3.4, `ACESFilmicToneMapping`, `PCFSoftShadowMap`) e as duas cenas existentes o reaproveitam sem redefinir nada. `cenaIcamento` deve fazer o mesmo — se alguém copiar o bloco de luzes do estudo, o resultado fica visualmente errado (escuro) por essa exata razão de versão.
- **`Geometry` removida do core** (r125): já não é um problema — `BoxGeometry`, `CylinderGeometry`, `TorusGeometry`, `ConeGeometry` no estudo já são `BufferGeometry` desde o r128, nenhuma API antiga (`.vertices`/`.faces`) é usada no arquivo.
- Nenhuma renomeação encontrada em `setPixelRatio`, `antialias`, câmera ou `WebGLRenderer` entre r128 e r186 que afete o código do estudo.

**O que portar (geometria/animação) vs. o que descartar (chrome de ferramenta interna).**

Portar: o módulo (chassi + corpo + tampa, 3 `box()` empilhadas — já bate com a assinatura `box(w,h,d,mat,x,y,z,pai)` de `stage()`), os 4 olhais de içamento (`TorusGeometry`, sem helper pronto em `stage()` — vira uma função local `anel()` dentro de `cenaIcamento`, no mesmo estilo de `tree()`/`caixa()`/`boneco()` que `cenaCasa` já define como closures locais), o gancho (outro toro), o cabo principal e os cabos do balancim (`THREE.Line`/`LineBasicMaterial`, com um helper local `cabo(a,b)` — o estudo já tem essa função pronta, só precisa mover para dentro do escopo da cena), a viga do balancim + travessas (mais `box()`).

Descartar: `WebGLRenderer`, `Scene`, `PerspectiveCamera`, luzes, `GridHelper`, chão e névoa manuais (tudo isso é `stage()`); os controles de câmera por ponteiro/roda/toque (`pointerdown`/`pointermove`/`wheel`/`touchmove` — cerca de 15 linhas do estudo) — competiriam com o gesto nativo de rolagem da página, violam a regra "sem scroll-jacking" já estabelecida na rodada 1, e são substituídos pelo mesmo `st.camKeys(CAM,t,wide)` por keyframes que `cena36`/`cenaCasa` já usam; o painel lateral (`#panel`, sliders de comprimento/altura, alternância "Com balancim"/"Cabos direto no gancho") — é uma ferramenta de estudo de engenharia, não faz sentido na história pública; o material `MeshLambertMaterial` vira `mat()` (que já embute `MeshStandardMaterial` com `roughness:.85,flatShading:true`, o padrão visual "low-poly" aprovado nas outras duas cenas).

**Narrativa proposta para `update(t)`.** Em vez do modo comparativo interativo do estudo, uma sequência curta e correta: módulo pousado (chão/carroceria) → balancim desce e os cabos tensionam na vertical → módulo sobe até a posição → breve permanência no alto. Opcionalmente, os primeiros 3–4s podem citar visualmente o "modo errado" (cabos direto no gancho, ângulo comprimindo as paredes — o próprio estudo já calcula esse ângulo e já tem os cones vermelhos de alerta) antes de cruzar para o modo correto, dando à maquete a mesma lógica de "decisão registrada" que already aparece em `cenaCasa` ("37 decisões registradas"). Texto sobreposto (`api.num`/`api.leg`): só puxar números que **já existem no site** — por exemplo "3,8 t" (classe do guindaste, já usado em `cenaCasa`); a altura do içamento na animação é só trajetória visual e não deve aparecer como se fosse uma medida documentada nova (ver P4-09 abaixo).

**Como vira `CENAS['icamento']`.** Uma função a mais no mesmo objeto que já tem `cena36`/`cenaCasa`:

```js
CENAS['icamento'] = cenaIcamento; // linha extra no CENAS existente
```

```js
function cenaIcamento(fig){
  var st=stage(fig,0xBFD3E6,30,90),S=st.S,mat=st.mat,box=st.box;
  var L=3.2,H=2.9,CH=.25,C=10,RESTY=0,LIFTY=2.0,DUR=14;
  function anel(x,y,z){var m=new THREE.Mesh(new THREE.TorusGeometry(.06,.02,8,20),mat(0xF2B233));
    m.rotation.y=Math.PI/2;m.position.set(x,y,z);S.add(m);return m;}
  function cabo(a,b){var g=new THREE.BufferGeometry().setFromPoints([a,b]);
    var l=new THREE.Line(g,new THREE.LineBasicMaterial({color:0xdce6ee}));S.add(l);return l;}
  var mod=new THREE.Group();S.add(mod);
  box(L,CH,C,mat(0x3d5568),0,CH/2,0,mod);
  box(L,H-CH-.08,C,mat(0xd8d4cc),0,CH+(H-CH-.08)/2,0,mod);
  var olhais=[];
  [-1,1].forEach(function(sx){[-1,1].forEach(function(sz){
    var px=sx*(L/2-.1),pz=sz*(C/2-.25);
    anel(px,CH+.12,pz);olhais.push(new THREE.Vector3(px,CH+.12,pz));
  });});
  var balY=H+1.6,cabos=[];
  var balastro=box(L-.1,.22,C-.3,mat(0xe8a13c),0,balY,0,S);
  olhais.forEach(function(o){cabos.push(cabo(new THREE.Vector3(o.x,balY-.1,o.z),o));});
  var CAM=[[0,[16,7,16],[0,1.5,0]],[6,[14,9,10],[0,2,0]],[10,[10,10,6],[0,3,0]],[DUR,[16,7,16],[0,2,0]]];
  var api={dur:DUR,update:function(t,wide){
    var y=lerp(RESTY,LIFTY,seg(t,3,9));
    mod.position.y=y;balastro.position.y=H+1.6+y;
    cabos.forEach(function(c,i){var o=olhais[i];
      c.geometry.setFromPoints([new THREE.Vector3(0,H+1.5+y,o.z),new THREE.Vector3(o.x,CH+.12+y,o.z)]);});
    st.camKeys(CAM,t,wide);
    api.leg=t<9?'Cabos verticais: só tração nos olhais, sem comprimir a parede.':'3,8 t · guindaste da classe certa.';
  }};
  return Object.assign(api,st);
}
```

(esqueleto de referência — falta calibrar geometria/keyframes finos; o ponto é a forma, não os números exatos de posição).

**Tamanho estimado.** `cena36` tem ~50 linhas de código-fonte no estilo denso do arquivo; `cenaCasa` (a maior, com guindaste articulado, caminhão e telhado kit) tem ~93 linhas e pesa cerca de 5,4 KB dentro de `maquetes.js`. `cenaIcamento` é mais simples que as duas (um módulo + um balancim + cabos, sem guindaste articulado, sem leitura de imagem, sem grupo de telhado com kit de montagem) — estimativa de 35–45 linhas, ~2–3 KB adicionados a `maquetes.js`. Sem novo arquivo, sem nova requisição HTTP.

**Encaixe em `index.html`.** Um novo `<section class="cena longa">` com `<figure class="fundo maquete" data-passo="icamento" data-cena="icamento">`, seguindo exatamente o padrão de `c4`/`c8` (canvas, `<img>` de fallback, `.hud`). `historia.js` não precisa de nenhuma mudança — já trata `data-cena` de forma genérica.

## O que a pesquisa diz

- O padrão de painel de capítulo fixo ("giant year, chapter title, running progress dots") do jornalismo longform pina um painel com o ano/título à esquerda enquanto o texto rola à direita — os "dots" de progresso do capítulo comunicam "onde estou" sem o leitor precisar medir a barra de rolagem; em mobile, essa barra lateral costuma colapsar numa faixa fina no topo com `overflow-x:auto` [Scrollytelling in web design — Webflow Blog](https://webflow.com/blog/scrollytelling-guide).
- Um índice (TOC) com barra de progresso por seção — cada entrada preenche conforme a seção correspondente passa pelo viewport — é o padrão citado para "não só em que capítulo estou, mas quanto desse capítulo já passou" [Multi-Section TOC Scroll Progress Tracker — CodeFronts](https://codefronts.com/motion/css-scroll-progress-bar/multi-section-toc-scroll-progress-tracker/).
- `scroll-margin-top` resolve especificamente o problema de um link âncora levar o alvo para debaixo de um cabeçalho fixo/sticky: aplicado no próprio elemento-alvo (`h3{scroll-margin-top:5rem}`), reserva o respiro necessário; a alternativa `scroll-padding-top` faz o mesmo, mas no contêiner de rolagem, e é preferível "quando tudo dentro de um contêiner precisa do mesmo deslocamento" — aqui, como só os `.cena` datados precisam do deslocamento (não a página toda), `scroll-margin-top` no alvo é a escolha certa [Fixed Headers and Jump Links? The Solution is scroll-margin-top — CSS-Tricks](https://css-tricks.com/fixed-headers-and-jump-links-the-solution-is-scroll-margin-top/). Suporte hoje é amplo (Safari adicionou em 14.1/2021) — os relatos de falha em Safari citados em comentários daquele artigo são de 2020, anteriores a esse suporte; vale conferir no caniuse antes de assumir 100%, dado o histórico de regressões do iOS Safari já registrado na rodada 1.
- `:target` estiliza o elemento cujo `id` bate com o fragmento da URL — mas depende de navegação real de fragmento; `history.replaceState` muda a URL sem necessariamente disparar essa recomputação de forma consistente entre navegadores, então não é uma base confiável para "qual capítulo está ativo" [History: replaceState() — MDN](https://developer.mozilla.org/docs/Web/API/History/replaceState).
- Trocar o hash a cada seção rolada é uma prática comum para deep-link e "sincronizar item ativo do menu", mas o cuidado mais citado é usar `replaceState` (não `pushState`) para não empilhar entradas de histórico a cada seção — cada `pushState` por seção rolada vira um "voltar" a mais que o usuário não pediu [history.replaceState Adds Browsing History Entries — xjavascript.com](https://www.xjavascript.com/blog/history-replacestate-still-adds-entries-to-the-browsing-history/).
- `background-blend-mode` mistura camadas de `background-image` (e cor) entre si, com sintaxe posicional (`background-image:url(a),url(b);background-blend-mode:screen,multiply`); `mix-blend-mode` faz o mesmo entre um elemento e o que está atrás dele. Os dois criam um novo contexto de empilhamento, o que precisa ser levado em conta antes de sobrepor uma dessas camadas a um `<canvas>` three.js (que já é seu próprio contexto de composição) [Compositing and Blending in CSS — Sara Soueidan](https://www.sarasoueidan.com/blog/compositing-and-blending-in-css/), [background-blend-mode — MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/background-blend-mode).
- `mask-image` serve para recortar uma forma de transparência customizada (diferente de blend, que mistura cor) — útil para, por exemplo, uma foto entrando com uma borda irregular sobre o render, sem depender de PNG pré-recortado [CSS mask-image: In-Depth Guide — Gerardo Perrucci](https://www.gperrucci.com/blog/css/mask-image).
- Levantamento de 2025 (HTTP Archive) achou mais de 60% dos sites "image-heavy" ainda servindo a mesma imagem para todos os tamanhos de tela, fazendo o mobile baixar imagens 3–8× maiores do que a tela usa — reforça `srcset`/`sizes` com passos de peso de arquivo (não de largura de dispositivo) como o ganho real em 3G/4G de obra, o mesmo público-alvo já identificado na rodada 1 [The Complete Guide to Responsive Images in 2026 — Krunkit](https://krunkit.me/blog/responsive-images-complete-guide).
- Migração de three.js relevante ao portar o estudo de içamento: `outputEncoding`→`outputColorSpace` com `SRGBColorSpace` como padrão desde r152, e `ColorManagement.enabled=true` por padrão [WebGLRenderer: Replace .outputEncoding with .outputColorSpace — PR #25756](https://github.com/mrdoob/three.js/pull/25756), [Migration Guide — three.js wiki](https://github.com/mrdoob/three.js/wiki/Migration-Guide); `useLegacyLights` passa a `false` por padrão em r155 e é removida por completo até r165, mudando a intensidade "correta" de luzes que antes pareciam certas em modo legado [Updates to lighting in three.js r155 — three.js forum](https://discourse.threejs.org/t/updates-to-lighting-in-three-js-r155/53733); `Geometry` foi removida do core em r125, então qualquer geometria no estudo (r128) já nasceu como `BufferGeometry` — nenhuma mudança necessária aqui.

## Trechos de código de referência

**1) Régua como overlay absoluto dentro de `.palco` (reaproveita o mesmo truque do `.hud`)**

```html
<div class="palco" aria-hidden="true">
  <nav class="regua" aria-hidden="true">
    <span class="regua__marca" data-ano="2017">2017</span>
    <span class="regua__marca" data-ano="2022">2022</span>
    <span class="regua__marca" data-ano="2025">2025</span>
    <span class="regua__marca" data-ano="2026">2026</span>
    <b class="regua__indicador"></b>
    <span class="regua__rotulo"></span>
  </nav>
  <!-- historia.js continua só fazendo palco.appendChild(fundo) — a régua não é um .fundo, nunca é movida -->
</div>
```

```css
.js-historia .palco .regua{position:absolute;inset:0 0 auto 0;z-index:2;display:flex;gap:12px;padding:8px 16px;font-family:var(--mono);font-size:.7rem;color:var(--ressalva-cena)}
.js-historia .palco .regua__indicador{position:absolute;left:0;bottom:-2px;height:2px;background:var(--relogio);transition:left .15s linear;width:8px}
```

**2) Extensão mínima de `ativar()`/`sincronizar()` — sem observer novo, sem listener novo**

```js
// dentro de ativar(passo), depois de f.classList.add('ativo'):
var regua=document.querySelector('.regua');
if(regua){
  regua.querySelector('.regua__rotulo').textContent=DATAS[passo]||'';
  if('replaceState' in history && ROLOU) // ROLOU: só depois da 1ª troca real de capítulo
    history.replaceState(null,'','#'+passo);
}
```

```js
// dentro de sincronizar(), sem novo listener: reaproveita o rAF do scroll já existente
var ind=document.querySelector('.regua__indicador');
if(ind){
  var p=scrollY/(document.documentElement.scrollHeight-innerHeight||1);
  ind.style.left=(p*100)+'%';
}
```

**3) `scroll-margin-top` só nos alvos datados, offset vindo de uma única variável**

```css
:root{--offset-topo:56px} /* altura real de .barra; medir 1x, não duplicar o número */
.cena[data-passo]{scroll-margin-top:var(--offset-topo)}
```

**4) Link de capítulo para o portfólio (navegação de página inteira, sem risco de scroll-jacking)**

```html
<p class="ressalva">B-36: vai em duas caixas, em três viagens, com 37 decisões registradas.
  <a href="portfolio.html#modular">Ver o caso completo →</a>
</p>
```

**5) `cenaIcamento` — ver esqueleto completo na seção anterior.**

## Requisitos para o plano

1. **P4-01 — MUST.** A régua e o hash da URL leem só o estado que `historia.js` já mantém (`H.ativa`, mais um cálculo simples de progresso geral de página); nenhum `IntersectionObserver` novo, nenhum `addEventListener('scroll', ...)` novo é criado fora do que já existe em `historia.js`. Testável por `grep -c "addEventListener('scroll'" historia.js` e `grep -c "new IntersectionObserver" historia.js` continuarem em 1 cada.
2. **P4-02 — MUST.** Se o hash da URL for atualizado ao rolar, é sempre via `history.replaceState`, nunca `history.pushState`, e só na troca de capítulo (dentro de `ativar()`), nunca a cada frame de `sincronizar()`. Testável por `grep -c "pushState" historia.js` dar zero, e por teste manual: rolar a história inteira e apertar "voltar" uma vez deve sair da página, não andar capítulo a capítulo.
3. **P4-03 — MUST.** Nenhuma marca da régua nem link "ver o caso completo →" chama `preventDefault`, `scrollIntoView`, `scrollTo` ou move foco por JS; toda navegação entre capítulos (dentro da história ou para o portfólio) é `<a href>` nativo. Testável por revisão de código + rolagem manual por teclado/barra de rolagem continuando livre.
4. **P4-04 — MUST.** No modo empilhado (sem JS ou `prefers-reduced-motion`), a régua "viva" não existe (`display:none` ou nem chega a ser criada); a data de cada capítulo continua visível como texto plano dentro do próprio `.texto` daquela cena. Testável desligando JS e conferindo que cada cena datada ainda mostra o ano/mês em texto, sem depender de nenhuma barra.
5. **P4-05 — SHOULD.** Os links "ver o caso completo →" usam só âncoras já publicadas em `00-contexto.md` (`#orcamento`, `#sistema`, `#sige`, `#modular`, `#obra`, `#ferramentas`, `#curriculo`, `#contato`); nenhuma âncora nova é inventada sem checar que existe em `portfolio.html`. Testável por `grep -o 'portfolio.html#[a-z]*' index.html` comparado à lista fixa.
6. **P4-06 — MUST.** `cenaIcamento` (nova função em `maquetes.js`) não recria `WebGLRenderer`, `PerspectiveCamera`, `HemisphereLight` nem `DirectionalLight` — usa só `stage()` para isso, como `cena36`/`cenaCasa` já fazem. Testável por `grep` dentro do bloco de `cenaIcamento` não encontrar nenhuma dessas quatro chamadas.
7. **P4-07 — MUST.** `cenaIcamento` não tem controle de câmera por ponteiro/roda/toque (o estudo original tem; a história não pode) — câmera só por `st.camKeys(CAM,t,wide)`. Testável por `grep` dentro do bloco de `cenaIcamento` não encontrar `pointerdown`, `wheel` nem `touchmove`.
8. **P4-08 — MUST.** Nenhum texto (`api.num`/`api.leg`) da cena de içamento introduz número que não exista já em `index.html` ou `00-contexto.md` (ex.: "3,8 t" pode ser reaproveitado de `cenaCasa`; uma altura de içamento em metros não documentada, não). Testável comparando toda string literal numérica da nova cena contra os números já presentes no site.
9. **P4-09 — SHOULD.** Fundos compostos (render + tela + foto) usam só CSS (`background-blend-mode`/`mix-blend-mode`/`mask-image`/`object-position` por breakpoint), sem canvas 2D de composição gerado em JS; a imagem final de cada fundo composto é servida com `srcset`/`sizes` de pelo menos duas larguras, não uma única imagem grande com `object-fit`. Testável por `grep` não achar `getContext('2d'` em `historia.js`/`index.html`, e pelas tags `<img>` de fundo composto terem `srcset` com ≥2 candidatos.
10. **P4-10 — SHOULD.** Toda marca da régua correspondente a um ano sem capítulo próprio no roteiro atual (ex.: 2022, se nenhuma cena for criada para UNIFEI/DCE) renderiza como texto inerte, não como `<a>` — a régua precisa suportar marca-com-link e marca-sem-link ao mesmo tempo. Testável por revisão visual/HTML: marcas sem `data-passo` correspondente não são `<a>`.

## Riscos e armadilhas

- **Régua duplicando observers.** A tentação óbvia ao implementar a régua é dar a ela seu próprio `IntersectionObserver` "para simplificar" — isso reintroduz o mesmo risco já documentado na rodada 1 (duas fontes de verdade sobre "qual cena está ativa" podem divergir por um frame, fazendo a régua e o crossfade de fundo mostrarem capítulos diferentes por um instante). A régua deve ser sempre consumidora do `H.ativa` que já existe, nunca produtora do seu próprio estado.
- **`pushState` por capítulo rolado.** É o erro mais comum em régua/scrollspy: cada capítulo virando uma entrada de histórico faz o botão "voltar" do navegador andar capítulo a capítulo em vez de sair da página — frustrante e, em analytics, infla artificialmente "páginas vistas". `replaceState`, sempre.
- **Offset de `scroll-margin-top` como número mágico duplicado.** Se a altura de `.barra` mudar (ela usa `flex-wrap`, então em telas muito estreitas pode virar duas linhas) e o `scroll-margin-top` ficar hardcoded num valor separado, o link de capítulo passa a aterrissar embaixo da barra. Uma única variável CSS (`--offset-topo`), lida nos dois lugares, evita a divergência — mas se a barra realmente puder quebrar em duas linhas, a variável fixa também quebra; vale medir com `ResizeObserver` em vez de assumir um valor fixo, ou simplesmente garantir por CSS que `.barra` nunca quebra linha em telas pequenas (ex.: abreviando os itens de `.acoes`).
- **Blend/mask sobre um `<canvas>` three.js.** `background-blend-mode`/`mix-blend-mode` cria um novo contexto de empilhamento e pede recomposição a cada repintura; se um fundo composto (CSS blend) também precisar sentar em cima ou embaixo de um `<canvas>` que está renderizando a 24+ fps, o custo de composição do navegador soma ao custo do WebGL no mesmo frame. Mitigação: manter o blend/mask só nos capítulos sem maquete 3D; nos capítulos com `<figure class="maquete">`, compor a imagem de fundo previamente (arquivo já composto), não via blend ao vivo.
- **Nem toda marca de ano tem capítulo.** A régua pede quatro marcas (2017 · 2022 · 2025 · 2026), mas o roteiro atual de 10 cenas não tem nenhuma parada em 2022 — se isso não for resolvido no conteúdo (nova cena UNIFEI/DCE) nem no design da régua (marca inerte), a régua vai prometer um capítulo que não existe.
- **`:target` não é uma base confiável de estado.** É tentador usar `:target` para estilizar "o capítulo ativo" via CSS puro — mas como `replaceState` não garante disparar a recomputação de `:target` de forma consistente entre navegadores, isso pode deixar a régua "presa" no primeiro capítulo visualmente enquanto o resto do JS já avançou. A régua deve depender só do estado já mantido por `historia.js`, nunca de `:target`.
- **Versão do three.js: copiar boilerplate do estudo em vez de reusar `stage()`.** Se `cenaIcamento` recriar `WebGLRenderer`/luzes do zero copiando o padrão do estudo (r128, `MeshLambertMaterial`, luzes calibradas para modo legado), o resultado final vai renderizar escuro/errado sob os padrões do r186 vendorizado — não por bug, mas porque a "intensidade certa" de luz mudou de padrão entre as duas versões (r155). É por isso que P4-06 exige reaproveitar `stage()`.
- **Peso de fundo composto em 3 camadas.** Empilhar render + captura de tela + foto sem `srcset` multiplica por três o problema de peso em mobile já levantado na rodada 1 (P4-08 daquela rodada, sobre "só a próxima imagem"). Com fundos compostos, cada capítulo pode ter o triplo do peso de antes se as três camadas forem servidas em resolução única.

## Fontes

- [Scrollytelling in web design: Top examples and tips for getting started — Webflow Blog](https://webflow.com/blog/scrollytelling-guide)
- [Multi-Section TOC Scroll Progress Tracker — CodeFronts](https://codefronts.com/motion/css-scroll-progress-bar/multi-section-toc-scroll-progress-tracker/)
- [Fixed Headers and Jump Links? The Solution is scroll-margin-top — CSS-Tricks](https://css-tricks.com/fixed-headers-and-jump-links-the-solution-is-scroll-margin-top/)
- [Creating a scroll-spy with 2 lines of CSS (scroll-target-group) — una.im](https://una.im/scroll-target-group)
- [History: replaceState() method — MDN](https://developer.mozilla.org/docs/Web/API/History/replaceState)
- [history.replaceState Adds Browsing History Entries — xjavascript.com](https://www.xjavascript.com/blog/history-replacestate-still-adds-entries-to-the-browsing-history/)
- [Compositing and Blending in CSS — Sara Soueidan](https://www.sarasoueidan.com/blog/compositing-and-blending-in-css/)
- [background-blend-mode — MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/background-blend-mode)
- [CSS mask-image: In-Depth Guide to Usage and Best Practices — Gerardo Perrucci](https://www.gperrucci.com/blog/css/mask-image)
- [The Complete Guide to Responsive Images in 2026 — Krunkit](https://krunkit.me/blog/responsive-images-complete-guide)
- [Using responsive images in HTML — MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Guides/Responsive_images)
- [WebGLRenderer: Replace .outputEncoding with .outputColorSpace — PR #25756 (mrdoob/three.js)](https://github.com/mrdoob/three.js/pull/25756)
- [Migration Guide — three.js wiki](https://github.com/mrdoob/three.js/wiki/Migration-Guide)
- [Updates to lighting in three.js r155 — three.js forum](https://discourse.threejs.org/t/updates-to-lighting-in-three-js-r155/53733)
- [Updates to Color Management in three.js r152 — three.js forum](https://discourse.threejs.org/t/updates-to-color-management-in-three-js-r152/50791)
