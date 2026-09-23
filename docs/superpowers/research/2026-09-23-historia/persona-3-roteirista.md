# Persona 3 — Lia, roteirista de narrativa de marca pessoal

## Quem é

Lia escreve textos curtos para sites de pessoas e empresas. Não pensa em "copy que converte" nem em SEO — pensa em arco narrativo, ritmo de leitura e numa ideia por tela. Antes de escrever a primeira frase, ela decide qual é a estrutura que sustenta o conjunto: onde fica a virada, onde fica a resolução, o que pode ser cortado sem quebrar o fio. Para `historia.html` ela trata cada tela como uma "página" de um roteiro: uma frase grande carrega a ideia, uma linha pequena carrega a prova (ou a ressalva), e o fundo muda de cena para marcar a passagem de uma ideia para a próxima — nunca as duas coisas na mesma tela.

## O arco que ela recomenda (e por quê)

Lia recomenda um híbrido de três peças, não uma estrutura só:

1. **ABT (E — MAS — PORTANTO)** como espinha dorsal de tensão. É o formato mais compacto que existe para isso: funciona numa frase, num parágrafo ou numa peça inteira, e evita que 10 telas de conquistas separadas soem como uma "listagem monótona de dados" (o efeito "e, e, e"). No roteiro, o "mas" é reservado para um único ponto — a virada contabilidade → obra, onde o número deixa de ser abstrato — porque um "mas" em toda tela dilui a tensão em vez de aumentá-la.
2. **Story Spine da Pixar** para não perder o fio cronológico. As experiências de Cássio (contabilidade, obra, sistema de orçamento, SIGE, casas modulares) são dispersas por natureza; o spine (era uma vez / todo dia / até que um dia / por causa disso, por causa disso, por causa disso / até que finalmente / e desde então) dá um encaixe pronto para cada "por causa disso" virar uma tela de prova, em vez de uma lista solta de projetos.
3. **StoryBrand, só para o fechamento.** Não faz sentido aplicar "o cliente é o herói" à peça inteira — aqui o protagonista da história é o próprio Cássio. Mas nas duas últimas telas, o leitor (recrutador) entra como quem tem um problema real (número sem origem custando caro), e o candidato aparece como quem já construiu a resposta — o guia com prova, não o herói. É isso que faz o CTA final ("me mande uma obra") soar como continuação da história, não como pedido de emprego solto.

Ela descarta a **Jornada do Herói completa**: 8 a 10 telas não comportam 12 etapas sem espremer cada uma a ponto de virar legenda, e a própria literatura de branding já registra fadiga com a fórmula aplicada a toda história curta — a recomendação corrente é usar pedaços dela, não a estrutura inteira.

## O que a pesquisa diz

- O ABT (E, MAS, PORTANTO) funciona em qualquer escala — uma frase, um parágrafo, uma peça inteira —, e o "mas" é o que evita a "listagem monótona de dados, fatos e resultados": é o formato mais compacto para transformar uma lista de conquistas em tensão e resolução. [fonte](https://www.sesync.org/resources/communications-toolkit-and-therefore-statement)
- O StoryBrand recomenda tratar quem lê como o herói e a marca como o guia que já resolveu o problema dele; serve para as telas finais, onde o leitor é o recrutador com um problema concreto — não para o roteiro inteiro, que continua sendo a história do candidato. [fonte](https://yukaichou.com/gamification-analysis/storybrand-donald-miller-customer-as-hero/)
- O Story Spine da Pixar (Era uma vez / Todo dia / Até que um dia / Por causa disso, por causa disso, por causa disso / Até que finalmente / E desde então) dá uma sequência pronta para transformar experiências dispersas num único fio; cada "por causa disso" pode virar uma tela de prova. [fonte](https://www.storyprompt.com/blog/the-story-spine-also-known-as-pixars-story-structure)
- A Jornada do Herói completa é vista como longa e formulaica demais quando o protagonista é uma pessoa só e o formato é curto; a recomendação é usar "pedaços" dela, não as 12 etapas inteiras. [fonte](https://umbrex.com/resources/frameworks/marketing-frameworks/heros-journey-storytelling-structure-for-brands/) [fonte](https://wordsbypeta.com/why-the-heros-journey-is-the-wrong-model-for-your-brand-story/)
- Em scrollytelling, a prática recomendada é "poucos passos para prender o leitor, fazer o ponto, e sair"; cada passo deve funcionar sozinho, como um cartão independente, e o texto deve ser cortado primeiro pensando em mobile (o que empurra para frases mais curtas, não mais longas). [fonte](https://pudding.cool/process/responsive-scrollytelling/)
- O padrão técnico do setor para scrollytelling é o Scrollama, baseado em `IntersectionObserver`, sem sequestrar o scroll — o mesmo modelo já escolhido para `historia.html` — o que confirma que o roteiro pode seguir a lógica de "um passo, uma revelação". [fonte](https://pudding.cool/process/introducing-scrollama/)
- A velocidade média de leitura silenciosa de um adulto fica entre 200 e 300 palavras por minuto (meta-análise de 190 estudos, 18.573 participantes); a 250 wpm, uma frase de 10 palavras leva pouco mais de 2 segundos — isso dá um teto real de densidade por tela. [fonte](https://www.sciencedirect.com/science/article/abs/pii/S0749596X19300786)
- Histórias de origem para marca pessoal funcionam melhor mostrando os eventos que moldaram a pessoa — inclusive os tropeços — e mantendo a primeira pessoa do início ao fim, em vez de uma bio seca em terceira pessoa. [fonte](https://copyposse.com/blog/4-types-of-stories-to-build-your-personal-brand/)
- Ressalvas ("small print") perdem força quando aparecem isoladas, longe da afirmação que qualificam; a recomendação de quem regula publicidade é pôr a ressalva perto do número que ela qualifica, não separada dele — argumento a favor da linha pequena de apoio sob toda frase com número, já prevista para a página. [fonte](https://www.asa.org.uk/advice-online/smallprint-and-footnotes.html)

## Roteiro proposto

Todos os números vêm do arquivo de contexto (`00-contexto.md`); nenhum é inventado.

| # | frase grande (≤ 10 palavras) | linha pequena de apoio/ressalva | papel no arco |
|---|---|---|---|
| 1 | Um número sem origem custa caro na obra. | Cássio Viller, estudante de Engenharia Civil (7º semestre), mira orçamento, planejamento e custos. | **E** (abertura da tese) — primeira metade da frase de tese; abre a tensão sem resolver. |
| 2 | Comecei contando números na contabilidade da família. | Escritório da família, desde 2017. | **E** (mundo antigo) — "todo dia" do story spine: a rotina antes da obra. |
| 3 | Na obra, o número virou problema de verdade. | Passagens por VEKS Engenharia, V Alves e Estruturas do Vale. | **MAS** (virada) — único "mas" do roteiro; o número deixa de ser abstrato. |
| 4 | De um zip a uma proposta em 36 minutos. | 11:35 → 12:11, ampliação de unidade de saúde (26 ambientes, 328 m²); à mão, cerca de 2 dias úteis (estimativa). | **PORTANTO 1** — primeira resposta construída, provada em tempo. |
| 5 | Treze obras no sistema; onze já viraram proposta. | De R$ 29 mil a R$ 24,5 milhões. A gestão de obra desse sistema ainda não rodou numa obra real. | **PORTANTO 2** — a resposta ganha escala; ressalva de limite dita sem rodeio. |
| 6 | Nos serviços conferidos, o desvio máximo foi 0,25%. | 19 serviços SINAPI conferidos; menções a informação interna caíram de 71 para 0. | **PORTANTO 2** (continuação) — a resposta ganha precisão. |
| 7 | Numa obra real, a gestão saiu do WhatsApp. | SIGE: 23 diários recuperados do WhatsApp; obra em 44,7% (era 27,6%), contra 60,8% planejado — lido numa cópia real do sistema. | **PORTANTO 3** — a resposta funciona fora do papel, num sistema distinto (SIGE, não o de orçamento). |
| 8 | Até uma casa que não cabe no caminhão. | Celeiro B-36: duas caixas, três viagens, 37 decisões registradas. | **PORTANTO 4 / clímax** — a mesma lógica alcança um domínio novo (logística de casas modulares). |
| 9 | Eu construí o jeito de ele não sumir. | Contabilidade, obra e sistemas — um caminho só. | **LOGO** (resolução) — segunda metade da tese; fecha o eco com a tela 1. |
| 10 | Faltam 3 semestres para o diploma. Não falta obra feita. | "Me mande uma obra" (WhatsApp) → leva também ao site completo. | **CTA** — StoryBrand invertido: o recrutador entra com o problema, o convite fecha a história. |

## Requisitos para o plano

1. **P3-01 (MUST):** cada frase grande tem no máximo 10 palavras — testável por contagem simples de tokens separados por espaço.
2. **P3-02 (MUST):** cada tela carrega uma única ideia (um fato, uma virada ou uma decisão); nenhuma frase grande pode juntar duas afirmações com "e" ou vírgula coordenativa.
3. **P3-03 (MUST):** toda frase grande que contém um número tem, na mesma tela, uma linha pequena de apoio/ressalva — sem exceção, conforme a regra do contexto ("nenhuma ressalva apagada").
4. **P3-04 (MUST):** a tese abre a tela 1 (primeira metade: "Um número sem origem custa caro na obra.") e fecha a tela 9 (segunda metade: "Eu construí o jeito de ele não sumir."), criando eco entre início e resolução.
5. **P3-05 (MUST):** nenhuma tela mistura números do sistema de orçamento (telas 5–6) com números do SIGE (tela 7) — regra herdada do contexto comum.
6. **P3-06 (SHOULD):** a palavra "mas" (ou equivalente estrutural de virada/conflito) aparece uma única vez no roteiro, na tela 3; as demais transições usam "portanto"/"e então", para não competir por tensão com a virada real.
7. **P3-07 (SHOULD):** primeira pessoa ("eu", "construí") do início ao fim; segunda pessoa ("você") no máximo uma vez, reservada à tela de CTA, para não soar como script de vendas.
8. **P3-08 (MUST):** somando as 10 frases grandes (≤ 100 palavras no total), a leitura de cada tela isolada fica abaixo de ~3 segundos a 200–300 wpm — teto de densidade por tela, não média do conjunto.
9. **P3-09 (MUST):** nenhum número ou fato aparece no roteiro sem estar listado em `00-contexto.md`; toda cifra é rastreável a uma linha específica do arquivo de contexto.
10. **P3-10 (SHOULD):** a linha pequena de apoio/ressalva não ultrapassa ~20 palavras, para não competir visualmente com a frase grande nem forçar o leitor a parar de rolar.

## Riscos e armadilhas

- **Diluir o "mas".** Se cada tela tentar ter sua própria pequena virada, nenhuma vira de fato — a tensão da tese (contabilidade → obra) precisa ficar isolada como o único ponto de conflito real do roteiro.
- **Jornada do Herói disfarçada.** É tentador esticar o roteiro para caber mentor/provação/abismo/elixir; com 8–10 telas isso produz telas de transição vazias, sem fato novo — cortar para o Story Spine evita esse inchaço.
- **StoryBrand ao pé da letra.** Tratar o recrutador como "herói" do início ao fim faria o texto soar como funil de vendas para uma vaga; a inversão só funciona nas duas últimas telas, depois que a história do candidato já foi contada.
- **Ressalva em bloco no fim.** Empilhar todas as ressalvas numa tela de "letras miúdas" no final mata a credibilidade — cada ressalva precisa ficar colada ao número que ela qualifica, tela por tela.
- **Confundir SIGE com o sistema de orçamento.** A tela 6 (SINAPI, 0,25%) e a tela 7 (SIGE, 44,7%) usam números de sistemas diferentes; qualquer reescrita futura que os aproxime demais no texto corre o risco de o leitor achar que é a mesma ferramenta.
- **Linha pequena virar parágrafo.** Ao tentar caber ressalva + contexto + fonte na mesma linha (caso da tela 7, que já chega a ~20 palavras), o risco é ultrapassar o limite e quebrar o ritmo de leitura por tela.
- **Tela 8 como não sequitur.** Casas modulares é o salto mais distante da linha "orçamento/planejamento"; sem uma frase de transição que amarre a mesma lógica (decisão registrada = número com origem), ela pode ler como projeto solto, não como clímax do arco.

## Fontes

- [SESYNC — Communications Toolkit: And, But, Therefore Statement](https://www.sesync.org/resources/communications-toolkit-and-therefore-statement)
- [Yukai Chou — StoryBrand Framework: Customer as Hero, Brand as Guide](https://yukaichou.com/gamification-analysis/storybrand-donald-miller-customer-as-hero/)
- [StoryPrompt — The Story Spine (também conhecido como Estrutura de Storytelling da Pixar)](https://www.storyprompt.com/blog/the-story-spine-also-known-as-pixars-story-structure)
- [Umbrex — Hero's Journey Storytelling Structure for Brands](https://umbrex.com/resources/frameworks/marketing-frameworks/heros-journey-storytelling-structure-for-brands/)
- [Words by Peta — Why the Hero's Journey Is the Wrong Model for Your Brand Story](https://wordsbypeta.com/why-the-heros-journey-is-the-wrong-model-for-your-brand-story/)
- [The Pudding — Responsive scrollytelling best practices](https://pudding.cool/process/responsive-scrollytelling/)
- [The Pudding — An Introduction to Scrollama.js](https://pudding.cool/process/introducing-scrollama/)
- [ScienceDirect — How many words do we read per minute? A review and meta-analysis of reading rate](https://www.sciencedirect.com/science/article/abs/pii/S0749596X19300786)
- [Copyposse — 4 Types of Stories To Build Your Personal Brand](https://copyposse.com/blog/4-types-of-stories-to-build-your-personal-brand/)
- [ASA | CAP — Small print and footnotes](https://www.asa.org.uk/advice-online/smallprint-and-footnotes.html)
