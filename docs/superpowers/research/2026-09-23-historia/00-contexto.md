# Contexto comum das personas — página `historia.html`

## Quem é o dono do site
Cássio Viller, estudante de Engenharia Civil (7º semestre, faltam 3), em São José dos Campos/SP. Cargo-alvo: **analista de orçamento, planejamento e custos** (CLT ou PJ, presencial ou remoto), em construtoras — especialmente de Light Steel Frame (LSF) e drywall. Vem da contabilidade (escritório da família, desde 2017), passou por obra (VEKS Engenharia, V Alves, Estruturas do Vale) e construiu sistemas para construtoras, com assistentes de IA sob a direção dele.

Tese do site: **"Um número sem origem custa caro na obra. Eu construí o jeito de ele não sumir."**

## O site atual
- `portfolio/site/index.html`: página única estática, sem framework, CSS inline. Estética de **prancha de obra**: carimbo "Folha 0X/08", linha de cota em ferrugem, fundo papel `#ECEBE6`, tinta `#171F29`, acento ferrugem `#B5440E`, azul-aço `#2E4763`. Fontes Barlow Condensed (display), IBM Plex Sans (texto) e IBM Plex Mono (técnico). Tema escuro por `prefers-color-scheme`.
- `portfolio/DESIGN.md`: a linguagem visual completa.
- `portfolio/tests/check_site.py`: checagem em Python puro (números iguais a um commit de referência, ressalvas presentes, tags balanceadas).
- Publicação: Replit static deploy da pasta `portfolio/site/`. Sem build, sem npm. Bibliotecas só por arquivo local em `site/vendor/` (já existe three.js).

## Provas que a história pode usar (números conferidos — sempre com a ressalva)
- **36 minutos** do pacote do projeto (zip) à proposta de mão de obra assinável, medidos 11:35 → 12:11, numa ampliação de unidade de saúde (26 ambientes, 328 m²). À mão: ~2 dias úteis (estimativa).
- **Sistema de orçamento**: 13 obras no sistema, 11 com proposta, de R$ 29 mil a R$ 24,5 milhões; nos 19 serviços SINAPI conferidos, desvio máximo de 0,25%; menções a informação interna numa proposta de 71 → 0. A parte de gestão de obra desse sistema ainda não rodou numa obra real.
- **SIGE** (outro sistema, de gestão de obra, em uso numa empresa de LSF): portal do cliente por link; 23 diários que estavam só no WhatsApp recuperados; a obra passa de 27,6% para 44,7% concluído contra 60,8% planejado — lido numa cópia do sistema com os dados reais.
- **Casas modulares**: o celeiro B-36 não cabe inteiro no caminhão — vai em duas caixas, três viagens; 37 decisões registradas.
- Frase de fechamento já usada: "Faltam 3 semestres para o diploma. Não falta obra feita." CTA: "Me mande uma obra" (WhatsApp).

## Ativos visuais já existentes (`portfolio/site/img/*.webp`)
t1–t4 (telas da linha do tempo dos 36 min, com relógio), upa-plan (planta com paredes em vermelho), s1 (restaurante de rodovia desenhado pelo sistema), s2 (ponto de venda de planta curva), o-*.webp (8 telas do orçamento + mapa de cotação + financeiro), p-*.webp (portal do cliente, diário, fotos reais de obra de galpões em LSF), m1–m7 e configurador-b36 (renders das casas modulares), c-* (telas de compras).

**Duas maquetes three.js** em `portfolio/site/maquetes.js`: cena `36min` (paredes sobem da planta enquanto um relógio anda de 11:35 a 12:11) e cena `casa-viaja` (duas caixas do B-36 viajam de caminhão e são içadas). Cada `<figure class="maquete" data-cena="…">` expõe `fig.__maquete.seek(t)` e `api.dur` — dá para amarrar o tempo da animação ao progresso do scroll. Já respeitam `prefers-reduced-motion` (ficam na imagem estática) e têm guarda de desempenho (<24 fps volta para a imagem).

## A página proposta
`portfolio/site/historia.html` — **scrollytelling**: uma frase direta e grande por tela, no centro; o fundo troca de cena conforme a frase muda; de 8 a 10 cenas; rolagem nativa (sem scrolljacking); linha pequena de ressalva sob toda frase com número; no fim, leva ao site completo (`index.html`) e ao WhatsApp. Técnica provável: fundo `position: sticky` + passos detectados por `IntersectionObserver` (padrão Scrollama, sem biblioteca), com CSS `animation-timeline: view()` opcional atrás de `@supports`.

## Regras que não mudam
Nenhum número novo que o site não sustente; nenhuma ressalva apagada; não misturar telas do SIGE com as do sistema de orçamento; nada de nome de cliente, e-mail ou margem real em imagem.
