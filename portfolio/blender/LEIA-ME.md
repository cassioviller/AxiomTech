# Render realista no Blender (Cycles na RTX 3060)

Para a sessão do Claude Code no PC do Cássio (Windows). As cenas continuam sendo escritas em three.js
(`portfolio/cenas/*.html`); aqui elas são exportadas quadro a quadro e renderizadas no Cycles com luz indireta, céu
fotográfico (HDRI) e texturas fotografadas CC0. Pesquisa e decisões: `docs/superpowers/specs/2026-10-01-render-realista.md`.

```
cenas/exportar.py  →  cenas/saida/export/<caso>/cena.json   (geometria, materiais, pose de cada malha e da câmera por quadro)
blender/baixar_assets.py  →  blender/assets/                (HDRI e texturas do Poly Haven, CC0; lista em assets.json)
blender/montar.py (dentro do Blender)  →  cenas/saida/<caso>-blender-quadros/q0000.png…
cenas/render.py --quadros <pasta> --so <caso>  →  site/video/v2-<caso>.mp4 e .webp
```

## 1. Preparar (uma vez)
Além do que está em `cenas/RENDER-LOCAL.md` (git, Python, ffmpeg, Playwright):
```powershell
winget install -e --id BlenderFoundation.Blender.LTS   # precisa ser a 5.2 LTS (testado na 5.2.2); conferir: blender --version
```
Se `blender` não entrar no PATH, usar o caminho completo (`"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"`).
Driver da NVIDIA 575 ou mais novo (OptiX).

## 2. Piloto: caso 4 (modulares)
```powershell
$env:PYTHONUTF8 = "1"
python portfolio/blender/baixar_assets.py                 # ≈ 100 MB, confere md5; só baixa o que falta
python portfolio/cenas/exportar.py --so modulares         # segundos; não usa a placa
# três quadros de conferência antes do render inteiro (começo, meio, fim):
blender -b -P portfolio/blender/montar.py -- --caso modulares --quadros 0-287:140 --saida portfolio/cenas/saida/modulares-teste
# olhar os PNGs; se estiverem bons, o vídeo inteiro (288 quadros; retoma de onde parou se cair):
blender -b -P portfolio/blender/montar.py -- --caso modulares
python portfolio/cenas/render.py --quadros portfolio/cenas/saida/modulares-blender-quadros --so modulares
python portfolio/tests/check_v2.py --video
```
- A primeira linha útil deve ser `Cycles em NVIDIA GeForce RTX 3060`. Se o script parar com "nenhuma placa
  encontrada", tentar `--dispositivo CUDA`; `--dispositivo CPU` funciona, mas leva minutos por quadro.
- Anotar no `ANDAMENTO.md` o tempo por quadro medido (não há medição ainda na 3060).
- Qualidade: `--amostras 256` é o padrão; 512 se sobrar ruído nas sombras. O ruído é o mesmo em todos os quadros
  (semente fixa) para o que sobrar do denoise não cintilar.

## 3. O que conferir nos quadros (e o que ainda falta)
Estado do `montar.py` em 01/10/2026: testado no Replit em CPU (Blender 5.2.2): três quadros do caso modulares a
960×540 com 48 amostras (≈ 30 s por quadro em 4 núcleos); os quatro casos exportam e montam sem erro, mas só o
modulares foi renderizado. **Nunca rodou em GPU.** Ainda não foi feito, e é o próximo passo depois do piloto:
- **Árvores e capim reais**: as árvores do kit (esferas) vão como estão; o exportador já marca cada uma (`arvores` no
  `cena.json`, com posição e escala) para trocar por modelos do Poly Haven.
- **Caminhão, guindaste e móveis** continuam os procedurais do kit (não há equivalente CC0 baixável por script).
- **Cores do documento**: o documento-alvo (emissão pura) fica fora da curva AgX na composição (`compor()`), então
  sai com o branco e as cores da imagem; conferir mesmo assim a passagem do último quadro para o documento da página.
- **Interiores (`abertura`, `veks`)**: só o sol/céu é exportado; as outras luzes do three.js (luminárias, luz de
  preenchimento) não. A sala pode sair escura: renderizar um quadro e, se preciso, somar luzes de área no `montar.py`.
- **Névoa** das cenas externas e as **cores por instância** (teclado da abertura) não são exportadas.
- Materiais sem foto (aço pintado, plástico, papel, folha) usam a cor pintada pelo kit; o aço (`metal_plate`) e a
  madeira podem pedir outra textura: ver os quadros e trocar em `assets.json`.

Trocar uma textura: mudar o id em `assets.json` (ids em polyhaven.com/textures), rodar `baixar_assets.py` de novo.

## 4. Devolver
Commit só dos `portfolio/site/video/v2-*.mp4|webp` (e do `ANDAMENTO.md` com as medições) e push. Os quadros, o
`cena.json` e os assets ficam fora do git.
