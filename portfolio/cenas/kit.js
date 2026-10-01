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
// qualidade do render, pela URL (?q=alta): a normal é a do Replit (SwiftShader, CPU); a alta é para o render local
// numa GPU (RTX 3060): buffer 4× (7680×4320, reduzido 4×4 na captura), sombra 8192 e GTAO com o dobro de amostras
const QUALIDADES = {normal: {escala: 2, sombra: 4096, ao: 16}, alta: {escala: 4, sombra: 8192, ao: 32}};
export const QUALIDADE = QUALIDADES[new URLSearchParams(location.search).get('q')] || QUALIDADES.normal;

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
  renderer.setPixelRatio(QUALIDADE.escala);
  renderer.setSize(LARGURA, ALTURA); // estilo 1920×1080 CSS, buffer 3840×2160 (alta: 7680×4320): o print reduz e suaviza as bordas
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
  sol.shadow.mapSize.set(QUALIDADE.sombra, QUALIDADE.sombra);
  sol.shadow.bias = -.0002;
  sol.shadow.normalBias = .02;
  sol.shadow.radius = 4;
  Object.assign(sol.shadow.camera, {left: -60, right: 60, top: 60, bottom: -60, near: 1, far: 200});
  cena.add(sol, sol.target);
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(QUALIDADE.escala);
  composer.setSize(LARGURA, ALTURA);
  composer.addPass(new RenderPass(cena, camera));
  const ao = new GTAOPass(cena, camera, LARGURA, ALTURA);
  ao.updateGtaoMaterial({radius: .5, distanceExponent: 1.5, thickness: 1, scale: 1.2, samples: QUALIDADE.ao});
  ao.updatePdMaterial({lumaPhi: 10, depthPhi: 2, normalPhi: 3, radius: 4, rings: 2, samples: QUALIDADE.ao});
  composer.addPass(ao);
  composer.addPass(new OutputPass());
  return {THREE, renderer, cena, camera, sol, hemi, composer, ao};
}

// ---------- materiais PBR procedurais ----------
// Cada tipo tem um tamanho real de ladrilho (L, em metros) e um desenho próprio do revestimento: veios na madeira,
// réguas no assoalho, peças e rejunte no porcelanato, ondas trapezoidais na telha, aço escovado, poros no concreto,
// casca de laranja na tinta, agregado no asfalto, sulcos na casca da árvore. O desenho dá três mapas: cor (sRGB),
// normais (derivadas da altura em metros pela inclinação real: o relevo tem o tamanho de verdade) e rugosidade.
// Mapeamento em metros (box mapping no espaço do objeto): a textura é projetada pela posição local de cada fragmento,
// no plano perpendicular ao eixo dominante da normal local, então o ladrilho tem o mesmo tamanho numa peça de 5 cm ou
// numa água de telhado de 7 m (antes, as UVs 0..1 de cada face esticavam o ruído em manchas), e acompanha a peça quando
// ela se move (o guindaste, os painéis subindo). Faces em x: (z, y); em y: (x, z); em z: (x, y). O "u" da textura
// (o eixo x do canvas) é o comprimento dos veios, das réguas e das ondas da telha.

// ruído de valor periódico com frequências independentes em u e v (escU, escV inteiros ≤ 256): fecha sem emenda
function geradorRuido(semente) {
  let s = semente;
  const rnd = () => (s = (s * 16807) % 2147483647) / 2147483647;
  const N = 256, grade = new Float32Array(N * N);
  for (let i = 0; i < N * N; i++) grade[i] = rnd();
  const n = (u, v, escU, escV = escU) => {
    const gx = u * escU, gy = v * escV, ix = Math.floor(gx), iy = Math.floor(gy), fx = suave(gx - ix), fy = suave(gy - iy);
    const a = ((ix % escU) + escU) % escU, b = (a + 1) % escU, c = ((iy % escV) + escV) % escV, e = (c + 1) % escV;
    return lerp(lerp(grade[c * N + a], grade[c * N + b], fx), lerp(grade[e * N + a], grade[e * N + b], fx), fy);
  };
  const fbm = (u, v, esc, escV = esc) => .55 * n(u, v, esc, escV) + .27 * n(u, v, 2 * esc, 2 * escV) + .18 * n(u, v, 4 * esc, 4 * escV);
  return {rnd, n, fbm};
}

// desenhos: (u, v ∈ [0,1), px = coluna, py = linha, R = gerador, P = pré-cálculo do tipo) → [altura em m, fator de cor, rugosidade]
// (ou [h, k, r, [r, g, b]] quando o pixel tem cor própria, como o rejunte); `prep` roda uma vez por tipo
const DESENHOS = {
  pasto: (u, v, px, py, R) => { const f = R.fbm(u, v, 10); return [.004 * f, 1 + (f - .5) * .4 + (R.rnd() - .5) * .14, 1]; },
  solo: (u, v, px, py, R) => { const f = R.fbm(u, v, 12); return [.003 * f, 1 + (f - .5) * .34 + (R.rnd() - .5) * .12, 1]; },
  concreto: {
    // poros (bolhas de ar na superfície) e agregado fino; manchas leves de cura
    prep: (tam, R) => { const h = new Float32Array(tam * tam);
      for (let i = 0; i < 2600; i++) { const cx = R.rnd() * tam, cy = R.rnd() * tam, r = .6 + R.rnd() * 1.8;
        for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) { const d = Math.hypot(dx, dy) / r; if (d < 1) {
          const x = ((Math.round(cx) + dx) % tam + tam) % tam, y = ((Math.round(cy) + dy) % tam + tam) % tam; h[y * tam + x] = Math.min(h[y * tam + x], -(1 - d * d)); } } }
      return h; },
    f: (u, v, px, py, R, P, tam) => { const f = R.fbm(u, v, 6), g = R.n(u, v, 128), poro = P[py * tam + px];
      return [.0006 * g + .0012 * poro + .0004 * f, 1 + (f - .5) * .1 + (g - .5) * .06 + (R.rnd() - .5) * .05 + .28 * poro, .9 - .1 * poro]; },
  },
  aco: (u, v, px, py, R) => { const s = R.n(u, v, 4, 220), m = R.fbm(u, v, 3); // escovado ao longo de u
    return [.00004 * s, 1 + (s - .5) * .08 + (m - .5) * .05, .3 + (s - .5) * .12 + (m - .5) * .1]; },
  acoPintado: (u, v, px, py, R) => { const f = R.fbm(u, v, 40), m = R.fbm(u, v, 3); // pintura eletrostática: casca de laranja fina
    return [.00012 * f, 1 + (f - .5) * .04 + (m - .5) * .04, .45 + (f - .5) * .1]; },
  plastico: (u, v, px, py, R) => { const f = R.fbm(u, v, 48); return [.00004 * f, 1 + (f - .5) * .03, .45 + (f - .5) * .08]; },
  papel: (u, v, px, py, R) => { const f = R.n(u, v, 96, 64), m = R.fbm(u, v, 4); // placa pintada: fibra fina, sem manchas
    return [.00004 * f, 1 + (f - .5) * .025 + (m - .5) * .02, .9]; },
  tinta: (u, v, px, py, R) => { const f = R.fbm(u, v, 56), m = R.fbm(u, v, 3); // parede pintada com rolo: casca de laranja
    return [.00018 * f, 1 + (f - .5) * .025 + (m - .5) * .02, .88 + (f - .5) * .08]; },
  madeira: (u, v, px, py, R) => { // veios ao longo de u: anéis deformados pelo ruído, fibras finas, nós raros
    const anel = v * 9 + 2.2 * R.n(u, v, 2, 5) + .6 * R.n(u, v, 8, 24), fr = anel - Math.floor(anel);
    const veio = Math.pow(Math.abs(Math.sin(fr * Math.PI)), 8), fibra = R.n(u, v, 6, 200), tom = R.fbm(u, v, 2, 3);
    return [-.00015 * veio + .00005 * fibra, 1 + (tom - .5) * .16 - .11 * veio + (fibra - .5) * .07, .62 + .14 * veio];
  },
  assoalho: { // réguas de 15 cm (16 por ladrilho de 2,4 m), topo alternado; junta rebaixada escura entre réguas
    prep: (tam, R) => Array.from({length: 16}, () => ({tom: (R.rnd() - .5) * .24, corte: R.rnd(), des: R.rnd() * 40})),
    f: (u, v, px, py, R, P, tam) => {
      const i = Math.floor(v * 16), p = P[i], lv = v * 16 - i, lu = (u + p.corte) % 1;
      const junta = Math.min(lv, 1 - lv) * tam / 16 < 1.2 || Math.min(lu, 1 - lu) * tam < 1.2;
      if (junta) return [-.0015, .45, 1];
      const anel = (lv + p.des) * 3 + 2 * R.n(u, v, 3, 16) + .5 * R.n(u, v, 12, 64), fr = anel - Math.floor(anel);
      const veio = Math.pow(Math.abs(Math.sin(fr * Math.PI)), 5), fibra = R.n(u, v, 8, 256);
      return [-.0002 * veio + .00005 * fibra, 1 + p.tom - .18 * veio + (fibra - .5) * .07, .45 + .2 * veio];
    },
  },
  porcelanato: { // peças de 60 × 60 cm (2 × 2 no ladrilho de 1,2 m), rejunte de 3 mm cinza, leve marmorizado, polido
    prep: (tam, R) => [0, 1, 2, 3].map(() => (R.rnd() - .5) * .05),
    f: (u, v, px, py, R, P, tam) => {
      const meia = tam / 2, x = px % meia, y = py % meia, e = Math.min(x, meia - 1 - x, y, meia - 1 - y);
      if (e < 1.3) return [-.0015, 1, 1, [0x8E, 0x8A, 0x83]];
      const f = R.fbm(u, v, 6), veio = Math.pow(1 - Math.abs(2 * R.n(u, v, 4, 10) - 1), 18);
      return [.00002 * f, 1 + P[(py < meia ? 0 : 2) + (px < meia ? 0 : 1)] + (f - .5) * .05 - .06 * veio, .28 + (f - .5) * .06];
    },
  },
  telha: { // telha trapezoidal de aço galvalume: ondas de 25 cm (crista 5 cm, alma inclinada, vale plano), altura 3 cm
    f: (u, v, px, py, R) => {
      const p = (u * 4) % 1, crista = .2, alma = .16;
      const h = p < crista ? 1 : p < crista + alma ? 1 - (p - crista) / alma : p < 1 - alma ? 0 : (p - (1 - alma)) / alma;
      const escorrido = R.n(u, v, 64, 3), m = R.fbm(u, v, 2);  // escorridos de chuva ao longo da onda
      return [.03 * h, 1 + (escorrido - .5) * .08 + (m - .5) * .05 + .04 * h, .38 + (escorrido - .5) * .14];
    },
  },
  folha: (u, v, px, py, R) => { const f = R.fbm(u, v, 12), g = R.n(u, v, 64); return [.004 * f + .001 * g, 1 + (f - .5) * .34 + (g - .5) * .18, .9]; },
  tronco: (u, v, px, py, R) => { // casca com sulcos verticais (ao longo de v), placas quebradas pelo ruído
    const s = Math.abs(Math.sin((u * 18 + 1.4 * R.n(u, v, 6, 3)) * Math.PI)), placa = R.fbm(u, v, 12, 4);
    return [.006 * Math.pow(s, .5) + .002 * placa, .78 + .3 * Math.pow(s, .5) + (placa - .5) * .2, 1];
  },
  asfalto: { // agregado: pedriscos claros e escuros no ligante, com vazios
    prep: (tam, R) => { const h = new Float32Array(tam * tam), c = new Float32Array(tam * tam);
      for (let i = 0; i < 9000; i++) { const cx = R.rnd() * tam, cy = R.rnd() * tam, r = .8 + R.rnd() * 2.2, k = R.rnd() < .5 ? .35 : -.25;
        for (let dy = -3; dy <= 3; dy++) for (let dx = -3; dx <= 3; dx++) { const d = Math.hypot(dx, dy) / r; if (d < 1) {
          const j = (((Math.round(cy) + dy) % tam + tam) % tam) * tam + (((Math.round(cx) + dx) % tam + tam) % tam); h[j] = Math.max(h[j], 1 - d * d); c[j] = k; } } }
      return {h, c}; },
    f: (u, v, px, py, R, P, tam) => { const j = py * tam + px, f = R.fbm(u, v, 4);
      return [.0015 * P.h[j], 1 + P.c[j] * P.h[j] + (f - .5) * .12 + (R.rnd() - .5) * .08, .92 - .1 * P.h[j]]; },
  },
  carpete: (u, v, px, py, R) => { // carpete de fios em laço: grão denso e irregular, fosco, sem brilho
    const g = R.n(u, v, 200), f = R.fbm(u, v, 24), m = R.fbm(u, v, 2);
    return [.0008 * g + .0005 * f, 1 + (g - .5) * .16 + (f - .5) * .08 + (m - .5) * .05, 1]; },
  acento: (u, v, px, py, R) => { const f = R.fbm(u, v, 40); return [.0001 * f, 1 + (f - .5) * .03, .55]; },
  vermelho: (u, v, px, py, R) => { const f = R.fbm(u, v, 40); return [.0001 * f, 1 + (f - .5) * .03, .65]; },
};
// cor-base, ladrilho L (m), resolução, rugosidade-base (multiplica o mapa), metal, reflexo do céu, macro (manchas de dezenas de m)
const TIPOS = {
  pasto: {cor: 0x5E7F3C, L: 10, tam: 1024, macro: .5},
  solo: {cor: 0xA3714F, L: 8, tam: 1024, macro: .35},
  concreto: {cor: 0xBAB5AB, L: 2, tam: 1024},
  aco: {cor: 0xC3CAD0, L: 1, tam: 512, metal: .8, env: 1.2},
  acoPintado: {cor: 0x5E6B78, L: .5, tam: 512, metal: .35, env: 1.1},
  madeira: {cor: 0xA27B52, L: 1, tam: 1024},
  assoalho: {cor: 0x9C7048, L: 2.4, tam: 1024, env: 1.1},
  porcelanato: {cor: 0xE4E0D8, L: 1.2, tam: 1024, env: .55},
  carpete: {cor: 0x67728A, L: .4, tam: 512},
  tinta: {cor: 0xEEEAE2, L: .6, tam: 512},
  plastico: {cor: 0x2E3237, L: .3, tam: 256, env: 1.2},
  papel: {cor: 0xF4F1EA, L: 1, tam: 512},
  telha: {cor: 0xAEB6BD, L: 1, tam: 512, metal: .55, env: 1.2},
  folha: {cor: 0x587B3E, L: .8, tam: 256},
  tronco: {cor: 0x7A6048, L: .6, tam: 512},
  asfalto: {cor: 0x4A4D50, L: 2, tam: 1024},
  acento: {cor: LARANJA, L: .3, tam: 256},
  vermelho: {cor: 0xC0392B, L: .3, tam: 256},  // as paredes a construir, na cor da planta
};

// os três mapas de um tipo, em canvas de tam × tam
function mapasDoTipo(tipo, semente) {
  const d = TIPOS[tipo], tam = d.tam, px = d.L / tam, R = geradorRuido(semente);
  const des = DESENHOS[tipo], fn = des.f || des, P = des.prep ? des.prep(tam, R) : null;
  const H = new Float32Array(tam * tam), K = new Float32Array(tam * tam), Rg = new Float32Array(tam * tam), C = new Array(tam * tam);
  for (let y = 0; y < tam; y++) for (let x = 0; x < tam; x++) {
    const o = fn(x / tam, y / tam, x, y, R, P, tam), i = y * tam + x;
    H[i] = o[0]; K[i] = o[1]; Rg[i] = o[2]; if (o[3]) C[i] = o[3];
  }
  const r0 = (d.cor >> 16) & 255, g0 = (d.cor >> 8) & 255, b0 = d.cor & 255;
  const mk = () => { const c = document.createElement('canvas'); c.width = c.height = tam; const g = c.getContext('2d'); return [c, g, g.createImageData(tam, tam)]; };
  const [cc, gc, ic] = mk(), [cn, gn, inn] = mk(), [cr, gr, ir] = mk();
  for (let y = 0; y < tam; y++) for (let x = 0; x < tam; x++) {
    const i = y * tam + x, q = i * 4, k = K[i], c = C[i];
    ic.data[q] = Math.min(255, (c ? c[0] : r0) * (c ? 1 : k)); ic.data[q + 1] = Math.min(255, (c ? c[1] : g0) * (c ? 1 : k));
    ic.data[q + 2] = Math.min(255, (c ? c[2] : b0) * (c ? 1 : k)); ic.data[q + 3] = 255;
    // inclinação real (m/m) por diferenças centrais periódicas; canvas y para baixo = v para cima (flipY)
    const dhu = (H[y * tam + (x + 1) % tam] - H[y * tam + (x + tam - 1) % tam]) / (2 * px);
    const dhv = -(H[((y + 1) % tam) * tam + x] - H[((y + tam - 1) % tam) * tam + x]) / (2 * px);
    const L = Math.hypot(dhu, dhv, 1);
    inn.data[q] = 128 + 127 * (-dhu / L); inn.data[q + 1] = 128 + 127 * (-dhv / L); inn.data[q + 2] = 128 + 127 / L; inn.data[q + 3] = 255;
    ir.data[q] = ir.data[q + 1] = ir.data[q + 2] = Math.min(1, Math.max(.04, Rg[i])) * 255; ir.data[q + 3] = 255;
  }
  gc.putImageData(ic, 0, 0); gn.putImageData(inn, 0, 0); gr.putImageData(ir, 0, 0);
  return {cor: cc, normal: cn, rugosidade: cr};
}
// pasto e solo têm um pintor próprio por cima: milhares de fios de capim (com tons de verde e de palha) ou pedriscos e
// marcas, desenhados com cópias deslocadas para a textura continuar periódica
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

// o box mapping no shader: a posição e a normal locais viram varyings; no fragmento, a UV em metros / L substitui as
// UVs da geometria nos mapas de cor, normais e rugosidade (e na base do espaço tangente, que o three deriva da UV)
const TROCA_UV = s => s.replace(/v(Map|NormalMap|RoughnessMap)Uv/g, 'uvCaixa');
function boxMapping(m, L, macro, macroMap) {
  m.onBeforeCompile = sh => {
    sh.uniforms.ladrilho = {value: L};
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vPosLocal; varying vec3 vNormLocal;')
      .replace('#include <uv_vertex>', '#include <uv_vertex>\n\tvPosLocal = position; vNormLocal = normal;');
    let fs = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vPosLocal; varying vec3 vNormLocal; uniform float ladrilho; vec2 uvCaixa;');
    for (const c of ['map_fragment', 'normal_fragment_begin', 'normal_fragment_maps', 'roughnessmap_fragment'])
      fs = fs.replace(`#include <${c}>`, TROCA_UV(THREE.ShaderChunk[c]));
    fs = fs.replace('void main() {', `void main() {
\tvec3 an = abs(vNormLocal);
\tuvCaixa = (an.x >= an.y && an.x >= an.z ? vPosLocal.zy : an.y >= an.z ? vPosLocal.xz : vPosLocal.xy) / ladrilho;`);
    if (macro) {
      sh.uniforms.macroMap = {value: macroMap}; sh.uniforms.macroEscala = {value: L / 40};
      fs = fs.replace('uniform float ladrilho;', 'uniform float ladrilho; uniform sampler2D macroMap; uniform float macroEscala;')
        .replace('#include <color_fragment>', '#include <color_fragment>\n\tdiffuseColor.rgb *= 2.0 * texture2D(macroMap, uvCaixa * macroEscala).rgb;');
    }
    sh.fragmentShader = fs;
  };
  m.customProgramCacheKey = () => 'caixa' + (macro ? '-macro' : '');
}

// para materiais das cenas que emprestam um mapa do kit (a areia e a brita usam as normais do solo): o mesmo box mapping
export function emMetros(m, tipo) { boxMapping(m, TIPOS[tipo].L, false, null); return m; }

const cache = {};
// `repetir` fica na assinatura por compatibilidade, sem efeito: o tamanho do ladrilho é o real de cada tipo (TIPOS.L)
export function material(tipo, {repetir = 1} = {}) {
  if (cache[tipo]) return cache[tipo];
  const d = TIPOS[tipo];
  if (!d) throw new Error('material desconhecido: ' + tipo);
  let semente = 7;
  for (const ch of tipo) semente = (semente * 31 + ch.charCodeAt(0)) % 2147483647;
  semente = semente || 1;
  const mapas = mapasDoTipo(tipo, semente);
  pintarDetalhe(tipo, mapas, d.tam, semente);
  const textura = (canvas, srgb) => {
    const tx = new THREE.CanvasTexture(canvas);
    if (srgb) tx.colorSpace = THREE.SRGBColorSpace;
    tx.wrapS = tx.wrapT = THREE.RepeatWrapping;
    tx.anisotropy = 8;
    return tx;
  };
  const m = new THREE.MeshStandardMaterial({
    map: textura(mapas.cor, true), normalMap: textura(mapas.normal, false), roughnessMap: textura(mapas.rugosidade, false),
    roughness: 1, metalness: d.metal || 0, envMapIntensity: d.env || 1,
  });
  // variação em grande escala (manchas de dezenas de metros) por cima do ladrilho: esconde a repetição do pasto e do solo
  const macro = d.macro ? textura(macroCanvas(d.macro, semente * 3 + 1), false) : null;
  boxMapping(m, d.L, !!d.macro, macro);
  return (cache[tipo] = m);
}
function macroCanvas(variacao, semente) {
  const tam = 256, R = geradorRuido(semente), c = document.createElement('canvas'); c.width = c.height = tam;
  const g = c.getContext('2d'), img = g.createImageData(tam, tam);
  for (let y = 0; y < tam; y++) for (let x = 0; x < tam; x++) {
    const k = Math.min(255, 128 * (1 + (R.fbm(x / tam, y / tam, 5) - .5) * variacao)), i = (y * tam + x) * 4;
    img.data[i] = img.data[i + 1] = img.data[i + 2] = k; img.data[i + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  return c;
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
