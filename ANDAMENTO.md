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
- 01/10: abertura (`0ad1d5a`), veks e sige (`03edd2b`) regravados. Modulares parou no quadro 103 (limite de 2 h da tarefa em segundo plano) e foi retomado às 13h: 288 quadros, 2,46 MB em crf 35 (teto do script: 36). `check_v2.py` (normal, `--navegador`, `--video`) OK. Rodada 14 dos vídeos concluída.
- Para o Cássio olhar: no pôster dos modulares a prancha "como cada caixa viaja" sai cortada à direita (o "=" fica sem o resultado e a legenda é cortada em "selagem"); já era assim antes desta regravação.

## Estado em 01/10/2026 (tarde) — rodada 15 (prancha inteira, render local na GPU)
- Pôster dos modulares: a prancha "como cada caixa viaja" entra inteira (2308×1443, margem branca); changelog rodada 15.
- Render em qualidade alta no PC do Cássio (Windows, RTX 3060) por outra sessão do Claude Code: `portfolio/cenas/RENDER-LOCAL.md`. O branch `site-v2-fase-2` vai para o GitHub (`origin`); os vídeos voltam por push e aqui se faz `git pull`.
- Pendente: decisão do Cássio sobre o teto de 2,5 MB por vídeo (subir ou AV1 com H.264 de reserva); depois deploy, `--origem`, iPhone real.

## PARA A SESSÃO NO PC DO CÁSSIO (Windows, RTX 3060) — ler primeiro, 01/10/2026
- Branch de trabalho: `site-v2-fase-2` (commit da rodada 15 em diante). O site é `portfolio/site/index.html`; servir com `python portfolio/servir.py 5000 --directory portfolio/site`.
- **O que fazer aí, na ordem:**
  1. Seguir `portfolio/cenas/RENDER-LOCAL.md` (instalar git/python/ffmpeg/playwright; `python portfolio/cenas/render.py --gpu --qualidade alta --so modulares`). O modo `--gpu` e a qualidade alta **nunca foram executados** (no Replit não há placa): se der erro, corrigir no `render.py`/`kit.js` e anotar aqui.
  2. O vídeo `v2-modulares.mp4` publicado ainda tem a prancha cortada (a correção da rodada 15 mudou o documento e a cena, mas o vídeo não foi regravado): o render do passo 1 resolve. Conferir no pôster `v2-modulares.webp` que a prancha aparece inteira, com "= UNIDAS NA OBRA · 6,00 × 6,00 m".
  3. Depois os outros três casos (`abertura`, `veks`, `sige`) em qualidade alta.
  4. Commit só dos `portfolio/site/video/v2-*.mp4|webp` e push.
- **Plano do render realista ("tipo Lumion")**: `docs/superpowers/specs/2026-10-01-render-realista.md` (pesquisa, ferramentas verificadas, plano revisto). Resumo: Blender 5.2.2 LTS + Cycles OptiX por linha de comando, assets CC0 do Poly Haven e do ambientCG por API, piloto no caso 4. Ainda não começou; depende de duas decisões do Cássio: (a) teto do vídeo — AV1 + H.264 de reserva (recomendado) ou subir de 2,5 MB para 4–5 MB; (b) começar pelos assets reais nas cenas three.js ou direto pelo piloto no Blender.
- **Fora do git (não existem aí):** `BRIEF.md`, os zips com os originais (`casas pre moldadas (1).zip`, `saida.zip`…), `portfolio/cenas/saida/`. Por isso **não rodar `cenas/documentos.py`** no PC; os documentos já recortados estão em `portfolio/site/docs/`.
- **Sigilo:** nada de nome de cliente nem endereço legível; os prints do portal do SIGE usam tarjas opacas. Só assets CC0, com a origem anotada.
- Testes: no PC basta `python portfolio/tests/check_v2.py --video`; os de cena (`--navegador`) foram calibrados no SwiftShader do Replit. `check_filme.py` falha desde a fase 2 (testa o filme antigo) — conhecido.
- Histórico e decisões: este arquivo (de cima para baixo), `portfolio/revisao/CHANGELOG.md` (rodadas 8–15), specs e planos em `docs/superpowers/`.

## 01/10/2026 (fim da tarde) — render realista, primeira etapa: código pronto para o piloto no PC
- Decisões do Cássio: seguir o recomendado (Blender + Cycles na RTX 3060, operado pelo Claude Code; AV1 com H.264 de reserva).
- Pronto e testado no Replit em CPU: `cenas/exportar.py`, `blender/baixar_assets.py`, `blender/montar.py`, `render.py --quadros`. **Roteiro do piloto: `portfolio/blender/LEIA-ME.md`** (fazer depois do passo 1 do bloco "PARA A SESSÃO NO PC", ou no lugar dele: o render do Blender substitui o do three.js).
- Resultado do teste (caso 4, 960×540, 48 amostras, CPU): luz, sombras e chão convincentes; **os modelos continuam caixas** (caminhão, guindaste, árvores de esferas) — é o que falta para sair do ar de maquete. Próximos passos, na ordem: (1) piloto na GPU e tempo por quadro; (2) árvores e capim do Poly Haven no lugar das marcadas em `cena.json`; (3) luzes dos interiores; (4) chanfros e sujeira nos procedurais; (5) AV1 + H.264 em `<source>` (não feito: mexe no `clipes.js`/`v2.js`, que buscam o vídeo por `currentTime`, e precisa ser medido com os quadros novos).
- No Replit o Blender só roda com `LD_LIBRARY_PATH` montado à mão (libX11, libSM, libICE… do nix); não está instalado de forma permanente. No PC é instalação normal.

## 02–03/10/2026 — render realista no PC do Cássio (RTX 3060): os 4 vídeos v2 regravados no Blender
- Pronto: `site/video/v2-{modulares,abertura,veks,sige}.mp4|webp` renderizados no Blender 5.2.2 LTS + Cycles a 1920×1080 (até 256 amostras adaptativas, OIDN, desfoque de movimento) e encodados por `render.py --quadros`. `check_v2.py` e `check_v2.py --video`: OK.
- **Tempo por quadro medido (RTX 3060, CUDA, 1920×1080, `--visual cinema`)**, mediana dos blocos: modulares 52 s (≈ 42–46 s com a placa livre; num trecho a placa foi dividida com outro processo e chegou a ~115 s), abertura 44 s, veks 43 s, sige 34 s. Total ≈ 960 quadros em ~12 h, em blocos de 30 quadros (< 30 min cada) por um executor fora da sessão.
- **OptiX não roda neste PC**: driver NVIDIA 561.17 (< 575) → `OPTIX_ERROR_INTERNAL_COMPILER_ERROR`; tudo em `--dispositivo CUDA` (o denoise é OIDN, não depende do OptiX). Atualizar o driver deve acelerar.
- **`montar.py --visual cinema`** (o padrão continua o visual antigo): céu de fim de tarde (HDRI CC0), sol em lâmpada Sun quente + céu frio de preenchimento, névoa de distância no compositor (com AOV para o documento sair limpo), bruma no horizonte, chanfro e "desgaste" nos materiais (poeira de laterita, AO, brilho variável), foco automático suavizado, bloom, grão, tonalização dividida; árvores, capim, pedras, plantas, relógio e cadeira do Poly Haven (CC0, `assets.json`); luz de teto nas salas e a luminária acesa no caso 2.
- **Todos os objetos modelados por script** no lugar das caixas do kit (os grupos marcados com `userData.asset` nas cenas e exportados em `grupos` pelo `exportar.js`): `blender/veiculos.py` (caminhão, guindaste, picape), `blender/objetos.py` (canteiro do modulares), `objetos_veks.py` (escritório: monitor, teclado, impressora, cadeira, gabinete…), `objetos_abertura.py`, `objetos_sige.py` (painéis LSF com perfis C/U e fitas em X, pilares I, gerador, contêiner, gado…). Nenhum texto, marca ou nome nos modelos.
- Correções nas cenas three.js (o site não muda de aparência): telhado do celeiro montado girado 90° (frontão sobre os portões; `caso-modulares.html`); `exportar.js` repete a pose de cada quadro até estabilizar (o guindaste mirava a partir da pose do quadro anterior e o quadro 0 saía diferente do 1 — `check_v2 --video` acusava "o início não está parado").
- **Prancha do B-36 redesenhada sem móveis** (`cenas/prancha_b36.py` → `site/docs/b36-caixas.webp` e o recorte; mesmo tamanho e posições, destaque e recorte de `documentos.json` valem): a original tinha móveis sobrepostos. Usada no site, no modulares e na abertura.
- Ferramentas no PC (fora do git): Blender 5.2.2, ffmpeg 9.0.2 e ImageMagick 7.1.2 em `C:\Users\cassi\ferramentas` (o `check_v2.py` precisa do `magick` no PATH).
- Vídeos em alta qualidade (os mestres crf 16, 8–16 MB) em `portfolio/video-alta/v2-<caso>-alta.mp4`, fora de `site/` para não pesar no deploy; o vídeo do site sai com crf 32–36 para caber em 2,5 MB.
