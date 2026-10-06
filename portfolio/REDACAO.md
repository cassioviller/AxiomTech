# Redação do site: como escrever sem tom de IA

Regras aplicadas em 06/10/2026 ao `site/` (index, portfolio, história), ao currículo e às folhas de caso, depois que um revisor apontou que o texto "tem coisas típicas de IA" e que isso tira a credibilidade. Valem para qualquer texto novo. Completam as regras de texto do spec do site v2 (`docs/superpowers/specs/2026-09-25-site-v2-design.md`, §5).

## De onde vêm

- Wikipedia, "Signs of AI writing" (WikiProject AI Cleanup): o catálogo de padrões observados em milhares de textos gerados por IA. https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
- Skill "humanizer" (jooray/humanizer), que transforma esse catálogo em instruções de reescrita e acrescenta a regra de não inventar fatos e a passada de auditoria. https://github.com/jooray/humanizer
- Textos em português sobre o que denuncia a IA para um recrutador: travessão em excesso, "não é X, é Y", frases todas do mesmo tamanho, conectivos de redação escolar. https://canaltech.com.br/inteligencia-artificial/dicas-descobrir-se-texto-foi-escrito-por-ia/ e https://diariodopara.com.br/concursos-e-empregos/como-recrutadores-identificam-textos-de-curriculos-gerados-por-inteligencia-artificial/

## Regras

1. **Sem travessão (—) no texto.** Usar vírgula, ponto, dois-pontos, parênteses ou "porque". O traço curto (–) fica só em intervalos ("mar/2026 – set/2026").
2. **Dizer o que é, sem negar o que não é.** "Comecei pela contabilidade, não pela obra" vira "Comecei a trabalhar na contabilidade da família". A negação fica quando ela é o próprio fato (uma ressalva: "os valores são propostas, não contratos assinados").
3. **Sem frase de efeito.** Nada de aforismo nem lema ("Dado ausente é ausente", "Sistema não muda hábito sozinho", "Diploma em curso. Obra já feita."). Escrever a afirmação concreta que a frase escondia.
4. **Sem frase picada para dar drama.** "Dali em diante, nada." "Cabem três." "Nunca zero." viram orações completas, ligadas à frase vizinha.
5. **Sem dois-pontos de suspense** ("E o portal mostrou o que as mensagens escondiam:"). Dois-pontos só para abrir uma lista ou uma explicação direta.
6. **Sem pergunta retórica** ("O cliente viu?", "Quer ver com uma obra sua?").
7. **Sem dar vontade ao sistema.** "O sistema não esconde a mudança", "cotação que não engana", "a carga se recusa" viram o que acontece de fato ("a mudança fica visível", "a carga não desfaz o avanço").
8. **Listas com o número de itens que os fatos têm.** Não forçar três.
9. **Primeira pessoa e verbo no passado para o que eu fiz** ("fiz", "medi", "orcei", "criei"). Evitar frase sem verbo em descrição de trabalho ("Conversão de…", "Proposta de…").
10. **Palavra de obra, não de software.** "Simulação" em vez de "ensaio", "carga de dados" na primeira vez que "carga" aparece, "entregas" em vez de "entregáveis", "base" em vez de "espinha dorsal".
11. **Autoria.** O sistema é "criei"; a IA aparece como ferramenta ("usei assistentes de IA para escrever o código; as regras e a revisão são minhas").
12. **Não inventar nada.** A reescrita não acrescenta fato, número, nome nem data. O que deixa o texto específico tem de vir do material do projeto (`BRIEF.md`, registros das obras).

## Como revisar um texto novo

1. Reescrever aplicando as regras acima.
2. Reler perguntando "o que aqui ainda parece escrito por IA?" e corrigir o que aparecer.
3. Rodar `python3 portfolio/tests/check_v2.py && python3 portfolio/tests/check_historia.py && python3 portfolio/tests/check_site.py` (os testes conferem números, ressalvas e as frases da home e da história) e `portfolio/build.sh` (os PDFs têm de continuar com 1 página).

## Prompt pronto

> Reescreva o texto abaixo em português do Brasil, na primeira pessoa, como um estudante de engenharia civil explicaria o próprio trabalho a um colega de obra. Não use travessão. Não use a construção "não X, mas Y" nem "X, não Y" para dar ênfase. Não use frase de efeito, lema, pergunta retórica nem frase de duas ou três palavras para dar impacto. Não atribua intenção a sistemas ou ferramentas. Use frases completas, de tamanhos variados, com verbo. Mantenha todos os números, datas, nomes e ressalvas exatamente como estão e não acrescente nenhum fato. Depois de reescrever, releia, aponte o que ainda parece texto de IA e corrija.
