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
 ['jul → set/2026','Diversas obras no sistema.','Lê o desenho, mede e orça. Nos 19 serviços SINAPI conferidos, desvio máximo de 0,25%. Código com assistentes de IA.',function(t){return t<5?['R$ 24,5 mi','maior proposta']:(t<7.6?['0,25%','desvio máx. vs. SINAPI']:['diversas obras','no sistema']);},'A gestão de obra deste sistema ainda não rodou em obra real.'],
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
# Rodada 9: reenquadramento do restaurante (as 12 miniaturas inteiras no último quadro)
TROCAS_RODADA_9 = [
    ("st.cam=[[0,[7,8.5,13],[0,1.2,0]],[5,[1,10,14.5],[0,1,0]],[10,[-3,15.5,19.5],[0,.6,-3]]];",
     "st.cam=[[0,[7,8.5,13],[0,1.2,0]],[5,[1,10,14.5],[0,1,0]],[10,[-2,18.5,23],[0,.4,-2.6]]];"),
]
# Rodada 4: cenas portadas da página (SC[9], SC[10], SC[11]), coladas antes do render nesta ordem: casa → içamento → zip
# (SC.push dá os índices). Estilo do filme: materiais por P(), um só acento ORANGE, nenhum texto pintado.
CENA_CASA = """// ================= CASA (portada da página: casa-viaja, 10 s) =================
// três viagens: caixa 1, caixa 2 (face de junção aberta: pórtico, viga de transferência e filme) e o telhado em kit,
// montado no pátio pelos montadores e içado inteiro. Acento: a viga de transferência. Sem texto.
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
slab(34,30,0xB8C99A,g);box(4.2,.05,40,0x9A958D,9,.04,0,g,true);for(var i=-19;i<20;i+=3)box(.12,.06,1.4,0xF3EFE6,9,.07,i,g,true);
[[-11,-8,1.3],[-12,4,1.1],[-8,9,1],[-6,-11,1.2],[-13,-2,.9],[3,10,1.1],[-6,10.5,.8],[14,-9,1],[14,6,1.1]].forEach(function(t){tree(t[0],t[1],t[2],g);});
var W=6,H=2.85,D=3,PIL=.55;for(var r=0;r<3;r++)[-2.6,0,2.6].forEach(function(x){box(.24,PIL,.24,0xC9C2B4,x,PIL/2,-2.5+r*2.5,g);});
function caixa(front){var q=new THREE.Group(),oz=front?-(D/2-.09):(D/2-.09),cz=front?(D/2-.06):-(D/2-.06);
 box(W,.22,D,0x8E9AA6,0,.11,0,q);box(W-.03,.05,D-.03,0xC7A57A,0,.245,0,q,true);
 box(W,H,.12,0xF3ECDD,0,.27+H/2,cz,q);box(.12,H,D,0xF3ECDD,-(W/2-.06),.27+H/2,0,q);box(.12,H,D,0xF3ECDD,W/2-.06,.27+H/2,0,q);box(W,.12,D,0xF3ECDD,0,.27+H-.06,0,q);
 box(.18,H-.12,.18,0x7D8E9E,-(W/2-.21),.27+(H-.12)/2,oz,q);box(.18,H-.12,.18,0x7D8E9E,W/2-.21,.27+(H-.12)/2,oz,q);box(W-.24,.42,.2,ORANGE,0,.27+H-.12-.21,oz,q);
 var dl=Math.hypot(W-.5,H-.5),da=Math.atan2(H-.5,W-.5);[1,-1].forEach(function(s){box(dl,.05,.05,0x7D8E9E,0,.27+(H-.42)/2,oz,q,true).rotation.z=s*da;});
 var fm=new THREE.Mesh(new THREE.BoxGeometry(W-.2,H-.5,.03),new THREE.MeshStandardMaterial({color:0xE3EBF2,transparent:true,opacity:.5,roughness:.3,depthWrite:false}));
 fm.position.set(0,.27+(H-.42)/2,oz+(front?-.14:.14));q.add(fm);q.filme=fm;
 if(front){box(1.3,2.2,.08,0xC7A57A,-1.55,.27+1.1,D/2+.05,q);box(1.3,2.2,.08,0xC7A57A,1.55,.27+1.1,D/2+.05,q);box(2.6,.6,.08,0xF3ECDD,0,.27+2.5,D/2+.05,q);box(2.55,2.05,.02,0x3A302A,0,.27+1.05,D/2+.02,q,true);}
 else box(1.2,1,.08,0xBFD8E6,-1.6,.27+1.5,-D/2-.05,q,true);
 box(.08,1,1.1,0xBFD8E6,-W/2-.05,.27+1.4,0,q,true);box(.08,1,1.1,0xBFD8E6,W/2+.05,.27+1.4,0,q,true);g.add(q);return q;}
st.c1=caixa(true);st.c2=caixa(false);
// telhado gambrel em kit: cada peça tem a pose deitada (p0, no chão do pátio) e a pose montada (p1)
var XQ=1.68,HQ=(3-XQ)*Math.tan(Math.PI/3),HH=HQ+XQ*Math.tan(Math.PI/6),RL=6.6;st.HH=HH;
st.roof=new THREE.Group();g.add(st.roof);var kit=[],ni=0;
function peca(m,p1,r1,p0,r0){m.rotation.copy(r1);var q1=m.quaternion.clone();m.rotation.copy(r0);var q0=m.quaternion.clone();m.position.copy(p1);m.quaternion.copy(q1);kit.push({m:m,p0:p0,q0:q0,p1:p1,q1:q1});st.roof.add(m);}
function agua(x0,y0,x1,y1){var L=Math.hypot(x1-x0,y1-y0),m=new THREE.Mesh(new THREE.BoxGeometry(L,.16,RL),P(0x4A4E55));m.castShadow=m.receiveShadow=true;edge(m);
 var ang=Math.atan2(y1-y0,x1-x0);if(ang>Math.PI/2)ang-=Math.PI;peca(m,new THREE.Vector3((x0+x1)/2,(y0+y1)/2,0),new THREE.Euler(0,0,ang),new THREE.Vector3(ni%2?.4:-.4,.08+ni*.18,0),new THREE.Euler(0,0,0));ni++;}
[-1,1].forEach(function(s){agua(s*3.3,0,s*XQ,HQ);agua(s*XQ,HQ,0,HH);});
var shp=new THREE.Shape();shp.moveTo(-3,0);shp.lineTo(-XQ,HQ);shp.lineTo(0,HH);shp.lineTo(XQ,HQ);shp.lineTo(3,0);shp.closePath();
[-1,1].forEach(function(s,i){var f=new THREE.Mesh(new THREE.ExtrudeGeometry(shp,{depth:.1,bevelEnabled:false}),P(0xF3ECDD));f.castShadow=true;edge(f);
 peca(f,new THREE.Vector3(0,0,s*2.95-.05),new THREE.Euler(0,0,0),new THREE.Vector3(-HH/2,.9+i*.12,0),new THREE.Euler(0,Math.PI/2,-Math.PI/2,'ZYX'));});
function montar(k){kit.forEach(function(p,i){var ki=ease(k*1.6-i*.12);p.m.position.lerpVectors(p.p0,p.p1,ki);p.m.quaternion.copy(p.q0).slerp(p.q1,ki);});}
// caminhão (cabine para +z: entra e sai de frente) e guindaste articulado
st.truck=new THREE.Group();g.add(st.truck);box(7.4,.5,2.6,0xDCD5C6,-.6,1.05,0,st.truck);box(2,2.2,2.5,0x8E9AA6,3.9,1.9,0,st.truck);box(1.9,.9,2.3,0xBFD8E6,3.95,2.7,0,st.truck,true);
[[-3.2,-1.2],[-3.2,1.2],[-1.6,-1.2],[-1.6,1.2],[3.5,-1.2],[3.5,1.2]].forEach(function(w){cyl(.55,.5,0x2B2F33,w[0],.55,w[1],st.truck,14).rotation.z=Math.PI/2;});st.truck.rotation.y=-Math.PI/2;
var crane=new THREE.Group();crane.position.set(5.5,0,-6.5);g.add(crane);box(4.6,.9,2.4,0xE8B53E,0,.95,0,crane);
[[-1.5,-1.3],[-1.5,1.3],[1.5,-1.3],[1.5,1.3]].forEach(function(w){cyl(.6,.6,0x2B2F33,w[0],.6,w[1],crane,14).rotation.z=Math.PI/2;});
[[-2.2,-1.5],[-2.2,1.5],[2.2,-1.5],[2.2,1.5]].forEach(function(o){box(.3,.3,1.3,0xB88A2E,o[0],.55,o[1]*.8,crane);cyl(.12,.7,0x7D8E9E,o[0],.35,o[1]*1.2,crane,8);});
var turret=new THREE.Group();turret.position.set(-.6,1.4,0);crane.add(turret);box(2.4,.9,1.9,0xB88A2E,0,.45,0,turret);box(1.2,1.1,1.4,0xE8B53E,-1.2,.55,.9,turret);
var pivot=new THREE.Group();pivot.position.set(.6,.8,0);turret.add(pivot);var L=11.5;box(L,.5,.5,0xE8B53E,L/2,0,0,pivot);box(L*.5,.36,.36,0xB88A2E,L*.9,0,0,pivot);
var tip=new THREE.Object3D();tip.position.set(L,0,0);pivot.add(tip);
var cabo=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]),new THREE.LineBasicMaterial({color:0x2a2622}));cabo.frustumCulled=false;g.add(cabo);
var hook=box(.5,.35,.5,0xB88A2E,0,0,0,g);
function boneco(x,z,ry){var q=new THREE.Group();cyl(.14,.75,0x6F8FA8,0,.375,0,q,8);box(.5,.6,.3,0xE3C46A,0,1.05,0,q);var h=new THREE.Mesh(new THREE.SphereGeometry(.17,10,8),P(0xE0B294));h.position.y=1.52;h.castShadow=true;q.add(h);cyl(.2,.12,0xE8B53E,0,1.66,0,q,8);q.position.set(x,0,z);q.rotation.y=ry;q.visible=false;g.add(q);return q;}
var YARD=new THREE.Vector3(3,0,-11.5),TOP=new THREE.Vector3(0,PIL+.27+H,0),BED=new THREE.Vector3(9,1.3,-.6);
var gente=[boneco(-.4,-10.6,Math.PI/2),boneco(6.8,-14,-Math.PI/2),boneco(3.6,-15,0)];
var TG={truck:new THREE.Vector3(9,0,0),site1:new THREE.Vector3(0,0,1.5),site2:new THREE.Vector3(0,0,-1.5),mid:new THREE.Vector3(0,0,0)};
var cur=new THREE.Vector3(9,0,0),tipW=new THREE.Vector3();
// mira do guindaste pelo eixo da torre (x 4,9; z −6,5): eixo, pivô (a 0,6) e alvo ficam alinhados, então a mira é exata e pura em t
function aimBoom(target){var dx=target.x-4.9,dz=target.z+6.5,D=Math.hypot(dx,dz);turret.rotation.y=Math.atan2(-dz,dx);pivot.rotation.z=Math.acos(Math.min(.98,(D-.6)/L));}
function icar(t,t0,t1,bx,fr,to,restY,r0,r1,hy){var a=ramp(t,t0,t0+(t1-t0)*.3),b=ramp(t,t0+(t1-t0)*.3,t0+(t1-t0)*.7),c=ramp(t,t0+(t1-t0)*.7,t1);
 var x=lerp(fr.x,to.x,b),z=lerp(fr.z,to.z,b),y=c>0?lerp(hy,restY,c):lerp(fr.y,hy,a);bx.position.set(x,y,z);bx.rotation.y=lerp(r0,r1,b);cur.set(x,0,z);return bx;}
st.cam=[[0,[21.2,9,28.4],[3,2,-1]],[2.5,[22,9.5,18.5],[4,2.5,-.5]],[5,[25,15,-10],[3,3,-2]],[7.5,[30,20,-4],[4,.5,-9]],[10,[8,28,32],[.3,2.5,-.6]]];
st.run=function(t){
 // caminhão: da névoa (z −16) ao ponto de descarga (z 0) e de volta, três vezes
 var tz;if(t<.8)tz=lerp(-16,0,ramp(t,.2,.8));else if(t<3)tz=0;else if(t<3.6)tz=lerp(0,16,ramp(t,3,3.6));else if(t<4.2)tz=lerp(-16,0,ramp(t,3.6,4.2));
 else if(t<6.2)tz=0;else if(t<6.8)tz=lerp(0,16,ramp(t,6.2,6.8));else if(t<7.4)tz=lerp(-16,0,ramp(t,6.8,7.4));else if(t<8.8)tz=0;else tz=lerp(0,16,ramp(t,8.8,9.4));
 st.truck.position.set(9,0,tz);
 var att=null,topo=0;function naCarroceria(o,ry){o.position.set(BED.x,BED.y,tz+BED.z);o.rotation.y=ry;}
 function filme(c,a,b){c.filme.material.opacity=.5*(1-ramp(t,a,b));c.filme.visible=c.filme.material.opacity>.01;}
 if(t<.8)naCarroceria(st.c1,-Math.PI/2);else if(t<3){att=icar(t,.8,3,st.c1,BED,TG.site1,PIL,-Math.PI/2,0,7.2);topo=3.4;}else{st.c1.position.set(0,PIL,1.5);st.c1.rotation.y=0;}
 filme(st.c1,3,3.4);
 st.c2.visible=t>=3.6;
 if(st.c2.visible){if(t<4.2)naCarroceria(st.c2,Math.PI/2);else if(t<6.2){att=icar(t,4.2,6.2,st.c2,BED,TG.site2,PIL,Math.PI/2,0,7.2);topo=3.4;}else{st.c2.position.set(0,PIL,-1.5);st.c2.rotation.y=0;}}
 filme(st.c2,6.2,6.6);
 st.roof.visible=t>=6.8;
 if(t<7.4){naCarroceria(st.roof,0);montar(0);}
 else if(t<7.8){att=icar(t,7.4,7.8,st.roof,BED,YARD,0,0,0,5.5);topo=1.2;montar(0);}
 else if(t<8.8){st.roof.position.copy(YARD);montar(ramp(t,7.85,8.75));}
 else if(t<9.8){att=icar(t,8.8,9.8,st.roof,YARD,TOP,TOP.y,0,0,5.4);topo=HH+.3;montar(1);}
 else{st.roof.position.copy(TOP);montar(1);}
 var mexida=ramp(t,7.8,7.95)*(1-ramp(t,8.75,8.85));
 gente.forEach(function(q,i){q.visible=t>=7.4;var ph=t*18+i*2;q.position.y=mexida*.12*Math.abs(Math.sin(ph));q.rotation.z=mexida*.08*Math.sin(ph*.7);});
 aimBoom(att?cur:(t<.8?TG.truck:t<3.6?TG.site1:t<4.2?TG.truck:t<6.8?TG.site2:t<7.4?TG.truck:t<8.8?YARD:TG.mid));
 g.updateMatrixWorld(true);tip.getWorldPosition(tipW);
 var hookY=att?att.position.y+topo:tipW.y-2.2;hook.position.set(tipW.x,hookY,tipW.z);
 cabo.geometry.setFromPoints([tipW,new THREE.Vector3(tipW.x,hookY+.18,tipW.z)]);};
})();"""
CENA_ICAMENTO = """// ================= IÇAMENTO (portado da página: icamento, 8 s) =================
// o módulo sai da carreta, sobe pelo balancim com os cabos na vertical (só tração nos olhais), anda e pousa no radier.
// Acento: o cavalo da carreta. Sem texto. t 0..10 = 8 s: 0→0,6 s parado · 0,6→3 sobe · 3→5,4 anda · 5,4→7,2 pousa · 7,2→8 parado
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
var L=8,C=3.2,H=2.9,CH=.3,TOPO=6.5,XC=6,XR=-6;
slab(60,40,0xB8C99A,g);box(L+2,.5,C+1.6,0xC9C2B4,XR,.25,0,g);
box(L+1,.5,C,0x4A4E55,XC,.55,0,g);box(L+1,.4,C+.6,0x8E9AA6,XC,1,0,g);st.cavalo=box(2.4,2.6,C+.4,ORANGE,XC+L/2+1.9,1.5,0,g);box(2.2,1,C+.2,0xBFD8E6,XC+L/2+1.9,2.5,0,g,true);
[[XC-3,-1.6],[XC-3,1.6],[XC+1,-1.6],[XC+1,1.6],[XC+L/2+1.9,-1.8],[XC+L/2+1.9,1.8]].forEach(function(w){cyl(.5,.4,0x2B2F33,w[0],.5,w[1],g,14).rotation.x=Math.PI/2;});
st.mod=new THREE.Group();g.add(st.mod);box(L,CH,C,0x7D8E9E,0,CH/2,0,st.mod);box(L-.1,H-CH,C-.1,0xF3ECDD,0,CH+(H-CH)/2,0,st.mod);box(L+.2,.14,C+.3,0x4A4E55,0,H+.07,0,st.mod);
box(1.1,1.9,.06,0xC7A57A,-2.2,CH+.95,C/2,st.mod,true);box(1.4,.9,.06,0xBFD8E6,1.6,CH+1.6,C/2,st.mod,true);
var cx=L/2-.2,cz=C/2+.05,cantos=[[-cx,-cz],[cx,-cz],[-cx,cz],[cx,cz]];
cantos.forEach(function(c){var o=new THREE.Mesh(new THREE.TorusGeometry(.16,.05,8,20),P(0xE8B53E));o.position.set(c[0],CH+.05,c[1]);st.mod.add(o);});
st.bal=new THREE.Group();g.add(st.bal);box(L,.25,.25,0xE8B53E,0,0,cz,st.bal);box(L,.25,.25,0xE8B53E,0,0,-cz,st.bal);box(.25,.25,C+.1,0xE8B53E,-cx,0,0,st.bal);box(.25,.25,C+.1,0xE8B53E,cx,0,0,st.bal);
var gancho=new THREE.Mesh(new THREE.TorusGeometry(.3,.08,8,20),P(0x4A4E55));g.add(gancho);
st.cabos=new THREE.LineSegments(new THREE.BufferGeometry(),new THREE.LineBasicMaterial({color:0x2a2622}));st.cabos.frustumCulled=false;g.add(st.cabos);
tree(-14,-9,1.2,g);tree(13,-10,1,g);tree(-12,9,.9,g);tree(16,7,1.1,g);
st.cam=[[0,[24,13,24],[6,3.5,0]],[3.3,[21,16,22],[5,6.5,0]],[6.6,[-4,17,26],[-3,6.5,0]],[10,[-19,12,24],[0,3,0]]];
st.run=function(t){var x=lerp(XC,XR,ramp(t,3.75,6.75)),y=t<6.75?lerp(1.2,TOPO,ramp(t,.75,3.75)):lerp(TOPO,.5,ramp(t,6.75,9));
 st.mod.position.set(x,y,0);var bY=y+H+2.2,hY=bY+2.6,pts=[];st.bal.position.set(x,bY,0);gancho.position.set(x,hY,0);
 cantos.forEach(function(c){pts.push(x+c[0],bY,c[1],x+c[0],y+CH+.05,c[1]);pts.push(x+c[0],bY,c[1],x,hY,0);}); // cabo vertical balancim→olhal; eslinga balancim→gancho
 pts.push(x,hY,0,x,hY+30,0); // cabo do guindaste, para fora do quadro
 st.cabos.geometry.setAttribute('position',new THREE.Float32BufferAttribute(pts,3));};
})();"""
CENA_ZIP = """// ================= 36 MINUTOS (portado da página: 36min, 10 s) =================
// a planta real do cliente (já publicada, anônima) no chão; a linha de cota varre a planta e as paredes de papel sobem
// nos pixels vermelhos; o relógio analógico anda de 11:35 a 12:11 com a varredura; a proposta empilha na mesa.
// Acento: a cota (e o ponteiro dos minutos). Sem texto. t: pacote pousa 0,3→0,9 · varredura e relógio 1,2→8,0 · páginas 8,0→9,4 · parado até 10
(function(){var g=new THREE.Group();S.add(g);var st={g:g};SC.push(st);
var PW=16,PH=PW*440/1400,CELL=5,HW=1.4;
slab(PW+4,PH+5,0xE2D6C1,g);
var planoTex;PRONTOS.push(new Promise(function(ok){planoTex=new THREE.TextureLoader().load('../site/img/upa-plan-grey.webp',ok,undefined,ok);}));
planoTex.encoding=THREE.sRGBEncoding;planoTex.anisotropy=4;
var planta=new THREE.Mesh(new THREE.PlaneGeometry(PW,PH),new THREE.MeshStandardMaterial({map:planoTex,roughness:1}));planta.rotation.x=-Math.PI/2;planta.position.y=.005;planta.receiveShadow=true;g.add(planta);
var wx=[],dummy=new THREE.Object3D();st.walls=null;
PRONTOS.push(new Promise(function(ok){var im=new Image();im.onload=function(){var w=1400,h=440,cv=document.createElement('canvas');cv.width=w;cv.height=h;var cx=cv.getContext('2d');cx.drawImage(im,0,0,w,h);
 var d=cx.getImageData(0,0,w,h).data,cells=[];
 for(var gy=0;gy<h;gy+=CELL)for(var gx=0;gx<w;gx+=CELL){var n=0;for(var y=gy;y<gy+CELL&&y<h;y++)for(var x=gx;x<gx+CELL&&x<w;x++){var k=(y*w+x)*4;if(d[k]>150&&d[k+1]<90&&d[k+2]<90)n++;}if(n>=CELL*CELL*.3)cells.push([gx,gy]);}
 var s=PW/w;st.walls=new THREE.InstancedMesh(new THREE.BoxGeometry(CELL*s,1,CELL*s),P(0xF3ECDD),cells.length);st.walls.castShadow=st.walls.receiveShadow=true;
 cells.forEach(function(c){wx.push([(c[0]+CELL/2)*s-PW/2,(c[1]+CELL/2)*s-PH/2]);});g.add(st.walls);ok();};im.onerror=ok;im.src='../site/img/upa-plan.webp';}));
var COTA=new THREE.MeshBasicMaterial({color:ORANGE});st.sweep=box(.1,.08,PH+1,COTA,0,.1,0,g,true);var sweepTop=box(.05,2.4,.05,COTA,0,1.2,-PH/2-.5,g,true);
var mesa=new THREE.Group();mesa.position.set(PW/2-1.5,0,PH/2+2.6);g.add(mesa);
box(4.2,.16,2.2,0xC7A57A,0,1.05,0,mesa);[[-1.9,-.9],[1.9,-.9],[-1.9,.9],[1.9,.9]].forEach(function(p){box(.14,1,.14,0x8C6E4E,p[0],.5,p[1],mesa);});
st.zip=box(.9,.6,.75,0xC9B79A,-1.3,1.43,0,mesa);
st.pages=[];for(var i=0;i<7;i++){var pg=box(1.1,.03,1.5,0xFFFFFF,1,1.15+i*.035,0,mesa,true);pg.rotation.y=(i%2?.05:-.04);pg.visible=false;st.pages.push(pg);}
// relógio analógico do filme (mostrador com 12 traços, sem algarismos) num pedestal ao lado da mesa
var CX=PW/2+2.4,CY=2.1,CZ=PH/2+.2;box(.5,CY-.6,.5,0xC9B79A,CX,(CY-.6)/2,CZ,g);var face=cyl(.9,.1,0xFBF8F0,CX,CY,CZ,g,32);face.rotation.x=Math.PI/2;
for(var q=0;q<12;q++){var tk=box(.05,.14,.02,0x1E1A17,CX+Math.sin(q*Math.PI/6)*.72,CY+Math.cos(q*Math.PI/6)*.72,CZ+.06,g,true);tk.rotation.z=-q*Math.PI/6;}
st.hm=box(.08,.48,.03,0x1E1A17,CX,CY,CZ+.09,g,true);st.hm.geometry.translate(0,.24,0);st.mm=box(.05,.72,.03,ORANGE,CX,CY,CZ+.11,g,true);st.mm.geometry.translate(0,.36,0);
tree(-PW/2-3.5,-PH/2-1,.9,g);tree(PW/2+4,-PH/2-2,.8,g);
st.cam=[[0,[3,28,8],[3,0,1.5]],[2.5,[-10,5,18],[3.5,1,1]],[7,[-4,7,22],[9,1,1.5]],[10,[17,8,17],[6,1,2]]];
st.run=function(t){var p=cl((t-1.2)/6.8),sx=lerp(-PW/2-.4,PW/2+2.6,p);var lx=Math.min(sx,PW/2+.4);st.sweep.position.x=lx;sweepTop.position.x=lx;st.sweep.visible=sweepTop.visible=t>1&&t<8.3;
 if(st.walls){for(var i=0;i<wx.length;i++){var hh=Math.max(.001,ease((sx-wx[i][0])/2.5)*HW);dummy.position.set(wx[i][0],.01+hh/2,wx[i][1]);dummy.scale.set(1,hh,1);dummy.updateMatrix();st.walls.setMatrixAt(i,dummy.matrix);}st.walls.instanceMatrix.needsUpdate=true;}
 st.zip.position.y=lerp(6,1.43,ramp(t,.3,.9));
 var mm=35+36*p;st.mm.rotation.z=-(mm/60)*Math.PI*2;st.hm.rotation.z=-((11+mm/60)/12)*Math.PI*2; // 11:35 → 12:11, linear com a varredura
 st.pages.forEach(function(pg,i){var a=ramp(t,8+i*.17,8.35+i*.17);pg.visible=a>0;pg.position.y=lerp(3,1.15+i*.035,a);pg.position.z=lerp(-1,0,a);});};
})();"""
# Rodada 4: blocos novos do filme "limpo" (clipes de fundo da história). Cada entrada é (âncora única, texto antes, texto depois).
INSERCOES_RODADA_4 = [
    # <style>: ?limpo esconde todo o DOM por cima do canvas (render_clipes.py)
    ("#end .cta span{font:500 15px PM;color:#1E1A17}",
     "",
     "\n/* ?limpo (render_clipes.py): só o canvas; renderAt continua escrevendo nestes nós, eles só não aparecem */\n"
     ".limpo #cap,.limpo #hud,.limpo #num,.limpo #cover,.limpo #end,.limpo .tag,.limpo .bar,.limpo .scrim,.limpo #prog,"
     ".limpo #wipe,.limpo #fade,.limpo .vig{display:none!important}"),
    # <script>, primeira linha: a flag ?limpo e as promessas das texturas das cenas portadas
    ("var R=new THREE.WebGLRenderer",
     "if(/[?&]limpo\\b/.test(location.search))document.documentElement.classList.add('limpo');\n"
     "var PRONTOS=[]; // promessas das texturas que as cenas portadas carregam (a planta real); render_clipes.py espera window.PRONTO\n",
     ""),
    # render: logo depois de camAt, a duração de cada cena e renderCena(i, t)
    ("function camAt(st,t,T){var u=ioSine(t/10)*.85+(t/10)*.15;st.cp.getPoint(u,tmp);st.ct.getPoint(u,tmp2);\n"
     "  tmp.x+=Math.sin(T*.63)*.06+Math.sin(T*1.7)*.02;tmp.y+=Math.sin(T*.81+1)*.05;tmp.z+=Math.cos(T*.57)*.05;cam.position.copy(tmp);cam.lookAt(tmp2);}",
     "",
     "\n// clipes da história (render_clipes.py): a cena i no tempo local t (0..10), sem DOM por cima; puro em (i, t), independente de ORDER/START\n"
     "var DURSC=[];ORDER.forEach(function(s,k){DURSC[s]=DUR[k];});DURSC[9]=10;DURSC[10]=8;DURSC[11]=10;\n"
     "window.renderCena=function(i,t){SC.forEach(function(s,j){s.g.visible=j===i;});sun.position.set(-8,16,10);var st=SC[i];st.run(t);"
     "camAt(st,t,t*DURSC[i]/10);R.render(S,cam);cur=-1;};"),
    # última linha do script: render_clipes.py espera as texturas antes do primeiro quadro
    ("renderAt(0);",
     "",
     "\nwindow.PRONTO=Promise.all(PRONTOS);"),
    # cena portada da casa (SC[9]): antes do render; as do içamento e do zip entram depois dela, com a mesma âncora
    ("// ================= render =================",
     CENA_CASA + "\n",
     ""),
    # cena portada do içamento (SC[10]): depois da casa, antes do render
    ("// ================= render =================",
     CENA_ICAMENTO + "\n",
     ""),
    # cena portada dos 36 minutos (SC[11]): depois do içamento, antes do render
    ("// ================= render =================",
     CENA_ZIP + "\n",
     ""),
]

# Formação sem a contagem de semestres que faltam (cartão de abertura e cartão final). Cada entrada: (antes, depois, vezes).
TROCAS_FORMACAO = [
    ("7º semestre, faltam 3 · Sistemas", "7º semestre · Sistemas", 2),
    ("Faltam 3 semestres para o diploma.<br>Não falta obra feita.", "Diploma em curso.<br>Obra já feita.", 1),
]


def main():
    s = FILME.read_text(encoding="utf-8")
    for velho, novo in TROCAS:
        assert s.count(velho) == 1, f"trecho não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
    for velho, novo in TROCAS_RODADA_4:
        assert s.count(velho) == 1, f"trecho da rodada 4 não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
    for velho, novo in TROCAS_RODADA_9:
        assert s.count(velho) == 1, f"trecho da rodada 9 não encontrado (ou repetido): {velho[:60]!r}"
        s = s.replace(velho, novo)
    for velho, novo, vezes in TROCAS_FORMACAO:
        assert s.count(velho) == vezes, f"trecho da formação: esperava {vezes}×: {velho[:60]!r}"
        s = s.replace(velho, novo)
    for ancora, antes, depois in INSERCOES_RODADA_4:
        assert s.count(ancora) == 1, f"âncora da rodada 4 não encontrada (ou repetida): {ancora[:60]!r}"
        s = s.replace(ancora, antes + ancora + depois)
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
