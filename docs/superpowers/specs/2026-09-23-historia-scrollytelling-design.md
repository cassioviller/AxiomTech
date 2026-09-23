# Spec — `historia.html`: a história do Cássio em 10 cenas

**Data:** 23/09/2026 · **Base:** pesquisa de 5 personas em `docs/superpowers/research/2026-09-23-historia/` (contexto comum em `00-contexto.md`).

## Objetivo
Uma página nova, `portfolio/site/historia.html`, que conta a trajetória do Cássio em **10 cenas**. Cada cena tem uma frase direta e grande no centro da tela e uma linha pequena de apoio ou ressalva; o fundo troca de cena quando a frase cruza o meio da tela. A página termina no convite ("Me mande uma obra"), no portfólio completo e no currículo. O site atual (`index.html`) não muda.

## Para quem (as 5 personas)
| Persona | Arquivo | O que exige da página |
|---|---|---|
| Renata, recrutadora técnica de construtora | `persona-1-recrutadora.md` | nome, cargo-alvo e contato na primeira tela; currículo e WhatsApp alcançáveis de qualquer ponto; palavras-chave da vaga em texto; senioridade dita cedo |
| Eduardo, diretor de engenharia de construtora LSF | `persona-2-diretor.md` | todo número com origem ou ressalva na mesma cena; verbos de constatação, não de milagre; limitação declarada antes do convite; o convite só depois da prova em obra real; vocabulário do ofício |
| Lia, roteirista de narrativa pessoal | `persona-3-roteirista.md` | arco ABT (um único "mas", na virada para a obra) + story spine; frase ≤ 10 palavras e uma ideia por tela; tese no começo e eco no fim; primeira pessoa, "você" só no convite |
| Tiago, dev front-end de scrollytelling | `persona-4-frontend.md` | `position: sticky` + `IntersectionObserver` no centro da tela, sem biblioteca; crossfade por opacidade; maquete 3D amarrada ao scroll por `seek()`; só uma maquete renderizando; `100vh` seguido de `100svh`, nunca `dvh` |
| Carla, acessibilidade e desempenho | `persona-5-a11y-perf.md` | rolagem 100% nativa; com movimento reduzido ou sem JS, cenas empilhadas e estáticas, cada frase com a sua imagem; fundos decorativos com `aria-hidden`; contraste ≥ 4,5:1 no pior pixel; sem rolagem horizontal a 320 px; primeira imagem com prioridade |

## Roteiro (texto final, exato)
| # | `data-passo` | Frase grande | Linha de apoio / ressalva | Fundo |
|---|---|---|---|---|
| 1 | `tese` | Um número sem origem custa caro na obra. | Cássio Viller, estudante de Engenharia Civil (7º semestre), mira orçamento, planejamento e custos. | `o-quantitativos.webp` (cada quantidade diz de onde veio) |
| 2 | `origem` | Comecei no centavo, não na parede. | Folha, notas e balancete no escritório da família, desde 2017. | sem imagem (palco escuro) |
| 3 | `obra` | Mas na obra, vi a mesma informação digitada cinco vezes. | VEKS Engenharia, V Alves e Estruturas do Vale, entre 2025 e 2026. | `p-fotos.webp` (canteiro real) |
| 4 | `zip` | Do zip à proposta assinável em 36 minutos. | Medidos: 11:35 → 12:11, numa ampliação de unidade de saúde com 26 ambientes e 328 m². À mão, cerca de 2 dias úteis (estimativa). | maquete `36min` (relógio segue o scroll); reserva `upa-plan-grey.webp` |
| 5 | `escala` | 13 obras no sistema, até R$ 24,5 milhões. | 11 com proposta; a menor, R$ 29 mil. A gestão de obra deste sistema ainda não rodou numa obra real. | `s1.webp` (o restaurante de rodovia de R$ 24,5 mi) |
| 6 | `precisao` | Desvio máximo de 0,25% nos 19 serviços conferidos. | Serviço a serviço, contra a tabela SINAPI da Caixa; acima de 1% de desvio, a importação é recusada. | `o-orcamento.webp` |
| 7 | `sige` | Numa obra real, 23 diários estavam só no WhatsApp. | No SIGE, que concebi: recuperados, levam a obra de 27,6% para 44,7% concluído, contra 60,8% planejado — lido numa cópia do sistema. | `p-diario-portal.webp` (o diário de 07/09 no portal; o `p-portal.webp` foi evitado porque mostra a "previsão de entrega", que o sistema não calcula) |
| 8 | `casa` | O celeiro não cabe inteiro no caminhão. | B-36: vai em duas caixas, em três viagens, com 37 decisões registradas. | maquete `casa-viaja` (segue o scroll); reserva `m1.webp` |
| 9 | `metodo` | Construí o jeito de o número não sumir. | Idealizei e dirigi os sistemas; o código foi escrito com assistentes de IA, e as regras, os testes e a revisão são meus. | `o-proposta.webp` |
| 10 | `convite` | Faltam 3 semestres para o diploma. Não falta obra feita. | Você me manda o pacote do projeto; eu devolvo levantamento, orçamento com faixa e proposta no seu modelo. + botões WhatsApp · portfólio completo · currículo | sem imagem |

Depois das cenas vem uma **ficha** estática ("O que faço numa construtora") com as palavras-chave em texto — quantitativos, SINAPI, BDI, cronograma físico-financeiro, curva S, diário de obra e medição, compras com cotação, fluxo de caixa — e a linha "Engenharia Civil, 7º semestre, faltam 3 · CLT ou PJ · São José dos Campos/SP, presencial ou remoto".

Todo número do roteiro já existe no texto visível do `index.html`. As cenas 4–6 e 9 usam só telas do sistema de orçamento; a cena 7 usa só tela do SIGE.

## Requisitos consolidados
| ID | Requisito | Personas |
|---|---|---|
| R-01 | Primeira tela, sem rolar: nome, cargo-alvo e contato (barra fixa + cena 1) | P1-01 |
| R-02 | Currículo (PDF) e WhatsApp alcançáveis de qualquer ponto (barra `sticky`) e no convite final | P1-05 |
| R-03 | Frase grande ≤ 10 palavras, uma ideia por cena; tese na cena 1 e eco na 9 | P3-01, P3-02, P3-04 |
| R-04 | Toda cena tem linha de apoio (≤ 30 palavras) na mesma tela; ressalvas literais presentes: "estimativa", "ainda não rodou", "nos 19 serviços conferidos", "cópia do sistema", "assistentes de IA" | P2-01, P2-02, P3-03, P3-10 |
| R-05 | Nenhum número que o `index.html` não sustente | P3-09, P4-09 |
| R-06 | Telas do SIGE e do sistema de orçamento nunca na mesma cena | P2-03, P3-05 |
| R-07 | Limitação declarada (cena 5) e prova em obra real (cena 7) antes do convite (cena 10) | P2-07, P2-09 |
| R-08 | Palavras-chave e termos do ofício como texto (ficha + cena 6) | P1-06, P2-05 |
| R-09 | Papel da IA dito com verbo de responsabilidade do autor (cena 9) | P2-06 |
| R-10 | Primeira pessoa; "você" uma única vez, no convite | P3-07 |
| R-11 | Rolagem 100% nativa: sem `scrollTo`, `scrollIntoView`, `preventDefault`, `wheel`/`touchmove` | P4-02, P5-03 |
| R-12 | Todo o texto no HTML desde o carregamento, na ordem de leitura; sem JS, sem `IntersectionObserver` ou com `prefers-reduced-motion: reduce`, as cenas ficam empilhadas e estáticas, cada frase com a sua imagem | P5-01, P5-05 |
| R-13 | Figuras de fundo com `aria-hidden="true"` e `alt=""`; nada focável dentro delas (o botão de pausa do `maquetes.js` fica escondido); o primeiro link é "Pular para o texto" | P5-06, P5-09 |
| R-14 | Contraste ≥ 4,5:1 no pior pixel: faixa `rgba(12,16,21,.78)` atrás do texto → 9,68:1 (branco) e 7,32:1 (`#D7E1EC`) mesmo sobre pixel branco | P5-02 |
| R-15 | Sem rolagem horizontal a 320 px; cenas com `min-height` (nunca altura fixa), para o texto crescer com o zoom | P5-07, P5-08 |
| R-16 | Troca de cena quando a frase cruza o meio da tela (`rootMargin: -45% 0px -45% 0px`) | P4-07 |
| R-17 | Maquete: tempo da animação = progresso da cena (`seek`); só a maquete da cena ativa fica no fluxo (as outras `hidden`); nunca anda sozinha depois da primeira sincronização (≤ 200 ms após montar) | P4-03, P4-04, P5-04, P5-12 |
| R-18 | `height:100vh` seguido de `height:100svh` (e `200vh`/`200svh`); nunca `dvh` | P4-05 |
| R-19 | Nenhuma dependência nova: só `three.js` já vendorizado, `maquetes.js` e o novo `historia.js` | P4-01 |
| R-20 | Primeira imagem com `preload` e `fetchpriority="high"`; demais `loading="lazy"`; todas com `width`/`height` | P5-10, P5-11 |

## Arquitetura
- **`historia.html`** (CSS inline, como o `index.html`): barra `sticky` no topo; `<main class="historia">` com um `<div class="palco">` vazio e 10 `<section class="cena">`, cada uma com a sua `<figure class="fundo">` (quando tem imagem) e o seu `<div class="texto">`. Sem JS, isso **já é** a página empilhada (R-12).
- **`historia.js`** (IIFE, `defer`, depois do `maquetes.js`): se houver `IntersectionObserver` e o movimento não estiver reduzido, move cada `.fundo` para o `.palco` (`position: sticky; margin-bottom: -100svh`), liga a classe `js-historia` no `<html>` e troca `.ativo` quando uma cena cruza o meio da tela. Maquetes ficam `hidden` fora da sua cena, então o `IntersectionObserver` interno do `maquetes.js` pausa as que não estão em cena.
- **Atributos:** `data-passo` identifica a cena da história; `data-cena` continua sendo só o nome da cena 3D do `maquetes.js` (`36min`, `casa-viaja`).
- **`maquetes.js`:** uma linha — a API passa a expor `dur` (`var api={frozen:false,dur:sc.dur,…}`), porque `fig.__maquete.dur` não existia.
- **Testes:** `portfolio/tests/check_historia.py` (estático, Python puro) e, com `--navegador`, um harness `portfolio/tests/historia_teste.html` que o Chromium headless abre em **tempo real**, controlado pelo DevTools Protocol por um cliente WebSocket mínimo em Python puro (servido por `python3 -m http.server` a partir de `portfolio/`). O harness rola um iframe cena a cena e registra o estado num `<pre>`. O ensaio mostrou que `--virtual-time-budget` quase não gera quadros (o `IntersectionObserver` não dispara) e que a janela headless tem mínimo de ~500×657, por isso o tamanho vem de `Emulation.setDeviceMetricsOverride`.

## Decisões (rulings) tomadas ao juntar as personas
1. **Estrutura por cena em vez de "fundo separado + passos"** (o esqueleto da persona 4). Com figura e texto na mesma `<section>`, a página sem JS ou com movimento reduzido já pareia cada frase com a sua imagem (P5-01), e o JS só reorganiza. Custo se errado: um passo de DOM a mais na carga.
2. **`api.dur` não existia** no `maquetes.js` (o contexto e a persona 4 supunham que sim): o plano expõe `dur:sc.dur`. Custo: nenhum para o `index.html`.
3. **Sem `animation-timeline: view()`** (P4-06, SHOULD) e **sem pré-carregar só a próxima cena** (P4-08, SHOULD): o crossfade já dá o efeito; imagens `lazy` + primeira com prioridade resolvem o LCP. Custo: ~600 KB de imagens podem baixar logo após a primeira no modo cenas.
4. **P1-02 (número nas 2–3 primeiras cenas):** o primeiro resultado numérico fica na cena 4, para preservar o arco (tese → origem → virada → prova). A barra fixa e a ficha cobrem a recrutadora com pressa. Custo: quem sair na cena 3 não vê número.
5. **Lighthouse e axe não rodam aqui** (sem Node): substituídos por checagens estáticas (atributos, contraste calculado, CSS) e pelo harness no Chromium; a medição real fica no roteiro manual.
6. **Sem GSAP** (P4-01): `sticky` resolve o pin e são 10 passos discretos.

## Decisões em aberto (do Cássio — não bloqueiam a execução)
1. **Estágio / júnior (P1-08):** a página diz "CLT ou PJ", como o site. Se aceitar estágio ou júnior, trocar na ficha e na barra.
2. **Link a partir do `index.html`:** a história fica acessível só pelo endereço até decidir se entra um link no topo do portfólio (ou se ela vira a abertura).
3. **`p-fotos.webp`** tem um trabalhador de perfil — decisão ainda aberta na REVISÃO; a cena 3 usa essa foto (já publicada no `index.html`).
4. **Imagem de prévia própria** (`og:image`) para a história; por enquanto reaproveita `og.png`.

## Roteiro manual (depois da execução)
iPhone real com iOS 26 (Safari) — barra de endereço recolhendo não pode fazer o palco pular; VoiceOver lendo as 10 frases em ordem; zoom de texto 200%; Lighthouse mobile quando houver Node/Chrome DevTools à mão (meta: LCP < 2,5 s, CLS < 0,1).
