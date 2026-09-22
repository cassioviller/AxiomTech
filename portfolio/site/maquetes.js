// Maquetes 3D embutidas (padrão visual da cena5 aprovada: low-poly, sol quente, sombras, laranja como único acento).
// Regras: three.js só carrega quando a maquete chega perto da tela; cada cena é função pura do tempo (update(t));
// só anima enquanto visível; se o aparelho não sustenta ~24 fps, volta para a imagem estática.
(function(){
'use strict';
var figs=[].slice.call(document.querySelectorAll('figure.maquete'));
if(!figs.length||!('IntersectionObserver' in window))return;
if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
try{var c=document.createElement('canvas');if(!(c.getContext('webgl2')||c.getContext('webgl')))return;}catch(e){return;}

// ?maquete=forcar ignora a guarda de fps; &t=12 congela no segundo 12 (para conferir quadros em teste)
var QS=location.search,FORCAR=/maquete=forcar/.test(QS),TFIXO=(QS.match(/[?&]t=([\d.]+)/)||[])[1];
var THREE=null,loading=null;
function lib(){return loading||(loading=import('./vendor/three.module.js').then(function(m){THREE=m;return m;}));}

function ease(x){x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);}
function seg(t,a,b){return ease((t-a)/(b-a));}
function lerp(a,b,t){return a+(b-a)*t;}
function pad(n){return(n<10?'0':'')+n;}

// ---------- base comum ----------
function stage(fig,sky,fogNear,fogFar){
  var canvas=fig.querySelector('canvas');
  var R=new THREE.WebGLRenderer({canvas:canvas,antialias:true,powerPreference:'high-performance'});
  R.setPixelRatio(Math.min(devicePixelRatio||1,1.75));
  R.shadowMap.enabled=true;R.shadowMap.type=THREE.PCFSoftShadowMap;
  R.toneMapping=THREE.ACESFilmicToneMapping;R.toneMappingExposure=.95;
  var S=new THREE.Scene();S.background=new THREE.Color(sky);S.fog=new THREE.Fog(sky,fogNear,fogFar);
  var cam=new THREE.PerspectiveCamera(34,16/9,.1,300);
  S.add(new THREE.HemisphereLight(0xE8F0FA,0x6B5A3E,1.5));
  var sun=new THREE.DirectionalLight(0xFFE9C9,3.4);sun.position.set(-14,22,10);sun.castShadow=true;
  sun.shadow.mapSize.set(2048,2048);var sc=sun.shadow.camera;sc.left=-24;sc.right=24;sc.top=24;sc.bottom=-24;sc.near=1;sc.far=80;sun.shadow.bias=-0.0006;
  S.add(sun);
  function mat(c,o){return new THREE.MeshStandardMaterial(Object.assign({color:c,roughness:.85,metalness:0,flatShading:true},o||{}));}
  function box(w,h,d,m,x,y,z,p){var g=new THREE.Mesh(new THREE.BoxGeometry(w,h,d),m);g.position.set(x,y,z);g.castShadow=true;g.receiveShadow=true;(p||S).add(g);return g;}
  function cyl(r,h,m,x,y,z,p,rz){var g=new THREE.Mesh(new THREE.CylinderGeometry(r,r,h,14),m);g.position.set(x,y,z);if(rz)g.rotation.z=rz;g.castShadow=true;g.receiveShadow=true;(p||S).add(g);return g;}
  function camKeys(K,t,wide){ // keyframes [t,[pos],[alvo]]; "wide" afasta a câmera em telas estreitas
    var i=0;while(i<K.length-2&&t>K[i+1][0])i++;var a=K[i],b=K[i+1],f=ease((t-a[0])/(b[0]-a[0]));
    var tx=lerp(a[2][0],b[2][0],f),ty=lerp(a[2][1],b[2][1],f),tz=lerp(a[2][2],b[2][2],f);
    var px=lerp(a[1][0],b[1][0],f),py=lerp(a[1][1],b[1][1],f),pz=lerp(a[1][2],b[1][2],f);
    cam.position.set(tx+(px-tx)*wide,ty+(py-ty)*wide,tz+(pz-tz)*wide);cam.lookAt(tx,ty,tz);}
  return {R:R,S:S,cam:cam,sun:sun,mat:mat,box:box,cyl:cyl,camKeys:camKeys};
}

// ---------- CENA: 36 minutos ----------
// As paredes saem da própria planta do cliente: os pixels vermelhos da imagem viram blocos que sobem.
function cena36(fig){
  var st=stage(fig,0xCFDDEA,40,120),S=st.S,mat=st.mat,box=st.box;
  var DUR=24,T0=2.5,T1=17.5; // relógio anda entre T0 e T1 (11:35 → 12:11)
  var PW=44,PH=PW*440/1400; // planta 1400×440 px
  var ORANGE=0xF07A3E;
  box(PW+10,1.2,PH+12,mat(0x6E4F35),0,-.62,0);
  box(PW+10,.06,PH+12,mat(0xB9B4A8),0,.0,0);
  var tex=new THREE.TextureLoader().load('img/upa-plan-grey.webp');tex.colorSpace=THREE.SRGBColorSpace;tex.anisotropy=4;
  var plan=new THREE.Mesh(new THREE.PlaneGeometry(PW,PH),new THREE.MeshStandardMaterial({map:tex,roughness:1}));
  plan.rotation.x=-Math.PI/2;plan.position.y=.05;plan.receiveShadow=true;S.add(plan);
  // varredura laranja (a linha de cota)
  var sweep=box(.12,.1,PH+1.2,new THREE.MeshBasicMaterial({color:ORANGE}),0,.12,0);sweep.castShadow=false;
  var sweepTop=box(.06,3.4,.06,new THREE.MeshBasicMaterial({color:ORANGE}),0,1.7,-PH/2-.6);sweepTop.castShadow=false;
  // mesa + proposta que empilha
  var mesa=new THREE.Group();mesa.position.set(PW/2-4,0,PH/2+3.4);S.add(mesa);
  box(6,.2,3,mat(0x8B5E3C),0,1.0,0,mesa);[[-2.7,-1.2],[2.7,-1.2],[-2.7,1.2],[2.7,1.2]].forEach(function(p){box(.2,1,.2,mat(0x7A5738),p[0],.5,p[1],mesa);});
  var zip=box(1.1,.7,.9,mat(ORANGE),-1.9,1.45,0,mesa);
  var pages=[];for(var i=0;i<7;i++){var pg=box(1.5,.035,2.05,mat(0xFBFAF6,{roughness:.6}),1.2,1.12+i*.04,0,mesa);pg.rotation.y=(i%2?.05:-.04);pages.push(pg);}
  // paredes: lidas da imagem
  var walls=null,wx=[],H=2.6,CELL=5,dummy=new THREE.Object3D();
  var img=new Image();img.onload=function(){
    var w=1400,h=440,cv=document.createElement('canvas');cv.width=w;cv.height=h;var cx=cv.getContext('2d',{willReadFrequently:true});cx.drawImage(img,0,0,w,h);
    var d=cx.getImageData(0,0,w,h).data,cells=[];
    for(var gy=0;gy<h;gy+=CELL)for(var gx=0;gx<w;gx+=CELL){var n=0;
      for(var y=gy;y<gy+CELL&&y<h;y++)for(var x=gx;x<gx+CELL&&x<w;x++){var k=(y*w+x)*4;if(d[k]>150&&d[k+1]<90&&d[k+2]<90)n++;}
      if(n>=CELL*CELL*.3)cells.push([gx,gy]);}
    var s=PW/w;walls=new THREE.InstancedMesh(new THREE.BoxGeometry(CELL*s,1,CELL*s),mat(0xF1ECE2,{roughness:.9}),cells.length);
    walls.castShadow=true;walls.receiveShadow=true;
    cells.forEach(function(c,i){wx.push([(c[0]+CELL/2)*s-PW/2,(c[1]+CELL/2)*s-PH/2]);});
    S.add(walls);api.dirty=true;
  };img.src='img/upa-plan.webp';
  var CAM=[[0,[0,46,4],[0,0,.5]],[T0,[0,44,6],[0,0,.5]],[8,[-16,18,26],[-7,1,0]],[14,[5,15,27],[7,1,0]],[T1,[16,14,27],[13,1,2]],[20.5,[25,11,25],[16.5,1,PH/2+2.2]],[DUR,[4,34,34],[2,0,2]]];
  var LEG=[[0,'Entra o pacote: 3 pranchas de arquitetura, 3 de estrutura e a proposta de material.'],[T0,'As paredes a construir são medidas direto no desenho do cliente.'],[8,'Cada número sai com origem e grau de confiança. O que falta, se declara.'],[14,'Rodam os motores da mesma planilha que o diretor usa.'],[T1,'12:11 — proposta assinável. 36 minutos, fechando ao centavo.']];
  var api={dur:DUR,dirty:true,
    update:function(t,wide){
      var p=seg2(t,T0,T1),sx=lerp(-PW/2-.5,PW/2+.5,p);
      sweep.position.x=sx;sweepTop.position.x=sx;sweep.visible=sweepTop.visible=t>T0-.4&&t<T1+.3;
      if(walls){for(var i=0;i<wx.length;i++){var r=ease((sx-wx[i][0])/3.2),hh=Math.max(.001,r*H);
        dummy.position.set(wx[i][0],.06+hh/2,wx[i][1]);dummy.scale.set(1,hh,1);dummy.updateMatrix();walls.setMatrixAt(i,dummy.matrix);}
        walls.instanceMatrix.needsUpdate=true;}
      zip.position.y=lerp(9,1.45,seg(t,.3,1.6));zip.visible=t>.3;
      pages.forEach(function(pg,i){var a=seg(t,T1-1.2+i*.32,T1-.5+i*.32);pg.visible=a>0;pg.position.y=lerp(5,1.12+i*.04,a);pg.position.z=lerp(-1.6,0,a);});
      st.camKeys(CAM,t,wide);
      var mins=Math.round(p*36),hh2=11+Math.floor((35+mins)/60),mm=(35+mins)%60;
      api.num=pad(hh2)+':'+pad(mm);
      var li=0;for(var j=0;j<LEG.length;j++)if(t>=LEG[j][0])li=j;api.leg=LEG[li][1];
    }};
  function seg2(t,a,b){return Math.max(0,Math.min(1,(t-a)/(b-a)));} // relógio linear: minuto a minuto
  return Object.assign(api,st);
}

// ---------- CENA: a casa viaja (port direto da cena5 aprovada, 26 s) ----------
function cenaCasa(fig){
  var st=stage(fig,0xBFD3E6,34,80),S=st.S,mat=st.mat,box=st.box,cyl=st.cyl;
  var M={grass:mat(0x8FB36A),earth:mat(0x6E4F35),road:mat(0x4A4E52,{roughness:1}),wall:mat(0xF1ECE2,{roughness:.9}),win:mat(0x8FB6CF,{roughness:.2,metalness:.2}),
    wood:mat(0x8B5E3C),roof:mat(0x3A3E44,{roughness:1}),steel:mat(0x9AA6B2,{metalness:.5,roughness:.45}),truck:mat(0xE5E7EA),cab:mat(0xD9542B),tire:mat(0x1E2124,{roughness:1}),
    crane:mat(0xF2B233),craneD:mat(0xC7871B),leaf:mat(0x6E9A4E),leaf2:mat(0x5C8642),trunk:mat(0x7A5738),conc:mat(0xBFBBB2),cable:new THREE.LineBasicMaterial({color:0x222222})};
  box(30,1.2,24,M.earth,0,-.6,0);box(30,.06,24,M.grass,0,.03,0);
  box(4.2,.05,60,M.road,9,.04,0);for(var i=-28;i<30;i+=3)box(.12,.06,1.4,mat(0xEDEDEA),9,.07,i);
  function tree(x,z,s){var g=new THREE.Group();cyl(.16*s,1.2*s,M.trunk,0,.6*s,0,g);var c1=new THREE.Mesh(new THREE.ConeGeometry(1.1*s,2.2*s,7),M.leaf);c1.position.y=1.9*s;c1.castShadow=true;g.add(c1);var c2=new THREE.Mesh(new THREE.ConeGeometry(.8*s,1.6*s,7),M.leaf2);c2.position.y=3.0*s;c2.castShadow=true;g.add(c2);g.position.set(x,0,z);S.add(g);}
  [[-11,-8,1.3],[-12,4,1.1],[-8,9,1.0],[-4,-10,1.2],[4,-10.5,.9],[-13,-2,.9],[3,10,1.1],[-6,10.5,.8]].forEach(function(t){tree(t[0],t[1],t[2]);});
  var PIL=.55;for(var r=0;r<3;r++){[-2.6,0,2.6].forEach(function(x){box(.24,PIL,.24,M.conc,x,PIL/2,-2.5+r*2.5);});}
  function caixa(front){var g=new THREE.Group(),W=6,H=2.85,D=3;
    box(W,.22,D,M.steel,0,.11,0,g);box(W-.03,.05,D-.03,M.wood,0,.245,0,g);box(W,H,D,M.wall,0,.27+H/2,0,g);
    if(front){box(1.3,2.2,.08,M.wood,-1.55,.27+1.1,D/2+.05,g);box(1.3,2.2,.08,M.wood,1.55,.27+1.1,D/2+.05,g);box(2.6,.6,.08,M.wall,0,.27+2.5,D/2+.05,g);
      box(.05,2.0,.05,M.steel,-.9,.27+1.1,D/2+.05,g);box(.05,2.0,.05,M.steel,.9,.27+1.1,D/2+.05,g);box(2.55,2.05,.02,mat(0x2a2320),0,.27+1.05,D/2+.02,g);}
    else{box(1.2,1.0,.08,M.win,-1.6,.27+1.5,-D/2-.05,g);}
    box(.08,1.0,1.1,M.win,-W/2-.05,.27+1.4,0,g);box(.08,1.0,1.1,M.win,W/2+.05,.27+1.4,0,g);return g;}
  var c1=caixa(true),c2=caixa(false);S.add(c1);S.add(c2);
  var XQ=1.68,HQ=(3-XQ)*Math.tan(Math.PI/3),HH=HQ+XQ*Math.tan(Math.PI/6);
  function agua(x0,y0,x1,y1,g){var dx=x1-x0,dy=y1-y0,L=Math.hypot(dx,dy);var m=new THREE.Mesh(new THREE.BoxGeometry(6.6,.16,L),M.roof);m.castShadow=true;m.receiveShadow=true;m.position.set(0,(y0+y1)/2,(x0+x1)/2);m.rotation.x=-Math.atan2(dy,dx);g.add(m);return m;}
  var roof=new THREE.Group();[-1,1].forEach(function(s){agua(s*3.3,0,s*XQ,HQ,roof);agua(s*XQ,HQ,0,HH,roof);});
  var shp=new THREE.Shape();shp.moveTo(-3,0);shp.lineTo(-XQ,HQ);shp.lineTo(0,HH);shp.lineTo(XQ,HQ);shp.lineTo(3,0);shp.closePath();
  [-1,1].forEach(function(s){var f=new THREE.Mesh(new THREE.ExtrudeGeometry(shp,{depth:.1,bevelEnabled:false}),M.wall);f.rotation.y=Math.PI/2;f.position.set(s*2.95,0,0);f.castShadow=true;roof.add(f);});
  S.add(roof);
  var truck=new THREE.Group();S.add(truck);
  box(7.4,.5,2.6,M.truck,-.6,1.05,0,truck);box(2.0,2.2,2.5,M.cab,3.9,1.9,0,truck);box(1.9,.9,2.3,M.win,3.95,2.7,0,truck);
  [[-3.2,-1.2],[-3.2,1.2],[-1.6,-1.2],[-1.6,1.2],[3.5,-1.2],[3.5,1.2]].forEach(function(w){cyl(.55,.5,M.tire,w[0],.55,w[1],truck,Math.PI/2);});
  truck.rotation.y=-Math.PI/2; // cabine para +z: o caminhão entra de frente e sai de frente
  var crane=new THREE.Group();crane.position.set(5.5,0,-6.5);S.add(crane);
  box(4.6,.9,2.4,M.crane,0,.95,0,crane);[[-1.5,-1.3],[-1.5,1.3],[1.5,-1.3],[1.5,1.3]].forEach(function(w){cyl(.6,.6,M.tire,w[0],.6,w[1],crane,Math.PI/2);});
  [[-2.2,-1.5],[-2.2,1.5],[2.2,-1.5],[2.2,1.5]].forEach(function(o){box(.3,.3,1.3,M.craneD,o[0],.55,o[1]*.8,crane);cyl(.12,.7,M.steel,o[0],.35,o[1]*1.2,crane);});
  var turret=new THREE.Group();turret.position.set(-.6,1.4,0);crane.add(turret);
  box(2.4,.9,1.9,M.craneD,0,.45,0,turret);box(1.2,1.1,1.4,M.crane,-1.2,.55,.9,turret);
  var boomPivot=new THREE.Group();boomPivot.position.set(.6,.8,0);turret.add(boomPivot);
  var L=11.5;box(L,.5,.5,M.crane,L/2,0,0,boomPivot);box(L*.5,.36,.36,M.craneD,L*.9,0,0,boomPivot);
  var tip=new THREE.Object3D();tip.position.set(L,0,0);boomPivot.add(tip);
  var cableGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]);var cable=new THREE.Line(cableGeo,M.cable);cable.frustumCulled=false;S.add(cable);
  var hook=box(.5,.35,.5,M.craneD,0,0,0);
  var DUR=26,TG={truck:new THREE.Vector3(9,0,0),site1:new THREE.Vector3(0,0,1.5),site2:new THREE.Vector3(0,0,-1.5),mid:new THREE.Vector3(0,0,0)};
  var cur=new THREE.Vector3(9,0,0),wp=new THREE.Vector3(),tipW=new THREE.Vector3(),from=new THREE.Vector3(9,1.3,-.6);
  function aimBoom(target){S.updateMatrixWorld();boomPivot.getWorldPosition(wp);var dx=target.x-wp.x,dz=target.z-wp.z,d=Math.hypot(dx,dz);turret.rotation.y=Math.atan2(-dz,dx);boomPivot.rotation.z=Math.acos(Math.min(.98,d/L));}
  function liftPath(t,t0,t1,bx,to,restY){var a=seg(t,t0,t0+(t1-t0)*.3),b=seg(t,t0+(t1-t0)*.3,t0+(t1-t0)*.7),c=seg(t,t0+(t1-t0)*.7,t1);
    var x=lerp(from.x,to.x,b),z=lerp(from.z,to.z,b),y=lerp(lerp(from.y,7.2,a),restY,c);if(c<=0)y=lerp(from.y,7.2,a);bx.position.set(x,y,z);bx.rotation.y=lerp(Math.PI/2,0,b);cur.set(x,0,z);return true;}
  var CAM=[[0,[20,10,22],[1,2,0]],[6,[16,7,14],[4,2,0]],[9.5,[14,9.5,13],[3,4.5,0]],[12,[10.5,6,10],[1,3,.5]],[16,[13,8,-11],[1,2.5,0]],[19,[15,9.5,-10],[1,4.5,0]],[21.5,[11,6.5,9.5],[0,3.5,0]],[26,[14,6.5,13],[0,3,0]]];
  var SUBS=[[0,'A conta veio antes do desenho: casas que saem prontas da fábrica.',''],[3,'Caixa 1 chega. Três metros de largura — sem escolta.',''],[8.5,'Guindaste da classe certa: 3,8 t por caixa.','3,8 t'],[13.5,'A segunda viagem. A face de junção viaja fechada.','4,12 m'],[17.5,'Vão livre de seis metros: a viga, não o pilar.','6,00 m'],[20.5,'O telhado chega em painéis. Terceira viagem.','3 viagens'],[23.5,'Uma casa que sai pronta da fábrica.','59,5 m²']];
  var api={dur:DUR,update:function(t,wide){
    var tz;if(t<6)tz=lerp(-30,0,seg(t,1.5,6));else if(t<11.8)tz=0;else if(t<13.2)tz=lerp(0,30,seg(t,11.8,13.2));else if(t<15)tz=lerp(-30,0,seg(t,13.2,15));else if(t<20)tz=0;else tz=lerp(0,30,seg(t,20,21.5));
    truck.position.set(9,0,tz);
    var a1=false,a2=false;
    if(t<7.2){c1.position.set(9,1.3,tz-.6);c1.rotation.y=Math.PI/2;}else if(t<12)a1=liftPath(t,7.2,11.6,c1,TG.site1,PIL);else{c1.position.set(0,PIL,1.5);c1.rotation.y=0;}
    c2.visible=t>=13.2;
    if(c2.visible){if(t<16.2){c2.position.set(9,1.3,tz-.6);c2.rotation.y=Math.PI/2;}else if(t<20.6)a2=liftPath(t,16.2,20.4,c2,TG.site2,PIL);else{c2.position.set(0,PIL,-1.5);c2.rotation.y=0;}}
    var rt=seg(t,20.6,23.2);roof.visible=t>20.2;roof.position.set(0,PIL+.27+2.85+(1-rt)*7,0);
    var att=a1||a2,roofing=t>20.4&&t<23.4;
    aimBoom(roofing?TG.mid:att?cur:(t<7.2?TG.truck:(t<13.2?TG.site1:TG.truck)));
    S.updateMatrixWorld();tip.getWorldPosition(tipW);
    var hookY=att?((a1?c1:c2).position.y+3.4):(roofing?roof.position.y+HH+.3:tipW.y-2.2);
    hook.position.set(tipW.x,hookY,tipW.z);
    cableGeo.setFromPoints([tipW,new THREE.Vector3(tipW.x,hookY+.18,tipW.z)]);
    st.camKeys(CAM,t,wide);
    var si=0;for(var i=0;i<SUBS.length;i++)if(t>=SUBS[i][0])si=i;api.leg=SUBS[si][1];api.num=SUBS[si][2];
  }};
  return Object.assign(api,st);
}

var CENAS={'36min':cena36,'casa-viaja':cenaCasa};

// ---------- ciclo de vida de cada figura ----------
function montar(fig){
  var cena=CENAS[fig.dataset.cena];if(!cena)return;
  var sc;try{sc=cena(fig);}catch(e){console.warn('maquete:',e);return;}
  var numEl=fig.querySelector('[data-relogio]'),legEl=fig.querySelector('[data-legenda]');
  var visible=false,raf=0,t=0,last=0,frames=0,slow=0,dead=false,lastNum,lastLeg;
  function size(){var w=fig.clientWidth,h=fig.clientHeight;sc.R.setSize(w,h,false);sc.cam.aspect=w/h;sc.cam.updateProjectionMatrix();}
  function frame(now){
    if(!visible||dead)return;
    var dt=Math.min(.1,(now-last)/1000);last=now;
    if(!api.frozen)t=(t+dt)%sc.dur;
    sc.update(t,fig.clientWidth<560?1.28:1);
    sc.R.render(sc.S,sc.cam);
    if(sc.num!==lastNum){lastNum=sc.num;numEl.textContent=sc.num||'';}
    if(sc.leg!==lastLeg){lastLeg=sc.leg;legEl.textContent=sc.leg||'';}
    // guarda de desempenho: mede depois do aquecimento; abaixo de ~24 fps, volta para a imagem
    frames++;if(!FORCAR&&frames>20&&frames<=110){if(dt>1/24)slow++;if(frames===110&&slow>55){matar();return;}}
    if(frames===3)fig.classList.add('viva');
    raf=requestAnimationFrame(frame);
  }
  function matar(){dead=true;fig.classList.remove('viva');cancelAnimationFrame(raf);sc.R.dispose();}
  var api={frozen:false,seek:function(x){t=x;api.frozen=true;}}; // seek(): usado nos testes para conferir um quadro exato
  fig.__maquete=api;if(TFIXO)api.seek(parseFloat(TFIXO));
  new IntersectionObserver(function(es){visible=es[0].isIntersecting;if(visible&&!dead){last=performance.now();cancelAnimationFrame(raf);raf=requestAnimationFrame(frame);}},{threshold:.15}).observe(fig);
  addEventListener('resize',size);size();
  sc.R.domElement.addEventListener('webglcontextlost',function(e){e.preventDefault();matar();});
}

var perto=new IntersectionObserver(function(es){es.forEach(function(e){
  if(!e.isIntersecting)return;perto.unobserve(e.target);
  lib().then(function(){montar(e.target);}).catch(function(err){console.warn('three.js não carregou; fica a imagem.',err);});
});},{rootMargin:'600px 0px'});
figs.forEach(function(f){perto.observe(f);});
})();
