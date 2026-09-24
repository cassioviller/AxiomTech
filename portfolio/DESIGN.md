# DESIGN.md — Cássio Viller · portfólio

Linguagem visual do site: `portfolio/site/index.html` (a história em cenas, página principal) e `portfolio/site/portfolio.html` (o portfólio completo). Leia antes de mexer em qualquer página, folha de caso ou currículo: a ideia é que tudo pareça saído da mesma prancha.

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

- **Clipes da história** (fundo dos capítulos em `index.html`): papel `#EFE6D6`, tinta `#1B1714`, laranja `#E0622A` — a paleta do filme, tone-mapped (ACES), sem filtro por cima; o contraste do texto vem só da faixa `--scrim`.

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
- Imagens em WebP, `loading="lazy"`, `alt` descritivo com os números da tela — exceto os 11 pôsteres dos clipes em index.html, que carregam sem lazy (têm de estar prontos para o crossfade e para os caminhos só-pôster; ver check_historia.py).

## 9. Guia para agentes

Ao criar ou alterar uma seção do portfólio: comece pelo carimbo e pela cota; use só os tokens da seção 2 e as três famílias da seção 3; escreva casos em Minto (resultado → o que fiz → prova), em primeira pessoa e sem mudar número conferido; rode `python3 portfolio/tests/check_site.py` antes de commitar; confira em 1280px e 390px, nos temas claro e escuro.
