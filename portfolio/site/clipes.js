// Clipes de fundo da história: um vídeo curto e mudo por capítulo, cujo tempo é o progresso da rolagem (historia.js chama
// fig.__clipe.seek(t), o mesmo contrato das maquetes). O clipe nunca anda sozinho: só currentTime, quantizado ao quadro,
// um seek em voo por vez, o último pedido vence. Carga em três portas: depois do 'load' da janela, quando a cena chega a
// 600 px da tela, e nunca com economia de dados, rede 2g, sem H.264 ou com ?clipes=nao (fica o pôster). Movimento
// reduzido, inclusive ligado no meio, descarrega tudo. A imagem só some (.viva) quando há um quadro pronto.
(function(){
'use strict';
var figs=[].slice.call(document.querySelectorAll('figure.clipe'));
if(!figs.length||!('IntersectionObserver' in window))return;
var FPS=24,TETO=250,LENTOS=3,VOO=600,MAXIMO=2; // ms de um seek lento; lentos seguidos até congelar; ms sem 'seeked' = seek perdido; vídeos com dados
var v0=document.createElement('video'),con=navigator.connection||{};
var PODE=!/[?&]clipes=nao\b/.test(location.search)&&v0.canPlayType('video/mp4; codecs="avc1.64001F"')!==''
  &&!con.saveData&&!/^(slow-)?2g$/.test(con.effectiveType||'');
var reduzir=matchMedia('(prefers-reduced-motion: reduce)'),carregados=[],perto={};
function quadro(t){return (Math.round(t*FPS)+0.5)/FPS;}
function depoisDoLoad(fn){if(document.readyState==='complete')fn();else addEventListener('load',fn);}

figs.forEach(function(fig){
  var v=fig.querySelector('video'),cena=fig.closest('.cena')||fig,src=fig.dataset.clipe,dur=parseFloat(fig.dataset.dur)||0;
  var alvo=-1,pedido=-1,emVoo=0,pronto=false,vivo=false,morto=false,lentos=0;
  var api={dur:dur,frozen:false,seek:function(t){api.frozen=true;alvo=quadro(Math.max(0,Math.min(dur,t)));pedir();},descarregar:descarregar};
  fig.__clipe=api;
  if(!PODE||!v||!dur||!src)return; // fica a imagem
  function viver(sim){vivo=sim;fig.classList.toggle('viva',sim);}
  function pedir(){
    if(!pronto||morto||reduzir.matches||alvo<0||v.readyState<1)return;   // nunca antes dos metadados: o alvo fica guardado
    if(emVoo){if(performance.now()-emVoo<VOO)return;emVoo=0;}            // um seek em voo por vez; 600 ms sem 'seeked' = perdido, libera
    if(alvo===pedido&&(vivo||emVoo))return;                               // o quadro-alvo não mudou
    pedido=alvo;emVoo=performance.now();v.currentTime=alvo;
  }
  function noBuffer(t){for(var i=0;i<v.buffered.length;i++)if(t>=v.buffered.start(i)&&t<=v.buffered.end(i))return true;return false;}
  function congelar(){morto=true;descarregar();}                          // plano B: pôster, sem mais seeks nesta figura
  function carregar(){
    if(pronto||morto||reduzir.matches)return;
    while(carregados.length>=MAXIMO)carregados.shift().descarregar();      // no máximo 2 vídeos com dados: sai o mais antigo
    carregados.push(api);pronto=true;
    v.setAttribute('src',src);v.preload='auto';v.load();
  }
  function descarregar(){
    var i=carregados.indexOf(api);if(i>=0)carregados.splice(i,1);
    if(!pronto)return;
    pronto=false;pedido=-1;emVoo=0;viver(false);v.removeAttribute('src');v.load();
  }
  v.addEventListener('loadedmetadata',function(){
    if(!v.seekable.length||v.seekable.end(0)<dur-0.5){congelar();return;} // servidor sem Range: não dá para buscar; fica o pôster
    pedir();
  });
  v.addEventListener('seeked',function(){
    var nosso=emVoo>0,levou=nosso?performance.now()-emVoo:0;emVoo=0;
    if(v.readyState===0){viver(false);return;}
    if(!vivo)viver(true);                                                  // só agora a imagem some: há um quadro pronto
    if(nosso){if(levou>TETO&&noBuffer(pedido)){if(++lentos>=LENTOS){congelar();return;}}else lentos=0;} // aparelho não dá conta
    if(alvo>=0&&alvo!==pedido)pedir();                                    // o último pedido vence
  });
  v.addEventListener('error',function(){congelar();});
  v.addEventListener('emptied',function(){if(v.readyState===0)viver(false);}); // WebKit sob pressão de memória
  depoisDoLoad(function(){
    new IntersectionObserver(function(es){perto[src]=es[0].isIntersecting;if(es[0].isIntersecting)carregar();else descarregar();},
      {rootMargin:'600px 0px'}).observe(cena);                             // a figure mora no palco sticky: observa-se a cena
  });
  reduzir.addEventListener('change',function(){if(reduzir.matches)descarregar();else if(perto[src])carregar();});
});
})();
