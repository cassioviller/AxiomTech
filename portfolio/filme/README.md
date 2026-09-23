# O filme da história (trailer de 85 s)

Fonte: `filme-codigo-fonte.zip` (v4), corrigido pelas regras de honestidade da página
(spec `docs/superpowers/specs/2026-09-23-filme-trailer-design.md`).

## Arquivos
- `film.html` — 9 dioramas em three.js r128 (`three.min.js`, sem CDN), legendas, capa e cartão final.
  Determinístico: `window.renderAt(T)` desenha o quadro do segundo T.
- `corrigir_filme.py` — aplica as correções ao `film.html` do zip (já aplicadas aqui; só rode sobre o original).
- `render.py` — Playwright chama `renderAt(i/30)` quadro a quadro e manda para o ffmpeg.
- `fonts/` — Barlow Condensed 600/700, IBM Plex Sans 400, IBM Plex Mono 500.

## Como gerar o vídeo (Replit)
    python3 -m pip install --user playwright     # uma vez
    python3 portfolio/filme/render.py            # ~13 min; gera o mestre e a versão web
    python3 portfolio/tests/check_filme.py --video

O Chromium que o Playwright baixa não roda no Replit (faltam bibliotecas do sistema): o
`render.py` usa o Chromium do sistema (`shutil.which("chromium")`). Saídas:
- `portfolio/filme/saida/historia-1280.mp4` — mestre 1280×720 (fora do site, ignorado pelo git)
- `portfolio/site/video/historia.mp4` — 960×540, H.264, sem áudio, `+faststart`
- `portfolio/site/video/historia.jpg` — capa (a ficha de abertura)

## Onde editar
- Textos: `CAPS[]` = [kicker, frase ≤ 7 palavras, apoio, hud(t), ressalva] — e o mesmo texto em
  `CAPITULOS` de `portfolio/tests/check_filme.py` (a checagem compara os dois).
- Ordem e duração: `ORDER`, `DUR`, `ENDD`. Capa: `<div id="cover">`. Cartão final: `<div id="end">`.
- Cada cena: um bloco `(function(){ ... })()` com `st.cam` (chaves de câmera) e `st.run(t)` (t de 0 a 10).
- Depois de editar: `python3 portfolio/tests/check_filme.py` (textos) e renderizar de novo.
