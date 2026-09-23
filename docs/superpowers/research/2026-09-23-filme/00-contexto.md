# Contexto comum das personas — rodada 3: o que aproveitar do filme

## O que existe hoje no site (branch `historia-scrollytelling`, testado)
- `portfolio/site/index.html` — a história em **17 capítulos datados** (2017 → set/2026), régua de tempo no cabeçalho, palco `sticky` que troca o fundo no meio da tela, links "Ver o caso completo" para `portfolio.html`, fundos tipográficos ("2017", "5×", "2026", "3ª", "22 baias") nos capítulos sem imagem, 3 maquetes three.js **ao vivo** amarradas ao scroll (`36min`, `casa-viaja`, `icamento`; cada uma cria o seu `WebGLRenderer`). Roteiro, regras e decisões: `docs/superpowers/specs/2026-09-23-historia-linha-do-tempo-design.md`.
- `portfolio/site/maquetes.js` (three.js **r186** ES module vendorizado em `site/vendor/`; `stage()`, `camKeys`, `CENAS`, `montar()` com guarda de fps e `seek()`), `portfolio/site/historia.js`, `portfolio/tests/check_historia.py` (estático + harness Chromium em tempo real via DevTools Protocol + WebGL real).
- Estética: prancha de obra — papel `#ECEBE6`, tinta `#171F29`, ferrugem `#B5440E`, aço `#2E4763`; Barlow Condensed / IBM Plex Sans / IBM Plex Mono (`portfolio/DESIGN.md`).

## O material novo: `filme-codigo-fonte.zip` (feito em outra sessão)
Cópia de trabalho: `/tmp/claude-1000/-home-runner-workspace/f9d44ef5-7d41-4ced-9ebe-ca35da9a73fc/scratchpad/filme/`
- `film.html` (347 linhas, 39 KB): **9 dioramas** em three.js **r128** (script global `three.min.js`), **um só `WebGLRenderer`** (1280×720, sombras PCFSoft), cada cena é um grupo `st.g` que liga/desliga, com `st.cam` (chaves de câmera por curva Catmull-Rom) e `st.run(t)` (t de 0 a 10). Capa, legendas (kicker, frase ≤7 palavras, apoio, HUD com contador, ressalva), transição em "wipe" diagonal ferrugem, barra de progresso, cartão final. Determinístico: `renderAt(T)` desenha o segundo T. Duração total 85 s.
  - Cenas (comentários no código): ABERTURA · quantitativos (tabela com etiquetas de origem "medido/derivado/a confirmar"); CENA 1 · escritório 2017; CENA 2 · duas construtoras (post-its "R$ 155.000" repetidos); VEKS · parede LSF; 13 OBRAS · restaurante medido; CENA 4 · prédio SIGE (andares CAIXA, MEDIÇÃO, COMPRAS, DIÁRIO); CELEIRO · balancim; CENA 3 · WhatsApp (diários voltando para o cronograma); CENA 6 · 36 minutos (planta + relógio).
  - Paleta do filme: papel quente `#EFE6D6`, tinta `#1B1714`, ferrugem `#E0622A`/`#F07A3E`.
- `render.py`: Playwright + ffmpeg (libx264, crf 20, 30 fps, 1280×720) → `cassio-viller-filme.mp4` (~20 min em CPU). Aqui não há Playwright, mas há `ffmpeg` e o controle de Chromium do `check_historia.py` (DevTools Protocol) consegue chamar `renderAt(T)` e capturar quadros.
- Quadros de cada capítulo já capturados: `…/scratchpad/filme/q00.png` … `q09.png` (q09 = cartão final), e as tiras `l1.png`, `l2.png`.

## Problemas de conteúdo já encontrados no filme (escrito antes das correções de hoje)
1. "13 obras orçadas" (HUD conta até 13 obras) — o site diz "13 obras **no sistema, 11 com proposta**".
2. Post-its "R$ 155.000" no capítulo das duas construtoras — valor inventado, parece dado.
3. "O módulo sobe pelo balancim, cabos na vertical" dito como fato e misturado ao B-36 — é **estudo** (a página já diz "No estudo, …"; módulo de 8 m).
4. SIGE com kicker "jul → set/2026" — a linha do tempo confirmada diz **mai → set/2026**.
5. "23 dias de obra perdidos no WhatsApp" — os diários estavam no WhatsApp, não se perderam.
6. "Mas a obra digitava tudo cinco vezes" — o site: "vi a mesma informação digitada cinco vezes".
7. "26 anos" na capa e no cartão final — não está no portfólio (a confirmar com o Cássio).
8. Capítulo 1 do filme e da página: **"Comecei no centavo, não na parede."** — o Cássio achou estranho e prefere algo **sobre a contabilidade** (proposta: "Comecei pela contabilidade, não pela obra."). O `portfolio.html` usa a mesma frase no topo.

## Caminhos já discutidos (as personas podem contestar)
- **A. Vídeo como fundo, avançado pelo scroll** — pesado (quadros-chave frequentes), engasga no iPhone, texto gravado no vídeo não é acessível.
- **B. Trazer os dioramas para as maquetes ao vivo** (recomendado) — cada capítulo ganha o seu diorama que anda com o scroll; texto segue em HTML; exige portar r128 → r186 e usar **um renderizador compartilhado** (9+ contextos WebGL pesariam).
- **C. O filme como trailer à parte** — MP4 corrigido, "Assista em 85 s" com capa, tocando só por clique; serve também para LinkedIn/WhatsApp.

## Regras que continuam valendo
Nenhum número que o portfólio não sustente (datas confirmadas pelo Cássio ficam como exceção explícita); nenhuma ressalva apagada; não misturar SIGE com sistema de orçamento; nada de valor inventado com cara de dado; sem build nem dependência nova além do three.js vendorizado; rolagem nativa; modo empilhado sem JS/movimento reduzido; contraste ≥ 4,5:1.
