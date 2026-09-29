# Portfólio de Cássio Viller

Plano e decisões: `../PLANO.md`. Nada aqui foi publicado nem commitado.

```
curriculo/   curriculo.html → curriculo-cassio-viller.pdf (1 página) + .txt (para colar em portais de vaga)
casos/       3 folhas de caso A4 (HTML → PDF), caso.css compartilhado, mensagens.md (modelos de WhatsApp/e-mail)
site/        site estático: index.html (a história em cenas, página principal; 11 clipes de fundo em video/), portfolio.html (portfólio completo), historia.js, clipes.js, maquetes.js, img/, video/ (cena-*.mp4 + .webp), vendor/ (three.js 0.186), og.png, PDFs
filme/       o filme (film.html + three.js r128): render_clipes.py gera os clipes de fundo; render.py, o trailer de envio (fora do site)
tests/       check_site.py, check_historia.py (--navegador: Chromium headless; --origem URL: Range na origem publicada), check_filme.py (--video), baseline.json
servir.py    servidor estático com Range (HTTP 206): o único em que o vídeo busca pela rolagem
ref/         originais do pacote (site antigo, cena5 aprovada) — só referência
build.sh     regenera todos os PDFs e copia para site/
```

## Usar

- Gerar PDFs: `./build.sh` (precisa de `chromium` e `pdftotext`; as folhas de caso buscam as fontes no Google Fonts).
- Ver o site: `python3 portfolio/servir.py 8000 --directory portfolio/site` → http://localhost:8000
  (precisa de um servidor **com Range**: o `python3 -m http.server` responde 200 sem `Accept-Ranges`, o navegador ignora
  todo seek e a história fica só com os pôsteres; abrir o arquivo direto bloqueia o three.js do portfólio).
- Gerar os clipes de fundo da história: `python3 portfolio/filme/render_clipes.py` (~10 min); conferir: `python3 portfolio/tests/check_filme.py --video`. Detalhes em `filme/README.md`.
- Clipe com o assunto encostado no alto ou no pé do 16:9: classe `foco-alto` / `foco-baixo` na `figure.clipe` (recorte vertical em janelas mais largas que 16:9); `foco-alto` em obra, casa, whatsapp e içamento; `foco-baixo` fica disponível, hoje sem uso (o `escala` ficou sem foco: as miniaturas estão no terço de cima). O palco começa abaixo da barra fixa (`--barra`, medida pelo `historia.js` por `ResizeObserver`: fontes, quebra de linha, janela).
- Conferir um quadro de uma maquete: `?maquete=forcar&t=12` na URL congela a cena no segundo 12 e ignora a guarda de fps.

## Antes de publicar

1. Preencher no `curriculo/curriculo.html` os dois `[confirmar URL]` (LinkedIn e portfólio) e rodar `./build.sh`.
2. No `site/index.html` e no `site/portfolio.html`: trocar `og:image` para URL absoluta (`https://dominio/og.png`) — o WhatsApp exige; incluir o
   link do LinkedIn onde está o comentário `<!-- LinkedIn: ... -->`.
3. Confirmar com a VEKS o que pode ser mostrado (valores de proposta, imagens de projeto, o bunker).
4. Testar as maquetes num Android médio de verdade. A guarda automática volta para a imagem estática abaixo de ~24 fps,
   mas isso só foi testado em renderização por software, não em aparelho.
5. Conferir que a origem publicada responde 206 a `Range` nos clipes: `python3 portfolio/tests/check_historia.py --origem https://<domínio>` (sem 206 a história mostra só os pôsteres — não quebra, mas perde o movimento).

## Regras de conteúdo (valem para qualquer edição)

Só números do site original / brief. Clientes sempre genéricos. Nunca: margens ou percentuais de ex-contratante,
salários, valores de contrato, endereço, nascimento, CPF/CNPJ, nomes de pessoas. `ref/img-nao-usadas/o1.webp` e `o2.webp` mostram
o nome do cliente da unidade de saúde — não usar; (foram tirados de `site/img/` para não irem junto na publicação).

## Site v2 (piloto, 25–29/09/2026)

Página nova ao lado da história: `site/v2.html` (abertura, caso SIGE na obra dos galpões, fechamento). Cada caso mostra uma cena criada em 3D que leva ao documento real: no fim do vídeo, a imagem real do documento entra exatamente sobre a tela da cena, com o número da manchete destacado em laranja. Spec: `docs/superpowers/specs/2026-09-25-site-v2-design.md`.

- Documentos reais (só de prints já anonimizados): `python3 portfolio/cenas/documentos.py` → `site/docs/`.
- Cena em vídeo 1920×1080: `python3 portfolio/cenas/render.py --so sige` → `site/video/v2-sige.mp4` e `.webp`. No Replit (SwiftShader) cada quadro leva 15–35 s: os 240 quadros levam cerca de 1 h; rodar em segundo plano.
- Conferir: `python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_v2.py --navegador && python3 portfolio/tests/check_v2.py --video`. A suíte de navegador leva uns 20 min pelo mesmo motivo.
- Ver no navegador: `python3 portfolio/servir.py 5000 --directory portfolio/site` e abrir `/v2.html` (precisa de Range).
