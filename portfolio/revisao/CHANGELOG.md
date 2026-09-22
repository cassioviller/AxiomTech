# CHANGELOG — revisão multiagente, 22/09/2026

Arquivo editado: `portfolio/site/index.html` (integrador). `portfolio/build.sh` rodado ao final: currículo e três folhas de caso em 1 página cada; PDFs copiados para `site/`.

Observação: as propostas `juridico.md`, `ia.md`, `eng.md` e `hist.md` não existiam em `revisao/propostas/`; os achados desses leitores (4–14, 17–19) foram aplicados direto do texto da `REVISAO.md` e das decisões do portão (A–H). Ordem seguida: jurídico → engenheiro/RH → dono/storyteller/colega → acessibilidade.

## Jurídico / sigilo
- [juridico] achado 17 — removido o projeto "Bunker de blindagem para fonte radioativa" (seção Obra) e a única menção a "defesa"; o `summary` do detalhe passou de "Ver mais quatro: bunker de blindagem, …" para "Ver mais três: suíte em Campos do Jordão, contratos, auditório".
- [juridico] achado 18 (decisão A) — "roda sob licença numa empresa real" (stat da primeira tela) → "que concebi e construí, hoje em uso numa empresa de Light Steel Frame".
- [juridico] achado 18 (decisão A) — lede do SIGE: "hoje roda sob licença numa empresa de steel frame" → "hoje está em uso numa empresa de Light Steel Frame".
- [juridico] achado 18 (decisão A) — coluna Resultado do SIGE: "em uso sob licença numa empresa de steel frame" → "em uso numa empresa de Light Steel Frame".
- [juridico] achado 18 (decisão A) — faixa azul do SIGE: título "Concebido, construído, implantado — e licenciado" → "— e em uso"; parágrafo "hoje é usado sob contrato de licença por" → "hoje está em uso numa".
- [juridico] achado 18 (decisão A) — currículo, item VEKS: "implantação do SIGE (licenciado à empresa)" → "(em uso na empresa)".
- [juridico] achado 19 — varredura de nomes de clientes, margens, percentuais de terceiros, dados pessoais e legendas de imagem: nada além do bunker (achado 17) para remover; empregadores (VEKS, V Alves, Estruturas do Vale, escritório da família) mantidos como fato de currículo.
- [juridico] achado 18 nas folhas de caso — `casos/caso-*.html` não contêm "licen", "Cassio" sem acento nem "0,25%"; nenhuma edição.

## Engenheiro
- [eng] achado 4 — stat "R$ 24,5 mi" da primeira tela: "desvio máximo de 0,25% contra a Caixa" → "reproduz as composições SINAPI com desvio máximo de 0,25%".
- [eng] achado 4 — cota da seção Sistema: "13 obras · 0,25% de desvio" → "13 obras · reproduz o SINAPI a 0,25%".
- [eng] achado 4 — coluna Resultado da seção Sistema: "com desvio máximo de 0,25% contra a tabela da Caixa" → "num sistema que reproduz as composições SINAPI com desvio máximo de 0,25%".
- [eng] achado 4 — stat "0,25%": "desvio máximo contra os custos oficiais publicados pela Caixa (SINAPI)" → "desvio máximo ao reproduzir as composições SINAPI publicadas pela Caixa".
- [eng] achado 4 — bloco "Sem maquiagem" (mantido): "Precisão de 0,25% contra a tabela oficial" → "Reproduz as composições SINAPI com desvio máximo de 0,25%".
- [eng] achado 5 — galpão 15 × 20: "estudo estrutural e de fundação otimizado (…)" → "pré-dimensionamento estrutural e de fundação (…), sujeito à revisão do engenheiro responsável"; etiqueta "estudo estrutural" → "pré-dimensionamento estrutural".
- [eng] achado 5 — B-36, coluna Resultado das casas modulares: "pré-dimensionado (sujeito à revisão do engenheiro responsável) até a ficha técnica comercial".
- [eng] achado 5 — B-36, cartão "Celeiros": "pré-dimensionamento estrutural completo — sujeito à revisão do engenheiro responsável —".
- [eng] achado 5 — "cálculo estrutural" só existia no bunker, removido pelo achado 17.
- [eng] achado 6 — coluna Resultado dos 36 min: "Proposta de mão de obra em LSF, assinável em 36 minutos, (…); os cortes ausentes entraram como pendência declarada."
- [eng] achado 7 — NÃO APLICADO por decisão da REVISAO: não há print do registro de engenharia sem nome de cliente; registrado em `PENDENCIAS.md`.

## Leitor-máquina / RH
- [ia] achado 8 (decisão D) — linha de cargo-alvo na primeira tela, logo abaixo do eyebrow: "Cargo-alvo: Analista de orçamento, planejamento e custos · CLT ou PJ · São José dos Campos, presencial ou remoto" (classe `.note` já existente, cor de tinta).
- [ia] achado 9 (decisão F) — "Cassio" → "Cássio" na barra do celular, no `.who` do trilho e no `<h1>`; `<title>`, og:title, footer e JSON-LD já estavam com acento. LinkedIn: sem URL, nenhum placeholder visível (o comentário HTML existente foi mantido).
- [ia] achado 10 — JSON-LD `jobTitle` → "Analista de orçamento, planejamento e custos"; cargos, datas e formação conferidos contra `curriculo.html` (VEKS 03–09/2026, V Alves 02/2025–07/2026, Estruturas do Vale 04/2025–03/2026, AZ Contabilidade 2017–, PUC SI 3º sem.) — batem; JSON válido.
- [ia] achado 11 — revisão de `alt`: todas as 23 imagens têm `alt` descritivo, nenhum vazio; nenhuma mudança necessária.

## Storyteller
- [hist] achado 12 — `.sub` da primeira tela substituído pelo parágrafo de 3 frases ("Comecei no centavo, não na parede: …").
- [hist] achado 13 — fechamento na caixa de Contato, após o parágrafo principal: "Faltam 3 semestres para o diploma. Não falta obra feita."
- [hist] achado 14 — carimbo da folha 01: "Orçamento por leitura de projeto · caso principal".

## Dono de construtora
- [dono] achado 1 (decisão C) — linha de termos abaixo dos botões da primeira tela: "Sem custo. Devolvo em até 3 dias úteis. O pacote não sai do meu computador."
- [dono] achado 1 (decisão C) — mesma linha na caixa de Contato, depois do fechamento do achado 13 e antes dos contatos.
- [dono] achado 2 — bloco "O que faço na sua construtora" (4 linhas, lista `.tl`) na seção Currículo, entre a cota e o `.cv-grid`, antes de "Experiência".
- [dono] achado 3 — item Axiom: `.when` "projetos próprios" → "projetos próprios · sem dedicação de expediente".

## Futuro colega
- [colega] achado 15 — bloco "Como trabalho" (4 linhas, lista `.tl`) logo depois de "O que faço na sua construtora", antes do `.cv-grid`.
- [colega] achado 16 — frase sobre IA na coluna "O que fiz" da seção Sistema: "Dirigi o desenvolvimento, feito com assistentes de IA — as regras de engenharia e de negócio, os testes e a revisão são meus." (versão reorganizada da proposta, sem repetir "regras" e "revisão").

## Acessibilidade / design
- [acess] achado 20a — `--accent` do tema claro #D4551B → #B5440E (eyebrow sobre fundo 4,63:1; texto branco em botão 5,53:1). Tema escuro inalterado; `theme-color` e maquete não usam o token.
- [acess] achado 20b — novo token `--steel-panel:#2E4763` (só em `:root`); `.case-banner` e `.savings` passam a usar `var(--steel-panel)` — painel azul-aço fixo nos dois temas, texto claro sempre ≥ 5,49:1.
- [acess] achado 20c — barra `.bar.hot .track i` fixada em #F07A3E (3,44:1 sobre o painel).
- [acess] achado 21a — removido o eyebrow "Três obras, do desenho à proposta" (seção Sistema).
- [acess] achado 21b — removido o eyebrow "Como o sistema chega ao preço" (detalhe do drywall).
- [acess] achado 21c — removido o eyebrow "SIGE · Sistema de gestão para construtoras" da faixa azul (junto com a edição do achado 18).
- [acess] achado 21d — removido o eyebrow "Três histórias" (SIGE).
- [acess] achado 21e — removido o eyebrow "Antes e depois" (SIGE, detalhe).
- [acess] achado 21f — removido o eyebrow "Rigor" (SIGE, detalhe).
- [acess] achado 21g — removido o eyebrow "Três decisões que a conta revelou" (Casas modulares).
- [acess] achado 21h — removido o eyebrow "Contato" da caixa de contato (o carimbo 08/08 já diz).
- [acess] achado 22a — foco de teclado: anel de tinta (`outline-color:var(--ink)`) em `.btn`, `.rail .cv` e `.topbar a`; anel para dentro (`outline-offset:-3px`) em `details summary`.
- [acess] achado 22b — `details.mais>summary:focus-visible` recebe a mesma cor laranja do `:hover`.
- [acess] achado 22c — os 9 sinais "+" dos cartões de história ganharam `aria-hidden="true"`.

## Não aplicados
- achado 7 — sem imagem disponível sem nome de cliente (decisão da própria REVISAO); em `PENDENCIAS.md`.
- achado 23 — currículo é do agente `cv`, não do integrador; conferido que `curriculo.html` já traz cargo-alvo D, Axiom "sem dedicação de expediente", "reproduz as composições SINAPI" e "pré-dimensionamento (sujeito à revisão do engenheiro responsável)".
- decisões E (depoimento) e G/H (V Alves, formatura/MS Project) — sem fato novo; nada criado.

## Verificação feita pelo integrador
- HTML: tags balanceadas (parser Python), JSON-LD válido, 0 imagens sem `alt`, nenhuma ocorrência restante de "licen", "bunker", "defesa", "Cassio" sem acento, "contra a Caixa" ou "estudo/cálculo estrutural".
- `./build.sh`: `curriculo-cassio-viller.pdf` 1 pág.; `caso-23-diarios.pdf`, `caso-36-minutos.pdf`, `caso-casa-no-teto.pdf` 1 pág. cada.

## Correção 1
Rodada de correção após os verificadores (fatos e sigilo). Arquivos editados: `curriculo/curriculo.html`, `site/img/t1.webp`, `site/img/t2.webp`, `site/img/t3.webp`, `site/img/t4.webp`, `site/img/configurador-b36.webp`. Os HTML (`site/index.html`, `casos/caso-36-minutos.html`) não mudaram: continuam apontando para os mesmos nomes de arquivo, e os `alt` e legendas já eram genéricos.

- [fatos] currículo, linha "Ferramentas" — confirmado: nenhuma fonte (PLANO.md, BRIEF.md L39, site aprovado L745) dá nível para AutoCAD, Revit, Civil 3D, SketchUp ou Python; só "Excel avançado" e "inglês intermediário". Removidos os níveis sem fonte: "Excel (avançado) · AutoCAD · Revit · Civil 3D · SketchUp · OrçaFascio · Python · Inglês (intermediário)." Os níveis voltam quando o Cássio responder à pendência 6 do PLANO.md (registrado em `PENDENCIAS.md`). Currículo continua em 1 página; `pdftotext` na ordem.
- [sigilo] `t1.webp` — pixelados: nome do zip no cartão ("203.1809 - UP…zip"), "UPA Bertioga" no parágrafo do chat, o item "Inventariar o pacote 203.1809 UPA Bertioga" no painel de progresso e o anexo em "Envios".
- [sigilo] `t2.webp` — pixelados: o mesmo item do painel de progresso e o anexo em "Envios".
- [sigilo] `t3.webp` — pixelados: título do painel ("Registro engenharia 203.1809 ubs boraceia"); todo o conteúdo do registro abaixo do título "5. Orçamento interno" (linha 5.1 com lucro/imposto/ADM/comissão, tabela de custo × venda, painel com margem líquida e BDI/markup, faixa medida da MO); no chat à esquerda, os nomes dos dois documentos ("Proposta rodrigo oliveira…", "Registro engenharia 203.1809…"), o "Nº 203.1809" e a expressão "CNPJ do cliente". O título "5. Orçamento interno", o motor de planilha e o texto das decisões (pé-direito, aço, casa de máquinas) ficaram legíveis: não têm cliente nem margem.
- [sigilo] `t4.webp` — pixelados: título do painel ("Proposta rodrigo oliveira ubs boraceia"), linha de endereço no cabeçalho da proposta, "fonte … (Prefeitura de Bertioga)" na faixa da planta, rodapé "MO Ampliação UBS Boraceia · nomes · Bertioga/SP" (mantido "VEKS Engenharia · Proposta Comercial", empregador de currículo), linha do CNPJ no carimbo e os mesmos itens do chat à esquerda de `t3`. Quadro de áreas, parâmetros e planta continuam visíveis (já eram o conteúdo da legenda).
- [sigilo] `configurador-b36.webp` — imagem animada (6 quadros, 2160×1140) recortada para 2160×1010 em todos os quadros: sai o bloco "BDI — Acórdão TCU 2622/2013" com os percentuais de AC e S+R+G no pé da barra lateral; ficam as opções, o resumo de preço/área/aço/peso e as vistas 3D. Verificado no Chromium headless. `alt` e legenda não citavam BDI; sem edição no HTML.
- [sigilo] PDFs — `./build.sh` rodado: `casos/caso-36-minutos.pdf` regerado com as imagens novas (conferido extraindo as imagens do PDF com `pdfimages`; `pdftotext` sem "bertioga", "boraceia" ou nome de pessoa) e copiado para `site/casos/`. Os demais PDFs também foram regerados (mesmo conteúdo).
- Método de redação: pixelização (redução a 12% e volta ao tamanho, mais desfoque leve) só nas regiões apontadas; nenhuma legenda, número ou texto do site foi alterado. Os originais não ficaram em `portfolio/`; estão só no diretório temporário desta sessão.
- Falso positivo: nenhum. Observação sobre "CNPJ do cliente" e "Nº 203.1809" em `t3`/`t4`: são a expressão e um número de pacote, não um CNPJ nem um nome; pixelados mesmo assim porque custam nada e o número liga ao nome do pacote que estava no painel.
- Atenção (não resolvido por esta rodada): as versões anteriores de `t1`–`t4` e do configurador estão no histórico do git (commit e28d9e3). Se o repositório for público, é preciso reescrever o histórico ou tratar as imagens como já expostas; registrado em `PENDENCIAS.md`.

## Correção 2
Rodada de correção após os verificadores (fatos). Arquivo editado: `site/index.html` (1 linha). Currículo e folhas de caso não mudaram.

- [fatos] `site/index.html` L466, carimbo da Folha 02 — confirmado: "Jul–Set/2026" não consta em nenhuma fonte. O site aprovado (`ref/site-sem-base64.html` L496) traz só o stat "11 sem. do primeiro registro ao estado atual"; o BRIEF.md e o PLANO.md não dão mês de início; o currículo registra a VEKS como mar/2026 – set/2026. O período era dedução (11 semanas antes de set/2026), não dado registrado. Trocado por "VEKS · 2026", no mesmo padrão das folhas 04 e 05. Como a célula do meio já dizia "· VEKS", ela ficou só "Sistema de orçamento" para não repetir o nome; nenhum número, cliente ou resultado mudou. O stat "11 sem." permanece como estava.
- Varredura: nenhuma outra ocorrência de "jul–set", "jul-set" ou "julho" no site, no currículo ou nas folhas (a única data com "jul" é "fev/2025 – jul/2026" da V Alves, fato de currículo).
- Falso positivo: nenhum.
- `./build.sh` rodado: `curriculo-cassio-viller.pdf`, `caso-23-diarios.pdf`, `caso-36-minutos.pdf`, `caso-casa-no-teto.pdf` — 1 pág. cada.
