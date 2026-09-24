#!/usr/bin/env python3
"""Aplica ao film.html do zip (filme-codigo-fonte.zip) as correções de honestidade da rodada 3.
Uso: python3 portfolio/filme/corrigir_filme.py   (idempotente: falha se o texto esperado não estiver lá)
"""
import re
from pathlib import Path

FILME = Path(__file__).resolve().parent / "film.html"
CAPS = """var ORDER=[5,0,1,6,3,7,8,2,4], DUR=[10.5,8,8,8,8,8.5,8.5,8.5,9], ENDD=8;
// [kicker, frase (≤7 palavras), apoio (≤ 200 palavras/min), hud, ressalva] — mesmas regras de honestidade da página
var CAPS=[
 ['Cássio Viller · portfólio','Número sem origem custa caro na obra.','Nove capítulos, de 2017 a 2026. Cada número tem origem: medido, derivado ou a confirmar.',null,''],
 ['2017 → 2024','Comecei pela contabilidade, não pela obra.','Escritório contábil da família desde 2017. Na UNIFEI, fiscal do DCE (2022) e diretor de vendas da InLoco Jr.',function(t){return['8 anos','de rotina contábil'];},''],
 ['fev/2025 → mar/2026','Mas vi o dado digitado cinco vezes.','Meio período, em paralelo: produção na V Alves (CLT) e estágio na Estruturas do Vale, onde nasceu o SIGE.',function(t){return['5×','o mesmo dado'];},''],
 ['mar → set/2026','Na VEKS, toda conta repetida virou ferramenta.','PJ, 6 meses, cumprido até o fim, com a V Alves até julho. Calculadora de parede e classificador de caixa.',function(t){return['6 meses','contrato PJ cumprido'];},''],
 ['mai → set/2026','O SIGE ganhou versão nova.','Cerca de 50 módulos em 6 áreas; entregas de 22/07 a 14/09/2026. Portal e diário em uso nos galpões.',function(t){return['~'+Math.round(50*ramp(t,1,8.2))+' módulos','em 6 áreas'];},''],
 ['jul → set/2026','13 obras no sistema, 11 com proposta.','Lê o desenho, mede e orça. Nos 19 serviços SINAPI conferidos, desvio máximo de 0,25%. Código com assistentes de IA.',function(t){return t<5?['R$ 24,5 mi','maior proposta']:(t<7.6?['0,25%','desvio máx. vs. SINAPI']:[Math.min(13,1+Math.round(12*ramp(t,6.9,9.2)))+' obras','no sistema']);},'A gestão de obra deste sistema ainda não rodou em obra real.'],
 ['ago/2026','O celeiro não cabe no caminhão.','B-36: duas caixas, três viagens, 37 decisões registradas. No estudo, o módulo sobe pelo balancim, cabos na vertical.',function(t){return['37','decisões registradas'];},'Pré-dimensionado, sujeito à revisão do engenheiro responsável.'],
 ['ago → set/2026','23 dias de diário só no WhatsApp.','Depois de 11/08, o diário saiu do sistema; 28 atividades prontas apareciam atrasadas nos dois galpões.',function(t){var n=Math.round(23*ramp(t,3,8.2));return[n+(n==1?' dia':' dias'),'de diário recuperados'];},'Recuperação lida numa cópia; no sistema em uso, a carga ainda não foi aplicada.'],
 ['set/2026','Proposta assinável em 36 minutos.','Medidos: 11:35 → 12:11, ampliação de unidade de saúde, 26 ambientes, 328 m². À mão, cerca de 2 dias úteis (estimativa).',null,'']];
"""
TABELA = ("var rows=[['Área de projeção (UPA)','328','m²','medido'],['Ambientes','26','un','medido'],"
          "['Placa de gesso por m²','2,11','m²','derivado'],['Montante por m²','2,91','m','derivado'],"
          "['Aço da casa 8 × 6 m','541','kg','derivado'],['Pé-direito','—','m','a confirmar']];")
TROCAS = [
    # nome com acento; sem "26 anos" (o portfólio não traz a idade)
    ('<div class="tag">Cassio Viller · <b>portfólio</b></div>', '<div class="tag">Cássio Viller · <b>portfólio</b></div>'),
    ('  <h1>Cassio Viller</h1>\n  <div class="a">26 anos · São José dos Campos/SP</div>', '  <h1>Cássio Viller</h1>\n  <div class="a">São José dos Campos/SP</div>'),
    ('<h1 id="e2">Cassio Viller<i id="endline"></i></h1>', '<h1 id="e2">Cássio Viller<i id="endline"></i></h1>'),
    ('<div class="l1" id="e3">26 anos · São José dos Campos/SP · orçamento, planejamento e custos</div>',
     '<div class="l1" id="e3">São José dos Campos/SP · orçamento, planejamento e custos</div>'),
    # planilha do escritório: nada de valor inventado; a célula em destaque "não bate" e depois "confere"
    ("c.fillText(k==0?'conta '+(r+1):(hi&&t>6.3&&t<8?'1.284,32':(r*317+k*91+120)+',00'),x+6,y+23);",
     "c.fillText(k==0?'conta '+(r+1):(hi?(t>=8?'confere':(t>6.3?'não bate':'· · ·')):'· · ·'),x+6,y+23);"),
    # post-its: o mesmo dado em cinco lugares, a quinta cópia diverge — sem valor em reais
    ("c.fillStyle=i==4?'#C23B22':'#1E1A17';c.font='bold 44px sans-serif';c.fillText(i==4?'R$ 150.500':'R$ 155.000',20,120);",
     "c.fillStyle=i==4?'#C23B22':'#1E1A17';c.font='bold 34px sans-serif';c.fillText(i==4?'OUTRO DADO':'MESMO DADO',20,120);"),
]
# Rodada 4 (o filme vira fundo da história, sem legenda para ressalvar): nada no quadro que o portfolio.html não sustente.
TROCAS_RODADA_4 = [
    # rua: os 5 cartões dizem MESMO DADO; sai o "OUTRO DADO" e o risco (o 5º continua vermelho e tremendo)
    ("c.fillText(i==4?'OUTRO DADO':'MESMO DADO',20,120);if(i==4){c.strokeStyle='#C23B22';c.lineWidth=5;c.beginPath();c.moveTo(16,106);c.lineTo(300,106);c.stroke();}",
     "c.fillText('MESMO DADO',20,120);"),
    # VEKS: o portfólio não fala de barras de 3 m
    ("'PLANO DE CORTE · barras de 3 m'", "'PLANO DE CORTE'"),
    # SIGE: 8 andares = #sige .flow do portfólio, sem numerais; a placa diz EM USO; tudo sobe 1,2 (um andar)
    ("var names=['PROPOSTA','OBRA','CRONOGRAMA','DIÁRIO','COMPRAS','MEDIÇÃO','CAIXA'];",
     "var names=['PROPOSTA','OBRA','CRONOGRAMA','DIÁRIO','MEDIÇÃO','COBRANÇA','CAIXA','PORTAL DO CLIENTE'];"),
    ("c.fillStyle='#fff';c.font='bold 50px sans-serif';c.fillText(nm,24,66);c.fillStyle='#D9541E';c.fillText(String(i+1).padStart(2,'0'),420,66);",
     "c.fillStyle='#fff';c.font='bold 40px sans-serif';c.fillText(nm,24,64);"),
    ("st.tube=box(.3,8.6,.3,ORANGE,-2.3,4.3,2.12,g);st.tube.geometry.translate(0,4.3,0);",
     "st.tube=box(.3,9.8,.3,ORANGE,-2.3,4.9,2.12,g);st.tube.geometry.translate(0,4.9,0);"),
    ("c.fillText('LICENCIADO',70,76);", "c.fillText('EM USO',140,76);"),
    ("st.lic=plane(2.8,.6,lic,0,9.3,0,g);box(.1,.8,.1,0x55606B,-1,8.7,0,g);box(.1,.8,.1,0x55606B,1,8.7,0,g);",
     "st.lic=plane(2.8,.6,lic,0,10.5,0,g);box(.1,.8,.1,0x55606B,-1,9.9,0,g);box(.1,.8,.1,0x55606B,1,9.9,0,g);"),
    ("st.cam=[[0,[7,1.6,10],[0,1.4,0]],[7.5,[7,8.6,10],[0,7.6,0]],[10,[11.5,9,16],[0,4.8,0]]];",
     "st.cam=[[0,[7,1.6,10],[0,1.4,0]],[7.5,[7,9.8,10],[0,8.8,0]],[10,[12.5,10,17.5],[0,5.4,0]]];"),
    ("st.tube.scale.y=Math.max(.01,ramp(t,.5,7.6));st.lic.visible=t>7.8;st.lic.scale.setScalar(Math.max(.001,back((t-7.8)/.5)));",
     "st.tube.scale.y=Math.max(.01,ramp(t,.5,8.0));st.lic.visible=t>8.2;st.lic.scale.setScalar(Math.max(.001,back((t-8.2)/.5)));"),
    # restaurante: o cubo é o desenho que entra, não um tamanho de arquivo
    ("c.font='bold 64px sans-serif';c.fillText('756',60,120);c.font='bold 44px sans-serif';c.fillText('MB',86,180);",
     "c.font='bold 44px sans-serif';c.fillText('DESENHO',26,146);"),
    # 36 min (só no trailer): sem título de prancha nem escala
    ("'PLANTA CONSTRUIR E DEMOLIR · ESC 1:100'", "'PLANTA'"),
    # escritório: calendário com 31 dias, não 35
    ("for(var r=0;r<5;r++)for(var k=0;k<7;k++)c.fillText(String(r*7+k+1),14+k*34,110+r*40);",
     "for(var r=0;r<5;r++)for(var k=0;k<7;k++)if(r*7+k<31)c.fillText(String(r*7+k+1),14+k*34,110+r*40);"),
]


def main():
    s = FILME.read_text(encoding="utf-8")
    for velho, novo in TROCAS:
        assert s.count(velho) == 1, f"trecho não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
    for velho, novo in TROCAS_RODADA_4:
        assert s.count(velho) == 1, f"trecho da rodada 4 não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
    s, n = re.subn(r"var rows=\[.*?\]\];", lambda m: TABELA, s, count=1, flags=re.S)
    assert n == 1, "tabela da abertura não encontrada"
    ini, fim = s.index("// ordem cronológica"), s.index("var NCH=CAPS.length-1;")
    s = s[:ini] + CAPS + s[fim:]
    linhas = s.split("\n")
    sem_legenda_antiga = [l for l in linhas if not l.startswith("st.cap=[")]  # legendas antigas, nunca exibidas
    assert len(linhas) - len(sem_legenda_antiga) == 5, "esperava 5 legendas antigas (st.cap)"
    FILME.write_text("\n".join(sem_legenda_antiga), encoding="utf-8")
    print("film.html corrigido")


if __name__ == "__main__":
    main()
