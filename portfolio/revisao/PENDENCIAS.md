# Pendências da revisão — 22/09/2026

Leitura de 2 minutos. Tudo abaixo foi aplicado no site (`portfolio/site/index.html`), no currículo (`portfolio/curriculo/curriculo.html`) e nas folhas de caso seguindo as decisões padrão da REVISAO.md. O que precisa da sua palavra está marcado.

## 1. Decisões padrão que você precisa confirmar

| | O que foi feito | O que muda se a resposta for outra |
|---|---|---|
| **A — Titularidade do SIGE** | Saiu "licenciado / sob licença / contrato de licença" do site, currículo, folhas e JSON-LD. Entrou "concebi e construí" e "em uso numa empresa de Light Steel Frame". | Se houver contrato de licença assinado, voltamos a afirmar "sob licença". Atenção: o site diz "em uso numa empresa de LSF" e, na seção Currículo, "implantação do SIGE (em uso na empresa)" no item VEKS — lidos juntos, identificam a empresa usuária. |
| **B — Autorização da VEKS** | VEKS ficou só como empregador. Bunker (cliente de defesa) removido. Imagens do sistema mantidas com legendas genéricas. Valores de proposta (R$ 24,5 mi, R$ 1,18 mi → R$ 452.865, R$ 964.917 etc.) mantidos, com aviso de que são propostas. | Sem autorização da VEKS, os valores de proposta e as capturas t3/t4 podem ter de sair. Em t3/t4 ficam legíveis em texto pequeno parâmetros internos da planilha ("MO do aço 5 R$/kg", "R$ 15 mil / 36 mil / 23 mil / +108 mil de MO") e a logo VEKS. Não há print do "registro de engenharia" sem nome de cliente, por isso não entrou (achado 7). |
| **C — Termos da oferta** | "Sem custo. Devolvo em até 3 dias úteis. O pacote não sai do meu computador." — abaixo dos botões da primeira tela e no bloco Contato. | Confirme os três: é sem custo mesmo; 3 dias úteis vale para qualquer porte de pacote; nenhum serviço externo no método contradiz "não sai do meu computador". Se algum não vale, a frase muda nos dois lugares. |
| **D — Cargo-alvo** | "Analista de orçamento, planejamento e custos · CLT ou PJ · São José dos Campos, presencial ou remoto" na primeira tela, no JSON-LD (jobTitle) e na linha `.role` do currículo. | Se o cargo for outro, troca nos três lugares. Confirme também as quatro frentes de "O que faço na sua construtora" (levantamento/orçamento de propostas; compras com cotação e quadro de concorrência; cronograma, diário e medição; fluxo de caixa e previsto × realizado) e a ordem de prioridade. |
| **E — Depoimento** | Nenhum bloco criado. | Só entra com depoimento real e autorizado. |
| **F — Nome** | "Cássio Viller" (com acento) em todo texto visível, `<h1>`, trilho, `<title>`, og:title, rodapé. Sem acento só no e-mail, no handle do GitHub e no nome do PDF. LinkedIn omitido (sem URL). | Passe a URL do LinkedIn para incluir no currículo e no site. **Falha aberta:** o JSON-LD ainda traz "Cássio Viller Silva de Azevedo" (nome completo sem fonte) — ver seção 3. |
| **G — V Alves** | Mantido como estava, sem fatos novos. | — |
| **H — Formatura / MS Project** | Sem dado; mantido. | Se tiver previsão de formatura ou uso de MS Project, informar. |

Também aplicado por padrão e que depende de você:
- **Axiom** (achado 3): site e currículo dizem "projetos próprios · sem dedicação de expediente", sem datas. Se houver CNPJ ativo ou cliente em atendimento comercial, a frase muda. Se quiser datas no currículo, informar.
- **"Como trabalho"** (achado 15): as quatro regras estão na primeira pessoa, valendo para você em qualquer empresa (não só como regra do SIGE). Na 4ª linha, "Eu recomendo" substitui "O método recomenda" da regra 06 — confirmar ou trocar.
- **Frase sobre IA** (achado 16): no site, "— as regras de engenharia, os testes e a revisão são meus". Confirmar que "os testes são meus" é verdade como um colega entende (você define e confere as verificações automáticas, mesmo com código escrito com assistentes). No currículo (linha 96) a frase segue como antes; decidir se acompanha (custa ~meia linha, e a página está no limite).
- **Laranja do tema claro** (achado 20a): proposta trocar `--accent` #D4551B por #B5440E — cor de identidade. Hoje falha AA (3,44:1 sobre o fundo; botão branco sobre laranja 4,11:1); com #B5440E sobe para 4,63:1 e 5,53:1. Tema escuro não muda. Decidir também se as folhas em PDF e o currículo acompanham.
- **Portfólio: cassioviller.tech** omitido do currículo até confirmar que o site vai na raiz desse domínio (PLANO.md, dúvida 7).

## 2. Pendências técnicas (para o integrador, não precisam de você)

- Tema escuro: `.case-banner` e `.savings` ficam azul-claro (#9DBBD8) com texto branco a 1,99:1. Criar `--steel-panel:#2E4763` no `:root` e trocar o fundo dos dois blocos. Correção obrigatória.
- Conferir que os achados 8 e 18 não reintroduziram eyebrow nos 8 cabeçalhos onde foi removido (Sistema ×2, SIGE ×4, Modular ×1, Contato ×1).
- Testar com Tab do início ao fim (anel de foco nos botões laranja, anel para dentro nos `summary`, aria-hidden no sinal "+").
- Folhas de caso: a folha 01 ainda não traz "caso principal" no carimbo (achado 14) nem a frase de escopo "proposta de mão de obra em LSF; os cortes ausentes entraram como pendência declarada" na coluna Resultado (achado 6). Precisa de nova rodada nas folhas.
- Rótulo "Processos, Orçamentos e Gestão de Obras (PJ)" na VEKS (currículo e JSON-LD) é construído; a fonte diz "prestador de serviços (PJ)". Aceitável, mas não literal.
- Para caber em 1 página: `.role` de 10,4pt para 9,8pt, espaço entre blocos apertado ~1,5px, "de São José dos Campos" saiu do resumo (cidade já está no cabeçalho). Nada de conteúdo foi removido.
- `build.sh` regenera também os PDFs das folhas — comportamento normal.
- Baixo risco: `img/upa-plan.webp` e `upa-plan-grey.webp` trazem "upa" no nome (sugere o tipo da unidade de saúde). Renomear se quiser fechar. `upa-plan.webp` está órfão.
- No `pdftotext`, os títulos "PROJETO PRÓPRIO" e "COMPETÊNCIAS E FERRAMENTAS" saem com letras espaçadas por causa do letter-spacing; pode atrapalhar leitura por ATS.

## 3. Falhas que restaram após 2 rodadas de correção

Todas de fatos sem fonte em PLANO.md ou no site aprovado. Corrigir e rodar o `build.sh` (o .txt e o PDF do currículo repetem as mesmas falhas).

| Onde | Está | Deve ficar |
|---|---|---|
| index.html, linha 363 (eyebrow) | "Engenharia Civil · 7º semestre, faltam 3 · 26 anos" | Remover "· 26 anos" (sem fonte; idade permite deduzir nascimento). |
| index.html, linha 369 (.sub) | "...no escritório da família, desde os 17." | "desde 2017" (fonte: "2017 – hoje · Analista contábil — escritório da família"). |
| index.html, linha 708 (HUD das modulares) | "3,8 t" por caixa | Sem fonte nas fontes de fatos (só em ref/cena5.html e maquetes.js). Confirmar origem ou trocar por número aprovado (ex.: "3 viagens"). |
| index.html, linha 601 (folha 03 SIGE) | "3.343 verificações automáticas aprovadas" | "mais de 3.300 verificações automáticas". |
| curriculo.html, linha 102 | "3.343 verificações automáticas aprovadas" | "mais de 3.300". |
| index.html, JSON-LD (~linha 19) | "Cássio Viller Silva de Azevedo" + alternateName | "Cássio Viller"; remover alternateName. |
| curriculo.html, linha 106 | "após 6 semestres na UNIFEI, Itajubá/MG (2020–2024)" | Remover "(2020–2024)". |
| curriculo.html, linha 70 | "Estruturas metálicas · São José dos Campos/SP" | "Empresa de estruturas · São José dos Campos/SP". |
| curriculo.html, linha 56 (VEKS) | "redigi contratos de empreitada e de mão de obra" | "revisei contrato de empreitada e redigi contrato de mão de obra". |

## 4. Observações dos verificadores (não bloqueiam)

- Todos os demais números do site e do currículo batem com PLANO.md e o site aprovado, item a item (36 min, 13 obras, R$ 24,5 mi, 0,25%, tabela do drywall, SIGE, modulares, obra, datas e cargos).
- Remoções e reescritas do portão coerentes: bunker/defesa fora; licença trocada; preço de venda do drywall retirado; margens removidas sem fato novo; 0,25% reescrito como consistência em todos os pontos; pré-dimensionamento qualificado no galpão e no B-36; etiqueta diz "Pré-dimensionamento estrutural", não "cálculo".
- Sigilo: nenhuma ocorrência de nomes de clientes, defesa, bunker, licença, CPF, CNPJ, salário, nascimento ou endereço. Clientes aparecem só por tipo ("rede de restaurantes de rodovia", "unidade de saúde no litoral paulista" etc.). "AZ Contabilidade" só no JSON-LD e no currículo; no site é "escritório da família". Percentuais são todos técnicos; valores em R$ são de proposta, com aviso.
- Layout: sem scroll horizontal em 390, 1280 e 1440 px; 23 `<img>` com alt, todas carregando; HTML balanceado; JSON-LD válido. PDFs com 1 página A4 cada, nada cortado; `pdftotext` do currículo na ordem certa.
- Leituras por persona: dono, engenheiro e RH encontram o que precisam na primeira tela. Observações menores: a primeira tela diz preço e prazo da oferta, mas o que volta (levantamento, orçamento com faixa, proposta no modelo dele) só aparece na Folha 01 e em Contato; "≈ 27×" compara 36 min medidos com ~2 dias úteis estimados (o asterisco declara); "fecha ao centavo" é fechamento aritmético com a planilha, não acurácia; no celular o botão do PDF fica perto da borda inferior em telas de ~700px.
- Nas folhas de caso, as quatro capturas da folha 01 têm alt="" (decorativas, com legenda ao lado).

## 5. Não aplicado e por quê

- **7 — print do registro de engenharia:** não há imagem sem nome de cliente. Fica para quando houver.
- **23 — currículo:** editado pelo agente cv, não pelo integrador; conferido que já traz cargo-alvo D, Axiom sem expediente, SINAPI como consistência e pré-dimensionamento qualificado. O achado 16 (frase sobre IA) não foi aplicado no currículo — ver seção 1.
- **Folhas de caso:** sem "licen", "Cassio" sem acento ou "0,25%" — nenhuma edição necessária nessa rodada (mas ver achados 6 e 14 na seção 2).
- **Propostas juridico.md, ia.md, eng.md e hist.md** não existiam em revisao/propostas/; os achados 4–14 e 17–19 foram aplicados direto do texto da REVISAO.md e das decisões A–H.

## Fechamento manual (Claude, 22/09 ~01:50) — decisão sobre as 9 falhas restantes do verificador "fatos"
O verificador não tinha acesso ao `BRIEF.md` (fora do git) nem ao currículo original; por isso apontou como "sem fonte" vários dados que estão lá.
- Corrigido: "· 26 anos" removido da primeira tela; "desde os 17" → "desde 2017"; currículo: "revisei contrato de empreitada, redigi contrato de mão de obra"; níveis das ferramentas restaurados a partir do currículo original (v4).
- Mantido (fonte = BRIEF.md / currículo original / cena5 aprovada): "3.343 verificações"; "3,8 t" no HUD da maquete; nome civil completo no JSON-LD; "(2020–2024)" UNIFEI; "Estruturas metálicas".
- Já resolvido na Correção 2: carimbo "Jul–Set/2026" → "VEKS · 2026".
