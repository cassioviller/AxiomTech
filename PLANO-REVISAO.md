# PLANO — Revisão multiagente do portfólio

Escrito em 22/09/2026. Cobre os achados da revisão por leitores (dono de construtora, engenheiro, investidor, IA,
storyteller, colega, RH, jurídico, acessibilidade, designer). Complementa o `PLANO.md`.

## 0. Princípios

1. **Um arquivo, um escritor.** `portfolio/site/index.html` é editado por um único agente integrador. Os demais
   produzem *propostas* em arquivos separados (`portfolio/revisao/propostas/*.md`) com o texto pronto para colar.
   Evita conflito de edição e deixa cada mudança revisável.
2. **Fato só do material do Cassio.** Nenhum agente inventa número, cliente, depoimento ou resultado. O que faltar
   vira `[PERGUNTA AO CASSIO]` na proposta, nunca texto na página.
3. **Sigilo antes de vitrine.** Todo texto novo passa pelo agente "Jurídico/sigilo" antes do integrador aplicar.
4. **Verificar de verdade.** Cada rodada termina com renderização (PDF e screenshots), verificação de overflow,
   validação do JSON-LD e conferência dos números contra a fonte.

## 1. Portão inicial — respostas que só o Cassio tem (bloqueia tudo)

Sem estas respostas os agentes trabalham com placeholders. Formulário curto, 10 minutos:

| # | Pergunta | Bloqueia |
|---|---|---|
| A | O SIGE é seu? Há cláusula de propriedade intelectual no estágio da Estruturas do Vale ou no contrato PJ da VEKS? Existe contrato de licença por escrito? | Todo texto "criei / licenciado" (fases 2 e 3) |
| B | A VEKS autoriza mostrar: valores de proposta, imagens 3D das obras, o bunker, o nome dela? (sim/não por item) | Casos 02, 05 e imagens |
| C | Termos da oferta "me mande uma obra": custo, prazo de devolução, sigilo do pacote | Primeira tela e Contato |
| D | Cargo(s)-alvo, CLT/PJ, presencial/remoto, região | Primeira tela, JSON-LD, currículo |
| E | Um depoimento (nome, cargo, empresa, frase) — ou "não tenho" | Bloco de prova social |
| F | URL do LinkedIn; grafia oficial do nome (Cassio ou Cássio) | Currículo, JSON-LD, `<h1>` |
| G | 2–3 fatos com número da V Alves (obras, equipe, compras) | Currículo e seção Obra |
| H | Previsão de formatura; sabe MS Project? | Currículo |

## 2. Rodada 1 — propostas em paralelo (8 agentes, ~15 min cada)

Cada agente recebe: `index.html` atual, `PLANO.md`, esta seção, as respostas do portão, e a regra "fato só da fonte".
Entrega: `portfolio/revisao/propostas/<nome>.md` com (a) o trecho atual, (b) o trecho proposto pronto para colar,
(c) justificativa em 1 linha, (d) perguntas pendentes.

| Agente | Persona | Escopo (só isto) | Saída |
|---|---|---|---|
| `dono` | Dono de construtora | Termos da oferta (C); bloco "O que faço na sua construtora" (4 linhas); frase sobre a Axiom | `dono.md` |
| `eng` | Engenheiro avaliador | Reescrever "0,25% contra a Caixa" como consistência; qualificar "cálculo/pré-dimensionamento estrutural" (bunker, galpão, B-36); escopo dos 36 min na coluna Resultado; indicar qual print serviria como "registro de engenharia" | `eng.md` |
| `ia` | Leitor-máquina / RH 7 s | Cargo-alvo na primeira tela; nome padronizado (F); revisar JSON-LD com D/F/H; ordem dos `<h2>`; `alt` faltantes | `ia.md` |
| `hist` | Storyteller | Parágrafo de 3 frases (contabilidade → obra → sistema) para a primeira tela; fechamento "Faltam 3 semestres…" na seção Contato; marca "caso principal" na folha 01 | `hist.md` |
| `colega` | Futuro colega | Bloco "Como trabalho" (4 linhas tiradas das seis regras e das histórias); frase sobre uso de IA que diz o que é seu | `colega.md` |
| `juridico` | Jurídico / ex-empregador | Lista de tudo que identifica cliente ou expõe a VEKS (texto e imagem); versão generalizada de cada item; parecer sobre "criei / licenciado" conforme A | `juridico.md` |
| `acess` | Acessibilidade + designer | Contraste medido de cada par cor/fundo; excesso de rótulos mono por dobra (quais tirar); foco de teclado nos `details`; ordem de tabulação da barra do celular | `acess.md` |
| `cv` | Currículo/ATS | Aplicar D/F/G/H em `curriculo.html`; conferir que cada linha do currículo bate com o site; teste `pdftotext` | edita **só** `portfolio/curriculo/curriculo.html` |

Só `cv` edita arquivo de produto, porque o currículo tem um único dono.

## 3. Rodada 2 — integração (1 agente, sequencial)

`integrador` lê as 7 propostas + parecer do `juridico`, e aplica em `index.html` nesta ordem:
1. Tudo do `juridico` (remoções e generalizações) — primeiro, para nada sensível sobreviver.
2. `ia` (estrutura, nome, JSON-LD) e `eng` (precisão das afirmações).
3. `dono`, `hist`, `colega` (conteúdo novo) — respeitando o limite: a primeira tela não cresce mais que 1 parágrafo
   + 1 linha de cargo-alvo + 1 linha de termos.
4. `acess`.
Regras: não alterar números; não criar seção nova (usa as existentes); registrar cada mudança em
`portfolio/revisao/CHANGELOG.md` com o agente de origem.
Depois roda `portfolio/build.sh` e regenera as folhas de caso se algum texto delas mudou (`eng`, `juridico`).

## 4. Rodada 3 — verificação (5 agentes em paralelo, só leitura)

| Agente | Confere | Falha se |
|---|---|---|
| `fatos` | Cada número da página contra `PLANO.md`, `ref/cassio-viller.html` e os PDFs de origem | Número novo sem fonte, ou número alterado |
| `sigilo` | Nomes de clientes, margens, dados pessoais, itens não autorizados em B | Qualquer ocorrência |
| `render` | Screenshots em 390/1280/1440; overflow; imagens quebradas; JSON-LD válido; `details` abrem; maquetes com `?maquete=forcar` | Overflow, erro de console, JSON inválido |
| `leitura` | Relê como dono de construtora, engenheiro e RH (as três personas de maior peso) em 60 s cada; lista o que ainda não responde | Pergunta central da persona sem resposta |
| `pdf` | Currículo em 1 página, texto extraível na ordem; folhas de caso em 1 página | Página extra ou texto fora de ordem |

Qualquer falha volta para o `integrador` (não para os agentes da rodada 1). Máximo de 2 ciclos; o que sobrar vira
pendência listada para o Cassio.

## 5. Entrega

- `index.html`, `curriculo.html` e folhas atualizados; `CHANGELOG.md` com origem de cada mudança.
- `portfolio/revisao/PENDENCIAS.md`: o que ficou aberto e por quê (normalmente: depoimento, autorização parcial da VEKS).
- Nada commitado nem publicado; o Cassio revisa o changelog e decide.

## 6. Como executar

- **Com orquestração** (recomendado): rodadas 1 e 3 são fan-out puro; rodada 2 é um agente. Cabe em ~14 agentes
  (8 + 1 + 5). Precisa da sua autorização explícita para rodar um workflow multiagente — diga "rode o workflow" ou
  "use um workflow" quando tiver respondido o portão.
- **Sem orquestração**: eu faço as três rodadas em sequência, sozinho, na mesma ordem. Mais lento, sem custo extra
  de agentes; a qualidade das verificações é a mesma, porque os critérios são os da seção 4.

## 7. Fora deste plano (fica para depois)

- Vídeo de 45 s; limpeza dos PDFs longos (Fase 5 do `PLANO.md`).
- Foto na primeira tela (decisão sua; se quiser, mande a foto e o `hist` propõe o lugar).
- Unir "Ferramentas" a "Obra e projetos" (recomendado, mas muda a numeração das folhas; fazer só depois desta revisão).
