# Insumo da revisão multiagente — 22/09/2026

## Arquivos
- Página: `portfolio/site/index.html` (só o integrador edita). Servida em http://localhost:5000/ .
- Currículo: `portfolio/curriculo/curriculo.html` (só o agente `cv` edita). `portfolio/build.sh` regenera os PDFs.
- Folhas de caso: `portfolio/casos/caso-*.html`.
- Fontes de verdade dos fatos: `PLANO.md`, `portfolio/ref/site-sem-base64.html` (site original aprovado), `portfolio/curriculo/curriculo.html`.
- Regras: nenhum número, cliente, depoimento ou resultado novo. Nunca publicar: salários, valores de contrato, CPF, endereço, nascimento, motivo de desligamento, nomes de pessoas de clientes, CNPJs, nomes de clientes, margens/percentuais de terceiros.

## Decisões padrão para o portão (o Cassio pediu para seguir sem perguntar)
- **A — Titularidade do SIGE: não confirmada.** Não afirmar "licenciado"/"sob licença"/"contrato de licença". Usar "concebi e construí" e "em uso numa empresa de Light Steel Frame". Registrar em PENDENCIAS.
- **B — Autorização da VEKS: não obtida.** Manter VEKS como empregador (fato de currículo). Remover o projeto do bunker (cliente de defesa, identificável). Manter as imagens geradas pelo sistema com legendas genéricas. Manter valores de proposta (já estavam no site aprovado) e registrar em PENDENCIAS que dependem de autorização.
- **C — Termos da oferta:** "Sem custo. Devolvo em até 3 dias úteis. O pacote não sai do meu computador." Registrar em PENDENCIAS para o Cassio confirmar.
- **D — Cargo-alvo:** "Analista de orçamento, planejamento e custos · CLT ou PJ · São José dos Campos, presencial ou remoto".
- **E — Depoimento:** nenhum. Não criar bloco de depoimento.
- **F — Nome:** "Cássio Viller" (com acento) em tudo, inclusive `<h1>` e trilho. LinkedIn: sem URL; não inserir placeholder visível na página.
- **G — V Alves:** sem fatos novos; manter como está.
- **H — Formatura / MS Project:** sem dado; manter como está.

## Achados por leitor (a corrigir)

### Dono de construtora
1. Oferta "me mande uma obra" sem termos → linha com C, abaixo dos botões da primeira tela e no bloco Contato.
2. Falta "o que faço na sua construtora" → bloco de 4 linhas (levantamento e orçamento de propostas; compras com cotação e quadro de concorrência; cronograma, diário e medição; fluxo de caixa e custo previsto × realizado). Colocar na seção Currículo, antes de "Experiência".
3. Dúvida "vai embora para a Axiom" → no currículo, item Axiom: "projetos próprios, sem dedicação de expediente".

### Engenheiro
4. "0,25% de desvio contra a Caixa/SINAPI" é consistência (o sistema reproduz as composições), não acurácia. Reescrever em todos os lugares (stats, tres, currículo, folhas se houver): "reproduz as composições SINAPI com desvio máximo de 0,25%". Manter o bloco "Sem maquiagem".
5. Qualificar "cálculo estrutural", "estudo estrutural", "pré-dimensionamento": sempre "pré-dimensionamento, sujeito à revisão do engenheiro responsável" (galpão 15×20, B-36).
6. Na coluna Resultado dos 36 min, incluir o escopo: "proposta de mão de obra em LSF; os cortes ausentes entraram como pendência declarada".
7. Print do "registro de engenharia": não há imagem disponível sem nome de cliente → não adicionar; registrar em PENDENCIAS.

### Leitor-máquina / RH 7 s
8. Cargo-alvo (D) na primeira tela, logo abaixo do carimbo/eyebrow.
9. Nome padronizado (F) — `<h1>`, `.who` do trilho, topbar, footer, JSON-LD, `<title>`, og:title.
10. JSON-LD: atualizar jobTitle com D; conferir que os dados batem com o currículo.
11. `alt` faltantes ou vazios: revisar.

### Storyteller
12. Parágrafo de 3 frases na primeira tela, substituindo o `.sub` atual: "Comecei no centavo, não na parede: folha, notas e balancete no escritório da família, desde os 17. Na obra, vi a mesma informação digitada cinco vezes. Construí o jeito de ela entrar uma vez — e de cada número ter origem."
13. Fechamento na seção Contato: "Faltam 3 semestres para o diploma. Não falta obra feita."
14. Carimbo da folha 01: acrescentar "caso principal".

### Futuro colega
15. Bloco "Como trabalho" (4 linhas, na seção Currículo, depois de "o que faço"): ensaio antes de gravar; norma escrita para quem preenche; mudança que mexe com dinheiro entra por fases, com volta atrás; o que muda gasto, venda ou promessa volta para quem assina.
16. Frase sobre IA: onde diz "dirigi o desenvolvimento, feito com assistentes de inteligência artificial sob minha revisão", completar: "— as regras de engenharia, os testes e a revisão são meus".

### Jurídico / sigilo
17. Remover o projeto "Bunker de blindagem para fonte radioativa" (seção Obra) e qualquer menção a "defesa".
18. Trocar "licenciado"/"sob licença"/"contrato de licença" conforme A (site, currículo, folhas, JSON-LD).
19. Varrer nomes de clientes, margens, percentuais, dados pessoais. Conferir legendas das imagens.

### Acessibilidade / design
20. Contraste: `--muted` já escurecido para #5B6672; conferir demais pares (eyebrow laranja #D4551B sobre #ECEBE6; texto sobre azul-aço).
21. Excesso de rótulos mono por dobra: onde há carimbo, remover o `.eyebrow` redundante do `.sec-head` (manter só os que acrescentam informação).
22. Foco de teclado visível em `details > summary` e nos botões.

### Currículo (`curriculo.html`)
23. Aplicar 4, 5, 9, 18; cargo-alvo D na linha `.role`; Axiom conforme 3; remover "[confirmar URL]" do LinkedIn e do Portfólio (deixar só "github.com/cassioviller" e "Portfólio: cassioviller.tech" se for o domínio; se não houver certeza, omitir a linha do portfólio). Continuar em 1 página; `pdftotext` na ordem.
