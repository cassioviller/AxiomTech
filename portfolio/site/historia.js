// História em cenas: quando a frase cruza o meio da tela, o fundo troca de cena.
// Regras: rolagem nativa (o script nunca move a página nem bloqueia o gesto); sem JS, sem
// IntersectionObserver ou com prefers-reduced-motion a página fica empilhada e estática, cada frase com a sua imagem.
(function(){
'use strict';
var H=window.Historia={ativa:null};
var cenas=[].slice.call(document.querySelectorAll('.cena[data-passo]'));
var palco=document.querySelector('.palco');
if(!cenas.length||!palco||!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;

// cada fundo vai para o palco fixo; a maquete fica hidden fora da sua cena, para só uma renderizar por vez
var fundos={},esconder={};
cenas.forEach(function(c){
  var f=c.querySelector('.fundo');
  if(!f)return;
  fundos[c.dataset.passo]=f;
  if(f.classList.contains('maquete'))f.hidden=true;
  palco.appendChild(f);
});
document.documentElement.classList.add('js-historia');

function esconderDepois(passo){
  clearTimeout(esconder[passo]);
  esconder[passo]=setTimeout(function(){if(H.ativa!==passo)fundos[passo].hidden=true;},650);
}
function ativar(passo){
  if(passo===H.ativa)return;
  var antes=H.ativa&&fundos[H.ativa];
  if(antes){
    antes.classList.remove('ativo');
    if(antes.classList.contains('maquete'))esconderDepois(H.ativa);
  }
  H.ativa=passo;
  var f=fundos[passo];
  if(f){
    clearTimeout(esconder[passo]);
    if(f.hidden){f.hidden=false;dispatchEvent(new Event('resize'));} // a maquete remede o canvas ao voltar
    void f.offsetWidth; // aplica o display antes da opacidade, senão não há transição
    f.classList.add('ativo');
  }
}
function cenaNoCentro(){
  var meio=innerHeight/2;
  for(var i=0;i<cenas.length;i++){var r=cenas[i].getBoundingClientRect();if(r.top<=meio&&r.bottom>meio)return cenas[i];}
  return null;
}

var io=new IntersectionObserver(function(es){
  es.forEach(function(e){if(e.isIntersecting)ativar(e.target.dataset.passo);});
},{rootMargin:'-45% 0px -45% 0px',threshold:0});
cenas.forEach(function(c){io.observe(c);});
var inicial=cenaNoCentro();
if(inicial)ativar(inicial.dataset.passo);
})();
