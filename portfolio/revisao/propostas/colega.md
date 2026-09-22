# Propostas — leitor "futuro colega"

Escopo: achados 15 e 16 da `REVISAO.md`. Arquivo alvo: `portfolio/site/index.html` (não editado aqui; trechos prontos para o integrador colar). Nenhum CSS novo: o bloco reaproveita `h3` com margem inline e a lista `.tl`, exatamente como o achado 2 (`dono.md`) e as colunas do currículo.

---

## Achado 15 — Bloco "Como trabalho"

Quatro linhas na seção Currículo, depois do bloco "O que faço na sua construtora" (achado 2) e antes do `.cv-grid`. Cada linha vem de algo que já está escrito na página — nenhum fato novo.

**ATUAL** (inserção; trecho imediatamente anterior no `index.html` de hoje, linhas 895–898):

```html
  <div class="cota" aria-hidden="true"><span>2017</span><i></i><span>contabilidade → obra → sistemas</span><i></i><span>hoje</span></div>
  <div class="cv-grid">
    <div>
      <h3 style="margin-bottom:16px">Experiência</h3>
```

Ordem final para o integrador: `.cota` → bloco do achado 2 ("O que faço na sua construtora") → **este bloco** → `<div class="cv-grid">`. Se o achado 2 ainda não tiver sido colado, este bloco entra direto entre o `.cota` e o `.cv-grid`.

**PROPOSTO** (colar imediatamente antes de `<div class="cv-grid">`, depois do `</ul>` do achado 2):

```html
  <h3 style="margin-bottom:16px">Como trabalho</h3>
  <ul class="tl" style="margin-bottom:36px">
    <li><b>Ensaio antes de gravar</b><p>A carga mostra tudo o que criaria sem gravar nada; só depois grava.</p></li>
    <li><b>Norma escrita para quem preenche</b><p>Sistema não muda hábito sozinho. O combinado com quem preenche vai por escrito.</p></li>
    <li><b>Mudança em dinheiro entra por fases</b><p>Nunca de uma vez para todos: empresa por empresa, com roteiro de volta atrás.</p></li>
    <li><b>Gasto, venda ou promessa: quem assina decide</b><p>Com o número das duas alternativas na mão. Eu recomendo; quem assina decide.</p></li>
  </ul>
  <div class="cv-grid">
    <div>
      <h3 style="margin-bottom:16px">Experiência</h3>
```

Origem de cada linha (tudo já na página): 1ª — história do diário recuperado ("A carga passa por um ensaio que mostra tudo o que seria criado sem gravar nada", "sempre com ensaio antes de gravar"); 2ª — mesma história ("Sistema não muda hábito sozinho... só o acordo com quem preenche evita o próximo buraco. Daí a norma escrita do diário"); 3ª — história 2 ("entrega-se por fases, com roteiro de volta atrás") e bloco Rigor ("Toda mudança arriscada é ligada empresa por empresa, com roteiro de volta atrás"); 4ª — regra 06 dos 36 min ("O que muda o que a empresa gasta, vende ou promete volta para o humano... O método recomenda; quem assina decide").

**Justificativa:** quem vai dividir sala com ele quer saber como ele mexe no que já está rodando e até onde decide sozinho — as quatro linhas respondem isso sem repetir as histórias.

**Pendências (só o Cássio):**
- Confirmar que as quatro regras valem para ele como pessoa (jeito de trabalhar em qualquer empresa), e não só como regras que o SIGE ou o método de orçamento obedecem — o bloco fala na primeira pessoa.
- Na 4ª linha, "Eu recomendo" substitui "O método recomenda" da regra 06. Se ele preferir manter a distância ("O método recomenda"), trocar a palavra.

---

## Achado 16 — Frase sobre IA

Na página o texto diz "assistentes de IA" (a `REVISAO.md` cita "inteligência artificial"; o trecho abaixo é o que está no arquivo). Como a frase já traz "Defini as regras de engenharia e de negócio" e "sob minha revisão", colar o complemento inteiro repetiria "regras de engenharia" e "revisão" duas vezes. A proposta reorganiza a frase para dizer o que o achado pede — regras, testes e revisão são dele — sem repetir nada.

**ATUAL** (linha 470):

```html
    <div><h5>O que fiz</h5><p>Idealizei o sistema que lê o desenho, mede, orça, programa o prazo e gera a proposta. Defini as regras de engenharia e de negócio e dirigi o desenvolvimento, feito com assistentes de IA sob minha revisão. E <b>orcei as obras com ele</b>.</p></div>
```

**PROPOSTO:**

```html
    <div><h5>O que fiz</h5><p>Idealizei o sistema que lê o desenho, mede, orça, programa o prazo e gera a proposta. Dirigi o desenvolvimento, feito com assistentes de IA — as regras de engenharia e de negócio, os testes e a revisão são meus. E <b>orcei as obras com ele</b>.</p></div>
```

Se o integrador preferir mexer o mínimo (só completar, como o achado pede literalmente), a alternativa é:

```html
    <div><h5>O que fiz</h5><p>Idealizei o sistema que lê o desenho, mede, orça, programa o prazo e gera a proposta. Defini as regras de engenharia e de negócio e dirigi o desenvolvimento, feito com assistentes de IA sob minha revisão — as regras de engenharia, os testes e a revisão são meus. E <b>orcei as obras com ele</b>.</p></div>
```

**Justificativa:** um colega lê "feito com IA" e quer saber o que sobra de autoria; dizer que regras, testes e revisão são dele fecha a dúvida numa linha.

**Pendências (só o Cássio):**
- Confirmar que "os testes são meus" é verdade no sentido que um colega vai entender: ele define e confere as verificações automáticas (as 3.300 do bloco Rigor), mesmo que o código delas tenha sido escrito com assistentes.
- A mesma frase existe no `curriculo.html` (linha 96: "Desenvolvimento dirigido por mim, com assistentes de IA sob minha revisão."). Se o site mudar, o agente `cv` decide se o currículo acompanha (achado 23 não lista isso; fica a critério do Cássio).
