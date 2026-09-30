// Kit das cenas do site v2: palco (render 2× para antisserrilhado, céu pintado que também ilumina a cena, sol com
// sombras suaves, oclusão GTAO), materiais PBR procedurais (cor, normais, rugosidade), câmera por chaves e o carregador
// dos documentos reais.
// Contrato de cada cena: publicar(palco, cam, run) define window.renderCena(t) (t = 0..10, pura em t) e window.PRONTO.
// Sem tone mapping (NoToneMapping): a tela com o documento real tem de sair no vídeo com as cores da imagem da página.
import * as THREE from 'three';
import {EffectComposer} from './vendor/addons/postprocessing/EffectComposer.js';
import {RenderPass} from './vendor/addons/postprocessing/RenderPass.js';
import {GTAOPass} from './vendor/addons/postprocessing/GTAOPass.js';
import {OutputPass} from './vendor/addons/postprocessing/OutputPass.js';
export {THREE};

export const LARGURA = 1920, ALTURA = 1080;
export const RETANGULO = {x: .2, y: 1 / 6, w: .6, h: 2 / 3}; // onde o documento termina no último quadro (frações do quadro); a página usa os mesmos números
const LARANJA = 0xE0622A;

export const limitar = x => Math.max(0, Math.min(1, x));
export const suave = x => { x = limitar(x); return x * x * (3 - 2 * x); };
export const rampa = (t, a, b) => suave((t - a) / (b - a));
export const lerp = (a, b, f) => a + (b - a) * f;

// o céu: uma equirretangular pintada (gradiente do zênite ao horizonte, o sol com halo, nuvens por ruído fbm, o chão
// abaixo do horizonte); é o fundo da cena e, filtrada pelo PMREM, a luz do ambiente (image-based lighting): o azul do céu
// entra nas sombras e o branco das nuvens nos reflexos. `sol` é a direção do sol (a mesma da luz direcional).
function pintarCeu(sol, {zenite = 0x3D6EB4, horizonte = 0xC9D8E6, chao = 0xA79F93, nuvens = .5} = {}) {
  const W = 2048, H = 1024, c = document.createElement('canvas');
  c.width = W; c.height = H;
  const g = c.getContext('2d'), img = g.createImageData(W, H), d = img.data;
  const rgb = h => [(h >> 16) & 255, (h >> 8) & 255, h & 255];
  const Z = rgb(zenite), Hz = rgb(horizonte), C = rgb(chao);
  const sd = sol.clone().normalize();
  const G = 8, grade = [];
  let sem = 12345;
  const rnd = () => (sem = (sem * 16807) % 2147483647) / 2147483647;
  for (let i = 0; i < 64 * 64; i++) grade.push(rnd());
  const v = (a, b) => grade[((b % 64 + 64) % 64) * 64 + ((a % 64 + 64) % 64)];
  const ruido2 = (x, y) => { const ix = Math.floor(x), iy = Math.floor(y), fx = suave(x - ix), fy = suave(y - iy);
    return lerp(lerp(v(ix, iy), v(ix + 1, iy), fx), lerp(v(ix, iy + 1), v(ix + 1, iy + 1), fx), fy); };
  const fbm = (x, y) => .5 * ruido2(x, y) + .25 * ruido2(2 * x + 7, 2 * y + 3) + .125 * ruido2(4 * x + 13, 4 * y + 5) + .0625 * ruido2(8 * x + 1, 8 * y + 9);
  for (let y = 0; y < H; y++) {
    const lat = (.5 - y / H) * Math.PI;  // +90° no topo
    const el = Math.sin(lat), t = Math.max(0, el);
    for (let x = 0; x < W; x++) {
      const lon = (x / W - .5) * 2 * Math.PI;
      const dir = [Math.cos(lat) * Math.sin(lon), el, -Math.cos(lat) * Math.cos(lon)];  // equirect padrão do three
      const cosSol = dir[0] * sd.x + dir[1] * sd.y + dir[2] * sd.z;
      let r, gg, b;
      if (el >= 0) {
        const k = Math.pow(t, .55);  // o azul aprofunda depressa acima do horizonte
        r = lerp(Hz[0], Z[0], k); gg = lerp(Hz[1], Z[1], k); b = lerp(Hz[2], Z[2], k);
        // nuvens: fbm em coordenadas projetadas, mais densas a meia altura, desaparecem no zênite e no horizonte
        const n = fbm(6 * dir[0] / (el + .25) * .5 + 3, 6 * dir[2] / (el + .25) * .5 + 5);
        const faixa = Math.sin(Math.min(1, t * 2.2) * Math.PI) ;
        const nuvem = limitar((n - (.62 - .2 * nuvens)) / .16) * faixa;
        const sombra = 1 - .18 * limitar((n - .7) / .1);  // a barriga da nuvem um pouco cinza
        r = lerp(r, 252 * sombra, nuvem); gg = lerp(gg, 250 * sombra, nuvem); b = lerp(b, 247 * sombra, nuvem);
        // o halo do sol e o disco
        const halo = Math.pow(Math.max(0, cosSol), 48) * .55 + Math.pow(Math.max(0, cosSol), 6) * .18;
        r = lerp(r, 255, halo); gg = lerp(gg, 250, halo); b = lerp(b, 235, halo);
        if (cosSol > .9994) { r = 255; gg = 253; b = 240; }
      } else {
        const k = Math.pow(-el, .6);
        r = lerp(Hz[0], C[0], k); gg = lerp(Hz[1], C[1], k); b = lerp(Hz[2], C[2], k);
      }
      const i = (y * W + x) * 4;
      d[i] = r; d[i + 1] = gg; d[i + 2] = b; d[i + 3] = 255;
    }
  }
  g.putImageData(img, 0, 0);
  const tx = new THREE.CanvasTexture(c);
  tx.mapping = THREE.EquirectangularReflectionMapping;
  tx.colorSpace = THREE.SRGBColorSpace;
  return tx;
}

export function criarPalco({ceu = 0xD9E2EA, nevoa = null, solPos = [-40, 60, 30], nuvens = .5} = {}) {
  const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
  renderer.setPixelRatio(2);
  renderer.setSize(LARGURA, ALTURA); // estilo 1920×1080 CSS, buffer 3840×2160: o print reduz e suaviza as bordas
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);
  const cena = new THREE.Scene();
  const sol = new THREE.DirectionalLight(0xFFF1DC, 2.4);
  sol.position.set(...solPos);
  const ceuTx = pintarCeu(sol.position, {horizonte: ceu, nuvens});
  cena.background = ceuTx;
  cena.backgroundBlurriness = 0;
  if (nevoa) cena.fog = new THREE.Fog(ceu, nevoa[0], nevoa[1]);
  const pmrem = new THREE.PMREMGenerator(renderer);
  cena.environment = pmrem.fromEquirectangular(ceuTx).texture;
  cena.environmentIntensity = .85;
  const camera = new THREE.PerspectiveCamera(35, LARGURA / ALTURA, .1, 600);
  const hemi = new THREE.HemisphereLight(0xCFDCEC, 0x8E7A62, .35);
  cena.add(hemi);
  sol.castShadow = true;
  sol.shadow.mapSize.set(4096, 4096);
  sol.shadow.bias = -.0002;
  sol.shadow.normalBias = .02;
  sol.shadow.radius = 4;
  Object.assign(sol.shadow.camera, {left: -60, right: 60, top: 60, bottom: -60, near: 1, far: 200});
  cena.add(sol, sol.target);
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(2);
  composer.setSize(LARGURA, ALTURA);
  composer.addPass(new RenderPass(cena, camera));
  const ao = new GTAOPass(cena, camera, LARGURA, ALTURA);
  ao.updateGtaoMaterial({radius: .5, distanceExponent: 1.5, thickness: 1, scale: 1.2, samples: 16});
  ao.updatePdMaterial({lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 4, rings: 2, samples: 16});
  composer.addPass(ao);
  composer.addPass(new OutputPass());
  return {THREE, renderer, cena, camera, sol, hemi, composer, ao};
}

// textura procedural: ruído de valor em 3 oitavas (grade G×G, periódica) + grão fino; semente fixa por tipo.
// Devolve o mapa de cor (cor-base em sRGB modulada pelo ruído), o mapa de normais (derivado do mesmo relevo, com a
// força `relevo`) e o mapa de rugosidade (a rugosidade-base variando com o relevo): é o que dá às superfícies o
// micro-relevo e o brilho irregular que a luz real revela (o mesmo princípio dos materiais PBR do Lumion).
function ruido(cor, variacao, G, tam, semente, relevo, rug) {
  let s = semente;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const grade = [];
  for (let i = 0; i < G * G * 16; i++) grade.push(rnd());
  const GG = G * 4;
  const v = (a, b) => grade[((b % GG + GG) % GG) * GG + ((a % GG + GG) % GG)];
  // cada oitava é periódica no seu próprio passo `esc` (índices módulo esc): a textura fecha sem emenda no ladrilho
  const oitava = (x, y, esc) => { const gx = x * esc, gy = y * esc, ix = Math.floor(gx), iy = Math.floor(gy), fx = suave(gx - ix), fy = suave(gy - iy);
    const a = ix % esc, b = (ix + 1) % esc, c = iy % esc, e = (iy + 1) % esc;
    return lerp(lerp(v(a, c), v(b, c), fx), lerp(v(a, e), v(b, e), fx), fy); };
  const alt = new Float32Array(tam * tam);
  for (let y = 0; y < tam; y++) for (let x = 0; x < tam; x++) {
    const u = x / tam, w = y / tam;
    alt[y * tam + x] = .62 * oitava(u, w, G) + .26 * oitava(u, w, 2 * G) + .12 * oitava(u, w, 4 * G);
  }
  const r0 = (cor >> 16) & 255, g0 = (cor >> 8) & 255, b0 = cor & 255;
  const mk = () => { const c = document.createElement('canvas'); c.width = c.height = tam; const g = c.getContext('2d'); return [c, g, g.createImageData(tam, tam)]; };
  const [cc, gc, ic] = mk(), [cn, gn, inn] = mk(), [cr, gr, ir] = mk();
  for (let y = 0; y < tam; y++) for (let x = 0; x < tam; x++) {
    const i = (y * tam + x) * 4, n = alt[y * tam + x];
    const k = 1 + (n - .5) * variacao + (rnd() - .5) * variacao * .35;
    ic.data[i] = Math.min(255, r0 * k); ic.data[i + 1] = Math.min(255, g0 * k); ic.data[i + 2] = Math.min(255, b0 * k); ic.data[i + 3] = 255;
    // normal por diferenças finitas (periódica), espaço tangente: x → R, y → G, z → B
    const dx = (alt[y * tam + (x + 1) % tam] - alt[y * tam + (x + tam - 1) % tam]) * tam * relevo * .5;
    const dy = (alt[((y + 1) % tam) * tam + x] - alt[((y + tam - 1) % tam) * tam + x]) * tam * relevo * .5;
    const L = Math.hypot(dx, dy, 1);
    inn.data[i] = 128 + 127 * (-dx / L); inn.data[i + 1] = 128 + 127 * (-dy / L); inn.data[i + 2] = 128 + 127 * (1 / L); inn.data[i + 3] = 255;
    const rr = Math.min(1, Math.max(.05, rug + (n - .5) * .5)) * 255;
    ir.data[i] = ir.data[i + 1] = ir.data[i + 2] = rr; ir.data[i + 3] = 255;
  }
  gc.putImageData(ic, 0, 0); gn.putImageData(inn, 0, 0); gr.putImageData(ir, 0, 0);
  return {cor: cc, normal: cn, rugosidade: cr};
}
// pasto e solo têm um pintor próprio por cima do ruído: milhares de fios de capim (com tons de verde e de palha) ou
// pedriscos e marcas, desenhados com cópias deslocadas para a textura continuar periódica
function pintarDetalhe(tipo, mapas, tam, semente) {
  let s = semente * 7 + 3;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const gc = mapas.cor.getContext('2d'), gn = mapas.normal.getContext('2d');
  const copias = (f) => { for (const dx of [-tam, 0, tam]) for (const dy of [-tam, 0, tam]) f(dx, dy); };
  if (tipo === 'pasto') {
    for (let i = 0; i < 26000; i++) {
      const x = rnd() * tam, y = rnd() * tam, L = 5 + rnd() * 11, ang = -Math.PI / 2 + (rnd() - .5) * 1.1;
      const palha = rnd() < .12, h = palha ? 62 + rnd() * 14 : 84 + rnd() * 24, sat = palha ? 45 + rnd() * 20 : 38 + rnd() * 30, lum = palha ? 42 + rnd() * 18 : 24 + rnd() * 22;
      gc.strokeStyle = `hsl(${h} ${sat}% ${lum}%)`; gc.lineWidth = 1 + rnd() * .8;
      copias((dx, dy) => { gc.beginPath(); gc.moveTo(x + dx, y + dy); gc.lineTo(x + dx + Math.cos(ang) * L, y + dy + Math.sin(ang) * L); gc.stroke(); });
      // no mapa de normais, cada fio inclina a normal para o lado (um risco claro e um escuro)
      gn.strokeStyle = rnd() < .5 ? 'rgb(168,128,255)' : 'rgb(88,128,255)'; gn.lineWidth = 1;
      copias((dx, dy) => { gn.beginPath(); gn.moveTo(x + dx, y + dy); gn.lineTo(x + dx + Math.cos(ang) * L, y + dy + Math.sin(ang) * L); gn.stroke(); });
    }
  } else if (tipo === 'solo') {
    for (let i = 0; i < 3500; i++) {
      const x = rnd() * tam, y = rnd() * tam, r = .8 + rnd() * 2.2, lum = 30 + rnd() * 30;
      gc.fillStyle = `hsl(${18 + rnd() * 14} ${20 + rnd() * 25}% ${lum}%)`;
      copias((dx, dy) => { gc.beginPath(); gc.ellipse(x + dx, y + dy, r, r * (.6 + rnd() * .4), rnd() * Math.PI, 0, 2 * Math.PI); gc.fill(); });
      gn.fillStyle = 'rgb(128,150,255)';
      copias((dx, dy) => { gn.beginPath(); gn.arc(x + dx, y + dy - r * .3, r * .8, 0, 2 * Math.PI); gn.fill(); });
    }
  }
}
// relevo: força do mapa de normais (0 = liso); env: intensidade do reflexo do céu no material
const TIPOS = {
  pasto: {cor: 0x5E7F3C, variacao: .4, G: 10, rug: 1, relevo: .008, macro: .5},
  solo: {cor: 0xA3714F, variacao: .34, G: 12, rug: 1, relevo: .01, macro: .35},
  concreto: {cor: 0xBAB5AB, variacao: .16, G: 16, rug: .9, relevo: .004},
  aco: {cor: 0xC3CAD0, variacao: .08, G: 24, rug: .34, metal: .8, relevo: .0015, env: 1.2},
  acoPintado: {cor: 0x5E6B78, variacao: .06, G: 12, rug: .5, metal: .35, relevo: .001, env: 1.1},
  madeira: {cor: 0xA27B52, variacao: .28, G: 6, rug: .75, relevo: .006},
  plastico: {cor: 0x2E3237, variacao: .04, G: 4, rug: .45, relevo: .001, env: 1.2},
  papel: {cor: 0xF4F1EA, variacao: .03, G: 4, rug: .92, relevo: .002},
  telha: {cor: 0xAEB6BD, variacao: .1, G: 10, rug: .45, metal: .55, relevo: .003, env: 1.2},
  folha: {cor: 0x587B3E, variacao: .34, G: 6, rug: .95, relevo: .01},
  tronco: {cor: 0x7A6048, variacao: .22, G: 6, rug: 1, relevo: .012},
  asfalto: {cor: 0x4A4D50, variacao: .1, G: 12, rug: .95, relevo: .006},
  acento: {cor: LARANJA, variacao: .05, G: 4, rug: .55, relevo: .001},
  vermelho: {cor: 0xC0392B, variacao: .05, G: 4, rug: .65, relevo: .001},  // as paredes a construir, na cor da planta
};
const cache = {};
export function material(tipo, {repetir = 1} = {}) {
  const chave = tipo + '|' + repetir;
  if (cache[chave]) return cache[chave];
  const d = TIPOS[tipo];
  if (!d) throw new Error('material desconhecido: ' + tipo);
  let semente = 7;
  for (const ch of tipo) semente = (semente * 31 + ch.charCodeAt(0)) % 2147483647;
  const tam = tipo === 'pasto' || tipo === 'solo' ? 1024 : 512;
  const mapas = ruido(d.cor, d.variacao, d.G, tam, semente || 1, d.relevo || 0, d.rug);
  pintarDetalhe(tipo, mapas, tam, semente || 1);
  const textura = (canvas, srgb) => {
    const tx = new THREE.CanvasTexture(canvas);
    if (srgb) tx.colorSpace = THREE.SRGBColorSpace;
    tx.wrapS = tx.wrapT = THREE.RepeatWrapping;
    tx.repeat.set(repetir, repetir);
    tx.anisotropy = 8;
    return tx;
  };
  const m = new THREE.MeshStandardMaterial({
    map: textura(mapas.cor, true), normalMap: textura(mapas.normal, false), roughnessMap: textura(mapas.rugosidade, false),
    roughness: 1, metalness: d.metal || 0, envMapIntensity: d.env || 1,
  });
  if (d.macro) {
    // variação em grande escala (manchas de dezenas de metros) por cima do ladrilho: esconde a repetição do pasto e do solo
    const macro = textura(ruido(0x808080, d.macro, 5, 256, semente * 3 + 1, 0, 1).cor, false);
    macro.repeat.set(1, 1);
    m.onBeforeCompile = sh => {
      sh.uniforms.macroMap = {value: macro}; sh.uniforms.macroEscala = {value: 1 / 24};
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <map_pars_fragment>', '#include <map_pars_fragment>\nuniform sampler2D macroMap; uniform float macroEscala;')
        .replace('#include <map_fragment>', '#include <map_fragment>\n\tdiffuseColor.rgb *= 2.0 * texture2D(macroMap, vMapUv * macroEscala).rgb;');
    };
    m.customProgramCacheKey = () => 'macro';
  }
  return (cache[chave] = m);
}

// uma árvore: tronco cônico e copa de sete esferas irregulares (icosaedros com vértices deslocados); `s` é a escala
export function arvore(s = 1) {
  const g = new THREE.Group();
  const tronco = new THREE.Mesh(new THREE.CylinderGeometry(.12 * s, .18 * s, 3 * s, 10), material('tronco'));
  tronco.position.y = 1.5 * s; tronco.castShadow = true; g.add(tronco);
  [[0, 3.6, 0, 1.5], [.6, 3.1, .3, 1.1], [-.5, 3.3, -.4, 1.2], [.2, 4.3, .5, 1.0], [-.7, 4.0, .4, .9], [.8, 3.8, -.6, .95], [-.2, 2.7, .8, .85]].forEach((f, i) => {
    const geo = new THREE.IcosahedronGeometry(f[3] * s, 2), pos = geo.attributes.position;
    for (let k = 0; k < pos.count; k++) { const r = 1 + .18 * Math.sin(12.9898 * k + 7 * i) * Math.cos(78.233 * k); pos.setXYZ(k, pos.getX(k) * r, pos.getY(k) * r, pos.getZ(k) * r); }
    geo.computeVertexNormals();
    const copa = new THREE.Mesh(geo, material('folha', {repetir: 2}));
    copa.position.set(f[0] * s, f[1] * s, f[2] * s); copa.castShadow = copa.receiveShadow = true; g.add(copa);
  });
  return g;
}

// vidro: reflete o céu (envMap) e deixa ver um interior escuro; sem transmissão física (cara no SwiftShader)
export function vidro() {
  if (cache.vidro) return cache.vidro;
  return (cache.vidro = new THREE.MeshPhysicalMaterial({color: 0x3A4A56, roughness: .06, metalness: 0, envMapIntensity: 1.6, clearcoat: 1, clearcoatRoughness: .04}));
}

const PRONTOS = [];
const carregador = new THREE.TextureLoader();
export function documento(url) {
  const p = carregador.loadAsync(url).then(tx => {
    tx.colorSpace = THREE.SRGBColorSpace;
    tx.anisotropy = 16;
    tx.minFilter = THREE.LinearMipmapLinearFilter;
    tx.generateMipmaps = true;
    return tx;
  });
  PRONTOS.push(p);
  return p;
}

// câmera por chaves: Catmull-Rom centrípeta nas posições e nos alvos; em t = tᵢ a câmera está exatamente na chave i
// (o último quadro é exato); a suavização é global (acelera no início, freia no fim), não em cada chave
export function trajeto(chaves) {
  const P = new THREE.CatmullRomCurve3(chaves.map(k => new THREE.Vector3(...k[1])), false, 'centripetal');
  const A = new THREE.CatmullRomCurve3(chaves.map(k => new THREE.Vector3(...k[2])), false, 'centripetal');
  const T = chaves.map(k => k[0]), n = T.length;
  return function (camera, t) {
    const tt = T[0] + (T[n - 1] - T[0]) * suave((t - T[0]) / (T[n - 1] - T[0]));
    let i = 0;
    while (i < n - 2 && tt > T[i + 1]) i++;
    const u = (i + limitar((tt - T[i]) / (T[i + 1] - T[i]))) / (n - 1);
    camera.position.copy(P.getPoint(u));
    camera.lookAt(A.getPoint(u));
    camera.updateMatrixWorld();
  };
}

// a chave que põe um plano de largura `largura` (proporção 1,6) exatamente em RETANGULO: câmera no eixo do plano
export function enquadrarPlano(camera, centro, normal, largura) {
  const vfov = THREE.MathUtils.degToRad(camera.fov);
  const hfov = 2 * Math.atan(Math.tan(vfov / 2) * camera.aspect);
  const d = largura / (2 * RETANGULO.w * Math.tan(hfov / 2));
  const pos = centro.clone().addScaledVector(normal.clone().normalize(), d);
  return [pos.toArray(), centro.toArray()];
}

export function publicar(palco, cam, run) {
  window.__palco = palco;
  window.PRONTO = Promise.all(PRONTOS);
  window.renderCena = function (t) { run(t); cam(palco.camera, t); palco.composer.render(); };
}
