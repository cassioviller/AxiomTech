# Site v2 · Fase 1 (piloto: caso SIGE na obra dos galpões) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer o piloto do site v2: o kit de cenas (three.js 0.186 com oclusão de ambiente, render em 1920×1080), o preparo dos documentos reais e o **caso SIGE na obra dos galpões** completo, numa página nova `portfolio/site/v2.html`. A cena criada leva ao documento real (o portal do cliente com 44,7% concluído), que aparece nítido e com destaque laranja.

**Architecture:**
- Cada cena é um HTML-módulo em `portfolio/cenas/` que usa `kit.js` e expõe `window.renderCena(t)` (t de 0 a 10) e `window.PRONTO`.
- `render.py` serve `portfolio/` com Range numa porta local, abre a cena no Chromium (SwiftShader), captura quadro a quadro e publica o MP4 1920×1080 e o pôster.
- `documentos.py` recorta os prints reais já anonimizados para `site/docs/` e grava as coordenadas do destaque.
- A página reaproveita o `clipes.js` sem mudança e ganha um `v2.js` que traduz a rolagem em três tempos: cena, documento, destaque e texto.

**Tech Stack:** three.js 0.186 (`site/vendor/`, ES module, importmap) + add-ons oficiais vendorizados (EffectComposer, GTAOPass, OutputPass, RoomEnvironment); Python 3 + Playwright 1.63 + Chromium 152 do sistema + ffmpeg/ffprobe + ImageMagick (`magick`); HTML/CSS/JS sem build.

**Spec:** `docs/superpowers/specs/2026-09-25-site-v2-design.md` (aprovado em 25/09). Emenda deste plano (Task 1 a grava no spec): o piloto é o **caso 3 (SIGE na obra dos galpões)**, não o caso 1. O caso 1 tem só prints de 760 px (a regra do spec proíbe ampliar documento) e fica para a fase 2, quando o Cássio mandar os originais.

## Decisões do plano (o spec não fixava; decididas aqui)

1. **Página do piloto em `site/v2.html`**, ao lado do `index.html` do protótipo. A fase 2 a transforma no `index.html`.
2. **Sem tone mapping ACES** (`NoToneMapping`, saída sRGB). Com ACES, a tela do notebook no vídeo teria cores diferentes da imagem real que a substitui, e a passagem do spec §6 ficaria visível. O realismo vem do ambiente (RoomEnvironment), da oclusão (GTAO), de sombras suaves e dos materiais com textura.
3. **Documentos do piloto só de imagens já anonimizadas do site** (`site/img/p-portal.webp`, `p-fotos.webp`, `p-diario-portal.webp`, com nome do cliente e endereço já borrados). O `documentos.py` recusa qualquer outra fonte.
4. **Retângulo de passagem:** `RETANGULO = {x: .2, y: 1/6, w: .6, h: 2/3}` do quadro, ou seja 1152×720 px em 1920×1080, proporção 1,6. A tela do notebook na cena tem 0,32 × 0,20 m (proporção 1,6). O documento principal é o topo do portal recortado em 1600×1000 (proporção 1,6).
5. **O acento laranja da cena SIGE:** os cones que marcam o caminho até o escritório de obra, via `material('acento')`, usado uma única vez no arquivo da cena.

## Global Constraints

- Branch `site-v2`. Um commit por tarefa, com o trailer `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`. Nunca `git add -A`: há um `film (1).html` não rastreado na raiz que não entra.
- Nenhum arquivo do protótipo muda: `site/index.html`, `historia.js`, `maquetes.js`, `portfolio.html`, `filme/`. Exceção: nada.
- `clipes.js` é reaproveitado **sem mudança** (contrato: `figure.clipe[data-clipe][data-dur]` dentro de um ancestral `.cena`; `fig.__clipe.seek(segundos)`; classe `.viva` quando há quadro pronto).
- **Vídeo:** 1920×1080, 24 fps, H.264 High nível 4.0, GOP 4, sem áudio; pontas paradas (0,3 s no início e 0,5 s no fim); teto 2,5 MB por caso.
- **Pôster:** último quadro, WebP com PSNR ≥ 40 dB, ≤ 150 KB.
- **Texto (spec §5):** manchete com ≤ 12 palavras e pelo menos um dígito; linha de apoio com ≤ 30 palavras.
- **Proibidos no texto visível:** metáfora e antítese do protótipo, "27×", "≈ 27", "2 dias úteis", "dois dias úteis", nomes de cliente ("Kabod", "Santa Mônica", "Itu", "UPA", "Bertioga", "203.1809").
- **Textos aprovados do caso:**
  - manchete: "Implantei a gestão de obra em dois galpões com 22 baias."
  - apoio: "Depois de 11/08 o diário ficou 23 dias só no WhatsApp. Recuperado, o avanço passou de 27,6% para 44,7%, lido numa cópia do sistema."
- **Texto aprovado da abertura:** "Orço obras, acompanho a execução e construí os sistemas que uso para isso."
- **Nas cenas:** nenhum texto pintado (sem `fillText`); um só acento laranja (`material('acento')` uma vez); documentos reais só como textura vinda de `site/docs/`.
- Sem dependência nova de Python ou npm. Os add-ons do three.js entram como arquivos copiados da mesma versão, 0.186.0.

## Review Focus

1. **Viewports fora de 16:9** (1366×768, 2560×1080, 1280×1024): o documento real tem de cair exatamente sobre a tela do notebook do vídeo, e o texto não pode cobrir o documento. Teste na Task 6, `checar_viewports`.
2. **Servidor sem Range** (Safari, hospedagem simples): o `clipes.js` congela no pôster, e o documento e o destaque continuam alinhados e visíveis no fim. Teste na Task 6, `checar_sem_range`.
3. **A passagem vídeo → imagem real** tem de ser invisível: o recorte do último quadro na região do retângulo deve bater com o documento (PSNR ≥ 28 dB). Teste na Task 4, `checar_passagem`.
4. **Imagem de documento ainda carregando:** `width`/`height` no HTML iguais às dimensões reais do arquivo, sem salto de layout. Teste na Task 6, estático.
5. **Celular 390×844:** o documento inteiro é ilegível, então aparece o recorte, inteiro na tela e nunca ampliado. Teste na Task 6, `checar_celular`.

## File Structure

- Create `portfolio/cenas/vendor/addons/…`: 13 arquivos oficiais do three.js 0.186.0 (lista na Task 1).
- Create `portfolio/cenas/kit.js`: palco (renderer 2×, luz, ambiente, sombras, GTAO), materiais com textura procedural, câmera por chaves, `enquadrarPlano`, carregador de documentos, `publicar`.
- Create `portfolio/cenas/teste.html`: cena mínima para testar o kit.
- Create `portfolio/cenas/render.py`: servidor local, navegador, captura, encode e pôster; tabela `CENAS`.
- Create `portfolio/cenas/documentos.json` e `portfolio/cenas/documentos.py`: recortes e destaques.
- Create `portfolio/site/docs/`: `sige-portal.webp`, `sige-portal-recorte.webp`, `sige-fotos.webp`, `sige-rdo.webp`, `destaques.json`.
- Create `portfolio/cenas/caso-sige.html`: a cena do caso.
- Create `portfolio/site/video/v2-sige.mp4` e `v2-sige.webp`.
- Create `portfolio/site/v2.html` e `portfolio/site/v2.js`.
- Create `portfolio/tests/check_v2.py`: todas as checagens do piloto.
- Modify `.gitignore` (`portfolio/cenas/saida/`), `docs/superpowers/specs/2026-09-25-site-v2-design.md` (emenda do piloto), `portfolio/README.md`, `ANDAMENTO.md`, `portfolio/revisao/CHANGELOG.md`.

---

### Task 1: Kit das cenas (add-ons, `kit.js`, cena de teste) e a emenda do piloto

**Files:**
- Create: `portfolio/cenas/vendor/addons/` (13 arquivos), `portfolio/cenas/kit.js`, `portfolio/cenas/teste.html`, `portfolio/tests/check_v2.py`
- Create: `portfolio/cenas/render.py` (só as funções `servidor`, `navegador`, `abrir_cena` e as constantes; o render entra na Task 2)
- Modify: `.gitignore`, `docs/superpowers/specs/2026-09-25-site-v2-design.md` (§10 e §12)

**Interfaces:**
- Produces (`kit.js`, ES module):
  - `THREE`, `LARGURA=1920`, `ALTURA=1080`, `RETANGULO={x:.2,y:1/6,w:.6,h:2/3}`
  - `criarPalco({ceu, nevoa}) → {renderer, cena, camera, sol, hemi, composer, ao}`
  - `material(tipo, {repetir}) → MeshStandardMaterial`, com tipos `pasto, solo, concreto, aco, acoPintado, madeira, plastico, papel, telha, folha, tronco, acento`
  - `documento(url) → Promise<Texture>`
  - `trajeto(chaves) → (camera, t) => void`, com `chaves = [[t,[x,y,z],[ax,ay,az]], …]`
  - `enquadrarPlano(camera, centro: Vector3, normal: Vector3, largura: number) → [[x,y,z],[ax,ay,az]]`
  - `limitar(x)`, `suave(x)`, `rampa(t,a,b)`, `lerp(a,b,f)`
  - `publicar(palco, cam, run)`: define `window.renderCena(t)`, `window.PRONTO` e `window.__palco`
- Produces (`render.py`): `RAIZ`, `LARGURA`, `ALTURA`, `ARGS`, `servidor(com_range=True)` (context manager → URL base de `portfolio/`), `navegador()` (context manager → browser), `abrir_cena(nav, url) → (page, erros)`
- Produces (`check_v2.py`): `check(cond, msg)`, `FALHAS`, `main()` com as flags `--navegador` e `--video`

- [ ] **Step 1: Emenda do spec e `.gitignore`**

No spec, §10 item 1: trocar "o caso 1 completo" por "o **caso 3 (SIGE na obra dos galpões)** completo". No fim do §10 acrescentar: "Emenda (25/09): o piloto é o caso 3. O caso 1 só tem prints de 760 px (t1–t4) e a planta de 1400 px, e a regra §7.7 proíbe ampliar documento; ele fica para a fase 2, com os originais que o Cássio mandar." No §12 item 4 acrescentar: "Aprovado em 25/09 com as manchetes e a frase da abertura como estão."

No `.gitignore`, depois do bloco `portfolio/filme/saida/`, acrescentar:

```
# mestres 1920×1080 das cenas do site v2 (a versão web fica em portfolio/site/video/)
portfolio/cenas/saida/
```

- [ ] **Step 2: Vendorizar os add-ons (0.186.0)**

```bash
cd /home/runner/workspace/portfolio/cenas && mkdir -p vendor/addons && B=https://cdn.jsdelivr.net/npm/three@0.186.0/examples/jsm && for f in postprocessing/EffectComposer.js postprocessing/RenderPass.js postprocessing/GTAOPass.js postprocessing/OutputPass.js postprocessing/Pass.js postprocessing/ShaderPass.js postprocessing/MaskPass.js shaders/CopyShader.js shaders/GTAOShader.js shaders/OutputShader.js shaders/PoissonDenoiseShader.js math/SimplexNoise.js environments/RoomEnvironment.js; do mkdir -p vendor/addons/$(dirname $f) && curl -sfL "$B/$f" -o vendor/addons/$f || echo "FALHOU $f"; done && find vendor/addons -name '*.js' | wc -l && grep -l "from 'three'" -r vendor/addons | wc -l
```

Expected: `13` e um número ≥ 10, sem nenhum `FALHOU`. Os add-ons importam `'three'`, que o importmap de cada cena resolve para `../site/vendor/three.module.js`.

- [ ] **Step 3: O teste do kit (falha primeiro)**

Criar `portfolio/tests/check_v2.py`:

```python
#!/usr/bin/env python3
"""Checagens do site v2 (piloto): kit das cenas, documentos, cena do caso SIGE, vídeo e página.

Uso: python3 portfolio/tests/check_v2.py              (estático: documentos, texto, marcação)
     python3 portfolio/tests/check_v2.py --navegador  (+ kit, cena e página no Chromium, via servidor local)
     python3 portfolio/tests/check_v2.py --video      (+ vídeo publicado)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]  # portfolio/
SITE = RAIZ / "site"
CENAS_DIR = RAIZ / "cenas"
sys.path.insert(0, str(CENAS_DIR))
FALHAS = []


def check(cond, msg):
    if not cond:
        FALHAS.append(msg)


def checar_kit():
    """teste.html no Chromium: renderer 2× (3840×2160), sem tone mapping, com ambiente; renderCena determinístico;
    a oclusão (GTAO) escurece o canto parede-piso; nenhum erro de JS."""
    from render import abrir_cena, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/teste.html")
        info = pg.evaluate("(function(){var p=window.__palco;return [p.renderer.domElement.width,p.renderer.domElement.height,"
                           "p.renderer.toneMapping===0,!!p.cena.environment,p.ao.constructor.name];})()")
        check(info == [3840, 2160, True, True, "GTAOPass"], f"kit: palco {info} ≠ [3840, 2160, True, True, 'GTAOPass']")
        pg.evaluate("renderCena(3)")
        a = pg.screenshot(type="png")
        pg.evaluate("renderCena(3)")
        b = pg.screenshot(type="png")
        check(a == b, "kit: renderCena(3) duas vezes deu quadros diferentes (a cena não é pura em t)")
        # o canto parede-piso (0; 0,05; -1,95) projetado em pixels; média de luminância 24×24 com e sem GTAO
        px = pg.evaluate("(function(){var v=new (window.__palco.THREE.Vector3)(0,.05,-1.95).project(window.__palco.camera);"
                         "return [Math.round((v.x+1)/2*1920),Math.round((1-v.y)/2*1080)];})()")
        lum = []
        for ligado in ("true", "false"):
            pg.evaluate(f"window.__palco.ao.enabled={ligado};renderCena(3)")
            lum.append(pg.evaluate(
                "(function(x,y){var c=document.createElement('canvas');c.width=24;c.height=24;var g=c.getContext('2d');"
                "var s=window.__palco.renderer.domElement;g.drawImage(s,(x-12)*2,(y-12)*2,48,48,0,0,24,24);"
                "var d=g.getImageData(0,0,24,24).data,t=0;for(var i=0;i<d.length;i+=4)t+=(d[i]+d[i+1]+d[i+2])/3;return t/(d.length/4);})"
                f"({px[0]},{px[1]})"))
        check(lum[0] <= lum[1] - 3, f"kit: o GTAO não escureceu o canto (com {lum[0]:.1f}, sem {lum[1]:.1f})")
        check(not erros, f"kit: erros de JS em teste.html: {erros}")


def main():
    if "--navegador" in sys.argv:
        checar_kit()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
```

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py --navegador`
Expected: exceção `ModuleNotFoundError: No module named 'render'`. É a falha esperada, porque o kit ainda não existe.

- [ ] **Step 4: `render.py` (servidor, navegador, abrir a cena)**

Criar `portfolio/cenas/render.py` com o cabeçalho abaixo (o render entra na Task 2):

```python
#!/usr/bin/env python3
"""Renderiza as cenas do site v2 (portfolio/cenas/<arquivo>.html) em vídeo 1920×1080 e pôster.
Cada cena é um módulo que expõe window.renderCena(t) (t = tempo local 0..10) e window.PRONTO (texturas prontas).
As cenas importam módulos ES: file:// não serve, então portfolio/ é servido com Range numa porta local.

Uso: python3 portfolio/cenas/render.py --so sige
Saídas: portfolio/cenas/saida/<caso>-mestre.mp4  mestre 1920×1080 crf 16 (ignorado pelo git)
        portfolio/site/video/v2-<caso>.mp4       1920×1080, 24 fps, H.264 High 4.0, GOP 4, sem áudio
        portfolio/site/video/v2-<caso>.webp      pôster = último quadro
"""
import re
import shutil
import subprocess
import sys
import threading
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

AQUI = Path(__file__).resolve().parent  # portfolio/cenas
RAIZ = AQUI.parent                      # portfolio
SAIDA = AQUI / "saida"
WEB = RAIZ / "site" / "video"
sys.path.insert(0, str(RAIZ))
from servir import ComRange  # noqa: E402

LARGURA, ALTURA = 1920, 1080
ARGS = ["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"]
PRONTO_COM_PRAZO = ("Promise.race([window.PRONTO, new Promise(function(_, falha){setTimeout(function(){"
                    "falha(new Error('PRONTO: 30 s sem resolver (textura de documento?)'));}, 30000);})])")


class SemRange(SimpleHTTPRequestHandler):
    """Servidor sem Range (HTTP 200 sempre): o caso do Safari numa hospedagem simples."""
    def log_message(self, *_):
        pass


@contextmanager
def servidor(com_range=True):
    """portfolio/ servido numa porta livre, numa thread; devolve a URL base (sem barra final)."""
    classe = ComRange if com_range else SemRange
    srv = ThreadingHTTPServer(("127.0.0.1", 0), partial(classe, directory=str(RAIZ)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{srv.server_address[1]}"
    finally:
        srv.shutdown()
        srv.server_close()


@contextmanager
def navegador():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = shutil.which("chromium")  # no Replit o Chromium do Playwright não roda: usa o do sistema
        nav = p.chromium.launch(executable_path=exe, args=ARGS) if exe else p.chromium.launch(args=ARGS)
        try:
            yield nav
        finally:
            nav.close()


def abrir_cena(nav, url):
    """Página 1920×1080 (escala 1) com a cena carregada e as texturas prontas; devolve (página, lista de erros de JS)."""
    pg = nav.new_page(viewport={"width": LARGURA, "height": ALTURA}, device_scale_factor=1)
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    pg.goto(url)
    pg.wait_for_function("typeof window.renderCena === 'function' && !!window.PRONTO", timeout=60000)
    pg.evaluate(PRONTO_COM_PRAZO)
    return pg, erros
```

- [ ] **Step 5: `kit.js`**

Criar `portfolio/cenas/kit.js`:

```js
// Kit das cenas do site v2: palco (render 2× para antisserrilhado, luz, ambiente, sombras suaves, oclusão GTAO),
// materiais com textura procedural, câmera por chaves e o carregador dos documentos reais.
// Contrato de cada cena: publicar(palco, cam, run) define window.renderCena(t) (t = 0..10, pura em t) e window.PRONTO.
// Sem tone mapping (NoToneMapping): a tela com o documento real tem de sair no vídeo com as cores da imagem da página.
import * as THREE from 'three';
import {EffectComposer} from './vendor/addons/postprocessing/EffectComposer.js';
import {RenderPass} from './vendor/addons/postprocessing/RenderPass.js';
import {GTAOPass} from './vendor/addons/postprocessing/GTAOPass.js';
import {OutputPass} from './vendor/addons/postprocessing/OutputPass.js';
import {RoomEnvironment} from './vendor/addons/environments/RoomEnvironment.js';
export {THREE};

export const LARGURA = 1920, ALTURA = 1080;
export const RETANGULO = {x: .2, y: 1 / 6, w: .6, h: 2 / 3}; // onde o documento termina no último quadro (frações do quadro); a página usa os mesmos números
const LARANJA = 0xE0622A;

export const limitar = x => Math.max(0, Math.min(1, x));
export const suave = x => { x = limitar(x); return x * x * (3 - 2 * x); };
export const rampa = (t, a, b) => suave((t - a) / (b - a));
export const lerp = (a, b, f) => a + (b - a) * f;

export function criarPalco({ceu = 0xD9E2EA, nevoa = null} = {}) {
  const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
  renderer.setPixelRatio(2);
  renderer.setSize(LARGURA, ALTURA); // estilo 1920×1080 CSS, buffer 3840×2160: o print reduz e suaviza as bordas
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);
  const cena = new THREE.Scene();
  cena.background = new THREE.Color(ceu);
  if (nevoa) cena.fog = new THREE.Fog(ceu, nevoa[0], nevoa[1]);
  const pmrem = new THREE.PMREMGenerator(renderer);
  cena.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture;
  cena.environmentIntensity = .55;
  const camera = new THREE.PerspectiveCamera(35, LARGURA / ALTURA, .1, 600);
  const hemi = new THREE.HemisphereLight(0xEEF3FA, 0x9A7B60, .9);
  cena.add(hemi);
  const sol = new THREE.DirectionalLight(0xFFF3E4, 2.2);
  sol.position.set(-40, 60, 30);
  sol.castShadow = true;
  sol.shadow.mapSize.set(4096, 4096);
  sol.shadow.bias = -.0002;
  sol.shadow.normalBias = .02;
  sol.shadow.radius = 3;
  Object.assign(sol.shadow.camera, {left: -60, right: 60, top: 60, bottom: -60, near: 1, far: 200});
  cena.add(sol, sol.target);
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(2);
  composer.setSize(LARGURA, ALTURA);
  composer.addPass(new RenderPass(cena, camera));
  const ao = new GTAOPass(cena, camera, LARGURA, ALTURA);
  ao.updateGtaoMaterial({radius: .5, distanceExponent: 1.5, thickness: 1, scale: 1.2, samples: 16});
  ao.updatePdMaterial({lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 4, rings: 2, samples: 16});
  composer.addPass(ao);
  composer.addPass(new OutputPass());
  return {THREE, renderer, cena, camera, sol, hemi, composer, ao};
}

// textura procedural: ruído de valor (grade G×G, periódica) + grão fino, na cor-base em sRGB; semente fixa por tipo
function ruido(cor, variacao, G, tam, semente) {
  let s = semente;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const grade = [];
  for (let i = 0; i < G * G; i++) grade.push(rnd());
  const v = (a, b) => grade[((b % G + G) % G) * G + ((a % G + G) % G)];
  const r0 = (cor >> 16) & 255, g0 = (cor >> 8) & 255, b0 = cor & 255;
  const c = document.createElement('canvas');
  c.width = c.height = tam;
  const g = c.getContext('2d'), img = g.createImageData(tam, tam);
  for (let y = 0; y < tam; y++) for (let x = 0; x < tam; x++) {
    const gx = x / tam * G, gy = y / tam * G, ix = Math.floor(gx), iy = Math.floor(gy);
    const fx = suave(gx - ix), fy = suave(gy - iy);
    const n = lerp(lerp(v(ix, iy), v(ix + 1, iy), fx), lerp(v(ix, iy + 1), v(ix + 1, iy + 1), fx), fy);
    const k = 1 + (n - .5) * variacao + (rnd() - .5) * variacao * .35, i = (y * tam + x) * 4;
    img.data[i] = Math.min(255, r0 * k); img.data[i + 1] = Math.min(255, g0 * k); img.data[i + 2] = Math.min(255, b0 * k); img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  return c;
}
const TIPOS = {
  pasto: {cor: 0x86A05C, variacao: .35, G: 8, rug: 1},
  solo: {cor: 0xB4663F, variacao: .3, G: 10, rug: 1},
  concreto: {cor: 0xBEB9AF, variacao: .18, G: 16, rug: .95},
  aco: {cor: 0xC3CAD0, variacao: .08, G: 24, rug: .38, metal: .75},
  acoPintado: {cor: 0x5E6B78, variacao: .06, G: 12, rug: .55, metal: .3},
  madeira: {cor: 0xA27B52, variacao: .25, G: 6, rug: .8},
  plastico: {cor: 0x2E3237, variacao: .04, G: 4, rug: .5},
  papel: {cor: 0xF4F1EA, variacao: .03, G: 4, rug: .95},
  telha: {cor: 0xAEB6BD, variacao: .1, G: 10, rug: .5, metal: .5},
  folha: {cor: 0x5F7F45, variacao: .3, G: 6, rug: 1},
  tronco: {cor: 0x7A6048, variacao: .2, G: 6, rug: 1},
  acento: {cor: LARANJA, variacao: .05, G: 4, rug: .6},
};
const cache = {};
export function material(tipo, {repetir = 1} = {}) {
  const chave = tipo + '|' + repetir;
  if (cache[chave]) return cache[chave];
  const d = TIPOS[tipo];
  if (!d) throw new Error('material desconhecido: ' + tipo);
  let semente = 7;
  for (const ch of tipo) semente = (semente * 31 + ch.charCodeAt(0)) % 2147483647;
  const tx = new THREE.CanvasTexture(ruido(d.cor, d.variacao, d.G, 512, semente || 1));
  tx.colorSpace = THREE.SRGBColorSpace;
  tx.wrapS = tx.wrapT = THREE.RepeatWrapping;
  tx.repeat.set(repetir, repetir);
  tx.anisotropy = 8;
  return (cache[chave] = new THREE.MeshStandardMaterial({map: tx, roughness: d.rug, metalness: d.metal || 0}));
}

const PRONTOS = [];
const carregador = new THREE.TextureLoader();
export function documento(url) {
  const p = carregador.loadAsync(url).then(tx => {
    tx.colorSpace = THREE.SRGBColorSpace;
    tx.anisotropy = 16;
    tx.minFilter = THREE.LinearMipmapLinearFilter;
    tx.generateMipmaps = true;
    return tx;
  });
  PRONTOS.push(p);
  return p;
}

// câmera por chaves: Catmull-Rom centrípeta nas posições e nos alvos; em t = tᵢ a câmera está exatamente na chave i
// (o último quadro é exato); a suavização é global (acelera no início, freia no fim), não em cada chave
export function trajeto(chaves) {
  const P = new THREE.CatmullRomCurve3(chaves.map(k => new THREE.Vector3(...k[1])), false, 'centripetal');
  const A = new THREE.CatmullRomCurve3(chaves.map(k => new THREE.Vector3(...k[2])), false, 'centripetal');
  const T = chaves.map(k => k[0]), n = T.length;
  return function (camera, t) {
    const tt = T[0] + (T[n - 1] - T[0]) * suave((t - T[0]) / (T[n - 1] - T[0]));
    let i = 0;
    while (i < n - 2 && tt > T[i + 1]) i++;
    const u = (i + limitar((tt - T[i]) / (T[i + 1] - T[i]))) / (n - 1);
    camera.position.copy(P.getPoint(u));
    camera.lookAt(A.getPoint(u));
    camera.updateMatrixWorld();
  };
}

// a chave que põe um plano de largura `largura` (proporção 1,6) exatamente em RETANGULO: câmera no eixo do plano
export function enquadrarPlano(camera, centro, normal, largura) {
  const vfov = THREE.MathUtils.degToRad(camera.fov);
  const hfov = 2 * Math.atan(Math.tan(vfov / 2) * camera.aspect);
  const d = largura / (2 * RETANGULO.w * Math.tan(hfov / 2));
  const pos = centro.clone().addScaledVector(normal.clone().normalize(), d);
  return [pos.toArray(), centro.toArray()];
}

export function publicar(palco, cam, run) {
  window.__palco = palco;
  window.PRONTO = Promise.all(PRONTOS);
  window.renderCena = function (t) { run(t); cam(palco.camera, t); palco.composer.render(); };
}
```

- [ ] **Step 6: `teste.html`**

Criar `portfolio/cenas/teste.html`:

```html
<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Cena de teste do kit</title>
<style>html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}</style>
<script type="importmap">{"imports":{"three":"../site/vendor/three.module.js"}}</script>
</head><body>
<script type="module">
// cena mínima do kit: piso, parede ao fundo (canto parede-piso em z = -2) e um cubo; câmera parada
import {THREE, criarPalco, material, trajeto, publicar} from './kit.js';
const palco = criarPalco();
const {cena} = palco;
const piso = new THREE.Mesh(new THREE.BoxGeometry(12, .2, 8), material('concreto', {repetir: 2}));
piso.position.y = -.1; piso.receiveShadow = true; cena.add(piso);
const parede = new THREE.Mesh(new THREE.BoxGeometry(12, 3, .2), material('papel'));
parede.position.set(0, 1.5, -2.1); parede.receiveShadow = parede.castShadow = true; cena.add(parede);
const cubo = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), material('madeira'));
cubo.position.set(1.5, .5, 0); cubo.castShadow = cubo.receiveShadow = true; cena.add(cubo);
publicar(palco, trajeto([[0, [3, 2.2, 6], [0, .6, -1]], [10, [3, 2.2, 6], [0, .6, -1]]]), t => { cubo.rotation.y = t * .1; });
</script>
</body></html>
```

- [ ] **Step 7: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py --navegador`
Expected: `OK`.

Se o GTAO der erro de shader no SwiftShader, não desligue o teste. Reporte BLOCKED com o erro, porque a oclusão é critério do spec §7.4. Se só a diferença de luminância ficar abaixo de 3, ajuste `scale` e `radius` em `updateGtaoMaterial`, sem mexer no teste.

- [ ] **Step 8: Commit**

```bash
cd /home/runner/workspace && git add .gitignore docs/superpowers/specs/2026-09-25-site-v2-design.md portfolio/cenas/vendor portfolio/cenas/kit.js portfolio/cenas/teste.html portfolio/cenas/render.py portfolio/tests/check_v2.py && git commit -m "Site v2: kit das cenas (three 0.186, GTAO, ambiente, render 2×), cena de teste e check_v2; piloto passa a ser o caso SIGE

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: Render e publicação (`render.py`)

**Files:**
- Modify: `portfolio/cenas/render.py` (acrescentar render, encode, pôster, `main`)
- Modify: `portfolio/tests/check_v2.py` (`checar_render`)

**Interfaces:**
- Consumes: `servidor`, `navegador`, `abrir_cena` (Task 1); `teste.html` (Task 1)
- Produces:
  - `FPS=24`, `CENAS = {"sige": ("caso-sige.html", 10.0)}` (a entrada existe desde já; a cena chega na Task 4)
  - `tempo_local(s, dur) → t`
  - `quadros(dur) → int`
  - `psnr(a, b) → float`
  - `renderizar(pg, dur, mestre)`
  - `encode_web(mestre, destino, crf)`
  - `poster(mp4, dur, destino)`
  - `publicar(caso, mestre, dur) → crf`
  - `TETO_CLIPE`, `TETO_POSTER`

- [ ] **Step 1: Teste que falha**

Em `check_v2.py`, acrescentar antes de `main`:

```python
def ffprobe(arquivo):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(arquivo)],
                       capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def checar_render():
    """render.py com a cena de teste: 1 s → 24 quadros 1920×1080; encode web H.264 High 4.0, sem áudio;
    pontas paradas (os dois primeiros quadros iguais); o pôster é o último quadro (PSNR ≥ 40 dB)."""
    import render
    with tempfile.TemporaryDirectory() as tmp, render.servidor() as base, render.navegador() as nav:
        tmp = Path(tmp)
        pg, erros = render.abrir_cena(nav, f"{base}/cenas/teste.html")
        mestre, web, cartaz = tmp / "teste-mestre.mp4", tmp / "teste.mp4", tmp / "teste.webp"
        render.renderizar(pg, 1.0, mestre)
        render.encode_web(mestre, web, render.CRF)
        render.poster(web, 1.0, cartaz)
        info = ffprobe(web)
        v = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
        a = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
        check(len(v) == 1 and (v[0]["width"], v[0]["height"]) == (1920, 1080), f"render: vídeo {v and (v[0]['width'], v[0]['height'])} ≠ 1920×1080")
        check(v and v[0].get("nb_frames") == "24", f"render: {v and v[0].get('nb_frames')} quadros em 1 s, esperava 24")
        check(v and v[0].get("profile") == "High" and v[0].get("level") == 40, f"render: perfil {v and (v[0].get('profile'), v[0].get('level'))} ≠ High 4.0")
        check(not a, "render: o vídeo tem trilha de áudio")
        q0, q1 = tmp / "q0.png", tmp / "q1.png"
        for n, f in ((0, q0), (1, q1)):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mestre), "-vf", f"select='eq(n,{n})'", "-vframes", "1", str(f)], check=True)
        check(render.psnr(q0, q1) >= 50, "render: o início não está parado (quadros 0 e 1 diferentes)")
        check(cartaz.exists() and cartaz.stat().st_size <= render.TETO_POSTER, "render: pôster ausente ou acima do teto")
        check(not erros, f"render: erros de JS: {erros}")
```

Em `main`, dentro do `if "--navegador"`, depois de `checar_kit()`, chamar `checar_render()`.

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py --navegador`
Expected: `AttributeError: module 'render' has no attribute 'renderizar'`.

- [ ] **Step 2: Render, encode, pôster e `main`**

Acrescentar ao `render.py`, depois de `abrir_cena`:

```python
FPS = 24
INICIO_PARADO, FIM_PARADO = 0.3, 0.5  # s parados no começo e no fim do vídeo
TETO_CLIPE, TETO_POSTER = int(2.5 * 1024 * 1024), 150 * 1024
CRF, CRF_MAX = 26, 32
CENAS = {"sige": ("caso-sige.html", 10.0)}  # caso: (arquivo em cenas/, duração do vídeo em s); t da cena vai de 0 a 10


def tempo_local(s, dur):
    """Segundo s do vídeo → t da cena (0..10): parado nos primeiros 0,3 s e nos últimos 0,5 s, linear no meio."""
    f = min(1.0, max(0.0, (s - INICIO_PARADO) / (dur - INICIO_PARADO - FIM_PARADO)))
    return 10.0 * f


def quadros(dur):
    return int(round(dur * FPS))


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *args], check=True)


def psnr(a, b):
    """PSNR médio (dB) entre duas imagens ou dois vídeos do mesmo tamanho; inf se iguais, 0.0 se o ffmpeg não mediu."""
    r = subprocess.run(["ffmpeg", "-i", str(a), "-i", str(b), "-lavfi", "psnr", "-f", "null", "-"], capture_output=True, text=True)
    m = re.search(r"average:(inf|[\d.]+)", r.stderr)
    if r.returncode != 0 or not m:
        return 0.0
    return float("inf") if m.group(1) == "inf" else float(m.group(1))


def renderizar(pg, dur, mestre):
    """Quadro a quadro: renderCena(t) → PNG da janela 1920×1080 → ffmpeg (mestre crf 16)."""
    mestre.parent.mkdir(parents=True, exist_ok=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-vcodec", "png", "-i", "-",
                           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", str(mestre)], stdin=subprocess.PIPE)
    n = quadros(dur)
    for k in range(n):
        pg.evaluate(f"renderCena({tempo_local(k / FPS, dur)!r})")
        ff.stdin.write(pg.screenshot(type="png"))
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit(f"{mestre.name}: ffmpeg falhou no mestre")
    print(f"{mestre.name}: {n} quadros", flush=True)


def encode_web(mestre, destino, crf):
    ffmpeg("-i", str(mestre), "-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-g", "4", "-keyint_min", "4",
           "-sc_threshold", "0", "-bf", "0", "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.0",
           "-movflags", "+faststart", "-an", str(destino))


def poster(mp4, dur, destino):
    """Pôster = último quadro do vídeo publicado: WebP com PSNR ≥ 40 dB e ≤ 150 KB (q75, senão 82, 90)."""
    png = destino.with_name(destino.stem + "-ultimo.png")
    png.unlink(missing_ok=True)
    ffmpeg("-i", str(mp4), "-vf", f"select='eq(n,{quadros(dur) - 1})'", "-vframes", "1", "-update", "1", str(png))
    if not png.exists():
        sys.exit(f"{mp4.name}: sem o quadro {quadros(dur) - 1} (o último) para o pôster")
    for q in (75, 82, 90):
        ffmpeg("-i", str(png), "-c:v", "libwebp", "-quality", str(q), str(destino))
        if psnr(destino, png) >= 40 and destino.stat().st_size <= TETO_POSTER:
            png.unlink()
            return
    sys.exit(f"{mp4.name}: pôster sem PSNR ≥ 40 dB dentro de 150 KB")


def publicar(caso, mestre, dur):
    """Encode web dentro de 2,5 MB (crf 26 → 32) e pôster. Devolve o crf usado."""
    WEB.mkdir(parents=True, exist_ok=True)
    destino = WEB / f"v2-{caso}.mp4"
    for crf in range(CRF, CRF_MAX + 1):
        encode_web(mestre, destino, crf)
        if destino.stat().st_size <= TETO_CLIPE:
            break
    else:
        sys.exit(f"{caso}: acima de 2,5 MB mesmo com crf {CRF_MAX}")
    poster(destino, dur, WEB / f"v2-{caso}.webp")
    print(f"{caso}: {destino.stat().st_size / 1024:.0f} KB (crf {crf})", flush=True)
    return crf


def main():
    i = sys.argv.index("--so") + 1 if "--so" in sys.argv else 0
    if i and (i >= len(sys.argv) or sys.argv[i] not in CENAS):
        sys.exit(f"--so pede um caso de CENAS: {', '.join(CENAS)}")
    casos = [sys.argv[i]] if i else list(CENAS)
    with servidor() as base, navegador() as nav:
        for caso in casos:
            arquivo, dur = CENAS[caso]
            pg, erros = abrir_cena(nav, f"{base}/cenas/{arquivo}")
            if erros:
                sys.exit(f"{caso}: erro de JavaScript ao carregar: {'; '.join(erros)}")
            mestre = SAIDA / f"{caso}-mestre.mp4"
            renderizar(pg, dur, mestre)
            if erros:
                sys.exit(f"{caso}: erro de JavaScript no render: {'; '.join(erros)}")
            publicar(caso, mestre, dur)
            pg.close()
    print("pronto:", WEB)


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py --navegador`
Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
cd /home/runner/workspace && git add portfolio/cenas/render.py portfolio/tests/check_v2.py && git commit -m "Site v2: render.py (captura 1920×1080, mestre crf 16, encode High 4.0 GOP 4 até 2,5 MB, pôster ≤ 150 KB) e checar_render

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: Documentos reais (`documentos.py`, `site/docs/`)

**Files:**
- Create: `portfolio/cenas/documentos.json`, `portfolio/cenas/documentos.py`
- Create: `portfolio/site/docs/` (4 WebP + `destaques.json`)
- Modify: `portfolio/tests/check_v2.py` (`checar_documentos`, estático)

**Interfaces:**
- Produces:
  - `site/docs/sige-portal.webp` (1600×1000), com destaque `[110, 278, 200, 78]` (x, y, largura, altura em px da imagem)
  - `site/docs/sige-portal-recorte.webp` (800×400, recorte `[20, 140, 800, 400]` do portal, que contém o destaque)
  - `site/docs/sige-fotos.webp` (1600×1353), `site/docs/sige-rdo.webp` (1600×1193)
  - `site/docs/destaques.json`: `{id: {"largura": w, "altura": h, "destaque": [x,y,w,h] | null, "recorte": [x,y,w,h] | null}}`
  - `documentos.py`: `LIBERADOS` (as três fontes anonimizadas) e `gerar() → dict`

- [ ] **Step 1: Teste que falha**

Em `check_v2.py`, acrescentar:

```python
DOCS = SITE / "docs"


def dims(arquivo):
    r = subprocess.run(["magick", "identify", "-format", "%w %h", str(arquivo)], capture_output=True, text=True)
    return tuple(int(x) for x in r.stdout.split()) if r.returncode == 0 else None


def checar_documentos():
    """site/docs: só o que o manifesto lista, vindo só de fontes liberadas (já anonimizadas); dimensões conferem;
    o destaque cai dentro da imagem e dentro do recorte."""
    from documentos import LIBERADOS, MANIFESTO
    man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    check((DOCS / "destaques.json").exists(), "documentos: site/docs/destaques.json ausente (rodar documentos.py)")
    if not (DOCS / "destaques.json").exists():
        return
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))
    esperados = {f"{i}.webp" for i in man} | {f"{i}-recorte.webp" for i, d in man.items() if d.get("recorte")} | {"destaques.json"}
    achados = {p.name for p in DOCS.iterdir()}
    check(achados == esperados, f"documentos: site/docs tem {sorted(achados ^ esperados)} fora do manifesto (ou falta)")
    for i, d in man.items():
        check(d["fonte"] in LIBERADOS, f"documentos: {i} vem de {d['fonte']}, fora das fontes anonimizadas liberadas")
        x, y, w, h = d["corte"]
        check(dims(DOCS / f"{i}.webp") == (w, h), f"documentos: {i}.webp {dims(DOCS / f'{i}.webp')} ≠ corte {w}×{h}")
        check(dest.get(i, {}).get("largura") == w and dest[i].get("altura") == h, f"documentos: destaques.json de {i} sem as dimensões do corte")
        if d.get("destaque"):
            dx, dy, dw, dh = d["destaque"]
            check(0 <= dx and 0 <= dy and dx + dw <= w and dy + dh <= h, f"documentos: destaque de {i} fora da imagem")
            check(dest[i]["destaque"] == d["destaque"], f"documentos: destaques.json de {i} ≠ manifesto")
        if d.get("recorte"):
            rx, ry, rw, rh = d["recorte"]
            check(dims(DOCS / f"{i}-recorte.webp") == (rw, rh), f"documentos: recorte de {i} com dimensões erradas")
            if d.get("destaque"):
                check(rx <= dx and ry <= dy and dx + dw <= rx + rw and dy + dh <= ry + rh, f"documentos: o recorte de {i} não contém o destaque")
    check(set(man) >= {"sige-portal", "sige-fotos", "sige-rdo"}, "documentos: o caso SIGE pede sige-portal, sige-fotos e sige-rdo")
```

Em `main`, antes do `if "--navegador"`, chamar `checar_documentos()` (é estático).

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py`
Expected: `ModuleNotFoundError: No module named 'documentos'`.

- [ ] **Step 2: Manifesto e script**

Criar `portfolio/cenas/documentos.json`:

```json
{
  "sige-portal": {"fonte": "site/img/p-portal.webp", "corte": [0, 0, 1600, 1000], "destaque": [110, 278, 200, 78], "recorte": [20, 140, 800, 400]},
  "sige-fotos": {"fonte": "site/img/p-fotos.webp", "corte": [0, 0, 1600, 1353]},
  "sige-rdo": {"fonte": "site/img/p-diario-portal.webp", "corte": [0, 0, 1600, 1193]}
}
```

O destaque `[110, 278, 200, 78]` é o número "44.7%" do anel "CONCLUÍDO", medido no print de 1600 px (texto entre x ≈ 120–300 e y ≈ 290–345).

Criar `portfolio/cenas/documentos.py`:

```python
#!/usr/bin/env python3
"""Prepara os documentos reais das cenas e da página do site v2: recorta cada fonte do manifesto (documentos.json)
para portfolio/site/docs/<id>.webp, grava o recorte do destaque para o celular (<id>-recorte.webp) e as coordenadas
em site/docs/destaques.json. Só aceita fontes já anonimizadas (LIBERADOS): nome de cliente e endereço borrados.

Uso: python3 portfolio/cenas/documentos.py
"""
import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
MANIFESTO = AQUI / "documentos.json"
DOCS = RAIZ / "site" / "docs"
# prints do site já anonimizados (nome do cliente e endereço borrados; conferido em 25/09 no p-portal)
LIBERADOS = {"site/img/p-portal.webp", "site/img/p-fotos.webp", "site/img/p-diario-portal.webp"}


def cortar(fonte, caixa, destino):
    x, y, w, h = caixa
    subprocess.run(["magick", str(fonte), "-crop", f"{w}x{h}+{x}+{y}", "+repage", "-quality", "90", str(destino)], check=True)


def gerar():
    man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    DOCS.mkdir(parents=True, exist_ok=True)
    for velho in DOCS.iterdir():
        velho.unlink()
    destaques = {}
    for i, d in man.items():
        if d["fonte"] not in LIBERADOS:
            sys.exit(f"{i}: fonte {d['fonte']} não está em LIBERADOS (anonimizar antes e liberar à mão)")
        fonte = RAIZ / d["fonte"]
        cortar(fonte, d["corte"], DOCS / f"{i}.webp")
        if d.get("recorte"):
            cx, cy, _, _ = d["corte"]
            rx, ry, rw, rh = d["recorte"]
            cortar(fonte, [cx + rx, cy + ry, rw, rh], DOCS / f"{i}-recorte.webp")
        destaques[i] = {"largura": d["corte"][2], "altura": d["corte"][3], "destaque": d.get("destaque"), "recorte": d.get("recorte")}
    (DOCS / "destaques.json").write_text(json.dumps(destaques, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return destaques


if __name__ == "__main__":
    for k, v in gerar().items():
        print(k, v["largura"], "×", v["altura"])
```

- [ ] **Step 3: Gerar e ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/cenas/documentos.py && python3 portfolio/tests/check_v2.py`
Expected: as três linhas `sige-portal 1600 × 1000`, `sige-fotos 1600 × 1353`, `sige-rdo 1600 × 1193`, depois `OK`.

- [ ] **Step 4: Olhar o destaque e o sigilo**

```bash
cd /home/runner/workspace/portfolio/site/docs && S=/tmp/claude-1000/-home-runner-workspace/eaf52574-a179-46a2-af04-b9d1b2aff72a/scratchpad && magick sige-portal.webp -fill none -stroke '#E0622A' -strokewidth 4 -draw "rectangle 110,278 310,356" $S/destaque.png
```

Abrir `destaque.png` e o `sige-portal-recorte.webp` com Read. Expected:
- a caixa laranja envolve "44.7%" com folga, sem cortar dígitos;
- o recorte mostra o anel com 44,7%, "109 Etapas" e "65 Relatórios";
- o nome da obra e o endereço aparecem borrados;
- nos quatro arquivos de `site/docs/`, nenhum nome de cliente legível (abrir `sige-fotos.webp` e `sige-rdo.webp` também).

Se a caixa cortar dígitos, corrija `destaque` no manifesto e regere. Se algum nome de cliente estiver legível, reporte BLOCKED: anonimizar é decisão do controlador.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/cenas/documentos.json portfolio/cenas/documentos.py portfolio/site/docs portfolio/tests/check_v2.py && git commit -m "Site v2: documentos reais do caso SIGE (portal com 44,7%, fotos, RDO) em site/docs, destaque e recorte para o celular

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: A cena do caso SIGE (`caso-sige.html`)

**Files:**
- Create: `portfolio/cenas/caso-sige.html`
- Modify: `portfolio/tests/check_v2.py` (`checar_cena_sige`, `checar_passagem`, estático `checar_cena_estatica`)

**Interfaces:**
- Consumes: `kit.js` (Task 1); `site/docs/sige-portal.webp`, `sige-fotos.webp`, `sige-rdo.webp` (Task 3); `render.abrir_cena`, `render.servidor`, `render.navegador` (Task 1)
- Produces: `window.__cena = {galpoes: Group[2], divisorias: Group[22], paineisSubindo: Group[3], tela: Mesh, quadros: Mesh[2]}`. `tela` é o plano 0,32 × 0,20 m com o `sige-portal`; `quadros` são as folhas presas na parede do escritório (`sige-fotos`, `sige-rdo`).

- [ ] **Step 1: Testes que falham**

Em `check_v2.py`, acrescentar:

```python
CENA_SIGE = CENAS_DIR / "caso-sige.html"


def checar_cena_estatica():
    """Estilo: nenhum texto pintado, um só acento, documentos só de ../site/docs/."""
    check(CENA_SIGE.exists(), "cena: portfolio/cenas/caso-sige.html não existe")
    if not CENA_SIGE.exists():
        return
    s = CENA_SIGE.read_text(encoding="utf-8")
    check("fillText" not in s and "strokeText" not in s, "cena sige: texto pintado (fillText/strokeText)")
    n = s.count("material('acento')")
    check(n == 1, f"cena sige: {n} usos de material('acento'), esperava 1")
    check(re.search(r"0x[Ee]0622[Aa]|ORANGE|LARANJA", s) is None, "cena sige: laranja fora de material('acento')")
    docs = set(re.findall(r"documento\('([^']+)'\)", s))
    check(docs == {"../site/docs/sige-portal.webp", "../site/docs/sige-fotos.webp", "../site/docs/sige-rdo.webp"},
          f"cena sige: documentos {sorted(docs)}")


def checar_cena_sige():
    """No Chromium: conteúdo (2 galpões, 22 divisórias, 3 painéis subindo e parados no fim), tela com o portal;
    t=0: os dois galpões inteiros no quadro, juntos ≥ 60% da largura, e antes do começo da névoa;
    t=10: os cantos da tela a ≤ 2 px de RETANGULO e o centro da tela como primeiro alvo de um raio da câmera."""
    from render import abrir_cena, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/caso-sige.html")
        conteudo = pg.evaluate("""(function(){var S=window.__cena;renderCena(10);
          return [S.galpoes.length,S.divisorias.length,S.paineisSubindo.length,
                  S.paineisSubindo.every(function(p){return Math.abs(p.rotation.x)<1e-6;}),
                  S.tela.material.map&&S.tela.material.map.image.src.split('/').pop(),
                  S.quadros.map(function(q){return q.material.map.image.src.split('/').pop();}).sort()];})()""")
        check(conteudo == [2, 22, 3, True, "sige-portal.webp", ["sige-fotos.webp", "sige-rdo.webp"]], f"cena sige: conteúdo {conteudo}")
        inicio = pg.evaluate("""(function(){var S=window.__cena,T=window.__palco.THREE,cam=window.__palco.camera,f=window.__palco.cena.fog;renderCena(0);
          var xs=[],ok=true,dmax=0;S.galpoes.forEach(function(G){var b=new T.Box3().setFromObject(G);
            [b.min.x,b.max.x].forEach(function(x){[b.min.z,b.max.z].forEach(function(z){[0,b.max.y].forEach(function(y){
              var p=new T.Vector3(x,y,z);dmax=Math.max(dmax,p.distanceTo(cam.position));p.project(cam);
              xs.push(p.x);if(Math.abs(p.x)>.95||Math.abs(p.y)>.95)ok=false;});});});});
          return [ok,Math.max.apply(null,xs)-Math.min.apply(null,xs),dmax<f.near];})()""")
        check(inicio[0], "cena sige: em t=0 algum canto dos galpões sai do quadro")
        check(inicio[1] >= 1.2, f"cena sige: em t=0 os galpões ocupam {inicio[1] / 2:.0%} da largura, esperava ≥ 60%")
        check(inicio[2], "cena sige: em t=0 parte dos galpões está dentro da névoa")
        fim = pg.evaluate("""(function(){var S=window.__cena,T=window.__palco.THREE,cam=window.__palco.camera;renderCena(10);
          S.tela.geometry.computeBoundingBox();var b=S.tela.geometry.boundingBox,cs=[];
          [[b.min.x,b.min.y],[b.max.x,b.min.y],[b.max.x,b.max.y],[b.min.x,b.max.y]].forEach(function(c){
            var p=S.tela.localToWorld(new T.Vector3(c[0],c[1],0)).project(cam);cs.push([(p.x+1)/2*1920,(1-p.y)/2*1080]);});
          var centro=S.tela.getWorldPosition(new T.Vector3()),dir=centro.clone().sub(cam.position).normalize();
          var hits=new T.Raycaster(cam.position.clone(),dir).intersectObject(window.__palco.cena,true).filter(function(h){return h.object.isMesh;});
          return [cs,hits.length>0&&hits[0].object===S.tela];})()""")
        alvo = [[384, 180], [1536, 180], [1536, 900], [384, 900]]  # RETANGULO em 1920×1080, cantos em sentido horário a partir do sup. esq.
        achados = sorted(fim[0], key=lambda c: (round(c[1] / 100), c[0]))
        esperado = sorted(alvo, key=lambda c: (round(c[1] / 100), c[0]))
        erro = max(max(abs(a[0] - e[0]), abs(a[1] - e[1])) for a, e in zip(achados, esperado))
        check(erro <= 2, f"cena sige: cantos da tela a {erro:.1f} px de RETANGULO no último quadro (máx. 2 px): {achados}")
        check(fim[1], "cena sige: no último quadro algo fica entre a câmera e o centro da tela")
        check(not erros, f"cena sige: erros de JS: {erros}")


def checar_passagem():
    """A passagem vídeo → imagem real é invisível: no último quadro, a região de RETANGULO, levada a 1600×1000,
    tem PSNR ≥ 28 dB contra site/docs/sige-portal.webp."""
    from render import abrir_cena, navegador, psnr, servidor
    with tempfile.TemporaryDirectory() as tmp, servidor() as base, navegador() as nav:
        tmp = Path(tmp)
        pg, _ = abrir_cena(nav, f"{base}/cenas/caso-sige.html")
        pg.evaluate("renderCena(10)")
        quadro = tmp / "fim.png"
        quadro.write_bytes(pg.screenshot(type="png"))
        regiao = tmp / "regiao.png"
        subprocess.run(["magick", str(quadro), "-crop", "1152x720+384+180", "+repage", "-resize", "1600x1000!", str(regiao)], check=True)
        doc = tmp / "doc.png"
        subprocess.run(["magick", str(DOCS / "sige-portal.webp"), str(doc)], check=True)
        valor = psnr(regiao, doc)
        check(valor >= 28, f"passagem: PSNR {valor:.1f} dB entre a tela do último quadro e o documento real (mín. 28)")
```

Em `main`: chamar `checar_cena_estatica()` junto do estático; dentro de `--navegador`, depois de `checar_render()`, chamar `checar_cena_sige()` e `checar_passagem()`.

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py`
Expected: `FALHOU:` com `cena: portfolio/cenas/caso-sige.html não existe`.

- [ ] **Step 2: A cena**

Criar `portfolio/cenas/caso-sige.html`:

```html
<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Cena · SIGE na obra dos galpões</title>
<style>html,body{margin:0;background:#000;overflow:hidden}canvas{display:block}</style>
<script type="importmap">{"imports":{"three":"../site/vendor/three.module.js"}}</script>
</head><body>
<script type="module">
// Caso SIGE na obra dos galpões: a obra (dois galpões de Light Steel Frame numa fazenda, 11 baias cada, terra vermelha
// como nas fotos) e o escritório de obra, onde o notebook mostra o portal do cliente real (44,7% concluído).
// t: 0,6 → 2,8 os três últimos painéis do galpão B sobem (verticalização, como nas fotos); a câmera desce da vista
// aérea (t=0) ao escritório (t=4 e 7) e termina de frente para a tela (t=10), com a tela exatamente em RETANGULO.
import {THREE, criarPalco, material, documento, trajeto, enquadrarPlano, publicar, rampa} from './kit.js';

const palco = criarPalco({ceu: 0xD9E2EA, nevoa: [140, 340]});
const {cena, camera, sol} = palco;
sol.position.set(-40, 60, 30);
const S = {galpoes: [], divisorias: [], paineisSubindo: [], tela: null, quadros: []};
window.__cena = S;

function perfil(c, a, p, x, y, z, pai, mat = material('aco')) {
  const m = new THREE.Mesh(new THREE.BoxGeometry(c, a, p), mat);
  m.position.set(x, y, z); m.castShadow = m.receiveShadow = true; pai.add(m); return m;
}
// painel de Light Steel Frame: guias em cima e embaixo, montantes a cada 40 cm, bloqueador no meio (como nas fotos)
function painelLSF(compr, alt, pai) {
  const g = new THREE.Group(); pai.add(g);
  perfil(compr, .09, .09, compr / 2, .045, 0, g);
  perfil(compr, .09, .09, compr / 2, alt - .045, 0, g);
  const n = Math.round(compr / .4);
  for (let i = 0; i <= n; i++) perfil(.04, alt - .18, .09, Math.min(i * .4, compr - .02), alt / 2, 0, g);
  perfil(compr, .04, .09, compr / 2, alt * .5, 0, g);
  return g;
}
function arvore(x, z, s) {
  const g = new THREE.Group(); g.position.set(x, 0, z); cena.add(g);
  const tronco = new THREE.Mesh(new THREE.CylinderGeometry(.12 * s, .18 * s, 3 * s, 8), material('tronco'));
  tronco.position.y = 1.5 * s; tronco.castShadow = true; g.add(tronco);
  [[0, 3.6, 0, 1.5], [.6, 3.1, .3, 1.1], [-.5, 3.3, -.4, 1.2]].forEach(f => {
    const copa = new THREE.Mesh(new THREE.IcosahedronGeometry(f[3] * s, 1), material('folha'));
    copa.position.set(f[0] * s, f[1] * s, f[2] * s); copa.castShadow = true; g.add(copa);
  });
}

// terreno: pasto e a praça da obra em terra vermelha
const pasto = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), material('pasto', {repetir: 60}));
pasto.rotation.x = -Math.PI / 2; pasto.receiveShadow = true; cena.add(pasto);
const praca = new THREE.Mesh(new THREE.PlaneGeometry(96, 56), material('solo', {repetir: 12}));
praca.rotation.x = -Math.PI / 2; praca.position.set(0, .02, 4); praca.receiveShadow = true; cena.add(praca);

// os dois galpões: piso de concreto, parede do fundo em painéis de LSF de 3 m, 11 divisórias de baia; o A já tem os pilares da cobertura
const COMPR = 33, LARG = 9, N_BAIAS = 11, H_PAINEL = 2.2, H_PILAR = 4.8;
function galpao(x0, comPilares) {
  const G = new THREE.Group(); G.position.set(x0, 0, 0); cena.add(G);
  const piso = new THREE.Mesh(new THREE.BoxGeometry(COMPR, .18, LARG), material('concreto', {repetir: 6}));
  piso.position.y = .09; piso.castShadow = piso.receiveShadow = true; G.add(piso);
  const fundo = [];
  for (let i = 0; i < COMPR / 3; i++) { const p = painelLSF(3, H_PAINEL, G); p.position.set(-COMPR / 2 + i * 3, .18, -LARG / 2 + .1); fundo.push(p); }
  const passo = COMPR / N_BAIAS;
  for (let k = 0; k < N_BAIAS; k++) {
    const d = painelLSF(3.6, H_PAINEL * .8, G); d.rotation.y = -Math.PI / 2;
    d.position.set(-COMPR / 2 + (k + .5) * passo, .18, -LARG / 2 + .15); S.divisorias.push(d);
  }
  if (comPilares) for (let k = 0; k <= N_BAIAS; k += 2)
    [-LARG / 2 + .3, LARG / 2 - .3].forEach(z => perfil(.25, H_PILAR, .25, -COMPR / 2 + k * passo, .18 + H_PILAR / 2, z, G, material('acoPintado')));
  S.galpoes.push(G);
  return fundo;
}
galpao(-20, true);
const fundoB = galpao(20, false);
S.paineisSubindo = fundoB.slice(-3); // os três últimos painéis do B ainda sobem (verticalização)

// canteiro: pilhas de perfis e os cones que marcam o caminho até o escritório (o acento da cena)
for (let i = 0; i < 6; i++) perfil(6, .09, .09, 0, .05 + i * .1, 9 + (i % 2) * .12, cena);
const cone = material('acento');
[[2, 10.5], [3.2, 12.5], [4.4, 14.5], [5.6, 16.5]].forEach(p => {
  const c = new THREE.Mesh(new THREE.ConeGeometry(.22, .7, 16), cone); c.position.set(p[0], .37, p[1]); c.castShadow = true; cena.add(c);
});
[[-45, -30, 1.4], [-38, -34, 1.1], [42, -31, 1.3], [50, -26, 1.2], [-52, 24, 1.2], [58, 30, 1.4]].forEach(a => arvore(a[0], a[1], a[2]));

// escritório de obra: telheiro aberto para a câmera, mesa, notebook com o portal, folhas presas na parede do fundo
const E = new THREE.Group(); E.position.set(0, 0, 20); cena.add(E);
const pisoE = new THREE.Mesh(new THREE.BoxGeometry(5, .12, 4), material('madeira', {repetir: 2})); pisoE.position.y = .06; pisoE.receiveShadow = true; E.add(pisoE);
[[-2.4, -1.9], [2.4, -1.9], [-2.4, 1.9], [2.4, 1.9]].forEach(p => perfil(.1, 2.7, .1, p[0], 1.35, p[1], E, material('acoPintado')));
perfil(5.4, .06, 4.4, 0, 2.73, 0, E, material('telha'));
const paredeE = perfil(5, 2.6, .08, 0, 1.36, -1.95, E, material('papel'));
paredeE.castShadow = false;
perfil(1.6, .05, .8, 0, .75, -.9, E, material('madeira'));
[[-.72, -1.22], [.72, -1.22], [-.72, -.58], [.72, -.58]].forEach(p => perfil(.05, .72, .05, p[0], .37, p[1], E, material('acoPintado')));
// notebook: base e tampa aberta 15° para trás; a tela (0,32 × 0,20) na face da frente da tampa
const note = new THREE.Group(); note.position.set(0, .775, -.85); E.add(note);
perfil(.34, .018, .24, 0, .009, 0, note, material('plastico'));
const tampa = new THREE.Group(); tampa.position.set(0, .018, -.12); tampa.rotation.x = -THREE.MathUtils.degToRad(15); note.add(tampa);
perfil(.34, .23, .008, 0, .115, 0, tampa, material('plastico'));
S.tela = new THREE.Mesh(new THREE.PlaneGeometry(.32, .2), new THREE.MeshBasicMaterial({color: 0xffffff}));
S.tela.position.set(0, .12, .0045); tampa.add(S.tela);
documento('../site/docs/sige-portal.webp').then(tx => { S.tela.material.map = tx; S.tela.material.needsUpdate = true; });
// folhas reais presas na parede: as fotos da obra e o relatório diário
[['../site/docs/sige-fotos.webp', 1600 / 1353, -1.05], ['../site/docs/sige-rdo.webp', 1600 / 1193, 1.05]].forEach(([url, prop, x]) => {
  const h = .78, folha = new THREE.Mesh(new THREE.PlaneGeometry(h * prop, h), new THREE.MeshStandardMaterial({color: 0xffffff, roughness: .9}));
  folha.position.set(x, 1.6, -1.9); folha.receiveShadow = true; E.add(folha); S.quadros.push(folha);
  documento(url).then(tx => { folha.material.map = tx; folha.material.needsUpdate = true; });
});

// câmera: vista aérea dos dois galpões → escritório → de frente para a tela (última chave calculada: tela exatamente em RETANGULO)
cena.updateMatrixWorld(true);
const centro = S.tela.getWorldPosition(new THREE.Vector3());
const normal = new THREE.Vector3(0, 0, 1).applyQuaternion(S.tela.getWorldQuaternion(new THREE.Quaternion()));
const fim = enquadrarPlano(camera, centro, normal, .32);
const aproximacao = centro.clone().addScaledVector(normal, 1.6);
const cam = trajeto([
  [0, [48, 34, 70], [0, 0, 0]],
  [4, [7, 5, 31], [0, 1.2, 19]],
  [7, aproximacao.toArray(), centro.toArray()],
  [10, fim[0], fim[1]],
]);
publicar(palco, cam, t => {
  S.paineisSubindo.forEach((p, j) => { p.rotation.x = Math.PI / 2 * (1 - rampa(t, .6 + j * .5, 1.8 + j * .5)); });
});
</script>
</body></html>
```

- [ ] **Step 3: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador`
Expected: `OK` e `OK`.

Se `checar_cena_sige` falhar no enquadramento de t=0 ou na névoa, ajuste só a primeira chave de `trajeto` e/ou `nevoa`. Se `checar_passagem` ficar abaixo de 28 dB, confira primeiro que `S.tela` usa `MeshBasicMaterial` e que o GTAO não escurece a tela. Se escurecer, reduza `radius` no kit e rode de novo `checar_kit`. Não baixe o limite.

- [ ] **Step 4: Olhar**

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/eaf52574-a179-46a2-af04-b9d1b2aff72a/scratchpad && python3 - <<'EOF'
import sys; sys.path.insert(0, "portfolio/cenas")
from render import servidor, navegador, abrir_cena
S = "/tmp/claude-1000/-home-runner-workspace/eaf52574-a179-46a2-af04-b9d1b2aff72a/scratchpad"
with servidor() as b, navegador() as n:
    pg, _ = abrir_cena(n, f"{b}/cenas/caso-sige.html")
    for t in (0, 2, 4, 7, 10):
        pg.evaluate(f"renderCena({t})"); pg.screenshot(path=f"{S}/sige-t{t}.png")
EOF
magick $S/sige-t{0,2,4,7,10}.png -resize 30% +append $S/sige-seq.png
```

Abrir `sige-t0.png`, `sige-t4.png`, `sige-t10.png` e `sige-seq.png` com Read e descrever cada um no relatório. Expected:
- t=0: os dois galpões inteiros, terra vermelha, estrutura de aço legível, sombras e céu limpo, sem desbotar;
- t=2: os painéis do B subindo;
- t=4: o escritório com os cones laranja;
- t=7: a mesa com o notebook e as folhas na parede;
- t=10: a tela com o portal nítido ocupando o centro, a moldura do notebook em volta e nenhum texto pintado.

Se algo parecer brinquedo (blocos lisos sem textura, sombra dura, cor lavada), reporte como preocupação com o print. A avaliação estética final é do Cássio, na Task 7.

- [ ] **Step 5: Commit**

```bash
cd /home/runner/workspace && git add portfolio/cenas/caso-sige.html portfolio/tests/check_v2.py && git commit -m "Site v2: cena do caso SIGE (dois galpões de LSF, escritório de obra, notebook com o portal real em RETANGULO no último quadro)

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: O vídeo do caso SIGE

**Files:**
- Create: `portfolio/site/video/v2-sige.mp4`, `portfolio/site/video/v2-sige.webp`
- Modify: `portfolio/tests/check_v2.py` (`checar_video`)

**Interfaces:**
- Consumes: `render.py` (`CENAS["sige"]`, `publicar`, `psnr`, `quadros`, `TETO_CLIPE`, `TETO_POSTER`); `caso-sige.html` (Task 4)
- Produces: `site/video/v2-sige.mp4` (240 quadros, 10 s) e `v2-sige.webp`, usados pela página na Task 6

- [ ] **Step 1: Teste que falha**

Em `check_v2.py`, acrescentar:

```python
def checar_video():
    """Vídeo publicado de cada caso de CENAS: 1920×1080, 24 fps, High 4.0, sem áudio, quadros = dur × 24, ≤ 2,5 MB;
    pontas paradas (PSNR ≥ 45 dB entre os dois primeiros e entre os dois últimos quadros); pôster ≤ 150 KB e
    PSNR ≥ 40 dB contra o último quadro."""
    import render
    for caso, (_arq, dur) in render.CENAS.items():
        mp4, cartaz = SITE / "video" / f"v2-{caso}.mp4", SITE / "video" / f"v2-{caso}.webp"
        check(mp4.exists() and cartaz.exists(), f"vídeo {caso}: v2-{caso}.mp4/.webp ausentes (rodar render.py --so {caso})")
        if not (mp4.exists() and cartaz.exists()):
            continue
        info = ffprobe(mp4)
        v = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
        check(not [s for s in info.get("streams", []) if s.get("codec_type") == "audio"], f"vídeo {caso}: tem áudio")
        check(v and (v[0]["width"], v[0]["height"], v[0].get("r_frame_rate"), v[0].get("profile"), v[0].get("level")) == (1920, 1080, "24/1", "High", 40),
              f"vídeo {caso}: {v and (v[0]['width'], v[0]['height'], v[0].get('r_frame_rate'), v[0].get('profile'), v[0].get('level'))}")
        n = render.quadros(dur)
        check(v and v[0].get("nb_frames") == str(n), f"vídeo {caso}: {v and v[0].get('nb_frames')} quadros, esperava {n}")
        check(mp4.stat().st_size <= render.TETO_CLIPE, f"vídeo {caso}: {mp4.stat().st_size / 1024 / 1024:.2f} MB > 2,5 MB")
        check(cartaz.stat().st_size <= render.TETO_POSTER, f"vídeo {caso}: pôster {cartaz.stat().st_size // 1024} KB > 150 KB")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            q = {}
            for k in (0, 1, n - 2, n - 1):
                q[k] = tmp / f"q{k}.png"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", f"select='eq(n,{k})'", "-vframes", "1", str(q[k])], check=True)
            check(render.psnr(q[0], q[1]) >= 45, f"vídeo {caso}: o início não está parado")
            check(render.psnr(q[n - 2], q[n - 1]) >= 45, f"vídeo {caso}: o fim não está parado")
            check(render.psnr(cartaz, q[n - 1]) >= 40, f"vídeo {caso}: o pôster não é o último quadro (PSNR < 40 dB)")
```

Em `main`: `if "--video" in sys.argv: checar_video()`.

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py --video`
Expected: `FALHOU:` com `vídeo sige: v2-sige.mp4/.webp ausentes`.

- [ ] **Step 2: Renderizar**

Run: `cd /home/runner/workspace && python3 portfolio/cenas/render.py --so sige`
Expected: `sige-mestre.mp4: 240 quadros`, `sige: NNNN KB (crf NN)` com NNNN ≤ 2560, `pronto: …`. Pode levar mais de 10 minutos em CPU; rode em primeiro plano, com timeout longo.

- [ ] **Step 3: Ver passar e olhar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py --video`
Expected: `OK`.

```bash
cd /home/runner/workspace && S=/tmp/claude-1000/-home-runner-workspace/eaf52574-a179-46a2-af04-b9d1b2aff72a/scratchpad && for N in 0 60 110 170 239; do ffmpeg -y -loglevel error -i portfolio/site/video/v2-sige.mp4 -vf "select='eq(n,$N)'" -vframes 1 -update 1 $S/v2s-$N.png; done && magick $S/v2s-{0,60,110,170,239}.png -resize 25% +append $S/v2s-seq.png
```

Abrir `v2s-seq.png` e `v2s-239.png` com Read. Expected:
- o mesmo percurso da Task 4, sem blocos de compressão visíveis na tela do portal;
- no quadro 239, o "44.7%" legível.

Se o texto do portal borrar pela compressão, suba a qualidade (crf menor dentro do teto). Se não couber em 2,5 MB, reporte DONE_WITH_CONCERNS com o tamanho: o teto é revisável no piloto (spec §7.1).

- [ ] **Step 4: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/video/v2-sige.mp4 portfolio/site/video/v2-sige.webp portfolio/tests/check_v2.py && git commit -m "Site v2: vídeo do caso SIGE (1920×1080, 10 s, pontas paradas) e checar_video

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: A página do piloto (`v2.html`, `v2.js`)

**Files:**
- Create: `portfolio/site/v2.html`, `portfolio/site/v2.js`
- Modify: `portfolio/tests/check_v2.py` (`checar_pagina_estatica`, `checar_pagina`, `checar_viewports`, `checar_sem_range`, `checar_celular`)

**Interfaces:**
- Consumes: `clipes.js` (sem mudança); `video/v2-sige.mp4`/`.webp` (Task 5); `docs/sige-portal.webp`, `docs/sige-portal-recorte.webp`, `docs/destaques.json` (Task 3); `RETANGULO` (Task 1): 20% / 16,6667% / 60% / 66,6667%
- Produces: `v2.js` define as variáveis CSS `--doc`, `--destaque` e `--lado` (0..1) em cada `.caso` e chama `fig.__clipe.seek(min(1, p/0,5) × dur)`. Estrutura de um caso:
  `section.caso.cena#<id>[data-caso]` > `.palco` > `.quadro` > (`figure.clipe` + `.doc` > (`img` + `span.destaque`)); e `section` > `.texto` > (`.rotulo`, `h2.manchete`, `p.apoio`, `figure.recorte`, `p.caso-link`)

- [ ] **Step 1: Testes que falham**

Em `check_v2.py`, acrescentar:

```python
PAGINA = SITE / "v2.html"
PROIBIDOS = ["27×", "≈ 27", "≈27", "2 dias úteis", "dois dias úteis", "Kabod", "Santa Mônica", "UPA", "Bertioga", "203.1809",
             "número não sumir", "Não falta obra feita", "número sem origem"]
RETANGULO_CSS = "left:20%;top:16.6667%;width:60%;height:66.6667%"


def texto_visivel(html_):
    import html as h
    html_ = re.sub(r"<(script|style)\b.*?</\1>", " ", html_, flags=re.S)
    return " ".join(h.unescape(re.sub(r"<[^>]+>", " ", html_)).split())


def checar_pagina_estatica():
    """v2.html: textos aprovados; regras de texto (§5); proibidos; documentos com width/height reais; .doc em RETANGULO;
    destaque em % igual ao destaques.json; figure.clipe apontando para o vídeo publicado com a duração de CENAS."""
    import render
    check(PAGINA.exists(), "página: portfolio/site/v2.html não existe")
    if not PAGINA.exists():
        return
    p = PAGINA.read_text(encoding="utf-8")
    vis = texto_visivel(p)
    check("Orço obras, acompanho a execução e construí os sistemas que uso para isso." in vis, "página: frase da abertura ausente")
    manchetes = [texto_visivel(m) for m in re.findall(r'<h2 class="manchete"[^>]*>(.*?)</h2>', p, re.S)]
    apoios = [texto_visivel(m) for m in re.findall(r'<p class="apoio"[^>]*>(.*?)</p>', p, re.S)]
    check(manchetes == ["Implantei a gestão de obra em dois galpões com 22 baias."], f"página: manchetes {manchetes}")
    check(apoios == ["Depois de 11/08 o diário ficou 23 dias só no WhatsApp. Recuperado, o avanço passou de 27,6% para 44,7%, lido numa cópia do sistema."],
          f"página: apoios {apoios}")
    for m in manchetes:
        check(len(m.split()) <= 12 and re.search(r"\d", m), f"página: manchete fora da regra (≤ 12 palavras, com número): {m!r}")
    for a in apoios:
        check(len(a.split()) <= 30, f"página: apoio com {len(a.split())} palavras (máx. 30)")
    for proibido in PROIBIDOS:
        check(proibido not in vis, f"página: texto proibido {proibido!r}")
    check(re.search(r"\bItu\b", vis) is None, "página: nome do município do cliente (Itu)")
    for src, w, h in re.findall(r'<img src="(docs/[^"]+)" width="(\d+)" height="(\d+)"', p):
        check(dims(SITE / src) == (int(w), int(h)), f"página: {src} com width/height {w}×{h} ≠ arquivo {dims(SITE / src)}")
    check(f'class="doc" style="{RETANGULO_CSS}"' in p, "página: .doc fora de RETANGULO (left:20%;top:16.6667%;width:60%;height:66.6667%)")
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))["sige-portal"]
    x, y, w, h = dest["destaque"]
    esperado = f"left:{x / dest['largura']:.4%};top:{y / dest['altura']:.4%};width:{w / dest['largura']:.4%};height:{h / dest['altura']:.4%}"
    check(f'class="destaque" style="{esperado}"' in p, f"página: destaque ≠ destaques.json (esperava style=\"{esperado}\")")
    dur = render.CENAS["sige"][1]
    check(f'<figure class="clipe" data-clipe="video/v2-sige.mp4" data-dur="{dur:g}" aria-hidden="true">' in p, "página: figure.clipe do caso SIGE")
    check('<script src="clipes.js" defer></script>' in p and '<script src="v2.js" defer></script>' in p, "página: scripts clipes.js e v2.js")


def abrir_pagina(nav, base, largura, altura, **kw):
    ctx = nav.new_context(viewport={"width": largura, "height": altura}, **kw)
    pg = ctx.new_page()
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: erros.append(f"{r.status} {r.url}") if r.status >= 400 else None)
    pg.goto(f"{base}/site/v2.html")
    pg.wait_for_load_state("load")
    return ctx, pg, erros


def rolar(pg, caso, p):
    """Rola até o progresso p (0..1) do caso e espera dois quadros de animação."""
    pg.evaluate(f"""(function(){{var c=document.getElementById('{caso}'),r=c.getBoundingClientRect();
      scrollTo(0,scrollY+r.top+{p}*(c.offsetHeight-innerHeight));}})()""")
    pg.evaluate("new Promise(function(r){requestAnimationFrame(function(){requestAnimationFrame(r);});})")


def caixas(pg, caso):
    return pg.evaluate(f"""(function(){{var c=document.getElementById('{caso}'),f=function(s){{var e=c.querySelector(s);if(!e)return null;
      var r=e.getBoundingClientRect();return [r.left,r.top,r.width,r.height,getComputedStyle(e).opacity,getComputedStyle(e).display];}};
      return {{quadro:f('.quadro'),doc:f('.doc'),dest:f('.destaque'),texto:f('.texto'),recorte:f('.recorte img'),img:f('.doc img')}};}})()""")


def checar_alinhado(b, nome):
    """O .doc ocupa RETANGULO do .quadro (as duas caixas já incluem o transform): ±1,5 px em cada lado."""
    q, d = b["quadro"], b["doc"]
    ref = [q[0] + .2 * q[2], q[1] + q[3] / 6, .6 * q[2], 2 * q[3] / 3]
    for nome_eixo, achado, esperado in zip(("left", "top", "width", "height"), d[:4], ref):
        check(abs(achado - esperado) <= 1.5, f"{nome}: .doc fora de RETANGULO em {nome_eixo} ({achado:.1f} ≠ {esperado:.1f})")


def checar_pagina():
    """1920×1080 com Range: sem erros nem 404; em p=0,25 o vídeo busca 5 s e mostra quadro (.viva); em p=0,25 o documento
    está invisível; em p=1 o documento, o destaque e o texto estão visíveis, o documento em RETANGULO, o destaque
    dentro do documento, a imagem real nunca ampliada, e o texto não cobre o documento."""
    from render import navegador, servidor
    with servidor() as base, navegador() as nav:
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080)
        check(pg.evaluate("document.documentElement.classList.contains('js-v2')"), "página: v2.js não ligou .js-v2")
        rolar(pg, "sige", .25)
        pg.wait_for_function("document.querySelector('#sige figure.clipe').classList.contains('viva')", timeout=20000)
        t = pg.evaluate("document.querySelector('#sige video').currentTime")
        check(abs(t - 5.0208) < .05, f"página: em p=0,25 o vídeo está em {t:.3f} s, esperava 5,021 s")
        b = caixas(pg, "sige")
        check(float(b["doc"][4]) == 0, f"página: em p=0,25 o documento já aparece (opacidade {b['doc'][4]})")
        rolar(pg, "sige", 1)
        b = caixas(pg, "sige")
        check(float(b["doc"][4]) == 1 and float(b["dest"][4]) == 1 and float(b["texto"][4]) == 1, f"página: em p=1 opacidades {b['doc'][4]}, {b['dest'][4]}, {b['texto'][4]}")
        checar_alinhado(b, "página 1920×1080")
        d, s = b["doc"], b["dest"]
        check(d[0] <= s[0] and d[1] <= s[1] and s[0] + s[2] <= d[0] + d[2] and s[1] + s[3] <= d[1] + d[3], "página: destaque fora do documento")
        check(b["img"][2] <= 1600, f"página: documento exibido com {b['img'][2]:.0f} px, acima dos 1600 px do arquivo (ampliado)")
        check(b["texto"][0] >= d[0] + d[2] + 16, "página: o texto cobre o documento em 1920×1080")
        check(not erros, f"página: erros/404: {erros}")
        ctx.close()


def checar_viewports():
    """Viewports fora de 16:9: documento em RETANGULO, inteiro na tela, texto sem cobrir o documento, em p=1."""
    from render import navegador, servidor
    with servidor() as base, navegador() as nav:
        for w, h in ((1366, 768), (2560, 1080), (1280, 1024)):
            ctx, pg, erros = abrir_pagina(nav, base, w, h)
            rolar(pg, "sige", 1)
            b = caixas(pg, "sige")
            checar_alinhado(b, f"página {w}×{h}")
            d = b["doc"]
            check(d[0] >= 0 and d[1] >= 0 and d[0] + d[2] <= w and d[1] + d[3] <= h, f"página {w}×{h}: documento sai da tela {d[:4]}")
            check(b["texto"][0] >= d[0] + d[2] + 16, f"página {w}×{h}: o texto cobre o documento")
            check(b["img"][2] <= 1600, f"página {w}×{h}: documento ampliado")
            check(not erros, f"página {w}×{h}: erros/404: {erros}")
            ctx.close()


def checar_sem_range():
    """Servidor sem Range: o clipe congela no pôster (sem .viva); documento, destaque e texto aparecem alinhados em p=1."""
    from render import navegador, servidor
    with servidor(com_range=False) as base, navegador() as nav:
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080)
        rolar(pg, "sige", .25)
        pg.wait_for_timeout(3000)
        check(not pg.evaluate("document.querySelector('#sige figure.clipe').classList.contains('viva')"), "sem Range: o clipe não congelou no pôster")
        rolar(pg, "sige", 1)
        b = caixas(pg, "sige")
        check(float(b["doc"][4]) == 1 and float(b["dest"][4]) == 1, "sem Range: documento/destaque invisíveis em p=1")
        checar_alinhado(b, "sem Range")
        ctx.close()


def checar_celular():
    """390×844: sem o documento inteiro (display none); o recorte visível, inteiro na tela em p=1 e nunca ampliado;
    movimento reduzido: sem .js-v2, pôster, documento e destaque visíveis; sem JS: manchete e documento visíveis."""
    from render import navegador, servidor
    with servidor() as base, navegador() as nav:
        ctx, pg, erros = abrir_pagina(nav, base, 390, 844, device_scale_factor=2, is_mobile=True, has_touch=True)
        rolar(pg, "sige", 1)
        b = caixas(pg, "sige")
        check(b["doc"][5] == "none", "celular: o documento inteiro aparece (ilegível em 390 px)")
        r = b["recorte"]
        check(r and r[5] != "none" and r[0] >= 0 and r[1] >= 0 and r[0] + r[2] <= 390 and r[1] + r[3] <= 844, f"celular: recorte fora da tela {r}")
        check(r and r[2] <= 800, "celular: recorte ampliado")
        check(not erros, f"celular: erros/404: {erros}")
        ctx.close()
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080, reduced_motion="reduce")
        check(not pg.evaluate("document.documentElement.classList.contains('js-v2')"), "movimento reduzido: .js-v2 ligado")
        b = caixas(pg, "sige")
        check(float(b["doc"][4]) == 1 and float(b["dest"][4]) == 1, "movimento reduzido: documento/destaque invisíveis")
        check(pg.evaluate("getComputedStyle(document.querySelector('#sige video')).display") == "none", "movimento reduzido: o vídeo aparece")
        ctx.close()
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080, java_script_enabled=False)
        b = caixas(pg, "sige")
        check(float(b["doc"][4]) == 1 and pg.is_visible("#sige h2.manchete"), "sem JS: manchete ou documento invisíveis")
        ctx.close()
```

Em `main`: chamar `checar_pagina_estatica()` no estático; dentro de `--navegador`, depois de `checar_passagem()`, chamar `checar_pagina()`, `checar_viewports()`, `checar_sem_range()` e `checar_celular()`.

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py`
Expected: `FALHOU:` com `página: portfolio/site/v2.html não existe`.

- [ ] **Step 2: `v2.js`**

Criar `portfolio/site/v2.js`:

```js
// Site v2: cada caso tem três tempos na rolagem. Na 1ª metade o vídeo da cena anda com o scroll (clipes.js busca o
// quadro); na 2ª o documento real aparece sobre a tela do último quadro (--doc), o destaque se desenha (--destaque)
// e o quadro abre espaço para o texto (--lado). Sem JS, sem IntersectionObserver ou com movimento reduzido: nada disso,
// e a página fica empilhada (pôster + documento + destaque + texto), porque o CSS parte de --doc = --destaque = 1.
(function(){
'use strict';
if(!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
var casos=[].slice.call(document.querySelectorAll('.caso'));
if(!casos.length)return;
document.documentElement.classList.add('js-v2');
var CENA=.5,DOC=[.5,.6],DESTAQUE=[.6,.7],LADO=[.62,.72],pendente=false;
function faixa(p,f){return Math.max(0,Math.min(1,(p-f[0])/(f[1]-f[0])));}
function atualizar(){
  pendente=false;
  casos.forEach(function(c){
    var r=c.getBoundingClientRect(),curso=c.offsetHeight-innerHeight;
    if(r.bottom<-innerHeight||r.top>2*innerHeight)return;
    var p=curso>0?Math.max(0,Math.min(1,-r.top/curso)):1;
    var fig=c.querySelector('figure.clipe');
    if(fig&&fig.__clipe)fig.__clipe.seek(Math.min(1,p/CENA)*fig.__clipe.dur);
    c.style.setProperty('--doc',faixa(p,DOC));
    c.style.setProperty('--destaque',faixa(p,DESTAQUE));
    c.style.setProperty('--lado',faixa(p,LADO));
  });
}
function pedir(){if(!pendente){pendente=true;requestAnimationFrame(atualizar);}}
addEventListener('scroll',pedir,{passive:true});
addEventListener('resize',pedir);
pedir();
})();
```

- [ ] **Step 3: `v2.html`**

Criar `portfolio/site/v2.html`:

```html
<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Cássio Viller — orçamento, planejamento e custos de obra</title>
<meta name="description" content="Cássio Viller, estudante de Engenharia Civil (7º semestre): orçamento, planejamento e custos de obra. Casos reais com os documentos produzidos.">
<meta name="theme-color" content="#12171D">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{
  --ground:#ECEBE6; --surface:#FFFFFF; --ink:#171F29; --ink-2:#3C4652; --muted:#5B6672;
  --accent:#B5440E; --accent-ink:#FFFFFF; --rule:#D3D1CA;
  --palco:#0F1419; --texto-palco:#F2F1EC; --apoio-palco:#D4DCE4; --laranja:#F07A3E;
  --display:"Barlow Condensed","Arial Narrow",Impact,sans-serif;
  --body:"IBM Plex Sans","Helvetica Neue",Arial,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){--ground:#12171D; --surface:#1A2129; --ink:#E9E7E1; --ink-2:#C4C8CC; --muted:#93A0AD; --accent:#F07A3E; --accent-ink:#161616; --rule:#2E3A47;}
}
:root[data-theme="dark"]{--ground:#12171D; --surface:#1A2129; --ink:#E9E7E1; --ink-2:#C4C8CC; --muted:#93A0AD; --accent:#F07A3E; --accent-ink:#161616; --rule:#2E3A47;}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--body);font-size:17px;line-height:1.6;-webkit-font-smoothing:antialiased}
img{display:block;max-width:100%;height:auto}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.pular{position:absolute;left:-9999px;top:8px;z-index:50;background:var(--accent);color:var(--accent-ink);padding:10px 14px;font-family:var(--mono);font-size:.8rem}
.pular:focus{left:12px}
.barra{position:sticky;top:0;z-index:30;display:flex;flex-wrap:wrap;align-items:center;gap:6px 18px;padding:10px 20px;background:var(--ground);border-bottom:1px solid var(--rule);font-family:var(--mono);font-size:.8rem}
.barra .nome{font-family:var(--display);font-weight:700;font-size:1.15rem;text-transform:uppercase;color:var(--ink);text-decoration:none}
.barra nav{display:flex;flex-wrap:wrap;gap:6px 16px;flex:1 1 auto}
.barra a{color:var(--ink)}
.abertura,.fechamento{max-width:62rem;margin:0 auto;padding:10vh 20px}
.abertura h1{font-family:var(--display);font-size:clamp(2.6rem,7vw,5rem);line-height:1;margin:0 0 .25em;text-transform:uppercase}
.vaga{font-size:1.35rem;font-weight:500;margin:0 0 .6em}
.posicionamento{font-size:1.15rem;color:var(--ink-2);max-width:42rem;margin:0}
.ficha{list-style:none;padding:0;margin:1.2em 0;color:var(--ink-2)}
.contato{display:flex;flex-wrap:wrap;gap:10px 18px;margin:0}
.contato a{color:var(--ink)}
.contato .zap{background:var(--accent);color:var(--accent-ink);padding:8px 12px;text-decoration:none;border-radius:2px}
.fechamento h2{font-family:var(--display);font-size:2rem;margin:0 0 .5em}
.fechamento ul{padding-left:1.1em;margin:0 0 1.2em}
/* caso, sem JS ou com movimento reduzido: quadro (pôster + documento + destaque) e texto empilhados */
.caso{position:relative;background:var(--palco)}
.palco{position:relative;overflow:hidden}
.quadro{position:relative;width:100%;aspect-ratio:16/9}
.clipe{position:absolute;inset:0;margin:0}
.clipe img,.clipe video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.clipe video{opacity:0}
.clipe.viva video{opacity:1}
.clipe.viva img{visibility:hidden;transition:visibility 0s .2s}
.doc{position:absolute;overflow:hidden;opacity:var(--doc,1)}
.doc img{width:100%;height:100%}
.destaque{position:absolute;border:3px solid var(--laranja);border-radius:3px;opacity:var(--destaque,1);transform:scale(calc(1.25 - .25*var(--destaque,1)));box-shadow:0 0 0 200vmax rgba(10,14,18,calc(.38*var(--destaque,1)))}
.texto{padding:28px 20px 48px;max-width:40rem;margin:0 auto;color:var(--texto-palco)}
.rotulo{font-family:var(--mono);font-size:.8rem;color:var(--laranja);margin:0 0 .6em;text-transform:uppercase;letter-spacing:.04em}
.manchete{font-family:var(--display);font-size:clamp(1.9rem,3.2vw,2.8rem);line-height:1.08;margin:0 0 .5em}
.apoio{color:var(--apoio-palco);margin:0 0 1em}
.recorte{display:none;margin:0 0 1em}
.caso-link a{color:var(--texto-palco)}
/* com JS e movimento: o palco fica preso na tela por 300vh; a cena anda na 1ª metade, o documento e o texto na 2ª */
.js-v2 .caso{height:300vh}
.js-v2 .palco{position:sticky;top:0;height:100vh}
.js-v2 .quadro{position:absolute;left:50%;top:50%;width:max(100vw,177.78vh);transform:translate(-50%,-50%) translateX(calc(var(--lado,0)*-13%)) scale(calc(1 - .24*var(--lado,0)))}
.js-v2 .texto{position:absolute;right:4vw;top:50%;width:min(30rem,30vw);transform:translateY(-50%);opacity:var(--lado,0);padding:0;margin:0}
@media (max-aspect-ratio:3/2) and (min-width:761px){.js-v2 .quadro{width:100vw}}
@media (max-width:760px){
  .doc{display:none}
  .recorte{display:block}
  .js-v2 .quadro{transform:translate(-50%,-50%)}
  .js-v2 .texto{left:0;right:0;top:auto;bottom:0;width:auto;transform:none;padding:20px;background:linear-gradient(transparent,rgba(10,14,18,.92) 14%)}
}
@media (prefers-reduced-motion: reduce){.clipe video{display:none}}
</style>
</head>
<body>
<a class="pular" href="#sige">Pular para o caso</a>
<header class="barra">
  <a class="nome" href="#inicio">Cássio Viller</a>
  <nav aria-label="Seções"><a href="#sige">SIGE na obra</a><a href="#contato">Contato</a></nav>
  <a href="curriculo-cassio-viller.pdf">Currículo (PDF)</a>
</header>
<main id="conteudo">
  <section class="abertura" id="inicio">
    <h1>Cássio Viller</h1>
    <p class="vaga">Orçamento, planejamento e custos de obra</p>
    <p class="posicionamento">Orço obras, acompanho a execução e construí os sistemas que uso para isso.</p>
    <ul class="ficha">
      <li>Engenharia Civil, 7º semestre (faltam 3), Cruzeiro do Sul, após 6 semestres na UNIFEI</li>
      <li>São José dos Campos/SP · CLT ou PJ · presencial ou remoto</li>
    </ul>
    <p class="contato"><a class="zap" href="https://wa.me/5512982071116">WhatsApp (12) 98207-1116</a><a href="mailto:cassiovillers@gmail.com">cassiovillers@gmail.com</a><a href="curriculo-cassio-viller.pdf">Currículo (PDF)</a></p>
  </section>

  <section class="caso cena" id="sige" data-caso="sige">
    <div class="palco">
      <div class="quadro">
        <figure class="clipe" data-clipe="video/v2-sige.mp4" data-dur="10" aria-hidden="true">
          <video muted playsinline preload="none" disableremoteplayback width="1920" height="1080"></video>
          <img src="video/v2-sige.webp" alt="" width="1920" height="1080">
        </figure>
        <div class="doc" style="left:20%;top:16.6667%;width:60%;height:66.6667%">
          <img src="docs/sige-portal.webp" width="1600" height="1000" alt="Portal do cliente no SIGE: obra com 44,7% concluído, 109 etapas e 65 relatórios diários; o nome do cliente aparece borrado.">
          <span class="destaque" style="left:6.8750%;top:27.8000%;width:12.5000%;height:7.8000%"></span>
        </div>
      </div>
      <div class="texto">
        <p class="rotulo">SIGE na obra dos galpões · jun → set/2026</p>
        <h2 class="manchete">Implantei a gestão de obra em dois galpões com 22 baias.</h2>
        <p class="apoio">Depois de 11/08 o diário ficou 23 dias só no WhatsApp. Recuperado, o avanço passou de 27,6% para 44,7%, lido numa cópia do sistema.</p>
        <figure class="recorte"><img src="docs/sige-portal-recorte.webp" width="800" height="400" alt="Recorte do portal do cliente: 44,7% concluído, 109 etapas, 65 relatórios."></figure>
        <p class="caso-link"><a href="portfolio.html#sige">Ver o caso completo →</a></p>
      </div>
    </div>
  </section>

  <section class="fechamento" id="contato">
    <h2>O que faço numa construtora</h2>
    <ul>
      <li>Levantamento de quantitativos no projeto</li>
      <li>Orçamento com composições SINAPI e BDI</li>
      <li>Cronograma físico-financeiro com curva S</li>
      <li>Diário de obra e medição</li>
      <li>Compras com cotação e quadro de concorrência</li>
      <li>Fluxo de caixa e custo previsto × realizado</li>
    </ul>
    <p class="contato"><a class="zap" href="https://wa.me/5512982071116">WhatsApp (12) 98207-1116</a><a href="mailto:cassiovillers@gmail.com">cassiovillers@gmail.com</a><a href="curriculo-cassio-viller.pdf">Currículo (PDF)</a><a href="portfolio.html">Portfólio completo</a></p>
  </section>
</main>
<script src="clipes.js" defer></script>
<script src="v2.js" defer></script>
</body>
</html>
```

O `.texto` fica dentro do `.palco`. No modo empilhado (sem JS) ele vem logo abaixo do quadro, e com `.js-v2` passa a sobrepor o palco, à direita.

- [ ] **Step 4: Ver passar**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador`
Expected: `OK` e `OK`.

Se `checar_viewports` acusar o texto cobrindo o documento numa proporção, ajuste só os números de `--lado` no CSS: o `translateX` de -13% e o `scale` de .24. Não mexa em `RETANGULO` nem nos testes. Se o vídeo não chegar a `.viva` em 20 s, confira no relatório se o servidor responde 206 ao Range (`curl -sI -H 'Range: bytes=0-1' <base>/site/video/v2-sige.mp4`).

- [ ] **Step 5: Olhar**

```bash
cd /home/runner/workspace && python3 - <<'EOF'
import sys; sys.path.insert(0, "portfolio/cenas"); sys.path.insert(0, "portfolio/tests")
from render import servidor, navegador
from check_v2 import abrir_pagina, rolar
S = "/tmp/claude-1000/-home-runner-workspace/eaf52574-a179-46a2-af04-b9d1b2aff72a/scratchpad"
with servidor() as b, navegador() as n:
    for (w, h, nome) in ((1920, 1080, "desk"), (390, 844, "cel")):
        ctx, pg, _ = abrir_pagina(n, b, w, h)
        pg.screenshot(path=f"{S}/v2-{nome}-abertura.png")
        for p in (.25, .55, 1):
            rolar(pg, "sige", p)
            try:
                pg.wait_for_function("document.querySelector('#sige figure.clipe').classList.contains('viva')", timeout=15000)
            except Exception:
                pass
            pg.wait_for_timeout(500)
            pg.screenshot(path=f"{S}/v2-{nome}-p{int(p * 100)}.png")
        ctx.close()
EOF
```

Abrir os oito prints com Read. Expected:
- a abertura mostra a ficha inteira na primeira tela;
- em p=25 a cena aparece no meio do percurso;
- em p=55 o documento real surge sobre a tela do notebook, sem salto;
- em p=100 o documento está nítido com a caixa laranja em "44.7%", e o texto está à direita (desktop) ou embaixo, com o recorte (celular).

Descreva cada print no relatório.

- [ ] **Step 6: Commit**

```bash
cd /home/runner/workspace && git add portfolio/site/v2.html portfolio/site/v2.js portfolio/tests/check_v2.py && git commit -m "Site v2: página do piloto (abertura, caso SIGE em três tempos, fechamento) com checagens de alinhamento, viewports, sem Range e celular

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: Documentação e o pacote de aprovação

**Files:**
- Modify: `portfolio/README.md`, `ANDAMENTO.md`, `portfolio/revisao/CHANGELOG.md`
- Modify: `portfolio/tests/check_v2.py` (`checar_readme`)

**Interfaces:**
- Consumes: tudo das Tasks 1–6.

- [ ] **Step 1: Teste que falha**

Em `check_v2.py`:

```python
def checar_readme():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    for trecho in ("site/v2.html", "cenas/render.py --so sige", "cenas/documentos.py", "tests/check_v2.py --navegador"):
        check(trecho in readme, f"README do portfólio sem {trecho!r}")
```

Chamar no estático, em `main`.

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py`
Expected: `FALHOU:` com `README do portfólio sem 'site/v2.html'`.

- [ ] **Step 2: Documentos**

No `portfolio/README.md`, acrescentar no fim:

```markdown

## Site v2 (piloto, 25/09/2026)

Página nova ao lado da história: `site/v2.html` (abertura, caso SIGE na obra dos galpões, fechamento). Cada caso mostra uma cena criada em 3D que leva ao documento real: no fim do vídeo, a imagem real do documento entra exatamente sobre a tela da cena, com o número da manchete destacado em laranja. Spec: `docs/superpowers/specs/2026-09-25-site-v2-design.md`.

- Documentos reais (só de prints já anonimizados): `python3 portfolio/cenas/documentos.py` → `site/docs/`.
- Cena em vídeo 1920×1080: `python3 portfolio/cenas/render.py --so sige` → `site/video/v2-sige.mp4` e `.webp`.
- Conferir: `python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador && python3 portfolio/tests/check_v2.py --video`.
- Ver no navegador: `python3 portfolio/servir.py 5000 --directory portfolio/site` e abrir `/v2.html` (precisa de Range).
```

No `portfolio/revisao/CHANGELOG.md`, no fim:

```markdown

---

# Rodada 11 — piloto do site v2, 25/09/2026

- O site das rodadas 1–10 vira protótipo (branch `historia-cenas-novas`, sem merge). Avaliação do Cássio: cenas com cara de brinquedo, desbotadas e genéricas, sem mostrar os documentos reais; texto enfeitado demais para um currículo.
- Spec `2026-09-25-site-v2-design.md`: abertura, quatro casos fortes, trajetória curta e fechamento; em cada caso, a cena criada leva ao documento real; manchete com fato e número (≤ 12 palavras), sem metáfora.
- Piloto = caso SIGE na obra dos galpões (o caso 1, dos 36 minutos, só tem prints de 760 px; espera os originais). Kit novo das cenas (three.js 0.186, GTAO, ambiente, render 2×, 1920×1080), documentos em `site/docs/`, página `site/v2.html`, checagens em `tests/check_v2.py`.
```

No `ANDAMENTO.md`, no fim:

```markdown

## Estado em 25/09/2026 — site v2, fase 1 (piloto) CONCLUÍDA, aguardando aprovação do Cássio
- Branch `site-v2`; spec `docs/superpowers/specs/2026-09-25-site-v2-design.md`; plano `docs/superpowers/plans/2026-09-25-site-v2-piloto.md`.
- O protótipo (16 capítulos) está no branch `historia-cenas-novas`, sem merge em `main`.
- Conferir: `python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador && python3 portfolio/tests/check_v2.py --video`.
- Próximo: o Cássio aprova (ou corrige) o padrão visual do piloto; depois a fase 2 (casos 2 e 4, caso 1 com os originais, abertura com cena, `v2.html` vira `index.html`).
```

- [ ] **Step 3: Suíte inteira**

Run: `cd /home/runner/workspace && python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador && python3 portfolio/tests/check_v2.py --video && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_site.py`
Expected: `OK` cinco vezes. O protótipo continua intacto: `check_historia` e `check_site` não mudam.

- [ ] **Step 4: Commit**

```bash
cd /home/runner/workspace && git add portfolio/README.md ANDAMENTO.md portfolio/revisao/CHANGELOG.md portfolio/tests/check_v2.py && git commit -m "Site v2: README, changelog da rodada 11 e retomada do piloto

Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>"
```

O pacote de aprovação fica com o controlador, depois da revisão final: os prints da Task 6, Step 5, e o site rodando na porta 5000 em `/v2.html`, mostrados ao Cássio. Os casos 2–4 só começam depois do "aprovado" dele.

---

## Self-review

- **Cobertura do spec (fase 1):**
  - §6, os três tempos: Task 6 (`v2.js`, CSS) e Task 4 (a tela em RETANGULO);
  - §6, o celular e o movimento reduzido: `checar_celular`;
  - §7.1, 1920×1080: Tasks 2 e 5;
  - §7.2, o assunto ≥ 60% e o documento a ±2 px: `checar_cena_sige`;
  - §7.3, a névoa: `checar_cena_sige`;
  - §7.4, materiais, luz e AO: Task 1 (`checar_kit`), com ACES trocado por `NoToneMapping` (decisão 2 do plano, justificada pela passagem do §6);
  - §7.5, a escala real: os perfis de LSF a cada 40 cm na Task 4;
  - §7.6, o acento e o texto pintado: `checar_cena_estatica`;
  - §7.7, o documento como textura, nunca ampliado: Tasks 4 e 6;
  - §8, documentos e anonimização: Task 3 (`LIBERADOS`);
  - §9.1–9.6: `checar_video`, `checar_cena_sige`, `checar_pagina*`, `checar_pagina_estatica`, `checar_documentos`;
  - §10, piloto e aprovação: Task 7.
- **Fora da fase 1 por desenho:** as cenas da abertura, dos casos 1, 2 e 4, a trajetória, o `index.html` e a revisão do `portfolio.html` e do currículo.
- **Nomes consistentes:**
  - `RETANGULO` (kit) ↔ `RETANGULO_CSS` e `checar_alinhado` (testes) ↔ o `style` do `.doc`;
  - `CENAS["sige"] = ("caso-sige.html", 10.0)` ↔ `data-dur="10"`;
  - `window.__palco` / `window.__cena` ↔ os testes das Tasks 1 e 4;
  - `destaques.json` ↔ o `style` do `.destaque` (6,875% / 27,8% / 12,5% / 7,8%).
- **Review Focus → testes:**
  1. `checar_viewports`;
  2. `checar_sem_range`;
  3. `checar_passagem`;
  4. `checar_pagina_estatica` (width/height iguais ao arquivo);
  5. `checar_celular`.
