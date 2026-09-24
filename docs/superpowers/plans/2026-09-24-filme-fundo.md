# O filme como fundo da história, avançado pela rolagem — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cada capítulo da história que tem cena ganha um clipe curto de vídeo, sem texto, no fundo do palco, cujo tempo avança com a rolagem; as três maquetes three.js da página viram clipes no estilo do filme; o trailer sai da página e a história deixa de rodar WebGL.

**Architecture:** O `film.html` ganha a flag `?limpo` (esconde todo o DOM por cima do canvas) e `renderCena(i, t)`, puro em (cena, tempo local); as três maquetes da página são portadas como cenas novas `SC[9..11]`, fora do trailer. Um `render_clipes.py` novo renderiza, por Playwright + Chromium do sistema, 11 clipes MP4 (960×540, 24 fps, H.264 High 3.1, GOP 4) e o pôster WebP de cada um. Na página, um `clipes.js` novo expõe o contrato `fig.__clipe = {dur, seek(t), frozen}` que `historia.js` já usa para as maquetes, movendo `currentTime` quantizado ao quadro; a carga é sob demanda, depois do `load`, a 600 px da cena, e cai para o pôster sem H.264, com economia de dados ou movimento reduzido. Um servidor com Range (`servir.py`) substitui o `http.server` porque sem 206 o Chrome ignora o seek.

**Tech Stack:** HTML/CSS estático; three.js r128 (só no `film.html`, fora do site); Python 3.12 (stdlib + Playwright para o render); Chromium 152 do sistema (com H.264 — conferido: `canPlayType('video/mp4; codecs="avc1.64001F"')` = `probably`); ffmpeg 6.1 com libx264 e libwebp.

**Spec:** `docs/superpowers/specs/2026-09-23-filme-fundo-design.md`. A pesquisa das 5 personas está em `docs/superpowers/research/2026-09-23-filme-fundo/`.

**Medições feitas antes de escrever o plano (valem para os `Expected:`):**
- 2 s da cena do restaurante em 960×540, 24 fps, crf 28, `-g 4 -bf 0`: 200 KB (≈ 100 KB/s). Onze clipes de 8–10 s somam ~96 s: perto do teto de 8 MB. O `render_clipes.py` reencoda o maior clipe com crf +1 (até 30) enquanto a soma passar de 8 MB.
- PSNR entre os quadros 0 e 7 (0,3 s) de um trecho do filme com a câmera andando: **27 dB**. O jitter e a curva de câmera do filme não param sozinhos; por isso o render **congela o tempo local** nos primeiros 0,3 s e nos últimos 0,5 s de cada clipe (`tempo_local()` em `render_clipes.py`). É o que faz "começa e termina parado" ser verdade por construção.
- Pôster WebP q75 de um quadro 960×540: 16 KB, PSNR 46,6 dB em relação ao PNG do quadro.
- DevTools: `Performance.getMetrics` expõe `TaskDuration`; `Input.dispatchKeyEvent` Tab move o foco; `Emulation.setEmulatedMedia` vira o `matchMedia` de `prefers-reduced-motion` em tempo real; `getEntriesByType('largest-contentful-paint')` vem vazio (o LCP precisa de `PerformanceObserver` com `buffered:true`).
- Altura do `<main>` hoje, em 390×800: 16000 px (14 capítulos × 800 + 3 longos × 1600).

## Global Constraints

- Trabalhar no branch `historia-scrollytelling`, um commit por tarefa, terminando em `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- Decisões do Cássio que não se reabrem: vídeo de fundo re-renderizado sem legendas/HUD/capa/cartão; texto da página por cima; trailer fora da página; o máximo de capítulos com cena; as 3 maquetes re-renderizadas no estilo do filme; um clipe curto por cena; execução sem supervisão.
- **Nenhuma frase da página muda.** A única linha nova é a de crédito na `.ficha`: `<p class="nota">As cenas ao fundo da história são dioramas em 3D feitos para este portfólio; as telas e fotos reais estão no portfólio completo.</p>`. "você" continua 1×; o convite fica com exatamente 3 `<a class="btn`.
- A imagem nunca afirma mais que o texto do capítulo nem contradiz a data/ressalva: nada de número, rótulo ou adereço que o `portfolio.html` não sustente. Sem cena: `tese`, `mudanca`, `galpoes`, `precisao`, `metodo`, `convite`. As cenas abertura (SC5), 36 min do filme (SC4) e celeiro do filme (SC8) nunca vão à página.
- Mapa (fonte da verdade em `portfolio/filme/render_clipes.py`, `CLIPES = {passo: (indice_SC, t0, t1, dur)}`): `origem` (0, 0→10, 8 s) · `obra` (1, 0→10, 8) · `veks` (6, 0→4,7, 8) · `ferramentas` (6, 4,7→10, 8) · `sige` (3, 0→10, 8) · `escala` (7, 0→10, 8,5) · `casa` (9, 0→10, 10) · `icamento` (10, 0→10, 8) · `whatsapp` (2, 0→3, 8) · `recuperado` (2, 3→10, 8) · `zip` (11, 0→10, 10). `veks.t1 == ferramentas.t0`; `whatsapp.t1 == recuperado.t0 == 3,0`.
- Encode web: `scale=960:540`, 24 fps, `libx264 -preset slow -crf 28 -g 4 -keyint_min 4 -sc_threshold 0 -bf 0 -pix_fmt yuv420p -profile:v high -level 3.1 -movflags +faststart -an`. Tetos: ≤ 0,9 MB por clipe, ≤ 8 MB na soma, pôster WebP q75 ≤ 60 KB. Reencode automático com crf 29 e 30 antes de falhar.
- Cada clipe é um plano contínuo, parado nas pontas: 40 ≤ YAVG ≤ 235 em todo quadro; |ΔYAVG| ≤ 20 entre quadros consecutivos; ≤ 3 mudanças ≥ 10 % por segundo; PSNR(s=0, s=0,3) ≥ 35 dB e PSNR(s=dur−0,5, s=dur) ≥ 35 dB. Pôster = último quadro do trecho (PSNR ≥ 40 dB).
- `film.html`: fica o `setViewOffset(1280,720,-230,-20,1280,720)`; `ORDER=[5,0,1,6,3,7,8,2,4]` e `renderAt` intactos; `CAPS == CAPITULOS` continua; `corrigir_filme.py` reproduz o `film.html` a partir do zip; cenas portadas sem `stage(`, materiais por `P()`, exatamente 1 material `0xE0622A` por cena (+ a linha de cota no `zip`), nenhum texto pintado.
- Página: figure de clipe exatamente `<figure class="fundo clipe" data-passo="X" data-dur="D" data-clipe="video/cena-X.mp4" aria-hidden="true">` com `<video muted playsinline preload="none" disableremoteplayback width="960" height="540"></video>` e `<img src="video/cena-X.webp" alt="" width="960" height="540" loading="lazy">`; sem `src` no HTML, sem `autoplay|loop|controls|poster|tabindex|<source>|<track>|<canvas>|.hud|data-cena|data-relogio|data-legenda`. Scripts exatamente `["clipes.js","historia.js"]`, `defer`, sem inline. `maquetes.js` não muda e continua só no `portfolio.html`.
- `clipes.js`: só `currentTime`, quantizado ao quadro (`(round(t·24)+0,5)/24`), um seek em voo por vez, o último pedido vence, libera após 600 ms sem `seeked`; nunca `play()`, `fastSeek`, rAF, `fetch`, `createObjectURL`; nunca seek com `readyState < 1`; carga só depois do `load` da janela e a 600 px da `.cena`; no máximo 2 `<video>` com dados; sem H.264, com `?clipes=nao`, `saveData` ou `effectiveType` ∈ {slow-2g, 2g}: só o pôster; `.viva` só no primeiro `seeked`; `TETO=250`, `LENTOS=3`, `VOO=600`.
- CSS: sem `filter` em seletor com `video`; `object-fit:cover;object-position:68% 50%`; `img` mantém `brightness(.6) saturate(.85)`; `100vh` antes de `100svh`, nunca `dvh`; `.palco{display:none}` no empilhado; `overflow:clip` no `<main>`; contraste `--scrim` ≥ 4,5 (`--relogio` ≥ 3, usado pelo `.ano`); ≥ 900 px em paisagem a faixa de texto vai à esquerda (`max-width:min(620px,48vw)`); comprimento do `<main>` inalterado (± 2 px).
- Servidor com Range é pré-requisito: `portfolio/servir.py` no `run` do `.replit` e no `chromium()` dos testes.
- Sem build nem dependência nova (Playwright já está instalado para o `render.py`).

## Review Focus

1. **Clipe que não existe no servidor (404 ou nome errado).** O leitor deve ver o pôster, sem `.viva`, sem erro não tratado no console. Teste: `checar_clipe_real` troca `data-clipe` de uma figura por um arquivo inexistente antes de rolar até ela (Task 11).
2. **Rolagem rápida por três capítulos de clipe seguidos** (veks → ferramentas → sige; whatsapp → recuperado → zip). O `rootMargin` de 600 px deixaria três vídeos com dados; o iPhone derruba a página. Teste: em cada parada, ≤ 2 `<video>` com `readyState > 0` (Task 11).
3. **Movimento reduzido ligado no meio da história.** Todo vídeo tem de sumir e descarregar em ≤ 1 s, sem JS extra para esconder (o CSS já esconde); ao desligar, o clipe ativo volta em ≤ 2 s. Teste: `checar_reduzido_real` (Task 11).
4. **`data-dur` divergindo do arquivo** (alguém reencoda um clipe com outra duração): `historia.js` mandaria seeks além do fim. Teste: `data-dur` = `CLIPES` = `ffprobe` ± 0,05 (Task 10).
5. **Origem publicada sem Range** (o deploy estático do Replit pode responder 200 sem `Accept-Ranges`). A página não pode quebrar: pôster e texto. Teste: `checar_clipe_real` com `http.server` puro — nenhuma `.viva` sem `seekable` completo, imagem visível, console limpo (Task 11); `check_historia.py --origem URL` confere 206 quando a URL existir (Task 10; em aberto).

---

## File Structure

| Arquivo | Responsabilidade |
|---|---|
| `portfolio/servir.py` (novo) | Servidor estático com `Range` → 206; usado pelo `.replit` e pelos testes |
| `.replit` | `run` e workflow com `servir.py` |
| `portfolio/tests/baseline.json` (novo) | `TaskDuration` de uma rolagem completa e altura do `<main>` **antes** da mudança |
| `portfolio/filme/film.html` | Texto pintado corrigido; flag `?limpo`; `renderCena(i, t)`; `PRONTO`; cenas portadas `SC[9]` casa, `SC[10]` içamento, `SC[11]` 36 min |
| `portfolio/filme/corrigir_filme.py` | Trocas da rodada 4 (reproduz o `film.html` a partir do zip) |
| `portfolio/filme/render_clipes.py` (novo) | `CLIPES`; render quadro a quadro; encode web; pôster; tetos |
| `portfolio/filme/render.py` | Trailer de envio em `filme/saida/historia-960.mp4` + `.jpg` (fora do site) |
| `portfolio/filme/README.md` | Clipes, render, "Como enviar" |
| `portfolio/site/video/cena-<passo>.mp4`, `.webp` | Os 11 clipes e pôsteres publicados (`historia.mp4|jpg` saem) |
| `portfolio/site/clipes.js` (novo) | Contrato `fig.__clipe`; seek quantizado; carga em três portas; pôster como plano B |
| `portfolio/site/historia.js` | `maquete` → `clipe` (4 linhas + comentários) |
| `portfolio/site/index.html` | Figures de clipe; CSS do vídeo; faixa à esquerda em tela larga; crédito; trailer removido |
| `portfolio/tests/historia_teste.html` | Harness com `?clipes=nao` e `__clipe` falso |
| `portfolio/tests/check_filme.py` | Texto pintado; `.limpo`/`renderCena`; cenas portadas (estático e com Chromium); clipes (F-03/F-04); trailer só se existir |
| `portfolio/tests/check_historia.py` | `ROTEIRO` com `("clipe", dur)`; marcação; CSS; `clipes.js`; harness; clipe real; reduzido real; dados; foco; layout; desempenho; ficha à vista; `--origem`; `--gravar-baseline` |
| `portfolio/DESIGN.md`, `portfolio/README.md`, `portfolio/revisao/CHANGELOG.md`, `ANDAMENTO.md` | Paleta dos clipes; servidor com Range; rodada 8; retomada |

---

### Task 1: Servidor com Range e linha de base

**Files:**
- Create: `portfolio/servir.py`
- Modify: `.replit`, `portfolio/tests/check_historia.py` (`chromium()`, novo `servidor()`, `checar_servidor()`, `medir_desempenho()`, `--gravar-baseline`)
- Create: `portfolio/tests/baseline.json` (gerado)

**Interfaces:**
- Produces: `servir.py <porta> --bind <ip> --directory <dir>` (mesma linha de comando do `http.server`); em `check_historia.py`: `servidor(porta, com_range=True)` (context manager), `chromium(largura, extra=(), altura=800, com_range=True)`, `medir_desempenho(ws) -> float` (segundos de `TaskDuration` numa rolagem capítulo a capítulo), `metrica(ws, nome)`; `tests/baseline.json` = `{"taskDuration": <s>, "alturaMain": {"390": <px>, "1280": <px>}}`.

- [ ] **Step 1: Escrever o teste do servidor**

Em `check_historia.py`, depois de `PORTA_CDP = 9333`:

```python
@contextlib.contextmanager
def servidor(porta, com_range=True):
    """Servidor estático em portfolio/: servir.py (com Range → 206) ou, para o teste negativo, o http.server puro."""
    base = [sys.executable, str(ROOT / "servir.py")] if com_range else [sys.executable, "-m", "http.server"]
    srv = subprocess.Popen(base + [str(porta), "--bind", "127.0.0.1", "--directory", str(ROOT)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", porta), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.05)
        yield
    finally:
        srv.terminate()
        srv.wait()


def checar_servidor():
    """servir.py responde 206 com Content-Range a um pedido com Range: sem isso o Chrome ignora todo seek no vídeo."""
    check((ROOT / "servir.py").exists(), "portfolio/servir.py não existe")
    if not (ROOT / "servir.py").exists():
        return
    with servidor(PORTA):
        req = urllib.request.Request(f"http://127.0.0.1:{PORTA}/site/index.html", headers={"Range": "bytes=0-99"})
        with urllib.request.urlopen(req) as r:
            check(r.status == 206 and r.headers.get("Content-Range", "").startswith("bytes 0-99/") and len(r.read()) == 100,
                  "servir.py: Range: bytes=0-99 deve responder 206, Content-Range e exatamente 100 bytes")
        with urllib.request.urlopen(f"http://127.0.0.1:{PORTA}/site/index.html") as r:
            check(r.status == 200 and r.headers.get("Accept-Ranges") == "bytes", "servir.py: sem Range, 200 com Accept-Ranges: bytes")
```

Em `chromium()`, trocar a assinatura e o servidor:

```python
@contextlib.contextmanager
def chromium(largura, extra=(), altura=800, com_range=True):
    """servir.py (Range) em portfolio/ + Chromium headless em tempo real, controlado pelo DevTools Protocol.
    Não usar --virtual-time-budget: nele quase não há quadros, e sem quadros nem o IntersectionObserver nem o scroll disparam."""
    with servidor(PORTA, com_range):
        nav = subprocess.Popen(["chromium", "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                                f"--window-size={largura},{altura}", f"--remote-debugging-port={PORTA_CDP}", *extra, "about:blank"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            alvos = []
            for _ in range(100):
                try:
                    alvos = json.load(urllib.request.urlopen(f"http://127.0.0.1:{PORTA_CDP}/json/list"))
                    break
                except OSError:
                    time.sleep(0.1)
            paginas = [a for a in alvos if a.get("type") == "page"]
            if not paginas:
                raise RuntimeError("o Chromium não abriu a porta do DevTools")
            ws = WS(paginas[0]["webSocketDebuggerUrl"])
            # o headless impõe janela mínima de ~500×657; o override garante exatamente largura × altura
            ws.comando("Emulation.setDeviceMetricsOverride", width=largura, height=altura, deviceScaleFactor=1, mobile=False)
            yield ws
        finally:
            nav.terminate()
            nav.wait()
```

(Apague o `srv = subprocess.Popen(...)`/`srv.terminate()` antigos: o servidor agora vem de `servidor()`.) Em `main()`, chamar `checar_servidor()` logo depois de `checar_maquetes_js()`, fora do `if "--navegador"`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py`
Expected: `FALHOU:` com ` - portfolio/servir.py não existe`.

- [ ] **Step 3: Escrever `portfolio/servir.py`**

```python
#!/usr/bin/env python3
"""Servidor estático com Range (HTTP 206). O Chrome só busca (`currentTime`) num vídeo cujo servidor responde
`Accept-Ranges: bytes` e 206 a `Range: bytes=a-b`; o `python3 -m http.server` responde 200 e o vídeo fica preso
no primeiro quadro. Mesma linha de comando do http.server:
    python3 portfolio/servir.py 5000 --bind 0.0.0.0 --directory portfolio/site
"""
import argparse
import io
import os
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class ComRange(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".webp": "image/webp", ".mp4": "video/mp4", ".js": "text/javascript"}

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def send_head(self):
        m = re.match(r"bytes=(\d+)-(\d*)$", self.headers.get("Range", ""))
        caminho = self.translate_path(self.path)
        if not m or not os.path.isfile(caminho):
            return super().send_head()
        tamanho = os.path.getsize(caminho)
        a = int(m.group(1))
        b = min(int(m.group(2)) if m.group(2) else tamanho - 1, tamanho - 1)
        if a >= tamanho or a > b:
            self.send_error(416, "Range Not Satisfiable")
            return None
        with open(caminho, "rb") as f:
            f.seek(a)
            dados = f.read(b - a + 1)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(caminho))
        self.send_header("Content-Range", f"bytes {a}-{b}/{tamanho}")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        return io.BytesIO(dados)

    def log_message(self, *_):
        pass


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("porta", type=int, nargs="?", default=8000)
    p.add_argument("--bind", default="127.0.0.1")
    p.add_argument("--directory", default=".")
    a = p.parse_args()
    ThreadingHTTPServer((a.bind, a.porta), partial(ComRange, directory=a.directory)).serve_forever()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py`
Expected: `OK`.

- [ ] **Step 5: `.replit` passa a usar o servidor com Range**

Trocar as duas ocorrências de `python3 -m http.server 5000 --bind 0.0.0.0 --directory portfolio/site` (o `run =` e o `args =` do workflow "Site do portfólio") por `python3 portfolio/servir.py 5000 --bind 0.0.0.0 --directory portfolio/site`.

Run: `cd /home/runner/workspace && grep -c "servir.py 5000" .replit && (python3 portfolio/servir.py 5057 --directory portfolio/site & sleep 1; curl -s -o /dev/null -w "%{http_code}\n" -H "Range: bytes=0-9" http://127.0.0.1:5057/index.html; kill %1)`
Expected: `2` e `206`.

- [ ] **Step 6: Gravar a linha de base de desempenho (antes de qualquer mudança na página)**

Em `check_historia.py`, depois de `checar_servidor()`:

```python
BASELINE = ROOT / "tests" / "baseline.json"


def metrica(ws, nome):
    return next(m["value"] for m in ws.comando("Performance.getMetrics")["metrics"] if m["name"] == nome)


def medir_desempenho(ws):
    """Segundos de TaskDuration numa rolagem completa, capítulo a capítulo (0,6 s em cada), com a página já carregada."""
    ws.comando("Performance.enable")
    antes = metrica(ws, "TaskDuration")
    n = ws.avaliar("document.querySelectorAll('.cena[data-passo]').length")
    for i in range(n):
        ws.avaliar(f"(function(){{var r=document.querySelectorAll('.cena[data-passo]')[{i}].getBoundingClientRect();"
                   "window.scrollTo(0,scrollY+r.top+r.height/2-innerHeight/2);})()")
        time.sleep(0.6)
    return metrica(ws, "TaskDuration") - antes


def gravar_baseline():
    """Linha de base da página de hoje (maquetes WebGL por SwiftShader): F-17 compara a página com clipes a 2× isto."""
    base = {"alturaMain": {}}
    for largura in (390, 1280):
        with chromium(largura, ("--enable-unsafe-swiftshader",)) as ws:
            ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/site/index.html")
            time.sleep(2.5)
            if largura == 390:
                base["taskDuration"] = round(medir_desempenho(ws), 3)
            base["alturaMain"][str(largura)] = ws.avaliar("document.getElementById('historia').offsetHeight")
    BASELINE.write_text(json.dumps(base, indent=1) + "\n", encoding="utf-8")
    print("baseline:", base)
```

Em `main()`, antes de tudo: `if "--gravar-baseline" in sys.argv: gravar_baseline(); return`.

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py --gravar-baseline && cat portfolio/tests/baseline.json`
Expected: `baseline: {...}` com `taskDuration` de alguns segundos (as maquetes renderizam por SwiftShader a cada quadro) e `alturaMain` `{"390": 16000, "1280": 16000}`.

**Ruling:** a spec pede `document.body.scrollHeight` inalterado, mas a seção do trailer sai da página (Task 9) e o `body` encurta por definição. O que não pode mudar é o comprimento da história: mede-se `#historia.offsetHeight`.

- [ ] **Step 7: Commit**

```bash
cd /home/runner/workspace && git add portfolio/servir.py .replit portfolio/tests/check_historia.py portfolio/tests/baseline.json
git commit -m "Servidor estático com Range (206) para o site e para os testes; linha de base de desempenho da história

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 2: Texto pintado nas cenas do filme (roteirista)

**Files:**
- Modify: `portfolio/filme/film.html` (cenas rua, VEKS, SIGE, restaurante, 36 min, escritório), `portfolio/filme/corrigir_filme.py`, `portfolio/tests/check_filme.py`

**Interfaces:**
- Produces: `check_filme.py` com `ANDARES = ["PROPOSTA","OBRA","CRONOGRAMA","DIÁRIO","MEDIÇÃO","COBRANÇA","CAIXA","PORTAL DO CLIENTE"]` (iguais aos `<span>` de `#sige .flow` do `portfolio.html`, em caixa-alta); `PROIBIDOS`/`EXIGIDOS` da rodada 4; `corrigir_filme.py` com `TROCAS_RODADA_4`.

- [ ] **Step 1: Escrever os testes**

Em `check_filme.py`, trocar `PROIBIDOS` e `EXIGIDOS` e acrescentar `ANDARES`:

```python
PROIBIDOS = ["26 anos", "155.000", "150.500", "Cassio", "orçadas", "perdidos", "389,04", "422,04", "11.480", "9,90",
             "a obra digitava", "no centavo",
             # rodada 4: nada no quadro que o portfólio não sustente (o clipe não tem legenda para ressalvar)
             "OUTRO DADO", "barras de 3 m", "LICENCIADO", "COMPRAS", "756", "CONSTRUIR E DEMOLIR", "ESC 1:"]
EXIGIDOS = ["Cássio Viller", "No estudo", "Pré-dimensionado", "numa cópia", "a carga ainda não foi aplicada",
            "MESMO DADO", "PLANO DE CORTE", "EM USO", "DESENHO", "PLANTA"]
ANDARES = ["PROPOSTA", "OBRA", "CRONOGRAMA", "DIÁRIO", "MEDIÇÃO", "COBRANÇA", "CAIXA", "PORTAL DO CLIENTE"]  # = #sige .flow do portfólio
```

No fim de `checar_texto(filme, portfolio, historia)`:

```python
    # SIGE: 8 andares com os nomes do fluxo do portfólio, sem numerais; placa "EM USO"
    flow = re.search(r'<div class="flow"[^>]*>(.*?)</div>', portfolio[portfolio.index('id="sige"'):], re.S)
    check(flow is not None and [limpo(s).upper() for s in re.findall(r"<span[^>]*>(.*?)</span>", flow.group(1))] == ANDARES,
          "os andares do SIGE no filme têm de ser os <span> de #sige .flow do portfólio")
    names = re.search(r"var names=\[([^\]]*)\];", filme)
    check(names is not None and [js_str(x) for x in re.findall(r"'((?:[^'\\]|\\.)*)'", names.group(1))] == ANDARES,
          f"var names do SIGE ≠ {ANDARES}")
    sige = filme[filme.index("CENA 4 · prédio SIGE"):filme.index("CENA 6 · 36 minutos")]
    check("padStart" not in sige, "SIGE: sem numeral nos andares (7 numerados leem-se como 7 áreas; o site diz 6)")
    check("st.cam=[[0,[7,1.6,10],[0,1.4,0]],[7.5,[7,9.8,10],[0,8.8,0]],[10,[12.5,10,17.5],[0,5.4,0]]];" in sige,
          "SIGE: chaves de câmera do 8º andar")
    check("if(r*7+k<31)" in filme, "escritório: calendário com até 31 dias")
    rua = filme[filme.index("CENA 2 · duas construtoras"):filme.index("CENA 3 · WhatsApp")]
    check("c.fillText('MESMO DADO',20,120);" in rua and "moveTo(16,106)" not in rua, "rua: os 5 cartões dizem MESMO DADO, sem risco")
    check("m.rotation.z=i==4?Math.sin(t*9)*.08*cl(t-7.2):0" in rua, "rua: o 5º cartão continua tremendo")
```

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py`
Expected: `FALHOU:` com `texto proibido no filme: 'OUTRO DADO'`, `'barras de 3 m'`, `'LICENCIADO'`, `'COMPRAS'`, `'756'`, `'CONSTRUIR E DEMOLIR'`, `'ESC 1:'`; `texto obrigatório ausente: 'EM USO'`, `'DESENHO'`; `var names do SIGE ≠ …`; `SIGE: sem numeral`; `chaves de câmera`; `calendário`; `MESMO DADO, sem risco`.

- [ ] **Step 3: As trocas em `corrigir_filme.py`**

Depois da lista `TROCAS`, acrescentar:

```python
# Rodada 4 (o filme vira fundo da história, sem legenda para ressalvar): nada no quadro que o portfolio.html não sustente.
TROCAS_RODADA_4 = [
    # rua: os 5 cartões dizem MESMO DADO; sai o "OUTRO DADO" e o risco (o 5º continua vermelho e tremendo)
    ("c.fillText(i==4?'OUTRO DADO':'MESMO DADO',20,120);if(i==4){c.strokeStyle='#C23B22';c.lineWidth=5;c.beginPath();c.moveTo(16,106);c.lineTo(300,106);c.stroke();}",
     "c.fillText('MESMO DADO',20,120);"),
    # VEKS: o portfólio não fala de barras de 3 m
    ("'PLANO DE CORTE · barras de 3 m'", "'PLANO DE CORTE'"),
    # SIGE: 8 andares = #sige .flow do portfólio, sem numerais; a placa diz EM USO; tudo sobe 1,2 (um andar)
    ("var names=['PROPOSTA','OBRA','CRONOGRAMA','DIÁRIO','COMPRAS','MEDIÇÃO','CAIXA'];",
     "var names=['PROPOSTA','OBRA','CRONOGRAMA','DIÁRIO','MEDIÇÃO','COBRANÇA','CAIXA','PORTAL DO CLIENTE'];"),
    ("c.fillStyle='#fff';c.font='bold 50px sans-serif';c.fillText(nm,24,66);c.fillStyle='#D9541E';c.fillText(String(i+1).padStart(2,'0'),420,66);",
     "c.fillStyle='#fff';c.font='bold 40px sans-serif';c.fillText(nm,24,64);"),
    ("st.tube=box(.3,8.6,.3,ORANGE,-2.3,4.3,2.12,g);st.tube.geometry.translate(0,4.3,0);",
     "st.tube=box(.3,9.8,.3,ORANGE,-2.3,4.9,2.12,g);st.tube.geometry.translate(0,4.9,0);"),
    ("c.fillText('LICENCIADO',70,76);", "c.fillText('EM USO',140,76);"),
    ("st.lic=plane(2.8,.6,lic,0,9.3,0,g);box(.1,.8,.1,0x55606B,-1,8.7,0,g);box(.1,.8,.1,0x55606B,1,8.7,0,g);",
     "st.lic=plane(2.8,.6,lic,0,10.5,0,g);box(.1,.8,.1,0x55606B,-1,9.9,0,g);box(.1,.8,.1,0x55606B,1,9.9,0,g);"),
    ("st.cam=[[0,[7,1.6,10],[0,1.4,0]],[7.5,[7,8.6,10],[0,7.6,0]],[10,[11.5,9,16],[0,4.8,0]]];",
     "st.cam=[[0,[7,1.6,10],[0,1.4,0]],[7.5,[7,9.8,10],[0,8.8,0]],[10,[12.5,10,17.5],[0,5.4,0]]];"),
    ("st.tube.scale.y=Math.max(.01,ramp(t,.5,7.6));st.lic.visible=t>7.8;st.lic.scale.setScalar(Math.max(.001,back((t-7.8)/.5)));",
     "st.tube.scale.y=Math.max(.01,ramp(t,.5,8.0));st.lic.visible=t>8.2;st.lic.scale.setScalar(Math.max(.001,back((t-8.2)/.5)));"),
    # restaurante: o cubo é o desenho que entra, não um tamanho de arquivo
    ("c.font='bold 64px sans-serif';c.fillText('756',60,120);c.font='bold 44px sans-serif';c.fillText('MB',86,180);",
     "c.font='bold 44px sans-serif';c.fillText('DESENHO',26,146);"),
    # 36 min (só no trailer): sem título de prancha nem escala
    ("'PLANTA CONSTRUIR E DEMOLIR · ESC 1:100'", "'PLANTA'"),
    # escritório: calendário com 31 dias, não 35
    ("for(var r=0;r<5;r++)for(var k=0;k<7;k++)c.fillText(String(r*7+k+1),14+k*34,110+r*40);",
     "for(var r=0;r<5;r++)for(var k=0;k<7;k++)if(r*7+k<31)c.fillText(String(r*7+k+1),14+k*34,110+r*40);"),
]
```

Em `main()`, logo depois do laço de `TROCAS` (e antes da tabela), acrescentar o mesmo laço para `TROCAS_RODADA_4`:

```python
    for velho, novo in TROCAS_RODADA_4:
        assert s.count(velho) == 1, f"trecho da rodada 4 não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
```

E aplicar **as mesmas trocas** ao `film.html` commitado (ele já tem as da rodada 3), com um script de uma vez:

```bash
cd /home/runner/workspace && python3 - <<'EOF'
import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("c", "portfolio/filme/corrigir_filme.py"); c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
p = pathlib.Path("portfolio/filme/film.html"); s = p.read_text(encoding="utf-8")
for velho, novo in c.TROCAS_RODADA_4:
    assert s.count(velho) == 1, velho[:60]
    s = s.replace(velho, novo)
p.write_text(s, encoding="utf-8"); print("aplicado")
EOF
```

- [ ] **Step 4: Ver passar, e conferir que o zip reproduz o arquivo commitado**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad/zip && rm -rf $S && mkdir -p $S && unzip -q -o filme-codigo-fonte.zip -d $S && cp portfolio/filme/corrigir_filme.py $S/ && python3 $S/corrigir_filme.py && cmp $S/film.html portfolio/filme/film.html && echo IDENTICO`
Expected: `OK`, `film.html corrigido`, `IDENTICO`.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/filme/corrigir_filme.py portfolio/tests/check_filme.py
git commit -m "Filme: texto pintado só com o que o portfólio sustenta (MESMO DADO, PLANO DE CORTE, 8 andares do SIGE, EM USO, DESENHO, PLANTA, calendário de 31 dias)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 3: O filme "limpo", `renderCena` e o render dos clipes

**Files:**
- Modify: `portfolio/filme/film.html` (`<style>` `.limpo`, flag, `PRONTOS`/`PRONTO`, `DURSC`, `window.renderCena`)
- Create: `portfolio/filme/render_clipes.py`
- Modify: `portfolio/tests/check_filme.py` (`checar_limpo`, `checar_clipe`, `checar_clipes`, `--video [passos]`), `.gitignore` (nada: `portfolio/filme/saida/` já está ignorado)

**Interfaces:**
- Produces: `film.html?limpo` esconde `#cap,#hud,#num,#cover,#end,.tag,.bar,.scrim,#prog,#wipe,#fade,.vig`; `window.renderCena(i, t)` desenha a cena `SC[i]` no tempo local `t` (0..10) e nada mais; `window.PRONTO` é uma Promise que resolve quando as texturas das cenas portadas carregaram (Task 6 a alimenta pelo array `PRONTOS`); `var DURSC` = duração em segundos de cada cena (`DURSC[9]=10`, `DURSC[10]=8`, `DURSC[11]=10`).
- `render_clipes.py`: `CLIPES`, `FPS=24`, `tempo_local(passo, s)`, `quadros(passo)`, `psnr(a, b)`, `ARGS` (flags do Chromium); CLI `--so <passo>`. Saídas `filme/saida/clipes/cena-<passo>-1280.mp4` (mestre), `site/video/cena-<passo>.mp4`, `site/video/cena-<passo>.webp`.
- `check_filme.py --video [passo …]`: confere os clipes pedidos (todos, sem argumento) e o trailer.

- [ ] **Step 1: Testes estáticos do `?limpo` e do `renderCena`**

Em `check_filme.py`:

```python
def checar_limpo(filme):
    """film.html?limpo: nenhum DOM por cima do canvas; renderCena(i, t) puro; o trailer (ORDER, renderAt) intacto."""
    check(".limpo #cap,.limpo #hud,.limpo #num,.limpo #cover,.limpo #end,.limpo .tag,.limpo .bar,.limpo .scrim,.limpo #prog,"
          ".limpo #wipe,.limpo #fade,.limpo .vig{display:none!important}" in filme, "film.html: falta a regra .limpo")
    check("if(/[?&]limpo\\b/.test(location.search))document.documentElement.classList.add('limpo');" in filme,
          "film.html: a flag ?limpo liga a classe no <html>")
    check("window.renderCena=function(i,t){" in filme, "film.html: falta window.renderCena(i, t)")
    check("var PRONTOS=[];" in filme and "window.PRONTO=Promise.all(PRONTOS);" in filme, "film.html: falta PRONTOS/PRONTO")
    check("DURSC[9]=10;DURSC[10]=8;DURSC[11]=10;" in filme, "film.html: durações das cenas portadas (casa 10 s, içamento 8 s, zip 10 s)")
    check("cam.setViewOffset(1280,720,-230,-20,1280,720)" in filme, "film.html: o viewOffset da composição fica")
    check("var ORDER=[5,0,1,6,3,7,8,2,4]" in filme and "window.renderAt=function(T)" in filme, "film.html: o trailer não muda")
```

Chamar `checar_limpo(filme)` em `main()` junto de `checar_texto`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py`
Expected: `FALHOU:` com as 5 linhas `film.html: falta …`/`flag ?limpo`/`durações`.

- [ ] **Step 3: `film.html`**

No `<style>`, depois da regra `#end .cta span{…}`:

```css
/* ?limpo (render_clipes.py): só o canvas; renderAt continua escrevendo nestes nós, eles só não aparecem */
.limpo #cap,.limpo #hud,.limpo #num,.limpo #cover,.limpo #end,.limpo .tag,.limpo .bar,.limpo .scrim,.limpo #prog,.limpo #wipe,.limpo #fade,.limpo .vig{display:none!important}
```

No `<script>`, a primeira linha (antes de `var R=new THREE.WebGLRenderer`):

```js
if(/[?&]limpo\b/.test(location.search))document.documentElement.classList.add('limpo');
var PRONTOS=[]; // promessas das texturas que as cenas portadas carregam (a planta real); render_clipes.py espera window.PRONTO
```

Na seção `// ================= render =================`, logo depois de `function camAt(st,t,T){…}`:

```js
// clipes da história (render_clipes.py): a cena i no tempo local t (0..10), sem DOM por cima; puro em (i, t), independente de ORDER/START
var DURSC=[];ORDER.forEach(function(s,k){DURSC[s]=DUR[k];});DURSC[9]=10;DURSC[10]=8;DURSC[11]=10;
window.renderCena=function(i,t){SC.forEach(function(s,j){s.g.visible=j===i;});sun.position.set(-8,16,10);var st=SC[i];st.run(t);camAt(st,t,t*DURSC[i]/10);R.render(S,cam);cur=-1;};
```

Última linha do script (depois de `renderAt(0);`): `window.PRONTO=Promise.all(PRONTOS);`

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py`
Expected: `OK`.

- [ ] **Step 5: Escrever `portfolio/filme/render_clipes.py`**

```python
#!/usr/bin/env python3
"""Gera os clipes de fundo da história: um MP4 curto e mudo por capítulo, a partir de film.html?limpo (sem legenda,
HUD, capa nem cartão), mais o pôster WebP (= último quadro). A tabela CLIPES é a fonte da verdade do mapa
capítulo → cena → trecho (spec 2026-09-23-filme-fundo-design.md); check_historia.py e check_filme.py a importam.

Uso: python3 portfolio/filme/render_clipes.py            (os 11 clipes, ~10 min em CPU)
     python3 portfolio/filme/render_clipes.py --so zip   (um clipe só; não confere a soma)
Saídas: portfolio/filme/saida/clipes/cena-<passo>-1280.mp4  mestre 1280×720 (ignorado pelo git)
        portfolio/site/video/cena-<passo>.mp4              960×540, 24 fps, H.264 High 3.1, GOP 4, sem áudio
        portfolio/site/video/cena-<passo>.webp             pôster = último quadro do clipe publicado
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida" / "clipes"
WEB = AQUI.parent / "site" / "video"
FPS = 24
INICIO_PARADO, FIM_PARADO = 0.3, 0.5  # s: o clipe começa e termina parado (o dissolve entre capítulos é entre quadros parados)
TETO_CLIPE, TETO_SOMA, TETO_POSTER = int(0.9 * 1024 * 1024), 8 * 1024 * 1024, 60 * 1024
CRF, CRF_MAX = 28, 30
# passo: (índice em SC, t0, t1, duração em s); t é o tempo local 0..10 da cena (st.run(t)); um trecho contíguo por capítulo
CLIPES = {
    "origem": (0, 0.0, 10.0, 8),
    "obra": (1, 0.0, 10.0, 8),
    "veks": (6, 0.0, 4.7, 8),
    "ferramentas": (6, 4.7, 10.0, 8),
    "sige": (3, 0.0, 10.0, 8),
    "escala": (7, 0.0, 10.0, 8.5),
    "casa": (9, 0.0, 10.0, 10),
    "icamento": (10, 0.0, 10.0, 8),
    "whatsapp": (2, 0.0, 3.0, 8),
    "recuperado": (2, 3.0, 10.0, 8),
    "zip": (11, 0.0, 10.0, 10),
}
ARGS = ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist", "--allow-file-access-from-files"]


def tempo_local(passo, s):
    """Segundo s do clipe → t local da cena: parado nos primeiros 0,3 s e nos últimos 0,5 s, linear no meio."""
    _sc, t0, t1, dur = CLIPES[passo]
    f = min(1.0, max(0.0, (s - INICIO_PARADO) / (dur - INICIO_PARADO - FIM_PARADO)))
    return t0 + (t1 - t0) * f


def quadros(passo):
    return int(round(CLIPES[passo][3] * FPS))


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def psnr(a, b):
    """PSNR médio (dB) entre duas imagens ou dois vídeos do mesmo tamanho; inf se iguais."""
    saida = subprocess.run(["ffmpeg", "-i", str(a), "-i", str(b), "-lavfi", "psnr", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.search(r"average:(inf|[\d.]+)", saida)
    return float("inf") if not m or m.group(1) == "inf" else float(m.group(1))


def encode_web(mestre, destino, crf):
    ffmpeg("-i", str(mestre), "-vf", "scale=960:540", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
           "-g", "4", "-keyint_min", "4", "-sc_threshold", "0", "-bf", "0", "-pix_fmt", "yuv420p", "-profile:v", "high",
           "-level", "3.1", "-movflags", "+faststart", "-an", str(destino))


def poster(mp4, passo, destino):
    """Pôster = último quadro do clipe publicado: WebP com PSNR ≥ 40 dB em relação a ele e ≤ 60 KB (q75, senão 82, 90)."""
    png = SAIDA / f"ultimo-{passo}.png"
    ffmpeg("-i", str(mp4), "-vf", f"select='eq(n,{quadros(passo) - 1})'", "-vframes", "1", "-update", "1", str(png))
    for q in (75, 82, 90):
        ffmpeg("-i", str(png), "-c:v", "libwebp", "-quality", str(q), str(destino))
        if psnr(destino, png) >= 40 and destino.stat().st_size <= TETO_POSTER:
            return
    sys.exit(f"{passo}: pôster sem PSNR ≥ 40 dB dentro de 60 KB")


def render(pagina, passo):
    """Quadro a quadro pelo Playwright: renderCena(i, t) → JPEG q92 → ffmpeg (mestre 1280×720, 24 fps, crf 18)."""
    sc = CLIPES[passo][0]
    mestre = SAIDA / f"cena-{passo}-1280.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-vcodec", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", str(mestre)], stdin=subprocess.PIPE)
    n = quadros(passo)
    for k in range(n):
        pagina.evaluate(f"renderCena({sc},{tempo_local(passo, k / FPS)!r})")
        ff.stdin.write(pagina.screenshot(type="jpeg", quality=92))
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit(f"{passo}: ffmpeg falhou no mestre")
    print(f"{passo}: {n} quadros", flush=True)
    return mestre


def publicar(passo, mestre):
    """Encode web dentro de 0,9 MB (crf 28, senão 29, 30) e pôster. Devolve o crf usado."""
    destino = WEB / f"cena-{passo}.mp4"
    for crf in range(CRF, CRF_MAX + 1):
        encode_web(mestre, destino, crf)
        if destino.stat().st_size <= TETO_CLIPE:
            break
    else:
        sys.exit(f"{passo}: acima de 0,9 MB mesmo com crf {CRF_MAX}")
    poster(destino, passo, WEB / f"cena-{passo}.webp")
    print(f"{passo}: {destino.stat().st_size / 1024:.0f} KB (crf {crf})", flush=True)
    return crf


def ajustar_soma(crfs):
    """Se os 11 clipes passarem de 8 MB, reencoda o maior com crf +1 (até 30) até caber."""
    while True:
        tamanhos = {p: (WEB / f"cena-{p}.mp4").stat().st_size for p in CLIPES}
        soma = sum(tamanhos.values())
        if soma <= TETO_SOMA:
            print(f"soma dos clipes: {soma / 1024 / 1024:.2f} MB", flush=True)
            return
        maior = max(tamanhos, key=tamanhos.get)
        if crfs[maior] >= CRF_MAX:
            sys.exit(f"soma dos clipes acima de 8 MB mesmo com crf {CRF_MAX} em {maior}")
        crfs[maior] += 1
        encode_web(SAIDA / f"cena-{maior}-1280.mp4", WEB / f"cena-{maior}.mp4", crfs[maior])
        poster(WEB / f"cena-{maior}.mp4", maior, WEB / f"cena-{maior}.webp")
        print(f"soma > 8 MB: {maior} reencodado com crf {crfs[maior]}", flush=True)


def main():
    from playwright.sync_api import sync_playwright
    passos = [sys.argv[sys.argv.index("--so") + 1]] if "--so" in sys.argv else list(CLIPES)
    SAIDA.mkdir(parents=True, exist_ok=True)
    WEB.mkdir(parents=True, exist_ok=True)
    crfs = {}
    with sync_playwright() as p:
        exe = shutil.which("chromium")  # no Replit o Chromium do Playwright não roda (faltam bibliotecas): usa o do sistema
        navegador = p.chromium.launch(executable_path=exe, args=ARGS) if exe else p.chromium.launch(args=ARGS)
        pagina = navegador.new_page(viewport={"width": 1280, "height": 720})
        pagina.goto((AQUI / "film.html").as_uri() + "?limpo")
        pagina.wait_for_timeout(2500)
        pagina.evaluate("PRONTO")  # texturas das cenas portadas (a planta real) carregadas
        for passo in passos:
            crfs[passo] = publicar(passo, render(pagina, passo))
        navegador.close()
    if "--so" not in sys.argv:
        ajustar_soma(crfs)
    print("pronto:", WEB)


if __name__ == "__main__":
    main()
```

- [ ] **Step 6: Testes dos clipes (F-03, F-04) em `check_filme.py`**

Depois dos imports: `import tempfile` e

```python
sys.path.insert(0, str(ROOT / "filme"))
from render_clipes import CLIPES, FPS, psnr, quadros  # noqa: E402  (a tabela do mapa é a fonte da verdade)

VIDEO_DIR = SITE / "video"
```

Funções novas (antes de `main`):

```python
def ffprobe_json(caminho, entradas):
    return json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", entradas, "-of", "json", str(caminho)],
                                     capture_output=True, text=True, check=True).stdout)


def quadros_chave(mp4):
    saida = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-skip_frame", "nokey", "-show_entries", "frame=pts_time",
                            "-of", "csv=p=0", str(mp4)], capture_output=True, text=True, check=True).stdout
    return [float(x.strip(", ")) for x in saida.split() if x.strip(", ")]


def tipos_de_quadro(mp4):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "frame=pict_type", "-of", "csv=p=0", str(mp4)],
                          capture_output=True, text=True, check=True).stdout.replace(",", "").split()


def luma(arquivo):
    """(YAVG, YDIF) por quadro, pelo filtro signalstats (serve para MP4 e para o pôster WebP, que tem 1 quadro)."""
    saida = subprocess.run(["ffprobe", "-v", "error", "-f", "lavfi", "-i", f"movie={arquivo},signalstats", "-show_entries",
                            "frame_tags=lavfi.signalstats.YAVG,lavfi.signalstats.YDIF", "-of", "csv=p=0"],
                           capture_output=True, text=True, check=True).stdout
    return [tuple(float(x) for x in l.strip(",").split(",")) for l in saida.splitlines() if l.strip(",")]


def quadro(mp4, n, destino):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", f"select='eq(n,{n})'", "-vframes", "1", "-update", "1",
                    str(destino)], check=True)


def checar_clipe(passo, tmp):
    """Um clipe publicado: H.264 High ≤ 3.1, 960×540, 24 fps, sem áudio, moov antes, GOP ≤ 4, sem B-frames, ≤ 0,9 MB,
    plano contínuo parado nas pontas, pôster = último quadro. Devolve o tamanho em bytes (0 se faltar)."""
    _sc, _t0, _t1, dur = CLIPES[passo]
    mp4, webp = VIDEO_DIR / f"cena-{passo}.mp4", VIDEO_DIR / f"cena-{passo}.webp"
    check(mp4.exists() and webp.exists(), f"falta {mp4.name} ou {webp.name} (rode python3 portfolio/filme/render_clipes.py --so {passo})")
    if not (mp4.exists() and webp.exists()):
        return 0
    info = ffprobe_json(mp4, "format=duration,size:stream=codec_type,codec_name,profile,level,width,height,pix_fmt,r_frame_rate")
    v = [s for s in info["streams"] if s["codec_type"] == "video"]
    check(len(v) == 1 and v[0]["codec_name"] == "h264" and v[0]["profile"] == "High" and int(v[0]["level"]) <= 31, f"{passo}: H.264 High ≤ 3.1 ({v})")
    check(v and (v[0]["width"], v[0]["height"], v[0]["pix_fmt"], v[0]["r_frame_rate"]) == (960, 540, "yuv420p", "24/1"), f"{passo}: 960×540 yuv420p 24 fps")
    check(not [s for s in info["streams"] if s["codec_type"] == "audio"], f"{passo}: sem faixa de áudio")
    check(abs(float(info["format"]["duration"]) - dur) <= 1 / FPS + 1e-3, f"{passo}: duração {info['format']['duration']} s ≠ {dur} s")
    dados = mp4.read_bytes()
    check(0 <= dados.find(b"moov") < dados.find(b"mdat"), f"{passo}: moov antes de mdat (+faststart)")
    tamanho = int(info["format"]["size"])
    check(tamanho <= 0.9 * 1024 * 1024, f"{passo}: {tamanho / 1024:.0f} KB > 0,9 MB")
    kf = quadros_chave(mp4)
    check(kf and max(b - a for a, b in zip(kf, kf[1:])) <= 4 / FPS + 1e-3, f"{passo}: quadro-chave a cada ≤ 4 quadros")
    check("B" not in tipos_de_quadro(mp4), f"{passo}: sem B-frames")
    y = luma(mp4)
    check(all(40 <= a <= 235 for a, _ in y), f"{passo}: luma média fora de 40..235 em algum quadro")
    check(all(abs(b[0] - a[0]) <= 20 for a, b in zip(y, y[1:])), f"{passo}: salto de luma > 20 entre quadros consecutivos")
    for i in range(0, len(y), FPS):
        check(sum(1 for _, d in y[i:i + FPS] if d >= 25.5) <= 3, f"{passo}: mais de 3 mudanças ≥ 10 % no segundo {i // FPS}")
    n = quadros(passo)
    for a, b in ((0, int(round(0.3 * FPS))), (n - 1 - int(round(0.5 * FPS)), n - 1)):
        fa, fb = tmp / f"{passo}-{a}.png", tmp / f"{passo}-{b}.png"
        quadro(mp4, a, fa)
        quadro(mp4, b, fb)
        check(psnr(fa, fb) >= 35, f"{passo}: os quadros {a} e {b} deveriam ser iguais (o clipe começa e termina parado)")
    p = ffprobe_json(webp, "stream=width,height")["streams"][0]
    check((p["width"], p["height"]) == (960, 540) and webp.stat().st_size <= 60 * 1024, f"{passo}: pôster 960×540 ≤ 60 KB")
    check(psnr(webp, tmp / f"{passo}-{n - 1}.png") >= 40, f"{passo}: pôster ≠ último quadro do clipe (PSNR < 40 dB)")
    yp = luma(webp)
    check(yp and 40 <= yp[0][0] <= 235, f"{passo}: pôster em branco ou preto")
    return tamanho


def checar_clipes(passos):
    check(set(passos) <= set(CLIPES), f"passos desconhecidos: {sorted(set(passos) - set(CLIPES))}")
    with tempfile.TemporaryDirectory() as tmp:
        soma = sum(checar_clipe(p, Path(tmp)) for p in passos if p in CLIPES)
    if set(passos) == set(CLIPES):
        check(soma <= 8 * 1024 * 1024, f"soma dos clipes {soma / 1024 / 1024:.2f} MB > 8 MB")
```

`main()` passa a ser:

```python
def main():
    check(FILME.exists(), "portfolio/filme/film.html não existe")
    if FILME.exists():
        filme = FILME.read_text(encoding="utf-8")
        checar_texto(filme, (SITE / "portfolio.html").read_text(encoding="utf-8"), (SITE / "index.html").read_text(encoding="utf-8"))
        checar_limpo(filme)
    if "--video" in sys.argv:
        passos = [a for a in sys.argv[sys.argv.index("--video") + 1:] if not a.startswith("--")]
        checar_clipes(passos or list(CLIPES))
        checar_video()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")
```

- [ ] **Step 7: Ver falhar pelo motivo certo**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --video origem`
Expected: `FALHOU:` só com ` - falta cena-origem.mp4 ou cena-origem.webp (rode python3 portfolio/filme/render_clipes.py --so origem)`.

- [ ] **Step 8: Render do primeiro clipe (~1 min)**

Run: `cd /home/runner/workspace && python3 portfolio/filme/render_clipes.py --so origem && python3 portfolio/tests/check_filme.py --video origem && ls -l portfolio/site/video/`
Expected: `origem: 192 quadros`, `origem: NNN KB (crf 28)` com NNN ≤ 921, `OK`; `cena-origem.mp4` e `cena-origem.webp` listados.

- [ ] **Step 9: Conferir quadros**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && for N in 0 60 120 191; do ffmpeg -y -loglevel error -i portfolio/site/video/cena-origem.mp4 -vf "select='eq(n,$N)'" -vframes 1 -update 1 $S/origem-$N.png; done && magick $S/origem-{0,60,120,191}.png -resize 50% +append $S/origem.png
```

Abrir `origem.png` com a ferramenta Read. Expected: quatro quadros do escritório **sem** tarja, legenda, HUD, contador ou vinheta; o último com a moeda ao lado do teclado e a tela em "confere"; calendário sem os dias 32–35.

- [ ] **Step 10: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/filme/render_clipes.py portfolio/tests/check_filme.py portfolio/site/video/cena-origem.mp4 portfolio/site/video/cena-origem.webp
git commit -m "Filme limpo (?limpo, renderCena) e render_clipes.py: o primeiro clipe de fundo, origem (8 s, 960×540, GOP 4)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 4: Cena portada `casa` (SC[9], 10 s)

**Files:**
- Modify: `portfolio/filme/film.html` (bloco novo depois de `// ================= CELEIRO · balancim`), `portfolio/tests/check_filme.py` (`PORTADAS`, `checar_portadas`, `checar_cenas_portadas`, `--cenas`)

**Interfaces:**
- Consumes: utilitários do `film.html`: `S`, `SC`, `P(c,o)`, `edge(m)`, `box(w,h,d,c,x,y,z,p,noEdge)`, `cyl(r,h,c,x,y,z,p,seg)`, `slab(w,d,top,p)`, `tree(x,z,s,p)`, `cl`, `ease`, `ramp`, `lerp`, `back`, `ORANGE`, `sun`; `renderCena(i,t)` e `cam` (Task 3).
- Produces: `SC[9]` com `st.g`, `st.cam` (5 chaves), `st.run(t)`, e para os testes `st.truck` (Group), `st.roof` (Group), `st.c1`, `st.c2`, `st.HH`. Marcador do bloco: `// ================= CASA (portada da página: casa-viaja, 10 s) =================`. `check_filme.py --cenas casa [icamento zip]` roda o Chromium e confere o conteúdo.

- [ ] **Step 1: Testes (estático + Chromium)**

Em `check_filme.py`, depois de `checar_limpo`:

```python
PORTADAS = {"casa": "// ================= CASA (portada da página: casa-viaja, 10 s) =================",
            "icamento": "// ================= IÇAMENTO (portado da página: icamento, 8 s) =================",
            "zip": "// ================= 36 MINUTOS (portado da página: 36min, 10 s) ================="}


def bloco_portado(filme, passo):
    ini = filme.find(PORTADAS[passo])
    if ini < 0:
        return ""
    fim = filme.find("// =================", ini + len(PORTADAS[passo]))
    return filme[ini:fim if fim > 0 else len(filme)]


def checar_portadas(filme, passos):
    """Estilo do filme nas cenas portadas: sem stage(), materiais por P() (exceto o filme translúcido e a textura da planta),
    um só acento ORANGE (+ a linha de cota no zip), nenhum texto pintado (F-18)."""
    for passo in passos:
        b = bloco_portado(filme, passo)
        check(b, f"film.html: falta o bloco {PORTADAS[passo]!r}")
        if not b:
            continue
        for proibido in ("stage(", "fillText", "SUBS", "LEG", "tex("):
            check(proibido not in b, f"cena portada {passo}: sem {proibido} (nenhum texto pintado, nada do maquetes.js)")
        for m in re.finditer(r"new THREE\.MeshStandardMaterial\(\{([^}]*)\}", b):
            check("transparent:true" in m.group(1) or "map:" in m.group(1),
                  f"cena portada {passo}: materiais por P(); só o filme translúcido e a textura da planta são MeshStandardMaterial")
        check(b.count("ORANGE") == (2 if passo == "zip" else 1), f"cena portada {passo}: exatamente 1 acento ORANGE (+ a linha de cota no zip)")
        check(re.search(r"0xE0622A", b, re.I) is None, f"cena portada {passo}: o laranja só entra como ORANGE")


LEITURAS = {  # expressão avaliada no film.html?limpo → valor esperado (F-18: as cenas portadas preservam o conteúdo)
    "casa": ("(function(){var st=SC[9],r=[];[.8,4.2,7.4].forEach(function(t){renderCena(9,t);var p=st.truck.position.clone().project(cam);"
             "r.push(Math.abs(p.x)<1&&Math.abs(p.y)<1&&Math.abs(st.truck.position.z)<.05);});renderCena(9,9.8);"
             "var q=st.roof.position.clone().project(cam);r.push(Math.abs(st.roof.position.y-3.67)<.05&&Math.abs(q.x)<1&&Math.abs(q.y)<1);return r;})()",
             [True, True, True, True]),
    "icamento": ("(function(){var st=SC[10];renderCena(10,5);var a=st.cabos.geometry.attributes.position.array,n=0;"
                 "for(var i=0;i<a.length;i+=6){if(Math.abs(a[i]-a[i+3])<1e-6&&Math.abs(a[i+2]-a[i+5])<1e-6&&Math.abs(a[i+1]-a[i+4])<10)n++;}"
                 "return [n,st.mod.position.y>3];})()", [4, True]),
    "zip": ("(function(){var st=SC[11],f=function(){return Math.round(((1-(((st.mm.rotation.z/(2*Math.PI))%1)+1)%1)%1)*60)%60;};"
            "renderCena(11,1.2);var a=f();renderCena(11,8);var b=f();return [a,b,!!st.walls&&st.walls.count>100];})()", [35, 11, True]),
}


def checar_cenas_portadas(passos):
    """Com o Chromium (SwiftShader) no film.html?limpo: a classe .limpo esconde a legenda; cada cena portada existe e responde a renderCena."""
    import shutil
    from playwright.sync_api import sync_playwright
    from render_clipes import ARGS
    erros = []
    with sync_playwright() as p:
        exe = shutil.which("chromium")
        nav = p.chromium.launch(executable_path=exe, args=ARGS) if exe else p.chromium.launch(args=ARGS)
        pg = nav.new_page(viewport={"width": 1280, "height": 720})
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.goto(FILME.as_uri() + "?limpo")
        pg.wait_for_timeout(2000)
        pg.evaluate("PRONTO")
        check(pg.evaluate("document.documentElement.classList.contains('limpo')"), "?limpo não ligou a classe .limpo")
        check(pg.evaluate("getComputedStyle(document.getElementById('cap')).display") == "none", ".limpo não escondeu a legenda")
        for passo in passos:
            idx = CLIPES[passo][0]
            check(pg.evaluate(f"!!SC[{idx}]"), f"SC[{idx}] ({passo}) não existe")
            if pg.evaluate(f"!!SC[{idx}]"):
                exp, esperado = LEITURAS[passo]
                achado = pg.evaluate(exp)
                check(achado == esperado, f"cena portada {passo}: conteúdo {achado} ≠ {esperado}")
        if set(passos) == set(PORTADAS):
            check(pg.evaluate("SC.length") == 12, "SC deve ter 12 cenas (9 do filme + 3 portadas)")
        nav.close()
    check(not erros, f"erros de JS no film.html?limpo: {erros}")
```

Em `main()`: depois de `checar_limpo(filme)`, `if "--cenas" in sys.argv: passos = [a for a in sys.argv[sys.argv.index("--cenas") + 1:] if not a.startswith("--")] or list(PORTADAS); checar_portadas(filme, passos); checar_cenas_portadas(passos)`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --cenas casa`
Expected: `FALHOU:` com `film.html: falta o bloco '// ================= CASA …'` e `SC[9] (casa) não existe`.

- [ ] **Step 3: O bloco da cena em `film.html`** (colar logo antes de `// ================= render =================`)

```js
// ================= CASA (portada da página: casa-viaja, 10 s) =================
// três viagens: caixa 1, caixa 2 (face de junção aberta: pórtico, viga de transferência e filme) e o telhado em kit,
// montado no pátio pelos montadores e içado inteiro. Acento: a viga de transferência. Sem texto.
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
slab(34,30,0xB8C99A,g);box(4.2,.05,40,0x9A958D,9,.04,0,g,true);for(var i=-19;i<20;i+=3)box(.12,.06,1.4,0xF3EFE6,9,.07,i,g,true);
[[-11,-8,1.3],[-12,4,1.1],[-8,9,1],[-6,-11,1.2],[-13,-2,.9],[3,10,1.1],[-6,10.5,.8],[14,-9,1],[14,6,1.1]].forEach(function(t){tree(t[0],t[1],t[2],g);});
var W=6,H=2.85,D=3,PIL=.55;for(var r=0;r<3;r++)[-2.6,0,2.6].forEach(function(x){box(.24,PIL,.24,0xC9C2B4,x,PIL/2,-2.5+r*2.5,g);});
function caixa(front){var q=new THREE.Group(),oz=front?-(D/2-.09):(D/2-.09),cz=front?(D/2-.06):-(D/2-.06);
 box(W,.22,D,0x8E9AA6,0,.11,0,q);box(W-.03,.05,D-.03,0xC7A57A,0,.245,0,q,true);
 box(W,H,.12,0xF3ECDD,0,.27+H/2,cz,q);box(.12,H,D,0xF3ECDD,-(W/2-.06),.27+H/2,0,q);box(.12,H,D,0xF3ECDD,W/2-.06,.27+H/2,0,q);box(W,.12,D,0xF3ECDD,0,.27+H-.06,0,q);
 box(.18,H-.12,.18,0x7D8E9E,-(W/2-.21),.27+(H-.12)/2,oz,q);box(.18,H-.12,.18,0x7D8E9E,W/2-.21,.27+(H-.12)/2,oz,q);box(W-.24,.42,.2,ORANGE,0,.27+H-.12-.21,oz,q);
 var dl=Math.hypot(W-.5,H-.5),da=Math.atan2(H-.5,W-.5);[1,-1].forEach(function(s){box(dl,.05,.05,0x7D8E9E,0,.27+(H-.42)/2,oz,q,true).rotation.z=s*da;});
 var fm=new THREE.Mesh(new THREE.BoxGeometry(W-.2,H-.5,.03),new THREE.MeshStandardMaterial({color:0xE3EBF2,transparent:true,opacity:.5,roughness:.3,depthWrite:false}));
 fm.position.set(0,.27+(H-.42)/2,oz+(front?-.14:.14));q.add(fm);q.filme=fm;
 if(front){box(1.3,2.2,.08,0xC7A57A,-1.55,.27+1.1,D/2+.05,q);box(1.3,2.2,.08,0xC7A57A,1.55,.27+1.1,D/2+.05,q);box(2.6,.6,.08,0xF3ECDD,0,.27+2.5,D/2+.05,q);box(2.55,2.05,.02,0x3A302A,0,.27+1.05,D/2+.02,q,true);}
 else box(1.2,1,.08,0xBFD8E6,-1.6,.27+1.5,-D/2-.05,q,true);
 box(.08,1,1.1,0xBFD8E6,-W/2-.05,.27+1.4,0,q,true);box(.08,1,1.1,0xBFD8E6,W/2+.05,.27+1.4,0,q,true);g.add(q);return q;}
st.c1=caixa(true);st.c2=caixa(false);
// telhado gambrel em kit: cada peça tem a pose deitada (p0, no chão do pátio) e a pose montada (p1)
var XQ=1.68,HQ=(3-XQ)*Math.tan(Math.PI/3),HH=HQ+XQ*Math.tan(Math.PI/6),RL=6.6;st.HH=HH;
st.roof=new THREE.Group();g.add(st.roof);var kit=[],ni=0;
function peca(m,p1,r1,p0,r0){m.rotation.copy(r1);var q1=m.quaternion.clone();m.rotation.copy(r0);var q0=m.quaternion.clone();m.position.copy(p1);m.quaternion.copy(q1);kit.push({m:m,p0:p0,q0:q0,p1:p1,q1:q1});st.roof.add(m);}
function agua(x0,y0,x1,y1){var L=Math.hypot(x1-x0,y1-y0),m=new THREE.Mesh(new THREE.BoxGeometry(L,.16,RL),P(0x4A4E55));m.castShadow=m.receiveShadow=true;edge(m);
 var ang=Math.atan2(y1-y0,x1-x0);if(ang>Math.PI/2)ang-=Math.PI;peca(m,new THREE.Vector3((x0+x1)/2,(y0+y1)/2,0),new THREE.Euler(0,0,ang),new THREE.Vector3(ni%2?.4:-.4,.08+ni*.18,0),new THREE.Euler(0,0,0));ni++;}
[-1,1].forEach(function(s){agua(s*3.3,0,s*XQ,HQ);agua(s*XQ,HQ,0,HH);});
var shp=new THREE.Shape();shp.moveTo(-3,0);shp.lineTo(-XQ,HQ);shp.lineTo(0,HH);shp.lineTo(XQ,HQ);shp.lineTo(3,0);shp.closePath();
[-1,1].forEach(function(s,i){var f=new THREE.Mesh(new THREE.ExtrudeGeometry(shp,{depth:.1,bevelEnabled:false}),P(0xF3ECDD));f.castShadow=true;edge(f);
 peca(f,new THREE.Vector3(0,0,s*2.95-.05),new THREE.Euler(0,0,0),new THREE.Vector3(-HH/2,.9+i*.12,0),new THREE.Euler(0,Math.PI/2,-Math.PI/2,'ZYX'));});
function montar(k){kit.forEach(function(p,i){var ki=ease(k*1.6-i*.12);p.m.position.lerpVectors(p.p0,p.p1,ki);p.m.quaternion.copy(p.q0).slerp(p.q1,ki);});}
// caminhão (cabine para +z: entra e sai de frente) e guindaste articulado
st.truck=new THREE.Group();g.add(st.truck);box(7.4,.5,2.6,0xDCD5C6,-.6,1.05,0,st.truck);box(2,2.2,2.5,0x8E9AA6,3.9,1.9,0,st.truck);box(1.9,.9,2.3,0xBFD8E6,3.95,2.7,0,st.truck,true);
[[-3.2,-1.2],[-3.2,1.2],[-1.6,-1.2],[-1.6,1.2],[3.5,-1.2],[3.5,1.2]].forEach(function(w){cyl(.55,.5,0x2B2F33,w[0],.55,w[1],st.truck,14).rotation.z=Math.PI/2;});st.truck.rotation.y=-Math.PI/2;
var crane=new THREE.Group();crane.position.set(5.5,0,-6.5);g.add(crane);box(4.6,.9,2.4,0xE8B53E,0,.95,0,crane);
[[-1.5,-1.3],[-1.5,1.3],[1.5,-1.3],[1.5,1.3]].forEach(function(w){cyl(.6,.6,0x2B2F33,w[0],.6,w[1],crane,14).rotation.z=Math.PI/2;});
[[-2.2,-1.5],[-2.2,1.5],[2.2,-1.5],[2.2,1.5]].forEach(function(o){box(.3,.3,1.3,0xB88A2E,o[0],.55,o[1]*.8,crane);cyl(.12,.7,0x7D8E9E,o[0],.35,o[1]*1.2,crane,8);});
var turret=new THREE.Group();turret.position.set(-.6,1.4,0);crane.add(turret);box(2.4,.9,1.9,0xB88A2E,0,.45,0,turret);box(1.2,1.1,1.4,0xE8B53E,-1.2,.55,.9,turret);
var pivot=new THREE.Group();pivot.position.set(.6,.8,0);turret.add(pivot);var L=11.5;box(L,.5,.5,0xE8B53E,L/2,0,0,pivot);box(L*.5,.36,.36,0xB88A2E,L*.9,0,0,pivot);
var tip=new THREE.Object3D();tip.position.set(L,0,0);pivot.add(tip);
var cabo=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]),new THREE.LineBasicMaterial({color:0x2a2622}));cabo.frustumCulled=false;g.add(cabo);
var hook=box(.5,.35,.5,0xB88A2E,0,0,0,g);
function boneco(x,z,ry){var q=new THREE.Group();cyl(.14,.75,0x6F8FA8,0,.375,0,q,8);box(.5,.6,.3,0xE3C46A,0,1.05,0,q);var h=new THREE.Mesh(new THREE.SphereGeometry(.17,10,8),P(0xE0B294));h.position.y=1.52;h.castShadow=true;q.add(h);cyl(.2,.12,0xE8B53E,0,1.66,0,q,8);q.position.set(x,0,z);q.rotation.y=ry;q.visible=false;g.add(q);return q;}
var YARD=new THREE.Vector3(3,0,-11.5),TOP=new THREE.Vector3(0,PIL+.27+H,0),BED=new THREE.Vector3(9,1.3,-.6);
var gente=[boneco(-.4,-10.6,Math.PI/2),boneco(6.8,-14,-Math.PI/2),boneco(3.6,-15,0)];
var TG={truck:new THREE.Vector3(9,0,0),site1:new THREE.Vector3(0,0,1.5),site2:new THREE.Vector3(0,0,-1.5),mid:new THREE.Vector3(0,0,0)};
var cur=new THREE.Vector3(9,0,0),wp=new THREE.Vector3(),tipW=new THREE.Vector3();
function aimBoom(target){g.updateMatrixWorld(true);pivot.getWorldPosition(wp);var dx=target.x-wp.x,dz=target.z-wp.z,d=Math.hypot(dx,dz);turret.rotation.y=Math.atan2(-dz,dx);pivot.rotation.z=Math.acos(Math.min(.98,d/L));}
function icar(t,t0,t1,bx,fr,to,restY,r0,r1,hy){var a=ramp(t,t0,t0+(t1-t0)*.3),b=ramp(t,t0+(t1-t0)*.3,t0+(t1-t0)*.7),c=ramp(t,t0+(t1-t0)*.7,t1);
 var x=lerp(fr.x,to.x,b),z=lerp(fr.z,to.z,b),y=c>0?lerp(hy,restY,c):lerp(fr.y,hy,a);bx.position.set(x,y,z);bx.rotation.y=lerp(r0,r1,b);cur.set(x,0,z);return bx;}
st.cam=[[0,[16,7,20],[3,2,-1]],[2.5,[13,6,9],[4,2.5,-.5]],[5,[14,9,-6],[3,3,-2]],[7.5,[13,10,-16],[2,2.5,-7]],[10,[15,8,12],[1,3,-2]]];
st.run=function(t){
 // caminhão: da névoa (z −16) ao ponto de descarga (z 0) e de volta, três vezes
 var tz;if(t<.8)tz=lerp(-16,0,ramp(t,.2,.8));else if(t<3)tz=0;else if(t<3.6)tz=lerp(0,16,ramp(t,3,3.6));else if(t<4.2)tz=lerp(-16,0,ramp(t,3.6,4.2));
 else if(t<6.2)tz=0;else if(t<6.8)tz=lerp(0,16,ramp(t,6.2,6.8));else if(t<7.4)tz=lerp(-16,0,ramp(t,6.8,7.4));else if(t<8.8)tz=0;else tz=lerp(0,16,ramp(t,8.8,9.4));
 st.truck.position.set(9,0,tz);
 var att=null,topo=0;function naCarroceria(o,ry){o.position.set(BED.x,BED.y,tz+BED.z);o.rotation.y=ry;}
 function filme(c,a,b){c.filme.material.opacity=.5*(1-ramp(t,a,b));c.filme.visible=c.filme.material.opacity>.01;}
 if(t<.8)naCarroceria(st.c1,-Math.PI/2);else if(t<3){att=icar(t,.8,3,st.c1,BED,TG.site1,PIL,-Math.PI/2,0,7.2);topo=3.4;}else{st.c1.position.set(0,PIL,1.5);st.c1.rotation.y=0;}
 filme(st.c1,3,3.4);
 st.c2.visible=t>=3.6;
 if(st.c2.visible){if(t<4.2)naCarroceria(st.c2,Math.PI/2);else if(t<6.2){att=icar(t,4.2,6.2,st.c2,BED,TG.site2,PIL,Math.PI/2,0,7.2);topo=3.4;}else{st.c2.position.set(0,PIL,-1.5);st.c2.rotation.y=0;}}
 filme(st.c2,6.2,6.6);
 st.roof.visible=t>=6.8;
 if(t<7.4){naCarroceria(st.roof,0);montar(0);}
 else if(t<7.8){att=icar(t,7.4,7.8,st.roof,BED,YARD,0,0,0,5.5);topo=1.2;montar(0);}
 else if(t<8.8){st.roof.position.copy(YARD);montar(ramp(t,7.85,8.75));}
 else if(t<9.8){att=icar(t,8.8,9.8,st.roof,YARD,TOP,TOP.y,0,0,5.4);topo=HH+.3;montar(1);}
 else{st.roof.position.copy(TOP);montar(1);}
 var mexida=ramp(t,7.8,7.95)*(1-ramp(t,8.75,8.85));
 gente.forEach(function(q,i){q.visible=t>=7.4;var ph=t*18+i*2;q.position.y=mexida*.12*Math.abs(Math.sin(ph));q.rotation.z=mexida*.08*Math.sin(ph*.7);});
 aimBoom(att?cur:(t<.8?TG.truck:t<3.6?TG.site1:t<4.2?TG.truck:t<6.8?TG.site2:t<7.4?TG.truck:t<8.8?YARD:TG.mid));
 g.updateMatrixWorld(true);tip.getWorldPosition(tipW);
 var hookY=att?att.position.y+topo:tipW.y-2.2;hook.position.set(tipW.x,hookY,tipW.z);
 cabo.geometry.setFromPoints([tipW,new THREE.Vector3(tipW.x,hookY+.18,tipW.z)]);};
})();
```

- [ ] **Step 4: Ver passar o teste; render e quadros**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --cenas casa && python3 portfolio/filme/render_clipes.py --so casa && python3 portfolio/tests/check_filme.py --video origem casa`
Expected: `OK`, `casa: 240 quadros`, `casa: NNN KB (crf 28)`, `OK`.

Se `check_filme.py --cenas casa` reprovar `conteúdo [...] ≠ [True, True, True, True]`, o caminhão ou o telhado estão fora do quadro numa das chaves: ajuste **só** `st.cam` (afaste a câmera ou mova o alvo para o objeto) e rode de novo. Não mexa nos tempos.

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && for N in 8 40 100 170 200 239; do ffmpeg -y -loglevel error -i portfolio/site/video/cena-casa.mp4 -vf "select='eq(n,$N)'" -vframes 1 -update 1 $S/casa-$N.png; done && magick $S/casa-{8,40,100}.png -resize 50% +append $S/casa-a.png && magick $S/casa-{170,200,239}.png -resize 50% +append $S/casa-b.png
```

Abrir `casa-a.png` e `casa-b.png` com a ferramenta Read. Expected: caminhão chegando com a caixa 1 (viga laranja à vista na face aberta); caixa no ar pelo guindaste; segunda caixa pousada ao lado; kit do telhado no pátio com os três montadores; telhado subindo inteiro; casa pronta com o telhado gambrel, caminhão saindo. Nada escrito em parte alguma. Se a composição deixar a casa colada na borda direita ou o pátio fora do quadro, ajustar `st.cam` e renderizar de novo.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/tests/check_filme.py portfolio/site/video/cena-casa.mp4 portfolio/site/video/cena-casa.webp
git commit -m "Filme: cena da casa (três viagens, telhado em kit) portada da página no estilo do filme; clipe casa (10 s)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 5: Cena portada `icamento` (SC[10], 8 s)

**Files:**
- Modify: `portfolio/filme/film.html` (bloco novo depois do bloco CASA)

**Interfaces:**
- Produces: `SC[10]` com `st.mod` (Group do módulo), `st.bal`, `st.cabos` (LineSegments: 4 cabos verticais balancim→olhal, 4 eslingas, 1 cabo do guindaste), `st.cam` (4 chaves). Tempo local `t` 0..10 = 8 s de clipe (t = s·1,25).

- [ ] **Step 1: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --cenas casa icamento`
Expected: `FALHOU:` com `falta o bloco '// ================= IÇAMENTO …'` e `SC[10] (icamento) não existe`.

- [ ] **Step 2: O bloco da cena** (colar depois do bloco CASA, antes de `// ================= render`)

```js
// ================= IÇAMENTO (portado da página: icamento, 8 s) =================
// o módulo sai da carreta, sobe pelo balancim com os cabos na vertical (só tração nos olhais), anda e pousa no radier.
// Acento: o cavalo da carreta. Sem texto. t 0..10 = 8 s: 0→0,6 s parado · 0,6→3 sobe · 3→5,4 anda · 5,4→7,2 pousa · 7,2→8 parado
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
var L=8,C=3.2,H=2.9,CH=.3,TOPO=6.5,XC=6,XR=-6;
slab(60,40,0xB8C99A,g);box(L+2,.5,C+1.6,0xC9C2B4,XR,.25,0,g);
box(L+1,.5,C,0x4A4E55,XC,.55,0,g);box(L+1,.4,C+.6,0x8E9AA6,XC,1,0,g);box(2.4,2.6,C+.4,ORANGE,XC+L/2+1.9,1.5,0,g);box(2.2,1,C+.2,0xBFD8E6,XC+L/2+1.9,2.5,0,g,true);
[[XC-3,-1.6],[XC-3,1.6],[XC+1,-1.6],[XC+1,1.6],[XC+L/2+1.9,-1.8],[XC+L/2+1.9,1.8]].forEach(function(w){cyl(.5,.4,0x2B2F33,w[0],.5,w[1],g,14).rotation.x=Math.PI/2;});
st.mod=new THREE.Group();g.add(st.mod);box(L,CH,C,0x7D8E9E,0,CH/2,0,st.mod);box(L-.1,H-CH,C-.1,0xF3ECDD,0,CH+(H-CH)/2,0,st.mod);box(L+.2,.14,C+.3,0x4A4E55,0,H+.07,0,st.mod);
box(1.1,1.9,.06,0xC7A57A,-2.2,CH+.95,C/2,st.mod,true);box(1.4,.9,.06,0xBFD8E6,1.6,CH+1.6,C/2,st.mod,true);
var cx=L/2-.2,cz=C/2+.05,cantos=[[-cx,-cz],[cx,-cz],[-cx,cz],[cx,cz]];
cantos.forEach(function(c){var o=new THREE.Mesh(new THREE.TorusGeometry(.16,.05,8,20),P(0xE8B53E));o.position.set(c[0],CH+.05,c[1]);st.mod.add(o);});
st.bal=new THREE.Group();g.add(st.bal);box(L,.25,.25,0xE8B53E,0,0,cz,st.bal);box(L,.25,.25,0xE8B53E,0,0,-cz,st.bal);box(.25,.25,C+.1,0xE8B53E,-cx,0,0,st.bal);box(.25,.25,C+.1,0xE8B53E,cx,0,0,st.bal);
var gancho=new THREE.Mesh(new THREE.TorusGeometry(.3,.08,8,20),P(0x4A4E55));g.add(gancho);
st.cabos=new THREE.LineSegments(new THREE.BufferGeometry(),new THREE.LineBasicMaterial({color:0x2a2622}));st.cabos.frustumCulled=false;g.add(st.cabos);
tree(-14,-9,1.2,g);tree(13,-10,1,g);tree(-12,9,.9,g);tree(16,7,1.1,g);
st.cam=[[0,[24,13,24],[6,3.5,0]],[3.3,[18,16,22],[2,6.5,0]],[6.6,[-4,17,26],[-3,6.5,0]],[10,[-23,12,23],[-6,3,0]]];
st.run=function(t){var x=lerp(XC,XR,ramp(t,3.75,6.75)),y=t<6.75?lerp(1.2,TOPO,ramp(t,.75,3.75)):lerp(TOPO,.5,ramp(t,6.75,9));
 st.mod.position.set(x,y,0);var bY=y+H+2.2,hY=bY+2.6,pts=[];st.bal.position.set(x,bY,0);gancho.position.set(x,hY,0);
 cantos.forEach(function(c){pts.push(x+c[0],bY,c[1],x+c[0],y+CH+.05,c[1]);pts.push(x+c[0],bY,c[1],x,hY,0);}); // cabo vertical balancim→olhal; eslinga balancim→gancho
 pts.push(x,hY,0,x,hY+30,0); // cabo do guindaste, para fora do quadro
 st.cabos.geometry.setAttribute('position',new THREE.Float32BufferAttribute(pts,3));};
})();
```

- [ ] **Step 3: Ver passar; render; quadros**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --cenas casa icamento && python3 portfolio/filme/render_clipes.py --so icamento && python3 portfolio/tests/check_filme.py --video origem casa icamento`
Expected: `OK`, `icamento: 192 quadros`, `icamento: NNN KB (crf 28)`, `OK`.

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && for N in 8 60 100 150 191; do ffmpeg -y -loglevel error -i portfolio/site/video/cena-icamento.mp4 -vf "select='eq(n,$N)'" -vframes 1 -update 1 $S/ica-$N.png; done && magick $S/ica-{8,60,100,150,191}.png -resize 40% +append $S/ica.png
```

Abrir `ica.png`. Expected: módulo na carreta (cavalo laranja); subindo com o balancim amarelo e os quatro cabos verticais; no ar a caminho do radier; descendo; pousado no radier com os cabos frouxos. Balancim e cabos dentro do quadro em todos.

- [ ] **Step 4: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/site/video/cena-icamento.mp4 portfolio/site/video/cena-icamento.webp
git commit -m "Filme: cena do içamento (balancim, cabos verticais) portada da página; clipe icamento (8 s)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 6: Cena portada `zip` — 36 minutos (SC[11], 10 s)

**Files:**
- Modify: `portfolio/filme/film.html` (bloco novo depois do bloco IÇAMENTO; alimenta `PRONTOS`)

**Interfaces:**
- Consumes: `PRONTOS` (Task 3); `../site/img/upa-plan.webp` (paredes: pixels vermelhos) e `../site/img/upa-plan-grey.webp` (textura do chão), ambas já publicadas.
- Produces: `SC[11]` com `st.walls` (InstancedMesh, preenchido depois do `load` da imagem), `st.sweep`, `st.mm`/`st.hm` (ponteiros), `st.zip`, `st.pages`, `st.cam` (4 chaves). `window.PRONTO` só resolve depois das duas imagens.

- [ ] **Step 1: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --cenas`
Expected: `FALHOU:` com `falta o bloco '// ================= 36 MINUTOS …'`, `SC[11] (zip) não existe`, `SC deve ter 12 cenas`.

- [ ] **Step 2: O bloco da cena** (depois do bloco IÇAMENTO, antes de `// ================= render`)

```js
// ================= 36 MINUTOS (portado da página: 36min, 10 s) =================
// a planta real do cliente (já publicada, anônima) no chão; a linha de cota varre a planta e as paredes de papel sobem
// nos pixels vermelhos; o relógio analógico anda de 11:35 a 12:11 com a varredura; a proposta empilha na mesa.
// Acento: a cota (e o ponteiro dos minutos). Sem texto. t: pacote pousa 0,3→0,9 · varredura e relógio 1,2→8,0 · páginas 8,0→9,4 · parado até 10
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
var PW=16,PH=PW*440/1400,CELL=5,HW=1.4;
slab(PW+4,PH+5,0xE2D6C1,g);
var planoTex;PRONTOS.push(new Promise(function(ok){planoTex=new THREE.TextureLoader().load('../site/img/upa-plan-grey.webp',ok,undefined,ok);}));
planoTex.encoding=THREE.sRGBEncoding;planoTex.anisotropy=4;
var planta=new THREE.Mesh(new THREE.PlaneGeometry(PW,PH),new THREE.MeshStandardMaterial({map:planoTex,roughness:1}));planta.rotation.x=-Math.PI/2;planta.position.y=.005;planta.receiveShadow=true;g.add(planta);
var wx=[],dummy=new THREE.Object3D();st.walls=null;
PRONTOS.push(new Promise(function(ok){var im=new Image();im.onload=function(){var w=1400,h=440,cv=document.createElement('canvas');cv.width=w;cv.height=h;var cx=cv.getContext('2d');cx.drawImage(im,0,0,w,h);
 var d=cx.getImageData(0,0,w,h).data,cells=[];
 for(var gy=0;gy<h;gy+=CELL)for(var gx=0;gx<w;gx+=CELL){var n=0;for(var y=gy;y<gy+CELL&&y<h;y++)for(var x=gx;x<gx+CELL&&x<w;x++){var k=(y*w+x)*4;if(d[k]>150&&d[k+1]<90&&d[k+2]<90)n++;}if(n>=CELL*CELL*.3)cells.push([gx,gy]);}
 var s=PW/w;st.walls=new THREE.InstancedMesh(new THREE.BoxGeometry(CELL*s,1,CELL*s),P(0xF3ECDD),cells.length);st.walls.castShadow=st.walls.receiveShadow=true;
 cells.forEach(function(c){wx.push([(c[0]+CELL/2)*s-PW/2,(c[1]+CELL/2)*s-PH/2]);});g.add(st.walls);ok();};im.onerror=ok;im.src='../site/img/upa-plan.webp';}));
var COTA=new THREE.MeshBasicMaterial({color:ORANGE});st.sweep=box(.1,.08,PH+1,COTA,0,.1,0,g,true);var sweepTop=box(.05,2.4,.05,COTA,0,1.2,-PH/2-.5,g,true);
var mesa=new THREE.Group();mesa.position.set(PW/2-1.5,0,PH/2+2.6);g.add(mesa);
box(4.2,.16,2.2,0xC7A57A,0,1.05,0,mesa);[[-1.9,-.9],[1.9,-.9],[-1.9,.9],[1.9,.9]].forEach(function(p){box(.14,1,.14,0x8C6E4E,p[0],.5,p[1],mesa);});
st.zip=box(.9,.6,.75,0xC9B79A,-1.3,1.43,0,mesa);
st.pages=[];for(var i=0;i<7;i++){var pg=box(1.1,.03,1.5,0xFFFFFF,1,1.15+i*.035,0,mesa,true);pg.rotation.y=(i%2?.05:-.04);pg.visible=false;st.pages.push(pg);}
// relógio analógico do filme (mostrador com 12 traços, sem algarismos) num pedestal ao lado da mesa
var CX=PW/2+2.4,CY=2.1,CZ=PH/2+.2;box(.5,CY-.6,.5,0xC9B79A,CX,(CY-.6)/2,CZ,g);var face=cyl(.9,.1,0xFBF8F0,CX,CY,CZ,g,32);face.rotation.x=Math.PI/2;
for(var q=0;q<12;q++){var tk=box(.05,.14,.02,0x1E1A17,CX+Math.sin(q*Math.PI/6)*.72,CY+Math.cos(q*Math.PI/6)*.72,CZ+.06,g,true);tk.rotation.z=-q*Math.PI/6;}
st.hm=box(.08,.48,.03,0x1E1A17,CX,CY,CZ+.09,g,true);st.hm.geometry.translate(0,.24,0);st.mm=box(.05,.72,.03,ORANGE,CX,CY,CZ+.11,g,true);st.mm.geometry.translate(0,.36,0);
tree(-PW/2-3.5,-PH/2-1,.9,g);tree(PW/2+4,-PH/2-2,.8,g);
st.cam=[[0,[0,19,3],[0,0,.5]],[2.5,[-11,8,10],[-3,.6,.5]],[7,[6,3.6,7],[2.5,.9,-.3]],[10,[9,8,12],[3,.8,1.2]]];
st.run=function(t){var p=cl((t-1.2)/6.8),sx=lerp(-PW/2-.4,PW/2+.4,p);st.sweep.position.x=sx;sweepTop.position.x=sx;st.sweep.visible=sweepTop.visible=t>1&&t<8.3;
 if(st.walls){for(var i=0;i<wx.length;i++){var hh=Math.max(.001,ease((sx-wx[i][0])/2.5)*HW);dummy.position.set(wx[i][0],.01+hh/2,wx[i][1]);dummy.scale.set(1,hh,1);dummy.updateMatrix();st.walls.setMatrixAt(i,dummy.matrix);}st.walls.instanceMatrix.needsUpdate=true;}
 st.zip.position.y=lerp(6,1.43,ramp(t,.3,.9));
 var mm=35+36*p;st.mm.rotation.z=-(mm/60)*Math.PI*2;st.hm.rotation.z=-((11+mm/60)/12)*Math.PI*2; // 11:35 → 12:11, linear com a varredura
 st.pages.forEach(function(pg,i){var a=ramp(t,8+i*.17,8.35+i*.17);pg.visible=a>0;pg.position.y=lerp(3,1.15+i*.035,a);pg.position.z=lerp(-1,0,a);});};
})();
```

- [ ] **Step 3: Ver passar; render; quadros**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --cenas && python3 portfolio/filme/render_clipes.py --so zip && python3 portfolio/tests/check_filme.py --video origem casa icamento zip`
Expected: `OK` (com `SC.length == 12` e `st.walls.count > 100`), `zip: 240 quadros`, `zip: NNN KB (crf 28)`, `OK`.

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && for N in 8 40 110 180 239; do ffmpeg -y -loglevel error -i portfolio/site/video/cena-zip.mp4 -vf "select='eq(n,$N)'" -vframes 1 -update 1 $S/zip-$N.png; done && magick $S/zip-{8,40,110,180,239}.png -resize 40% +append $S/zip.png
```

Abrir `zip.png`. Expected: planta cinza vista de cima, pacote kraft caindo na mesa; cota laranja começando à esquerda com as primeiras paredes de papel de pé; meio da varredura, paredes em primeiro plano, relógio perto das 11:53; varredura no fim, relógio em 12:11; planta pronta com a pilha de 7 páginas. **Nenhum texto** além do que a própria planta publicada traz.

- [ ] **Step 4: Commit**

```bash
cd /home/runner/workspace && git add portfolio/filme/film.html portfolio/site/video/cena-zip.mp4 portfolio/site/video/cena-zip.webp
git commit -m "Filme: cena dos 36 minutos (planta real, cota, relógio analógico) portada da página; clipe zip (10 s)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 7: Os 11 clipes renderizados

**Files:**
- Create: `portfolio/site/video/cena-{obra,veks,ferramentas,sige,escala,whatsapp,recuperado}.{mp4,webp}` (gerados); os 4 já commitados podem ser regerados (o render é determinístico a menos da textura de papel aleatória: aceite as diferenças de bytes)

- [ ] **Step 1: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --video`
Expected: `FALHOU:` com 7 linhas `falta cena-<passo>.mp4 ou …` (obra, veks, ferramentas, sige, escala, whatsapp, recuperado).

- [ ] **Step 2: Render completo (~10 min; rodar em segundo plano e esperar)**

Run: `cd /home/runner/workspace && python3 portfolio/filme/render_clipes.py 2>&1 | tee /tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad/render.log`
Expected: uma linha `<passo>: N quadros` e uma `<passo>: NNN KB (crf 28|29|30)` por clipe, depois `soma dos clipes: X.XX MB` com X ≤ 8, e `pronto: …/site/video`. Se algum clipe passar de 0,9 MB com crf 30, o script para com o nome dele: relatar; não subir o teto.

- [ ] **Step 3: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_filme.py --video && du -ch portfolio/site/video/cena-*.mp4 | tail -1 && ls portfolio/site/video`
Expected: `OK`; total ≤ 8,0M; 22 arquivos `cena-*` (mais `historia.mp4`/`historia.jpg`, que saem na Task 9).

- [ ] **Step 4: Conferir o último quadro de cada clipe (o pôster) contra a tabela da spec**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && magick portfolio/site/video/cena-{origem,obra,veks,ferramentas}.webp -resize 45% +append $S/posters-a.png && magick portfolio/site/video/cena-{sige,escala,whatsapp,recuperado}.webp -resize 45% +append $S/posters-b.png && magick portfolio/site/video/cena-{casa,icamento,zip}.webp -resize 45% +append $S/posters-c.png
```

Abrir os três PNG. Expected (coluna "Pôster" da spec): origem = tela "confere", moeda na mesa · obra = 5 cartões "MESMO DADO", treliça no alto · veks = guia e montantes de pé (sem as placas) · ferramentas = placas na parede, "PLANO DE CORTE" no chão · sige = 8 andares acesos, placa "EM USO" · escala = restaurante pronto e as 12 miniaturas · whatsapp = celular "Obra galpões", quadro **sem** balão chegando · recuperado = quadro com barras verdes · casa = telhado pousado, caminhão saindo · icamento = módulo no radier, cabos frouxos · zip = paredes de pé, relógio em 12:11, pilha de páginas. Nenhum pôster com tarja, legenda ou HUD.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/video/cena-*.mp4 portfolio/site/video/cena-*.webp
git commit -m "Os 11 clipes de fundo da história renderizados (960×540, 24 fps, GOP 4, ≤ 0,9 MB cada) com pôsteres

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 8: `clipes.js`

**Files:**
- Create: `portfolio/site/clipes.js`
- Modify: `portfolio/tests/check_historia.py` (`checar_clipes_js`)

**Interfaces:**
- Produces: em cada `figure.clipe`, `fig.__clipe = {dur, frozen, seek(t), descarregar()}`, criado na hora (com `dur` de `data-dur`) mesmo quando o clipe não vai carregar (`seek` só marca `frozen` e guarda o alvo). Constantes `FPS=24,TETO=250,LENTOS=3,VOO=600,MAXIMO=2`. Nada mais é global.
- Consumes: `historia.js` chama `fig.__clipe.seek(progresso·dur·0,999)` a cada quadro de rolagem da cena ativa (Task 10 renomeia `__maquete` → `__clipe`).

- [ ] **Step 1: Teste estático (F-06)**

Em `check_historia.py`, depois de `checar_js()`:

```python
def checar_clipes_js():
    caminho = SITE / "clipes.js"
    check(caminho.exists(), "portfolio/site/clipes.js não existe")
    if not caminho.exists():
        return
    js = re.sub(r"//[^\n]*", "", caminho.read_text(encoding="utf-8"))  # comentários não contam
    for proibido in ("play(", "autoplay", "loop", "fastSeek", "requestAnimationFrame", "fetch(", "createObjectURL",
                     "scrollTo", "scrollBy", "scrollIntoView", "preventDefault", "'wheel'", "'touchmove'", "aria-live"):
        check(proibido not in js, f"clipes.js não pode usar {proibido}")
    for exigido in ("canPlayType", "'seeked'", "seekable", "rootMargin:'600px", "preload='auto'", ".load()", "removeAttribute('src')",
                    "prefers-reduced-motion: reduce", "'change'", "saveData", "clipes=nao", "readyState", "'load'",
                    "TETO=250", "LENTOS=3", "VOO=600", "MAXIMO=2", "fig.__clipe=api"):
        check(exigido in js, f"clipes.js precisa de {exigido}")
    check("(Math.round(t*FPS)+0.5)/FPS" in js, "clipes.js: seek quantizado ao quadro, (round(t·24)+0,5)/24")
    check("v.currentTime=" in js and js.count("currentTime=") == 1, "clipes.js: o tempo do vídeo só muda por currentTime, num lugar só")
```

Chamar `checar_clipes_js()` em `main()` depois de `checar_js()`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py`
Expected: `FALHOU:` com ` - portfolio/site/clipes.js não existe`.

- [ ] **Step 3: Escrever `portfolio/site/clipes.js`**

```js
// Clipes de fundo da história: um vídeo curto e mudo por capítulo, cujo tempo é o progresso da rolagem (historia.js chama
// fig.__clipe.seek(t), o mesmo contrato das maquetes). O clipe nunca anda sozinho: só currentTime, quantizado ao quadro,
// um seek em voo por vez, o último pedido vence. Carga em três portas: depois do 'load' da janela, quando a cena chega a
// 600 px da tela, e nunca com economia de dados, rede 2g, sem H.264 ou com ?clipes=nao (fica o pôster). Movimento
// reduzido, inclusive ligado no meio, descarrega tudo. A imagem só some (.viva) quando há um quadro pronto.
(function(){
'use strict';
var figs=[].slice.call(document.querySelectorAll('figure.clipe'));
if(!figs.length||!('IntersectionObserver' in window))return;
var FPS=24,TETO=250,LENTOS=3,VOO=600,MAXIMO=2; // ms de um seek lento; lentos seguidos até congelar; ms sem 'seeked' = seek perdido; vídeos com dados
var v0=document.createElement('video'),con=navigator.connection||{};
var PODE=!/[?&]clipes=nao\b/.test(location.search)&&v0.canPlayType('video/mp4; codecs="avc1.64001F"')!==''
  &&!con.saveData&&!/^(slow-)?2g$/.test(con.effectiveType||'');
var reduzir=matchMedia('(prefers-reduced-motion: reduce)'),carregados=[],perto={};
function quadro(t){return (Math.round(t*FPS)+0.5)/FPS;}
function depoisDoLoad(fn){if(document.readyState==='complete')fn();else addEventListener('load',fn);}

figs.forEach(function(fig){
  var v=fig.querySelector('video'),cena=fig.closest('.cena')||fig,src=fig.dataset.clipe,dur=parseFloat(fig.dataset.dur)||0;
  var alvo=-1,pedido=-1,emVoo=0,pronto=false,vivo=false,morto=false,lentos=0;
  var api={dur:dur,frozen:false,seek:function(t){api.frozen=true;alvo=quadro(Math.max(0,Math.min(dur,t)));pedir();},descarregar:descarregar};
  fig.__clipe=api;
  if(!PODE||!v||!dur||!src)return; // fica a imagem
  function viver(sim){vivo=sim;fig.classList.toggle('viva',sim);}
  function pedir(){
    if(!pronto||morto||reduzir.matches||alvo<0||v.readyState<1)return;   // nunca antes dos metadados: o alvo fica guardado
    if(emVoo){if(performance.now()-emVoo<VOO)return;emVoo=0;}            // um seek em voo por vez; 600 ms sem 'seeked' = perdido, libera
    if(alvo===pedido&&(vivo||emVoo))return;                               // o quadro-alvo não mudou
    pedido=alvo;emVoo=performance.now();v.currentTime=alvo;
  }
  function noBuffer(t){for(var i=0;i<v.buffered.length;i++)if(t>=v.buffered.start(i)&&t<=v.buffered.end(i))return true;return false;}
  function congelar(){morto=true;descarregar();}                          // plano B: pôster, sem mais seeks nesta figura
  function carregar(){
    if(pronto||morto||reduzir.matches)return;
    while(carregados.length>=MAXIMO)carregados.shift().descarregar();      // no máximo 2 vídeos com dados: sai o mais antigo
    carregados.push(api);pronto=true;
    v.setAttribute('src',src);v.preload='auto';v.load();
  }
  function descarregar(){
    var i=carregados.indexOf(api);if(i>=0)carregados.splice(i,1);
    if(!pronto)return;
    pronto=false;pedido=-1;emVoo=0;viver(false);v.removeAttribute('src');v.load();
  }
  v.addEventListener('loadedmetadata',function(){
    if(!v.seekable.length||v.seekable.end(0)<dur-0.5){congelar();return;} // servidor sem Range: não dá para buscar; fica o pôster
    pedir();
  });
  v.addEventListener('seeked',function(){
    var nosso=emVoo>0,levou=nosso?performance.now()-emVoo:0;emVoo=0;
    if(v.readyState===0){viver(false);return;}
    if(!vivo)viver(true);                                                  // só agora a imagem some: há um quadro pronto
    if(nosso){if(levou>TETO&&noBuffer(pedido)){if(++lentos>=LENTOS){congelar();return;}}else lentos=0;} // aparelho não dá conta
    if(alvo>=0&&alvo!==pedido)pedir();                                    // o último pedido vence
  });
  v.addEventListener('error',function(){congelar();});
  v.addEventListener('emptied',function(){if(v.readyState===0)viver(false);}); // WebKit sob pressão de memória
  depoisDoLoad(function(){
    new IntersectionObserver(function(es){perto[src]=es[0].isIntersecting;if(es[0].isIntersecting)carregar();else descarregar();},
      {rootMargin:'600px 0px'}).observe(cena);                             // a figure mora no palco sticky: observa-se a cena
  });
  reduzir.addEventListener('change',function(){if(reduzir.matches)descarregar();else if(perto[src])carregar();});
});
})();
```

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && node -e "new Function(require('fs').readFileSync('portfolio/site/clipes.js','utf8'))" && echo SINTAXE-OK`
Expected: `OK` e `SINTAXE-OK` (se não houver `node`, pular a segunda parte: o Chromium da Task 10 pega erro de sintaxe).

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/clipes.js portfolio/tests/check_historia.py
git commit -m "clipes.js: o clipe de fundo segue a rolagem por currentTime quantizado ao quadro, com carga sob demanda e pôster como plano B

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 9: O trailer sai da página e vira arquivo de envio

**Files:**
- Modify: `portfolio/filme/render.py`, `portfolio/filme/README.md`, `portfolio/site/index.html` (seção `.filme`, CSS, botão), `portfolio/tests/check_historia.py` (`checar_filme`/`duracao_video` saem; `checar_texto`; `checar_fim_do_palco` → `checar_ficha_a_vista`; `checar_sem_trailer`), `portfolio/tests/check_filme.py` (`checar_video` → `checar_trailer`, condicional; `git ls-files`)
- Delete: `portfolio/site/video/historia.mp4`, `portfolio/site/video/historia.jpg`

**Interfaces:**
- Produces: `render.py` grava `portfolio/filme/saida/historia-960.mp4` e `historia-960.jpg` (ignorados pelo git); `check_filme.py --video` confere o trailer só se o arquivo existir; `check_historia.py` não importa mais `check_filme`.

- [ ] **Step 1: Testes**

Em `check_historia.py`:
- apagar `VIDEO = …`, `duracao_video()` e `checar_filme()` inteiros e a chamada `checar_filme(pagina)` em `main()`;
- em `checar_texto`, trocar as linhas `d = duracao_video()` e `extras = …` por `extras = numeros(t) - numeros(limpo(corpo(portfolio)))`;
- trocar `checar_fim_do_palco()` por:

```python
def checar_ficha_a_vista():
    """O palco é sticky com margin-bottom:-100vh: não pode passar do fim da história e cobrir a ficha no fim da página."""
    ver = ("(function(sel){var r=document.querySelector(sel).getBoundingClientRect();"
           "var topo=Math.max(r.top,0),base=Math.min(r.bottom,innerHeight);if(base<=topo)return 'fora';"
           "var e=document.elementFromPoint(innerWidth/2,(topo+base)/2);"
           "return e&&e.closest(sel)?'visivel':(e&&e.closest('.palco')?'coberto pelo palco':'coberto por '+(e&&e.tagName));})")
    for largura in (390, 1280):
        with chromium(largura, ("--disable-3d-apis",)) as ws:
            ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/site/index.html")
            time.sleep(1.5)
            ws.avaliar("window.scrollTo(0,document.documentElement.scrollHeight)")
            time.sleep(1)
            ficha = ws.avaliar(ver + "('.ficha')")
        check(ficha == "visivel", f"{largura} px: no fim da página, a ficha precisa estar à vista ({ficha})")


def checar_sem_trailer(pagina):
    """O trailer saiu da página (F-14): nada aponta para ele; o convite tem 3 botões."""
    for trecho in ('class="filme"', 'id="filme"', 'href="#filme"', "transcricao", "Assistir ao filme", "A história em",
                   "Transcrição do filme", "historia.mp4", "historia.jpg"):
        check(trecho not in pagina, f"o trailer saiu da página: ainda há {trecho!r}")
    ultima = cenas(pagina)[-1][3] if cenas(pagina) else ""
    check(ultima.count('<a class="btn') == 3, "o convite tem exatamente 3 botões")
    check(not (SITE / "video" / "historia.mp4").exists() and not (SITE / "video" / "historia.jpg").exists(), "site/video/historia.* saem do site")
```

Em `main()`: `checar_sem_trailer(pagina)` junto das checagens estáticas; `checar_ficha_a_vista()` no lugar de `checar_fim_do_palco()`.

Em `check_filme.py`: trocar `VIDEO = SITE / "video" / "historia.mp4"` e `CAPA = …` por `TRAILER = ROOT / "filme" / "saida" / "historia-960.mp4"` e `CAPA = ROOT / "filme" / "saida" / "historia-960.jpg"`; renomear `checar_video` → `checar_trailer`:

```python
def checar_trailer():
    """Trailer de envio (WhatsApp/LinkedIn), fora do site: só se render.py já rodou. H.264 960×540, 85 s, ≤ 16 MB, moov antes."""
    if not TRAILER.exists():
        print("trailer de envio ausente (python3 portfolio/filme/render.py): pulado")
        return
    info = ffprobe(TRAILER)
    videos = [s for s in info["streams"] if s["codec_type"] == "video"]
    check(len(videos) == 1 and videos[0]["codec_name"] == "h264" and (videos[0]["width"], videos[0]["height"]) == (960, 540),
          f"trailer deve ser H.264 960×540 (achei {videos})")
    check(not [s for s in info["streams"] if s["codec_type"] == "audio"], "o trailer não tem áudio: sem faixa de som")
    total = sum(c[4] for c in CAPITULOS) + FIM
    check(abs(float(info["format"]["duration"]) - total) <= 0.5, f"duração {info['format']['duration']} s ≠ {total} s")
    check(int(info["format"]["size"]) <= 16 * 1024 * 1024, "trailer acima de 16 MB (o WhatsApp não manda como mídia)")
    dados = TRAILER.read_bytes()
    check(0 <= dados.find(b"moov") < dados.find(b"mdat"), "o índice (moov) precisa vir antes dos dados: -movflags +faststart")
    check(CAPA.exists() and tuple(ffprobe(CAPA)["streams"][0][k] for k in ("width", "height")) == (960, 540), "capa do trailer em 960×540")
```

Em `checar_clipes`, dentro do `if set(passos) == set(CLIPES):`, acrescentar:

```python
        publicados = sorted(subprocess.run(["git", "ls-files", "site/video"], cwd=ROOT, capture_output=True, text=True).stdout.split())
        esperados = sorted(f"site/video/cena-{p}.{e}" for p in CLIPES for e in ("mp4", "webp"))
        check(publicados == esperados, f"git ls-files site/video ≠ os 22 arquivos dos clipes: {publicados}")
```

E em `main()` chamar `checar_trailer()` no lugar de `checar_video()`. Trocar a docstring do módulo: "vídeo gerado (portfolio/site/video/)" → "clipes (portfolio/site/video/cena-*) e trailer de envio (portfolio/filme/saida/)". Nos `README`: "Como enviar" tem de conter "7º semestre", "CLT ou PJ", "85 s", "sem áudio" — teste em `check_filme.py`:

```python
def checar_readme():
    readme = (ROOT / "filme" / "README.md").read_text(encoding="utf-8")
    check("## Como enviar" in readme, "README do filme sem a seção \"Como enviar\"")
    for trecho in ("7º semestre", "CLT ou PJ", "85 s", "sem áudio", "16 MB"):
        check(trecho in readme, f"README do filme: \"Como enviar\" sem {trecho!r}")
```

(chamar em `main()` junto de `checar_limpo`).

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py; python3 portfolio/tests/check_filme.py`
Expected: `check_historia`: `FALHOU:` com `o trailer saiu da página: ainda há 'class="filme"'` (e os outros trechos), `site/video/historia.* saem do site`; `check_filme`: `README do filme sem a seção "Como enviar"`.

- [ ] **Step 3: `index.html`**

Apagar: o bloco CSS de `/* o filme: toca só por clique; a transcrição repete as legendas */` até `.transcricao b{color:var(--ink)}` (8 linhas); a linha `<a class="btn fantasma" href="#filme">Assistir ao filme ↓</a>`; a `<section class="filme" …>…</section>` inteira (de `<section class="filme"` até o `</section>` antes de `<section class="ficha"`). Ajustar o comentário do CSS `/* overflow:clip corta o palco … sem ele, o palco cobre o filme e a ficha */` → `… cobre a ficha */`.

- [ ] **Step 4: `render.py` e README do filme**

`render.py`: apagar `WEB = …`; `mestre, capa = SAIDA / "historia-1280.mp4", SAIDA / "capa-1280.jpg"` fica; os dois últimos `subprocess.run` gravam em `SAIDA / "historia-960.mp4"` e `SAIDA / "historia-960.jpg"`; `print("pronto:", SAIDA / "historia-960.mp4")`; docstring: `Saídas: portfolio/filme/saida/historia-1280.mp4 (mestre) · historia-960.mp4 e historia-960.jpg (trailer de envio, 960×540; fora do site, ignorado pelo git)`. Apagar `WEB.mkdir(...)`.

`README.md` do filme, novo conteúdo:

```markdown
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
```

- [ ] **Step 5: Apagar o trailer do site e ver passar**

Run: `cd /home/runner/workspace && git rm -q portfolio/site/video/historia.mp4 portfolio/site/video/historia.jpg && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3`
Expected: `OK`, `trailer de envio ausente … pulado` + `OK`, e o `--navegador` termina em `OK` (a `checar_ficha_a_vista` verde em 390 e 1280).

- [ ] **Step 6: Commit**

```bash
cd /home/runner/workspace && git add -A portfolio/filme/render.py portfolio/filme/README.md portfolio/site/index.html portfolio/site/video portfolio/tests/check_historia.py portfolio/tests/check_filme.py
git commit -m "O trailer sai da página e vira arquivo de envio (filme/saida/historia-960.mp4); README com \"Como enviar\"

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 10: Os clipes entram na página

**Files:**
- Modify: `portfolio/site/index.html` (11 figures, CSS, crédito, scripts), `portfolio/site/historia.js` (4 linhas + comentários), `portfolio/tests/historia_teste.html`, `portfolio/tests/check_historia.py` (`ROTEIRO`, `LONGAS`, `checar_fundo`, `checar_marcacao`, `checar_css`, `checar_scripts`, `checar_js`, `checar_navegador`, `checar_maquete_real` sai, `checar_nota`, `checar_origem`), `portfolio/DESIGN.md`

**Interfaces:**
- Consumes: `CLIPES` de `render_clipes.py` (Task 3), `clipes.js` (Task 8), os 22 arquivos de `site/video/` (Task 7).
- Produces: `ROTEIRO` com fundos `("clipe", dur)`; `LONGAS = {"casa", "icamento", "zip"}`; `historia.js` lê `f.__clipe` e a classe `clipe`; harness com `?clipes=nao` e `__clipe` falso; `check_historia.py --origem URL`.

- [ ] **Step 1: Testes estáticos**

Em `check_historia.py`:

(a) imports: depois de `ROOT = …`, acrescentar
```python
sys.path.insert(0, str(ROOT / "filme"))
from render_clipes import CLIPES  # noqa: E402  (mapa capítulo → cena → trecho: a fonte da verdade)

LONGAS = {"casa", "icamento", "zip"}  # capítulos de 200 svh (10 s, 10 s e 8 s de clipe, mas com mais a dizer)
```

(b) `ROTEIRO`: trocar os fundos — `origem` `("clipe", 8)` · `obra` `("clipe", 8)` · `veks` `("clipe", 8)` · `ferramentas` `("clipe", 8)` · `sige` `("clipe", 8)` · `escala` `("clipe", 8.5)` · `casa` `("clipe", 10)` · `icamento` `("clipe", 8)` · `whatsapp` `("clipe", 8)` · `recuperado` `("clipe", 8)` · `zip` `("clipe", 10)`; `mudanca` `("ano", "2025")` e `galpoes` `("ano", "22 baias")` ficam; `tese`, `precisao`, `metodo` ficam com `img`; docstring de `cap()`: `("clipe", duração em s)` no lugar de `("maquete", …)`.

(c) `checar_fundo`: a tabela de classes vira `{"img": "fundo", "ano": "fundo tipo", "clipe": "fundo clipe"}`; a linha do `data-cena` vira `check("data-cena" not in fa, …)`; depois do bloco `if tipo == "ano": …return`, para `img` e `clipe`: `check(limpo(fmiolo) == "", f"cena {passo}: nenhum nó de texto dentro da figura (só o .ano dos fundos tipográficos)")`; a variável `arquivo, largura, altura` passa a ser:

```python
    if tipo == "img":
        arquivo, largura, altura, src = fundo[1], fundo[2], fundo[3], f"img/{fundo[1]}"
    else:
        dur = fundo[1]
        arquivo, largura, altura, src = f"cena-{passo}.webp", 960, 540, f"video/cena-{passo}.webp"
        check(fa.get("data-dur") == f"{dur:g}" and fa.get("data-clipe") == f"video/cena-{passo}.mp4",
              f"cena {passo}: figure de clipe com data-dur=\"{dur:g}\" e data-clipe=\"video/cena-{passo}.mp4\"")
        check(CLIPES.get(passo, (0, 0, 0, None))[3] == dur, f"cena {passo}: duração {dur} ≠ CLIPES de render_clipes.py")
        v = re.search(r"<video ([^>]*)></video>", fmiolo)
        check(v is not None and v.group(1) == 'muted playsinline preload="none" disableremoteplayback width="960" height="540"',
              f"cena {passo}: <video muted playsinline preload=\"none\" disableremoteplayback width=\"960\" height=\"540\"></video>, nada mais")
        for proibido in ("<canvas", "<source", "<track", 'class="hud"', "data-relogio", "data-legenda", "title=", "tabindex"):
            check(proibido not in fmiolo, f"cena {passo}: {proibido} não entra na figura de clipe")
        mp4 = SITE / "video" / f"cena-{passo}.mp4"
        if mp4.exists():
            real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(mp4)],
                                        capture_output=True, text=True, check=True).stdout)
            check(abs(real - dur) <= 0.05, f"cena {passo}: data-dur {dur} ≠ duração real {real:.3f} s")
```
e a checagem de `src` da imagem usa `src` (não mais `f"img/{arquivo}"`) e a existência `(SITE / src).exists()`. Apagar o bloco final `if tipo == "maquete": …`.

(d) `checar_marcacao`: `longa = passo in LONGAS` (no lugar de `c["fundo"][0] == "maquete"`), mensagem "a classe 'longa' vai só em casa, icamento e zip"; e depois do laço:

```python
    clipes = {c["passo"]: c["fundo"][1] for c in ROTEIRO if c["fundo"] and c["fundo"][0] == "clipe"}
    check(clipes == {p: v[3] for p, v in CLIPES.items()}, f"ROTEIRO e CLIPES divergem: {clipes} × {CLIPES}")
    check(CLIPES["veks"][2] == CLIPES["ferramentas"][1] and CLIPES["whatsapp"][2] == CLIPES["recuperado"][1] == 3.0,
          "cenas partilhadas: veks.t1 == ferramentas.t0 e whatsapp.t1 == recuperado.t0 == 3,0")
    check(not {4, 5, 8} & {v[0] for v in CLIPES.values()}, "as cenas 36 min do filme (SC4), abertura (SC5) e celeiro (SC8) nunca vão à página")
    check(all(v[1] < v[2] for v in CLIPES.values()), "cada trecho anda para a frente (t0 < t1)")
    for proibido in ("<canvas", 'class="hud"', "data-relogio", "data-legenda", "data-cena", "<track", "<source"):
        check(proibido not in pagina, f"index.html não tem mais {proibido}")
    check(re.search(r"<video [^>]*\bsrc=", pagina) is None, "nenhum <video> com src no HTML (o JS atribui na hora de carregar)")
```

(e) `checar_nota(pagina)`:
```python
NOTA = ('<p class="nota">As cenas ao fundo da história são dioramas em 3D feitos para este portfólio; '
        'as telas e fotos reais estão no portfólio completo.</p>')


def checar_nota(pagina):
    ficha = re.search(r'<section class="ficha"[^>]*>(.*?)</section>', pagina, re.S)
    check(ficha is not None and NOTA in ficha.group(1) and ficha.group(1).index(NOTA) > ficha.group(1).index("faltam 3 · CLT ou PJ"),
          "a linha de crédito dos dioramas fica na ficha, depois de \"Engenharia Civil, 7º semestre…\"")
```

(f) `checar_css`: apagar as três checagens de `.pausa`, `.hud b{…background:var(--scrim)`, `.hud b:empty`; acrescentar:

```python
    check(".fundo video{display:none}" in css, "modo empilhado: o vídeo não existe, fica a imagem")
    pv = re.search(r"\.js-historia \.palco \.fundo video\{([^}]*)\}", css)
    check(pv is not None and all(x in pv.group(1) for x in ("display:block", "object-fit:cover", "object-position:68% 50%", "opacity:0", "transition:opacity .4s")),
          "modo cenas: o vídeo cobre o palco (object-fit:cover; object-position:68% 50%), começa invisível e aparece em .4s")
    check(re.search(r"video[^{}]*\{[^}]*filter", css) is None, "sem filter em seletor com video (a paleta do filme fica como está)")
    check(".js-historia .palco .fundo.viva video{opacity:1}" in css and ".js-historia .palco .fundo.viva img{visibility:hidden}" in css,
          "a imagem só some (.viva) quando há quadro pronto")
    check(re.search(r"\.js-historia \.palco \.fundo img\{[^}]*filter:brightness\(\.6\) saturate\(\.85\)", css) is not None,
          "as fotos dos capítulos sem clipe mantêm brightness(.6) saturate(.85)")
    reduzido = bloco_css(css, "@media (prefers-reduced-motion: reduce){")
    check(".js-historia .palco .fundo video{display:none}" in reduzido and ".js-historia .palco .fundo.viva img{visibility:visible}" in reduzido,
          "movimento reduzido em tempo real: o CSS esconde o vídeo e mostra a imagem sem JS")
    larga = bloco_css(css, "@media (min-width:900px) and (orientation:landscape){")
    check(".js-historia .cena{justify-content:flex-start}" in larga and ".js-historia .texto{max-width:min(620px,48vw);margin-left:max(24px,6vw);text-align:left}" in larga,
          "tela larga: a faixa de texto vai para a esquerda, como no filme")
    for sumido in (".hud", ".pausa", "canvas"):
        check(sumido not in css, f"CSS sem {sumido}")
    check("#E0622A" in (ROOT / "DESIGN.md").read_text(encoding="utf-8"), "DESIGN.md: a paleta dos clipes (#EFE6D6 / #1B1714 / #E0622A) fica registrada")
```
com o utilitário:
```python
def bloco_css(css, inicio):
    """Conteúdo de um bloco @media, contando chaves."""
    i = css.find(inicio)
    if i < 0:
        return ""
    j, n = i + len(inicio), 1
    while j < len(css) and n:
        n += {"{": 1, "}": -1}.get(css[j], 0)
        j += 1
    return css[i + len(inicio):j - 1]
```
Na mensagem do `--relogio`, trocar "relógio da maquete" por "`--relogio` (o .ano dos fundos tipográficos)".

(g) `checar_scripts`: `nomes == ["clipes.js", "historia.js"]`, mensagem "scripts devem ser clipes.js e historia.js, nessa ordem".

(h) `checar_js`: acrescentar `"__maquete"` e `"'maquete'"` à lista de proibidos; manter o resto. `checar_maquetes_js()` fica (o arquivo não muda).

(i) `checar_navegador`: `maquetes = …` vira `clipes = [c["passo"] for c in ROTEIRO if c["fundo"] and c["fundo"][0] == "clipe"]`; nas strings esperadas, `maquetes=` → `clipes=` (em `salto ativa=tese clipes=-`, `cena {passo} … clipes={maq}`), `maq = passo if passo in clipes else "-"`, `if passo in clipes:` (imagem visível e seeks). Apagar `checar_maquete_real()` inteiro e a chamada.

(j) `--origem`:
```python
def checar_origem(url):
    """Na origem publicada, cada clipe tem de responder 206 a um Range (sem isso a página cai no pôster, por construção)."""
    for passo in CLIPES:
        req = urllib.request.Request(f"{url.rstrip('/')}/video/cena-{passo}.mp4", headers={"Range": "bytes=0-99"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                check(r.status == 206 and "Content-Range" in r.headers, f"{url}: cena-{passo}.mp4 respondeu {r.status} a Range (esperava 206)")
        except OSError as e:
            check(False, f"{url}: cena-{passo}.mp4 não respondeu ({e})")
```
Em `main()`: `if "--origem" in sys.argv: checar_origem(sys.argv[sys.argv.index("--origem") + 1])`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py 2>&1 | head -30`
Expected: `FALHOU:` com, entre outras, `cena origem: classe da figura 'fundo tipo', esperava 'fundo clipe'`, `cena casa: … 'fundo maquete'`, `index.html não tem mais <canvas`, `scripts devem ser clipes.js e historia.js`, `modo empilhado: o vídeo não existe`, `a linha de crédito dos dioramas`, `DESIGN.md: a paleta dos clipes`.

- [ ] **Step 3: `index.html` — as figures**

Trocar cada uma destas 11 linhas/blocos pela figure de clipe correspondente (o modelo, com `X` = passo e `D` = duração):

```html
    <figure class="fundo clipe" data-passo="X" data-dur="D" data-clipe="video/cena-X.mp4" aria-hidden="true">
      <video muted playsinline preload="none" disableremoteplayback width="960" height="540"></video>
      <img src="video/cena-X.webp" alt="" width="960" height="540" loading="lazy">
    </figure>
```

| passo | linha atual (começo) | D |
|---|---|---|
| origem | `<figure class="fundo tipo" data-passo="origem" …><span class="ano">2017</span></figure>` | 8 |
| obra | `<figure class="fundo tipo" data-passo="obra" …><span class="ano">5×</span></figure>` | 8 |
| veks | `<figure class="fundo tipo" data-passo="veks" …><span class="ano">2026</span></figure>` | 8 |
| ferramentas | `<figure class="fundo tipo" data-passo="ferramentas" …><span class="ano">3ª</span></figure>` | 8 |
| sige | `<figure class="fundo" data-passo="sige" …><img src="img/c-aprovacao.webp" …></figure>` | 8 |
| escala | `<figure class="fundo" data-passo="escala" …><img src="img/s1.webp" …></figure>` | 8.5 |
| casa | o bloco `<figure class="fundo maquete" data-passo="casa" data-cena="casa-viaja" …>` … `</figure>` (4 linhas) | 10 |
| icamento | idem, `data-cena="icamento"` | 8 |
| whatsapp | `<figure class="fundo" data-passo="whatsapp" …><img src="img/p-fotos.webp" …></figure>` | 8 |
| recuperado | `<figure class="fundo" data-passo="recuperado" …><img src="img/p-diario-portal.webp" …></figure>` | 8 |
| zip | o bloco `<figure class="fundo maquete" data-passo="zip" data-cena="36min" …>` … `</figure>` (4 linhas) | 10 |

`mudanca` ("2025") e `galpoes` ("22 baias") ficam como estão. As seções `casa`, `icamento` e `zip` continuam `class="cena longa"`.

- [ ] **Step 4: `index.html` — CSS, crédito, scripts**

No CSS do modo empilhado, trocar `.fundo canvas,.fundo .hud{display:none}` e `.fundo .pausa{display:none!important}` por:
```css
.fundo video{display:none}
```
No CSS do modo cenas, trocar as 6 regras de `.js-historia .palco .fundo canvas{…}` até `.js-historia .palco .hud [data-legenda]{display:none}` por:
```css
/* o clipe cobre o palco sem filtro (paleta do filme); a imagem (pôster = último quadro) só some quando há quadro pronto (.viva) */
.js-historia .palco .fundo video{display:block;position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:68% 50%;opacity:0;transition:opacity .4s}
.js-historia .palco .fundo.viva video{opacity:1}
.js-historia .palco .fundo.viva img{visibility:hidden}
```
Trocar a última regra `@media (prefers-reduced-motion: reduce){.js-historia .palco .fundo,.js-historia .palco .fundo canvas{transition:none}}` por:
```css
/* movimento reduzido ligado no meio da história: o CSS esconde o vídeo e mostra a imagem na hora, sem JS; clipes.js descarrega */
@media (prefers-reduced-motion: reduce){.js-historia .palco .fundo,.js-historia .palco .fundo video{transition:none}.js-historia .palco .fundo video{display:none}.js-historia .palco .fundo.viva img{visibility:visible}}
/* tela larga: a faixa de texto à esquerda, como no filme; o assunto do clipe fica a ~68 % da largura */
@media (min-width:900px) and (orientation:landscape){.js-historia .cena{justify-content:flex-start}.js-historia .texto{max-width:min(620px,48vw);margin-left:max(24px,6vw);text-align:left}.js-historia .frase{margin:0}.js-historia .ressalva{margin-left:0}.js-historia .cta{justify-content:flex-start}}
```
Estilo do crédito, depois de `.ficha p{…}`: `.ficha .nota{font-family:var(--mono);font-size:.78rem;color:var(--muted)}`. Na `.ficha`, depois de `<p>Engenharia Civil, 7º semestre, faltam 3 · CLT ou PJ · …</p>`, a linha `<p class="nota">As cenas ao fundo da história são dioramas em 3D feitos para este portfólio; as telas e fotos reais estão no portfólio completo.</p>`. Scripts: `<script src="clipes.js" defer></script>` no lugar de `maquetes.js`. Comentários do CSS que citam maquete/canvas: `/* modo cenas: historia.js liga .js-historia no <html> e leva cada .fundo para o .palco */` fica; `.js-historia .palco .fundo.tipo` fica.

`DESIGN.md`, na seção "## 2. Paleta de cores e papéis", linha nova no fim da lista: `- **Clipes da história** (fundo dos capítulos em `index.html`): papel `#EFE6D6`, tinta `#1B1714`, laranja `#E0622A` — a paleta do filme, tone-mapped (ACES), sem filtro por cima; o contraste do texto vem só da faixa `--scrim`.`

- [ ] **Step 5: `historia.js` e o harness**

`historia.js`: linha 2 do comentário: `nas cenas de clipe, o tempo do vídeo é o progresso do scroll dentro da cena`; linha 28: `// cada fundo vai para o palco fixo; o clipe fica hidden fora da sua cena`; linha 35: `if(f.classList.contains('clipe'))f.hidden=true;`; linha 40: `// clipe da cena ativa: o tempo do vídeo segue o scroll (seek congela o tempo), nunca anda sozinho`; linha 43: `if(!f||!f.classList.contains('clipe'))return;`; linha 44: `var api=f.__clipe;`; linha 45 (comentário): `// clipes.js ainda não rodou: um só temporizador…`; linha 79: `if(antes.classList.contains('clipe'))esconderDepois(H.ativa);`; linha 85 (comentário): `// o clipe volta a ser exibido antes da opacidade`. Nada mais muda.

`historia_teste.html`: `src="../site/index.html?clipes=nao"`; `function clipesVisiveis(d){return [].filter.call(d.querySelectorAll('.palco .clipe'),…` ; `function tempo(m){var t=m.__clipe&&m.__clipe.t;…`; comentário e instalação: `// clipe falso: com ?clipes=nao o clipes.js não carrega vídeo; o harness responde a seek() e guarda t` e `[].forEach.call(d.querySelectorAll('figure.clipe'),function(m){m.__clipe={dur:1000,t:null,seek:function(x){this.t=x;}};});`; `' clipes='+clipesVisiveis(d)` nas duas linhas de log; `figure.clipe[data-passo="'+p+'"]`; `figure.clipe[data-passo="zip"]`; `delete mz.__clipe;`; `mz.__clipe={dur:1000,…}`.

- [ ] **Step 6: Ver passar (estático, harness e ficha)**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -5`
Expected: `OK` três vezes. No harness (`--navegador`): `cena casa ativa=casa fundo=casa clipes=casa`, `img casa=visible`, `seek casa≈500`, `seek25≈250` para os 11 clipes; reduzido com `js-historia=false`, `palco-filhos=0`, `frases-visiveis=17`.

- [ ] **Step 7: Olhar a página**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad && mkdir -p $S && python3 - <<'EOF'
import sys, time, base64
sys.path.insert(0, 'portfolio/tests'); import check_historia as ch
S='/tmp/claude-1000/-home-runner-workspace/4379c55d-69af-4640-a6b2-4dcfb39ddfc0/scratchpad'; import os; os.makedirs(S, exist_ok=True)
for largura, altura, passo, nome in ((390, 844, 'icamento', 'fone'), (1366, 768, 'zip', 'larga')):
    with ch.chromium(largura, ("--enable-unsafe-swiftshader",), altura=altura) as ws:
        ws.comando("Page.navigate", url=f"http://127.0.0.1:{ch.PORTA}/site/index.html"); time.sleep(2.5)
        ws.avaliar(f"(function(){{var r=document.getElementById('{passo}').getBoundingClientRect();window.scrollTo(0,scrollY+r.top+r.height*.5-innerHeight/2);}})()")
        time.sleep(6)
        open(f"{S}/pagina-{nome}.png","wb").write(base64.b64decode(ws.comando("Page.captureScreenshot", format="png")["data"]))
EOF
```

Abrir `pagina-fone.png` e `pagina-larga.png`. Expected: no celular, o módulo do içamento no ar ao fundo (recorte central-direito do 16:9), faixa de texto centrada e legível, sem tira em branco; na tela larga, a planta dos 36 min ao fundo com o assunto à direita e a faixa de texto à esquerda, terminando antes da metade da tela.

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/index.html portfolio/site/historia.js portfolio/tests/historia_teste.html portfolio/tests/check_historia.py portfolio/DESIGN.md
git commit -m "História: os 11 clipes de fundo avançam com a rolagem (clipes.js + historia.js); sem WebGL; faixa à esquerda em tela larga; crédito dos dioramas

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 11: Os clipes no navegador de verdade (F-08, F-09, F-10, F-11, F-13, F-17)

**Files:**
- Modify: `portfolio/tests/check_historia.py` (docstring; `ESPIAO`, `TROCA_404`, `LER_CLIPES`, `ler_clipes`, `ler_clipe`, `esperar`, `navegar`, `rolar_ate`, `quadro`; `checar_clipe_real`, `checar_reduzido_real`, `checar_dados`, `checar_foco`, `checar_layout`, `checar_desempenho`; `main()`)

**Interfaces:**
- Consumes: `chromium(largura, extra=(), altura=800, com_range=True)`, `servidor()`, `medir_desempenho(ws)`, `BASELINE` (Task 1); `CLIPES`, `LONGAS`, `ROTEIRO` com fundos `("clipe", dur)` (Task 10); `clipes.js` com `fig.__clipe = {dur, frozen, seek, descarregar}`, a classe `.viva` e `MAXIMO=2` (Task 8); a marcação e o CSS da Task 10 (`figure.clipe`, `.texto`, `a.pular`, `#historia`).
- Produces: `check_historia.py --navegador` roda, depois do harness e da ficha, as seis checagens reais. Nada novo para outras tarefas.

**Medido antes de escrever esta tarefa (Chromium 152 headless, servidor com Range, clipe 960×540 a 24 fps com GOP 4):** cada `seeked` chega em 5–16 ms (mediana 8,8 ms); 30 seeks um por rAF → 30 `seeked`, intervalo mediano ≈ 16 ms (limitado pelo rAF); depois de `removeAttribute('src')`+`load()`, `readyState` 0 e `networkState` 3; **sem Range**, `loadedmetadata` vem com `seekable` = `[0,0]` (e assim fica), e um seek dispara `seeked` com `currentTime` 0 — o clipe fica preso no primeiro quadro em silêncio; o `<video>` aparece em `performance.getEntriesByType('resource')` com `initiatorType` `video`; um `MutationObserver` registrado por `Page.addScriptToEvaluateOnNewDocument` vê a figure **antes** de os scripts `defer` rodarem; `Object.defineProperty(navigator,'connection',{value:…})` vale para a página; `Input.dispatchKeyEvent` Tab (`keyDown`+`keyUp`, `windowsVirtualKeyCode` 9) percorre barra e régua; `Emulation.setEmulatedMedia` dispara o `change` do `matchMedia` (reduce → `true`, no-preference → `false`); `loadEventStart` da entrada `navigation` e o `startTime` das imagens `lazy` (que vêm depois) permitem dizer "nada baixou antes do load"; **na página de hoje** (390×800) o LCP é o `H1` (a foto entra com opacidade 0 e transição) e o CLS de uma rolagem completa é 9×10⁻⁵ (o marco da régua muda de 2 px para 12 px a cada capítulo).

**Rulings (a spec é a autoridade; onde ela pede um número que a página de hoje já não dá, o teste mede o que a persona queria):**
- F-08 "em `scrollY=0` após o `load`, zero `.mp4`": com `rootMargin:'600px 0px'`, o capítulo 2 (`origem`) começa exatamente na borda inferior da tela e carrega logo depois do `load`, por construção. O que P4-15 e P5-09 querem é que nenhum clipe compita com o LCP: **toda requisição `.mp4` começa depois de `loadEventStart`** e, parado em `scrollY=0`, há no máximo 2 vídeos com dados. Custo se errado: um clipe (≤ 0,9 MB) baixando na primeira tela depois do load.
- F-17 "LCP continua `o-quantitativos.webp`": em headless o LCP de hoje já é o `H1`. Teste como a P5-12 escreveu: **LCP ∈ {IMG `o-quantitativos.webp`, H1}**, nunca `VIDEO`. Custo se errado: nenhum — o que não pode acontecer é o vídeo virar LCP.
- F-17 "CLS = 0": a página de hoje já mede 9×10⁻⁵ pelo marco da régua. **CLS ≤ 0,01** (a troca pôster→vídeo e a carga dos clipes não podem somar nada visível; 0,1 é o limite "bom" do Google). Custo se errado: um deslocamento de até 1 % da tela passaria.
- F-08 "30 seeks um por rAF → ≥ 20 `seeked`, mediana ≤ 40 ms": mede-se o **intervalo entre `seeked` consecutivos** (um seek em voo por vez: com pedido pendente, o intervalo é a latência do seek). Medido hoje: 30/30 e ≈ 16 ms.
- Review Focus 1 (clipe em 404): o `clipes.js` lê `data-clipe` na hora de criar a API, então a troca tem de acontecer antes de ele rodar — `MutationObserver` injetado antes da navegação (medido: chega antes). Se um dia chegar tarde (`__troca === 'tarde'`), a alternativa é `Network.enable` + `Network.setBlockedURLs(urls=['*cena-whatsapp.mp4'])` antes de navegar.

- [ ] **Step 1: Escrever as checagens reais**

Em `check_historia.py`, docstring do módulo, trocar a frase do `--navegador` por: `Com --navegador: o Chromium headless abre tests/historia_teste.html em tempo real e confere a troca de cenas; depois, com os clipes de verdade e o servidor com Range, a carga sob demanda, o seek pela rolagem, o 404, movimento reduzido ligado no meio, economia de dados, foco, composição e desempenho.`

Depois de `checar_ficha_a_vista()` (e antes de `main()`):

```python
# ---------- clipes de verdade (F-08, F-09, F-10, F-11, F-13, F-17): espiões injetados antes da navegação e leituras da página ----------
ESPIAO = (
    "window.__plays=0;window.__erros=[];window.__lcp='';window.__cls=0;"
    "var _play=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){window.__plays++;return _play.apply(this,arguments);};"
    "addEventListener('error',function(e){__erros.push(String(e.message));});"
    "addEventListener('unhandledrejection',function(e){__erros.push('promise: '+String(e.reason));});"
    "var _ce=console.error;console.error=function(){__erros.push(String(arguments[0]));return _ce.apply(console,arguments);};"
    "new PerformanceObserver(function(l){l.getEntries().forEach(function(e){__lcp=(e.element&&e.element.tagName||'?')+' '+(e.url||'');});})"
    ".observe({type:'largest-contentful-paint',buffered:true});"
    "new PerformanceObserver(function(l){l.getEntries().forEach(function(e){if(!e.hadRecentInput)__cls+=e.value;});})"
    ".observe({type:'layout-shift',buffered:true});")
# troca o clipe do whatsapp por um arquivo que não existe (404) antes de o clipes.js rodar: o leitor tem de ver o pôster
TROCA_404 = ("window.__troca='tarde';new MutationObserver(function(ms,o){var f=document.querySelector('figure.clipe[data-passo=\"whatsapp\"]');"
             "if(f){f.dataset.clipe='video/nao-existe.mp4';window.__troca=window.Historia?'tarde':'antes';o.disconnect();}})"
             ".observe(document,{childList:true,subtree:true});")
LER_CLIPES = (
    "JSON.stringify((function(){var figs=[].slice.call(document.querySelectorAll('figure.clipe'));"
    "var res=performance.getEntriesByType('resource'),nav=performance.getEntriesByType('navigation')[0];"
    "var mp4=res.filter(function(e){return /\\.mp4/.test(e.name);});"
    "function passos(f){return f.map(function(x){return x.dataset.passo;});}"
    "return {mp4:mp4.length,mp4AntesDoLoad:mp4.filter(function(e){return e.startTime<nav.loadEventStart;}).length,"
    "three:res.filter(function(e){return /three/i.test(e.name);}).length,"
    "comDados:passos(figs.filter(function(f){return f.querySelector('video').readyState>0;})),"
    "comSrc:passos(figs.filter(function(f){return f.querySelector('video').hasAttribute('src');})),"
    "vivas:passos(figs.filter(function(f){return f.classList.contains('viva');})),"
    "pausados:figs.every(function(f){return f.querySelector('video').paused;}),plays:window.__plays||0,erros:window.__erros||[],"
    "ativa:(window.Historia||{}).ativa,jsHistoria:document.documentElement.classList.contains('js-historia')};})())")


def ler_clipes(ws):
    """Resumo dos clipes da página: requisições .mp4 (e se alguma veio antes do load), vídeos com dados/src, .viva, play(), erros."""
    return json.loads(ws.avaliar(LER_CLIPES))


def ler_clipe(ws, passo):
    """Estado de uma figure de clipe: .viva, API, readyState, seekable, currentTime, visibilidade da imagem e do vídeo."""
    return json.loads(ws.avaliar(
        "JSON.stringify((function(p){var f=document.querySelector('figure.clipe[data-passo=\"'+p+'\"]'),v=f.querySelector('video'),a=f.__clipe;"
        "return {viva:f.classList.contains('viva'),frozen:!!a&&a.frozen===true,dur:a?a.dur:null,ready:v.readyState,"
        "seekEnd:v.seekable.length?v.seekable.end(0):-1,t:v.currentTime,img:getComputedStyle(f.querySelector('img')).visibility,"
        "video:getComputedStyle(v).display,opacidade:getComputedStyle(v).opacity,src:v.getAttribute('src'),paused:v.paused};})("
        + json.dumps(passo) + "))"))


def esperar(ws, expressao, prazo):
    """Avalia `expressao` a cada 0,25 s até dar verdadeiro ou o prazo (s) acabar; devolve o último valor."""
    fim = time.time() + prazo
    while True:
        valor = ws.avaliar(expressao)
        if valor or time.time() >= fim:
            return valor
        time.sleep(0.25)


def navegar(ws, caminho="site/index.html"):
    """Abre a página e espera o load da janela (o clipes.js só carrega depois dele) e o historia.js."""
    ws.comando("Page.navigate", url=f"http://127.0.0.1:{PORTA}/{caminho}")
    check(esperar(ws, "document.readyState==='complete'&&!!window.Historia", 15), f"{caminho}: a página não carregou em 15 s")
    time.sleep(0.5)


def rolar_ate(ws, passo, fracao):
    """Rola até o progresso `fracao` da cena (0: o topo cruza o meio da tela; 1: o fim cruza) — o mesmo progresso() do historia.js."""
    ws.avaliar(f"(function(){{var r=document.getElementById('{passo}').getBoundingClientRect();"
               f"window.scrollTo(0,scrollY+r.top+r.height*{fracao}-innerHeight/2);}})()")


def quadro(t):
    """O quantizador do clipes.js: o meio do quadro mais próximo, a 24 fps (Math.round, para t ≥ 0)."""
    return (int(t * 24 + 0.5) + 0.5) / 24


VIDEO_ICAMENTO = "document.querySelector('figure.clipe[data-passo=\"icamento\"] video')"


def checar_clipe_real():
    """Servidor com Range e clipes de verdade (F-08): nada baixa antes do load; a 40 % do içamento o clipe carrega, busca o
    quadro do progresso e só então a imagem some; seeks a cada rAF chegam; nunca play(); no máximo 2 vídeos com dados numa
    rolagem rápida; 404 e ?clipes=nao ficam no pôster; sem Range, nenhuma .viva e nenhum erro."""
    dur = CLIPES["icamento"][3]
    with chromium(390, altura=844) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO + TROCA_404)
        navegar(ws)
        time.sleep(1)
        e = ler_clipes(ws)
        check(e["jsHistoria"] and e["ativa"] == "tese", f"modo cenas na tese (js-historia={e['jsHistoria']}, ativa={e['ativa']})")
        check(e["mp4AntesDoLoad"] == 0 and e["three"] == 0,
              f"nenhum .mp4 antes do load nem three.js ({e['mp4AntesDoLoad']} mp4 antes do load, {e['three']} three)")
        check(len(e["comDados"]) <= 2, f"em scrollY=0, no máximo 2 vídeos com dados (achei {e['comDados']})")
        check(ws.avaliar("window.__troca") == "antes", "o espião do 404 precisa trocar data-clipe antes de o clipes.js rodar")
        # 40 % do içamento: carrega, busca o quadro do progresso e mostra o vídeo
        rolar_ate(ws, "icamento", 0.4)
        pronto = esperar(ws, "(function(){var f=document.querySelector('figure.clipe[data-passo=\"icamento\"]');"
                             "return f.classList.contains('viva')&&!!f.__clipe&&f.__clipe.frozen===true;})()", 25)
        time.sleep(0.6)  # a transição de opacidade do vídeo dura .4 s
        c = ler_clipe(ws, "icamento")
        check(pronto, f"a 40 % do içamento, .viva e __clipe.frozen em ≤ 25 s (estado: {c})")
        check(c["ready"] >= 2 and c["seekEnd"] >= dur - 0.5, f"içamento: readyState {c['ready']} (≥ 2) e seekable até {c['seekEnd']} (≥ {dur - 0.5})")
        check(abs(c["t"] - quadro(0.4 * dur)) <= 0.15, f"içamento a 40 %: currentTime {c['t']:.3f} ≠ quadro(0,4·{dur}) = {quadro(0.4 * dur):.3f}")
        check(c["img"] == "hidden" and c["opacidade"] == "1",
              f"com quadro pronto, a imagem some e o vídeo aparece (img {c['img']}, opacity {c['opacidade']})")
        rolar_ate(ws, "icamento", 0.75)
        alvo = quadro(0.75 * dur)
        esperar(ws, f"Math.abs({VIDEO_ICAMENTO}.currentTime-{alvo})<=0.15", 3)
        c = ler_clipe(ws, "icamento")
        check(abs(c["t"] - alvo) <= 0.15, f"içamento a 75 %: currentTime {c['t']:.3f} ≠ {alvo:.3f}")
        # 30 seeks, um por rAF: intervalo entre seeked consecutivos (um seek em voo por vez; com pedido pendente, é a latência)
        ws.avaliar("window.__medida=null;(function(){var f=document.querySelector('figure.clipe[data-passo=\"icamento\"]'),v=f.querySelector('video'),"
                   "a=f.__clipe,ini=performance.now(),n=0,lat=[];function s(){var t=performance.now();lat.push(t-ini);ini=t;}v.addEventListener('seeked',s);"
                   "(function passo(){if(n>=30){setTimeout(function(){v.removeEventListener('seeked',s);lat.sort(function(x,y){return x-y;});"
                   "window.__medida={n:lat.length,mediana:lat.length?lat[lat.length>>1]:-1,t:v.currentTime};},700);return;}"
                   "a.seek(1+n*0.2);n++;requestAnimationFrame(passo);})();})()")
        m = json.loads(esperar(ws, "JSON.stringify(window.__medida)", 10) or "null") or {}
        check(m.get("n", 0) >= 20 and 0 <= m.get("mediana", -1) <= 40,
              f"30 seeks um por rAF: {m.get('n')} seeked (≥ 20), mediana {m.get('mediana')} ms (≤ 40) — GOP curto e seek por currentTime")
        check(abs(m.get("t", -1) - quadro(1 + 29 * 0.2)) <= 0.15, f"o último pedido vence: currentTime {m.get('t')} ≠ {quadro(1 + 29 * 0.2):.3f}")
        t1 = ws.avaliar(VIDEO_ICAMENTO + ".currentTime")
        time.sleep(2)
        t2 = ws.avaliar(VIDEO_ICAMENTO + ".currentTime")
        check(t1 == t2, f"parado 2 s, o clipe não anda sozinho ({t1} → {t2})")
        e = ler_clipes(ws)
        check(e["plays"] == 0 and e["pausados"], f"play() nunca é chamado ({e['plays']}) e todo vídeo fica pausado ({e['pausados']})")
        # rolagem rápida por três capítulos de clipe seguidos: nunca mais de 2 vídeos com dados
        for passo in ("veks", "ferramentas", "sige", "whatsapp", "recuperado", "zip"):
            rolar_ate(ws, passo, 0.5)
            time.sleep(0.35)
            e = ler_clipes(ws)
            check(len(e["comDados"]) <= 2, f"parada em {passo}: {e['comDados']} vídeos com dados (máx. 2)")
        # 404: o clipe do whatsapp não existe no servidor — pôster, sem .viva, sem src, sem erro não tratado
        rolar_ate(ws, "whatsapp", 0.5)
        time.sleep(3)
        c, e = ler_clipe(ws, "whatsapp"), ler_clipes(ws)
        check(not c["viva"] and c["img"] == "visible" and c["src"] is None and c["ready"] == 0,
              f"clipe inexistente (404): fica o pôster, sem .viva e sem src (estado: {c})")
        check(e["erros"] == [], f"console limpo com um clipe em 404: {e['erros']}")
        # ?clipes=nao na mesma página: nenhum vídeo, pôster visível, API presente (o historia.js continua chamando seek)
        navegar(ws, "site/index.html?clipes=nao")
        rolar_ate(ws, "icamento", 0.4)
        time.sleep(3)
        c, e = ler_clipe(ws, "icamento"), ler_clipes(ws)
        check(e["mp4"] == 0 and e["comSrc"] == [] and e["jsHistoria"],
              f"?clipes=nao: zero .mp4 e modo cenas (achei {e['mp4']} mp4, src em {e['comSrc']}, js-historia={e['jsHistoria']})")
        check(c["img"] == "visible" and not c["viva"] and c["dur"] == dur and c["frozen"], f"?clipes=nao: pôster visível e API com dur={dur} (estado: {c})")
    # origem publicada sem Range (o http.server puro): a página não pode quebrar — pôster e texto, console limpo
    with chromium(390, altura=844, com_range=False) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        time.sleep(5)  # tempo de sobra para metadados → seekable [0,0] → congelar() → descarregar()
        c, e = ler_clipe(ws, "icamento"), ler_clipes(ws)
        check(e["vivas"] == [] and c["img"] == "visible" and c["src"] is None and c["ready"] == 0,
              f"servidor sem Range: nenhuma .viva, pôster visível, vídeo descarregado (estado: {c}, vivas {e['vivas']})")
        check(e["erros"] == [], f"servidor sem Range: console limpo ({e['erros']})")


def checar_reduzido_real():
    """Movimento reduzido (F-09): na carga, empilhado, nenhum clipe e o vídeo sem display; ligado no meio da história, todo
    vídeo descarrega em ≤ 1 s e o pôster volta pelo CSS; nada novo baixa; ao desligar, o clipe ativo recarrega em ≤ 2 s."""
    with chromium(390, ("--force-prefers-reduced-motion",), altura=844) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        time.sleep(3)
        c, e = ler_clipe(ws, "icamento"), ler_clipes(ws)
        check(not e["jsHistoria"] and e["mp4"] == 0 and c["video"] == "none" and c["img"] == "visible",
              f"movimento reduzido na carga: empilhado, zero .mp4, vídeo display:none (js-historia={e['jsHistoria']}, mp4={e['mp4']}, video={c['video']}, img={c['img']})")
    with chromium(390, altura=844) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        check(esperar(ws, "document.querySelector('figure.clipe[data-passo=\"icamento\"]').classList.contains('viva')", 25),
              "içamento .viva antes de ligar o movimento reduzido")
        ws.comando("Emulation.setEmulatedMedia", features=[{"name": "prefers-reduced-motion", "value": "reduce"}])
        descarregou = esperar(ws, "[].every.call(document.querySelectorAll('figure.clipe video'),function(v){return !v.hasAttribute('src')&&v.readyState===0;})", 1)
        c = ler_clipe(ws, "icamento")
        check(descarregou, f"movimento reduzido ligado no meio: todo vídeo sem src e readyState 0 em ≤ 1 s (içamento: {c})")
        check(c["video"] == "none" and c["img"] == "visible",
              f"movimento reduzido ligado no meio: o CSS esconde o vídeo e mostra a imagem (video {c['video']}, img {c['img']})")
        antes = ler_clipes(ws)["mp4"]
        rolar_ate(ws, "zip", 0.4)
        time.sleep(1)
        rolar_ate(ws, "casa", 0.4)
        time.sleep(1)
        e = ler_clipes(ws)
        check(e["mp4"] == antes and e["comSrc"] == [],
              f"com movimento reduzido ligado, nenhum clipe novo baixa em 2 s de rolagem ({antes} → {e['mp4']}, src em {e['comSrc']})")
        ws.comando("Emulation.setEmulatedMedia", features=[{"name": "prefers-reduced-motion", "value": "no-preference"}])
        voltou = esperar(ws, "document.querySelector('figure.clipe[data-passo=\"casa\"] video').readyState>=1", 2)
        check(voltou and ler_clipes(ws)["ativa"] == "casa", "ao desligar o movimento reduzido, o clipe ativo (casa) recarrega em ≤ 2 s")


def checar_dados():
    """Economia de dados e rede lenta (F-10): o modo cenas fica, mas nenhum clipe baixa; em 3g baixa."""
    for conexao, baixa in (("{saveData:true,effectiveType:'4g'}", False), ("{saveData:false,effectiveType:'2g'}", False),
                           ("{saveData:false,effectiveType:'3g'}", True)):
        with chromium(390, altura=844) as ws:
            ws.comando("Page.enable")
            ws.comando("Page.addScriptToEvaluateOnNewDocument",
                       source=ESPIAO + f"Object.defineProperty(navigator,'connection',{{value:{conexao},configurable:true}});")
            navegar(ws)
            rolar_ate(ws, "icamento", 0.4)
            if baixa:
                esperar(ws, "performance.getEntriesByType('resource').some(function(e){return /\\.mp4/.test(e.name);})", 10)
            else:
                time.sleep(3)
            c, e = ler_clipe(ws, "icamento"), ler_clipes(ws)
            check(e["jsHistoria"], f"navigator.connection={conexao}: o modo cenas continua")
            check((e["mp4"] > 0) == baixa, f"navigator.connection={conexao}: esperava {'algum' if baixa else 'nenhum'} .mp4, achei {e['mp4']}")
            if not baixa:
                check(c["img"] == "visible" and not c["viva"], f"navigator.connection={conexao}: fica o pôster (estado: {c})")


def checar_foco():
    """Tab a partir de "Pular para o texto", 60 vezes (F-11): o foco nunca entra no palco nem num <video>, mesmo com clipe carregado."""
    with chromium(390, altura=844) as ws:
        navegar(ws)
        rolar_ate(ws, "icamento", 0.4)
        esperar(ws, "document.querySelector('figure.clipe[data-passo=\"icamento\"]').classList.contains('viva')", 25)
        ws.avaliar("document.querySelector('a.pular').focus({preventScroll:true})")
        caminho = []
        for _ in range(60):
            for tipo in ("keyDown", "keyUp"):
                ws.comando("Input.dispatchKeyEvent", type=tipo, key="Tab", code="Tab", windowsVirtualKeyCode=9, nativeVirtualKeyCode=9)
            caminho.append(ws.avaliar("(function(){var e=document.activeElement;return (e.closest&&e.closest('.palco')?'PALCO ':'')+e.tagName+"
                                      "(e.classList&&e.classList.length?'.'+e.classList[0]:'')+(e.id?'#'+e.id:'');})()"))
        check(len(set(caminho)) >= 10, f"o Tab do DevTools tem de percorrer a página (foco só em {sorted(set(caminho))})")
        errados = [x for x in caminho if x.startswith("PALCO") or x.startswith("VIDEO")]
        check(not errados, f"o foco entrou no palco ou num vídeo: {errados}")


def checar_layout():
    """Composição (F-13): em tela larga a faixa de texto termina antes de 54 % da largura; no celular a faixa de cada capítulo
    curto deixa clipe à mostra; o comprimento da história (#historia) é o da linha de base."""
    base = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else None
    check(base is not None, "tests/baseline.json não existe (python3 portfolio/tests/check_historia.py --gravar-baseline, antes da mudança)")
    for largura, altura in ((1366, 768), (1920, 1080)):
        with chromium(largura, altura=altura) as ws:
            navegar(ws)
            for passo in ("sige", "zip"):
                rolar_ate(ws, passo, 0.5)
                time.sleep(0.8)
                direita = ws.avaliar(f"document.querySelector('#{passo} .texto').getBoundingClientRect().right/innerWidth")
                check(direita <= 0.54, f"{largura}×{altura}: a faixa de texto de {passo} termina em {direita:.2f} da largura (máx. 0,54)")
    curtos = [c["passo"] for c in ROTEIRO if c["fundo"] and c["fundo"][0] == "clipe" and c["passo"] not in LONGAS]
    with chromium(390, altura=844) as ws:
        navegar(ws)
        for passo in curtos:
            rolar_ate(ws, passo, 0.5)
            time.sleep(0.5)
            r = json.loads(ws.avaliar(f"JSON.stringify((function(){{var r=document.querySelector('#{passo} .texto').getBoundingClientRect();"
                                      f"return {{h:r.height/innerHeight,cima:r.top/innerHeight,baixo:1-r.bottom/innerHeight}};}})())"))
            check(r["h"] <= 0.75, f"390×844: a faixa de {passo} ocupa {r['h']:.0%} da altura (máx. 75 %)")
            check(max(r["cima"], r["baixo"]) >= 0.1, f"390×844: a faixa de {passo} não deixa 10 % de clipe à mostra acima ou abaixo ({r})")
    alturas = {}
    for largura in (390, 1280):
        with chromium(largura) as ws:  # a altura padrão (800) é a da linha de base
            navegar(ws)
            alturas[str(largura)] = ws.avaliar("document.getElementById('historia').offsetHeight")
    if base:
        for largura, altura in alturas.items():
            check(abs(altura - base["alturaMain"][largura]) <= 2, f"{largura} px: #historia mede {altura} px, linha de base {base['alturaMain'][largura]} (± 2)")


def checar_desempenho():
    """Desempenho (F-17): LCP é a foto da tese ou o H1, nunca um vídeo; CLS ≤ 0,01; TaskDuration de uma rolagem completa
    ≤ 2× a linha de base gravada antes da mudança (mesmas flags: a base tinha as maquetes WebGL por SwiftShader)."""
    base = json.loads(BASELINE.read_text(encoding="utf-8")) if BASELINE.exists() else None
    with chromium(390, ("--enable-unsafe-swiftshader",)) as ws:
        ws.comando("Page.enable")
        ws.comando("Page.addScriptToEvaluateOnNewDocument", source=ESPIAO)
        navegar(ws)
        time.sleep(1.5)
        tarefa = medir_desempenho(ws)
        time.sleep(1)
        lcp, cls = ws.avaliar("window.__lcp"), ws.avaliar("window.__cls")
    check(lcp.startswith("H1") or (lcp.startswith("IMG") and lcp.endswith("o-quantitativos.webp")),
          f"o LCP é a foto da tese ou o H1, nunca um vídeo (achei {lcp!r})")
    check(cls <= 0.01, f"CLS da história: {cls} (máx. 0,01)")
    if base:
        check(tarefa <= 2 * base["taskDuration"], f"TaskDuration da rolagem completa: {tarefa:.2f} s, linha de base {base['taskDuration']} s (máx. 2×)")
```

Em `main()`, o bloco do `--navegador` fica:

```python
        if "--navegador" in sys.argv:
            checar_navegador()
            checar_ficha_a_vista()
            checar_clipe_real()
            checar_reduzido_real()
            checar_dados()
            checar_foco()
            checar_layout()
            checar_desempenho()
```

- [ ] **Step 2: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -8`
Expected: `OK` e `OK` (o `--navegador` leva uns 4 minutos: são 14 aberturas do Chromium). Para iterar numa checagem só:
`python3 -c "import sys; sys.path.insert(0,'portfolio/tests'); import check_historia as c; c.checar_clipe_real(); print('\n'.join(c.FALHAS) or 'OK')"`.

Uma falha aqui é defeito no `clipes.js` ou no `index.html` (Tasks 8 e 10), não no teste — corrige-se lá e volta-se a rodar — **salvo** se a mensagem citar o próprio DevTools (`o Tab do DevTools tem de percorrer a página`, `o espião do 404 precisa trocar data-clipe antes`): aí o mecanismo do Chromium mudou e valem as alternativas dos rulings acima (`Network.setBlockedURLs` para o 404; `rawKeyDown` no lugar de `keyDown` para o Tab).

- [ ] **Step 3: Commit**

```bash
cd /home/runner/workspace && git add portfolio/tests/check_historia.py
git commit -m "Testes reais dos clipes: carga depois do load, seek pela rolagem, 404, sem Range, movimento reduzido no meio, economia de dados, foco, composição e desempenho

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task 12: README do portfólio, changelog da rodada 8 e retomada

**Files:**
- Modify: `portfolio/README.md`, `portfolio/revisao/CHANGELOG.md`, `ANDAMENTO.md`, `portfolio/tests/check_historia.py` (`checar_readme`)

**Interfaces:**
- Consumes: tudo o que as Tasks 1–11 entregaram (só descreve).
- Produces: nada para código; o registro de onde a rodada parou.

- [ ] **Step 1: Teste do README (F-16: "o README do portfólio explica")**

Em `check_historia.py`, depois de `checar_maquetes_js()`:

```python
def checar_readme():
    """O README do portfólio explica o servidor com Range e como gerar os clipes (F-16)."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for trecho in ("servir.py", "206", "render_clipes.py", "--origem", "clipes.js"):
        check(trecho in readme, f"README do portfólio sem {trecho!r}")
```

Chamar `checar_readme()` em `main()` logo depois de `checar_maquetes_js()`.

- [ ] **Step 2: Ver falhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py`
Expected: `FALHOU:` com `README do portfólio sem 'servir.py'` (e os outros quatro trechos).

- [ ] **Step 3: `portfolio/README.md`**

No bloco de árvore, trocar a linha `site/` e acrescentar três linhas:

```
site/        site estático: index.html (a história em cenas, página principal; 11 clipes de fundo em video/), portfolio.html (portfólio completo), historia.js, clipes.js, maquetes.js, img/, video/ (cena-*.mp4 + .webp), vendor/ (three.js 0.186), og.png, PDFs
filme/       o filme (film.html + three.js r128): render_clipes.py gera os clipes de fundo; render.py, o trailer de envio (fora do site)
tests/       check_site.py, check_historia.py (--navegador: Chromium headless; --origem URL: Range na origem publicada), check_filme.py (--video), baseline.json
servir.py    servidor estático com Range (HTTP 206): o único em que o vídeo busca pela rolagem
```

Em "## Usar", trocar a linha "Ver o site" por:

```
- Ver o site: `python3 portfolio/servir.py 8000 --directory portfolio/site` → http://localhost:8000
  (precisa de um servidor **com Range**: o `python3 -m http.server` responde 200 sem `Accept-Ranges`, o navegador ignora
  todo seek e a história fica só com os pôsteres; abrir o arquivo direto bloqueia o three.js do portfólio).
- Gerar os clipes de fundo da história: `python3 portfolio/filme/render_clipes.py` (~10 min); conferir: `python3 portfolio/tests/check_filme.py --video`. Detalhes em `filme/README.md`.
```

Em "## Antes de publicar", item novo no fim: `5. Conferir que a origem publicada responde 206 a \`Range\` nos clipes: \`python3 portfolio/tests/check_historia.py --origem https://<domínio>\` (sem 206 a história mostra só os pôsteres — não quebra, mas perde o movimento).`

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py`
Expected: `OK`.

- [ ] **Step 5: Changelog da rodada 8**

Acrescentar ao fim de `portfolio/revisao/CHANGELOG.md`:

```markdown

---

# Rodada 8 — o filme como fundo da história, avançado pela rolagem, 24/09/2026

- Pesquisa das 5 personas (rodada 4) em `docs/superpowers/research/2026-09-23-filme-fundo/`; spec em `docs/superpowers/specs/2026-09-23-filme-fundo-design.md`; plano em `docs/superpowers/plans/2026-09-24-filme-fundo.md`.
- 11 capítulos ganham um clipe curto de vídeo ao fundo (960×540, 24 fps, H.264 com GOP 4, sem texto, ≤ 0,9 MB cada e ≤ 8 MB na soma), cujo tempo é o progresso da rolagem: `site/clipes.js` (seek só por `currentTime`, quantizado ao quadro, um em voo por vez; carga depois do `load` e a 600 px da cena; no máximo 2 vídeos com dados; pôster = último quadro como plano B). `historia.js` só trocou `maquete` por `clipe`.
- As três maquetes three.js da página (casa, içamento, 36 min) foram portadas para o `film.html` no estilo do filme (`SC[9..11]`) e renderizadas como clipes: a história não roda mais WebGL; `maquetes.js` segue só no portfólio completo.
- `film.html`: `?limpo` (só o canvas) e `renderCena(i, t)`; texto pintado corrigido pela regra "nada que o portfólio não sustente" (MESMO DADO, PLANO DE CORTE, EM USO, andares do SIGE iguais ao `.flow`, DESENHO, PLANTA, calendário ≤ 31). `render_clipes.py` gera mestre, versão web e pôster de cada clipe, reencodando até os tetos.
- O trailer saiu da página: `render.py` grava `filme/saida/historia-960.mp4` (fora do site, fora do git); README do filme com "Como enviar" (WhatsApp/LinkedIn).
- Página: sem `filter` no vídeo (paleta do filme); em tela larga a faixa de texto vai para a esquerda; no celular, recorte `68% 50%`; linha de crédito dos dioramas na ficha; comprimento da história inalterado.
- `portfolio/servir.py`: servidor estático com Range (206) no `.replit` e nos testes — sem ele o navegador ignora todo seek.
- Testes: `check_filme.py --video` (texto pintado, cenas portadas, clipes: peso, GOP, pontas paradas, pôster); `check_historia.py --navegador` (marcação e CSS dos clipes; harness; clipe real com Range e sem Range; 404; `?clipes=nao`; movimento reduzido ligado no meio; economia de dados; foco; composição; LCP/CLS/TaskDuration contra `tests/baseline.json`).
- Em aberto: iPhone real (latência de seek, `preload` sem gesto, recorte em retrato → render 9:16 se houver "tiras"); URL do deploy para `--origem`; do Cássio: idade; UNIFEI 2020 ou 2022; estágio/júnior; versão vertical do trailer.
```

- [ ] **Step 6: `ANDAMENTO.md`**

Trocar a linha `Atualizado em 22/09/2026, ~01:40.` por `Atualizado em 24/09/2026.` e acrescentar ao fim do arquivo:

```markdown

## Estado em 24/09/2026 — rodada 8 (o filme como fundo da história) CONCLUÍDA
- Branch `historia-scrollytelling`; spec `docs/superpowers/specs/2026-09-23-filme-fundo-design.md`; plano `docs/superpowers/plans/2026-09-24-filme-fundo.md` (12 tarefas, um commit cada); changelog `portfolio/revisao/CHANGELOG.md`, rodada 8.
- Site no ar: `python3 portfolio/servir.py 5000 --bind 0.0.0.0 --directory portfolio/site` (o Run do `.replit`; precisa de Range).
- Regenerar os clipes: `python3 portfolio/filme/render_clipes.py`; trailer de envio: `python3 portfolio/filme/render.py` → `portfolio/filme/saida/historia-960.mp4`.
- Conferir tudo: `python3 portfolio/tests/check_historia.py --navegador && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_site.py`.
- Próximos passos: merge de `historia-scrollytelling` em `main` e deploy; `check_historia.py --origem <URL>` na origem publicada; testar num iPhone real; pendências do Cássio (idade, UNIFEI, estágio/júnior, trailer vertical).
```

- [ ] **Step 7: Checagem final**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_historia.py --navegador 2>&1 | tail -3 && python3 portfolio/tests/check_filme.py --video && python3 portfolio/tests/check_site.py && git status --short`
Expected: `OK`, `OK`, `OK`; o `git status` mostra só os arquivos desta tarefa (e os untracked de sempre: `film (1).html`, zips).

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add portfolio/README.md portfolio/revisao/CHANGELOG.md ANDAMENTO.md portfolio/tests/check_historia.py
git commit -m "Changelog da rodada 8: o filme como fundo da história; README com o servidor com Range; retomada

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---
