// Clipes de fundo da história: um vídeo curto e mudo por capítulo, cujo tempo é o progresso da rolagem (historia.js chama
// fig.__clipe.seek(t), o mesmo contrato das maquetes). O clipe nunca anda sozinho: só currentTime, quantizado ao quadro,
// um seek em voo por vez, o último pedido vence. Carga em três portas: depois do 'load' da janela, quando a cena chega a
// 600 px da tela (2 alturas de tela no site v2), e nunca com economia de dados, rede 2g, sem H.264 ou com ?clipes=nao (fica o pôster). Movimento
// reduzido, inclusive ligado no meio, descarrega tudo. A imagem só some (.viva) quando há um quadro pronto. Carregados
// ficam no máximo MAXIMO (2; o site v2 pede 3) clipes, os mais perto do meio da tela dentro da faixa;
// no site v2 um clipe que saiu da faixa continua com os dados até um mais perto precisar da vaga, para a volta (rolar
// para cima) não baixar tudo de novo. arrumar() reavalia isso a cada seek, entrada/saída da faixa ou troca de movimento reduzido — nunca
// descarte por ordem de chegada.
(function(){
'use strict';
var figs=[].slice.call(document.querySelectorAll('figure.clipe'));
if(!figs.length||!('IntersectionObserver' in window))return;
var FPS=24,TETO=250,LENTOS=3,VOO=600,MAXIMO=2,FOLGA=100,ESPERA_RANGE=1500; // ms de um seek lento; lentos seguidos até congelar; ms sem 'seeked' = seek perdido; vídeos com dados; px de vantagem de quem já carregou; ms de espera por um seekable completo antes de congelar
var v0=document.createElement('video'),con=navigator.connection||{};
var PODE=!/[?&]clipes=nao\b/.test(location.search)&&v0.canPlayType('video/mp4; codecs="avc1.64001F"')!==''
  &&!con.saveData&&!/^(slow-)?2g$/.test(con.effectiveType||'');
var reduzir=matchMedia('(prefers-reduced-motion: reduce)'),todas=[];
// <html data-clipes-max="N"> (opcional): a página aceita N clipes carregados (o site v2 usa 3: a volta não recarrega)
// e quem saiu da faixa guarda os dados até um mais perto precisar da vaga (GUARDA); sem o atributo, sai ao deixar a faixa
var GUARDA='clipesMax' in document.documentElement.dataset;
if(+document.documentElement.dataset.clipesMax>MAXIMO)MAXIMO=+document.documentElement.dataset.clipesMax;
// data-clipe-hd (opcional): a versão em alta, em qualquer tela; sem ele fica data-clipe
function depoisDoLoad(fn){if(document.readyState==='complete')fn();else addEventListener('load',fn);}
function chave(a){return a.dist()-(a.pronto?FOLGA:0);}
function arrumar(){
  if(reduzir.matches){todas.forEach(function(a){a.descarregar();});return;}
  var quer=todas.filter(function(a){return (a.perto||GUARDA&&a.pronto)&&!a.morto;}).sort(function(a,b){return chave(a)-chave(b);}).slice(0,MAXIMO);
  todas.forEach(function(a){if(a.pronto&&quer.indexOf(a)<0)a.descarregar();});   // sai quem não está mais entre os mais perto
  quer.forEach(function(a){if(a.perto)a.carregar();});                           // entra quem está na faixa, se ainda não tiver dados
}

figs.forEach(function(fig){
  var v=fig.querySelector('video'),cena=fig.closest('.cena')||fig,src=fig.dataset.clipeHd||fig.dataset.clipe,dur=parseFloat(fig.dataset.dur)||0;
  var alvo=-1,pedido=-1,emVoo=0,vivo=false,lentos=0,tinha=false,ligado=false,esperados=0,desde=0; // esperados: 'emptied' que os nossos load() ainda vão disparar; desde: hora dos metadados da carga atual (0: nenhuma)
  var ultimo=Math.round(dur*FPS)-1;                                         // índice do último quadro: o fim da cena pede este quadro, nunca além
  function quadro(t){return (Math.min(Math.round(t*FPS),ultimo)+0.5)/FPS;}
  var api={dur:dur,frozen:false,pronto:false,morto:false,perto:false,dist:dist,carregar:carregar,
    seek:function(t){api.frozen=true;alvo=quadro(Math.max(0,Math.min(dur,t)));if(ligado)arrumar();pedir();},
    descarregar:descarregar};
  fig.__clipe=api;
  if(!PODE||!v||!dur||!src)return; // fica a imagem
  ligado=true;todas.push(api);
  function dist(){var r=cena.getBoundingClientRect(),meio=innerHeight/2;                       // v2 (cenas de 9 telas): 0 com o meio da tela
    return GUARDA?Math.max(0,r.top-meio,meio-r.bottom):Math.abs(r.top+r.height/2-meio);}         // dentro da cena; na história, do centro dela
  function viver(sim){vivo=sim;fig.classList.toggle('viva',sim);}
  function pedir(){
    if(!api.pronto||api.morto||reduzir.matches||alvo<0||v.readyState<1||!temRange())return;   // nunca antes dos metadados nem sem seekable completo: o alvo fica guardado
    if(emVoo){if(performance.now()-emVoo<VOO)return;emVoo=0;}            // um seek em voo por vez; 600 ms sem 'seeked' = perdido, libera
    if(alvo===pedido&&(vivo||emVoo))return;                               // o quadro-alvo não mudou
    pedido=alvo;tinha=noBuffer(alvo);emVoo=performance.now();v.currentTime=alvo;
  }
  function noBuffer(t){for(var i=0;i<v.buffered.length;i++)if(t>=v.buffered.start(i)&&t<=v.buffered.end(i))return true;return false;}
  function congelar(){api.morto=true;descarregar();arrumar();}            // plano B: pôster, sem mais seeks nesta figura; libera a vaga
  function recarregar(){desde=0;esperados=v.networkState!==0?1:0;v.load();}     // load() descarta o 'emptied' pendente do load() anterior e enfileira no máximo um (só se networkState ≠ EMPTY)
  function carregar(){
    if(api.pronto||api.morto||reduzir.matches)return;
    if(todas.filter(function(a){return a.pronto;}).length>=MAXIMO)return;  // trava de segurança: arrumar() já desocupou a vaga antes de chamar
    api.pronto=true;
    v.setAttribute('src',src);v.preload='auto';recarregar();
  }
  function descarregar(){
    if(!api.pronto)return;
    api.pronto=false;pedido=-1;emVoo=0;viver(false);v.removeAttribute('src');recarregar();
  }
  function temRange(){return v.seekable.length>0&&v.seekable.end(0)>=dur-0.5;}
  function conferirRange(ini){                                              // sem Range o Chrome diz seekable [0,0] (um seek cai no quadro 0);
    if(!api.pronto||ini!==desde)return;                                     // o Safari pode preencher seekable só depois: espera ESPERA_RANGE antes de desistir;
    if(temRange()){pedir();return;}                                         // a cadeia morre se a figura descarregou ou recarregou (desde mudou)
    if(performance.now()-ini>ESPERA_RANGE){congelar();return;}
    setTimeout(function(){conferirRange(ini);},250);
  }
  v.addEventListener('loadedmetadata',function(){esperados=0;conferirRange(desde=performance.now());});
  v.addEventListener('loadeddata',function(){                               // o 1º 'seeked' pode chegar sem quadro (readyState<2): agora há
    if(vivo||alvo<0)return;
    if(!emVoo&&pedido===alvo&&pedido===v.currentTime)viver(true);else pedir(); // já está no quadro pedido: só mostra; senão pedir() busca de novo
  });
  v.addEventListener('progress',function(){if(!vivo&&alvo>=0&&v.readyState>=2)pedir();}); // Safari: 'seeked' sem quadro e os dados chegam depois
  v.addEventListener('canplay',function(){if(!vivo&&alvo>=0&&v.readyState>=2)pedir();}); // Safari: 'seeked' sem quadro num clipe já todo em buffer não dispara 'progress'
  v.addEventListener('seeked',function(){
    var nosso=emVoo>0,levou=nosso?performance.now()-emVoo:0;emVoo=0;
    if(v.readyState<2){viver(false);return;}
    if(!vivo)viver(true);                                                  // só agora a imagem some: há um quadro pronto
    if(nosso){if(levou>TETO&&tinha){if(++lentos>=LENTOS){congelar();return;}}else lentos=0;} // aparelho não dá conta, e não foi só espera de rede
    if(alvo>=0&&alvo!==pedido)pedir();                                    // o último pedido vence
  });
  v.addEventListener('error',function(){congelar();});
  v.addEventListener('emptied',function(){                                  // WebKit sob pressão de memória esvazia o vídeo sozinho
    if(esperados>0){esperados--;return;}                                    // este veio do nosso load() (carregar/descarregar), não é despejo
    if(v.readyState!==0||!api.pronto)return;
    viver(false);api.pronto=false;pedido=-1;emVoo=0;v.removeAttribute('src');arrumar(); // foi o navegador: libera a vaga (sem src, nem o WebKit recarrega sozinho) e recarrega quando voltar a estar entre os mais perto
  });
  depoisDoLoad(function(){
    new IntersectionObserver(function(es){api.perto=es[es.length-1].isIntersecting;arrumar();}, // um observer por figure, um alvo só: vale a entrada mais nova do lote
      {rootMargin:GUARDA?'200% 0px':'600px 0px'}).observe(cena);           // a figure mora no palco sticky: observa-se a cena; no v2 a faixa é de 2 telas
  });
});
if(reduzir.addEventListener)reduzir.addEventListener('change',arrumar);else reduzir.addListener(arrumar); // Safari ≤ 13: só addListener(fn), sem o tipo
})();
