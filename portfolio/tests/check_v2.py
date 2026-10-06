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
        asfalto = pg.evaluate("(function(){try{var m=window.__kit.material('asfalto');return [m.map&&m.map.isTexture,m.roughness];}catch(e){return String(e);}})()")
        check(asfalto == [True, 1], f"kit: material('asfalto') {asfalto}")
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
    check(set(man) >= {"sige-portal", "sige-fotos", "sige-rdo", "veks-orcamento", "veks-levantamento", "veks-planta-cliente", "veks-proposta-pagina", "veks-proposta-modelo", "b36-caixas", "b36-transporte", "b36-ata", "veks-proposta"},
          f"documentos: faltam ids no manifesto: {sorted({'sige-portal', 'sige-fotos', 'sige-rdo', 'veks-orcamento', 'veks-levantamento', 'veks-planta-cliente', 'veks-proposta-pagina', 'veks-proposta-modelo', 'b36-caixas', 'b36-transporte', 'b36-ata', 'veks-proposta'} - set(man))}")
    for i, d in man.items():
        f = d["fonte"]
        check(f.startswith(("zip:", "pdf:")) or (RAIZ / f).exists(), f"documentos: fonte de {i} não existe: {f}")
        if f.startswith("zip:") or f.startswith("pdf:"):
            check("!" in f and Path(f.split(":", 1)[1].split("!")[0]).suffix == ".zip", f"documentos: fonte {f!r} de {i} não é zip:<arquivo.zip>!<membro>")
        if f.startswith("pdf:"):
            check(re.search(r"#\d+$", f) is not None, f"documentos: fonte pdf de {i} sem #página")


CENAS_HTML = {"abertura.html": {"veks-proposta", "veks-orcamento", "sige-portal", "b36-caixas"},
              "caso-orcamento.html": {"veks-levantamento", "veks-orcamento", "veks-planta-cliente", "veks-proposta-pagina", "veks-proposta-modelo"},
              "caso-sige.html": {"sige-portal", "sige-fotos", "sige-rdo"},
              "caso-modulares.html": {"b36-caixas", "b36-transporte", "b36-ata"}}


def checar_cena_estatica():
    """Estilo de cada cena: nenhum texto pintado, um só acento, documentos só de ../site/docs/ (os previstos)."""
    for arquivo, docs_esperados in CENAS_HTML.items():
        cena = CENAS_DIR / arquivo
        check(cena.exists(), f"cena: portfolio/cenas/{arquivo} não existe")
        if not cena.exists():
            continue
        s = cena.read_text(encoding="utf-8")
        check("fillText" not in s and "strokeText" not in s, f"cena {arquivo}: texto pintado (fillText/strokeText)")
        n = s.count("material('acento')")
        check(n == 1, f"cena {arquivo}: {n} usos de material('acento'), esperava 1")
        check(re.search(r"0x[Ee]0622[Aa]|ORANGE|LARANJA", s) is None, f"cena {arquivo}: laranja fora de material('acento')")
        docs = set(re.findall(r"documento\('\.\./site/docs/([a-z0-9-]+)\.webp'\)", s))
        check(docs == docs_esperados, f"cena {arquivo}: documentos {sorted(docs)}, esperava {sorted(docs_esperados)}")
        check('<link rel="icon" href="data:,">' in s, f"cena {arquivo}: sem o ícone inerte (o 404 de /favicon.ico vira erro de console)")


CASOS = {
    "veks": {"cena": "caso-orcamento.html", "doc": "veks-proposta-modelo", "dur": 10},
    "sige": {"cena": "caso-sige.html", "doc": "sige-portal", "dur": 10},
    "modulares": {"cena": "caso-modulares.html", "doc": "b36-caixas", "dur": 12},
}
ALVO = [[384, 180], [1536, 180], [1536, 900], [384, 900]]  # RETANGULO em 1920×1080, cantos a partir do sup. esq.


def inicio_da_cena(pg, js_assunto):
    """t=0: [todos os cantos das caixas do assunto dentro de ±0,95; largura projetada (0..2); tudo antes da névoa]."""
    return pg.evaluate("""(function(){var T=window.__palco.THREE,cam=window.__palco.camera,f=window.__palco.cena.fog;renderCena(0);
      var xs=[],ok=true,dmax=0;(""" + js_assunto + """).forEach(function(G){var b=new T.Box3().setFromObject(G);
        [b.min.x,b.max.x].forEach(function(x){[b.min.z,b.max.z].forEach(function(z){[b.min.y,b.max.y].forEach(function(y){
          var p=new T.Vector3(x,y,z);dmax=Math.max(dmax,p.distanceTo(cam.position));p.project(cam);
          xs.push(p.x);if(Math.abs(p.x)>.95||Math.abs(p.y)>.95)ok=false;});});});});
      return [ok,Math.max.apply(null,xs)-Math.min.apply(null,xs),!f||dmax<f.near];})()""")


def enquadramento_final(pg):
    """t=10: [cantos do alvo em px 1920×1080, o alvo é o primeiro Mesh atingido por um raio da câmera ao seu centro]."""
    return pg.evaluate("""(function(){var S=window.__cena,T=window.__palco.THREE,cam=window.__palco.camera;renderCena(10);
      S.alvo.geometry.computeBoundingBox();var b=S.alvo.geometry.boundingBox,cs=[];
      [[b.min.x,b.min.y],[b.max.x,b.min.y],[b.max.x,b.max.y],[b.min.x,b.max.y]].forEach(function(c){
        var p=S.alvo.localToWorld(new T.Vector3(c[0],c[1],0)).project(cam);cs.push([(p.x+1)/2*1920,(1-p.y)/2*1080]);});
      var centro=S.alvo.getWorldPosition(new T.Vector3()),dir=centro.clone().sub(cam.position).normalize();
      var hits=new T.Raycaster(cam.position.clone(),dir).intersectObject(window.__palco.cena,true).filter(function(h){return h.object.isMesh;});
      return [cs,hits.length>0&&hits[0].object===S.alvo];})()""")


def checar_enquadramento(pg, nome):
    fim = enquadramento_final(pg)
    achados = sorted(fim[0], key=lambda c: (round(c[1] / 100), c[0]))
    esperado = sorted(ALVO, key=lambda c: (round(c[1] / 100), c[0]))
    erro = max(max(abs(a[0] - e[0]), abs(a[1] - e[1])) for a, e in zip(achados, esperado))
    check(erro <= 2, f"{nome}: cantos do alvo a {erro:.1f} px de RETANGULO no último quadro (máx. 2 px): {achados}")
    check(fim[1], f"{nome}: no último quadro algo fica entre a câmera e o centro do alvo")


def checar_proporcao_alvo(pg, doc, nome):
    """O plano-alvo tem a proporção exata do corte do documento (senão a imagem real entra esticada)."""
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))[doc]
    prop = pg.evaluate("(function(){var p=window.__cena.alvo.geometry.parameters;return p.width/p.height;})()")
    esperado = dest["largura"] / dest["altura"]
    check(abs(prop / esperado - 1) <= .005, f"{nome}: alvo com proporção {prop:.4f}, o corte de {doc} tem {esperado:.4f}")


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
                  S.quadros.map(function(q){return q.material.map.image.src.split('/').pop();}).sort(), S.alvo===S.tela];})()""")
        check(conteudo == [2, 22, 3, True, "sige-portal.webp", ["sige-fotos.webp", "sige-rdo.webp"], True], f"cena sige: conteúdo {conteudo}")
        inicio = inicio_da_cena(pg, "window.__cena.galpoes")
        check(inicio[0], "cena sige: em t=0 algum canto dos galpões sai do quadro")
        check(inicio[1] >= 1.2, f"cena sige: em t=0 os galpões ocupam {inicio[1] / 2:.0%} da largura, esperava ≥ 60%")
        check(inicio[2], "cena sige: em t=0 parte dos galpões está dentro da névoa")
        checar_enquadramento(pg, "cena sige")
        checar_proporcao_alvo(pg, "sige-portal", "cena sige")
        check(not erros, f"cena sige: erros de JS: {erros}")


def checar_cena_abertura():
    """A mesa: quatro documentos reais; t=0 a mesa inteira, ≥ 60% da largura; t 0,5→2,5 a proposta desliza e para;
    t=10 os quatro documentos inteiros no quadro, cada um com ≥ 12% da largura."""
    from render import abrir_cena, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/abertura.html")
        nomes = pg.evaluate("(function(){var S=window.__cena;renderCena(10);return [S.docs.map(function(d){return d.material.map&&d.material.map.image.src.split('/').pop();}).sort(),S.alvo===null,S.assunto.length];})()")
        check(nomes == [["b36-caixas.webp", "sige-portal.webp", "veks-orcamento.webp", "veks-proposta.webp"], True, 1], f"cena abertura: {nomes}")
        inicio = inicio_da_cena(pg, "window.__cena.assunto")
        check(inicio[0], "cena abertura: em t=0 a mesa sai do quadro")
        check(inicio[1] >= 1.2, f"cena abertura: em t=0 a mesa ocupa {inicio[1] / 2:.0%} da largura, esperava ≥ 60%")
        check(inicio[2], "cena abertura: em t=0 a mesa está dentro da névoa")
        pos = pg.evaluate("(function(){var S=window.__cena,r=[];[0,2.5,10].forEach(function(t){renderCena(t);r.push(S.proposta.position.x.toFixed(3));});return r;})()")
        check(pos[0] != pos[1] and pos[1] == pos[2], f"cena abertura: a proposta não desliza e para (x em t=0, 2,5 e 10: {pos})")
        fim = pg.evaluate("""(function(){var S=window.__cena,T=window.__palco.THREE,cam=window.__palco.camera;renderCena(10);
          return S.docs.map(function(d){d.geometry.computeBoundingBox();var b=d.geometry.boundingBox,xs=[],ok=true;
            [[b.min.x,b.min.y],[b.max.x,b.min.y],[b.max.x,b.max.y],[b.min.x,b.max.y]].forEach(function(c){
              var p=d.localToWorld(new T.Vector3(c[0],c[1],0)).project(cam);xs.push(p.x);if(Math.abs(p.x)>.95||Math.abs(p.y)>.95)ok=false;});
            return [ok,(Math.max.apply(null,xs)-Math.min.apply(null,xs))/2];});})()""")
        for i, (ok, larg) in enumerate(fim):
            check(ok, f"cena abertura: em t=10 o documento {i} sai do quadro")
            check(larg >= .12, f"cena abertura: em t=10 o documento {i} tem {larg:.0%} da largura (mín. 12%)")
        check(not erros, f"cena abertura: erros de JS: {erros}")


def checar_cena_veks():
    """Da planta à proposta: a planta do cliente sobre a mesa, o monitor com o levantamento e depois o orçamento, as paredes
    se levantam da planta (nenhuma em t=0, algumas em t=2,5, todas em t=5), a proposta sai da impressora (dentro em t=6,
    em repouso na bandeja em t=10) e a faixa da página é o alvo; t=0: planta e monitor inteiros e ≥ 60% da largura;
    t=10: a faixa exatamente em RETANGULO."""
    from render import abrir_cena, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/caso-orcamento.html")
        conteudo = pg.evaluate("""(function(){var S=window.__cena;renderCena(10);var p=S.proposta.position,r=S.repouso.proposta;
          return [S.alvo.parent===S.folha,S.alvo.material.map&&S.alvo.material.map.image.src.split('/').pop(),
                  S.tela.material.map&&S.tela.material.map.image.src.split('/').pop(),S.docs.slice().sort(),S.assunto.length,
                  Math.hypot(p.x-r[0],p.y-r[1],p.z-r[2])<1e-3,S.estado.erguidas===S.estado.n&&S.estado.n>300];})()""")
        check(conteudo == [True, "veks-proposta-modelo.webp", "veks-orcamento.webp",
                           ["veks-levantamento.webp", "veks-orcamento.webp", "veks-planta-cliente.webp", "veks-proposta-modelo.webp", "veks-proposta-pagina.webp"],
                           2, True, True], f"cena veks: conteúdo em t=10 {conteudo}")
        meio = pg.evaluate("""(function(){var S=window.__cena,r=[];[0,2.5,5,6].forEach(function(t){renderCena(t);
          r.push([S.estado.erguidas,S.tela.material.map&&S.tela.material.map.image.src.split('/').pop(),+S.proposta.position.z.toFixed(3)]);});return r;})()""")
        check(meio[0][0] == 0 and 0 < meio[1][0] < meio[3][0] == meio[2][0], f"cena veks: paredes erguidas em t=0, 2,5, 5, 6: {[m[0] for m in meio]} (esperava 0, algumas, todas, todas)")
        check(meio[1][1] == "veks-levantamento.webp" and meio[2][1] == "veks-orcamento.webp", f"cena veks: telas do monitor em t=2,5 e 5: {meio[1][1]}, {meio[2][1]}")
        check(meio[3][2] < -.1, f"cena veks: em t=6 a proposta já saiu da impressora (z {meio[3][2]})")
        inicio = inicio_da_cena(pg, "window.__cena.assunto")
        check(inicio[0], "cena veks: em t=0 a planta ou o monitor saem do quadro")
        check(inicio[1] >= 1.2, f"cena veks: em t=0 a estação ocupa {inicio[1] / 2:.0%} da largura, esperava ≥ 60%")
        check(inicio[2], "cena veks: em t=0 parte da estação está dentro da névoa")
        checar_enquadramento(pg, "cena veks")
        checar_proporcao_alvo(pg, "veks-proposta-modelo", "cena veks")
        check(not erros, f"cena veks: erros de JS: {erros}")


def checar_cena_modulares():
    """O B-36: 2 caixas, o caminhão chega, o guindaste iça a caixa 1 até a fundação e depois monta o telhado peça a peça
    a partir da pilha do kit (6 peças: 2 frontões e 4 águas); a prancha no cavalete é o alvo; t=0: caixa 2 e guindaste
    inteiros e ≥ 60% da largura, nenhuma peça montada e a pilha no chão; t=6,4: montagem a meio, o gancho sobre a peça
    que está no ar; t=10 tudo em repouso, as 6 peças no pose final, e a prancha em RETANGULO."""
    from render import abrir_cena, navegador, servidor
    with servidor() as base, navegador() as nav:
        pg, erros = abrir_cena(nav, f"{base}/cenas/caso-modulares.html")
        fim = pg.evaluate("""(function(){var S=window.__cena;renderCena(10);var c=S.caixas[0].position,r=S.repouso;
          return [S.caixas.length,S.alvo===S.prancha,S.docs.slice().sort(),
                  Math.hypot(c.x-r.caixa1[0],c.y-r.caixa1[1],c.z-r.caixa1[2])<1e-3, Math.abs(S.telhado.position.y-r.telhado)<1e-3,
                  Math.abs(S.caminhao.position.z)<1e-3, S.pecas.length,
                  S.pecas.every(function(p){return p.userData.montada&&p.position.distanceTo(p.userData.fim.p)<1e-3&&p.quaternion.angleTo(p.userData.fim.q)<1e-3;})];})()""")
        check(fim == [2, True, ["b36-ata.webp", "b36-caixas.webp", "b36-transporte.webp"], True, True, True, 6, True], f"cena modulares: fim {fim}")
        meio = pg.evaluate("""(function(){var S=window.__cena,r=[],T=window.__cena.telhado;[0,2,4.2,6.4].forEach(function(t){renderCena(t);
          var montadas=S.pecas.filter(function(p){return p.userData.montada;}).length;
          var noAr=S.pecas.filter(function(p){return !p.userData.montada&&p.position.distanceTo(p.userData.ini.p)>1e-3;});
          var alturas=S.pecas.map(function(p){return T.localToWorld(p.position.clone()).y;});
          var g=S.guindaste.gancho.position,d=noAr.length?T.localToWorld(noAr[0].position.clone()).distanceTo(g):null;
          r.push([S.caminhao.position.z.toFixed(1),S.caixas[0].position.y.toFixed(2),montadas,noAr.length,Math.max.apply(null,alturas),d]);});return r;})()""")
        check(float(meio[0][0]) < -30 and float(meio[1][0]) < 0 and float(meio[2][0]) == 0, f"cena modulares: o caminhão não entra (z em t=0, 2, 4,2: {[m[0] for m in meio]})")
        check(float(meio[2][1]) > 4, f"cena modulares: em t=4,2 a caixa 1 não está no ar (y {meio[2][1]})")
        check(meio[0][2] == 0 and meio[0][3] == 0 and meio[0][4] < 1.5, f"cena modulares: em t=0 o telhado não está todo na pilha, no chão (montadas {meio[0][2]}, no ar {meio[0][3]}, topo {meio[0][4]:.2f} m)")
        check(1 <= meio[3][2] <= 5 and meio[3][3] == 1, f"cena modulares: em t=6,4 a montagem não está a meio (montadas {meio[3][2]}, no ar {meio[3][3]})")
        check(meio[3][5] is not None and meio[3][5] < 1.6, f"cena modulares: em t=6,4 o gancho não está sobre a peça no ar ({meio[3][5]} m)")
        inicio = inicio_da_cena(pg, "window.__cena.assunto")
        check(inicio[0], "cena modulares: em t=0 a caixa 2 ou o guindaste saem do quadro")
        check(inicio[1] >= 1.2, f"cena modulares: em t=0 o assunto ocupa {inicio[1] / 2:.0%} da largura, esperava ≥ 60%")
        check(inicio[2], "cena modulares: em t=0 parte do assunto está dentro da névoa")
        checar_enquadramento(pg, "cena modulares")
        checar_proporcao_alvo(pg, "b36-caixas", "cena modulares")
        check(not erros, f"cena modulares: erros de JS: {erros}")


def checar_passagem(caso):
    """A passagem vídeo → imagem real é invisível: no último quadro, a região de RETANGULO, levada ao tamanho do corte,
    tem PSNR ≥ 28 dB contra site/docs/<doc>.webp."""
    from render import abrir_cena, capturar, navegador, psnr, servidor
    c = CASOS[caso]
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))[c["doc"]]
    with tempfile.TemporaryDirectory() as tmp, servidor() as base, navegador() as nav:
        tmp = Path(tmp)
        pg, _ = abrir_cena(nav, f"{base}/cenas/{c['cena']}")
        pg.evaluate("renderCena(10)")
        quadro = tmp / "fim.png"
        quadro.write_bytes(capturar(pg))
        regiao = tmp / "regiao.png"
        subprocess.run(["magick", str(quadro), "-crop", "1152x720+384+180", "+repage", "-resize", f"{dest['largura']}x{dest['altura']}!", str(regiao)], check=True)
        doc = tmp / "doc.png"
        subprocess.run(["magick", str(DOCS / f"{c['doc']}.webp"), str(doc)], check=True)
        valor = psnr(regiao, doc)
        check(valor >= 28, f"passagem {caso}: PSNR {valor:.1f} dB entre o alvo do último quadro e o documento real (mín. 28)")


def checar_video():
    """Vídeo publicado de cada caso de CENAS: 1920×1080, 24 fps, High 4.0, sem áudio, quadros = dur × 24, ≤ 2,5 MB;
    pontas paradas (PSNR ≥ 45 dB entre os dois primeiros e entre os dois últimos quadros); pôster ≤ 150 KB e
    PSNR ≥ 40 dB contra o último quadro."""
    import render
    for caso, (_arq, dur) in render.CENAS.items():
        mp4, cartaz = SITE / "video" / f"v2-{caso}.mp4", SITE / "video" / f"v2-{caso}.webp"
        check(mp4.exists() and cartaz.exists(), f"vídeo {caso}: v2-{caso}.mp4/.webp ausentes (rodar render.py --so {caso})")
        if not (mp4.exists() and cartaz.exists()):
            continue
        info = ffprobe(mp4)
        v = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
        check(not [s for s in info.get("streams", []) if s.get("codec_type") == "audio"], f"vídeo {caso}: tem áudio")
        check(v and (v[0]["width"], v[0]["height"], v[0].get("r_frame_rate"), v[0].get("profile"), v[0].get("level")) == (1920, 1080, "24/1", "High", 40),
              f"vídeo {caso}: {v and (v[0]['width'], v[0]['height'], v[0].get('r_frame_rate'), v[0].get('profile'), v[0].get('level'))}")
        n = render.quadros(dur)
        check(v and v[0].get("nb_frames") == str(n), f"vídeo {caso}: {v and v[0].get('nb_frames')} quadros, esperava {n}")
        check(mp4.stat().st_size <= render.TETO_CLIPE, f"vídeo {caso}: {mp4.stat().st_size / 1024 / 1024:.2f} MB > 2,5 MB")
        check(cartaz.stat().st_size <= render.TETO_POSTER, f"vídeo {caso}: pôster {cartaz.stat().st_size // 1024} KB > 150 KB")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            q = {}
            for k in (0, 1, n - 2, n - 1):
                q[k] = tmp / f"q{k}.png"
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", f"select='eq(n,{k})'", "-vframes", "1", str(q[k])], check=True)
            check(render.psnr(q[0], q[1]) >= 45, f"vídeo {caso}: o início não está parado")
            check(render.psnr(q[n - 2], q[n - 1]) >= 45, f"vídeo {caso}: o fim não está parado")
            check(render.psnr(cartaz, q[n - 1]) >= 40, f"vídeo {caso}: o pôster não é o último quadro (PSNR < 40 dB)")


PAGINA = SITE / "index.html"
PROIBIDOS = ["27×", "≈ 27", "≈27", "2 dias úteis", "dois dias úteis", "Kabod", "Santa Mônica", "UPA", "Bertioga", "203.1809",
             "número não sumir", "Não falta obra feita", "número sem origem"]
RETANGULO_CSS = "left:20%;top:16.6667%;width:60%;height:66.6667%"


def texto_visivel(html_):
    import html as h
    html_ = re.sub(r"<(script|style)\b.*?</\1>", " ", html_, flags=re.S)
    return " ".join(h.unescape(re.sub(r"<[^>]+>", " ", html_)).split())


def checar_pagina_estatica():
    """v2.html: textos aprovados; regras de texto (§5); proibidos; documentos com width/height reais; .doc em RETANGULO;
    destaque em % igual ao destaques.json; figure.clipe apontando para o vídeo publicado com a duração de CENAS."""
    import render
    check(PAGINA.exists(), "página: portfolio/site/index.html não existe")
    if not PAGINA.exists():
        return
    p = PAGINA.read_text(encoding="utf-8")
    vis = texto_visivel(p)
    check("Orço obras, acompanho a execução e construí os sistemas que uso para isso." in vis, "página: frase da abertura ausente")
    TEXTOS = {
        "veks": ("Orcei diversas obras: propostas de R$ 29 mil a 24,5 milhões.",
                 "Comparei as composições calculadas pelo sistema com as do SINAPI, serviço a serviço: nos 19 serviços conferidos, a maior diferença foi de 0,25%."),
        "sige": ("Implantei a gestão de obra em dois galpões com 22 baias.",
                 "Construí o cronograma ligado ao diário de obra (RDO) e ao portal do cliente: 109 etapas, 65 diários e 378 fotos num link que o cliente pode acessar."),
        "modulares": ("Projetei casas modulares para chegar à obra em 3 caminhões.",
                      "Duas caixas de 3,00 × 6,00 m e o telhado em kit, uma carga por caminhão. Também orcei e fiz a proposta."),
    }
    # o caso 1 do spec (36 minutos) não tem cena própria: os prints originais não vêm e os de 760 px não podem ser ampliados.
    # O número entra no caso do orçamento, cujo documento é a proposta feita nesses 36 minutos.
    MEDIDAS = {"veks": "Esta proposta (ampliação de 328 m², 26 ambientes) saiu em 36 minutos, medidos do primeiro arquivo aberto ao PDF. À mão, cerca de 1 dia útil (estimativa)."}
    LINKS = {"veks": ["sistema", "orcamento"], "sige": ["sige"], "modulares": ["modular"]}
    portfolio = (SITE / "portfolio.html").read_text(encoding="utf-8")
    secoes = re.findall(r'<section class="caso cena" id="([a-z]+)" data-caso="\1">(.*?)</section>', p, re.S)
    check([s[0] for s in secoes] == list(CASOS), f"página: casos {[s[0] for s in secoes]}, esperava {list(CASOS)} nessa ordem")
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))
    for caso, corpo in secoes:
        m = re.findall(r'<h2 class="manchete"[^>]*>(.*?)</h2>', corpo, re.S)
        a = re.findall(r'<p class="apoio"[^>]*>(.*?)</p>', corpo, re.S)
        check(len(m) == 1 and texto_visivel(m[0]) == TEXTOS[caso][0], f"página {caso}: manchete {m and texto_visivel(m[0])!r}")
        check(len(a) == 1 and texto_visivel(a[0]) == TEXTOS[caso][1], f"página {caso}: apoio {a and texto_visivel(a[0])!r}")
        for t in m:
            t = texto_visivel(t)
            check(len(t.split()) <= 12 and re.search(r"\d", t), f"página {caso}: manchete fora da regra (≤ 12 palavras, com número): {t!r}")
        for t in a:
            check(len(texto_visivel(t).split()) <= 30, f"página {caso}: apoio com {len(texto_visivel(t).split())} palavras (máx. 30)")
        md = [texto_visivel(t) for t in re.findall(r'<p class="medida"[^>]*>(.*?)</p>', corpo, re.S)]
        check(md == ([MEDIDAS[caso]] if caso in MEDIDAS else []), f"página {caso}: linha da medida {md!r}")
        for t in md:
            check(len(t.split()) <= 30 and "(estimativa)" in t, f"página {caso}: medida fora da regra (≤ 30 palavras, com a ressalva da estimativa): {t!r}")
        doc = CASOS[caso]["doc"]
        d = dest[doc]
        x, y, w, h = d["destaque"]
        esperado = f"left:{x / d['largura']:.4%};top:{y / d['altura']:.4%};width:{w / d['largura']:.4%};height:{h / d['altura']:.4%}"
        check(f'class="doc" style="{RETANGULO_CSS}"' in corpo, f"página {caso}: .doc fora de RETANGULO")
        check(f'<img src="docs/{doc}.webp" width="{d["largura"]}" height="{d["altura"]}"' in corpo, f"página {caso}: img do documento {doc} com src/width/height errados")
        check(f'class="destaque" style="{esperado}"' in corpo, f"página {caso}: destaque ≠ destaques.json (esperava style=\"{esperado}\")")
        rx, ry, rw, rh = d["recorte"]
        check(f'<img src="docs/{doc}-recorte.webp" width="{rw}" height="{rh}"' in corpo, f"página {caso}: recorte de {doc} com src/width/height errados")
        check(f'<figure class="clipe" data-clipe="video/v2-{caso}.mp4" data-clipe-hd="video/v2-{caso}-hd.mp4" data-dur="{CASOS[caso]["dur"]:g}" aria-hidden="true">' in corpo, f"página {caso}: figure.clipe")
        elo = re.search(r'<p class="caso-link">(.*?)</p>', corpo, re.S)
        alvos = re.findall(r'<a href="portfolio\.html#([a-z-]+)">', elo.group(1)) if elo else []
        check(alvos == LINKS[caso], f"página {caso}: links do caso completo {alvos}, esperava {LINKS[caso]}")
        for alvo in alvos:
            check(f'id="{alvo}"' in portfolio, f"página {caso}: link do caso completo sem âncora existente em portfolio.html (#{alvo})")
    for proibido in PROIBIDOS:
        check(proibido not in vis, f"página: texto proibido {proibido!r}")
    check(re.search(r"\bItu\b", vis) is None, "página: nome do município do cliente (Itu)")
    for src, w, h in re.findall(r'<img src="(docs/[^"]+)" width="(\d+)" height="(\d+)"', p):
        check(dims(SITE / src) == (int(w), int(h)), f"página: {src} com width/height {w}×{h} ≠ arquivo {dims(SITE / src)}")
    check('<section class="caso cena so-cena" id="mesa" data-caso="mesa">' in p and '<figure class="clipe" data-clipe="video/v2-abertura.mp4" data-clipe-hd="video/v2-abertura-hd.mp4" data-dur="8" aria-hidden="true">' in p, "página: a cena da abertura (#mesa, só cena, 8 s)")
    check('<img src="video/v2-abertura.webp" alt="" width="1920" height="1080" fetchpriority="high">' in p, "página: o pôster da abertura é o LCP (width/height/fetchpriority)")
    trilho = re.search(r'<nav class="trilho" aria-label="Seções">(.*?)</nav>', p, re.S)
    hrefs = re.findall(r'href="#([a-z]+)"', trilho.group(1)) if trilho else []
    check(hrefs == ["inicio", "veks", "sige", "modulares", "trajetoria", "contato"], f"página: trilho {hrefs}")
    for h in hrefs:
        check(f'id="{h}"' in p, f"página: âncora do trilho sem alvo: #{h}")
    faixa = re.search(r'<ol class="faixa">(.*?)</ol>', p, re.S)
    itens = [texto_visivel(li) for li in re.findall(r"<li>(.*?)</li>", faixa.group(1), re.S)] if faixa else []
    check(len(itens) == 4 and [it.split(" ")[0] for it in itens] == ["2017", "2020", "fev/2025", "mar"], f"página: trajetória {itens}")
    for nome in ("AZ Contabilidade", "UNIFEI", "InLoco Jr.", "V Alves", "Estruturas do Vale", "VEKS"):
        check(nome in " ".join(itens), f"página: trajetória sem {nome!r}")
    check("calculadora de parede" not in vis and "classificador de fluxo de caixa" not in vis, "página: a linha das ferramentas saiu da trajetória")
    check('<script src="clipes.js?v=' in p and '<script src="v2.js?v=' in p, "página: scripts clipes.js e v2.js")


def abrir_pagina(nav, base, largura, altura, **kw):
    ctx = nav.new_context(viewport={"width": largura, "height": altura}, **kw)
    pg = ctx.new_page()
    erros = []
    pg.on("pageerror", lambda e: erros.append(str(e)))
    pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)
    pg.on("response", lambda r: erros.append(f"{r.status} {r.url}") if r.status >= 400 else None)
    pg.goto(f"{base}/site/index.html")
    pg.wait_for_load_state("load")
    return ctx, pg, erros


def rolar(pg, caso, p):
    """Rola até o progresso p (0..1) do caso, espera o progresso suavizado do v2.js (c.__p) chegar lá e mais dois quadros."""
    pg.evaluate(f"""(function(){{var c=document.getElementById('{caso}'),r=c.getBoundingClientRect();
      scrollTo(0,scrollY+r.top+{p}*(c.offsetHeight-innerHeight));}})()""")
    pg.wait_for_function(f"""(function(){{var c=document.getElementById('{caso}'),curso=c.offsetHeight-innerHeight;
      var alvo=curso>0?Math.max(0,Math.min(1,-c.getBoundingClientRect().top/curso)):1;
      return c.__p===undefined||c.__p===alvo;}})()""", timeout=5000)
    pg.evaluate("new Promise(function(r){requestAnimationFrame(function(){requestAnimationFrame(r);});})")


def caixas(pg, caso):
    return pg.evaluate(f"""(function(){{var c=document.getElementById('{caso}'),f=function(s){{var e=c.querySelector(s);if(!e)return null;
      var r=e.getBoundingClientRect();return [r.left,r.top,r.width,r.height,getComputedStyle(e).opacity,getComputedStyle(e).display];}};
      return {{quadro:f('.quadro'),doc:f('.doc'),dest:f('.destaque'),texto:f('.texto'),recorte:f('.recorte img'),img:f('.doc img')}};}})()""")


def checar_alinhado(b, nome):
    """O .doc ocupa RETANGULO do .quadro (as duas caixas já incluem o transform): ±1,5 px em cada lado."""
    q, d = b["quadro"], b["doc"]
    ref = [q[0] + .2 * q[2], q[1] + q[3] / 6, .6 * q[2], 2 * q[3] / 3]
    for nome_eixo, achado, esperado in zip(("left", "top", "width", "height"), d[:4], ref):
        check(abs(achado - esperado) <= 1.5, f"{nome}: .doc fora de RETANGULO em {nome_eixo} ({achado:.1f} ≠ {esperado:.1f})")


def checar_texto_fora_do_quadro(b, nome):
    """Em p=1 o texto fica à direita do quadro inteiro (não só do documento): ≥ 16 px de folga e inteiro na tela."""
    q, t = b["quadro"], b["texto"]
    check(t[0] >= q[0] + q[2] + 16, f"{nome}: o texto invade o quadro do vídeo ({q[0] + q[2] - t[0]:.0f} px)")


def checar_pagina():
    """1920×1080 com Range, em cada caso: sem erros nem 404; em p=0,25 o vídeo busca o quadro do meio e mostra quadro
    (.viva); em p=0,25 o documento está invisível; em p=1 o documento, o destaque e o texto estão visíveis, o documento em
    RETANGULO, o destaque dentro do documento, a imagem real nunca ampliada, e o texto não cobre o documento."""
    from render import navegador, servidor
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))
    with servidor() as base, navegador() as nav:
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080)
        check(pg.evaluate("document.documentElement.classList.contains('js-v2')"), "página: v2.js não ligou .js-v2")
        for caso in CASOS:
            rolar(pg, caso, .25)
            pg.wait_for_function(f"document.querySelector('#{caso} figure.clipe').classList.contains('viva')", timeout=20000)
            t = pg.evaluate(f"document.querySelector('#{caso} video').currentTime")
            meio = CASOS[caso]["dur"] / 2 + 1 / 48
            check(abs(t - meio) < .05, f"página {caso}: em p=0,25 o vídeo está em {t:.3f} s, esperava {meio:.3f} s")
            b = caixas(pg, caso)
            check(float(b["doc"][4]) == 0, f"página {caso}: em p=0,25 o documento já aparece (opacidade {b['doc'][4]})")
            vis = pg.evaluate(f"getComputedStyle(document.querySelector('#{caso} .texto')).visibility")
            check(vis == "hidden", f"página {caso}: em p=0,25 o texto invisível ainda recebe foco (visibility {vis}, esperava hidden)")
            rolar(pg, caso, 1)
            b = caixas(pg, caso)
            check(float(b["doc"][4]) == 1 and float(b["dest"][4]) == 1 and float(b["texto"][4]) == 1, f"página {caso}: em p=1 opacidades {b['doc'][4]}, {b['dest'][4]}, {b['texto'][4]}")
            vis = pg.evaluate(f"getComputedStyle(document.querySelector('#{caso} .texto')).visibility")
            check(vis == "visible", f"página {caso}: em p=1 o texto está com visibility {vis}")
            checar_alinhado(b, f"página {caso} 1920×1080")
            d, s = b["doc"], b["dest"]
            check(d[0] <= s[0] and d[1] <= s[1] and s[0] + s[2] <= d[0] + d[2] and s[1] + s[3] <= d[1] + d[3], f"página {caso}: destaque fora do documento")
            larg = dest[CASOS[caso]["doc"]]["largura"]
            check(b["img"][2] <= larg, f"página {caso}: documento exibido com {b['img'][2]:.0f} px, acima dos {larg} px do arquivo (ampliado)")
            check(b["texto"][0] >= d[0] + d[2] + 16, f"página {caso}: o texto cobre o documento em 1920×1080")
            checar_texto_fora_do_quadro(b, f"página {caso} 1920×1080")
        check(not erros, f"página: erros/404: {erros}")
        ctx.close()


def checar_viewports():
    """Viewports fora de 16:9, em cada caso: documento em RETANGULO, inteiro na tela, texto sem cobrir o documento, em p=1."""
    from render import navegador, servidor
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))
    with servidor() as base, navegador() as nav:
        for w, h in ((1366, 768), (2560, 1080), (1280, 1024)):
            ctx, pg, erros = abrir_pagina(nav, base, w, h)
            for caso in CASOS:
                rolar(pg, caso, 1)
                b = caixas(pg, caso)
                checar_alinhado(b, f"página {caso} {w}×{h}")
                d = b["doc"]
                check(d[0] >= 0 and d[1] >= 0 and d[0] + d[2] <= w and d[1] + d[3] <= h, f"página {caso} {w}×{h}: documento sai da tela {d[:4]}")
                check(b["texto"][0] >= d[0] + d[2] + 16, f"página {caso} {w}×{h}: o texto cobre o documento")
                checar_texto_fora_do_quadro(b, f"página {caso} {w}×{h}")
                check(b["img"][2] <= dest[CASOS[caso]["doc"]]["largura"], f"página {caso} {w}×{h}: documento ampliado")
            check(not erros, f"página {w}×{h}: erros/404: {erros}")
            ctx.close()


def checar_sem_range():
    """Servidor sem Range: o clipe congela no pôster (sem .viva); documento, destaque e texto aparecem alinhados em p=1 de cada caso."""
    from render import navegador, servidor
    with servidor(com_range=False) as base, navegador() as nav:
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080)
        rolar(pg, "sige", .25)
        pg.wait_for_timeout(3000)
        check(not pg.evaluate("document.querySelector('#sige figure.clipe').classList.contains('viva')"), "sem Range: o clipe não congelou no pôster")
        for caso in CASOS:
            rolar(pg, caso, 1)
            b = caixas(pg, caso)
            check(float(b["doc"][4]) == 1 and float(b["dest"][4]) == 1, f"sem Range: documento/destaque de {caso} invisíveis em p=1")
            checar_alinhado(b, f"sem Range {caso}")
        ctx.close()


def checar_celular():
    """390×844, em cada caso: sem o documento inteiro (display none); o recorte visível, inteiro na tela em p=1 e nunca
    ampliado; movimento reduzido: sem .js-v2, pôster, documento e destaque visíveis; sem JS: manchete e documento visíveis."""
    from render import navegador, servidor
    dest = json.loads((DOCS / "destaques.json").read_text(encoding="utf-8"))
    with servidor() as base, navegador() as nav:
        ctx, pg, erros = abrir_pagina(nav, base, 390, 844, device_scale_factor=2, is_mobile=True, has_touch=True)
        for caso in CASOS:
            rolar(pg, caso, 1)
            b = caixas(pg, caso)
            check(b["doc"][5] == "none", f"celular {caso}: o documento inteiro aparece (ilegível em 390 px)")
            r = b["recorte"]
            check(r and r[5] != "none" and r[0] >= 0 and r[1] >= 0 and r[0] + r[2] <= 390 and r[1] + r[3] <= 844, f"celular {caso}: recorte fora da tela {r}")
            check(r and r[2] <= dest[CASOS[caso]["doc"]]["recorte"][2], f"celular {caso}: recorte ampliado")
            m = pg.evaluate(f"""(function(){{var t=document.querySelector('#{caso} .rotulo').getBoundingClientRect(),
              e=document.querySelector('#{caso} .caso-link').getBoundingClientRect(),
              barra=document.querySelector('.barra').getBoundingClientRect();return [t.top,barra.bottom,e.bottom];}})()""")
            check(m[0] >= m[1] and m[2] <= 844, f"celular {caso}: o texto não cabe entre a barra e o fim da tela (topo {m[0]:.0f}, barra {m[1]:.0f}, base {m[2]:.0f})")
        check(not erros, f"celular: erros/404: {erros}")
        ctx.close()
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080, reduced_motion="reduce")
        check(not pg.evaluate("document.documentElement.classList.contains('js-v2')"), "movimento reduzido: .js-v2 ligado")
        b = caixas(pg, "sige")
        check(float(b["doc"][4]) == 1 and float(b["dest"][4]) == 1, "movimento reduzido: documento/destaque invisíveis")
        check(pg.evaluate("getComputedStyle(document.querySelector('#sige video')).display") == "none", "movimento reduzido: o vídeo aparece")
        ctx.close()
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080, java_script_enabled=False)
        b = caixas(pg, "sige")
        check(float(b["doc"][4]) == 1 and pg.is_visible("#sige h2.manchete"), "sem JS: manchete ou documento invisíveis")
        ctx.close()


def checar_recorte_viewports():
    """Telas médias e baixas (celular deitado 844×390, tablet em pé 768×1024) têm a versão completa, como o computador:
    em cada caso, em p=1, o documento à vista, o texto inteiro entre a barra e o fim da tela e ao lado do quadro, sem cobri-lo."""
    from render import navegador, servidor
    with servidor() as base, navegador() as nav:
        for w, h in ((844, 390), (768, 1024)):
            ctx, pg, erros = abrir_pagina(nav, base, w, h, device_scale_factor=2, is_mobile=True, has_touch=True)
            check(pg.evaluate("document.documentElement.classList.contains('js-v2')"), f"{w}×{h}: sem .js-v2 (vídeo preso)")
            for caso in CASOS:
                rolar(pg, caso, 1)
                b = caixas(pg, caso)
                check(b["doc"][5] != "none" and float(b["doc"][4]) == 1, f"{caso} {w}×{h}: o documento não aparece em p=1")
                m = pg.evaluate(f"""(function(){{var t=document.querySelector('#{caso} .rotulo').getBoundingClientRect(),
                  e=document.querySelector('#{caso} .caso-link').getBoundingClientRect(),
                  q=document.querySelector('#{caso} .quadro').getBoundingClientRect(),
                  barra=document.querySelector('.barra').getBoundingClientRect();return [t.top,barra.bottom,e.bottom,t.left,q.right];}})()""")
                check(m[0] >= m[1] and m[2] <= h, f"{caso} {w}×{h}: o texto não cabe entre a barra e o fim da tela (topo {m[0]:.0f}, barra {m[1]:.0f}, base {m[2]:.0f})")
                check(m[3] >= m[4], f"{caso} {w}×{h}: o texto cobre o quadro (texto em {m[3]:.0f} px, quadro até {m[4]:.0f} px)")
            check(not erros, f"{w}×{h}: erros/404: {erros}")
            ctx.close()


def checar_abertura():
    """Critério 1 do spec: em 1366×768 a ficha inteira (nome, vaga, posicionamento, contato) cabe sem rolar; a cena da
    abertura anda com a rolagem (só cena: p=0,5 → 4 s de 8) e não tem documento nem texto."""
    from render import navegador, servidor
    with servidor() as base, navegador() as nav:
        ctx, pg, erros = abrir_pagina(nav, base, 1366, 768)
        fundo = pg.evaluate("document.querySelector('#inicio .contato').getBoundingClientRect().bottom")
        check(fundo <= 768, f"abertura 1366×768: o contato termina em {fundo:.0f} px, abaixo da primeira tela")
        check(pg.evaluate("document.querySelector('#mesa .doc, #mesa .texto') === null"), "abertura: #mesa tem .doc ou .texto")
        rolar(pg, "mesa", .5)
        pg.wait_for_function("document.querySelector('#mesa figure.clipe').classList.contains('viva')", timeout=20000)
        t = pg.evaluate("document.querySelector('#mesa video').currentTime")
        check(abs(t - 4.0208) < .05, f"abertura: em p=0,5 o vídeo está em {t:.3f} s, esperava 4,021 s (só cena)")
        check(not erros, f"abertura: erros/404: {erros}")
        ctx.close()


def checar_trilho():
    """Trilho lateral em 1366×768 e 1920×1080: não cobre o documento nem o texto em p=1 de nenhum caso; a âncora da
    seção visível recebe aria-current; abaixo de 1200 px o trilho some."""
    from render import navegador, servidor
    def cruza(a, b):
        return a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3]
    with servidor() as base, navegador() as nav:
        for w, h in ((1366, 768), (1920, 1080)):
            ctx, pg, erros = abrir_pagina(nav, base, w, h)
            for caso in CASOS:
                rolar(pg, caso, 1)
                b = caixas(pg, caso)
                trilho = pg.evaluate("(function(){var r=document.querySelector('nav.trilho').getBoundingClientRect();return [r.left,r.top,r.width,r.height];})()")
                check(not cruza(trilho, b["doc"][:4]) and not cruza(trilho, b["texto"][:4]), f"trilho {w}×{h}: cobre o documento ou o texto em {caso}")
                atual = pg.evaluate("(function(){var a=document.querySelector('nav.trilho a[aria-current=\"true\"]');return a&&a.getAttribute('href');})()")
                check(atual == f"#{caso}", f"trilho {w}×{h}: em {caso} o aria-current está em {atual}")
            ctx.close()
        ctx, pg, erros = abrir_pagina(nav, base, 1100, 800)
        check(pg.evaluate("getComputedStyle(document.querySelector('nav.trilho')).display") == "none", "trilho: aparece em 1100 px")
        ctx.close()


def checar_troca_de_clipes():
    """clipes.js mantém no máximo 3 vídeos com dados em tela larga (2 nas estreitas): ir da abertura ao caso 4 e voltar ao caso 2 traz o caso 2 de volta a .viva."""
    from render import navegador, servidor
    with servidor() as base, navegador() as nav:
        ctx, pg, erros = abrir_pagina(nav, base, 1920, 1080)
        for caso in ("mesa", "veks", "sige", "modulares"):
            rolar(pg, caso, .3)
            pg.wait_for_function(f"document.querySelector('#{caso} figure.clipe').classList.contains('viva')", timeout=20000)
        com_dados = pg.evaluate("[].filter.call(document.querySelectorAll('figure.clipe video'),function(v){return v.readyState>0;}).length")
        check(com_dados <= 3, f"clipes: {com_dados} vídeos com dados ao mesmo tempo (máx. 3)")
        rolar(pg, "veks", .3)
        pg.wait_for_function("document.querySelector('#veks figure.clipe').classList.contains('viva')", timeout=20000)
        check(not erros, f"clipes: erros/404: {erros}")
        ctx.close()


def checar_readme():
    readme = (RAIZ / "README.md").read_text(encoding="utf-8")
    for trecho in ("site/index.html", "site/historia.html", "cenas/render.py --so", "cenas/documentos.py", "tests/check_v2.py --navegador", "zip:"):
        check(trecho in readme, f"README do portfólio sem {trecho!r}")


def checar_renomeacao():
    """O site v2 é o index.html; o protótipo continua inteiro em historia.html; v2.html redireciona (o link do piloto circulou)."""
    check((SITE / "historia.html").exists() and '<section class="cena" id="tese"' in (SITE / "historia.html").read_text(encoding="utf-8"),
          "renomeação: site/historia.html não é o protótipo (sem #tese)")
    v2 = SITE / "v2.html"
    check(v2.exists() and re.search(r'<meta http-equiv="refresh" content="0; ?url=\./">', v2.read_text(encoding="utf-8")), "renomeação: v2.html não redireciona para ./")
    check('<section class="caso cena" id="veks"' in PAGINA.read_text(encoding="utf-8"), "renomeação: index.html não é o site v2")
    hist = (RAIZ / "tests" / "check_historia.py").read_text(encoding="utf-8")
    check("index.html" not in hist, "renomeação: check_historia.py ainda aponta para index.html")


def main():
    checar_documentos()
    checar_cena_estatica()
    checar_pagina_estatica()
    checar_readme()
    checar_renomeacao()
    if "--navegador" in sys.argv:
        checar_kit()
        checar_render()
        checar_cena_abertura()
        checar_cena_veks()
        checar_passagem("veks")
        checar_cena_modulares()
        checar_passagem("modulares")
        checar_cena_sige()
        checar_passagem("sige")
        checar_pagina()
        checar_viewports()
        checar_sem_range()
        checar_celular()
        checar_recorte_viewports()
        checar_abertura()
        checar_trilho()
        checar_troca_de_clipes()
    if "--video" in sys.argv:
        checar_video()
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
