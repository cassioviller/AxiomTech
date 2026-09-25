# Site v2 — quatro casos, cena criada + documento real · Design

Data: 25/09/2026. Branch: `site-v2` (a partir de `main`, rodada 9). O site das rodadas 1–10 passa a ser o **protótipo**: o branch `historia-cenas-novas` (16 capítulos, cenas SC[0..16]) fica guardado sem merge, como referência.

## 1. Por que refazer

Avaliação do Cássio sobre o protótipo (25/09):

- **Imagens ruins:** as cenas 3D têm cara de brinquedo (low-poly liso), são ilegíveis e desbotadas (assunto pequeno, névoa, quadro vazio) e genéricas (caixas, folhas, uma peça laranja). Nenhum momento mostra os documentos reais que ele produziu.
- **Texto enfeitado demais para um currículo:** frases de efeito ("Construí o jeito de o número não sumir.", "Faltam 3 semestres para o diploma. Não falta obra feita.").
- **Roteiro fraco:** 16 capítulos cronológicos, vários repetindo a mesma ideia.

## 2. Objetivo e leitor (sem mudança em relação ao BRIEF)

- **Objetivo:** conseguir a próxima vaga em orçamento, planejamento, custos ou gestão de obra (CLT ou PJ).
- **Leitor:** dono de construtora, gestor ou RH de engenharia. Não é programador. Decide em segundos se continua.
- **Continuam valendo:** os fatos, números e regras de sigilo do `BRIEF.md` (§1, "Nunca publicar"), com a correção da §5.2 (1 dia útil).

**Critérios de sucesso**

1. Em 10 s o leitor sabe quem é o Cássio, o que ele faz e para que vaga serve.
2. Toda frase da página é um fato verificável, sem metáfora nem antítese.
3. Cada caso mostra, nítido, pelo menos um documento real feito pelo Cássio, com o número da manchete destacado nele.
4. As cenas criadas e os documentos reais aparecem em equilíbrio: nenhum caso é só 3D e nenhum é só print.

## 3. Decisões tomadas no brainstorming

| # | Decisão | Alternativas descartadas |
|---|---|---|
| D1 | Manter o conceito de cenas animadas, refazendo **todas** com outro nível de acabamento | Tirar o 3D; manter só 1–2 cenas |
| D2 | **Poucos casos fortes:** abertura + 4 casos + trajetória curta + fechamento | Cronologia enxuta; capítulos por competência |
| D3 | **A cena leva ao documento:** material real e criado misturados na mesma cena, com equilíbrio | Tela dividida (já rejeitada no BRIEF §3.2); documentos animados com 3D só na abertura |
| D4 | No caso 1, um **cronômetro de 0:00 a 36:00**, não os horários do relógio (11:35 → 12:11), para não confundir | Lupa no relógio do Windows |
| D5 | "À mão, cerca de **1 dia útil** (estimativa)", no lugar de "2 dias úteis"; **nenhum multiplicador** ("≈27×" sai de tudo) | Recalcular para ≈13× |
| D6 | O 3D continua em three.js, renderizado em vídeo; o salto de qualidade vem de modelagem, luz, materiais, enquadramento e resolução | Blender/Cycles: não há Blender nem GPU (4 CPUs, 7 GB) |
| D7 | **Piloto primeiro:** o caso 1 completo, aprovado pelo Cássio antes dos outros | Fazer tudo de uma vez |

## 4. Estrutura da página (`portfolio/site/index.html`, reescrito)

Ordem: **abertura → caso 1 → caso 2 → caso 3 → caso 4 → trajetória → fechamento.** O menu lateral lista essas 7 entradas.

### 4.1 Abertura — a ficha em 10 segundos

- **Nome:** Cássio Viller.
- **Vaga:** orçamento, planejamento e custos de obra.
- **Formação:** Engenharia Civil, 7º semestre (faltam 3), Cruzeiro do Sul, após 6 semestres na UNIFEI.
- **Cidade e regime:** São José dos Campos/SP · CLT ou PJ · presencial ou remoto.
- **Contato:** WhatsApp, e-mail e currículo em PDF.
- **Posicionamento, uma frase factual (proposta):** "Orço obras, acompanho a execução e construí os sistemas que uso para isso."
- **Cena criada:** uma mesa de trabalho. Sobre ela estão os documentos reais dos quatro casos (a proposta, uma tela do orçamento, o cronograma do SIGE, a prancha do B-36), como texturas.
- **Imagem principal da página (LCP):** o pôster dessa cena, carregado com prioridade.

### 4.2 Os quatro casos

As manchetes abaixo são rascunhos, a validar no spec review. Os números são todos do BRIEF ou do texto aprovado do protótipo.

| # | Caso | Manchete | Linha de apoio (fonte/ressalva) | Cena criada | Documento real (origem) | Destaque laranja |
|---|---|---|---|---|---|---|
| 1 | Orçamento em 36 minutos | "Orçamento e proposta de uma ampliação de 328 m² em 36 minutos." | "Unidade de saúde, 26 ambientes. Medido do primeiro arquivo aberto à proposta pronta. À mão, cerca de 1 dia útil (estimativa)." | Mesa de orçamentista com notebook; o pacote do projeto chega; cronômetro de 0:00 a 36:00 | Os 4 prints da linha do tempo (`img/t1..t4.webp`, já pixelados) e a proposta (`img/o-proposta.webp`) | O valor total na proposta; o cronômetro em 36:00 |
| 2 | Sistema de orçamento (VEKS) | "Orcei 13 obras, de R$ 29 mil a R$ 24,5 milhões." | "11 com proposta. Conferência com a SINAPI: desvio máximo de 0,25% nos 19 serviços conferidos. A gestão de obra deste sistema ainda não rodou numa obra real." | Estação de trabalho com planta sobre a mesa e o sistema no monitor | Quantitativos, orçamento e consolidação (`saida.zip` → `manual-do-app/prints/diretor-projetos-1-*.png`) | A linha do desvio; o total da obra |
| 3 | SIGE na obra dos galpões | "Implantei a gestão de obra em dois galpões com 22 baias." | "Depois de 11/08 o diário ficou 23 dias só no WhatsApp. Recuperado, o avanço passou de 27,6% para 44,7%, lido numa cópia do sistema." | Canteiro dos dois galpões de LSF; celular do encarregado; escritório de obra | Cronograma, diário, portal do cliente, fotos (`portfolio.zip` → `img/kabod/01..09`) | 27,6% → 44,7% no cronograma |
| 4 | Casas modulares | "O celeiro B-36 não cabia no caminhão: dividi em duas caixas." | "Três viagens, telhado em kit, 37 decisões registradas. Pré-dimensionado, sujeito à revisão do engenheiro responsável." | Fábrica → caminhão → içamento na obra, em LSF | Render do B-36, prancha de transporte, pranchas 2D, ata de decisões (`casas pre moldadas (1).zip`) | As duas caixas na prancha de transporte; "37" na ata |

### 4.3 Trajetória — uma faixa, sem cena 3D

2017 contabilidade (AZ Contabilidade) → 2020–2024 UNIFEI (DCE, InLoco Jr.) → fev/2025 V Alves (gerente de produção) + Estruturas do Vale (estágio; o SIGE nasceu aqui) → mar–set/2026 VEKS (PJ, 6 meses).

Uma linha cita as ferramentas: calculadora de parede LSF/drywall e classificador de fluxo de caixa.

### 4.4 Fechamento

- "O que faço numa construtora": a lista objetiva do protótipo, que já é factual.
- Contato, currículo em PDF e link para o portfólio completo.
- Sem frase de efeito.

## 5. Regras de texto (site inteiro, incluindo o `portfolio.html`)

1. **Manchete:** fato na primeira pessoa, com verbo e pelo menos um número medido; no máximo 12 palavras.
2. **Linha de apoio:** a fonte ou a ressalva ("estimativa", "pré-dimensionado…", "numa cópia do sistema", "ainda não rodou numa obra real"). No máximo 30 palavras.
3. **Proibido:** metáfora, antítese, pergunta retórica, adjetivo de autoelogio ("robusto", "inovador", "revolucionário"), multiplicador ("27×", "13×").
4. **Números:** só os medidos ou os do BRIEF, com a unidade. Onde era estimativa, a palavra "estimativa" continua.
5. **Correção D5:** "2 dias úteis"/"dois dias úteis" viram "1 dia útil" no `index.html`, no `portfolio.html` e no currículo (`curriculo.html`, `.txt` e PDF regenerado). O "≈ 27" do `portfolio.html` sai.

## 6. Anatomia de um caso na tela

Cada caso ocupa a tela inteira e avança com a rolagem em três tempos:

1. **Cena criada.** Vídeo 3D do lugar do trabalho. O documento real já aparece dentro da cena, como textura: na tela do notebook, na prancha sobre a mesa, no celular.
2. **Aproximação.** A câmera chega ao documento. No último quadro, o documento ocupa um retângulo conhecido da tela.
3. **Prova.** O vídeo dá lugar à imagem real do documento, em HTML e na resolução original do print, posicionada exatamente sobre esse retângulo. A passagem é invisível e o texto do documento nunca passa pela compressão do vídeo. Um destaque laranja (caixa ou sublinhado desenhado em SVG/CSS sobre a imagem, não pintado nela) marca o número da manchete. O texto do caso entra ao lado (tela larga) ou embaixo (tela estreita).

**Equilíbrio:** a cena criada ocupa cerca da primeira metade da rolagem do caso e o documento real a segunda.

**Celular:** os mesmos três tempos. No tempo 3 o documento aparece em recorte, só a região do destaque (uma segunda imagem, recortada a partir do original), porque a tela inteira do sistema não se lê em 390 px.

**`prefers-reduced-motion`:** nenhum vídeo toca. Cada caso mostra o pôster (último quadro) com o documento real e o destaque já no lugar.

**Sem JavaScript:** o texto e as imagens reais aparecem em sequência, legíveis. O texto faz sentido sem as cenas.

## 7. Padrão visual das cenas (critérios verificáveis)

1. Vídeo em **1920×1080** (hoje 960×540), H.264, pôster WebP. Tetos de tamanho redefinidos no piloto e registrados no plano; alvo inicial ≤ 2,5 MB por caso.
2. **Assunto ≥ 60% da largura do quadro** no último quadro, conferido por projeção no teste. O documento-alvo ocupa o retângulo de passagem com erro ≤ 2 px.
3. **Sem névoa sobre o assunto:** a névoa começa atrás do assunto mais distante do último quadro.
4. **Materiais e luz:** um kit comum, feito no piloto. Materiais com textura (madeira, aço galvanizado, concreto, papel), sombras suaves, oclusão de ambiente (SSAO ou baked), tone mapping ACES e antisserrilhado (render em 2× e redução).
5. **Modelagem com escala real:** perfis de LSF com seção de montante, mesa e notebook em proporção real. Nada de blocos lisos representando objetos.
6. **Um acento laranja por cena**, e **nenhum texto pintado**. O texto vem dos documentos reais e do HTML.
7. **Documentos como textura** nas cenas: carregados dos arquivos reais já anonimizados (§8), em resolução suficiente para ficar nítidos no último quadro.

## 8. Produção

- **Cenas:** um arquivo HTML por cena em `portfolio/cenas/` (`abertura.html`, `caso-36min.html`, `caso-orcamento.html`, `caso-sige.html`, `caso-modulares.html`), com um módulo comum `portfolio/cenas/kit.js` (renderer, luz, materiais, câmera por chaves, `renderCena(t)`, `window.PRONTO`).
  - three.js local (`site/vendor/`, 0.186, já no repositório) em vez do r128 do filme.
  - O `film.html` e o `corrigir_filme.py` não são usados.
- **Render:** `portfolio/cenas/render.py`, derivado do `render_clipes.py`: Playwright + Chromium + ffmpeg, pontas paradas, PSNR do pôster.
- **Documentos:** `portfolio/cenas/documentos.py` extrai dos zips os arquivos da tabela §4.2. Para cada um:
  - aplica a anonimização (pixelar nomes de cliente, como em `t1..t4`);
  - grava em `portfolio/site/docs/` a versão inteira e o recorte do destaque, em WebP;
  - grava as coordenadas do destaque num JSON (`docs/destaques.json`), usado pela página e pelos testes.
  - A lista do que pixelar em cada arquivo é revisada à mão pelo controlador antes de publicar.
- **Página:** `index.html` novo com as 7 seções. Aproveita do protótipo o carregamento progressivo de vídeo (`clipes.js`, no máximo 2 vídeos com dados), a versão sem movimento, o menu lateral e o `servir.py`. O `historia.js` é reescrito para os três tempos de §6. O `maquetes.js` sai.
- **Portfólio completo:** `portfolio.html` fica como página de detalhe. Na fase 3 o texto é revisado pelas regras §5, sem mudar a estrutura.

## 9. Testes

Scripts em `portfolio/tests/`, no mesmo estilo dos atuais (`check()`, OK/FALHOU):

1. **Vídeo:** pontas paradas, PSNR do pôster ≥ 40 dB, sem áudio, 1920×1080, tetos de tamanho.
2. **Enquadramento:** por projeção no último quadro, assunto ≥ 60% da largura e retângulo do documento dentro de ±2 px do alvo da página.
3. **Documentos reais:** cada caso tem pelo menos uma imagem de `site/docs/` visível no tempo 3. Largura natural ≥ largura exibida (nunca ampliada). O destaque existe e cai dentro da imagem.
4. **Texto:** manchetes com ≤ 12 palavras e pelo menos um dígito; linhas de apoio com ≤ 30 palavras; nenhuma palavra da lista proibida (nomes de clientes do BRIEF, "27×", "≈ 27", "2 dias úteis", "dois dias úteis" e as frases de efeito do protótipo citadas em §1); as ressalvas obrigatórias presentes.
5. **Página no navegador:** sem erro de console; `prefers-reduced-motion` mostra pôster + documento; 390 px mostra o recorte; sem JS o texto aparece.
6. **Sigilo:** nenhum arquivo em `site/docs/` sai sem estar na lista revisada de anonimização.

## 10. Ordem de trabalho

1. **Fase 1, piloto:** o kit (`kit.js`, `render.py`, `documentos.py`) e o caso 1 completo (cena, documentos, seção na página, testes). O Cássio aprova o padrão visual por prints e pelo site rodando. **Os casos 2–4 não começam antes dessa aprovação.**
2. **Fase 2:** casos 2–4, abertura, trajetória e fechamento. O protótipo sai do `index.html`.
3. **Fase 3:** revisão do texto do `portfolio.html` e do currículo pelas regras §5 (incluindo D5) e regeneração do PDF.

Cada fase tem o próprio plano de implementação. Este spec cobre as três; o primeiro plano cobre só a fase 1.

## 11. Fora do escopo

Publicar e fazer deploy; push para o GitHub; o trailer de envio (`render.py` do filme); o teste num iPhone real; novas fotos ou prints que ainda não existem nos zips.

## 12. Pontos a confirmar no review deste spec

1. A frase de posicionamento da abertura (§4.1).
2. As quatro manchetes (§4.2).
3. Se o currículo PDF entra na fase 3 ou fica para depois.
4. Qual print mostra a conferência com a SINAPI (0,25%) no caso 2. Se nenhum print dos zips mostra, o destaque do caso 2 fica no total da obra e o 0,25% fica só no texto.
