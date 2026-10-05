// Site v2: cada caso tem três tempos na rolagem. Na 1ª metade o vídeo da cena anda com o scroll (clipes.js busca o
// quadro); na 2ª o documento real aparece sobre a tela do último quadro (--doc), o destaque se desenha (--destaque)
// e o quadro abre espaço para o texto (--lado). Um caso "só cena" (.so-cena, a abertura) usa a rolagem inteira no vídeo.
// Sem JS, sem IntersectionObserver ou com movimento reduzido: nada disso, e a página fica empilhada (pôster + documento
// + destaque + texto), porque o CSS parte de --doc = --destaque = 1. O trilho lateral marca a seção mais perto do meio.
(function(){
'use strict';
if(!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
var casos=[].slice.call(document.querySelectorAll('.caso'));
if(!casos.length)return;
// tela baixa (celular deitado): o palco preso não cabe com o texto; fica empilhada, como sem JS, e acompanha a rotação
var CURTA=matchMedia('(max-height: 520px)');
function modo(){document.documentElement.classList.toggle('js-v2',!CURTA.matches);}
modo();
var DOC=[.5,.6],DESTAQUE=[.6,.7],LADO=[.62,.72],pendente=false;
var trilho=[].slice.call(document.querySelectorAll('nav.trilho a[href^="#"]'));
var secoes=trilho.map(function(a){return document.getElementById(a.getAttribute('href').slice(1));});
function faixa(p,f){return Math.max(0,Math.min(1,(p-f[0])/(f[1]-f[0])));}
function marcar(){
  var meio=innerHeight/2,atual=-1;
  secoes.forEach(function(s,i){if(s&&s.getBoundingClientRect().top<=meio)atual=i;});
  trilho.forEach(function(a,i){if(i===atual)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});
}
// a roda do mouse anda aos saltos (100 px por clique): o progresso mostrado persegue o da rolagem com amortecimento
// exponencial, quadro a quadro, igual na descida e na subida; fora da tela (salto pelo menu) ele vai direto ao alvo
var SEGUE=.16,ultimoT=0; // fração do caminho que falta percorrida a cada quadro de 60 Hz
function atualizar(agora){
  pendente=false;
  var dt=ultimoT?Math.min(100,agora-ultimoT):16.7,k=1-Math.pow(1-SEGUE,dt/16.7),anda=false;
  ultimoT=agora;
  marcar();
  if(CURTA.matches)return;
  casos.forEach(function(c){
    var r=c.getBoundingClientRect(),curso=c.offsetHeight-innerHeight;
    if(r.bottom<-innerHeight||r.top>2*innerHeight){c.__p=undefined;return;}
    var alvo=curso>0?Math.max(0,Math.min(1,-r.top/curso)):1;
    var p=c.__p===undefined||r.bottom<=0||r.top>=innerHeight?alvo:c.__p+(alvo-c.__p)*k;
    if(Math.abs(alvo-p)<.0004)p=alvo;else anda=true;
    c.__p=p;
    var fig=c.querySelector('figure.clipe'),cena=c.classList.contains('so-cena')?1:.5;
    if(fig&&fig.__clipe)fig.__clipe.seek(Math.min(1,p/cena)*fig.__clipe.dur);
    if(cena===1)return;
    var lado=faixa(p,LADO);
    c.style.setProperty('--doc',faixa(p,DOC));
    c.style.setProperty('--destaque',faixa(p,DESTAQUE));
    c.style.setProperty('--lado',lado);
    c.style.setProperty('--vis',lado>0?'visible':'hidden'); // texto invisível fora do fluxo de foco (teclado)
  });
  if(anda)pedir();else ultimoT=0;
}
function pedir(){if(!pendente){pendente=true;requestAnimationFrame(atualizar);}}
addEventListener('scroll',pedir,{passive:true});
addEventListener('resize',pedir);
if(CURTA.addEventListener)CURTA.addEventListener('change',function(){modo();pedir();});
pedir();
})();
