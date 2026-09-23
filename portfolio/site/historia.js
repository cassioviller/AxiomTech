// História em cenas: quando a frase cruza o meio da tela, o fundo troca de cena e a régua de tempo marca o capítulo;
// nas cenas de maquete, o tempo da animação 3D é o progresso do scroll dentro da cena.
// Regras: rolagem nativa (o script nunca move a página nem bloqueia o gesto); sem JS, sem
// IntersectionObserver ou com prefers-reduced-motion a página fica empilhada e estática, cada frase com a sua imagem.
(function(){
'use strict';
// progresso 0→1 de uma cena: 0 quando o topo cruza o meio da tela, 1 quando o fim cruza
function progresso(topo,altura,alturaTela){
  if(!(altura>0))return 0;
  return Math.max(0,Math.min(1,(alturaTela/2-topo)/altura));
}
var H=window.Historia={ativa:null,progresso:progresso};

// saltar pela régua (ou pelo "Pular para o texto") leva o foco ao título do capítulo — vale também no modo empilhado
document.addEventListener('click',function(e){
  var a=e.target.closest&&e.target.closest('.regua a[href^="#"], a.pular');
  if(!a)return;
  var alvo=document.getElementById(a.getAttribute('href').slice(1));
  var titulo=alvo&&alvo.querySelector('.frase');
  if(titulo)setTimeout(function(){titulo.focus({preventScroll:true});},0);
});

var cenas=[].slice.call(document.querySelectorAll('.cena[data-passo]'));
var palco=document.querySelector('.palco');
if(!cenas.length||!palco||!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;

// cada fundo vai para o palco fixo; a maquete fica hidden fora da sua cena, para só uma renderizar por vez
var fundos={},esconder={},aguardando=0,pendente=false;
var regua=document.querySelector('.regua'),reguaOl=regua&&regua.querySelector('ol'),reguaData=regua&&regua.querySelector('.regua-data');
cenas.forEach(function(c){
  var f=c.querySelector('.fundo');
  if(!f)return;
  fundos[c.dataset.passo]=f;
  if(f.classList.contains('maquete'))f.hidden=true;
  palco.appendChild(f);
});
document.documentElement.classList.add('js-historia');

// maquete da cena ativa: o relógio da animação segue o scroll (seek congela o tempo), nunca anda sozinho
function sincronizar(){
  var f=H.ativa&&fundos[H.ativa];
  if(!f||!f.classList.contains('maquete'))return;
  var api=f.__maquete;
  if(!api||!api.dur){ // three.js ainda carregando: um só temporizador, repetido enquanto a cena da maquete estiver ativa
    if(!aguardando)aguardando=setTimeout(function(){aguardando=0;sincronizar();},200);
    return;
  }
  var r=document.querySelector('.cena[data-passo="'+H.ativa+'"]').getBoundingClientRect();
  api.seek(progresso(r.top,r.height,innerHeight)*api.dur*0.999);
}
// régua: exatamente um marco com aria-current="step"; a data do capítulo aparece à direita
function marcarRegua(passo){
  if(!regua)return;
  var antes=regua.querySelector('a[aria-current]');
  if(antes)antes.removeAttribute('aria-current');
  var a=regua.querySelector('a[href="#'+passo+'"]');
  if(!a)return;
  a.setAttribute('aria-current','step');
  var t=a.querySelector('time');
  if(reguaData)reguaData.textContent=t?t.textContent.split('→')[0].trim():reguaData.getAttribute('data-padrao'); // só o início: cabe no celular
  var li=a.parentNode;
  reguaOl.scrollLeft=li.offsetLeft-(reguaOl.clientWidth-li.offsetWidth)/2; // centraliza o marco: rola só a régua, nunca a página
}
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
  marcarRegua(passo);
  sincronizar();
}
function cenaNoCentro(){
  var meio=innerHeight/2;
  for(var i=0;i<cenas.length;i++){var r=cenas[i].getBoundingClientRect();if(r.top<=meio&&r.bottom>meio)return cenas[i];}
  return null;
}

var io=new IntersectionObserver(function(){
  // qualquer entrada ou saída na faixa do meio recalcula a cena: numa pequena volta, quem sai não "entra" de novo
  var c=cenaNoCentro();
  if(c)ativar(c.dataset.passo);
},{rootMargin:'-45% 0px -45% 0px',threshold:0});
cenas.forEach(function(c){io.observe(c);});
addEventListener('scroll',function(){
  if(pendente)return;
  pendente=true;
  requestAnimationFrame(function(){pendente=false;sincronizar();});
},{passive:true});
var inicial=cenaNoCentro();
if(inicial)ativar(inicial.dataset.passo);
})();
