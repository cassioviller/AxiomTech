# Propostas — agente `acess` (acessibilidade e design)

Escopo: achados 20, 21 e 22 da `REVISAO.md`. Arquivo alvo: `portfolio/site/index.html` (não editado; só propostas).
Todos os trechos "ATUAL" são cópia exata do arquivo e servem para busca. Contrastes medidos pela fórmula WCAG 2.x (relação de luminância).

---

## Achado 20 — Contraste

### O que foi medido

| Par (tema claro) | Onde aparece | Contraste | AA (texto pequeno = 4,5:1) |
|---|---|---|---|
| `--muted` #5B6672 sobre `--ground` #ECEBE6 | rótulos do trilho, `.stats span`, legendas | **4,90:1** | passa |
| `--muted` #5B6672 sobre `--surface` #FFFFFF | legendas em cartão, `.ba .a`, `h5` | **5,85:1** | passa |
| `--muted` #5B6672 sobre `--surface-2` #F5F4F0 | `.shot figcaption` | **5,32:1** | passa |
| `--accent` #D4551B sobre `--ground` #ECEBE6 | `.eyebrow`, `.cota`, `.laws i`, `summary .n` | **3,44:1** | **falha** |
| `--accent` #D4551B sobre `--surface` #FFFFFF | `.eyebrow` em cartão, `.tag.hot`, `.flow i` | **4,11:1** | **falha** |
| `--accent-ink` #FFFFFF sobre `--accent` #D4551B | botões `.btn`, `.rail .cv`, `.topbar a` | **4,11:1** | **falha** |
| texto sobre azul-aço #2E4763 (#fff, #F2B896, #D7E1EC, #C9D6E3, #B9C8D6) | `.case-banner`, `.savings` | 9,56 / 5,49 / 7,22 / 6,47 / 5,59 | passa |
| barra `.bar.hot` (#D4551B sobre #2E4763) | gráfico de tempo | **2,33:1** | falha o 3:1 de elemento gráfico |

| Par (tema escuro) | Onde aparece | Contraste | AA |
|---|---|---|---|
| `--muted` #93A0AD sobre #12171D / #1A2129 / #202932 | idem | 6,75 / 6,09 / 5,53 | passa |
| `--accent` #F07A3E sobre #12171D / #1A2129 | eyebrows, cotas | 6,48 / 5,84 | passa |
| `--accent-ink` #161616 sobre #F07A3E | botões | 6,51 | passa |
| **#FFFFFF sobre `--steel` = #9DBBD8** | `.case-banner`, `.savings` (fundo vira azul-claro no escuro) | **1,99:1** | **falha grave** |
| #F2B896 / #D7E1EC / #C9D6E3 / #B9C8D6 sobre #9DBBD8 | idem | 1,15 / 1,51 / 1,35 / 1,17 | **falha grave** |

Conclusão: `--muted` está resolvido. Faltam três correções: (a) o laranja do tema claro; (b) o painel azul-aço no tema escuro; (c) a barra laranja sobre azul.

### 20a — Laranja do tema claro

**ATUAL** (linha 50, dentro de `:root{`):
```
  --accent:#D4551B; --accent-ink:#FFFFFF; --steel:#2E4763; --steel-soft:#DCE4EC; --rule:#D3D1CA; --rule-soft:#E4E2DC;
```

**PROPOSTO**:
```
  --accent:#B5440E; --accent-ink:#FFFFFF; --steel:#2E4763; --steel-soft:#DCE4EC; --rule:#D3D1CA; --rule-soft:#E4E2DC;
```

Justificativa: mesmo tom, um passo mais escuro — eyebrow sobre o fundo sobe de 3,44 para **4,63:1**, sobre branco para **5,53:1**, e o texto branco dos botões de 4,11 para **5,53:1**; o tema escuro (#F07A3E) não muda.

Pendência: o laranja é cor de identidade do site — o Cássio precisa aprovar o tom #B5440E (ver lado a lado com #D4551B). O `og.png`, o `theme-color` e o laranja da maquete 3D (`maquetes.js`, `ORANGE=0xF07A3E`) não são afetados; se as folhas de caso em PDF usam #D4551B, alinhar depois com o agente das folhas.

### 20b — Painel azul-aço no tema escuro

Hoje `.case-banner` e `.savings` usam `var(--steel)` como fundo, mas o texto dentro deles é fixo (#fff, #F2B896, #D7E1EC…). No escuro `--steel` vira #9DBBD8 e o painel fica azul-claro com letra branca (1,99:1). O fundo do painel precisa ser fixo como o texto já é.

**ATUAL** (linha 50, dentro de `:root{`, após aplicar 20a):
```
  --accent:#B5440E; --accent-ink:#FFFFFF; --steel:#2E4763; --steel-soft:#DCE4EC; --rule:#D3D1CA; --rule-soft:#E4E2DC;
```

**PROPOSTO** (acrescenta o token `--steel-panel`; não precisa de versão escura — os dois blocos escuros herdam do `:root`):
```
  --accent:#B5440E; --accent-ink:#FFFFFF; --steel:#2E4763; --steel-panel:#2E4763; --steel-soft:#DCE4EC; --rule:#D3D1CA; --rule-soft:#E4E2DC;
```

**ATUAL** (linha 122):
```
.case-banner{background:var(--steel);color:#fff;padding:26px 28px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px 28px;align-items:end;margin-bottom:28px}
```

**PROPOSTO**:
```
.case-banner{background:var(--steel-panel);color:#fff;padding:26px 28px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:16px 28px;align-items:end;margin-bottom:28px}
```

**ATUAL** (linha 190):
```
.savings{margin-top:44px;background:var(--steel);color:#fff;padding:24px 26px;display:grid;gap:14px}
```

**PROPOSTO**:
```
.savings{margin-top:44px;background:var(--steel-panel);color:#fff;padding:24px 26px;display:grid;gap:14px}
```

Justificativa: nos dois temas o painel fica #2E4763 e todos os pares de texto voltam para 5,49:1 ou mais; no fundo escuro #12171D o painel ainda se destaca (1,88:1 de diferença de superfície, suficiente para um bloco com borda de cor).

Pendência: nenhuma.

### 20c — Barra laranja sobre azul-aço

Com 20a a barra `.bar.hot` (fundo `var(--accent)`) cairia para 1,73:1 sobre o painel. Fixar a cor da barra no laranja claro, como o relógio da maquete já faz.

**ATUAL** (linha 198):
```
.bar.hot .track i{background:var(--accent);min-width:8px}
```

**PROPOSTO**:
```
.bar.hot .track i{background:#F07A3E;min-width:8px}
```

Justificativa: elemento gráfico sobre #2E4763 sobe de 2,33 para **3,44:1** (mínimo 3:1 para gráficos), nos dois temas.

Pendência: nenhuma.

---

## Achado 21 — Excesso de rótulos mono por dobra

Critério: onde a seção já tem carimbo (`.carimbo`), o `.eyebrow` de um `.sec-head` (ou de um cabeçalho de bloco) só fica se disser algo que o carimbo e o título não dizem.

**Ficam** (acrescentam informação): eyebrow da primeira tela ("Engenharia Civil · 7º semestre…" — o achado 8 pendura o cargo-alvo nele); "Para o cliente / Para a empresa / Para a próxima rodada" (dizem a quem serve cada entregável); "Por que dá para confiar num orçamento de 36 minutos" (é o argumento, não um rótulo); "Sem maquiagem" (a REVISAO manda manter o bloco); "Conferência / Do custo ao preço / E o prazo" (são o único título dos cartões); "Tempo até a proposta" (único rótulo do gráfico).

**Saem** (8 remoções): repetem o carimbo, o título logo abaixo ou a numeração 01–03 das histórias. Nenhuma remoção exige CSS: `.sec-head` é `flex` em coluna com `gap`, e some um filho.

### 21a — Seção Sistema, cabeçalho das três obras

**ATUAL** (linhas 488–491):
```
  <div class="sec-head" style="margin-top:44px">
    <span class="eyebrow">Três obras, do desenho à proposta</span>
    <h3>O que aconteceu quando o sistema encontrou obra de verdade</h3>
  </div>
```

**PROPOSTO**:
```
  <div class="sec-head" style="margin-top:44px">
    <h3>O que aconteceu quando o sistema encontrou obra de verdade</h3>
  </div>
```

Justificativa: as três histórias já vêm numeradas 01–03 e o título diz o resto.

### 21b — Seção Sistema, dentro do detalhe "como o sistema chega ao preço"

**ATUAL** (linhas 522–526):
```
  <div class="sec-head" style="margin-top:44px">
    <span class="eyebrow">Como o sistema chega ao preço</span>
    <h3>Um exemplo do começo ao fim: 1 m² de parede de drywall</h3>
```

**PROPOSTO**:
```
  <div class="sec-head" style="margin-top:44px">
    <h3>Um exemplo do começo ao fim: 1 m² de parede de drywall</h3>
```

Justificativa: o `summary` que abre o bloco já diz "Ver como o sistema chega ao preço"; o leitor acabou de clicar nisso.

### 21c — Seção SIGE, faixa azul

**ATUAL** (linhas 603–605):
```
    <div>
      <span class="eyebrow">SIGE · Sistema de gestão para construtoras</span>
      <h3>Concebido, construído, implantado — e licenciado</h3>
```

**PROPOSTO**:
```
    <div>
      <h3>Concebido, construído, implantado — e licenciado</h3>
```

Justificativa: é o mesmo texto do carimbo da folha ("SIGE · sistema de gestão para construtoras"), a 20 linhas de distância. (O texto do `<h3>` — "licenciado" — é assunto do achado 18, decisão A; aqui não se mexe nele.)

### 21d — Seção SIGE, cabeçalho das três histórias

**ATUAL** (linhas 621–624):
```
  <div class="sec-head" style="margin-top:44px">
    <span class="eyebrow">Três histórias</span>
    <h3>Como isso se traduziu no dia a dia</h3>
  </div>
```

**PROPOSTO**:
```
  <div class="sec-head" style="margin-top:44px">
    <h3>Como isso se traduziu no dia a dia</h3>
  </div>
```

Justificativa: "Três histórias" é contagem do que a numeração 01–03 já mostra.

### 21e — Seção SIGE, dentro do detalhe, "Antes e depois"

**ATUAL** (linhas 666–669):
```
  <div class="sec-head" style="margin-top:44px">
    <span class="eyebrow">Antes e depois</span>
    <h3>O que mudou na operação</h3>
  </div>
```

**PROPOSTO**:
```
  <div class="sec-head" style="margin-top:44px">
    <h3>O que mudou na operação</h3>
  </div>
```

Justificativa: a tabela logo abaixo tem as colunas "Antes" e "Depois, com o sistema", e o `summary` já anunciou "o antes e depois em 8 temas".

### 21f — Seção SIGE, dentro do detalhe, "Rigor"

**ATUAL** (linhas 681–684):
```
  <div class="sec-head" style="margin-top:44px">
    <span class="eyebrow">Rigor</span>
    <h3>O que sustenta os números</h3>
  </div>
```

**PROPOSTO**:
```
  <div class="sec-head" style="margin-top:44px">
    <h3>O que sustenta os números</h3>
  </div>
```

Justificativa: rótulo de uma palavra que só qualifica o que o título já diz.

### 21g — Seção Casas modulares, cabeçalho das três decisões

**ATUAL** (linhas 726–729):
```
  <div class="sec-head" style="margin-top:44px">
    <span class="eyebrow">Três decisões que a conta revelou</span>
    <h3>Onde o número mudou o projeto</h3>
  </div>
```

**PROPOSTO**:
```
  <div class="sec-head" style="margin-top:44px">
    <h3>Onde o número mudou o projeto</h3>
  </div>
```

Justificativa: eyebrow e título dizem a mesma coisa com palavras trocadas; a contagem está na numeração.

### 21h — Seção Contato, caixa de contato

**ATUAL** (linhas 930–932):
```
    <div>
      <span class="eyebrow">Contato</span>
      <h3>Me mande uma obra.</h3>
```

**PROPOSTO**:
```
    <div>
      <h3>Me mande uma obra.</h3>
```

Justificativa: o carimbo da folha 08/08 já diz "Contato" logo acima da caixa. (Não conflita com o achado 1, que acrescenta a linha de termos abaixo do parágrafo, não aqui.)

Pendência (21, geral): nenhuma de fato; só conferir com o integrador que os achados 8 e 18 não reintroduzem eyebrow nesses mesmos cabeçalhos.

---

## Achado 22 — Foco de teclado visível em `details > summary` e nos botões

### Diagnóstico

Existe uma regra global `:focus-visible{outline:2px solid var(--accent);outline-offset:3px}` (linha 74) que já atinge `summary`, `.btn`, links e `.stats.s3 a`. Dois problemas ficam:

1. Nos elementos preenchidos de laranja (`.btn`, `.rail .cv`, `.topbar a`) o anel de foco é laranja também: fica um anel laranja a 3 px de um bloco laranja — visível por norma (há a fresta do fundo), fraco na prática. O anel deve ser de tinta (`--ink`), que rende 13,9:1 sobre o fundo claro e o equivalente no escuro.
2. Nos `summary` o anel sai 3 px para fora do cartão; nos cartões das histórias isso funciona, mas no celular encosta na calha e no `details.mais` (sem caixa) o anel sobe por cima da linha do `border-top`. Anel para dentro (`outline-offset:-3px`) resolve nos dois casos e o `details.mais` ganha a mesma cor de foco que já tem no `:hover`.

Não há problema de suporte: `summary` recebe foco por teclado nativamente e o sinal "+"/"−" muda com `[open]`. O `::-webkit-details-marker{display:none}` e o `list-style:none` retiram só o triângulo, não o foco.

### 22a — Anel de foco: regra global + botões laranja + summary

**ATUAL** (linha 74):
```
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
```

**PROPOSTO** (substitui a linha por três):
```
:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.btn:focus-visible,.rail .cv:focus-visible,.topbar a:focus-visible{outline-color:var(--ink)}
details summary:focus-visible{outline-offset:-3px}
```

Justificativa: anel de tinta sobre botão laranja é inconfundível nos dois temas; anel para dentro do `summary` não invade calha nem borda vizinha. Regra de 2 linhas, no mesmo bloco de base do CSS (logo após `a:hover`).

### 22b — `details.mais`: foco com a mesma cor do hover

**ATUAL** (linha 321):
```
details.mais>summary:hover{color:var(--accent)}
```

**PROPOSTO**:
```
details.mais>summary:hover,details.mais>summary:focus-visible{color:var(--accent)}
```

Justificativa: quem navega por Tab recebe o mesmo sinal de "isto abre" que quem passa o mouse.

### 22c — Sinal "+" dos cartões de história é decorativo

Mesmo elemento, custo zero: o "+" dentro do `summary` é lido pelo leitor de tela como "mais" depois do título.

**ATUAL** (9 ocorrências, todas iguais — substituir todas):
```
<span class="x">+</span></summary>
```

**PROPOSTO**:
```
<span class="x" aria-hidden="true">+</span></summary>
```

Justificativa: o estado aberto/fechado já é anunciado pelo próprio `summary`; o sinal só serve ao olho.

Pendência (22): nenhuma. Sugestão de conferência do integrador: abrir a página, apertar Tab do início ao fim e ver o anel em: botão "Me mande uma obra", botão fantasma do PDF, os três `.stats.s3`, cada `summary` das histórias e cada `details.mais`.

---

## Resumo das pendências que só o Cássio resolve

1. **(20a)** Aprovar o laranja um passo mais escuro no tema claro: #B5440E no lugar de #D4551B (cor de identidade; muda botões, eyebrows, cotas e a barra do carimbo em todo o site claro).
2. **(20a, fora do `index.html`)** Se as folhas de caso em PDF e o currículo usam o mesmo #D4551B, decidir se acompanham a mudança.

Itens sem pendência: 20b, 20c, 21a–h, 22a–c.
