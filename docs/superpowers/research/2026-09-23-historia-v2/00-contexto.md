# Contexto comum das personas — rodada 2: a história na linha do tempo

## O que já existe (rodada 1, testada)
- `portfolio/site/index.html` — **página principal**: a história em 10 cenas (frase grande ≤ 10 palavras + linha de ressalva). Fundo em palco `position: sticky`, troca de cena quando a seção cruza o meio da tela (`IntersectionObserver`), crossfade, duas maquetes three.js amarradas ao scroll (`fig.__maquete.seek`), barra fixa com nome, cargo-alvo, currículo e WhatsApp, ficha de palavras-chave e rodapé. Sem JS ou com `prefers-reduced-motion`: cenas empilhadas e estáticas, cada frase com a sua imagem.
- `portfolio/site/historia.js` — a lógica das cenas; `portfolio/site/maquetes.js` — as cenas 3D (`36min`, `casa-viaja`), API `fig.__maquete = {frozen, dur, seek(t)}`.
- `portfolio/site/portfolio.html` — o portfólio completo (antes era o index). Âncoras: `#orcamento` (36 min), `#sistema` (sistema de orçamento), `#sige` (portal e diário), `#modular` (casas modulares), `#obra` (obras e projetos VEKS), `#ferramentas` (calculadora LSF, classificador de fluxo de caixa, padrão de PDFs, fluxo de compras), `#curriculo`, `#contato`.
- `portfolio/DESIGN.md` — estética de **prancha de obra**: carimbo "Folha 0X", linha de cota em ferrugem, papel `#ECEBE6`, tinta `#171F29`, ferrugem `#B5440E`, aço `#2E4763`; Barlow Condensed / IBM Plex Sans / IBM Plex Mono.
- Testes: `portfolio/tests/check_historia.py` (roteiro exato, números que o portfólio sustenta, ressalvas, contraste da faixa no pior caso, `aria-hidden`, `svh`; com `--navegador`, harness no Chromium em tempo real via DevTools Protocol) e `portfolio/tests/check_site.py` (portfólio).
- Pesquisa da rodada 1 (personas e fontes): `docs/superpowers/research/2026-09-23-historia/`. Spec da rodada 1: `docs/superpowers/specs/2026-09-23-historia-scrollytelling-design.md`.

## O que o Cássio pediu agora
"A proposta inicial é essa, agora só precisa ser desenvolvida." Nas quatro frentes: **impacto visual, mais história, acabamento e ligação com o portfólio** — e **"um storytelling de acordo com minha linha do tempo e de quando montei cada coisa"**.

## A linha do tempo (confirmada pelo Cássio)
| Quando | Marco |
|---|---|
| 2017 → hoje | Escritório contábil da família: folha, notas, balancete |
| 2022 → 2024 | UNIFEI (Itajubá), Engenharia Civil, 6 semestres; fiscal financeiro do DCE em 2022; diretor de vendas da InLoco Jr. (empresa júnior) de mar/2023 a dez/2024 |
| 2025 | Transferência para a Cruzeiro do Sul (EAD) e mudança para São José dos Campos; hoje no 7º semestre, faltam 3; Sistemas de Informação na PUC (EAD) em paralelo, 3º semestre |
| fev/2025 → jul/2026 | V Alves Construção: gerente de produção e operações (CLT, meio período) |
| abr/2025 → mar/2026 | Estruturas do Vale: estágio comercial (meio período). **Nasce o SIGE** (primeira versão, 10+ módulos) |
| mar/2026 → set/2026 | VEKS Engenharia (PJ, 6 meses) |
| mar–abr/2026 | Primeiros meses na VEKS: **calculadora de parede LSF/drywall** e **classificador do fluxo de caixa** |
| mai → set/2026 | **SIGE, versão atual** (entregas registradas de 22/07 a 14/09/2026) |
| 08/06/2026 | Começa a obra dos galpões (baias) que usa o SIGE |
| 9/jul → 21/set/2026 | **Sistema de orçamento**: 13 obras no sistema, 11 com proposta |
| ago/2026 | **Casas modulares** (B-36, FL-30, kitnet): arquivos de 07/08 a 02/09; 23 diários ficam só no WhatsApp depois de 11/08 |
| set/2026 | **Proposta em 36 minutos** (11:35 → 12:11); diários recuperados (lidos numa cópia do sistema; carga ainda não aplicada no sistema em uso) |

Atenção: há **sobreposição de vínculos** em 2025–2026 (V Alves + estágio, depois V Alves + VEKS). O portfólio já explica ("meio período, em paralelo com o estágio — as duas jornadas somadas davam um expediente inteiro"); a linha do tempo precisa tratar isso com a mesma honestidade.

## Direção escolhida (abordagem A — recomendada, as personas podem contestar)
**Linha do tempo como régua de obra**: uma régua de tempo persistente (linha de cota com 2017 · 2022 · 2025 · 2026) que avança com o scroll e marca o capítulo atual; a história vira **capítulos datados** na ordem acima; transições por capítulo; fundos **compostos** (render + tela + foto, menos "print de sistema cru"); uma **terceira maquete** a partir do estudo de içamento das casas modulares; cada capítulo com "ver o caso completo →" para a âncora certa do `portfolio.html`. Alternativas descartadas por ora: voo contínuo num único mundo 3D (B, caro e arriscado no celular) e vídeo de tela ligado ao scroll (C, depende de gravações).

## Material novo disponível (zip "casas pré-moldadas", cópia de trabalho fora do repositório)
Pasta: `/tmp/claude-1000/-home-runner-workspace/f9d44ef5-7d41-4ced-9ebe-ca35da9a73fc/scratchpad/casas/`
- Estudos 3D em HTML (three.js r128 via CDN, `MeshLambertMaterial`, ~10–25 KB cada): `icamento-3d.html` (içamento do módulo), `modulo-3d.html`, `modulo-comodos-3d.html`, `familia-p1-p2-p3-3d.html`.
- Renders e pranchas: `B36-render-externa.png`, `B36-render-balcao.png`, `B36-render-interior.png`, `render-fl30-pathtracer.png`, `celeiro-montado-opcoes.png`, `prancha-transporte-tiltup-gambrel.png` (usa gabarito de 3,40 m — número que o portfólio não traz), `kitnet-layouts-30m2.png`, `fachada-frontal-*.png`.
- **Não publicar:** contratos, fichas, termos e orçamentos `.docx`/`.html` (internos da VEKS).

## Regras que continuam valendo
Nenhum número novo que o portfólio não sustente; nenhuma ressalva apagada ("cópia do sistema", "estimativa", "ainda não rodou", "nos 19 serviços conferidos", "assistentes de IA"); não misturar telas do SIGE com as do sistema de orçamento; nada de nome de cliente, e-mail ou margem real; sem build, sem dependência nova (three.js já está vendorizado em `site/vendor/`); rolagem nativa; modo empilhado sem JS/movimento reduzido.

## Pendências menores da rodada 1 (podem entrar)
Relógio laranja da maquete com contraste ~2:1 sobre céu claro; cena do B-36 sem "pré-dimensionado (sujeito à revisão do engenheiro responsável)"; portas fixas no harness.
