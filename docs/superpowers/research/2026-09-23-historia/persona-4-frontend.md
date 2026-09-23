# Persona 4 — Tiago, dev front-end de scrollytelling

## Quem é

Tiago é desenvolvedor front-end freelancer, fez reportagens interativas para veículos de jornalismo de dados (linha The Pudding / Reuters Graphics) e curte three.js para maquetes leves. Trabalha sozinho, sem time de build: prefere HTML/CSS/JS direto, sem bundler, porque os projetos que entrega muitas vezes vão para hospedagens estáticas simples (como o Replit deste site). Testa tudo no celular antes de considerar pronto — já apanhou várias vezes de `100vh` pulando com a barra do Safari e de `position: sticky` que "morre" porque um ancestral tem `overflow` diferente de `visible`. Para ele, a régua de qualidade de uma página de scrollytelling é: rolagem nativa (sem `scroll-jacking`), funciona sem JavaScript pesado, funciona sem three.js (com fallback de imagem), e não trava no celular de obra do usuário final.

Ao olhar este repositório, o que mais chama atenção dele é que já existe uma API pronta para amarrar o scroll a uma maquete 3D: `fig.__maquete.seek(t)` em `portfolio/site/maquetes.js`. Ele trataria a página `historia.html` como "só" o esqueleto de scrollytelling + crossfade de cenas em cima do que já existe, sem reescrever a parte 3D.

## Arquitetura que ele recomenda

**Arquivos: `historia.html` + `historia.js`. Sem `historia.css` separado.**

- `historia.html` — marcação da página, com `<style>` inline no `<head>`, do mesmo jeito que `index.html` já faz (CSS inline é a convenção do site, ver `DESIGN.md` §1: "sem framework, CSS inline"). Mantém a página inteira legível e "diffável" num único arquivo, e evita mais uma requisição HTTP numa página que já carrega `three.js` e `maquetes.js`.
- `historia.js` — toda a lógica de passos (IntersectionObserver dos textos, troca de cena/crossfade, cálculo de progresso e chamada de `fig.__maquete.seek(t)`). Justificativa: `maquetes.js` já é um arquivo à parte para a parte 3D; separar o "motor" de scrollytelling do HTML segue o mesmo precedente, deixa `historia.html` só com marcação + estilo, e facilita testar a lógica de passos isoladamente (ex.: simular `scrollY` em Node/jsdom) sem precisar do WebGL. Carregado com `defer`, como script clássico (sem `type="module"`), no mesmo estilo IIFE de `maquetes.js` — sem build, sem import/export.
- Ordem de carregamento em `historia.html`: `vendor/three.js` → `maquetes.js` → `historia.js`. `historia.js` não recria nada de 3D; só lê `fig.__maquete` depois que `maquetes.js` já montou a figura (ver guarda no snippet 4 abaixo).

**Esqueleto HTML das cenas.**

Duas famílias de `data-cena` coexistem no DOM e **não devem ser confundidas**, porque pertencem a elementos diferentes:

1. `data-cena` no wrapper de fundo (`.cena`) — identifica a cena da narrativa (uma frase/tela da história). É lido só por `historia.js`.
2. `data-cena` no `<figure class="maquete" data-cena="36min">` — já existe hoje em `maquetes.js` e escolhe qual função de `CENAS` (`cena36` ou `cenaCasa`) constrói a cena 3D. `historia.js` não toca nisso; só liga/desliga a visibilidade do `<figure>` que já está lá.

```html
<section class="historia">
  <!-- fundo fixo: uma camada por cena, cross-fade por opacidade -->
  <div class="historia__fundo" aria-hidden="true">
    <div class="cena ativa" data-cena="abertura">
      <img src="img/t1.webp" alt="" fetchpriority="high">
    </div>
    <div class="cena" data-cena="36min">
      <!-- reaproveita a maquete que já existe; data-cena aqui é da API de maquetes.js -->
      <figure class="maquete" data-cena="36min">
        <img src="img/t2.webp" alt="Relógio andando de 11:35 a 12:11 enquanto as paredes sobem">
        <canvas hidden></canvas>
        <figcaption><span data-relogio></span> <span data-legenda></span></figcaption>
      </figure>
    </div>
    <div class="cena" data-cena="casa-viaja">
      <figure class="maquete" data-cena="casa-viaja">
        <img src="img/m3.webp" alt="Caixas do B-36 sendo içadas do caminhão">
        <canvas hidden></canvas>
        <figcaption><span data-relogio></span> <span data-legenda></span></figcaption>
      </figure>
    </div>
    <!-- demais cenas: só <img>, sem maquete -->
  </div>

  <!-- passos: um por frase, cada um ocupa a tela toda -->
  <div class="historia__passos">
    <p class="passo ativo" data-cena="abertura">
      <span class="frase">Um número sem origem custa caro na obra.</span>
      <span class="ressalva">medidos 11:35 → 12:11, ampliação de unidade de saúde (26 ambientes, 328 m²)</span>
    </p>
    <p class="passo" data-cena="36min">
      <span class="frase">Do zip à proposta em 36 minutos.</span>
      <span class="ressalva">à mão, cerca de 2 dias úteis — estimativa</span>
    </p>
    <p class="passo" data-cena="casa-viaja">
      <span class="frase">Uma casa modular não cabe inteira no caminhão.</span>
      <span class="ressalva">37 decisões registradas para o B-36</span>
    </p>
    <!-- … até 8–10 passos -->
  </div>
</section>
```

**Como o JS troca a cena.** `historia.js` observa cada `.passo` com um `IntersectionObserver` centrado na tela (ver snippet 2). Quando um passo vira o "ativo", ele: (a) tira `.ativo` do passo e da `.cena` anteriores; (b) põe `.ativo` no passo e na `.cena` de mesmo `data-cena`, disparando o crossfade por CSS (`opacity` com `transition`); (c) se a cena que sai tinha um `<figure class="maquete">` visível, aplica `display:none` nele para que o `IntersectionObserver` interno de `maquetes.js` (threshold `.15`, linha ~222) marque `isIntersecting=false` e pare o próprio `requestAnimationFrame` — sem isso, duas cenas 3D podem ficar renderizando ao mesmo tempo mesmo com uma delas em `opacity:0` (ver Riscos).

**Como amarra `seek(t)` ao progresso.** Enquanto o passo ativo tiver uma `.cena` com `<figure class="maquete">` visível, um único listener de `scroll` (com `requestAnimationFrame` para não empilhar chamadas) calcula o quanto aquele passo específico já rolou (0 a 1, usando `getBoundingClientRect()` do próprio `.passo` dividido pela altura dele) e chama `fig.__maquete.seek(progresso * api.dur)` — sempre com guarda `if (fig.__maquete)`, porque em `prefers-reduced-motion` ou falha de carga do three.js essa API nunca existe.

## O que a pesquisa diz

- O padrão "sticky graphic + steps" do jornalismo de dados: fixar o gráfico com `position: sticky` dentro de um contêiner alto e deixar uma biblioteca de "step-trigger" (ou `IntersectionObserver` puro) dizer qual passo está ativo — "the sticky graphic is entirely handled by CSS, while the only thing done in JavaScript is handling the step triggers" [Easier scrollytelling with position sticky (The Pudding)](https://pudding.cool/process/scrollytelling-sticky/).
- Scrollama (da própria The Pudding) formaliza esse padrão em cima de `IntersectionObserver`, com três recursos: "step triggers", "step progress" (0–100% de um passo) e um helper de "sticky graphic"; o `root` do observer é o próprio viewport quando não especificado [scrollama — README](https://github.com/russellsamora/scrollama/blob/main/README.md), [An Introduction to Scrollama.js](https://pudding.cool/process/introducing-scrollama/).
- Para disparar a troca de cena quando o passo cruza o **centro** da tela (não a borda), o truque comum é um `rootMargin` negativo simétrico (ex.: `"-45% 0px -45% 0px"`) ou `threshold: 0.5` — reduz a "janela" de interseção a uma faixa fina no meio do viewport.
- `fetchpriority="high"` deve ir na imagem que decide o LCP (a primeira cena, visível sem rolar); as imagens das cenas seguintes entram como prioridade baixa/lazy e só disparam o carregamento quando o passo anterior fica ativo, não todas de uma vez [fetchpriority — MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/fetchpriority), [Optimize resource loading with the Fetch Priority API — web.dev](https://web.dev/articles/fetch-priority), [Optimize Resource Loading: The fetchpriority=high Attribute — DebugBear](https://www.debugbear.com/blog/fetchpriority-attribute).
- Crossfade de cenas de fundo é, na prática, CSS puro: camadas absolutas empilhadas, cada uma com `opacity` e `transition`; a alternativa `cross-fade()` do CSS existe mas serve para combinar duas imagens numa só, não para trocar cenas ativas por scroll [cross-fade() — CSS-Tricks](https://css-tricks.com/almanac/functions/c/cross-fade/).
- Amarrar three.js ao scroll normalmente é feito de duas formas: (1) normalizar `scrollY` para 0–1 dividindo pela distância total rolável e usar esse valor diretamente como "tempo" da cena, sem depender de `Clock`/`deltaTime` (que servem para animação por tempo real, não por posição de scroll) [Crafting Scroll Based Animations in Three.js — Codrops](https://tympanus.net/codrops/2022/01/05/crafting-scroll-based-animations-in-three-js/); (2) usar GSAP ScrollTrigger, que já entrega o progresso 0–1 pronto via callback — mas isso é peso extra que este projeto não precisa (ver abaixo).
- CSS scroll-driven animations (`animation-timeline: view()`, `animation-range`) já são viáveis para o efeito de entrada/saída da frase (fade + leve escala) sem nenhum JS: Chrome/Edge suportam sem flag desde a versão 115 (jul/2023); Safari só a partir da versão 26 (set/2025); Firefox estável ainda não suporta de forma confiável — por isso `@supports (animation-timeline: view())` como *progressive enhancement*, nunca como único caminho, é obrigatório [MDN — CSS scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations), [caniuse — animation-timeline: view()](https://caniuse.com/mdn-css_properties_animation-timeline_view), [CSS Scroll-Driven Animations Guide 2026 — CSSAwwwards](https://cssawwwards.com/blog/css-scroll-driven-animations-guide-2026).
- `100vh` mede o viewport "pior caso" (com toda a UI do navegador visível) e por isso "pula" no iOS Safari quando a barra de endereço recolhe/expande; as unidades `svh` (small), `lvh` (large) e `dvh` (dynamic) existem justamente para dar três respostas explícitas diferentes — `dvh` acompanha a barra em tempo real (pode gerar layout "vivo" demais durante a rolagem), `svh` fixa no menor tamanho possível (mais estável para uma seção `sticky` que não deve pular) [Fix 100vh Layout Bugs on Mobile Safari — CORE JSC](https://us.corejsc.com/blog/fixing-100vh-mobile-safari-dynamic-viewport-bug/).
- `position: sticky` para de funcionar (ou funciona errado) se qualquer ancestral entre o elemento e o contêiner de rolagem tiver `overflow` diferente de `visible` sem altura compatível — é uma limitação conhecida e discutida há anos no CSSWG, não um bug de navegador isolado [CSSWG — support position:sticky inside overflow ancestor](https://lists.w3.org/Archives/Public/public-css-archive/2019Apr/0718.html); iOS 26 Safari, além disso, introduziu regressões novas de posicionamento de elementos `fixed`/`sticky` quando a UI do navegador está sendo redesenhada [Fix iOS 26 Safari sticky/fixed bug — Pratik Pathak](https://pratikpathak.com/fix-ios-26-safari-web-layouts-are-breaking-due-to-fixed-sticky-position-elements-getting-misplaced/).
- GSAP (núcleo + todos os plugins, incluindo ScrollTrigger) passou a ser 100% gratuito para uso comercial desde abril/2025 (depois da aquisição pela Webflow) — a licença deixou de ser um obstáculo real [GSAP — no-charge license discussion](https://gsap.com/community/forums/topic/37065-sctrolltrigger-and-scrollsmoother-use-case-no-charge-licence/), [GSAP no GitHub](https://github.com/greensock/GSAP). Ainda assim, o núcleo + ScrollTrigger pesa lá pelos ~80 KB, e sua vantagem central é *pinning* automático + timelines complexas com muitos estados simultâneos [Best JS Scroll Animation & Scrollytelling Libraries 2026](https://sajanmangattu.medium.com/best-javascript-scroll-animation-scrollytelling-libraries-2026-5d63f67a1dca) — coisa que este projeto não precisa, porque `position: sticky` já resolve o "pin" e são só 8–10 passos discretos, não uma timeline coreografada [ScrollTrigger needed? — discussão Lenis](https://github.com/darkroomengineering/lenis/discussions/140).

## Trechos de código de referência

**1) Sticky + passos (HTML/CSS mínimo)**

```html
<section class="historia">
  <div class="historia__fundo"><!-- cenas absolutas aqui --></div>
  <div class="historia__passos">
    <p class="passo" data-cena="abertura">…</p>
    <p class="passo" data-cena="36min">…</p>
  </div>
</section>
```

```css
.historia{position:relative}
.historia__fundo{
  position:sticky;top:0;
  height:100vh;height:100svh; /* svh sobrescreve vh só onde suportado; ver snippet 6 */
  overflow:hidden;
}
.historia__passos{position:relative;z-index:1}
.passo{
  min-height:100vh;min-height:100svh;
  display:flex;align-items:center;justify-content:center;
  text-align:center;padding:2rem;
}
```

Atenção: nenhum ancestral de `.historia__fundo` (inclusive `body`/`html`) pode ter `overflow` diferente de `visible` sem uma altura explícita — é a causa mais comum de `sticky` "morto" no meio de uma página que também tem `overflow-x:hidden` no `body` para evitar barra de rolagem horizontal.

**2) `IntersectionObserver` disparando no centro da tela**

```js
var passos = document.querySelectorAll('.passo');
var atual = null;
var obs = new IntersectionObserver(function (entradas) {
  entradas.forEach(function (e) {
    if (e.isIntersecting) ativar(e.target.dataset.cena, e.target);
  });
}, {
  root: null,               // viewport
  rootMargin: '-45% 0px -45% 0px', // só conta interseção numa faixa fina no meio da tela
  threshold: 0
});
passos.forEach(function (p) { obs.observe(p); });
```

**3) Crossfade de cenas de fundo**

```css
.cena{position:absolute;inset:0;opacity:0;transition:opacity .5s ease}
.cena.ativo{opacity:1}
```

```js
function ativar(nomeCena, passoEl) {
  document.querySelectorAll('.passo.ativo, .cena.ativo').forEach(function (el) {
    el.classList.remove('ativo');
    if (el.classList.contains('cena')) pausarMaqueteSe(el);
  });
  passoEl.classList.add('ativo');
  var cena = document.querySelector('.cena[data-cena="' + nomeCena + '"]');
  if (cena) cena.classList.add('ativo');
}
function pausarMaqueteSe(cenaEl) {
  var fig = cenaEl.querySelector('.maquete');
  if (fig) fig.style.display = 'none'; // tira da interseção -> maquetes.js pausa o rAF sozinho
}
```

**4) Progresso do passo → `seek(t)`**

```js
var pendente = false;
addEventListener('scroll', function () {
  if (pendente) return;
  pendente = true;
  requestAnimationFrame(function () {
    pendente = false;
    var passoAtivo = document.querySelector('.passo.ativo');
    if (!passoAtivo) return;
    var cena = document.querySelector('.cena[data-cena="' + passoAtivo.dataset.cena + '"]');
    var fig = cena && cena.querySelector('.maquete');
    if (!fig || !fig.__maquete || fig.style.display === 'none') return; // guarda: reduced-motion / three.js não carregou / cena escondida

    var r = passoAtivo.getBoundingClientRect();
    var progresso = 1 - Math.min(1, Math.max(0, r.top / (innerHeight - r.height || 1)));
    fig.__maquete.seek(progresso * (fig.__maquete.dur || 1));
  });
}, { passive: true });
```

**5) `animation-timeline: view()` com fallback obrigatório**

```css
.frase{opacity:1;transform:none} /* estado padrão: sempre legível, sem JS nem CSS novo */

@supports (animation-timeline: view()) {
  .frase{
    animation: entra-frase linear both;
    animation-timeline: view();
    animation-range: entry 0% cover 35%;
  }
  @keyframes entra-frase{
    from{opacity:.3;transform:scale(.96)}
    to{opacity:1;transform:scale(1)}
  }
}
```

**6) `svh` com fallback para navegadores sem suporte**

```css
.historia__fundo, .passo{
  height:100vh;   /* fallback: sempre aplicado primeiro */
  height:100svh;  /* sobrescreve só onde svh é reconhecido; senão a linha é ignorada */
}
```

## Requisitos para o plano

1. **P4-01 — MUST.** `historia.html`/`historia.js` não adicionam nenhuma dependência nova além do `three.js` já vendorizado em `portfolio/site/vendor/`; GSAP fica de fora. Testável por `grep` não encontrar nenhum `<script src=` externo nem `node_modules` referenciado.
2. **P4-02 — MUST.** Rolagem nativa: nenhum `preventDefault` em `wheel`/`touchmove`, nenhum `scrollTo`/`scrollIntoView` forçado pelo JS da história. Testável por revisão de código (busca por essas chamadas) mais um teste manual de rolagem por barra de rolagem/teclado.
3. **P4-03 — MUST.** Ao trocar de passo, a cena 3D que sai de cena recebe `display:none` (não só `opacity:0`) antes de a próxima entrar, para que o `IntersectionObserver` interno de `maquetes.js` (threshold `.15`) marque `isIntersecting=false` e pare o próprio `requestAnimationFrame`. Testável verificando, com o DevTools de performance, que só uma figura `.maquete` está com `raf` ativo por vez.
4. **P4-04 — MUST.** Toda chamada a `fig.__maquete.seek(...)` é precedida por `if (fig.__maquete)`. Testável simulando `prefers-reduced-motion: reduce` (onde a API não deve existir) e confirmando que não há erro no console.
5. **P4-05 — MUST.** Nenhuma seção de `historia.html` usa `100vh` sozinho nem `100dvh` como único valor; sempre `height:100vh` seguido de `height:100svh` (cascata de fallback). Testável por busca textual no CSS.
6. **P4-06 — SHOULD.** Efeitos de `animation-timeline: view()` só existem dentro de `@supports (animation-timeline: view())`, com um estado padrão (fora do `@supports`) que já é legível sem nenhuma animação. Testável desligando `animation-timeline` no DevTools e conferindo que a frase continua legível.
7. **P4-07 — MUST.** A troca de passo ativo dispara no centro vertical da tela (via `rootMargin` negativo simétrico ou `threshold: 0.5`), não na borda de entrada/saída do elemento. Testável rolando devagar e observando em qual ponto da tela a cena muda.
8. **P4-08 — SHOULD.** Só a imagem da primeira cena tem `fetchpriority="high"`; as demais só começam a carregar quando o passo anterior fica ativo (pré-carregamento de "a próxima", não de todas). Testável pela aba Network mostrando o pedido da imagem da cena N+1 disparando perto da ativação da cena N.
9. **P4-09 — MUST.** Nenhuma frase ou ressalva usa número que não exista já no site (`index.html`) ou no `00-contexto.md`; toda frase com número mantém a ressalva na mesma tela. Testável reaproveitando a lógica de `portfolio/tests/check_site.py` (números batendo com commit de referência, ressalvas presentes).
10. **P4-10 — SHOULD.** `historia.js` não duplica a "guarda de desempenho" de `maquetes.js` (contagem de fps, `matar()`); só liga/desliga visibilidade e chama `seek()`. Testável por revisão: nenhuma lógica de fps em `historia.js`.

## Riscos e armadilhas

- **Duas cenas 3D "vivas" ao mesmo tempo.** `opacity:0` não tira um elemento da interseção geométrica que o `IntersectionObserver` de `maquetes.js` mede (threshold `.15`); se a cena de fundo trocar só por CSS, o `<figure class="maquete">` que "saiu" continua com seu próprio `requestAnimationFrame` rodando, gastando GPU e podendo até disparar errado a guarda de "<24fps" por concorrência entre dois contextos WebGL simultâneos. Mitigação: P4-03 (`display:none` na cena inativa).
- **`position: sticky` "morto" por causa de um ancestral.** Qualquer `overflow` (inclusive `overflow-x:hidden` no `body`, comum para evitar rolagem horizontal) num ancestral entre `.historia__fundo` e o `body` quebra o `sticky` sem erro nenhum no console — é silencioso e só aparece testando em página inteira, não em isolamento (CodePen).
- **`dvh` parece a escolha "moderna" mas é a errada aqui.** Como `dvh` acompanha a barra de endereço do Safari em tempo real, uma seção `sticky` com `height:100dvh` pode encolher/crescer *durante* a rolagem (a barra recolhe ao rolar para baixo), criando um "pulo" visual bem perceptível numa página cujo efeito inteiro depende de nada pular. `svh` (tamanho mínimo, estável) é a escolha certa para o contêiner sticky; `dvh` só faria sentido para algo que deve preencher a tela real a cada instante.
- **iOS 26 trouxe regressões novas em `fixed`/`sticky`**, não só o clássico problema de `100vh` — vale testar especificamente num iPhone com iOS 26 antes de considerar pronto, não só em um emulador de viewport no desktop.
- **Firefox estável não suporta `animation-timeline: view()`.** Sem o `@supports` do snippet 5, uma parte do público simplesmente não vê a frase aparecer (fica com o `opacity` do `@keyframes` "preso" no estado inicial se a regra for aplicada sem guarda) — o estado padrão fora do `@supports` precisa ser a versão 100% legível, não um estado intermediário da animação.
- **`rootMargin` percentual se comporta mal se o passo for mais alto que a tela.** Se algum `.passo` acabar maior que `100vh` (texto longo + ressalva grande em fonte ampliada por acessibilidade do usuário), o gatilho de centro pode nunca disparar limpo — vale testar com fonte do sistema aumentada (`text-size-adjust`/zoom) e não só no tamanho de fonte padrão.
- **Pré-carregar todas as imagens de cena de uma vez** (em vez de "a próxima") soma rápido em 3G/4G de obra — o público-alvo (analistas e gestores de obra vendo pelo celular) não tem necessariamente Wi-Fi bom; a régua "só a próxima cena" do P4-08 é sobre banda, não só sobre LCP.

## Fontes

- [Easier scrollytelling with position sticky — The Pudding](https://pudding.cool/process/scrollytelling-sticky/)
- [An Introduction to Scrollama.js — The Pudding](https://pudding.cool/process/introducing-scrollama/)
- [scrollama — README (russellsamora/scrollama)](https://github.com/russellsamora/scrollama/blob/main/README.md)
- [fetchpriority — MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Attributes/fetchpriority)
- [Optimize resource loading with the Fetch Priority API — web.dev](https://web.dev/articles/fetch-priority)
- [Optimize Resource Loading: The fetchpriority=high Attribute — DebugBear](https://www.debugbear.com/blog/fetchpriority-attribute)
- [cross-fade() — CSS-Tricks](https://css-tricks.com/almanac/functions/c/cross-fade/)
- [Crafting Scroll Based Animations in Three.js — Codrops](https://tympanus.net/codrops/2022/01/05/crafting-scroll-based-animations-in-three-js/)
- [MDN — CSS scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)
- [caniuse — animation-timeline: view()](https://caniuse.com/mdn-css_properties_animation-timeline_view)
- [caniuse — animation-timeline: scroll()](https://caniuse.com/mdn-css_properties_animation-timeline_scroll)
- [CSS Scroll-Driven Animations: Scroll Timelines Guide (2026) — CSSAwwwards](https://cssawwwards.com/blog/css-scroll-driven-animations-guide-2026)
- [Fix 100vh Layout Bugs on Mobile Safari — CORE JSC](https://us.corejsc.com/blog/fixing-100vh-mobile-safari-dynamic-viewport-bug/)
- [CSSWG — support position:sticky inside overflow ancestor (#865)](https://lists.w3.org/Archives/Public/public-css-archive/2019Apr/0718.html)
- [Fix iOS 26 Safari sticky/fixed layout bug — Pratik Pathak](https://pratikpathak.com/fix-ios-26-safari-web-layouts-are-breaking-due-to-fixed-sticky-position-elements-getting-misplaced/)
- [GSAP — no-charge license discussion](https://gsap.com/community/forums/topic/37065-sctrolltrigger-and-scrollsmoother-use-case-no-charge-licence/)
- [GSAP no GitHub](https://github.com/greensock/GSAP)
- [Best JavaScript Scroll Animation & Scrollytelling Libraries 2026 — Medium](https://sajanmangattu.medium.com/best-javascript-scroll-animation-scrollytelling-libraries-2026-5d63f67a1dca)
- [ScrollTrigger needed? — discussão darkroomengineering/lenis #140](https://github.com/darkroomengineering/lenis/discussions/140)
