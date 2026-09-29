// Site v2: cada caso tem três tempos na rolagem. Na 1ª metade o vídeo da cena anda com o scroll (clipes.js busca o
// quadro); na 2ª o documento real aparece sobre a tela do último quadro (--doc), o destaque se desenha (--destaque)
// e o quadro abre espaço para o texto (--lado). Sem JS, sem IntersectionObserver ou com movimento reduzido: nada disso,
// e a página fica empilhada (pôster + documento + destaque + texto), porque o CSS parte de --doc = --destaque = 1.
(function(){
'use strict';
if(!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
var casos=[].slice.call(document.querySelectorAll('.caso'));
if(!casos.length)return;
document.documentElement.classList.add('js-v2');
var CENA=.5,DOC=[.5,.6],DESTAQUE=[.6,.7],LADO=[.62,.72],pendente=false;
function faixa(p,f){return Math.max(0,Math.min(1,(p-f[0])/(f[1]-f[0])));}
function atualizar(){
  pendente=false;
  casos.forEach(function(c){
    var r=c.getBoundingClientRect(),curso=c.offsetHeight-innerHeight;
    if(r.bottom<-innerHeight||r.top>2*innerHeight)return;
    var p=curso>0?Math.max(0,Math.min(1,-r.top/curso)):1;
    var fig=c.querySelector('figure.clipe');
    if(fig&&fig.__clipe)fig.__clipe.seek(Math.min(1,p/CENA)*fig.__clipe.dur);
    c.style.setProperty('--doc',faixa(p,DOC));
    c.style.setProperty('--destaque',faixa(p,DESTAQUE));
    c.style.setProperty('--lado',faixa(p,LADO));
  });
}
function pedir(){if(!pendente){pendente=true;requestAnimationFrame(atualizar);}}
addEventListener('scroll',pedir,{passive:true});
addEventListener('resize',pedir);
pedir();
})();
