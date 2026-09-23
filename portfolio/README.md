# Portfólio de Cássio Viller

Plano e decisões: `../PLANO.md`. Nada aqui foi publicado nem commitado.

```
curriculo/   curriculo.html → curriculo-cassio-viller.pdf (1 página) + .txt (para colar em portais de vaga)
casos/       3 folhas de caso A4 (HTML → PDF), caso.css compartilhado, mensagens.md (modelos de WhatsApp/e-mail)
site/        site estático: index.html (a história em cenas, página principal), portfolio.html (portfólio completo), historia.js, maquetes.js, img/, vendor/ (three.js 0.186), og.png, PDFs
ref/         originais do pacote (site antigo, cena5 aprovada) — só referência
build.sh     regenera todos os PDFs e copia para site/
```

## Usar

- Gerar PDFs: `./build.sh` (precisa de `chromium` e `pdftotext`; as folhas de caso buscam as fontes no Google Fonts).
- Ver o site: `cd site && python3 -m http.server 8000` → http://localhost:8000
  (precisa de servidor; abrir o arquivo direto bloqueia o carregamento do three.js).
- Conferir um quadro de uma maquete: `?maquete=forcar&t=12` na URL congela a cena no segundo 12 e ignora a guarda de fps.

## Antes de publicar

1. Preencher no `curriculo/curriculo.html` os dois `[confirmar URL]` (LinkedIn e portfólio) e rodar `./build.sh`.
2. No `site/index.html` e no `site/portfolio.html`: trocar `og:image` para URL absoluta (`https://dominio/og.png`) — o WhatsApp exige; incluir o
   link do LinkedIn onde está o comentário `<!-- LinkedIn: ... -->`.
3. Confirmar com a VEKS o que pode ser mostrado (valores de proposta, imagens de projeto, o bunker).
4. Testar as maquetes num Android médio de verdade. A guarda automática volta para a imagem estática abaixo de ~24 fps,
   mas isso só foi testado em renderização por software, não em aparelho.

## Regras de conteúdo (valem para qualquer edição)

Só números do site original / brief. Clientes sempre genéricos. Nunca: margens ou percentuais de ex-contratante,
salários, valores de contrato, endereço, nascimento, CPF/CNPJ, nomes de pessoas. `ref/img-nao-usadas/o1.webp` e `o2.webp` mostram
o nome do cliente da unidade de saúde — não usar; (foram tirados de `site/img/` para não irem junto na publicação).
