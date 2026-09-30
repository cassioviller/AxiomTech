# ANDAMENTO — registro para retomar se a sessão cair

Atualizado em 24/09/2026. Leia de cima para baixo; o último bloco é o estado atual.

## Onde está cada coisa
- `PLANO.md` — plano geral (fases 0–5). Fases 0–4 feitas.
- `PLANO-REVISAO.md` — plano da revisão multiagente (rodadas de propostas → integração → verificação).
- `portfolio/revisao/REVISAO.md` — achados (23 itens) e decisões padrão do portão (A–H) que os agentes seguiram.
- `portfolio/revisao/CHANGELOG.md` — cada mudança do workflow, por agente e achado (inclui "Correção 1" e "Correção 2").
- `portfolio/revisao/PENDENCIAS.md` — o que o Cássio precisa confirmar.
- `portfolio/revisao/propostas/` — propostas dos agentes dono, colega, acess (ia, eng, hist, juridico caíram por erro de API 529/500; o integrador aplicou esses achados direto da REVISAO.md).
- Site no ar: porta 5000 (`python3 portfolio/servir.py 5000 --bind 0.0.0.0 --directory portfolio/site`, servidor com Range; é o Run do `.replit`).
- Axiom: movido para `axiom/` e fora do git (`.gitignore`). Nada commitado ainda além do `e28d9e3`.

## Feito nesta sessão (ordem cronológica)
1. Currículo 1 página, 3 folhas de caso em PDF, site "prancha de obra", 2 maquetes 3D (three.js 0.186 em `site/vendor/`).
2. Axiom retirado do git; `.replit` passou a servir o portfólio.
3. Maquete "A casa viaja": caixa girada 90° na carroceria, caminhão anda de frente (`maquetes.js`).
4. Página: resumo de 3 colunas por caso (problema / o que fiz / resultado), 5 blocos "Ver…" recolhidos, ledes encurtados, JSON-LD Person.
5. Revisão por 10 leitores → `PLANO-REVISAO.md` → workflow rodado (27 agentes, 44 min). Resultado:
   - 21 achados aplicados (1–6, 8–22). Não aplicado: 7 (sem print anonimizado do registro de engenharia).
   - Sigilo: agente pixelou nome do cliente ("UPA Bertioga", "203.1809") nos prints `t1..t4.webp` e no `configurador-b36.webp`. Bunker removido. "licenciado" → "em uso".
   - Engenharia: "0,25% contra a Caixa" → "reproduz as composições SINAPI a 0,25%"; "cálculo/estudo estrutural" → "pré-dimensionamento, sujeito à revisão do engenheiro responsável".
   - Primeira tela: parágrafo de história, cargo-alvo, termos da oferta; contato com "Faltam 3 semestres…".
   - Currículo: agente `cv` aplicou o mesmo; "Correção 1" tirou os níveis das ferramentas (FALSO POSITIVO — o CV original v4 tinha níveis; restaurar).
   - Duas rodadas de correção; 9 "falhas" restantes do verificador de fatos, quase todas falsos positivos porque ele não leu o BRIEF.md (que está fora do git mas existe no disco).

## Estado atual (01:50) — REVISÃO CONCLUÍDA
- [x] 9 falhas restantes resolvidas (4 corrigidas, 5 mantidas com fonte) — ver tabela abaixo e o fim de `PENDENCIAS.md`.
- [x] Níveis das ferramentas restaurados no currículo.
- [x] `./build.sh` rodado; primeira tela e prints pixelados conferidos por screenshot.
- [x] PENDENCIAS.md atualizado.
- [x] Commit — feito nas rodadas seguintes (ver CHANGELOG.md).
- Próximos passos possíveis: responder as pendências A–H de `PENDENCIAS.md`; Fase 5 do PLANO.md (vídeo 45 s, PDFs longos); publicar (Deploy estático do Replit já configurado).

## As 9 falhas restantes do verificador "fatos" e a decisão
| Trecho | Decisão |
|---|---|
| "· 26 anos" na primeira tela | REMOVER (idade não é obrigatória e permite deduzir nascimento). |
| "desde os 17" no parágrafo | TROCAR por "desde 2017" (dado registrado). |
| "3,8 t" no HUD da maquete | MANTER — vem da `cena5.html` aprovada e do BRIEF (legenda "3,8 t · 4,12 m…"). |
| "3.343 verificações" (site e currículo) | MANTER — número exato está no BRIEF §2.1 e no Portfolio_SIGE.pdf. |
| Nome completo no JSON-LD | MANTER — nome civil está no BRIEF; útil para máquinas. |
| "(2020–2024)" UNIFEI no currículo | MANTER — BRIEF, tabela de trajetória. |
| "Estruturas metálicas" (Estruturas do Vale) | MANTER — BRIEF cena 3 ("canteiro de estruturas metálicas"). |
| "redigi contratos de empreitada e de mão de obra" | CORRIGIR: "revisei contrato de empreitada e redigi contrato de mão de obra". |
| Carimbo "Jul–Set/2026" (já corrigido para "VEKS · 2026" na Correção 2) | OK. |

## Estado em 24/09/2026 — rodada 8 (o filme como fundo da história) CONCLUÍDA
- Branch `historia-scrollytelling` (já integrado em `main`); spec `docs/superpowers/specs/2026-09-23-filme-fundo-design.md`; plano `docs/superpowers/plans/2026-09-24-filme-fundo.md` (12 tarefas, um commit por tarefa mais os de correção); changelog `portfolio/revisao/CHANGELOG.md`, rodada 8.
- Site no ar: `python3 portfolio/servir.py 5000 --bind 0.0.0.0 --directory portfolio/site` (o Run do `.replit`; precisa de Range).
- Regenerar os clipes: `python3 portfolio/filme/render_clipes.py`; trailer de envio: `python3 portfolio/filme/render.py` → `portfolio/filme/saida/historia-960.mp4`.
- Conferir tudo: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_site.py`.
- Próximos passos: o merge de `historia-scrollytelling` em `main` foi feito em 24/09/2026 (fast-forward, 54 commits, branch apagado); falta: push para o GitHub; deploy estático; `python3 portfolio/tests/check_historia.py --origem <URL>` na origem publicada; teste num iPhone real; pendências do Cássio (idade, UNIFEI, estágio/júnior, trailer vertical).

## Estado em 24/09/2026 — rodada 9 (ajustes dos prints e da revisão) CONCLUÍDA
- Branch `historia-rodada-9` integrado em `main`; plano `docs/superpowers/plans/2026-09-24-historia-rodada-9-ajustes.md` (12 tarefas); changelog rodada 9.
- Foco vertical por clipe: `foco-alto` em obra, casa, whatsapp e içamento; `foco-baixo` fica disponível, hoje sem uso (o `escala` não usa foco).
- O trailer de envio (`portfolio/filme/render.py`) não foi regerado e ainda tem a câmera antiga do restaurante: rodar `render.py` antes de enviar.
- Conferir tudo: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_filme.py --cenas && python3 portfolio/tests/check_site.py`.
- Próximo: o plano irmão `2026-09-24-historia-cenas-novas.md` (cinco cenas novas: mudança, galpões, precisão, método, convite); depois push, deploy, `--origem`, iPhone real.

## Estado em 29/09/2026 — site v2, fase 1 (piloto) CONCLUÍDA, aguardando aprovação do Cássio
- Branch `site-v2`; spec `docs/superpowers/specs/2026-09-25-site-v2-design.md`; plano `docs/superpowers/plans/2026-09-25-site-v2-piloto.md`.
- O protótipo (16 capítulos) está no branch `historia-cenas-novas`, sem merge em `main`.
- Conferir: `python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador && python3 portfolio/tests/check_v2.py --video`.
- Ressalvas para o Cássio olhar: as texturas de pasto e terra têm manchas grandes e o conjunto ainda parece maquete; o vídeo ficou em crf 33 (2,43 MB) para caber no teto de 2,5 MB; nos prints anonimizados o contorno das palavras borradas ainda se adivinha.
- Próximo: o Cássio aprova (ou corrige) o padrão visual do piloto; depois a fase 2 (casos 2 e 4, caso 1 com os originais, abertura com cena, `v2.html` vira `index.html`).

## Estado em 30/09/2026 — site v2, fase 2 CONCLUÍDA, aguardando aprovação do Cássio
- Branch `site-v2-fase-2`; plano `docs/superpowers/plans/2026-09-29-site-v2-fase-2.md`; changelog rodada 12.
- `site/index.html` = site v2 (abertura com cena, casos 2, 3 e 4, trajetória, fechamento); `site/historia.html` = protótipo; `site/v2.html` redireciona.
- Vídeos: `python3 portfolio/cenas/render.py --so <caso>` (≈ 1 h cada no Replit, um de cada vez, em segundo plano; log em `portfolio/cenas/saida/render-<caso>.log`). Se a sessão cair no meio, rodar o mesmo comando de novo: desde 30/09 os quadros ficam em `saida/<caso>-mestre-quadros/` e o render retoma do primeiro que falta.
- Conferir: `python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador && python3 portfolio/tests/check_v2.py --video && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_site.py`.
- Pendente do Cássio: os prints originais do caso 1 (36 minutos); a decisão sobre o sigilo dos nomes borrados no portal do SIGE; a aprovação visual das três cenas novas.
- Próximo: o caso 1 quando os originais chegarem (plano curto); a fase 3; push, deploy, `--origem`, iPhone real.

## Estado em 30/09/2026 — rodada 13 (sigilo do portal, 36 minutos no caso do orçamento)
- Branch `site-v2-fase-2`, depois do commit `c36eb06` (trilho ao lado do documento). Sem plano formal: três ajustes pequenos, changelog rodada 13.
- O Cássio não manda mais prints: o caso 1 (36 minutos) fica sem cena própria (emenda de 30/09 no spec) e entra como linha da medida no caso do orçamento.
- Sigilo: tarjas opacas nos prints do portal do SIGE (`p-portal`, `p-celular`, `p-diario-portal`), docs regerados, `v2-sige.mp4` regravado.
- Conferir: `python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador && python3 portfolio/tests/check_v2.py --video && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_site.py`.
- Caso 4: telhado em kit montado peça a peça pelo guindaste (pedido do Cássio); `v2-modulares.mp4` regravado.
- Prints de aprovação em `portfolio/cenas/saida/prints-fase-2/` (fora do git).
- Próximo: a fase 3 (texto do `portfolio.html` e do currículo pelas regras do spec §5); push, deploy, `--origem`, iPhone real.

## Estado em 30/09/2026 (21h) — rodada 14 (realismo das cenas), EM ANDAMENTO
- Commit `ded4016`: céu pintado com PMREM, materiais PBR procedurais, capim, vidro, árvores no kit; caso 4 monta o telhado com a câmera na obra.
- Depois dele, sem commit (a sessão caiu às 20:49): as quatro cenas ganharam o entorno — canteiro completo no SIGE e nos modulares (relevo na praça, vala, poças, veículos, materiais, cercas, gado), sala mobiliada na abertura e no orçamento (janela, estante, objetos na mesa). `portfolio/cenas/_sige_antes.html` = cópia do `caso-sige.html` do HEAD (comparação antes/depois; não versionar).
- Materiais do kit refeitos (mapeamento em metros, um desenho por revestimento, relevo em metros; ver CHANGELOG rodada 14); fase 3 do texto feita (portfolio.html, currículo 1 página, folha dos 36 min). Suítes OK (check_filme falha como desde a fase 2: testa o filme antigo). Quadros de conferência em `portfolio/cenas/saida/prints-r14b` e `-r14c`. Vídeos: regravar em cadeia abertura, veks, sige, modulares.
