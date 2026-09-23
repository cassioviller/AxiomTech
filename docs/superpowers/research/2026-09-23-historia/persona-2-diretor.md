# Persona 2 — Eduardo, diretor de engenharia de construtora LSF

## Quem é
Eduardo tem 20 anos de obra. Começou como estagiário de campo, hoje é diretor de engenharia e sócio de uma construtora que fabrica e monta Light Steel Frame. Já viu orçamento estourar por preço desatualizado, por escopo mal entendido, por subestimar a logística de canteiro — e sabe que quem paga a conta é sempre o prazo e a margem. Não lê currículo bonito: lê número. Abre `historia.html` à noite, no notebook da sala, depois do jantar, com o WhatsApp da obra ainda piscando. Não vai rolar a página inteira por educação — só continua se as duas ou três primeiras telas provarem, com um número verificável, que quem escreveu entende orçamento, cronograma e risco melhor do que a média dos currículos que recebe. Ele mesmo usa IA em planilha, mas não confia em quem promete "revolução" sem mostrar a fonte do número. Quer contratar alguém que reduza risco, não alguém que crie mais um relatório bonito e frágil.

## O que o convence — e o que o faz fechar a aba
Convence:
- Um número com origem declarada na mesma tela (base, data, escopo do que foi medido) — porque ele mesmo cobra isso de quem faz orçamento na obra dele.
- Vocabulário técnico correto e no lugar certo: SINAPI, BDI, cronograma físico-financeiro, curva S, medição — usados com precisão, não como enfeite.
- Prova em obra real, não só maquete: o SIGE rodando numa empresa de LSF de verdade, com atraso real medido (27,6% → 44,7% contra 60,8% planejado), pesa mais para ele do que qualquer tela de sistema "no papel".
- Reconhecer um limite antes de ele perguntar — "a parte de gestão de obra desse sistema ainda não rodou numa obra real" dito de bate-pronto vale mais do que qualquer alarde de resultado.
- Deixar claro que a IA foi usada sob direção do candidato, com verificação humana — não como caixa-preta que "decide sozinha".

Fecha a aba:
- Número sem unidade, sem escopo ou sem data ("orçamentos 40% mais rápidos", sem dizer o quê, quando, contra o quê).
- Qualquer mistura entre as telas de sistemas diferentes (SIGE com sistema de orçamento) — para quem lê tela de obra o dia inteiro, a inconsistência salta e derruba a credibilidade de tudo o resto.
- Linguagem de vendedor de software ("revolucionário", "automático", "resolve tudo") em vez de linguagem de quem mede.
- "Fiz tudo sozinho" — quem constrói orçamento isolado, sem checagem cruzada com gente de obra, é sinal de alerta, não de mérito.
- Página lenta ou que exige interação (hover, clique) para revelar a ressalva de um número — se a ressalva não está visível de cara, ele desconfia que está escondida de propósito.

## O que a pesquisa diz
- Vagas e conteúdo de carreira de analista de orçamento/planejamento pedem leitura de projetos, levantamento de quantitativos, composição de custos, cronograma físico-financeiro e domínio de planilhas/softwares (Sienge, MS Project, Excel avançado) como base técnica mínima. [fonte](https://blog.altoqi.com.br/lideranca-e-carreira/profissao-orcamentista)
- O mesmo material cita "trabalhar sozinho" como receita para o insucesso do orçamentista — colaboração e checagem cruzada são valorizadas, isolamento é red flag comportamental. [fonte](https://blog.altoqi.com.br/lideranca-e-carreira/profissao-orcamentista)
- Um levantamento de causas de estouro orçamentário em obras lista 14 causas recorrentes, entre elas detalhamento deficiente de engenharia, estimativas defasadas e falta de acompanhamento do orçado versus comprado — todas ligadas a números que perderam a origem ou não foram atualizados. [fonte](https://pmkb.com.br/artigos/causas-de-estouro-em-orcamento-sao-inadmissiveis/)
- Artigos de erros comuns de orçamento apontam BDI aplicado incorretamente (omitindo encargos para "parecer competitivo") e uso de preços desatualizados sem validação de mercado como falhas frequentes. [fonte](https://www.noventa.com.br/blog/orcamento-de-obras-7-erros-que-podem-comprometer-todo-o-projeto)
- A prática recomendada é incluir reserva de contingência de 5% a 10% do custo total do orçamento para cobrir imprevistos (clima, greve, geotecnia) — orçamento "enxuto" sem essa margem é tratado como erro. [fonte](https://www.brickup.app/post/10-erros-comuns-no-orcamento-de-obras-e-como-evita-los-o-guia-definitivo-para-a-gestao-de-custos)
- A tabela SINAPI é atualizada mensalmente e o orçamento executivo deve sempre ser baseado na referência mais atual disponível — ou seja, a data/versão da base usada é parte do que dá confiabilidade ao número. [fonte](https://sienge.com.br/blog/tabela-sinapi-no-orcamento-da-obra/)
- O setor de construção tem cultura historicamente conservadora e avessa a risco: apenas 19% das empresas do setor imobiliário já usam alguma ferramenta de IA (pesquisa Abrainc), e apenas 39% das organizações e 15% dos funcionários usam IA regularmente segundo a FGV IBRE — ceticismo é a norma, não a exceção. [fonte](https://sienge.com.br/inteligencia-artificial-na-construcao-civil/)
- Falta de explicabilidade nas decisões de uma ferramenta de IA compromete diretamente a auditoria e a confiança de quem decide — quanto mais claro o "como cheguei nesse número", mais fácil a ferramenta (e quem a construiu) ganhar confiança. [fonte](https://sienge.com.br/inteligencia-artificial-na-construcao-civil/)
- No Light Steel Frame, os painéis chegam pré-fabricados ao canteiro, reduzindo etapas de execução e permitindo obra até 50% mais ágil que o método convencional, com menos desperdício — o que faz de logística de transporte e montagem um tema com apelo direto para quem dirige uma construtora de LSF. [fonte](https://www.abcem.org.br/site/blog/light-steel-framing-o-modelo-de-constru%C3%A7%C3%A3o-flexivel-para-todos-os-projetos)

## Requisitos para o plano
1. **P2-01 — MUST**: toda frase com número tem, na mesma cena, a origem ou a ressalva em até 1 linha (base/data, escopo do que foi medido, ou "estimativa"/"não rodou em obra real ainda"). Testável: nenhuma cena com dígito passa sem uma segunda linha de ressalva visível sem interação.
2. **P2-02 — MUST**: a cena do desvio de 0,25% nos 19 serviços SINAPI nomeia explicitamente "SINAPI" e o escopo ("19 serviços conferidos"), nunca generaliza para "o orçamento inteiro" ou "o sistema acerta tudo".
3. **P2-03 — MUST**: nenhuma cena mistura imagens do SIGE com as do sistema de orçamento (regra já existente no contexto). Testável: cada `<figure>` da cena usa só arquivos do mesmo prefixo (`o-*`/`p-*`).
4. **P2-04 — MUST**: a cena do SIGE usa verbo de constatação, não de solução mágica — "o diário mostrou a obra em 44,7% contra 60,8% planejado", nunca "o sistema resolveu o atraso". Evita o overclaiming que um diretor de obra identificaria na hora.
5. **P2-05 — MUST**: pelo menos uma cena nomeia corretamente um termo técnico do ofício (BDI, cronograma físico-financeiro, curva S ou medição) em vez de parafrasear de forma vaga — sinaliza domínio de vocabulário a um leitor que usa esses termos todo dia.
6. **P2-06 — SHOULD**: a cena que descreve o papel da IA evita "revolucionário"/"automático" e usa verbo de responsabilidade do autor ("eu configurei", "eu conferi", "sob minha direção") — alinhado ao ceticismo documentado do setor sobre falta de explicabilidade.
7. **P2-07 — MUST**: pelo menos uma cena declara, sem ser perguntada, uma limitação não resolvida (ex.: "a parte de gestão de obra desse sistema ainda não rodou numa obra real") — antes do CTA final, nunca depois.
8. **P2-08 — SHOULD**: a cena das casas modulares (B-36) usa vocabulário de logística real (caixas, viagens, decisões registradas) que ecoa o argumento de industrialização/transporte de painéis do LSF, sem precisar explicar o que é LSF a quem já vive disso.
9. **P2-09 — MUST**: o CTA final ("Me mande uma obra") só aparece depois de pelo menos uma prova em obra real de LSF (o caso do SIGE), não apenas depois de simulações ou maquetes — porque para este leitor "já rodou numa obra de verdade?" é a pergunta que decide tudo.
10. **P2-10 — SHOULD**: a página é legível parada, sem depender de hover/clique para revelar ressalva ou fonte — compatível com o hábito de leitura calma, à noite, no computador.

## Riscos e armadilhas
- Deixar a descoberta da limitação ("gestão de obra do sistema nunca rodou em obra real") para o leitor achar sozinho — se Eduardo perceber isso depois de já ter acreditado no oposto, a confiança quebra de vez, não só naquele número.
- Confundir, mesmo que por um segundo, uma tela do SIGE com uma do sistema de orçamento — para quem lê tela de obra o dia inteiro, isso não passa despercebido e derruba a credibilidade do resto da história.
- Escrever a parte de IA em tom de vendedor ("plataforma inteligente", "automatizado") em vez de tom de quem verificou linha por linha — o setor já é cético com IA e pune quem soa a promessa vazia.
- Apresentar o desvio de 0,25% ou os 36 minutos sem o escopo exato (quantos serviços, que obra, medido como) — vira número "bonito demais" e ele desconfia por hábito profissional.
- Deixar implícito "fiz tudo sozinho" — mesmo sendo verdade que ele dirigiu assistentes de IA, o texto precisa deixar claro que os números vêm de obras reais (VEKS, V Alves, Estruturas do Vale) e foram conferidos, não inventados numa mesa sozinho.
- Cenas iniciais fracas: como ele só continua "se o começo convencer", qualquer abertura genérica (sem número, sem tese clara) custa o resto da leitura antes mesmo de chegar ao SIGE, que é a prova mais forte para o perfil dele.

## Quais provas do contexto usar e em que ordem
1. Tese de abertura — "um número sem origem custa caro na obra. Eu construí o jeito de ele não sumir." — sem números ainda, estabelece o problema que ele já viveu na pele.
2. **36 minutos** (zip → proposta de mão de obra assinável, 11:35 → 12:11) com a ressalva "à mão: ~2 dias úteis (estimativa)" — prova de velocidade medida, não estimada, e fácil de verificar mentalmente.
3. **Sistema de orçamento**: desvio máximo de 0,25% nos 19 serviços SINAPI conferidos — fala direto com a preocupação dele sobre base de custo e precisão.
4. Menções a informação interna caindo de 71 para 0 numa proposta — prova de cuidado profissional com confidencialidade, relevante para quem manda proposta a cliente.
5. Ressalva explícita da parte não testada ("a parte de gestão de obra desse sistema ainda não rodou numa obra real") — antes de mostrar o SIGE, para não parecer omissão.
6. **SIGE em uso numa empresa de LSF real**, com a obra em 27,6% → 44,7% contra 60,8% planejado — a prova mais importante para este leitor especificamente: é LSF, é obra real, é atraso real medido, não maquete.
7. **Casas modulares B-36** — o celeiro que não cabe no caminhão, vai em duas caixas, três viagens, 37 decisões registradas — ressoa com o argumento de industrialização e logística de painéis do LSF.
8. Fechamento: "Faltam 3 semestres para o diploma. Não falta obra feita." + CTA "Me mande uma obra" (WhatsApp) — só depois de pelo menos uma prova em obra real ter aparecido.

## Fontes
- [Profissão orçamentista: tudo o que você precisa saber — AltoQI](https://blog.altoqi.com.br/lideranca-e-carreira/profissao-orcamentista)
- [PMKB — Causas de estouro em orçamento são inadmissíveis](https://pmkb.com.br/artigos/causas-de-estouro-em-orcamento-sao-inadmissiveis/)
- [Noventa — Orçamento de Obras: 7 erros que podem comprometer todo o projeto](https://www.noventa.com.br/blog/orcamento-de-obras-7-erros-que-podem-comprometer-todo-o-projeto)
- [Brickup — 10 Erros Comuns no Orçamento de Obras e Como Evitá-los](https://www.brickup.app/post/10-erros-comuns-no-orcamento-de-obras-e-como-evita-los-o-guia-definitivo-para-a-gestao-de-custos)
- [Sienge — Tabela SINAPI da Caixa: como usar no orçamento da obra](https://sienge.com.br/blog/tabela-sinapi-no-orcamento-da-obra/)
- [Sienge — Inteligência Artificial na Construção Civil](https://sienge.com.br/inteligencia-artificial-na-construcao-civil/)
- [ABCEM — Como funciona o sistema Light Steel Framing?](https://www.abcem.org.br/site/blog/light-steel-framing-o-modelo-de-constru%C3%A7%C3%A3o-flexivel-para-todos-os-projetos)
