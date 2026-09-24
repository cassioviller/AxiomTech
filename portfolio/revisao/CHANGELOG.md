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

---

# Rodada 3 — cruzamento com `portfolio.zip` e `saida.zip`, 23/09/2026

Fontes: PDFs novos (`saida/portfolio/*.pdf`, 21/09), `afirmacoes.json`, `REVISAO.md`, `uma-pagina.md` e o manual do app v2 (`saida/manual-do-app-v2/prints`).

## Números e afirmações
- "13 obras orçadas" → "13 obras no sistema, 11 com proposta" (meta, og, JSON-LD, stat do hero, lede, cota, Resultado e stat da Folha 02), como nos PDFs novos.
- 0,25% qualificado com "nos 19 serviços conferidos" (hero, Resultado, stat, "Medido"); o 0,00% ganhou a ressalva "repete a mesma conta, não acerta custo de obra pronta".
- "11 sem." ganhou o período: 9/jul a 21/set/2026.
- Caso R$ 24,5 mi: tirado "em horas" (nenhuma fonte sustenta).
- Margens: "não aparecem aqui" → as das obras reais não aparecem; as da casa de demonstração, sim (a legenda da consolidação mostra 30%).
- SIGE: Resultado, cota, legenda do portal e caso 01 com "cópia do sistema" e carga pendente no sistema em uso (REVISAO L-01); legenda do portal sem "previsão de entrega" (L-02).
- SIGE: "4 guias ilustrados" → "4 guias passo a passo (3 ilustrados)"; período "1ª versão 2025 · atual mai–set/2026" e autoria com assistente de IA, como em `uma-pagina.md`.
- SIGE: "avisos automáticos para 10 tipos de evento" removido (S7-10/S7-21); compras e conta a pagar com a ressalva "onde a empresa ligou"; ponto "com opção de" reconhecimento facial; 3.300 → "3.343 sem falha na última rodada completa (04/09/2026)"; "seis frentes concluídas" (S7-05 desatualizada) → "atacados em seis frentes".
- Frase de ponte: o SIGE é outro sistema, e o "Ainda falta" da Folha 02 diz que o diário em uso real é do SIGE.

## Imagens novas
- Folha 02, "Depois da proposta": `o-mapa.webp` (mapa comparativo, de `diretor-obras-1-compras-requisicoes-1.png`) e `o-financeiro.webp` (orçado × comprometido × realizado, de `diretor-obras-1-financeiro.png`), manual v2, obra DEMO-CASA.
- Caso 04 (compras): `c-aprovacao.webp` (`demo/11-aprovacao.png`) e `c-recebimento.webp` (`demo/12-recebimento.png`, sem o menu fantasma).

## Folha de caso
- `casos/caso-23-diarios.html`: "voltaram para o lugar certo" → leitura em cópia, 27,6% → 44,7% (60,8% planejado), carga pendente no sistema em uso. PDF regerado (1 página) e copiado para `site/casos/`.

## Acessibilidade
- Link "Pular para o conteúdo" e `main#conteudo`.
- Botão Pausar/Continuar nas maquetes 3D (WCAG 2.2.2), em `maquetes.js`.

## Não publicar (achado na análise)
- `diretor-admin-usuarios.png` (e-mail pessoal), `diretor-painel.png` e `orcamento_109_1506.*` (obra real e nome de pessoa), `diretor-admin-diagnostico.png` (caminho local e alertas), `encarregado-obras-1-rdo-10.png` (hash não confere no demo).
- Manual v1: as telas do encarregado são páginas 404; usar só a v2.

## Pendente — decisão do autor
- PDFs novos com "[SEU NOME]", "[cargo/área]", "[e-mail]", "[preencher]": preencher antes de linkar no site.
- Nomes de clientes nos PDFs novos (Rede Graal, DIASE/Goodman, Tenda Una, "Residência Cassio") x site anonimizado: escolher um padrão.
- Margens abertas no `portfolio.pdf` novo x sigilo no site.
- `og:image` absoluto, `og:url` e canonical dependem do domínio definitivo.
- "Marcos Tavares" em `c-aprovacao.webp`: confirmar que é usuário fictício do manual.
- Versão em inglês (há `PORTFOLIO.en.md`); títulos h2 → h5 nos blocos Problema/O que fiz/Resultado.

---

# Rodada 4 — storytelling Minto e DESIGN.md, 23/09/2026

- `portfolio/DESIGN.md`: linguagem visual do site no formato awesome-design-md (9 seções, todos os tokens de `:root`).
- 10 casos em Minto (resultado → o que fiz → prova): Folha 02 com "O que fiz" em primeira pessoa e "com o sistema"; Folha 03 com Resultado no topo (casos 02–04 ganharam Resultado a partir de fatos já no site); Folha 04 com Resultado no topo.
- 5 legendas de galeria reescritas para dizer a decisão.
- `portfolio/tests/check_site.py`: números iguais a `2a686cf`, ressalvas presentes, tags balanceadas, casos abrindo pelo resultado, DESIGN.md completo.

---

# Rodada 5 — página historia.html (a história em cenas), 23/09/2026

- Pesquisa com 5 personas (recrutadora, diretor de engenharia, roteirista, dev front-end e acessibilidade/desempenho) em `docs/superpowers/research/2026-09-23-historia/`; spec em `docs/superpowers/specs/2026-09-23-historia-scrollytelling-design.md`.
- `site/historia.html`: 10 cenas (frase ≤ 10 palavras + ressalva), barra fixa com currículo e WhatsApp, ficha com as palavras-chave, rodapé. Sem JS ou com movimento reduzido: cenas empilhadas, cada frase com a sua imagem.
- `site/historia.js`: fundo em palco `sticky`, troca no meio da tela (`IntersectionObserver`), crossfade; maquetes 3D amarradas ao scroll por `seek()`, só uma no fluxo por vez. Rolagem nativa.
- `site/maquetes.js`: a API `fig.__maquete` passa a expor `dur`.
- `tests/check_historia.py` (+ `tests/historia_teste.html` no Chromium headless): roteiro exato, números que o index sustenta, ressalvas, contraste da faixa no pior caso, `aria-hidden`, `svh`, 320 px sem rolagem horizontal, movimento reduzido.
- O `index.html` não mudou. Em aberto (do Cássio): estágio/júnior, link a partir do portfólio, foto `p-fotos.webp`, imagem de prévia própria.

---

# Rodada 6 — a história na linha do tempo, 23/09/2026

- Pesquisa com as 5 personas (rodada 2) em `docs/superpowers/research/2026-09-23-historia-v2/`; spec em `docs/superpowers/specs/2026-09-23-historia-linha-do-tempo-design.md`.
- `site/index.html`: 17 capítulos em ordem cronológica, de 2017 a set/2026, cada um com data (`<time>`), frase, ressalva e link "Ver…" para a seção do portfólio; vínculos simultâneos ditos com o tipo de contrato; fundos tipográficos nos capítulos sem imagem; barra com o status atual.
- Régua de tempo no cabeçalho (`nav` + `ol`, um `aria-current="step"`, foco no título ao saltar).
- `site/maquetes.js`: cena `icamento` (o módulo sobe pelo balancim, cabos verticais), ligada ao scroll.
- Relógio da maquete sobre faixa escura (contraste ≥ 3:1).
- `tests/check_historia.py`: cronologia, datas contra o currículo, links únicos, régua, WebGL real do içamento.
- Para o Cássio conferir: iPhone real, zoom 200%, leitor de tela e memória das três maquetes. Em aberto: estágio/júnior; UNIFEI 2020–2024 (currículo) ou 2022–2024 (conversa) — a página não mostra o ano de entrada.

---

# Rodada 7 — o filme como trailer da história, 23/09/2026

- Pesquisa das 5 personas (rodada 3) em `docs/superpowers/research/2026-09-23-filme/`; spec em `docs/superpowers/specs/2026-09-23-filme-trailer-design.md`.
- "Comecei pela contabilidade, não pela obra." na história, no portfólio e no filme.
- `portfolio/filme/`: o filme do zip, corrigido por `corrigir_filme.py` — 13 obras no sistema/11 com proposta; SIGE mai → set/2026; balancim como estudo; "só no WhatsApp"; "vi o dado digitado"; nome com acento; sem "26 anos"; tabela da abertura com números do portfólio; post-its e planilha sem valores inventados; legendas antigas removidas; apoio ≤ 200 palavras/min.
- `render.py` roda no Replit com o Chromium do sistema; `site/video/historia.mp4` (960×540, 85 s, sem áudio) e capa.
- Trailer na história, só por clique, com transcrição; "Assistir ao filme ↓" no convite.
- Correção: o palco (sticky, `margin-bottom:-100vh`) cobria por uma tela o que vinha depois da história — a ficha, no fim da página; `overflow:clip` no `<main>` corta o palco onde a história acaba.
- `tests/check_filme.py` (texto do filme e vídeo) e `check_historia.py` (seção do trailer; vídeo e ficha à vista depois do palco).
- Próximo passo (plano separado): dioramas ao vivo como fundo dos capítulos, com um renderizador compartilhado.
- Em aberto (Cássio): idade; UNIFEI 2020 ou 2022; estágio/júnior; versão curta do trailer para o LinkedIn.

---

# Rodada 8 — o filme como fundo da história, avançado pela rolagem, 24/09/2026

- Pesquisa das 5 personas (rodada 4) em `docs/superpowers/research/2026-09-23-filme-fundo/`; spec em `docs/superpowers/specs/2026-09-23-filme-fundo-design.md`; plano em `docs/superpowers/plans/2026-09-24-filme-fundo.md`.
- 11 capítulos ganham um clipe curto de vídeo ao fundo (960×540, 24 fps, H.264 com GOP 4, sem texto, ≤ 0,9 MB cada e ≤ 8 MB na soma), cujo tempo é o progresso da rolagem: `site/clipes.js` (seek só por `currentTime`, quantizado ao quadro, um em voo por vez; carga depois do `load` e a 600 px da cena; no máximo 2 vídeos com dados; pôster = último quadro como plano B). `historia.js` só trocou `maquete` por `clipe`.
- As três maquetes three.js da página (casa, içamento, 36 min) foram portadas para o `film.html` no estilo do filme (`SC[9..11]`) e renderizadas como clipes: a história não roda mais WebGL; `maquetes.js` segue só no portfólio completo.
- `film.html`: `?limpo` (só o canvas) e `renderCena(i, t)`; texto pintado corrigido pela regra "nada que o portfólio não sustente" (MESMO DADO, PLANO DE CORTE, EM USO, andares do SIGE iguais ao `.flow`, DESENHO, PLANTA, calendário ≤ 31). `render_clipes.py` gera mestre, versão web e pôster de cada clipe, reencodando até os tetos.
- O trailer saiu da página: `render.py` grava `filme/saida/historia-960.mp4` (fora do site, fora do git); README do filme com "Como enviar" (WhatsApp/LinkedIn).
- Página: sem `filter` no vídeo (paleta do filme); pôster do clipe sem filtro e com o mesmo recorte do vídeo (crossfade entre dois quadros iguais); em tela larga a faixa de texto vai para a esquerda; no celular, recorte `68% 50%`; linha de crédito dos dioramas na ficha; comprimento da história inalterado; pôsteres carregados sem lazy, prontos para o crossfade e para os caminhos só-pôster (revisão final).
- `portfolio/servir.py`: servidor estático com Range (206) no `.replit` e nos testes — sem ele o navegador ignora todo seek.
- Testes: `check_filme.py --video` (texto pintado, estilo das cenas portadas, clipes: peso, GOP, pontas paradas, pôster); `check_filme.py --cenas` (conteúdo das cenas portadas no Chromium, ~20 s); `check_historia.py --navegador` (marcação e CSS dos clipes; harness; clipe real com Range e sem Range; 404; `?clipes=nao`; movimento reduzido ligado no meio; economia de dados; foco; composição; LCP/CLS/TaskDuration contra `tests/baseline.json`).
- Em aberto: iPhone real (latência de seek, `preload` sem gesto, recorte em retrato → render 9:16 se houver "tiras"); URL do deploy para `--origem`; do Cássio: idade; UNIFEI 2020 ou 2022; estágio/júnior; versão vertical do trailer.
- Passada pós-merge (/code-review high com as 5 personas): recarga do clipe depois de `emptied` do WebKit; re-seek em `loadeddata` quando o `seeked` chega sem quadro; `transition:none` no pôster sob movimento reduzido; `--cenas` valida os passos; `checar_portadas` confere o módulo do içamento ≤ 8 m no `film.html`; DESIGN.md e ANDAMENTO.md atualizados.

---

# Rodada 9 — ajustes depois dos prints e da revisão, 24/09/2026

- Prints dos 17 capítulos (celular e desktop, pelo endereço público): https://claude.ai/artifact/AfNihqpe9eP2TRuNPzzrPB. Plano: `docs/superpowers/plans/2026-09-24-historia-rodada-9-ajustes.md`.
- Página: o palco começa abaixo da barra fixa (`--barra`, medida pelo `historia.js` por `ResizeObserver`: fontes, quebra de linha, janela); foco vertical por clipe (`foco-alto` em obra, casa, whatsapp e içamento; `foco-baixo` em escala); marco tipográfico à direita na tela larga; celular deitado com a faixa à esquerda e menor.
- `clipes.js`: despejo pelo navegador reconhecido pela conta dos `emptied` nossos (antes ou depois dos metadados); um só `emptied` nosso por `load()`; sem seek enquanto o `seekable` não está completo; a espera pelo Range morre com a carga que a criou; `progress` refaz o seek que chegou sem quadro; espera de até 1,5 s por um `seekable` completo antes de congelar; o quantizador nunca passa do último quadro (o `historia.js` deixou o `0,999`).
- Filme: `escala` termina com as 12 miniaturas inteiras e `icamento` com o cavalo no quadro (câmeras; clipes regerados; enquadramento conferido por projeção no `--cenas`). `render_clipes.py` espera `PRONTO` com prazo.
- `maquetes.js`: sai a cena morta do içamento. Testes: checagens que passavam sem provar foram amarradas (regra do vídeo ancorada, 404 pedido de verdade, precondições em `check`, caixas com largura), mensagens com o valor medido, `--origem` sem URL avisa, exceção de JS vira `FALHOU`.
