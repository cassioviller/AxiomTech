# O filme da história

Fonte: `filme-codigo-fonte.zip` (v4), corrigido pelas regras de honestidade da página por `corrigir_filme.py`
(rodadas 3 e 4). Hoje o filme tem dois usos:

1. **Clipes de fundo da história** (`site/index.html`): 11 trechos curtos e mudos, sem legenda, HUD, capa nem cartão,
   um por capítulo, cujo tempo avança com a rolagem. Spec: `docs/superpowers/specs/2026-09-23-filme-fundo-design.md`.
2. **Trailer de envio** (85 s, com legendas): para mandar a uma recrutadora pelo WhatsApp ou LinkedIn. Não está no site.

## Arquivos
- `film.html` — 9 dioramas do trailer + 3 cenas portadas da página (`SC[9]` casa, `SC[10]` içamento, `SC[11]` 36 min),
  three.js r128 (`three.min.js`, sem CDN). Determinístico: `renderAt(T)` desenha o segundo T do trailer;
  `renderCena(i, t)` desenha a cena `i` no tempo local `t` (0..10). `?limpo` esconde todo o DOM por cima do canvas.
- `corrigir_filme.py` — aplica as correções ao `film.html` do zip (só rode sobre o original).
- `render_clipes.py` — a tabela `CLIPES` (capítulo → cena → trecho) e o render dos clipes e pôsteres.
- `render.py` — o trailer de envio, quadro a quadro.
- `fonts/` — Barlow Condensed 600/700, IBM Plex Sans 400, IBM Plex Mono 500 (só o trailer usa).

## Como gerar (Replit)
    python3 portfolio/filme/render_clipes.py         # ~10 min; os 11 clipes + pôsteres em site/video/
    python3 portfolio/filme/render_clipes.py --so zip
    python3 portfolio/tests/check_filme.py --video   # clipes (peso, GOP, pontas paradas, pôster) e trailer se existir
    python3 portfolio/tests/check_filme.py --cenas   # ~20 s, Chromium: conteúdo das cenas portadas (SC[9..11]) e ?limpo
    python3 portfolio/filme/render.py                # ~13 min; trailer em filme/saida/historia-960.mp4 + .jpg

O Chromium do Playwright não roda no Replit (faltam bibliotecas): os scripts usam o `chromium` do sistema.
O site precisa de um servidor com `Range` (`portfolio/servir.py`): sem 206 o navegador não busca no vídeo.

## Como enviar o trailer
- **WhatsApp:** anexar `saida/historia-960.mp4` como **mídia** (≤ 16 MB; hoje ~2,7 MB), não como documento, para
  tocar na conversa. Mensagem sugerida: "Sou estudante de Engenharia Civil, 7º semestre, e miro orçamento, planejamento
  e custos, CLT ou PJ. Este filme de 85 s (sem áudio, legendado) conta a história; a página completa está em <link>."
- **LinkedIn:** upload nativo do MP4 (não link do YouTube); o mesmo texto no post; a capa `historia-960.jpg` como
  miniatura, se o LinkedIn pedir.
- Sem áudio de propósito: toca mudo no feed e no celular; tudo o que importa está escrito.

## Onde editar
- Textos do trailer: `CAPS[]` = [kicker, frase ≤ 7 palavras, apoio, hud(t), ressalva] — e o mesmo texto em `CAPITULOS`
  de `portfolio/tests/check_filme.py` (a checagem compara os dois). Ordem e duração: `ORDER`, `DUR`, `ENDD`.
- Mapa dos clipes: `CLIPES` em `render_clipes.py` (e o `ROTEIRO` de `check_historia.py` tem de bater).
- Cada cena: um bloco `(function(){ ... })()` com `st.cam` (chaves de câmera) e `st.run(t)`. Regra do texto pintado:
  nada que o `portfolio.html` não sustente (`check_filme.py` lê todo literal do script).
- Depois de editar: `python3 portfolio/tests/check_filme.py` e renderizar de novo.
