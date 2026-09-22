# Propostas — leitor "dono de construtora"

Escopo: achados 1, 2 e 3 da `REVISAO.md`. Arquivo alvo: `portfolio/site/index.html` (não editado aqui; trechos prontos para o integrador colar). Nenhum CSS novo: tudo reaproveita classes que já existem no arquivo (`.note`, `.tl`, `.when`, `h3` com margem inline, como nas demais colunas do currículo).

---

## Achado 1 — Oferta "me mande uma obra" sem termos

Termos da decisão C: "Sem custo. Devolvo em até 3 dias úteis. O pacote não sai do meu computador." Entram em dois lugares: abaixo dos botões da primeira tela e no bloco Contato.

### 1a — Primeira tela (abaixo dos botões)

**ATUAL** (inserção; trecho imediatamente anterior, linhas 368–371):

```html
  <div class="cta">
    <a class="btn big" href="https://wa.me/5512982071116?text=Ol%C3%A1%2C%20C%C3%A1ssio.%20Vi%20seu%20portf%C3%B3lio%20e%20quero%20te%20mandar%20uma%20obra%20para%20or%C3%A7ar." target="_blank" rel="noopener">Me mande uma obra ↗</a>
    <a class="btn ghost big" href="curriculo-cassio-viller.pdf" target="_blank" rel="noopener">Baixar currículo (PDF) ↓</a>
  </div>
```

**PROPOSTO** (colar logo depois do `</div>` do `.cta`, antes de `<div class="stats s3"`):

```html
  <div class="cta">
    <a class="btn big" href="https://wa.me/5512982071116?text=Ol%C3%A1%2C%20C%C3%A1ssio.%20Vi%20seu%20portf%C3%B3lio%20e%20quero%20te%20mandar%20uma%20obra%20para%20or%C3%A7ar." target="_blank" rel="noopener">Me mande uma obra ↗</a>
    <a class="btn ghost big" href="curriculo-cassio-viller.pdf" target="_blank" rel="noopener">Baixar currículo (PDF) ↓</a>
  </div>
  <p class="note" style="margin-top:12px">Sem custo. Devolvo em até 3 dias úteis. O pacote não sai do meu computador.</p>
```

**Justificativa:** o dono só chama se souber quanto custa, quando volta e onde o projeto dele vai parar — as três respostas cabem numa linha embaixo do botão.

### 1b — Bloco Contato

**ATUAL** (linha 933):

```html
      <p>Você me manda o pacote de projeto. Eu devolvo três documentos — levantamento, orçamento com faixa e proposta no seu modelo — e a gente conversa sobre o resto. Procuro uma posição em gestão de obras, orçamento e controle de custos — ou em melhoria de processos numa construtora que queira parar de viver de planilha.</p>
```

**PROPOSTO:**

```html
      <p>Você me manda o pacote de projeto. Eu devolvo três documentos — levantamento, orçamento com faixa e proposta no seu modelo — e a gente conversa sobre o resto. Procuro uma posição em gestão de obras, orçamento e controle de custos — ou em melhoria de processos numa construtora que queira parar de viver de planilha.</p>
      <p class="note" style="margin-top:10px">Sem custo. Devolvo em até 3 dias úteis. O pacote não sai do meu computador.</p>
```

Observação para o integrador: dentro de `.contact-box`, a regra `.contact-box p` (cor `--ink-2`) vence a cor de `.note`; fonte mono e tamanho `.8rem` ficam. Legível e coerente — não precisa de CSS novo. Se quiser a cor cinza igual à da primeira tela, trocar `<p class="note" …>` por `<span class="note" style="display:block;margin-top:10px">`.

**Justificativa:** quem chega ao Contato pelo trilho não viu a primeira tela; os termos precisam estar ao lado do botão do WhatsApp também.

**Pendências (só o Cássio):**
- Confirmar os três termos (decisão C): sem custo; prazo de até 3 dias úteis (vale para qualquer porte de pacote ou só para o porte do caso dos 36 min?); "o pacote não sai do meu computador" (há algum uso de serviço externo no método que contradiga isso?).

---

## Achado 2 — Falta "o que faço na sua construtora"

Bloco de 4 linhas na seção Currículo, antes de "Experiência". Entra como bloco de largura inteira entre a linha de cota e o `.cv-grid`, usando a mesma lista `.tl` das colunas do currículo (sem CSS novo). O achado 15 ("Como trabalho") entra logo depois deste bloco, antes do `.cv-grid`.

**ATUAL** (inserção; trecho imediatamente anterior, linhas 895–898):

```html
  <div class="cota" aria-hidden="true"><span>2017</span><i></i><span>contabilidade → obra → sistemas</span><i></i><span>hoje</span></div>
  <div class="cv-grid">
    <div>
      <h3 style="margin-bottom:16px">Experiência</h3>
```

**PROPOSTO** (colar entre o `.cota` e o `<div class="cv-grid">`):

```html
  <div class="cota" aria-hidden="true"><span>2017</span><i></i><span>contabilidade → obra → sistemas</span><i></i><span>hoje</span></div>
  <h3 style="margin-bottom:16px">O que faço na sua construtora</h3>
  <ul class="tl" style="margin-bottom:36px">
    <li><b>Levantamento e orçamento de propostas</b><p>Meço no projeto, orço na planilha da empresa e entrego a proposta no seu modelo.</p></li>
    <li><b>Compras com cotação e quadro de concorrência</b><p>Requisição, cotações, quadro de concorrência e conferência do que chegou ao canteiro.</p></li>
    <li><b>Cronograma, diário e medição</b><p>Diário que move o cronograma e calcula a medição, com norma escrita para quem preenche.</p></li>
    <li><b>Fluxo de caixa e custo previsto × realizado</b><p>Lançamentos classificados por regra, obra separada de escritório, custo por centro de custo.</p></li>
  </ul>
  <div class="cv-grid">
    <div>
      <h3 style="margin-bottom:16px">Experiência</h3>
```

Origem de cada linha de apoio (sem fato novo): 1ª — seção Orçamento em 36 min ("levantamento medido no desenho", "mesma planilha que o diretor usa", "proposta no modelo da empresa"); 2ª — obra das baias em Itu ("requisições… cotações e quadro de concorrência") e SIGE ("recebimento conferido"); 3ª — SIGE ("o diário move o cronograma e calcula a medição", "norma escrita do diário"); 4ª — Ferramentas, classificador do fluxo de caixa ("classifica cada lançamento por regras, separa o que é obra do que é empresa… por centro de custo").

**Justificativa:** o dono lê "sistemas" e "36 minutos" e ainda não sabe o que o Cássio faria na segunda-feira; quatro linhas de rotina de obra respondem antes do histórico de empregos.

**Pendências (só o Cássio):**
- Confirmar que as quatro frentes são o que ele quer assumir no cargo (não só o que já fez) e que a ordem reflete a prioridade dele.

---

## Achado 3 — Dúvida "vai embora para a Axiom"

**ATUAL** (linha 906):

```html
        <li><span class="when">projetos próprios</span><b>Axiom — sistemas personalizados e chatbots</b><p>Site institucional e desenvolvimento sob demanda para pequenas empresas.</p></li>
```

**PROPOSTO:**

```html
        <li><span class="when">projetos próprios · sem dedicação de expediente</span><b>Axiom — sistemas personalizados e chatbots</b><p>Site institucional e desenvolvimento sob demanda para pequenas empresas.</p></li>
```

**Justificativa:** a marca de tempo (`.when`) é onde os outros itens dizem "meio período" e "PJ"; é ali que o dono procura quanto do expediente cada coisa toma.

**Pendências (só o Cássio):**
- Confirmar que a Axiom hoje não toma horário de expediente (o site aprovado dizia "empresa própria"; o `PLANO.md` pede "Projetos próprios, sem CEO"). Se houver CNPJ ativo ou cliente em atendimento no horário comercial, a frase precisa mudar.
- O mesmo texto vai para o `curriculo.html` (achado 23, agente `cv`).
