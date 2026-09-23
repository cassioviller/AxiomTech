# Spec — o filme como trailer da história (rodada 3)

**Data:** 23/09/2026 · **Base:** pesquisa das 5 personas em `docs/superpowers/research/2026-09-23-filme/` (contexto em `00-contexto.md`) · **Parte de:** as specs da história (`2026-09-23-historia-scrollytelling-design.md` e `2026-09-23-historia-linha-do-tempo-design.md`), cujas regras continuam valendo.

## Objetivo
Aproveitar o `filme-codigo-fonte.zip` (9 dioramas three.js, legendas, capa e cartão final; 85 s) no site, **com o texto corrigido** pelas mesmas regras de honestidade da página, e trocar a frase da origem ("Comecei no centavo, não na parede.") por uma frase sobre a contabilidade.

## Decisão de caminho (a partir das personas)
- **C agora — o filme como trailer à parte** (Renata, Carla, Lia, Tiago): MP4 leve, **só por clique**, depois da história e antes da ficha, com **transcrição** em texto (o vídeo não tem áudio; texto queimado no quadro não serve de alternativa — WCAG 1.2.1).
- **B depois — dioramas ao vivo como fundo** (Tiago, Eduardo): exige um renderizador compartilhado só na página da história (o `portfolio.html` também usa `maquetes.js`). Fica para um plano próprio. Candidatos confiáveis (Eduardo): prédio do SIGE, restaurante das 13 obras, parede da VEKS; a cena "duas construtoras" e a do WhatsApp só depois dos ajustes; não usar a tabela da abertura como fundo.
- **A descartado** — vídeo avançado pelo scroll: pesado, engasga no iPhone e o texto gravado não é acessível.

## A frase da contabilidade
**"Comecei pela contabilidade, não pela obra."** (escolha da Lia, a partir da sugestão do Cássio) — idêntica em três lugares: capítulo `origem` da história, topo do `portfolio.html` ("Comecei pela contabilidade, não pela obra: folha, notas e balancete…") e capítulo 1 do filme. Prepara o "Mas na obra, vi a mesma informação digitada cinco vezes." sem repetir o "mas".

## O filme corrigido (texto exato)
| # | Kicker | Frase (≤ 7 palavras) | Apoio (≤ 200 palavras/min) | HUD | Ressalva | Duração |
|---|---|---|---|---|---|---|
| 0 | Cássio Viller · portfólio | Número sem origem custa caro na obra. | Nove capítulos, de 2017 a 2026. Cada número tem origem: medido, derivado ou a confirmar. | — | — | 10,5 s |
| 1 | 2017 → 2024 | Comecei pela contabilidade, não pela obra. | Escritório contábil da família desde 2017. Na UNIFEI, fiscal do DCE (2022) e diretor de vendas da InLoco Jr. | 8 anos · de rotina contábil | — | 8 s |
| 2 | fev/2025 → mar/2026 | Mas vi o dado digitado cinco vezes. | Meio período, em paralelo: produção na V Alves (CLT) e estágio na Estruturas do Vale, onde nasceu o SIGE. | 5× · o mesmo dado | — | 8 s |
| 3 | mar → set/2026 | Na VEKS, toda conta repetida virou ferramenta. | PJ, 6 meses, cumprido até o fim, com a V Alves até julho. Calculadora de parede e classificador de caixa. | 6 meses · contrato PJ cumprido | — | 8 s |
| 4 | mai → set/2026 | O SIGE ganhou versão nova. | Cerca de 50 módulos em 6 áreas; entregas de 22/07 a 14/09/2026. Portal e diário em uso nos galpões. | ~50 módulos · em 6 áreas | — | 8 s |
| 5 | jul → set/2026 | 13 obras no sistema, 11 com proposta. | Lê o desenho, mede e orça. Nos 19 serviços SINAPI conferidos, desvio máximo de 0,25%. Código com assistentes de IA. | R$ 24,5 mi → 0,25% → 13 obras no sistema | A gestão de obra deste sistema ainda não rodou em obra real. | 8,5 s |
| 6 | ago/2026 | O celeiro não cabe no caminhão. | B-36: duas caixas, três viagens, 37 decisões registradas. No estudo, o módulo sobe pelo balancim, cabos na vertical. | 37 · decisões registradas | Pré-dimensionado, sujeito à revisão do engenheiro responsável. | 8,5 s |
| 7 | ago → set/2026 | 23 dias de diário só no WhatsApp. | Depois de 11/08, o diário saiu do sistema; 28 atividades prontas apareciam atrasadas nos dois galpões. | N dias · de diário recuperados | Recuperação lida numa cópia; no sistema em uso, a carga ainda não foi aplicada. | 8,5 s |
| 8 | set/2026 | Proposta assinável em 36 minutos. | Medidos: 11:35 → 12:11, ampliação de unidade de saúde, 26 ambientes, 328 m². À mão, cerca de 2 dias úteis (estimativa). | (relógio da cena) | — | 9 s |

Ordem das cenas cronológica: abertura, escritório, duas construtoras, VEKS, **SIGE (mai)**, **restaurante (jul)**, celeiro, WhatsApp, 36 minutos (`ORDER=[5,0,1,6,3,7,8,2,4]`); cartão final de 8 s; total **85 s**.

**Adereços e textos fora das legendas:**
- Nome **Cássio Viller** com acento (etiqueta, capa, cartão final); **sem "26 anos"** (o portfólio não traz a idade).
- Tabela da abertura só com quantidades que o portfólio sustenta: Área de projeção (UPA) 328 m² *medido*; Ambientes 26 un *medido*; Placa de gesso por m² 2,11 m² *derivado*; Montante por m² 2,91 m *derivado*; Aço da casa 8 × 6 m 541 kg *derivado*; Pé-direito — m *a confirmar*.
- Post-its das duas construtoras: "MESMO DADO" em quatro cópias e "OUTRO DADO" riscado na quinta (sem valor em reais).
- Planilha do escritório: células "· · ·"; a célula em destaque passa de "não bate" a "confere" (sem valor inventado).
- As 5 legendas antigas por cena (`st.cap`, nunca exibidas, com "Aos 17", "sob licença", "perdidos") saem do código.

## Requisitos
| ID | Requisito | Personas |
|---|---|---|
| F-01 | A frase da contabilidade é idêntica na história, no portfólio e no filme; nenhuma ocorrência de "centavo, não na parede" | P3-01 |
| F-02 | Legendas, ordem e durações do filme exatamente como a tabela acima; frase ≤ 7 palavras; apoio ≤ 200 palavras/min (a 76% do capítulo) | P3, P2 |
| F-03 | Nenhum número no filme (HTML visível + todo texto literal do script, menos cores e fontes) que o portfólio não sustente; proibidos "26 anos", "155.000", "150.500", "Cassio", "orçadas", "perdidos", "a obra digitava", "no centavo" e as quantidades antigas; obrigatórios "Cássio Viller", "No estudo", "Pré-dimensionado", "numa cópia", "a carga ainda não foi aplicada" | P2-01…P2-10 |
| F-04 | O filme mora no projeto (`portfolio/filme/`: `film.html`, `three.min.js`, `fonts/`, `render.py`, `corrigir_filme.py`, `README.md`); o mestre de 1280×720 fica em `portfolio/filme/saida/` (ignorado pelo git) | P4 |
| F-05 | Render aqui, sem o Chromium do Playwright (não roda no Replit): `render.py` usa o Chromium do sistema; versão web `site/video/historia.mp4` H.264 960×540, sem áudio, `+faststart`, ≤ 12 MB, duração = 85 s; capa `site/video/historia.jpg` 960×540 (a ficha de abertura) | P4, P5 |
| F-06 | Trailer na história: `<section class="filme" id="filme">` depois da história e antes da ficha; título com a duração real ("A história em 85 segundos"); `<video controls preload="none" playsinline poster=… width="960" height="540">` **sem autoplay nem loop**; `<details>` "Transcrição do filme (o vídeo não tem áudio)" com as 9 legendas; o convite ganha "Assistir ao filme ↓" | P1-01, P1-02, P5-02, P5-04 |
| F-07 | Nada depois da história fica coberto pelo palco: depois de "Assistir ao filme ↓", o vídeo está à vista; no fim da página, a ficha está à vista (em 390 e 1280 px). Achado no ensaio: o palco `sticky` com `margin-bottom:-100vh` passava uma tela além do `</main>` e já escondia a ficha | P5 (ensaio) |

## Decisões (rulings)
1. **Duração mantida em 85 s** (Renata sugere 30–60 s como ideal, não como regra): o apoio foi encurtado até caber em ≤ 200 palavras/min em cada capítulo, e a duração aparece no título antes do clique. Custo: um trailer mais longo que o ideal para recrutador.
2. **Correções aplicadas por script** (`corrigir_filme.py`) sobre o `film.html` do zip, em vez de colar o arquivo inteiro no plano — reprodutível e conferido: o script gera um arquivo idêntico ao do ensaio.
3. **A "duração" é o único número novo na página** e vem do próprio vídeo (ffprobe), não de uma lista de exceções.
4. **HUD "8 anos de rotina contábil"** mantido: está no currículo ("oito anos de rotina contábil"). Custo: fica desatualizado com o tempo.
5. **Caminho B em plano separado.** Custo: os capítulos sem imagem continuam com o fundo tipográfico até lá.

## Em aberto (do Cássio)
A idade (a capa tinha "26 anos"); UNIFEI 2020–2024 (currículo) × 2022–2024 (conversa); estágio/júnior; se o trailer deve ter uma versão curta (30–60 s) para o LinkedIn.
