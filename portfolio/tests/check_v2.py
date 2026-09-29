#!/usr/bin/env python3
"""Checagens do site v2 (piloto): kit das cenas, documentos, cena do caso SIGE, vídeo e página.

Uso: python3 portfolio/tests/check_v2.py              (estático: documentos, texto, marcação)
     python3 portfolio/tests/check_v2.py --navegador  (+ kit, cena e página no Chromium, via servidor local)
     python3 portfolio/tests/check_v2.py --video      (+ vídeo publicado)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]  # portfolio/
SITE = RAIZ / "site"
CENAS_DIR = RAIZ / "cenas"
sys.path.insert(0, str(CENAS_DIR))
FALHAS = []


def check(cond, msg):
    if not cond:
        FALHAS.append(msg)


def checar_kit():
    """teste.html no Chromium: renderer 2× (3840×2160), sem tone mapping, com ambiente; renderCena determinístico;
    a oclusão (GTAO) escurece o canto parede-piso; nenhum erro de JS."""
    from render import abrir_cena, capturar, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/teste.html")
        info = pg.evaluate("(function(){var p=window.__palco;return [p.renderer.domElement.width,p.renderer.domElement.height,"
                           "p.renderer.toneMapping===0,!!p.cena.environment,p.ao.constructor.name];})()")
        check(info == [3840, 2160, True, True, "GTAOPass"], f"kit: palco {info} ≠ [3840, 2160, True, True, 'GTAOPass']")
        # a captura lê o buffer do WebGL (render.capturar), não o compositor: o 1º pg.screenshot depois de carregar saía vazio
        pg.evaluate("renderCena(3)")
        a = capturar(pg)
        pg.evaluate("renderCena(3)")
        b = capturar(pg)
        check(a == b, "kit: renderCena(3) duas vezes deu quadros diferentes (a cena não é pura em t)")
        pg.evaluate("renderCena(4)")
        check(capturar(pg) != a and len(a) > 100000, "kit: a captura não muda com t (não está lendo o render)")
        # o canto parede-piso (0; 0,05; -1,95) projetado em pixels; média de luminância 24×24 com e sem GTAO
        px = pg.evaluate("(function(){var v=new (window.__palco.THREE.Vector3)(0,.05,-1.95).project(window.__palco.camera);"
                         "return [Math.round((v.x+1)/2*1920),Math.round((1-v.y)/2*1080)];})()")
        lum = []
        for ligado in ("true", "false"):
            pg.evaluate(f"window.__palco.ao.enabled={ligado};renderCena(3)")
            lum.append(pg.evaluate(
                "(function(x,y){var c=document.createElement('canvas');c.width=24;c.height=24;var g=c.getContext('2d');"
                "var s=window.__palco.renderer.domElement;g.drawImage(s,(x-12)*2,(y-12)*2,48,48,0,0,24,24);"
                "var d=g.getImageData(0,0,24,24).data,t=0;for(var i=0;i<d.length;i+=4)t+=(d[i]+d[i+1]+d[i+2])/3;return t/(d.length/4);})"
                f"({px[0]},{px[1]})"))
        check(lum[0] <= lum[1] - 3, f"kit: o GTAO não escureceu o canto (com {lum[0]:.1f}, sem {lum[1]:.1f})")
        check(not erros, f"kit: erros de JS em teste.html: {erros}")


def ffprobe(arquivo):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(arquivo)],
                       capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def checar_render():
    """render.py com a cena de teste: 1 s → 24 quadros 1920×1080; encode web H.264 High 4.0, sem áudio;
    pontas paradas (os dois primeiros quadros iguais); o pôster é o último quadro (PSNR ≥ 40 dB)."""
    import render
    with tempfile.TemporaryDirectory() as tmp, render.servidor() as base, render.navegador() as nav:
        tmp = Path(tmp)
        pg, erros = render.abrir_cena(nav, f"{base}/cenas/teste.html")
        mestre, web, cartaz = tmp / "teste-mestre.mp4", tmp / "teste.mp4", tmp / "teste.webp"
        render.renderizar(pg, 1.0, mestre)
        render.encode_web(mestre, web, render.CRF)
        render.poster(web, 1.0, cartaz)
        info = ffprobe(web)
        v = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
        a = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
        check(len(v) == 1 and (v[0]["width"], v[0]["height"]) == (1920, 1080), f"render: vídeo {v and (v[0]['width'], v[0]['height'])} ≠ 1920×1080")
        check(v and v[0].get("nb_frames") == "24", f"render: {v and v[0].get('nb_frames')} quadros em 1 s, esperava 24")
        check(v and v[0].get("profile") == "High" and v[0].get("level") == 40, f"render: perfil {v and (v[0].get('profile'), v[0].get('level'))} ≠ High 4.0")
        check(not a, "render: o vídeo tem trilha de áudio")
        q0, q1 = tmp / "q0.png", tmp / "q1.png"
        for n, f in ((0, q0), (1, q1)):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mestre), "-vf", f"select='eq(n,{n})'", "-vframes", "1", str(f)], check=True)
        check(render.psnr(q0, q1) >= 50, "render: o início não está parado (quadros 0 e 1 diferentes)")
        check(cartaz.exists() and cartaz.stat().st_size <= render.TETO_POSTER, "render: pôster ausente ou acima do teto")
        check(not erros, f"render: erros de JS: {erros}")


DOCS = SITE / "docs"


def dims(arquivo):
    r = subprocess.run(["magick", "identify", "-format", "%w %h", str(arquivo)], capture_output=True, text=True)
    return tuple(int(x) for x in r.stdout.split()) if r.returncode == 0 else None


def checar_documentos():
    """site/docs: só o que o manifesto lista, vindo só de fontes liberadas (já anonimizadas); dimensões conferem;
    o destaque cai dentro da imagem e dentro do recorte."""
    from documentos import LIBERADOS, MANIFESTO
    man = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    check((DOCS / "destaques.json").exists(), "documentos: site/docs/destaques.json ausente (rodar documentos.py)")
    if not (DOCS / "destaques.json").exists():
        return
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))
    esperados = {f"{i}.webp" for i in man} | {f"{i}-recorte.webp" for i, d in man.items() if d.get("recorte")} | {"destaques.json"}
    achados = {p.name for p in DOCS.iterdir()}
    check(achados == esperados, f"documentos: site/docs tem {sorted(achados ^ esperados)} fora do manifesto (ou falta)")
    for i, d in man.items():
        check(d["fonte"] in LIBERADOS, f"documentos: {i} vem de {d['fonte']}, fora das fontes anonimizadas liberadas")
        x, y, w, h = d["corte"]
        check(dims(DOCS / f"{i}.webp") == (w, h), f"documentos: {i}.webp {dims(DOCS / f'{i}.webp')} ≠ corte {w}×{h}")
        check(dest.get(i, {}).get("largura") == w and dest[i].get("altura") == h, f"documentos: destaques.json de {i} sem as dimensões do corte")
        if d.get("destaque"):
            dx, dy, dw, dh = d["destaque"]
            check(0 <= dx and 0 <= dy and dx + dw <= w and dy + dh <= h, f"documentos: destaque de {i} fora da imagem")
            check(dest[i]["destaque"] == d["destaque"], f"documentos: destaques.json de {i} ≠ manifesto")
        if d.get("recorte"):
            rx, ry, rw, rh = d["recorte"]
            check(dims(DOCS / f"{i}-recorte.webp") == (rw, rh), f"documentos: recorte de {i} com dimensões erradas")
            if d.get("destaque"):
                check(rx <= dx and ry <= dy and dx + dw <= rx + rw and dy + dh <= ry + rh, f"documentos: o recorte de {i} não contém o destaque")
    check(set(man) >= {"sige-portal", "sige-fotos", "sige-rdo"}, "documentos: o caso SIGE pede sige-portal, sige-fotos e sige-rdo")


CENA_SIGE = CENAS_DIR / "caso-sige.html"


def checar_cena_estatica():
    """Estilo: nenhum texto pintado, um só acento, documentos só de ../site/docs/."""
    check(CENA_SIGE.exists(), "cena: portfolio/cenas/caso-sige.html não existe")
    if not CENA_SIGE.exists():
        return
    s = CENA_SIGE.read_text(encoding="utf-8")
    check("fillText" not in s and "strokeText" not in s, "cena sige: texto pintado (fillText/strokeText)")
    n = s.count("material('acento')")
    check(n == 1, f"cena sige: {n} usos de material('acento'), esperava 1")
    check(re.search(r"0x[Ee]0622[Aa]|ORANGE|LARANJA", s) is None, "cena sige: laranja fora de material('acento')")
    docs = set(re.findall(r"documento\('([^']+)'\)", s))
    check(docs == {"../site/docs/sige-portal.webp", "../site/docs/sige-fotos.webp", "../site/docs/sige-rdo.webp"},
          f"cena sige: documentos {sorted(docs)}")


def checar_cena_sige():
    """No Chromium: conteúdo (2 galpões, 22 divisórias, 3 painéis subindo e parados no fim), tela com o portal;
    t=0: os dois galpões inteiros no quadro, juntos ≥ 60% da largura, e antes do começo da névoa;
    t=10: os cantos da tela a ≤ 2 px de RETANGULO e o centro da tela como primeiro alvo de um raio da câmera."""
    from render import abrir_cena, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/caso-sige.html")
        conteudo = pg.evaluate("""(function(){var S=window.__cena;renderCena(10);
          return [S.galpoes.length,S.divisorias.length,S.paineisSubindo.length,
                  S.paineisSubindo.every(function(p){return Math.abs(p.rotation.x)<1e-6;}),
                  S.tela.material.map&&S.tela.material.map.image.src.split('/').pop(),
                  S.quadros.map(function(q){return q.material.map.image.src.split('/').pop();}).sort()];})()""")
        check(conteudo == [2, 22, 3, True, "sige-portal.webp", ["sige-fotos.webp", "sige-rdo.webp"]], f"cena sige: conteúdo {conteudo}")
        inicio = pg.evaluate("""(function(){var S=window.__cena,T=window.__palco.THREE,cam=window.__palco.camera,f=window.__palco.cena.fog;renderCena(0);
          var xs=[],ok=true,dmax=0;S.galpoes.forEach(function(G){var b=new T.Box3().setFromObject(G);
            [b.min.x,b.max.x].forEach(function(x){[b.min.z,b.max.z].forEach(function(z){[0,b.max.y].forEach(function(y){
              var p=new T.Vector3(x,y,z);dmax=Math.max(dmax,p.distanceTo(cam.position));p.project(cam);
              xs.push(p.x);if(Math.abs(p.x)>.95||Math.abs(p.y)>.95)ok=false;});});});});
          return [ok,Math.max.apply(null,xs)-Math.min.apply(null,xs),dmax<f.near];})()""")
        check(inicio[0], "cena sige: em t=0 algum canto dos galpões sai do quadro")
        check(inicio[1] >= 1.2, f"cena sige: em t=0 os galpões ocupam {inicio[1] / 2:.0%} da largura, esperava ≥ 60%")
        check(inicio[2], "cena sige: em t=0 parte dos galpões está dentro da névoa")
        fim = pg.evaluate("""(function(){var S=window.__cena,T=window.__palco.THREE,cam=window.__palco.camera;renderCena(10);
          S.tela.geometry.computeBoundingBox();var b=S.tela.geometry.boundingBox,cs=[];
          [[b.min.x,b.min.y],[b.max.x,b.min.y],[b.max.x,b.max.y],[b.min.x,b.max.y]].forEach(function(c){
            var p=S.tela.localToWorld(new T.Vector3(c[0],c[1],0)).project(cam);cs.push([(p.x+1)/2*1920,(1-p.y)/2*1080]);});
          var centro=S.tela.getWorldPosition(new T.Vector3()),dir=centro.clone().sub(cam.position).normalize();
          var hits=new T.Raycaster(cam.position.clone(),dir).intersectObject(window.__palco.cena,true).filter(function(h){return h.object.isMesh;});
          return [cs,hits.length>0&&hits[0].object===S.tela];})()""")
        alvo = [[384, 180], [1536, 180], [1536, 900], [384, 900]]  # RETANGULO em 1920×1080, cantos em sentido horário a partir do sup. esq.
        achados = sorted(fim[0], key=lambda c: (round(c[1] / 100), c[0]))
        esperado = sorted(alvo, key=lambda c: (round(c[1] / 100), c[0]))
        erro = max(max(abs(a[0] - e[0]), abs(a[1] - e[1])) for a, e in zip(achados, esperado))
        check(erro <= 2, f"cena sige: cantos da tela a {erro:.1f} px de RETANGULO no último quadro (máx. 2 px): {achados}")
        check(fim[1], "cena sige: no último quadro algo fica entre a câmera e o centro da tela")
        check(not erros, f"cena sige: erros de JS: {erros}")


def checar_passagem():
    """A passagem vídeo → imagem real é invisível: no último quadro, a região de RETANGULO, levada a 1600×1000,
    tem PSNR ≥ 28 dB contra site/docs/sige-portal.webp."""
    from render import abrir_cena, capturar, navegador, psnr, servidor
    with tempfile.TemporaryDirectory() as tmp, servidor() as base, navegador() as nav:
        tmp = Path(tmp)
        pg, _ = abrir_cena(nav, f"{base}/cenas/caso-sige.html")
        pg.evaluate("renderCena(10)")
        quadro = tmp / "fim.png"
        quadro.write_bytes(capturar(pg))
        regiao = tmp / "regiao.png"
        subprocess.run(["magick", str(quadro), "-crop", "1152x720+384+180", "+repage", "-resize", "1600x1000!", str(regiao)], check=True)
        doc = tmp / "doc.png"
        subprocess.run(["magick", str(DOCS / "sige-portal.webp"), str(doc)], check=True)
        valor = psnr(regiao, doc)
        check(valor >= 28, f"passagem: PSNR {valor:.1f} dB entre a tela do último quadro e o documento real (mín. 28)")


def main():
    checar_documentos()
    checar_cena_estatica()
    if "--navegador" in sys.argv:
        checar_kit()
        checar_render()
        checar_cena_sige()
        checar_passagem()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
