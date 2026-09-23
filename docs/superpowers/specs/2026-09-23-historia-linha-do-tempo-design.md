# Spec — a história na linha do tempo (rodada 2 da página principal)

**Data:** 23/09/2026 · **Base:** pesquisa das 5 personas em `docs/superpowers/research/2026-09-23-historia-v2/` (contexto em `00-contexto.md`) · **Parte de:** `docs/superpowers/specs/2026-09-23-historia-scrollytelling-design.md` (rodada 1, cujas regras continuam valendo).

## Objetivo
Desenvolver a página principal (`portfolio/site/index.html`) nas quatro frentes pedidas pelo Cássio — impacto visual, mais história, acabamento e ligação com o portfólio — contando a trajetória **na ordem real em que cada coisa aconteceu**, de 2017 a set/2026. Abordagem escolhida: **régua de tempo + capítulos datados** (abordagem A).

## O que as personas pediram (resumo)
| Persona | Exigências principais |
|---|---|
| Renata, recrutadora | "Onde ele está agora" visível sem rolar; datas por extenso em cada vínculo; vínculos simultâneos lado a lado com o tipo de contrato; link para o caso completo em cada capítulo; datas iguais às do currículo |
| Eduardo, diretor | "meio período, em paralelo" e "PJ, 6 meses, cumprido até o fim" ditos com todas as letras; "cópia do sistema" e carga não aplicada preservadas; B-36 sempre "pré-dimensionado (sujeito à revisão do engenheiro responsável)"; nada do gabarito de 3,40 m; o convite só depois de prova em obra real |
| Lia, roteirista | Ordem estritamente cronológica; cada capítulo com a sua data; frase ≤ 10 palavras e apoio ≤ 30; um único "mas" (a entrada na obra); 12 a 16 capítulos + moldura |
| Tiago, front-end | Nada de observer ou listener novo para a régua: ela lê o estado que `historia.js` já tem; links do caso são âncoras normais do `portfolio.html`; a maquete de içamento entra como `CENAS['icamento']` usando `stage()` e `camKeys` |
| Carla, acessibilidade | `<nav aria-label>` + `<ol>` com exatamente um `aria-current="step"`; sem `aria-live` na régua; salto pela régua leva o foco ao título (`tabindex="-1"`) e o título não fica atrás da barra; nomes de link únicos por caso; `<time datetime>`; sem JS, a régua é uma lista estática |

## Roteiro (17 capítulos, texto exato)
| # | `id` / `data-passo` | Data exibida (`<time datetime>`) | Frase grande | Linha de apoio / ressalva | Fundo | Caso completo (link) |
|---|---|---|---|---|---|---|
| 1 | `tese` | — | Um número sem origem custa caro na obra. | Cássio Viller, estudante de Engenharia Civil (7º semestre), mira orçamento, planejamento e custos. | `o-quantitativos.webp` | — |
| 2 | `origem` | 2017 → 2024 (`2017`, `2024`) | Comecei no centavo, não na parede. | Escritório contábil da família desde 2017; na UNIFEI, fiscal do DCE em 2022 e diretor de vendas da InLoco Jr. de 2023 a 2024. | tipográfico "2017" | `#curriculo` · "Ver no currículo: contabilidade e UNIFEI →" |
| 3 | `mudanca` | 2025 (`2025`) | Em 2025, mudei de cidade e de curso. | Cruzeiro do Sul (EAD), morando em São José dos Campos: hoje no 7º semestre, faltam 3. Sistemas de Informação na PUC, em paralelo. | tipográfico "2025" | `#curriculo` · "Ver no currículo: formação →" |
| 4 | `obra` | fev/2025 → mar/2026 (`2025-02`, `2026-03`) | Mas na obra, vi a mesma informação digitada cinco vezes. | V Alves (gerente de produção, CLT meio período) e Estruturas do Vale (estágio, meio período), em paralelo. No estágio nasceu o SIGE. | tipográfico "5×" | `#curriculo` · "Ver no currículo: V Alves e Estruturas do Vale →" |
| 5 | `veks` | mar/2026 → set/2026 (`2026-03`, `2026-09`) | Em março de 2026, entrei na VEKS Engenharia. | PJ, contrato de 6 meses cumprido até o fim; a V Alves, em meio período, seguiu até julho. | tipográfico "2026" | `#obra` · "Ver o caso completo: obras na VEKS →" |
| 6 | `ferramentas` | mar → abr/2026 (`2026-03`, `2026-04`) | Toda conta repetida virou ferramenta. | Nos primeiros meses na VEKS: a calculadora de parede em LSF e drywall e o classificador do fluxo de caixa. | tipográfico "3ª" | `#ferramentas` · "Ver as ferramentas: calculadora e classificador →" |
| 7 | `sige` | mai → set/2026 (`2026-05`, `2026-09`) | De maio a setembro, o SIGE ganhou versão nova. | Cerca de 50 módulos em 6 áreas, entregas registradas de 22/07 a 14/09/2026; código escrito com assistente de IA, sob a minha direção. | `c-aprovacao.webp` | `#sige` · "Ver o caso completo: SIGE →" |
| 8 | `galpoes` | jun/2026 (`2026-06-08`) | Em junho, começou a obra que testaria o SIGE. | Dois galpões e 22 baias numa fazenda, em Light Steel Frame: a obra real do portal do cliente e do diário. | tipográfico "22 baias" | `#obra` · "Ver o caso completo: galpões e baias →" |
| 9 | `escala` | jul → set/2026 (`2026-07-09`, `2026-09-21`) | 13 obras no sistema, até R$ 24,5 milhões. | 11 com proposta; a menor, R$ 29 mil. A gestão de obra deste sistema ainda não rodou numa obra real. | `s1.webp` | `#sistema` · "Ver o caso completo: sistema de orçamento →" |
| 10 | `precisao` | jul → set/2026 (`2026-07-09`, `2026-09-21`) | Desvio máximo de 0,25% nos 19 serviços conferidos. | Serviço a serviço, contra a tabela SINAPI da Caixa; acima de 1% de desvio, a importação é recusada. | `o-orcamento.webp` | `#sistema` · "Ver o caso completo: conferência SINAPI →" |
| 11 | `casa` | ago/2026 (`2026-08`) | O celeiro não cabe inteiro no caminhão. | B-36, pré-dimensionado e sujeito à revisão do engenheiro responsável: duas caixas, três viagens, 37 decisões registradas. | maquete `casa-viaja` · reserva `m1.webp` | `#modular` · "Ver o caso completo: celeiro B-36 →" |
| 12 | `icamento` | ago/2026 (`2026-08`) | No estudo, o módulo sobe pelo balancim, cabos na vertical. | Estudo 3D de agosto: com os cabos na vertical, a parede não é comprimida. Balancim de içamento e guindaste da classe certa viraram itens de regra no orçamento. *(revisão final: deixar claro que é estudo; módulo da maquete com 8 m)* | **maquete nova `icamento`** · reserva `m2.webp` | `#modular` · "Ver o caso completo: casas modulares →" |
| 13 | `whatsapp` | ago/2026 (`2026-08-11`) | Depois de 11/08, o diário saiu do sistema. | 42 diários lançados até ali; os 23 dias seguintes ficaram só no grupo de WhatsApp, e 28 atividades prontas apareciam como atrasadas. | `p-fotos.webp` (fotos de 07/09, um desses dias) | `#sige` · "Ver o caso completo: o diário no WhatsApp →" |
| 14 | `recuperado` | set/2026 (`2026-09`) | Recuperado, o diário mostrou 44,7% de avanço. | Antes, 27,6%; planejado para 07/09, 60,8%. Lido numa cópia do sistema; no sistema em uso, a carga ainda não foi aplicada. | `p-diario-portal.webp` | `#sige` · "Ver o caso completo: diários recuperados →" |
| 15 | `zip` | set/2026 (`2026-09`) | Em setembro, uma proposta assinável em 36 minutos. | Medidos: 11:35 → 12:11, numa ampliação de unidade de saúde com 26 ambientes e 328 m². À mão, cerca de 2 dias úteis (estimativa). | maquete `36min` · reserva `upa-plan-grey.webp` | `#orcamento` · "Ver o caso completo: 36 minutos →" |
| 16 | `metodo` | — | Construí o jeito de o número não sumir. | De 2017 a 2026: contabilidade, obra e sistemas. Idealizei e dirigi; o código foi escrito com assistentes de IA, e as regras e a revisão são minhas. | `o-proposta.webp` | — |
| 17 | `convite` | — | Faltam 3 semestres para o diploma. Não falta obra feita. | Você me manda o pacote do projeto; eu devolvo levantamento, orçamento com faixa e proposta no seu modelo. (+ WhatsApp · portfólio completo · currículo) | sem fundo | — |

Depois vem a ficha (palavras-chave), como na rodada 1. Todos os números acima existem no texto visível do `portfolio.html`. As datas "22/07", "14/09/2026", "jun/2026", "abr/2026" e "ago/2026" vêm da linha do tempo confirmada pelo Cássio e não aparecem no portfólio: ficam registradas como exceções explícitas (`DATAS_CONFIRMADAS`) no teste.

## Requisitos (novos nesta rodada; os da rodada 1 continuam)
| ID | Requisito | Personas |
|---|---|---|
| T-01 | 17 capítulos, **ordem cronológica estrita** pela primeira data de cada capítulo datado | P3-01 |
| T-02 | Cada capítulo datado mostra a data em `<p class="data">` com `<time datetime>`; o texto visível e os `datetime` são os da tabela | P1-02, P3-02, P5-07 |
| T-03 | Vínculos simultâneos ditos com o tipo de contrato: "CLT meio período", "estágio, meio período", "em paralelo" (cap. 4); "PJ, contrato de 6 meses cumprido até o fim" e "seguiu até julho" (cap. 5) | P1-03, P1-04, P2-01, P2-02, P3-05 |
| T-04 | Ressalvas literais obrigatórias: as da rodada 1 + "em paralelo", "pré-dimensionado", "sujeito à revisão do engenheiro responsável", "no sistema em uso, a carga ainda não foi aplicada"; proibido "3,40" | P2-03, P2-05, P2-06 |
| T-05 | Um único "mas" (cap. 4) entre as frases grandes; "você" só no convite | P3-08, P3-07 |
| T-06 | Cada capítulo datado tem `<p class="caso"><a href="portfolio.html#…">`; a âncora existe no `portfolio.html`; **nomes de link únicos** | P1-07, P3-10, P5-06 |
| T-07 | Barra fixa com o status atual: "7º semestre de Eng. Civil · orçamento, planejamento e custos · CLT ou PJ", currículo e WhatsApp | P1-01, P1-06 |
| T-08 | **Régua de tempo** no cabeçalho: `<nav class="regua" aria-label="Linha do tempo">` + `<ol>` com um link por capítulo (`href="#id"`), nome acessível com data + marco; `aria-current="step"` em exatamente um link (o primeiro, no HTML; o ativo, com JS); sem `aria-live`; alvos de pelo menos 28 px de largura, com rolagem horizontal **da própria régua** (nunca da página) quando não couber; data do capítulo ativo à direita | P5-01, P5-02, P5-11, P4 |
| T-09 | Salto pela régua (e pelo "Pular para o texto") leva o foco ao título do capítulo (`<h1/h2 class="frase" tabindex="-1">`); o título fica abaixo da barra (`scroll-margin-top`) | P5-04, P5-05 |
| T-10 | Capítulos sem imagem ganham fundo **tipográfico** (`<figure class="fundo tipo">` com `<span class="ano">`) — número grande e esmaecido, estilo prancha; só números que o portfólio sustenta | visual |
| T-11 | **Terceira maquete** `icamento`: módulo sai da carreta, sobe pelo balancim com cabos verticais, anda e pousa no radier; tempo = scroll (`seek`), mesma API (`dur`, `num`, `leg`); sem número no HUD; reserva `m2.webp` | P2-07, P4 |
| T-12 | Relógio da maquete (HUD) com fundo escuro atrás (contraste ≥ 3:1 no pior caso, texto grande) | pendência da rodada 1 |
| T-13 | Sem JS ou com movimento reduzido: tudo empilhado, a régua é uma lista estática de links (sem marcador móvel) | P5-03, P5-12 |

## Decisões (rulings) ao juntar as personas
1. **A régua mora no cabeçalho, não no palco.** O Tiago propôs pôr a régua dentro do `.palco`, mas o palco é `aria-hidden="true"`, e a navegação ficaria invisível para leitores de tela (conflito com P5-01). Ela fica no `<header class="barra">`, como segunda linha. Custo se errado: a barra fica mais alta (cerca de 36 px).
2. **Nada de `history.replaceState` para o hash** (opção do Tiago). Não há pedido para compartilhar capítulo por URL, e os `id` semânticos já permitem links manuais como `index.html#sige`. Custo: o endereço não acompanha a rolagem.
3. **Vínculos simultâneos no texto do capítulo**, não numa régua com duas faixas (P1-03 pedia lado a lado na régua). Os capítulos 4 e 5 dizem os dois vínculos e o tipo de contrato. Custo: a régua não desenha a sobreposição.
4. **"Aberto a estágio/júnior"** (P1-06) continua como decisão do Cássio: o texto mantém "CLT ou PJ", como o portfólio.
5. **Contraste pelo pior caso matemático** (faixa `rgba(12,16,21,.78)` sobre pixel branco), não por captura de tela pixel a pixel (P5-08). Todo texto de cena fica sobre a faixa, então a fórmula vale para qualquer fundo. Custo: nenhum, enquanto o texto estiver na faixa.
6. **Três contextos WebGL** (P5-10 sugeria no máximo 2). Só a maquete da cena ativa fica no fluxo e as outras param o laço, mas o `maquetes.js` não libera contexto. Três estão bem abaixo do limite dos navegadores. Custo: memória em celular muito fraco.
7. **Sem fundos "compostos"** (render + tela + foto) nesta rodada. Os capítulos sem imagem ganham o fundo tipográfico e a terceira maquete. Custo: menos variedade visual do que a abordagem A prometia.
8. **`p-fotos.webp` só no capítulo do WhatsApp** (13), porque as fotos são de 07/09, um dos 23 dias. O capítulo 4 (2025) não usa foto de obra que ainda não existia (risco de anacronismo apontado pela Lia).
9. **Moldura sem data** (tese, método, convite): esses capítulos não entram na verificação cronológica.

## Decisões em aberto (do Cássio)
Estágio/júnior; imagem de prévia própria; a foto com trabalhador de perfil (`p-fotos.webp`).
