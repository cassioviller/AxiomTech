// Clipes de fundo da história: um vídeo curto e mudo por capítulo, cujo tempo é o progresso da rolagem (historia.js chama
// fig.__clipe.seek(t), o mesmo contrato das maquetes). O clipe nunca anda sozinho: só currentTime, quantizado ao quadro,
// um seek em voo por vez, o último pedido vence. Carga em três portas: depois do 'load' da janela, quando a cena chega a
// 600 px da tela, e nunca com economia de dados, rede 2g, sem H.264 ou com ?clipes=nao (fica o pôster). Movimento
// reduzido, inclusive ligado no meio, descarrega tudo. A imagem só some (.viva) quando há um quadro pronto. Carregados
// ficam só os MAXIMO (2) clipes mais perto do meio da tela dentro da faixa de 600 px; arrumar() reavalia isso a cada
// seek, entrada/saída da faixa ou troca de movimento reduzido — nunca descarte por ordem de chegada.
(function(){
'use strict';
var figs=[].slice.call(document.querySelectorAll('figure.clipe'));
if(!figs.length||!('IntersectionObserver' in window))return;
var FPS=24,TETO=250,LENTOS=3,VOO=600,MAXIMO=2,FOLGA=100; // ms de um seek lento; lentos seguidos até congelar; ms sem 'seeked' = seek perdido; vídeos com dados; px de vantagem de quem já carregou
var v0=document.createElement('video'),con=navigator.connection||{};
var PODE=!/[?&]clipes=nao\b/.test(location.search)&&v0.canPlayType('video/mp4; codecs="avc1.64001F"')!==''
  &&!con.saveData&&!/^(slow-)?2g$/.test(con.effectiveType||'');
var reduzir=matchMedia('(prefers-reduced-motion: reduce)'),todas=[];
function quadro(t){return (Math.round(t*FPS)+0.5)/FPS;}
function depoisDoLoad(fn){if(document.readyState==='complete')fn();else addEventListener('load',fn);}
function chave(a){return a.dist()-(a.pronto?FOLGA:0);}
function arrumar(){
  if(reduzir.matches){todas.forEach(function(a){a.descarregar();});return;}
  var quer=todas.filter(function(a){return a.perto&&!a.morto;}).sort(function(a,b){return chave(a)-chave(b);}).slice(0,MAXIMO);
  todas.forEach(function(a){if(a.pronto&&quer.indexOf(a)<0)a.descarregar();});   // sai quem não está mais entre os mais perto
  quer.forEach(function(a){a.carregar();});                                      // entra quem está, se ainda não tiver dados
}

figs.forEach(function(fig){
  var v=fig.querySelector('video'),cena=fig.closest('.cena')||fig,src=fig.dataset.clipe,dur=parseFloat(fig.dataset.dur)||0;
  var alvo=-1,pedido=-1,emVoo=0,vivo=false,lentos=0,tinha=false,ligado=false;
  var api={dur:dur,frozen:false,pronto:false,morto:false,perto:false,dist:dist,carregar:carregar,
    seek:function(t){api.frozen=true;alvo=quadro(Math.max(0,Math.min(dur,t)));if(ligado)arrumar();pedir();},
    descarregar:descarregar};
  fig.__clipe=api;
  if(!PODE||!v||!dur||!src)return; // fica a imagem
  ligado=true;todas.push(api);
  function dist(){var r=cena.getBoundingClientRect();return Math.abs(r.top+r.height/2-innerHeight/2);}
  function viver(sim){vivo=sim;fig.classList.toggle('viva',sim);}
  function pedir(){
    if(!api.pronto||api.morto||reduzir.matches||alvo<0||v.readyState<1)return;   // nunca antes dos metadados: o alvo fica guardado
    if(emVoo){if(performance.now()-emVoo<VOO)return;emVoo=0;}            // um seek em voo por vez; 600 ms sem 'seeked' = perdido, libera
    if(alvo===pedido&&(vivo||emVoo))return;                               // o quadro-alvo não mudou
    pedido=alvo;tinha=noBuffer(alvo);emVoo=performance.now();v.currentTime=alvo;
  }
  function noBuffer(t){for(var i=0;i<v.buffered.length;i++)if(t>=v.buffered.start(i)&&t<=v.buffered.end(i))return true;return false;}
  function congelar(){api.morto=true;descarregar();arrumar();}            // plano B: pôster, sem mais seeks nesta figura; libera a vaga
  function carregar(){
    if(api.pronto||api.morto||reduzir.matches)return;
    if(todas.filter(function(a){return a.pronto;}).length>=MAXIMO)return;  // trava de segurança: arrumar() já desocupou a vaga antes de chamar
    api.pronto=true;
    v.setAttribute('src',src);v.preload='auto';v.load();
  }
  function descarregar(){
    if(!api.pronto)return;
    api.pronto=false;pedido=-1;emVoo=0;viver(false);v.removeAttribute('src');v.load();
  }
  v.addEventListener('loadedmetadata',function(){
    if(!v.seekable.length||v.seekable.end(0)<dur-0.5){congelar();return;} // servidor sem Range: não dá para buscar; fica o pôster
    pedir();
  });
  v.addEventListener('seeked',function(){
    var nosso=emVoo>0,levou=nosso?performance.now()-emVoo:0;emVoo=0;
    if(v.readyState<2){viver(false);return;}
    if(!vivo)viver(true);                                                  // só agora a imagem some: há um quadro pronto
    if(nosso){if(levou>TETO&&tinha){if(++lentos>=LENTOS){congelar();return;}}else lentos=0;} // aparelho não dá conta, e não foi só espera de rede
    if(alvo>=0&&alvo!==pedido)pedir();                                    // o último pedido vence
  });
  v.addEventListener('error',function(){congelar();});
  v.addEventListener('emptied',function(){if(v.readyState===0)viver(false);}); // WebKit sob pressão de memória
  depoisDoLoad(function(){
    new IntersectionObserver(function(es){api.perto=es[0].isIntersecting;arrumar();},
      {rootMargin:'600px 0px'}).observe(cena);                             // a figure mora no palco sticky: observa-se a cena
  });
});
reduzir.addEventListener('change',arrumar);
})();
