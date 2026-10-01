# Render local na GPU (Windows + RTX 3060)

Instruções para uma sessão do Claude Code no PC do Cássio. O site, as cenas e os testes são montados no Replit; aqui só
se renderizam os vídeos das cenas em qualidade alta e se devolvem para o GitHub. No Replit o render roda no SwiftShader
(CPU, ≈ 1 h por cena, qualidade normal); na placa de vídeo leva minutos e a qualidade alta fica viável.

## O que muda na qualidade alta (`cenas/kit.js`, `?q=alta`)
| | normal (Replit) | alta (GPU) |
|---|---|---|
| buffer do quadro | 3840×2160, reduzido 2×2 | 7680×4320, reduzido 4×4 |
| mapa de sombra do sol | 4096 | 8192 |
| amostras do GTAO | 16 | 32 |

O vídeo publicado continua 1920×1080, 24 fps, H.264, dentro de 2,5 MB (o `render.py` escolhe o crf).

## 1. Preparar o PC (uma vez)
Em PowerShell:
```powershell
winget install -e --id Git.Git
winget install -e --id Python.Python.3.12
winget install -e --id Gyan.FFmpeg
# feche e abra o terminal para o PATH valer
python -m pip install playwright==1.63.0
python -m playwright install chromium
git clone https://github.com/cassioviller/AxiomTech.git
cd AxiomTech
git checkout site-v2-fase-2
```
Conferir: `ffmpeg -version` e `python -c "import playwright"` sem erro. Driver da NVIDIA atualizado.

## 2. Renderizar
Sempre a partir da raiz do repositório, com UTF-8 no console (as mensagens têm acentos e "×"):
```powershell
$env:PYTHONUTF8 = "1"
git pull
python portfolio/cenas/render.py --gpu --qualidade alta --so modulares
```
- Casos: `abertura`, `veks`, `sige`, `modulares`; sem `--so` renderiza os quatro em sequência.
- Abre uma janela do Chromium (é proposital: o headless pode cair no SwiftShader). Não feche a janela; minimizar
  não atrapalha (o render não depende da animação da página).
- A primeira linha mostra a placa: `modulares: qualidade alta, WebGL em ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 …)`.
  Se aparecer SwiftShader/llvmpipe, o script para com erro: atualizar o driver; se continuar, conferir em
  `chrome://gpu` na janela aberta.
- Se cair no meio, rodar o mesmo comando: os quadros prontos ficam em `portfolio/cenas/saida/<caso>-alta-mestre-quadros/`
  e o render retoma do primeiro que falta.
- Erro "buffer … não é múltiplo inteiro de 1920x1080": a placa limitou o tamanho do canvas; avisar no commit e
  usar `--qualidade normal` (com `--gpu`, ainda bem mais rápido que no Replit).

Saídas: `portfolio/site/video/v2-<caso>.mp4` e `v2-<caso>.webp` (pôster). O mestre (`portfolio/cenas/saida/`) fica
fora do git.

## 3. Conferir e devolver
```powershell
python portfolio/tests/check_v2.py --video
git status --short
```
Só os arquivos `portfolio/site/video/v2-*.mp4` e `v2-*.webp` devem aparecer como modificados. Ver o pôster
(`v2-<caso>.webp`): a prancha/documento inteiro e nítido no centro. Depois:
```powershell
git add portfolio/site/video/v2-*.mp4 portfolio/site/video/v2-*.webp
git commit -m "Site v2: vídeo do caso <caso> renderizado na GPU (qualidade alta)"
git push origin site-v2-fase-2
```
No Replit, o Claude faz `git pull` e confere o site na porta 5000.

## Observações
- Não rodar `cenas/documentos.py` aqui: ele precisa dos zips com os originais, que ficam fora do git. Os documentos
  já recortados estão em `portfolio/site/docs/`.
- Os testes de cena (`check_v2.py --navegador`) foram calibrados no SwiftShader do Replit; no PC basta o `--video`.
