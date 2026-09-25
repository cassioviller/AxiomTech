// Kit das cenas do site v2: palco (render 2× para antisserrilhado, luz, ambiente, sombras suaves, oclusão GTAO),
// materiais com textura procedural, câmera por chaves e o carregador dos documentos reais.
// Contrato de cada cena: publicar(palco, cam, run) define window.renderCena(t) (t = 0..10, pura em t) e window.PRONTO.
// Sem tone mapping (NoToneMapping): a tela com o documento real tem de sair no vídeo com as cores da imagem da página.
import * as THREE from 'three';
import {EffectComposer} from './vendor/addons/postprocessing/EffectComposer.js';
import {RenderPass} from './vendor/addons/postprocessing/RenderPass.js';
import {GTAOPass} from './vendor/addons/postprocessing/GTAOPass.js';
import {OutputPass} from './vendor/addons/postprocessing/OutputPass.js';
import {RoomEnvironment} from './vendor/addons/environments/RoomEnvironment.js';
export {THREE};

export const LARGURA = 1920, ALTURA = 1080;
export const RETANGULO = {x: .2, y: 1 / 6, w: .6, h: 2 / 3}; // onde o documento termina no último quadro (frações do quadro); a página usa os mesmos números
const LARANJA = 0xE0622A;

export const limitar = x => Math.max(0, Math.min(1, x));
export const suave = x => { x = limitar(x); return x * x * (3 - 2 * x); };
export const rampa = (t, a, b) => suave((t - a) / (b - a));
export const lerp = (a, b, f) => a + (b - a) * f;

export function criarPalco({ceu = 0xD9E2EA, nevoa = null} = {}) {
  const renderer = new THREE.WebGLRenderer({antialias: true, preserveDrawingBuffer: true});
  renderer.setPixelRatio(2);
  renderer.setSize(LARGURA, ALTURA); // estilo 1920×1080 CSS, buffer 3840×2160: o print reduz e suaviza as bordas
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.body.appendChild(renderer.domElement);
  const cena = new THREE.Scene();
  cena.background = new THREE.Color(ceu);
  if (nevoa) cena.fog = new THREE.Fog(ceu, nevoa[0], nevoa[1]);
  const pmrem = new THREE.PMREMGenerator(renderer);
  cena.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture;
  cena.environmentIntensity = .55;
  const camera = new THREE.PerspectiveCamera(35, LARGURA / ALTURA, .1, 600);
  const hemi = new THREE.HemisphereLight(0xEEF3FA, 0x9A7B60, .9);
  cena.add(hemi);
  const sol = new THREE.DirectionalLight(0xFFF3E4, 2.2);
  sol.position.set(-40, 60, 30);
  sol.castShadow = true;
  sol.shadow.mapSize.set(4096, 4096);
  sol.shadow.bias = -.0002;
  sol.shadow.normalBias = .02;
  sol.shadow.radius = 3;
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

// textura procedural: ruído de valor (grade G×G, periódica) + grão fino, na cor-base em sRGB; semente fixa por tipo
function ruido(cor, variacao, G, tam, semente) {
  let s = semente;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const grade = [];
  for (let i = 0; i < G * G; i++) grade.push(rnd());
  const v = (a, b) => grade[((b % G + G) % G) * G + ((a % G + G) % G)];
  const r0 = (cor >> 16) & 255, g0 = (cor >> 8) & 255, b0 = cor & 255;
  const c = document.createElement('canvas');
  c.width = c.height = tam;
  const g = c.getContext('2d'), img = g.createImageData(tam, tam);
  for (let y = 0; y < tam; y++) for (let x = 0; x < tam; x++) {
    const gx = x / tam * G, gy = y / tam * G, ix = Math.floor(gx), iy = Math.floor(gy);
    const fx = suave(gx - ix), fy = suave(gy - iy);
    const n = lerp(lerp(v(ix, iy), v(ix + 1, iy), fx), lerp(v(ix, iy + 1), v(ix + 1, iy + 1), fx), fy);
    const k = 1 + (n - .5) * variacao + (rnd() - .5) * variacao * .35, i = (y * tam + x) * 4;
    img.data[i] = Math.min(255, r0 * k); img.data[i + 1] = Math.min(255, g0 * k); img.data[i + 2] = Math.min(255, b0 * k); img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  return c;
}
const TIPOS = {
  pasto: {cor: 0x86A05C, variacao: .35, G: 8, rug: 1},
  solo: {cor: 0xB4663F, variacao: .3, G: 10, rug: 1},
  concreto: {cor: 0xBEB9AF, variacao: .18, G: 16, rug: .95},
  aco: {cor: 0xC3CAD0, variacao: .08, G: 24, rug: .38, metal: .75},
  acoPintado: {cor: 0x5E6B78, variacao: .06, G: 12, rug: .55, metal: .3},
  madeira: {cor: 0xA27B52, variacao: .25, G: 6, rug: .8},
  plastico: {cor: 0x2E3237, variacao: .04, G: 4, rug: .5},
  papel: {cor: 0xF4F1EA, variacao: .03, G: 4, rug: .95},
  telha: {cor: 0xAEB6BD, variacao: .1, G: 10, rug: .5, metal: .5},
  folha: {cor: 0x5F7F45, variacao: .3, G: 6, rug: 1},
  tronco: {cor: 0x7A6048, variacao: .2, G: 6, rug: 1},
  acento: {cor: LARANJA, variacao: .05, G: 4, rug: .6},
};
const cache = {};
export function material(tipo, {repetir = 1} = {}) {
  const chave = tipo + '|' + repetir;
  if (cache[chave]) return cache[chave];
  const d = TIPOS[tipo];
  if (!d) throw new Error('material desconhecido: ' + tipo);
  let semente = 7;
  for (const ch of tipo) semente = (semente * 31 + ch.charCodeAt(0)) % 2147483647;
  const tx = new THREE.CanvasTexture(ruido(d.cor, d.variacao, d.G, 512, semente || 1));
  tx.colorSpace = THREE.SRGBColorSpace;
  tx.wrapS = tx.wrapT = THREE.RepeatWrapping;
  tx.repeat.set(repetir, repetir);
  tx.anisotropy = 8;
  return (cache[chave] = new THREE.MeshStandardMaterial({map: tx, roughness: d.rug, metalness: d.metal || 0}));
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
