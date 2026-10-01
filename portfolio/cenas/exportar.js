// Exportador das cenas do site v2 para o Blender (ver cenas/exportar.py e portfolio/blender/montar.py).
// Roda dentro da página da cena (Playwright), depois de window.PRONTO. Não usa glTF: a animação das cenas é uma função
// pura de t (window.poseCena), então o que vai para o Blender é a pose de cada malha em cada quadro (matriz de mundo),
// mais a geometria, o material (com o tipo do kit, que o Blender troca por textura fotografada) e a câmera.
// Formato: {meta, materiais[], geometrias{}, itens[], camera, sol}; vetores numéricos em base64 (Float32, little-endian).
// Eixos e unidades do three.js (Y para cima, metros); a conversão para o Blender é feita lá.
window.exportarCena = function (tempos) {
  const P = window.__palco, THREE = P.THREE, cena = P.cena, camera = P.camera, N = tempos.length;
  const b64 = arr => { const u = new Uint8Array(arr.buffer, arr.byteOffset, arr.byteLength); let s = '';
    for (let i = 0; i < u.length; i += 32768) s += String.fromCharCode.apply(null, u.subarray(i, i + 32768)); return btoa(s); };
  const nomeDoMapa = tx => {
    if (!tx || !tx.image) return null;
    if (tx.image.src) return decodeURIComponent(tx.image.src.split('/').pop());
    if (!tx.userData.exportado) tx.userData.exportado = 'canvas-' + tx.uuid.slice(0, 8);
    return tx.userData.exportado;
  };
  const canvases = {};

  // --- materiais ---
  const materiais = [], idMat = new Map();
  function mat(m) {
    if (Array.isArray(m)) m = m[0];
    if (idMat.has(m.uuid)) return idMat.get(m.uuid);
    const d = {nome: m.name || '', tipo: m.userData.tipo || null, emMetros: m.userData.emMetros || null, ladrilho: m.userData.ladrilho || null,
      basico: !!m.isMeshBasicMaterial, vidro: m.name === 'vidro',
      cor: m.color ? m.color.toArray() : [1, 1, 1], rugosidade: m.roughness ?? 1, metal: m.metalness ?? 0,
      emissivo: m.emissive ? m.emissive.clone().multiplyScalar(m.emissiveIntensity ?? 1).toArray() : [0, 0, 0],
      transparente: !!m.transparent, opacidade: m.opacity ?? 1, duasFaces: m.side === THREE.DoubleSide,
      mapa: null, mapaPorQuadro: null, _m: m};
    idMat.set(m.uuid, materiais.length); materiais.push(d);
    return materiais.length - 1;
  }

  // --- geometrias: triângulos soltos, com a UV "em metros" do box mapping do kit calculada pela normal da face ---
  const geometrias = {};
  function geo(g) {
    if (geometrias[g.uuid]) return g.uuid;
    const pos = g.attributes.position, nor = g.attributes.normal, uv0 = g.attributes.uv, idx = g.index;
    const inicio = g.drawRange.start, fim = Math.min(idx ? idx.count : pos.count, inicio + g.drawRange.count);
    const n = fim - inicio, p = new Float32Array(n * 3), nn = new Float32Array(n * 3), um = new Float32Array(n * 2), u0 = new Float32Array(n * 2);
    const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), fn = new THREE.Vector3();
    for (let k = 0; k + 2 < n; k += 3) {
      const v = [0, 1, 2].map(j => idx ? idx.getX(inicio + k + j) : inicio + k + j);
      a.fromBufferAttribute(pos, v[0]); b.fromBufferAttribute(pos, v[1]); c.fromBufferAttribute(pos, v[2]);
      fn.copy(b).sub(a).cross(c.clone().sub(a));
      const ax = Math.abs(fn.x), ay = Math.abs(fn.y), az = Math.abs(fn.z);
      const eixo = ax >= ay && ax >= az ? 0 : ay >= az ? 1 : 2;  // a mesma regra do boxMapping do kit, pela normal da face
      for (let j = 0; j < 3; j++) {
        const i = v[j], o = k + j, x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
        p[o * 3] = x; p[o * 3 + 1] = y; p[o * 3 + 2] = z;
        if (nor) { nn[o * 3] = nor.getX(i); nn[o * 3 + 1] = nor.getY(i); nn[o * 3 + 2] = nor.getZ(i); }
        um[o * 2] = eixo === 0 ? z : x; um[o * 2 + 1] = eixo === 0 ? y : eixo === 1 ? z : y;
        if (uv0) { u0[o * 2] = uv0.getX(i); u0[o * 2 + 1] = uv0.getY(i); }
      }
    }
    geometrias[g.uuid] = {vertices: n, posicao: b64(p), normal: nor ? b64(nn) : null, uvMetros: b64(um), uv: uv0 ? b64(u0) : null};
    return g.uuid;
  }

  // --- itens: cada malha visível da cena; InstancedMesh vira um item com `instancias` ---
  const itens = [], arvores = [];
  const dentroDeAsset = o => { for (let x = o; x; x = x.parent) if (x.userData && x.userData.asset) return x; return null; };
  cena.traverse(o => {
    if (o.userData && o.userData.asset === 'arvore') arvores.push(o);
    if (!o.isMesh || !o.geometry || !o.geometry.attributes.position) return;
    const asset = dentroDeAsset(o);
    itens.push({o, d: {nome: o.name || o.type + '-' + o.id, geometria: geo(o.geometry), material: mat(o.material),
      sombra: !!o.castShadow, asset: asset ? asset.userData.asset + '-' + asset.id : null,
      instancias: o.isInstancedMesh ? o.count : 0,
      coresDasInstancias: o.isInstancedMesh && o.instanceColor ? b64(new Float32Array(o.instanceColor.array.slice(0, o.count * 3))) : null}});
  });

  // --- os quadros ---
  const visivel = o => { for (let x = o; x; x = x.parent) if (!x.visible) return false; return true; };
  const M = new THREE.Matrix4(), I = new THREE.Matrix4();
  for (const it of itens) {
    const n = Math.max(1, it.d.instancias);
    it.m = new Float32Array(N * n * 16); it.v = new Uint8Array(N);
  }
  const cam = new Float32Array(N * 16), fov = new Float32Array(N);
  const arv = arvores.map(() => new Float32Array(16));
  for (let q = 0; q < N; q++) {
    window.poseCena(tempos[q]);
    for (const it of itens) {
      const o = it.o;
      it.v[q] = visivel(o) ? 1 : 0;
      if (o.isInstancedMesh) for (let i = 0; i < o.count; i++) { o.getMatrixAt(i, I); M.multiplyMatrices(o.matrixWorld, I); it.m.set(M.elements, (q * o.count + i) * 16); }
      else it.m.set(o.matrixWorld.elements, q * 16);
    }
    for (const d of materiais) {
      const nome = nomeDoMapa(d._m.map);
      if (d._m.map && d._m.map.isCanvasTexture && !canvases[nome]) canvases[nome] = d._m.map.image.toDataURL('image/png');
      if (q === 0) { d.mapa = nome; d._mapas = [nome]; } else d._mapas.push(nome);
    }
    cam.set(camera.matrixWorld.elements, q * 16); fov[q] = camera.fov;
    if (q === 0) arvores.forEach((a, i) => arv[i].set(a.matrixWorld.elements));
  }
  // o que não muda vai uma vez só
  for (const it of itens) {
    const n = Math.max(1, it.d.instancias) * 16;
    let parado = true;
    for (let i = n; i < it.m.length && parado; i++) if (Math.abs(it.m[i] - it.m[i % n]) > 1e-6) parado = false;
    it.d.animado = !parado;
    it.d.matrizes = b64(parado ? it.m.subarray(0, n) : it.m);
    it.d.visivel = it.v.every(x => x === 1) ? null : Array.from(it.v);
  }
  for (const d of materiais) {
    if (d._mapas.some(x => x !== d._mapas[0])) d.mapaPorQuadro = d._mapas;
    delete d._m; delete d._mapas;
  }
  const sol = P.sol;
  return {
    meta: {quadros: N, tempos, largura: 1920, altura: 1080, eixos: 'three (Y para cima, metros)',
      fundo: cena.fog ? cena.fog.color.toArray() : null, nevoa: cena.fog ? [cena.fog.near, cena.fog.far] : null},
    materiais, geometrias, itens: itens.map(it => it.d), canvases,
    arvores: arvores.map((a, i) => ({id: 'arvore-' + a.id, escala: a.userData.escala, matriz: Array.from(arv[i])})),
    camera: {matrizes: b64(cam), fov: Array.from(fov), aspecto: camera.aspect, perto: camera.near, longe: camera.far},
    sol: {posicao: sol.position.toArray(), alvo: sol.target.position.toArray(), cor: sol.color.toArray(), intensidade: sol.intensity},
  };
};
