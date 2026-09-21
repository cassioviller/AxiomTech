# PLANO — Currículo e portfólio de Cassio Viller

Escrito em 21/09/2026. Substitui a seção 5 do `BRIEF.md` (filme de 10 cenas como abertura).
O resto do brief continua valendo: fatos, números, lista do que nunca publicar, estilo aprovado da `cena5.html`.

## 1. Objetivo e critério de sucesso

**Objetivo:** conseguir a próxima posição (orçamento, planejamento, custos, gestão de obra) em construtora,
incorporadora ou empresa de engenharia, de preferência no Vale do Paraíba ou remoto.

**Sucesso = entrevistas marcadas**, não visitas ao site. Cada entrega abaixo existe para uma destas três situações:

| Situação | O que a pessoa abre | Tempo de atenção |
|---|---|---|
| RH / portal de vagas (Gupy, Catho, Indeed) | Currículo PDF + LinkedIn | 7 segundos |
| Dono de construtora recebe mensagem no WhatsApp | Folha de caso de 1 página + link do site | 30–60 segundos |
| Quem se interessou e quer conferir | Site completo + PDFs longos | 5–10 minutos |

## 2. Decisões já tomadas (e por quê)

1. **Filme de 3 minutos como abertura: cancelado.** Intro que toca sozinha é antipadrão (NN/g), o leitor decide em ~10 s,
   custa semanas e arrisca travar em Android médio. O estilo 3D aprovado é reaproveitado em maquetes embutidas (fase 4)
   e num vídeo curto opcional (fase 5).
2. **Estilo: "prancha de obra".** Mantém a identidade atual do site (concreto, azul-aço, laranja único, Barlow Condensed +
   IBM Plex) e acrescenta carimbo de folha por seção e a linha laranja de cota como único elemento animado.
3. **Primeiro os documentos, depois o site, por último o 3D.** O currículo atual é o elo mais fraco e é o mais usado.
4. **Sigilo acima de vitrine.** Clientes sempre genéricos; nada de margens/percentuais de ex-contratante; nada de dados
   pessoais sensíveis. Vale para site, PDFs e LinkedIn.

## 3. Fases

### Fase 0 — Higiene do repositório (15 min)
- [x] `.gitignore`: `handoff-portfolio-cassio.zip`, `docs-pessoais/`, `BRIEF.md` (contém telefone e histórico pessoal).
- [x] Criar pasta `portfolio/` neste workspace para o trabalho (não mexe no site da Axiom em `client/`).
- [x] Extrair para `portfolio/` só: `cassio-viller.html`, `cena5.html`, `img/`, `configurador-b36.webp`.

### Fase 1 — Currículo de 1 página (prioridade máxima)
Entrega: `portfolio/curriculo/` com fonte HTML + PDF A4, e versão .docx/texto puro para portais.
- [x] Cabeçalho: nome, cidade/UF, telefone, e-mail, LinkedIn, link do site. **Sem** nascimento, endereço, estado civil, foto.
- [x] Linha-objetivo com o vocabulário das vagas: orçamento de obras · planejamento e controle de custos · gestão de obra.
- [x] Resumo de 3 linhas com 3 números (36 min · 13 obras até R$ 24,5 mi · SIGE ~50 módulos licenciado).
- [x] Experiência em ordem cronológica inversa, formato `Cargo | Empresa | MM/AAAA – MM/AAAA`, 3–5 linhas com verbo + número:
      VEKS Engenharia → V Alves Construção → Estruturas do Vale → AZ Contabilidade → InLoco Jr. / DCE UNIFEI.
- [x] Palavras-chave da triagem automática: levantamento de quantitativos, composição de custos, SINAPI, cronograma
      físico-financeiro, curva S, medição, diário de obra (RDO), compras, fluxo de caixa, Light Steel Frame, MS Project*.
      (*só se for verdade — confirmar com o Cassio.)
- [x] Formação: Eng. Civil 7º sem. (Cruzeiro do Sul, após 6 sem. na UNIFEI), previsão de conclusão; SI/PUC em uma linha.
- [x] Ferramentas com nível. Axiom como "Projetos próprios", sem "CEO".
- [x] Conferir: texto extraível pelo `pdftotext` na ordem certa (teste de ATS); zero erro de digitação.

### Fase 2 — Três folhas de caso (1 página A4 cada, PDF)
Entrega: `portfolio/casos/`. Estrutura fixa: manchete com número → problema → o que fiz → resultado → prova (imagem) → contato.
- [x] **36 minutos** — do zip à proposta assinável (prints com relógio `t1..t4`, as 6 regras em uma linha cada).
- [x] **A casa que coube em R$ 500 mil** — R$ 1,18 mi → R$ 452 mil, 54 dias; acréscimos precificados um a um.
- [x] **23 diários recuperados do WhatsApp** — 185 fotos, 72 avanços, 28 atividades que apareciam atrasadas.
- [x] Mensagem-modelo de WhatsApp/e-mail (3 variações: dono de construtora, RH, indicação) com a oferta
      "me mande um pacote, devolvo levantamento + orçamento com faixa + proposta".

### Fase 3 — Site
Entrega: `portfolio/site/` (HTML estático, imagens em `img/`, sem base64), pronto para `cassioviller.tech`.
- [x] Primeira tela "placa de obra": ficha, tese, 3 números, botões **Me mande uma obra** e **Baixar currículo (PDF)**.
- [x] Carimbo de folha por seção; linha de cota laranja marcando o número de cada caso.
- [ ] Cada caso no formato: manchete → 3 linhas (problema / o que fiz / resultado) → prova → detalhe em `<details>`.
      (Não feito: os casos mantêm a estrutura do site original; o formato de 3 linhas existe nas folhas em PDF.)
- [x] Subir o caso da residência (R$ 1,18 mi → R$ 452 mil) para destaque.
- [x] Drywall: mostrar formação do custo e a conferência com a Caixa (R$ 106,05 × R$ 106,00); tirar o preço de venda.
- [x] Prévia de link para WhatsApp (Open Graph: título, descrição, imagem 1200×630).
- [x] Reordenar para o leitor de obra: Orçamento 36 min → Sistema de orçamento → SIGE → Casas modulares → Obra → Currículo.
      (Hoje abre com o SIGE, que é o caso mais "de software".)
- [x] Testes: 390×780, 1280×720, 1440×900; sem scroll horizontal; peso da 1ª tela < 300 KB.
      (O tema continua seguindo o sistema do visitante — claro ou escuro — como no site original.)

### Fase 4 — Maquetes 3D embutidas (só depois das fases 1–3 no ar)
Padrão `cena5.html`, three.js atual, cena como função do tempo, toca só quando visível, imagem estática como fallback
e para `prefers-reduced-motion`.
- [x] Maquete "36 minutos": paredes sobem da planta da UPA enquanto o relógio anda 11:35 → 12:11.
- [x] Maquete "A casa viaja": `cena5` encurtada, dentro da seção de casas modulares.
- [ ] Medir fps em Android médio de verdade (a guarda automática de ~24 fps está implementada; só foi testada em renderização por software).

### Fase 5 — Opcional
- [ ] Vídeo de 45 s (problema → virada → 36 min) exportado das maquetes, para LinkedIn e WhatsApp.
- [ ] Limpeza dos PDFs longos (`Portfolio_SIGE`, `Portfolio_Sistema_Orcamento_VEKS`): preencher campos em branco e
      "Meu papel", generalizar clientes, remover percentuais de margem. Ficam como anexo "para quem pedir mais".

## Estado em 21/09/2026

Fases 0–4 entregues em `portfolio/` (ver `portfolio/README.md`). Fase 5 não feita: o vídeo de 45 s pede captura quadro a quadro
(o `ffmpeg` existe no ambiente; a captura pelo Chromium headless levaria ~1 h) e os PDFs longos vieram sem o arquivo-fonte,
então não dá para editá-los aqui. Nada foi commitado nem publicado.

## 4. Pendências que dependem do Cassio

| # | Pergunta | Bloqueia |
|---|---|---|
| 1 | URL do LinkedIn (e atualizar o perfil com o texto do currículo novo) | Fase 1, 3 |
| 2 | "O que procuro": cargo(s)-alvo, presencial/híbrido/remoto, região, CLT ou PJ | Fase 1 |
| 3 | "Meu papel" no SIGE, em 3–4 frases | Fase 3, 5 |
| 4 | Autorização da VEKS (por escrito, pode ser WhatsApp) para mostrar valores de proposta, imagens e o bunker | Fase 2, 3 |
| 5 | Previsão de formatura (mês/ano) e se tem registro/estágio obrigatório pendente | Fase 1 |
| 6 | Sabe MS Project? Outras ferramentas de planejamento/orçamento além de OrçaFascio? | Fase 1 |
| 7 | Onde hospedar: `cassioviller.tech` na raiz, com a Axiom em subdomínio (como hoje)? | Fase 3 |
| 8 | Lista inicial de 30–50 construtoras/incorporadoras-alvo (posso pesquisar uma base para ele completar) | Prospecção |

## 5. Regras que valem em tudo

- Fatos e números: só os do `BRIEF.md` e do site. Sempre o número medido (36 min, nunca "menos de uma hora").
- Nunca: salários, valores de contrato, CPF, endereço, nascimento, motivo do desligamento, nomes de pessoas, CNPJs,
  nomes de clientes, margens de terceiros.
- Linguagem de obra, não de software. Sem falar de stack.
- Uso de IA: declarar com naturalidade ("dirigi o desenvolvimento, feito com assistentes de IA sob minha revisão").
- Nada é commitado nem publicado sem o Cassio ver antes.

## 6. Ordem de execução sugerida

Fase 0 → Fase 1 (currículo) → Fase 2, folha "36 minutos" → mostrar ao Cassio → resto da Fase 2 → Fase 3 → Fase 4 → Fase 5.
As pendências 1, 2, 5 e 6 podem ser respondidas em paralelo; o currículo sai com marcadores `[confirmar]` onde faltar resposta.
