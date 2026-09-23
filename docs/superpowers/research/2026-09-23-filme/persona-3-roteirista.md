# Persona 3 — Lia (rodada 3: o filme)

## A frase da contabilidade (opções e escolha)

Contexto do problema (item 8 de `00-contexto.md`): "Comecei no centavo, não na parede." aparece em três lugares — o capítulo `origem` (2017→2024) de `index.html`, o mesmo capítulo do filme (`CAPS[1]`) e o parágrafo de abertura de `portfolio.html` (linha 390: "Comecei no centavo, não na parede: folha, notas e balancete no escritório da família, desde 2017. Na obra, vi a mesma informação digitada cinco vezes. …"). O Cássio achou a frase estranha e sugeriu algo sobre contabilidade. A frase seguinte, sempre, é "Mas na obra, vi a mesma informação digitada cinco vezes." (página) / "Mas vi o dado digitado cinco vezes." (filme, ≤7 palavras) — então a nova frase precisa abrir caminho para esse "mas", não competir com ele.

| Opção | Texto | Palavras |
|---|---|---|
| A | **Comecei pela contabilidade, não pela obra.** | 6 |
| B | Fiz contas antes de pisar na obra. | 7 |
| C | Aprendi números na contabilidade antes da obra. | 7 |

**Escolha: opção A — "Comecei pela contabilidade, não pela obra."**

Por quê:
- É a própria sugestão do Cássio registrada no contexto ("Comecei pela contabilidade, não pela obra."); adotar a mesma reduz o risco de uma segunda rodada de "achei estranho".
- Mantém a mesma arquitetura da frase original ("Comecei [X], não [Y].") — troca mínima, mais fácil de auditar nos três arquivos e de não quebrar o teste `check_historia.py` por engano em outro ponto da frase.
- A palavra final, "obra", encaixa como gancho para a frase seguinte ("Mas na obra, vi…" / "Mas vi o dado digitado…") sem precisar de um segundo "mas" — o eco de "obra" já sinaliza a virada. Isso preserva a regra herdada da rodada 2 (P3-08: um único "mas", no capítulo de entrada na obra).
- Cabe sem alteração nos três lugares:
  - `index.html`, capítulo `origem`: `<h2 class="frase" tabindex="-1">Comecei pela contabilidade, não pela obra.</h2>`
  - `film.html`, `CAPS[1][1]`: `'Comecei pela contabilidade, não pela obra.'`
  - `portfolio.html`, linha 390 (hero): `<p class="sub">Comecei pela contabilidade, não pela obra: folha, notas e balancete no escritório da família, desde 2017. Na obra, vi a mesma informação digitada cinco vezes. Construí o jeito de ela entrar uma vez — e de cada número ter origem.</p>` — a troca do início não força reescrever o resto do parágrafo, e o "Na obra, vi…" que já vem em seguida repete "obra" de propósito, reforçando a régua.

Risco de dependência (fora do escopo desta persona, mas registrado): `portfolio/tests/check_historia.py`, linha 44, tem a string antiga como valor esperado (`"Comecei no centavo, não na parede."`); a troca em `index.html` exige atualizar esse teste no mesmo commit, senão ele passa a falhar.

## O que a pesquisa diz

- Um trailer/vídeo de marca pessoal de 60–90 s segue a estrutura gancho → contexto/história → entrega de valor → CTA, com o gancho precisando prender a atenção nos primeiros segundos; a duração recomendada para vídeo de marca pessoal é 60–120 s, com "uma mensagem clara e um CTA acionável" — o que reforça a lógica de "um capítulo, uma ideia" que a página já usa. [fonte](https://housesparrowfilms.com/blogs/how-to-script-a-personal-branding-video-that-truly-connects/)
- Para um roteiro de 60 s, a contagem de referência é de 130–160 palavras no total (cerca de 150 palavras por minuto, no ritmo natural de locução) — uma régua útil para calibrar quanto texto cabe por capítulo quando o filme não tem locução, só leitura silenciosa. [fonte](https://www.contentbeta.com/blog/60-second-video-script/)
- Para vídeo silencioso em autoplay, a prática de mercado usa 6–12 palavras por cartela e 1,5–2,5 s de exibição por cartela, trocando texto ou imagem a cada 1,2–1,8 s na "janela de gancho" — o filme atual já usa cartelas curtas para a frase (≤7 palavras), mas o texto de apoio é bem mais longo do que essa janela sugere. [fonte](https://www.influencers-time.com/silent-first-editing-subtitle-rules-for-muted-autoplay-feeds/)
- O padrão de emissoras e streamings (BBC/Netflix) para legendas é 15–20 caracteres por segundo, 140–180 palavras por minuto, no máximo ~42 caracteres por linha e 1–7 s de exibição por cartela — passar disso faz o espectador perder palavras mesmo lendo em silêncio. [fonte](https://cleansubtitle.com/blog/subtitle-line-length-guide)
- Uma segunda fonte com os mesmos números: 160–180 palavras/minuto é a faixa confortável, com mínimo de ~0,3 s por palavra e a regra de quebrar o texto na pontuação (nunca entre artigo e substantivo, ou preposição e seu complemento) — relevante para como o `apoio` do filme deveria ser cortado se precisar encurtar. [fonte](https://onecraft.app/blog/video-captions-best-practices/)
- **Aplicando essas taxas ao `film.html` atual, a maioria dos capítulos exige uma velocidade de leitura bem acima do confortável.** Cada capítulo mostra a `frase` e o `apoio` juntos, do fade-in (~35% do tempo do capítulo) até o fade-out (~93%) — uma janela real de aproximadamente `0,76 × duração do capítulo`. Nos capítulos de 8–8,5 s, essa janela é de ~6,1–6,5 s. Dividindo as palavras do `apoio` por esse tempo:
  - CENA "sistema de orçamento" (31 palavras / 6,46 s) ≈ **288 wpm**
  - CENA VEKS (29 palavras / 6,08 s) ≈ **286 wpm**
  - CENA "duas construtoras" (25 palavras / 6,08 s) ≈ **247 wpm**
  - CENA SIGE (27 palavras / 6,08 s) ≈ **266 wpm**
  - CENA celeiro/balancim, já com a correção do item 3 (24 palavras / 6,46 s) ≈ **223 wpm**
  - CENA WhatsApp (24 palavras / 6,46 s) ≈ **223 wpm**
  - CENA 36 min (23 palavras / 6,84 s) ≈ **202 wpm**
  - CENA origem/contabilidade (20 palavras / 6,08 s) ≈ **197 wpm**
  - Abertura/quantitativos (17 palavras / 7,98 s) ≈ **128 wpm** — a única dentro da faixa confortável
  Todas as outras oito cenas ultrapassam os 160–180 wpm de referência, e a maioria ultrapassa até os ~200 wpm citados como teto para conteúdo "rápido" — ou seja, mesmo sem trocar uma palavra por honestidade, o `apoio` do filme já está denso demais para o tempo de tela que tem. [fonte](https://onecraft.app/blog/video-captions-best-practices/) [fonte](https://cleansubtitle.com/blog/subtitle-line-length-guide)
- Manter a mesma história em formatos de duração diferente (vídeo de 60–90 s vs. página completa) funciona quando existe um "parágrafo-âncora" com a narrativa central, repetido em todo canal, e cada canal recebe um papel diferente (vídeo cria conexão emocional rápida, página reúne prova) em vez de tentar caber o mesmo nível de detalhe nos dois — o que justifica o filme comprimir 17 capítulos da página em 9, desde que nenhum fato comprimido vire uma imprecisão nova. [fonte](https://bluecube.com.sg/blogs/how-to-build-a-consistent-brand-narrative-across-channels/)

## Roteiro corrigido do trailer (tabela)

Numeração pelos índices de `CAPS[k]` em `film.html` (k = 0..8; `NCH = 8`). "Página" indica o(s) capítulo(s) de `index.html`/`docs/.../2026-09-23-historia-linha-do-tempo-design.md` que o capítulo do filme comprime. Mudanças em **negrito**; o resto é mantido do filme atual.

**Capa (`#cover`, antes de k=0):** kicker "Portfólio · 2017 → 2026" (sem mudança) · h1 "Cassio Viller" · linha `.a`: **"São José dos Campos/SP"** (era "26 anos · São José dos Campos/SP" — item 7) · `.f`: "Engenharia Civil — 7º semestre, faltam 3 · Sistemas de Informação — 3º semestre / Orçamento, planejamento e custos de obra" (sem mudança) · contato (sem mudança).

| k | Página | Kicker | Frase (≤7 palavras) | Apoio (≤35 palavras) | HUD | Ressalva |
|---|---|---|---|---|---|---|
| 0 | tese | **"Cássio Viller · portfólio"** (era "· 26 anos" — item 7) | Número sem origem custa caro na obra. | Nove capítulos, de 2017 a 2026. Cada número desta história tem origem: medido, derivado ou a confirmar. | — | — |
| 1 | origem | 2017 → 2024 | **"Comecei pela contabilidade, não pela obra."** (era "Comecei no centavo, não na parede." — item 8) | Escritório contábil da família desde 2017. Na UNIFEI, fiscal do DCE (2022) e diretor de vendas da InLoco Jr. (2023–2024). | 8 anos / de rotina contábil | — |
| 2 | obra | fev/2025 → mar/2026 | **"Mas vi o dado digitado cinco vezes."** (era "Mas a obra digitava tudo cinco vezes." — item 6; sujeito volta a ser "eu", não "a obra") | Meio período em duas empresas, em paralelo: gerente de produção na V Alves (CLT) e estágio comercial na Estruturas do Vale, onde nasceu o SIGE. | 5× / o mesmo dado | — |
| 3 | veks + ferramentas | mar → set/2026 | Na VEKS, toda conta repetida virou ferramenta. | PJ, contrato de 6 meses cumprido até o fim; a V Alves seguiu até julho. Orçamentos e obras em Light Steel Frame; calculadora de parede e classificador de caixa. | 6 meses / contrato PJ cumprido | — |
| 4 | escala + precisão | jul → set/2026 | **"13 obras no sistema, 11 com proposta."** (era "13 obras orçadas, até R$ 24,5 milhões." — item 1; a maior proposta some da frase mas continua no HUD) | O sistema lê o desenho, mede e orça. Desvio máximo de 0,25% contra a SINAPI nos 19 serviços conferidos. Idealizei e dirigi; o código, com assistentes de IA, sob minha revisão. | (dinâmico, sem mudança) R$ 24,5 mi / maior proposta → 0,25% / desvio máx. vs. SINAPI → nº obras / no sistema | A gestão de obra deste sistema ainda não rodou em obra real. |
| 5 | sige | **"mai → set/2026"** (era "jul → set/2026" — item 4) | O SIGE ganhou versão nova: 50 módulos. | Cerca de 50 módulos em 6 áreas, entregas registradas de 22/07 a 14/09/2026. Portal do cliente e diário de obra em uso nos dois galpões da fazenda. | (dinâmico) nº módulos / em 6 áreas | — |
| 6 | casa + içamento | ago/2026 | O celeiro não cabe no caminhão. | B-36: duas caixas, três viagens. **No estudo**, o módulo sobe pelo balancim, cabos na vertical — por isso virou regra do orçamento. 37 decisões registradas. *(era "O módulo sobe pelo balancim, cabos na vertical" como fato — item 3)* | 37 / decisões registradas | Pré-dimensionado, sujeito à revisão do engenheiro responsável. |
| 7 | whatsapp + recuperado | ago → set/2026 | **"23 dias de diário só no WhatsApp."** (era "23 dias de obra perdidos no WhatsApp." — item 5; nada "se perdeu", ficou fora do sistema) | Nos dois galpões (22 baias, Light Steel Frame, obra desde junho), o diário saiu do sistema depois de 11/08; 28 atividades prontas apareciam atrasadas. | (dinâmico) nº dias / de diário recuperados | Recuperação lida numa cópia; no sistema em uso, a carga ainda não foi aplicada. |
| 8 | zip | set/2026 | Proposta assinável em 36 minutos. | Medidos: 11:35 → 12:11, ampliação de unidade de saúde com 26 ambientes e 328 m². À mão, cerca de 2 dias úteis (estimativa). | (dinâmico, da própria cena) min / 11:35 → hh:mm | — |

**Cartão final (`#end`):** `.eh` "Faltam 3 semestres para o diploma. / Não falta obra feita." (sem mudança) · `h1` "Cassio Viller" (sem mudança) · `.l1`: **"São José dos Campos/SP · orçamento, planejamento e custos"** (era "26 anos · São José dos Campos/SP · orçamento, planejamento e custos" — item 7) · `.l2` e `.cta` sem mudança.

Todos os números do apoio/HUD acima foram conferidos linha a linha em `portfolio/site/portfolio.html`: "13 obras no sistema, 11 com proposta" (meta description e `#sistema`), "Mai–Set/2026" e "cerca de 50 módulos em 6 áreas" (`#sige`, linha 638/665), "duas caixas… três viagens" e "37 decisões registradas" e "pré-dimensionado (sujeito à revisão do engenheiro responsável)" (linhas 795–865), "42 diários… 11/08", "28 atividades", "23 dias… no WhatsApp", "a carga… ainda não foi aplicada no sistema em uso" (linhas 648–688), "11:35 → 12:11", "26 ambientes, 328 m²", "~2 dias úteis" (linhas 415–448). Nenhuma ocorrência de "26 anos" existe no portfólio — por isso ela sai da capa e do cartão final (item 7), sem substituto numérico inventado.

**Nota de arte (fora do texto, item 2):** a cena "duas construtoras" (por trás do capítulo k=2) tem post-its de textura mostrando "R$ 155.000" repetido quatro vezes e "R$ 150.500" riscado na quinta — um valor com cara de dado real que não existe em lugar nenhum do portfólio. Como o texto do capítulo já foi corrigido para não afirmar um valor, a textura da cena deveria trocar o número por um rótulo genérico (ex.: "MESMO VALOR" ou dígitos pixelizados/borrados) — ver requisito P3-08 abaixo.

## Requisitos para o plano

1. **P3-01 (MUST):** a frase do capítulo 2017→2024 é, nos três arquivos (`film.html` `CAPS[1][1]`, `index.html` capítulo `origem`, `portfolio.html` abertura do `.sub`), "Comecei pela contabilidade, não pela obra." — testável por igualdade literal de string nos três lugares.
2. **P3-02 (MUST):** a frase do capítulo "entrada na obra" no filme tem "vi" (1ª pessoa) como verbo antes de "cinco vezes", nunca "a obra" como sujeito de um verbo de digitar — testável verificando ausência de "obra digitava"/"obra digitou" e presença de um verbo conjugado em 1ª pessoa antes de "cinco vezes".
3. **P3-03 (MUST):** o kicker do capítulo SIGE no filme é "mai → set/2026" — testável comparando a string com o intervalo "Mai–Set/2026" citado em `portfolio.html`.
4. **P3-04 (MUST):** a frase do capítulo do sistema de orçamento nunca diz "obras orçadas" sem, na mesma tela (frase ou apoio), também dizer quantas têm proposta — testável por regex que rejeite "orçadas" isolado de "proposta" no par frase+apoio daquele capítulo.
5. **P3-05 (MUST):** qualquer menção ao módulo subindo pelo balancim com cabos na vertical é precedida por um qualificador de estudo ("No estudo", "Em estudo 3D" ou equivalente) na mesma frase/apoio — testável checando que a palavra "estudo" precede "balancim" no texto daquele capítulo.
6. **P3-06 (MUST):** a frase sobre os 23 dias no WhatsApp não usa a palavra "perdidos" (nem sinônimo de sumiço, como "sumiram"); descreve que os diários ficaram só no WhatsApp/fora do sistema, e a ressalva "recuperação lida numa cópia… a carga ainda não foi aplicada" permanece literal — testável por ausência de "perdid" no texto e presença da ressalva exata.
7. **P3-07 (MUST):** a string "26 anos" não aparece em nenhum elemento de texto de `film.html` (kicker de `CAPS[0]`, `#cover .a`, `#end .l1`) nem é reintroduzida em qualquer correção futura, pois não existe em `portfolio.html` — testável por grep de "26 anos" no HTML/JS do filme.
8. **P3-08 (SHOULD):** a textura dos post-its da cena "duas construtoras" não repete um valor monetário específico ("R$ 155.000" ou qualquer outro) como se fosse dado real; usa um rótulo genérico ou número ilegível — testável comparando visualmente o quadro renderizado contra a ausência desse valor em `portfolio.html`.
9. **P3-09 (SHOULD):** a velocidade de leitura efetiva do `apoio` de cada capítulo (palavras ÷ [0,76 × duração do capítulo em segundos] × 60) fica em até ~200 wpm; capítulos acima disso (hoje: todos exceto a abertura) são candidatos a cortar palavras do apoio (não da ressalva) ou a ganhar mais segundos de duração — testável recalculando o wpm de cada `CAPS[k][2]` contra `DUR[k]` sempre que o texto mudar.

## Riscos e armadilhas

- **O apoio do filme já era denso demais antes mesmo das correções de honestidade.** Como mostra a seção de pesquisa, oito das nove cenas ultrapassam ~200 palavras por minuto de leitura efetiva — a correção de conteúdo (itens 1, 3, 5, 6) trocou palavras por outras palavras, sem reduzir a contagem total; se a implementação também aceitar o requisito P3-09, o corte de palavras deve vir do meio do apoio (dados redundantes com o HUD), não das ressalvas, que a rodada 2 já protegeu como "nunca apagar".
- **O teste automatizado tem a frase antiga como valor esperado.** `portfolio/tests/check_historia.py`, linha 44, espera literalmente "Comecei no centavo, não na parede." — trocar a frase em `index.html` sem atualizar esse teste quebra a suíte; isso é trabalho de quem implementa (não desta rodada de pesquisa), mas precisa entrar na mesma tarefa.
- **A capa e o cartão final ficam com uma linha mais fraca depois de tirar "26 anos".** "São José dos Campos/SP" sozinha é uma informação de baixo impacto para ocupar a posição de destaque (`.a` na capa, primeira metade do `.l1` no final). Uma alternativa não testada aqui, para quem implementar considerar: subir a frase de cargo-alvo ("Orçamento, planejamento e custos de obra", que hoje já está em `.f`) para essa posição, e deixar a cidade só no `.f`/`.l2`.
- **O filme comprime 17 capítulos da página em 9 — isso é compressão editorial, não erro, mas duas informações fortes ficam de fora do texto visível do filme:** a mudança de cidade/curso em 2025 (capítulo `mudanca` da página) e os números de recuperação do diário (27,6% → 44,7% vs. 60,8% planejado, capítulo `recuperado`). O capítulo 7 do filme (WhatsApp) já cobre a ressalva da recuperação, mas não os três percentuais — se algum dia sobrar orçamento de palavra (após resolver o P3-09), esses três números são o dado mais forte da história e o candidato natural a entrar primeiro.
- **Post-its da cena "duas construtoras" (item 2) não são texto de roteiro — são textura 3D.** Esta persona registra o requisito (P3-08) mas não pode corrigi-lo neste arquivo; fica para quem mexe em `film.html`/`render.py`.
- **"Mas vi o dado digitado cinco vezes." troca "a mesma informação" por "o dado".** É uma perda pequena de nuance (a repetição do *mesmo* dado, não de um dado qualquer) para caber em 7 palavras — mas o HUD da mesma cena já diz "5× / o mesmo dado", então a nuance não desaparece da tela, só migra de elemento.

## Fontes

- [House Sparrow Films — How to Script a Personal Branding Video That Truly Connects](https://housesparrowfilms.com/blogs/how-to-script-a-personal-branding-video-that-truly-connects/)
- [Content Beta — How to Write a 60 second Video Script?](https://www.contentbeta.com/blog/60-second-video-script/)
- [Influencers Time — Subtitle Rules for Muted Autoplay Feeds](https://www.influencers-time.com/silent-first-editing-subtitle-rules-for-muted-autoplay-feeds/)
- [CleanSubtitle — How Long Should Subtitle Lines Be? Character Limits Explained](https://cleansubtitle.com/blog/subtitle-line-length-guide)
- [Onecraft — Video Captions Best Practices: Style, Timing, Placement](https://onecraft.app/blog/video-captions-best-practices/)
- [BlueCube Media — How to Build a Consistent Brand Narrative Across Channels](https://bluecube.com.sg/blogs/how-to-build-a-consistent-brand-narrative-across-channels/)
- Números conferidos diretamente em `portfolio/site/portfolio.html` (meta description; seções `#sistema`, `#sige`, `#modular`, `#orcamento`, diário/WhatsApp) e em `portfolio/site/index.html` (capítulos `origem`, `mudanca`, `obra`).
