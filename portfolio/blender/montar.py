"""Monta no Blender uma cena exportada por portfolio/cenas/exportar.py e renderiza os quadros no Cycles.
Troca os materiais procedurais do kit por texturas fotografadas (Poly Haven, CC0), o céu pintado por um HDRI que ilumina
a cena, e usa luz indireta de verdade (path tracing), AgX e desfoque de movimento. Roda sem interface.

Uso (da raiz do repositório; os argumentos do script vêm depois de "--"):
  blender -b -P portfolio/blender/montar.py -- --caso modulares                         # todos os quadros
  blender -b -P portfolio/blender/montar.py -- --caso modulares --quadros 287           # um quadro
  blender -b -P portfolio/blender/montar.py -- --caso modulares --quadros 0-287:24      # de 24 em 24
Opções: --dispositivo OPTIX|CUDA|CPU (padrão OPTIX; para se não achar a placa) · --amostras 256 · --escala 100 (%)
        --saida <pasta> (padrão portfolio/cenas/saida/<caso>-blender-quadros) · --salvar <arquivo.blend> · --sem-render
Saída: q0000.png… (1920×1080), os mesmos nomes do render.py; um quadro já gravado não é refeito (retoma de onde parou).
Depois: python portfolio/cenas/render.py --quadros <pasta> --so <caso>   (encoda o vídeo do site e o pôster)
"""
import argparse
import base64
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib  # noqa: E402

# --visual cinema: o módulo de modelos de cada caso (MODELOS, INSTANCIADOS, SUBSTITUIDOS e extras(vm, ctx))
MODULO = {"modulares": "objetos", "veks": "objetos_veks", "abertura": "objetos_abertura", "sige": "objetos_sige"}
MOD = None  # o módulo do caso em curso (ver main)
SUBSTITUIDOS = set()

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent  # portfolio/
ASSETS = AQUI / "assets"
# three.js (Y para cima) → Blender (Z para cima): (x, y, z) → (x, −z, y). A malha fica nas coordenadas locais do three.
C = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.float64)
CHANFRO = 0.0  # raio (m) do chanfro de shader nas arestas; o --visual cinema liga (ver main)
FRIO = (.85, .95, 1.1)  # --visual cinema: tinta do céu (luz de preenchimento fria)
AMARELO = (.45, .26, .02)
SOLO = None  # --visual cinema: retângulo (xmin, xmax, ymin, ymax) do solo da obra no Blender, para a borda irregular
VIAS = []  # --visual cinema: retângulos do asfalto (mesma forma), onde não nasce capim  # tinta de equipamento (sRGB ~205, 160, 40) da lança do guindaste no --visual cinema


def argumentos():
    p = argparse.ArgumentParser(prog="montar.py")
    p.add_argument("--caso", required=True)
    p.add_argument("--quadros", default=None, help="N, A-B ou A-B:passo (padrão: todos)")
    p.add_argument("--dispositivo", default="OPTIX", choices=["OPTIX", "CUDA", "CPU"])
    p.add_argument("--amostras", type=int, default=256)
    p.add_argument("--escala", type=int, default=100)
    p.add_argument("--saida", default=None)
    p.add_argument("--salvar", default=None)
    p.add_argument("--sem-render", action="store_true")
    p.add_argument("--sem-desfoque", action="store_true", help="sem desfoque de movimento")
    p.add_argument("--todas-chaves", action="store_true", help="chaves em todos os quadros mesmo num teste (o foco fica igual ao final)")
    p.add_argument("--visual", default="padrao", choices=["padrao", "cinema"],
                   help="cinema: céu de fim de tarde, névoa de distância, arestas chanfradas, contraste e vinheta")
    p.add_argument("--ceu", default=None, help="id de um HDRI em assets/hdri (padrão: o do assets.json para o visual)")
    p.add_argument("--ceu-forca", type=float, default=None, help="multiplica a luz do céu (padrão 1; 1,5 no cinema)")
    return p.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def f32(b64, forma):
    return np.frombuffer(base64.b64decode(b64), dtype="<f4").reshape(forma).astype(np.float64)


def matrizes(b64, n):
    """n matrizes 4×4 do three.js (por colunas) → array (n, 4, 4) por linhas."""
    return f32(b64, (n, 4, 4)).transpose(0, 2, 1)


# ---------- malhas ----------
def malha(nome, pos, nor, uv_m, uv):
    """Triângulos soltos: pos (n, 3), normais (n, 3) ou None, UVs (n, 2) por vértice (= por canto)."""
    n = len(pos)
    m = bpy.data.meshes.new(nome)
    m.vertices.add(n); m.loops.add(n); m.polygons.add(n // 3)
    m.vertices.foreach_set("co", pos.astype(np.float32).ravel())
    m.loops.foreach_set("vertex_index", np.arange(n, dtype=np.int32))
    m.polygons.foreach_set("loop_start", np.arange(0, n, 3, dtype=np.int32))
    m.polygons.foreach_set("loop_total", np.full(n // 3, 3, dtype=np.int32))
    for nome_uv, dados in (("uvMetros", uv_m), ("uv", uv)):
        if dados is not None:
            m.uv_layers.new(name=nome_uv).data.foreach_set("uv", dados.astype(np.float32).ravel())
    m.update(calc_edges=True)
    m.validate(clean_customdata=False)
    if nor is not None and len(m.vertices) == n:
        m.polygons.foreach_set("use_smooth", np.ones(len(m.polygons), dtype=bool))
        comp = np.linalg.norm(nor, axis=1, keepdims=True)
        m.normals_split_custom_set_from_vertices((nor / np.where(comp == 0, 1, comp)).astype(np.float32))
    return m


# ---------- materiais ----------
def imagem(caminho, cor=True):
    img = bpy.data.images.load(str(caminho), check_existing=True)
    if not cor:
        img.colorspace_settings.name = "Non-Color"
    return img


def no_uv(nt, camada, escala=(1, 1)):
    uv = nt.nodes.new("ShaderNodeUVMap"); uv.uv_map = camada
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (escala[0], escala[1], 1)
    nt.links.new(uv.outputs["UV"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def no_imagem(nt, img, vetor):
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = img
    nt.links.new(vetor, n.inputs["Vector"])
    return n


def material(d, indice, pasta, quadros):
    m = bpy.data.materials.new(d["nome"] or d["tipo"] or "material")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    saida = nt.nodes.new("ShaderNodeOutputMaterial")
    if CHANFRO and not d["tipo"] and not d["mapa"] and np.allclose(d["cor"], (.58, .62, .64), atol=.02):
        d = dict(d, tipo="zinco")  # cinema: o zinco liso do kit (tapume, cobertura) vira a chapa trapezoidal fotografada
    tipo = d["tipo"] or d["emMetros"]
    foto = indice["texturas"].get(d["tipo"]) if d["tipo"] else None
    doc = d["mapa"] and not d["mapa"].startswith("canvas-")

    if doc:  # documento real (site/docs): emissão pura se era MeshBasicMaterial, senão papel com a imagem
        vetor = no_uv(nt, "uv")
        nomes = sorted({x for x in (d["mapaPorQuadro"] or [d["mapa"]]) if x})
        cor = None
        for nome in nomes:
            tex = no_imagem(nt, imagem(RAIZ / "site" / "docs" / nome), vetor)
            tex.extension = "EXTEND"
            sai = tex.outputs["Color"]
            if d["mapaPorQuadro"]:  # a tela que troca de imagem: peso 0/1 por quadro
                peso = nt.nodes.new("ShaderNodeValue"); peso.label = nome
                for q in quadros:
                    peso.outputs[0].default_value = 1.0 if d["mapaPorQuadro"][q] == nome else 0.0
                    peso.outputs[0].keyframe_insert("default_value", frame=q)
                mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"
                mul.inputs["Factor"].default_value = 1
                nt.links.new(sai, mul.inputs["A"]); nt.links.new(peso.outputs[0], mul.inputs["B"])
                sai = mul.outputs["Result"]
            if cor is None:
                cor = sai
            else:
                soma = nt.nodes.new("ShaderNodeMix"); soma.data_type = "RGBA"; soma.blend_type = "ADD"
                soma.inputs["Factor"].default_value = 1
                nt.links.new(cor, soma.inputs["A"]); nt.links.new(sai, soma.inputs["B"])
                cor = soma.outputs["Result"]
        if d["basico"]:
            em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1
            nt.links.new(cor, em.inputs["Color"]); nt.links.new(em.outputs[0], saida.inputs["Surface"])
        else:
            p = nt.nodes.new("ShaderNodeBsdfPrincipled"); p.inputs["Roughness"].default_value = d["rugosidade"]
            nt.links.new(cor, p.inputs["Base Color"]); nt.links.new(p.outputs[0], saida.inputs["Surface"])
        m["documento"] = True
        m["emissao"] = bool(d["basico"])
        if CHANFRO and d["basico"]:  # cinema: a máscara do documento sai de um AOV, filtrado como a imagem (ver compor)
            aov = nt.nodes.new("ShaderNodeOutputAOV"); aov.aov_name = "documento"; aov.inputs["Value"].default_value = 1
        return m

    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs[0], saida.inputs["Surface"])
    p.inputs["Metallic"].default_value = d["metal"]
    p.inputs["Roughness"].default_value = d["rugosidade"]
    p.inputs["Base Color"].default_value = (*d["cor"], 1)
    if d["vidro"]:  # vidro de fachada do kit: escuro e espelhado
        p.inputs["Roughness"].default_value = .04
        p.inputs["Coat Weight"].default_value = 1
        if CHANFRO:  # cinema: visto de cima o vidro escuro só refletia o chão (um "buraco"); película: reflete céu e entorno
            p.inputs["Metallic"].default_value = .5; p.inputs["Base Color"].default_value = (.12, .14, .16, 1)
        return m
    if d["transparente"] and d["opacidade"] < 1:  # vidraça dos interiores
        p.inputs["Transmission Weight"].default_value = 1
        p.inputs["Roughness"].default_value = .02
        p.inputs["IOR"].default_value = 1.45
        p.inputs["Base Color"].default_value = (.95, .97, .98, 1)
        return m
    if any(d["emissivo"]):
        p.inputs["Emission Color"].default_value = (*d["emissivo"], 1); p.inputs["Emission Strength"].default_value = 1
    normal = None
    if foto:  # textura fotografada, no tamanho real
        mx, my = foto["metros"]
        vetor = no_uv(nt, "uvMetros", (1 / mx, 1 / my))
        mapas = foto["mapas"]
        cor = no_imagem(nt, imagem(ASSETS / mapas["cor"]), vetor).outputs["Color"]
        pasto_cinema = CHANFRO and d["tipo"] == "pasto"
        if pasto_cinema:  # anti-ladrilho: uma segunda leitura girada 34° e em outra escala, trocada por ruído largo
            uv2 = nt.nodes.new("ShaderNodeMapping"); uv2.inputs["Rotation"].default_value = (0, 0, .6)
            uv2.inputs["Scale"].default_value = (.43, .43, 1); nt.links.new(vetor, uv2.inputs["Vector"])
            outra = no_imagem(nt, imagem(ASSETS / mapas["cor"]), uv2.outputs["Vector"]).outputs["Color"]
            troca = nt.nodes.new("ShaderNodeTexNoise"); troca.inputs["Scale"].default_value = .03; troca.inputs["Detail"].default_value = 3
            nt.links.new(nt.nodes.new("ShaderNodeTexCoord").outputs["Object"], troca.inputs["Vector"])
            rampa = nt.nodes.new("ShaderNodeMapRange"); rampa.inputs["From Min"].default_value = .42; rampa.inputs["From Max"].default_value = .58
            nt.links.new(troca.outputs[0], rampa.inputs["Value"])
            mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
            nt.links.new(rampa.outputs["Result"], mx.inputs["Factor"]); nt.links.new(cor, mx.inputs["A"]); nt.links.new(outra, mx.inputs["B"])
            cor = mx.outputs["Result"]
        if foto.get("tom"):  # matiz e saturação do tom, luminosidade da foto
            h = foto["tom"].lstrip("#")
            srgb = [int(h[k:k + 2], 16) / 255 for k in (0, 2, 4)]
            linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb]
            tom = nt.nodes.new("ShaderNodeMix"); tom.data_type = "RGBA"; tom.blend_type = "COLOR"
            tom.inputs["Factor"].default_value = .6 if CHANFRO and d["tipo"] == "pasto" else .85  # cinema: verde menos neon
            tom.inputs["B"].default_value = (*linear, 1)
            nt.links.new(cor, tom.inputs["A"])
            cor = tom.outputs["Result"]
        if d["tipo"] in ("pasto", "solo", "asfalto"):  # manchas de dezenas de metros por cima do ladrilho: escondem a repetição
            ruido = nt.nodes.new("ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = .06; ruido.inputs["Detail"].default_value = 4
            nt.links.new(nt.nodes.new("ShaderNodeTexCoord").outputs["Object"], ruido.inputs["Vector"])
            manchas = nt.nodes.new("ShaderNodeMapRange"); manchas.inputs["To Min"].default_value = .7; manchas.inputs["To Max"].default_value = 1.25
            nt.links.new(ruido.outputs[0], manchas.inputs["Value"])
            mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1
            nt.links.new(cor, mul.inputs["A"]); nt.links.new(manchas.outputs["Result"], mul.inputs["B"])
            cor = mul.outputs["Result"]
        nt.links.new(cor, p.inputs["Base Color"])
        if pasto_cinema:
            p.inputs["Roughness"].default_value = .9; p.inputs["Specular IOR Level"].default_value = .3
        elif "rugosidade" in mapas:
            rug = no_imagem(nt, imagem(ASSETS / mapas["rugosidade"], False), vetor).outputs["Color"]
            if CHANFRO and d["tipo"] in ("pasto", "solo", "asfalto"):  # cinema: chão fosco, sem o brilho branco do sol rasante
                piso = nt.nodes.new("ShaderNodeMath"); piso.operation = "MAXIMUM"; piso.inputs[1].default_value = .85
                nt.links.new(rug, piso.inputs[0]); rug = piso.outputs[0]
                p.inputs["Specular IOR Level"].default_value = .3
            nt.links.new(rug, p.inputs["Roughness"])
        if "normal" in mapas:
            nm = nt.nodes.new("ShaderNodeNormalMap"); nm.uv_map = "uvMetros"
            nt.links.new(no_imagem(nt, imagem(ASSETS / mapas["normal"], False), vetor).outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
            normal = nm.outputs["Normal"]
            if pasto_cinema:  # o sol rasante desenha o ladrilho pelo relevo: normal fraca
                nm.inputs["Strength"].default_value = .3
        if CHANFRO and "relevo" in mapas and d["tipo"] in ("solo", "concreto"):  # cinema: o relevo da foto vira bump (no pasto, mostraria o ladrilho)
            rb = nt.nodes.new("ShaderNodeBump"); rb.inputs["Distance"].default_value = .02
            nt.links.new(no_imagem(nt, imagem(ASSETS / mapas["relevo"], False), vetor).outputs["Color"], rb.inputs["Height"])
            if normal is not None:
                nt.links.new(normal, rb.inputs["Normal"])
            nt.links.new(rb.outputs["Normal"], p.inputs["Normal"]); normal = rb.outputs["Normal"]
        if CHANFRO and d["tipo"] == "solo" and SOLO:  # cinema: a borda do solo vira recorte irregular sobre o pasto
            x0, x1, y0, y1 = SOLO
            pos = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(nt.nodes.new("ShaderNodeNewGeometry").outputs["Position"], pos.inputs["Vector"])
            dist = mat(nt, "MINIMUM", mat(nt, "MINIMUM", faixa(nt, pos.outputs["X"], x0, x0 + 10, 0, 10), faixa(nt, pos.outputs["X"], x1 - 10, x1, 10, 0)),
                       mat(nt, "MINIMUM", faixa(nt, pos.outputs["Y"], y0, y0 + 10, 0, 10), faixa(nt, pos.outputs["Y"], y1 - 10, y1, 10, 0)))
            rr = no(nt, "ShaderNodeTexNoise", Vector=nt.nodes.new("ShaderNodeTexCoord").outputs["Object"], Scale=.35, Detail=5.0).outputs[0]
            recorte = faixa(nt, mat(nt, "ADD", dist, faixa(nt, rr, .3, .7, -2.2, 1.2)), 0, 1.5, 0, 1)
            tr = nt.nodes.new("ShaderNodeBsdfTransparent"); ms = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(recorte, ms.inputs["Fac"]); nt.links.new(tr.outputs[0], ms.inputs[1]); nt.links.new(p.outputs[0], ms.inputs[2])
            nt.links.new(ms.outputs[0], saida.inputs["Surface"])
        if CHANFRO and d["tipo"] == "solo":  # cinema: laterita menos saturada (não ler como quadra de saibro)
            hs = nt.nodes.new("ShaderNodeHueSaturation"); hs.inputs["Hue"].default_value = .515; hs.inputs["Saturation"].default_value = .85; hs.inputs["Value"].default_value = 1.1
            nt.links.new(p.inputs["Base Color"].links[0].from_socket, hs.inputs["Color"]); nt.links.new(hs.outputs["Color"], p.inputs["Base Color"])
    elif d["mapa"] and (pasta / f"{d['mapa']}.png").exists():  # sem foto: o mapa de cor pintado pelo kit, no ladrilho do kit
        L = d["ladrilho"] or 1
        vetor = no_uv(nt, "uvMetros", (1 / L, 1 / L))
        nt.links.new(no_imagem(nt, imagem(pasta / f"{d['mapa']}.png"), vetor).outputs["Color"], p.inputs["Base Color"])
        p.inputs["Roughness"].default_value = .55 if tipo in ("acoPintado", "plastico", "acento", "vermelho") else .9
    escuro = not foto and not d["mapa"] and max(d["cor"]) < .06  # para-brisa, pneu: o desgaste os acinzentava
    if CHANFRO and d["tipo"] not in ("pasto", "solo", "asfalto", "folha", "tronco", "areia", "brita") and not escuro and not any(d["emissivo"]):
        normal = desgaste(nt, p, d, normal, pintado=not foto)
    if CHANFRO and d["tipo"] not in ("pasto", "solo", "asfalto"):  # aresta viva denuncia o 3D: arredondada no shader
        bv = nt.nodes.new("ShaderNodeBevel"); bv.samples = 4; bv.inputs["Radius"].default_value = CHANFRO
        if normal is not None:
            nt.links.new(normal, bv.inputs["Normal"])
        nt.links.new(bv.outputs["Normal"], p.inputs["Normal"])
    return m


def no(nt, tipo, **entradas):
    n = nt.nodes.new(tipo)
    for k, v in entradas.items():
        if hasattr(v, "is_output"):
            nt.links.new(v, n.inputs[k])
        else:
            n.inputs[k].default_value = v
    return n


def mat(nt, op, a, b):
    n = nt.nodes.new("ShaderNodeMath"); n.operation = op  # sem clamp: distâncias em metros passam de 1
    for k, v in enumerate((a, b)):
        if hasattr(v, "is_output"):
            nt.links.new(v, n.inputs[k])
        else:
            n.inputs[k].default_value = v
    return n.outputs[0]


def faixa(nt, v, de, ate, para_de, para_ate):
    return no(nt, "ShaderNodeMapRange", Value=v, **{"From Min": de, "From Max": ate, "To Min": para_de, "To Max": para_ate}).outputs["Result"]


def desgaste(nt, p, d, normal, pintado):
    """--visual cinema: o "uso" que faz a caixa lisa ler como objeto real. Variação larga de tom, poeira de laterita
    subindo da base (até 1,2 m do chão), escorrido nas faces verticais, oclusão nos encontros, brilho variável e, na
    tinta (sem foto), a casca de laranja. Devolve a normal (para o chanfro encadear)."""
    bc = p.inputs["Base Color"]
    if bc.is_linked:
        cor = bc.links[0].from_socket
    else:
        rgb = nt.nodes.new("ShaderNodeRGB"); rgb.outputs[0].default_value = bc.default_value; cor = rgb.outputs[0]
    obj = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")

    def mul_cor(c, fator):
        m = nt.nodes.new("ShaderNodeMix"); m.data_type = "RGBA"; m.blend_type = "MULTIPLY"; m.inputs["Factor"].default_value = 1
        nt.links.new(c, m.inputs["A"])
        if hasattr(fator, "is_output"):
            nt.links.new(fator, m.inputs["B"])
        else:
            m.inputs["B"].default_value = (fator, fator, fator, 1)
        return m.outputs["Result"]

    if d["tipo"] == "papel":  # o branco do kit (~0,96) estoura ao sol: tinta branca real fica perto de 0,75
        cor = mul_cor(cor, .8)
    largo = no(nt, "ShaderNodeTexNoise", Vector=obj, Scale=.8, Detail=6.0).outputs[0]
    cor = mul_cor(cor, faixa(nt, largo, .3, .7, .92, 1.04))
    # poeira de laterita da obra: forte junto ao chão, some até 1,2 m, recortada por ruído
    z = no(nt, "ShaderNodeSeparateXYZ", Vector=geo.outputs["Position"]).outputs["Z"]
    perto_do_chao = faixa(nt, z, 0, 1.2, 1, 0)
    manchas = faixa(nt, no(nt, "ShaderNodeTexNoise", Vector=obj, Scale=4.0, Detail=4.0).outputs[0], .4, .65, 0, 1)
    poeira = mat(nt, "MULTIPLY", mat(nt, "MULTIPLY", perto_do_chao, manchas), .35)
    pz = nt.nodes.new("ShaderNodeMix"); pz.data_type = "RGBA"; pz.blend_type = "MIX"
    nt.links.new(poeira, pz.inputs["Factor"]); nt.links.new(cor, pz.inputs["A"]); pz.inputs["B"].default_value = (.19, .075, .035, 1)
    cor = pz.outputs["Result"]
    # escorrido: ruído esticado na vertical, só nas faces verticais
    esticado = no(nt, "ShaderNodeMapping", Vector=obj, Scale=(6, .3, 6)).outputs["Vector"]  # Object é o espaço do three: Y para cima
    risco = faixa(nt, no(nt, "ShaderNodeTexNoise", Vector=esticado, Scale=3.0, Detail=3.0).outputs[0], .5, .7, 0, 1)
    nz = no(nt, "ShaderNodeSeparateXYZ", Vector=geo.outputs["Normal"]).outputs["Z"]
    vertical = mat(nt, "LESS_THAN", mat(nt, "ABSOLUTE", nz, 0), .3)
    cor = mul_cor(cor, faixa(nt, mat(nt, "MULTIPLY", risco, vertical), 0, 1, 1, .87))
    # oclusão nos encontros (caixa sobre caixa, pé no chão)
    ao = nt.nodes.new("ShaderNodeAmbientOcclusion"); ao.samples = 2; ao.inputs["Distance"].default_value = .3
    nt.links.new(cor, ao.inputs["Color"])
    cor = mul_cor(cor, faixa(nt, ao.outputs["AO"], 0, 1, .6, 1))
    nt.links.new(cor, bc)
    # brilho: a tinta varia de 0,35 a 0,7; onde tem poeira, fosca
    rug_in = p.inputs["Roughness"]
    rug = rug_in.links[0].from_socket if rug_in.is_linked else (faixa(nt, largo, .3, .7, .35, .7) if pintado else rug_in.default_value)
    rmix = no(nt, "ShaderNodeMapRange", Value=mat(nt, "MULTIPLY", poeira, 2.5), **{"To Min": rug, "To Max": .85})
    nt.links.new(rmix.outputs["Result"], rug_in)
    if pintado:  # casca de laranja da pintura
        bump = no(nt, "ShaderNodeBump", Height=no(nt, "ShaderNodeTexNoise", Vector=obj, Scale=300.0).outputs[0], Strength=.03)
        if normal is not None:
            nt.links.new(normal, bump.inputs["Normal"])
        nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
        normal = bump.outputs["Normal"]
    return normal


# ---------- objetos ----------
def decompor(M):
    return Matrix(M.tolist()).decompose()


def animar(ob, Ms, quadros, visivel):
    """Ms: (N, 4, 4) já no espaço do Blender. Chaves de posição, rotação (quatérnio contínuo) e escala em cada quadro."""
    ob.rotation_mode = "QUATERNION"
    anterior = None
    for q in quadros:
        loc, rot, esc = decompor(Ms[q])
        if anterior is not None:
            rot.make_compatible(anterior)
        anterior = rot.copy()
        ob.location, ob.rotation_quaternion, ob.scale = loc, rot, esc
        for caminho in ("location", "rotation_quaternion", "scale"):
            ob.keyframe_insert(caminho, frame=q)
        if visivel is not None:
            ob.hide_render = not visivel[q]
            ob.keyframe_insert("hide_render", frame=q)


def colecao_do_modelo(modelo):
    """Carrega de um .blend do Poly Haven só os objetos listados em assets.json (o arquivo traz LOD0, LOD1 e peças soltas)
    numa coleção fora da cena; devolve (coleção, altura, base z). O que um objeto usa (geometry nodes, peças) vem junto."""
    caminho = ASSETS / modelo["arquivo"]
    col = bpy.data.collections.new(Path(caminho).stem)
    with bpy.data.libraries.load(str(caminho), link=False) as (de, para):
        para.objects = [o for o in de.objects if not modelo.get("objetos") or o in modelo["objetos"]]
    zs = []
    for ob in para.objects:
        if ob is None:
            continue
        col.objects.link(ob)
        zs += [(ob.matrix_world @ Vector(c)).z for c in ob.bound_box]
    base, topo = (min(zs), max(zs)) if zs else (0, 1)
    return col, topo - base, base


def instancia(col, nome, matriz):
    ob = bpy.data.objects.new(nome, None)
    ob.instance_type = "COLLECTION"; ob.instance_collection = col
    ob.matrix_world = matriz
    bpy.context.scene.collection.objects.link(ob)
    return ob


def aro_da_roda(roda, centro, raio, largura, material_aro):
    """--visual cinema: aro metálico (0,55 do raio, 1 cm para fora de cada lado) preso à roda do kit; segue a animação."""
    n, r, h = 24, raio * .55, largura / 2 + .01
    ang = np.linspace(0, 2 * np.pi, n + 1)
    tri = []
    for a0, a1 in zip(ang[:-1], ang[1:]):
        p0, p1 = (r * np.cos(a0), r * np.sin(a0)), (r * np.cos(a1), r * np.sin(a1))
        for y in (-h, h):  # tampas
            tri += [(0, y, 0), (p0[0], y, p0[1]), (p1[0], y, p1[1])] if y > 0 else [(0, y, 0), (p1[0], y, p1[1]), (p0[0], y, p0[1])]
        tri += [(p0[0], -h, p0[1]), (p0[0], h, p0[1]), (p1[0], h, p1[1]), (p0[0], -h, p0[1]), (p1[0], h, p1[1]), (p1[0], -h, p1[1])]
    P = np.array(tri) + centro
    me = malha("aro", P, None, np.zeros((len(P), 2)), None); me.materials.append(material_aro)
    ob = bpy.data.objects.new("aro", me); bpy.context.scene.collection.objects.link(ob)
    ob.parent = roda; ob.matrix_parent_inverse = Matrix.Identity(4)


def vegetacao(dados, indice, arbustos):
    """--visual cinema: árvores e arbustos do Poly Haven (CC0) no lugar das esferas do kit. A árvore do kit tem ~5,3 m × escala;
    o modelo fica com 1,3× isso (árvore de pasto real) e um giro fixo por árvore. arbustos: [(matriz no Blender, altura)]."""
    rnd = np.random.default_rng(11)
    modelos = indice.get("modelos", {})
    arv = [colecao_do_modelo(m) for m in modelos.get("arvore", [])]
    arb = [colecao_do_modelo(m) for m in modelos.get("arbusto", [])]
    mata = [colecao_do_modelo(m) for m in modelos.get("mata", [])] or arv
    if arv:
        for k, a in enumerate(dados["arvores"]):
            col, alt, base = arv[k % len(arv)]
            M = C @ np.array(a["matriz"], dtype=np.float64).reshape(4, 4).T @ C.T  # o modelo já é Z para cima: só a posição muda de eixo
            e = 5.3 * a["escala"] * 1.3 / alt
            R = Matrix.Rotation(rnd.uniform(0, 2 * math.pi), 4, "Z")
            instancia(col, a["id"], Matrix(M.tolist()) @ R @ Matrix.Diagonal((e, e, e, 1)) @ Matrix.Translation((0, 0, -base)))
        # o horizonte em camadas: capões de mata num anel de 160–420 m, que a névoa esfuma (o pasto do kit era uma régua)
        n = 0
        for _ in range(14):
            ang, raio = rnd.uniform(0, 2 * math.pi), rnd.uniform(160, 420)
            cx, cy = raio * math.cos(ang), raio * math.sin(ang)
            for _ in range(int(rnd.integers(4, 9))):
                col, alt, base = mata[n % len(mata)]
                e = rnd.uniform(7, 13) / alt
                R = Matrix.Rotation(rnd.uniform(0, 2 * math.pi), 4, "Z")
                instancia(col, f"mata.{n}", Matrix.Translation((cx + rnd.normal(0, 14), cy + rnd.normal(0, 14), 0)) @ R
                          @ Matrix.Diagonal((e, e, e, 1)) @ Matrix.Translation((0, 0, -base)))
                n += 1
        print(f"mata: {n} árvores em 14 capões no horizonte", flush=True)
    if arb:
        for k, (M, h, pe) in enumerate(arbustos):
            col, alt, base = arb[k % len(arb)]
            e = h * rnd.uniform(.6, 1.3) / alt
            loc = M.to_translation()
            if loc.length > 70 and rnd.uniform() < .4:  # longe da obra (> 70 m), menos touceiras: a grade regular do kit some
                continue
            R = Matrix.Rotation(rnd.uniform(0, 2 * math.pi), 4, "Z")
            instancia(col, f"arbusto.{k}", Matrix.Translation((loc.x, loc.y, max(0.0, loc.z + pe))) @ R @ Matrix.Diagonal((e, e, e, 1))
                      @ Matrix.Translation((0, 0, -base)))
    if arb and SOLO:  # touceiras baixas ao longo da borda do solo: a régua terra/pasto vira transição
        x0, x1, y0, y1 = SOLO
        cena = bpy.context.scene
        bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
        cam_xy = [(M[0, 3], M[1, 3]) for M in C @ matrizes(dados["camera"]["matrizes"], dados["meta"]["quadros"])]
        lados = [((x0, y0), (x1, y0), (0, -1)), ((x1, y0), (x1, y1), (1, 0)), ((x1, y1), (x0, y1), (0, 1)), ((x0, y1), (x0, y0), (-1, 0))]
        compr = [math.dist(a_, b_) for a_, b_, _ in lados]
        for k in range(180):
            i = int(rnd.choice(4, p=np.array(compr) / sum(compr)))
            (ax, ay), (bx, by), (nx, ny) = lados[i]
            t, fora = rnd.uniform(), rnd.uniform(.3, 2.5)  # só do lado de fora: dentro ficam muro, picape e contêiner
            px, py = ax + (bx - ax) * t + nx * fora, ay + (by - ay) * t + ny * fora
            if any(v[0] - 2 < px < v[1] + 2 and v[2] - 2 < py < v[3] + 2 for v in VIAS):  # o tufo é largo: 2 m de folga
                continue
            if min(math.dist((px, py), c) for c in cam_xy) < 2.5:  # nada no caminho da câmera na descida
                continue
            achou, ponto, *_ = cena.ray_cast(dg, Vector((px, py, 10)), Vector((0, 0, -1)))
            if achou and ponto.z > .05:  # algo em cima do chão ali (muro, veículo, monte, outro tufo)
                continue
            col, alt, base = arb[k % len(arb)]
            e = rnd.uniform(.25, .7) / alt
            instancia(col, f"borda.{k}", Matrix.Translation((px, py, 0))
                      @ Matrix.Rotation(rnd.uniform(0, 2 * math.pi), 4, "Z") @ Matrix.Diagonal((e, e, e, 1)) @ Matrix.Translation((0, 0, -base)))
    print(f"vegetação: {len(dados['arvores']) if arv else 0} árvores e {len(arbustos) if arb else 0} arbustos do Poly Haven", flush=True)


def construir(dados, indice, pasta, quadros, cinema=False):
    """cinema: as árvores do kit (itens com asset "arvore-…") e o arbusto instanciado (folha, parado) ficam de fora e
    voltam como modelos reais em vegetacao()."""
    N = dados["meta"]["quadros"]
    arbustos, lanca, pneu, aro, instancias_kit, medidas = [], None, None, None, {}, {}
    col = bpy.context.scene.collection
    geos = {}
    for k, g in dados["geometrias"].items():
        n = g["vertices"]
        geos[k] = (f32(g["posicao"], (n, 3)), f32(g["normal"], (n, 3)) if g["normal"] else None,
                   f32(g["uvMetros"], (n, 2)), f32(g["uv"], (n, 2)) if g["uv"] else None)
    global SOLO
    solos = []
    if cinema:
        for it in dados["itens"]:
            tipo = dados["materiais"][it["material"]]["tipo"]
            if tipo in ("solo", "asfalto") and not it["animado"] and not it["instancias"]:
                M = matrizes(it["matrizes"], 1)[0]
                P = geos[it["geometria"]][0] @ M[:3, :3].T + M[:3, 3]  # three
                ret = (P[:, 0].min(), P[:, 0].max(), -P[:, 2].max(), -P[:, 2].min())  # Blender: y = −z do three
                if tipo == "solo":
                    if (ret[1] - ret[0]) * (ret[3] - ret[2]) > 200:  # só um terreno de verdade (não a terra de um vaso)
                        solos.append(ret)
                else:
                    VIAS.append(ret)
    # a borda irregular só quando o solo é uma peça só (modulares); com praça e estrada no mesmo material (sige) não
    SOLO = solos[0] if len(solos) == 1 else None
    mats = [material(d, indice, pasta, quadros) for d in dados["materiais"]]
    malhas = {}
    for it in dados["itens"]:
        pos, nor, uv_m, uv = geos[it["geometria"]]
        if len(pos) < 3:
            continue
        n_inst = max(1, it["instancias"])
        Ms = matrizes(it["matrizes"], (N if it["animado"] else 1) * n_inst).reshape(-1, n_inst, 4, 4)
        mat = mats[it["material"]]
        if cinema and it["animado"] and dados["materiais"][it["material"]]["tipo"] == "aco":
            ext = np.sort(pos.max(0) - pos.min(0))
            if ext[2] >= 5 and ext[1] <= .6:  # os segmentos da lança (5–12 m, finos): tinta amarela de equipamento
                if lanca is None:
                    lanca = material(dict(dados["materiais"][it["material"]], nome="lanca", tipo=None, mapa=None,
                                          cor=list(AMARELO), metal=.2, rugosidade=.45), indice, pasta, quadros)
                mat = lanca
        roda = None
        if cinema and len(pos) == 240:
            ext = pos.max(0) - pos.min(0)
            if abs(ext[0] - ext[2]) < .02 and ext[1] < ext[0] * .6 and ext[0] >= .45:  # cilindro de roda (eixo Y local)
                roda = (pos.max(0) + pos.min(0)) / 2, ext[0] / 2, ext[1]
                if pneu is None:
                    pneu = material(dict(dados["materiais"][it["material"]], nome="pneu", tipo=None, mapa=None,
                                         cor=[.025, .025, .027], metal=0, rugosidade=.85, emissivo=[0, 0, 0]), indice, pasta, quadros)
                    aro = material(dict(dados["materiais"][it["material"]], nome="aro", tipo=None, mapa=None,
                                        cor=[.35, .35, .34], metal=.7, rugosidade=.4, emissivo=[0, 0, 0]), indice, pasta, quadros)
                mat = pneu
        base_asset = (it.get("asset") or "").rsplit("-", 1)[0].split(":")[0]
        if it.get("asset"):
            medidas[it["asset"]] = [float(v) for v in pos.max(0) - pos.min(0)]
        if cinema and MOD is not None and (base_asset in MOD.INSTANCIADOS or base_asset == "pedra"):  # instanciados: o modelo vai nas matrizes de cada instância
            instancias_kit.setdefault(base_asset, []).extend(Matrix((C @ M @ C.T).tolist()) for M in Ms[0])
        doc = bool(dados["materiais"][it["material"]]["mapa"]) and not dados["materiais"][it["material"]]["mapa"].startswith("canvas-")
        if cinema and not doc and (base_asset.startswith(("arvore", "caminhao", "guindaste", "picape")) or base_asset in SUBSTITUIDOS):
            continue  # árvores, veículos e objetos do canteiro voltam como modelos (vegetacao, veiculos.py, objetos.py)
        if cinema and it["instancias"] and not it["animado"] and dados["materiais"][it["material"]]["tipo"] == "folha":
            pe, altura = float(pos[:, 1].min()), float(pos[:, 1].max() - pos[:, 1].min())  # a malha pode ter a origem no meio
            arbustos += [(Matrix((C @ M).tolist()), altura * float(np.linalg.norm(M[:3, 1])),
                          pe * float(np.linalg.norm(M[:3, 1]))) for M in Ms[0]]
            continue
        if it["instancias"] and not it["animado"]:  # instâncias paradas: uma malha só, já no espaço do mundo (three)
            P = np.concatenate([pos @ M[:3, :3].T + M[:3, 3] for M in Ms[0]])
            Nn = None if nor is None else np.concatenate([nor @ np.linalg.inv(M[:3, :3]) for M in Ms[0]])
            me = malha(it["nome"], P, Nn, np.tile(uv_m, (n_inst, 1)), None if uv is None else np.tile(uv, (n_inst, 1)))
            me.materials.append(mat)
            ob = bpy.data.objects.new(it["nome"], me); col.objects.link(ob)
            ob.matrix_world = Matrix(C.tolist())
            continue
        if it["geometria"] not in malhas:
            malhas[it["geometria"]] = malha(it["geometria"][:8], pos, nor, uv_m, uv)
            malhas[it["geometria"]].materials.append(None)  # o material vai no objeto: a malha é partilhada
        for i in range(n_inst):
            ob = bpy.data.objects.new(it["nome"] + (f".{i}" if it["instancias"] else ""), malhas[it["geometria"]])
            col.objects.link(ob)
            ob.material_slots[0].link = "OBJECT"; ob.material_slots[0].material = mat
            if roda:
                aro_da_roda(ob, *roda, aro)
            if mat.get("emissao"):  # o documento-alvo: fora do AgX na composição (ver compor) e sem fazer sombra
                ob.visible_shadow = False
                ob.pass_index = 1
            if it["animado"]:
                animar(ob, C @ Ms[:, i], quadros, it["visivel"])
            else:
                ob.matrix_world = Matrix((C @ Ms[0, i]).tolist())
                if it["visivel"] is not None:
                    for q in quadros:
                        ob.hide_render = not it["visivel"][q]; ob.keyframe_insert("hide_render", frame=q)
    if cinema:
        pasto = [k for k, d in enumerate(dados["materiais"]) if d["tipo"] == "pasto"]
        if pasto:  # o pasto do kit acaba a 300 m (a régua no horizonte): um chão de 8 km logo abaixo, com o mesmo material
            L = 4000.0
            P = np.array([[-L, -.2, -L], [L, -.2, L], [L, -.2, -L], [-L, -.2, -L], [-L, -.2, L], [L, -.2, L]])  # abaixo das trilhas do solo (−0,1 m)
            me = malha("pasto-horizonte", P, None, P[:, [0, 2]] * [1, -1], None)
            me.materials.append(mats[pasto[0]])
            ob = bpy.data.objects.new("pasto-horizonte", me); col.objects.link(ob)
            ob.matrix_world = Matrix(C.tolist())
        if dados.get("grupos") and MOD is not None:  # veículos e objetos modelados (veiculos.py, objetos.py), presos aos grupos animados
            import veiculos
            import objetos
            raizes = {}
            for g in dados["grupos"]:
                ob = bpy.data.objects.new(g["id"], None); col.objects.link(ob)
                Ms = C @ matrizes(g["matrizes"], N) @ C.T
                if np.allclose(Ms, Ms[0]):  # parado: uma matriz só
                    ob.matrix_world = Matrix(Ms[0].tolist())
                else:
                    animar(ob, Ms, quadros, None)
                raizes.setdefault(g["asset"], []).append(ob)
                if g["id"] in medidas:  # o tamanho da peça do kit (para modelos que dependem dele, ex.: as águas)
                    ob["dims"] = medidas[g["id"]]
            do_kit = {d["tipo"]: mats[k] for k, d in enumerate(dados["materiais"]) if d["tipo"]}
            vm = veiculos.materiais(desgaste, do_kit.get("madeira"))
            print(f"veículos: {veiculos.montar({k: v[0] for k, v in raizes.items()}, vm)} peças modeladas", flush=True)
            modelo_foto = next((d for d in dados["materiais"] if d["tipo"] == "concreto"),
                               next(d for d in dados["materiais"] if d["tipo"]))  # molde para os materiais de foto
            for tipo, metal in (("conteiner", .3), ("zinco", .6), ("areia", 0), ("brita", 0)):
                vm[tipo] = material(dict(modelo_foto, nome=tipo, tipo=tipo, metal=metal), indice, pasta, quadros)
            vm["concreto"] = do_kit.get("concreto", vm["cinza"])
            vm["tronco"] = do_kit.get("tronco", vm["madeira"])
            pedras = [colecao_do_modelo(m) for m in indice.get("modelos", {}).get("pedra", [])]
            ctx = {"solo": SOLO, "vias": VIAS, "cena": bpy.context.scene, "indice": indice, "colecao": colecao_do_modelo}
            if hasattr(MOD, "carregar"):
                MOD.carregar(ctx)
            n = objetos.montar(raizes, instancias_kit, vm, pedras, MOD.MODELOS, MOD.INSTANCIADOS, getattr(MOD, "SUJOS", ()))
            print(f"objetos modelados ({MOD.__name__}): {n} peças", flush=True)
            if hasattr(MOD, "extras"):
                MOD.extras(vm, ctx)
        vegetacao(dados, indice, arbustos)


def camera(dados, quadros):
    c = dados["camera"]
    cam = bpy.data.cameras.new("camera")
    cam.sensor_fit = "VERTICAL"
    cam.clip_start, cam.clip_end = c["perto"], c["longe"]
    ob = bpy.data.objects.new("camera", cam)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.scene.camera = ob
    Ms = C @ matrizes(c["matrizes"], dados["meta"]["quadros"])
    animar(ob, Ms, quadros, None)
    for q in quadros:
        cam.lens = cam.sensor_height / (2 * math.tan(math.radians(c["fov"][q]) / 2)); cam.keyframe_insert("lens", frame=q)


FOCO_MINIMO = .3  # m; nas cenas externas (aéreas) 8 m, para cabo/cabine/módulo passando não puxarem o foco (ver main)


def foco(quadros, fstop=4.0):
    """--visual cinema: profundidade de campo com foco no que está no centro do quadro (raio da câmera), quadro a quadro.
    A f/4 com essa lente, nas aéreas (foco a dezenas de metros) tudo fica nítido; só o close desfoca o fundo."""
    cena = bpy.context.scene
    cam = cena.camera
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = fstop
    ultimo, dist = 50.0, []
    for q in quadros:
        cena.frame_set(q)
        dg = bpy.context.evaluated_depsgraph_get()
        M = cam.matrix_world
        origem, frente = M.to_translation(), -(M.to_3x3() @ Vector((0, 0, 1))).normalized()
        achou, ponto, _, _, ob, _ = cena.ray_cast(dg, origem, frente)
        ultimo = (ponto - origem).length if achou else ultimo
        # nas aéreas, nada a menos de 8 m puxa o foco (cabo, cabine, módulo passando); só a placa do documento puxa
        doc = achou and ob is not None and ob.pass_index == 1
        dist.append(math.log(max(ultimo, .3) if doc else max(ultimo, FOCO_MINIMO)))
    # um raio só pode pegar o cabo ou a lança por um quadro: mediana e média de 7 quadros (em log) evitam o foco aos saltos
    suave, ini = [], 0
    for fim in range(1, len(quadros) + 1):  # só dentro de trechos contínuos (o teste renderiza quadros soltos)
        if fim == len(quadros) or quadros[fim] != quadros[fim - 1] + 1:
            d = np.array(dist[ini:fim])
            med = np.array([np.median(d[max(0, i - 3):i + 4]) for i in range(len(d))])
            suave += [med[max(0, i - 3):i + 4].mean() for i in range(len(med))]
            ini = fim
    for q, v in zip(quadros, suave):
        cam.data.dof.focus_distance = math.exp(v)
        cam.data.dof.keyframe_insert("focus_distance", frame=q)


def azimute_do_sol(img):
    """Azimute (rad, no mundo do Blender sem rotação) do ponto mais claro do HDRI equirretangular."""
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(px)
    lum = px.reshape(h, w, 4)[:, :, :3].sum(axis=2)
    passo = max(1, w // 1024)
    lum = lum[::passo, ::passo]
    y, x = np.unravel_index(np.argmax(lum), lum.shape)
    a = ((x + .5) / lum.shape[1] - .5) * 2 * math.pi  # u = atan2(dir.y, −dir.x) / 2π + ½
    return math.atan2(math.sin(a), -math.cos(a)), math.degrees(((y + .5) / lum.shape[0] - .5) * math.pi)


def cor_do_horizonte(img, forca):
    """Radiância média (linear) da faixa de 0° a 6° acima do horizonte do HDRI: a cor da névoa de distância, para o que
    está longe se fundir com o céu atrás."""
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32); img.pixels.foreach_get(px)
    linhas = px.reshape(h, w, 4)[:, :, :3]  # a linha 0 é a de baixo (−90°); o horizonte fica em h/2
    faixa = linhas[h // 2: h // 2 + max(1, int(h * 6 / 180))]
    return (np.median(faixa.reshape(-1, 3), axis=0) * forca).tolist()


def lampada_do_sol(az, elev, forca=5.5, kelvin=4000):
    """--visual cinema: o disco do sol do HDRI fica cortado (ver mundo) e uma Sun no mesmo azimute e altura dá a luz
    direta: sombra definida (1,2°), cor quente controlada; o céu, tingido de frio, vira o preenchimento das sombras."""
    luz = bpy.data.lights.new("sol", "SUN")
    luz.energy = forca; luz.angle = math.radians(1.2)
    try:
        luz.use_temperature = True; luz.temperature = kelvin
    except AttributeError:
        luz.color = (1.0, .80, .62)
    ob = bpy.data.objects.new("sol", luz)
    bpy.context.scene.collection.objects.link(ob)
    e = math.radians(elev)
    para_o_sol = Vector((math.cos(e) * math.cos(az), math.cos(e) * math.sin(az), math.sin(e)))
    ob.rotation_mode = "QUATERNION"; ob.rotation_quaternion = para_o_sol.to_track_quat("Z", "Y")


def mundo(dados, indice, ceu=None, forca=1.0, cinema=False):
    w = bpy.data.worlds.new("ceu"); bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    img = bpy.data.images.load(str(ASSETS / "hdri" / f"{ceu}.hdr") if ceu else str(ASSETS / indice["hdri"]))
    az_hdri, elev = azimute_do_sol(img)
    s = dados["sol"]["posicao"]  # three → Blender: (x, −z, y)
    az_cena = math.atan2(-s[2], s[0])
    coord = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, az_hdri - az_cena)
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = img
    fundo = nt.nodes.new("ShaderNodeBackground"); fundo.inputs["Strength"].default_value = forca
    sai = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(coord.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    cor = env.outputs["Color"]
    if cinema:  # corta o disco do sol do HDRI (ele vira a lâmpada Sun); o resto do céu passa inteiro
        corte = nt.nodes.new("ShaderNodeVectorMath"); corte.operation = "MINIMUM"; corte.inputs[1].default_value = (20, 20, 20)
        nt.links.new(cor, corte.inputs[0]); cor = corte.outputs["Vector"]
        frio = nt.nodes.new("ShaderNodeVectorMath"); frio.operation = "MULTIPLY"; frio.inputs[1].default_value = FRIO
        nt.links.new(cor, frio.inputs[0]); cor = frio.outputs["Vector"]  # sombra fria × luz quente: a riqueza da referência
        lampada_do_sol(az_cena, elev)
    nt.links.new(cor, fundo.inputs["Color"]); nt.links.new(fundo.outputs[0], sai.inputs["Surface"])
    print(f"céu: {Path(img.filepath).stem}, sol do HDRI a {elev:.0f}° de altura; "
          f"girado {math.degrees(az_hdri - az_cena):.0f}° para o azimute da cena", flush=True)
    h = cor_do_horizonte(img, forca)
    return [c * f for c, f in zip(h, FRIO)] if cinema else h


# --visual cinema: as salas (casos internos) recebem a luz do teto que o three.js tinha como luz ambiente/preenchimento:
# uma luz de área retangular quente sob o forro. (centro x, y, z no three; largura x, profundidade z; potência W)
LUZ_DO_TETO = {"veks": ((0, 2.95, -1.0), (3.0, 2.0), 650), "abertura": ((0, 2.95, .5), (2.4, 2.4), 450)}


def luz_do_teto(caso):
    if caso not in LUZ_DO_TETO:
        return
    (x, y, z), (lx, lz), w = LUZ_DO_TETO[caso]
    luz = bpy.data.lights.new("teto", "AREA")
    luz.shape = "RECTANGLE"; luz.size, luz.size_y = lx, lz; luz.energy = w
    try:
        luz.use_temperature = True; luz.temperature = 4000
    except AttributeError:
        luz.color = (1.0, .85, .7)
    ob = bpy.data.objects.new("teto", luz)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = (x, -z, y)  # three → Blender; a luz de área aponta para −Z (para baixo)


def bruma_no_ceu(cor, forca):
    """--visual cinema: o céu perto do horizonte (até ~6°) vai para a cor da névoa, a mesma que o compositor põe no chão
    distante; a régua entre chão e céu some."""
    nt = bpy.context.scene.world.node_tree
    fundo = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeBackground")
    ceu = fundo.inputs["Color"].links[0].from_socket
    direcao = nt.nodes.new("ShaderNodeTexCoord").outputs["Generated"]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(direcao, sep.inputs["Vector"])
    fx = nt.nodes.new("ShaderNodeMapRange"); fx.inputs["From Min"].default_value = -.02; fx.inputs["From Max"].default_value = .1
    fx.inputs["To Min"].default_value = 1; fx.inputs["To Max"].default_value = 0
    nt.links.new(sep.outputs["Z"], fx.inputs["Value"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = "RGBA"
    nt.links.new(fx.outputs["Result"], mx.inputs["Factor"]); nt.links.new(ceu, mx.inputs["A"]); mx.inputs["B"].default_value = (*(c / forca for c in cor), 1)  # o Background multiplica pela força
    nt.links.new(mx.outputs["Result"], fundo.inputs["Color"])


def placa(dispositivo):
    cena = bpy.context.scene
    if dispositivo == "CPU":
        cena.cycles.device = "CPU"
        return
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = dispositivo
    prefs.get_devices()
    placas = [d for d in prefs.devices if d.type == dispositivo]
    if not placas:
        sys.exit(f"--dispositivo {dispositivo}: nenhuma placa encontrada (driver NVIDIA ≥ 575?); "
                 f"dispositivos: {[(d.name, d.type) for d in prefs.devices]}. Usar --dispositivo CUDA ou CPU.")
    for d in prefs.devices:
        d.use = d.type == dispositivo
    cena.cycles.device = "GPU"
    print("Cycles em", ", ".join(d.name for d in placas), flush=True)


def configurar(a, dados):
    cena = bpy.context.scene
    r = cena.render
    r.engine = "CYCLES"
    placa(a.dispositivo)
    r.resolution_x, r.resolution_y, r.resolution_percentage = dados["meta"]["largura"], dados["meta"]["altura"], a.escala
    r.fps = dados["meta"]["fps"]
    cena.frame_start, cena.frame_end = 0, dados["meta"]["quadros"] - 1
    cy = cena.cycles
    cy.samples = a.amostras
    cy.use_adaptive_sampling = True; cy.adaptive_threshold = .015 if a.visual == "cinema" else .01
    cy.use_denoising = True; cy.denoiser = "OPENIMAGEDENOISE"; cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    cy.use_animated_seed = False; cy.seed = 7  # o mesmo ruído em todos os quadros: o que sobra do denoise não cintila
    cy.max_bounces = 8; cy.diffuse_bounces = 4; cy.glossy_bounces = 4
    cy.sample_clamp_indirect = 10
    r.use_persistent_data = True
    r.use_motion_blur = not a.sem_desfoque; r.motion_blur_shutter = .35
    cena.view_settings.view_transform = "Standard"  # o AgX entra na composição, menos sobre o documento (ver compor)
    cena.view_settings.look = "None"
    r.image_settings.file_format = "PNG"; r.image_settings.color_mode = "RGB"; r.image_settings.color_depth = "8"
    r.film_transparent = False


def mistura(g, modo, a, b, fator):
    m = g.nodes.new("ShaderNodeMix"); m.data_type = "RGBA"; m.blend_type = modo
    m.inputs["Factor"].default_value = fator
    for entrada, v in (("A", a), ("B", b)):
        if isinstance(v, (tuple, list)):
            m.inputs[entrada].default_value = (*v, 1)
        else:
            g.links.new(v, m.inputs[entrada])
    return m


def conta(g, op, a, b):
    m = g.nodes.new("ShaderNodeMath"); m.operation = op
    for k, v in enumerate((a, b)):
        if isinstance(v, (int, float)):
            m.inputs[k].default_value = v
        else:
            g.links.new(v, m.inputs[k])
    return m.outputs[0]


def compor(cinema=None):
    """A curva de tons AgX em tudo, menos no documento-alvo (objetos com pass_index 1): a emissão dele sai com as cores
    exatas da imagem, como na página, que põe o documento real por cima do último quadro. A cena fica em "Standard" e o
    AgX é aplicado aqui (linear → AgX Base sRGB, relido como sRGB); a máscara vem do passe de índice do objeto.
    cinema = {"horizonte": cor linear, "nevoa": (início, profundidade) em m}: antes do AgX, a névoa de distância (passe
    Mist, só nos objetos: o céu já é céu) puxa o que está longe para a cor do horizonte; depois, contraste, saturação e
    vinheta. O documento-alvo fica de fora de tudo isso."""
    cena = bpy.context.scene
    vl = cena.view_layers[0]
    vl.use_pass_object_index = True
    g = bpy.data.node_groups.new("composicao", "CompositorNodeTree")
    g.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    if cinema:
        aov = vl.aovs.add(); aov.name = "documento"; aov.type = "VALUE"
    if cinema:  # filme transparente: Alpha é a cobertura dos objetos (suavizada) e o céu volta pelo passe Environment
        vl.use_pass_mist = True; vl.use_pass_environment = True
        cena.render.film_transparent = True
        ms = cena.world.mist_settings
        ms.start, ms.depth = cinema["nevoa"]; ms.falloff = "INVERSE_QUADRATIC"  # √: o ar já pesa nos capões a 160–400 m
        cena.camera.data.clip_end = 10000  # o chão de 8 km vai até o horizonte
    rl = g.nodes.new("CompositorNodeRLayers"); rl.scene = cena
    imagem_linear = rl.outputs["Image"]
    if cinema:
        # com o filme transparente o fundo entra no Mist como 0: num pixel de borda m = a·m_obj → m_obj = m / a.
        # Assim a névoa pega só a parte do pixel que é objeto e a folha da mata não vira pontilhado.
        a = rl.outputs["Alpha"]
        m_obj = conta(g, "DIVIDE", rl.outputs["Mist"], conta(g, "MAXIMUM", a, 1e-4))
        fator = conta(g, "MULTIPLY", conta(g, "MINIMUM", conta(g, "MAXIMUM", m_obj, 0.0), 1.0), cinema["forca"])
        nevoa = mistura(g, "MULTIPLY", cinema["horizonte"], a, 1)  # a cor da névoa, pré-multiplicada pela cobertura
        nev = mistura(g, "MIX", imagem_linear, nevoa.outputs["Result"], 0)
        g.links.new(fator, nev.inputs["Factor"])
        ceu = mistura(g, "MULTIPLY", rl.outputs["Environment"], conta(g, "SUBTRACT", 1.0, a), 1)
        imagem_linear = mistura(g, "ADD", nev.outputs["Result"], ceu.outputs["Result"], 1).outputs["Result"]
        imagem_linear = mistura(g, "MULTIPLY", imagem_linear, (.81, .81, .81), 1).outputs["Result"]  # exposição −0,3
        gl = g.nodes.new("CompositorNodeGlare")  # bloom leve: o brilho do sol nos vidros e no metal "vaza" como na lente
        gl.inputs["Type"].default_value = "Bloom"; gl.inputs["Threshold"].default_value = 1.0
        gl.inputs["Strength"].default_value = .25; gl.inputs["Size"].default_value = .6
        g.links.new(imagem_linear, gl.inputs["Image"]); imagem_linear = gl.outputs["Image"]
    ida = g.nodes.new("CompositorNodeConvertColorSpace"); ida.from_color_space = "Linear Rec.709"; ida.to_color_space = "AgX Base sRGB"
    volta = g.nodes.new("CompositorNodeConvertColorSpace"); volta.from_color_space = "sRGB"; volta.to_color_space = "Linear Rec.709"
    mascara = g.nodes.new("CompositorNodeIDMask"); mascara.inputs["Index"].default_value = 1; mascara.inputs["Anti-Alias"].default_value = True
    por_cima = g.nodes.new("CompositorNodeAlphaOver")
    sai = g.nodes.new("NodeGroupOutput")
    indice = next(o for o in rl.outputs if o.name in ("Object Index", "IndexOB"))
    g.links.new(imagem_linear, ida.inputs["Image"]); g.links.new(ida.outputs["Image"], volta.inputs["Image"])
    g.links.new(indice, mascara.inputs["ID value"])
    fundo = volta.outputs["Image"]
    if cinema:
        cv = g.nodes.new("CompositorNodeCurveRGB")  # curva S suave: pretos mais ricos, realces preservados
        curva = cv.mapping.curves[3]
        curva.points.new(.25, .21); curva.points.new(.75, .79)
        cv.mapping.update()
        g.links.new(fundo, cv.inputs["Image"])
        bc = cv
        hs = g.nodes.new("CompositorNodeHueSat"); hs.inputs["Saturation"].default_value = 1.0
        g.links.new(bc.outputs["Image"], hs.inputs["Image"])
        el = g.nodes.new("CompositorNodeEllipseMask")
        el.inputs["Size"].default_value = (1.15, 1.25); el.inputs["Value"].default_value = 1
        bl = g.nodes.new("CompositorNodeBlur")
        try:
            bl.inputs["Size"].default_value = (360, 360)
        except TypeError:
            bl.inputs["Size"].default_value = 360
        g.links.new(el.outputs["Mask"], bl.inputs["Image"])
        vin = mistura(g, "MULTIPLY", hs.outputs["Image"], bl.outputs["Image"], .18)
        tom = g.nodes.new("CompositorNodeColorBalance")  # sombras levemente frias, realces levemente quentes
        for ident, v in (("Color Lift", (.99, 1, 1.015, 1)), ("Color Gain", (1.02, 1, .97, 1))):
            next(i for i in tom.inputs if i.identifier == ident).default_value = v
        g.links.new(vin.outputs["Result"], tom.inputs["Image"])
        vin = tom
        # grão de filme: esconde o banding do céu e da névoa no H.264 de 8 bits
        px = g.nodes.new("CompositorNodeImageCoordinates"); g.links.new(rl.outputs["Image"], px.inputs["Image"])
        ruido = g.nodes.new("ShaderNodeTexWhiteNoise"); ruido.noise_dimensions = "4D"
        g.links.new(px.outputs["Pixel"], ruido.inputs["Vector"])
        g.links.new(conta(g, "FLOOR", conta(g, "DIVIDE", g.nodes.new("CompositorNodeSceneTime").outputs["Frame"], 6), 0), ruido.inputs["W"])
        grao = conta(g, "MULTIPLY_ADD", ruido.outputs["Value"], .02)  # ±1 %, troca a cada 6 quadros (bitrate do MP4)
        grao.node.inputs[2].default_value = .99
        fundo = mistura(g, "MULTIPLY", vin.outputs[0], grao, 1).outputs["Result"]
    g.links.new(fundo, por_cima.inputs["Background"]); g.links.new(rl.outputs["Image"], por_cima.inputs["Foreground"])
    if cinema:  # o AOV acompanha o desfoque de movimento e de lente; o índice de objeto (binário) deixava franja pontilhada
        g.links.new(rl.outputs["documento"], por_cima.inputs["Factor"])
    else:
        g.links.new(mascara.outputs["Alpha"], por_cima.inputs["Factor"])
    g.links.new(por_cima.outputs["Image"], sai.inputs[0])
    cena.compositing_node_group = g
    cena.render.use_compositing = True
    cena.render.compositor_device = "CPU"  # sem OpenGL: funciona também sem interface e sem placa


def lista_de_quadros(texto, total):
    if not texto:
        return list(range(total))
    faixa, _, passo = texto.partition(":")
    ini, _, fim = faixa.partition("-")
    qs = list(range(int(ini), int(fim or ini) + 1, int(passo or 1)))
    if any(q < 0 or q >= total for q in qs):
        sys.exit(f"--quadros fora de 0..{total - 1}")
    return qs


def main():
    a = argumentos()
    pasta = RAIZ / "cenas" / "saida" / "export" / a.caso
    if not (pasta / "cena.json").exists():
        sys.exit(f"{pasta / 'cena.json'} não existe: rodar antes  python portfolio/cenas/exportar.py --so {a.caso}")
    if not (ASSETS / "indice.json").exists():
        sys.exit("assets não baixados: rodar antes  python portfolio/blender/baixar_assets.py")
    dados = json.loads((pasta / "cena.json").read_text(encoding="utf-8"))
    indice = json.loads((ASSETS / "indice.json").read_text(encoding="utf-8"))
    render = lista_de_quadros(a.quadros, dados["meta"]["quadros"])
    # chaves em todos os quadros do vídeo (e nos vizinhos dos pedidos, para o desfoque de movimento)
    todos = range(dados["meta"]["quadros"])
    chaves = list(todos) if len(render) > 24 or a.todas_chaves else sorted({q for r in render for q in (r - 1, r, r + 1) if q in todos})

    global CHANFRO, MOD, SUBSTITUIDOS, FOCO_MINIMO
    cinema = a.visual == "cinema"
    FOCO_MINIMO = 8.0 if a.caso in ("modulares", "sige") else .3
    CHANFRO = .03 if cinema else 0.0
    ceu = a.ceu or (indice.get("hdri_cinema") if cinema else None)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    configurar(a, dados)
    if cinema and a.caso in MODULO:
        try:
            MOD = importlib.import_module(MODULO[a.caso])
            SUBSTITUIDOS = MOD.SUBSTITUIDOS
        except ModuleNotFoundError:
            MOD = None
    construir(dados, indice, pasta, chaves, cinema)
    camera(dados, chaves)
    forca = a.ceu_forca if a.ceu_forca is not None else (.9 if cinema else 1.0)  # cinema: o céu é o preenchimento
    horizonte = mundo(dados, indice, ceu, forca, cinema)
    # névoa: 30 % a cor do horizonte do HDRI, 70 % um azul-acinzentado frio com o mesmo brilho (perspectiva aérea)
    lum = .2126 * horizonte[0] + .7152 * horizonte[1] + .0722 * horizonte[2]
    nevoa_cor = [.3 * h + .7 * lum * f for h, f in zip(horizonte, (.86, .96, 1.12))]
    if cinema:
        bruma_no_ceu(nevoa_cor, forca)
        luz_do_teto(a.caso)
        foco(chaves)
    compor({"horizonte": nevoa_cor, "nevoa": (60, 2000), "forca": 1.0} if cinema else None)
    print(f"{a.caso}: {len(bpy.data.objects)} objetos, {len(bpy.data.materials)} materiais", flush=True)
    if a.salvar:
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(a.salvar).resolve()))
    if a.sem_render:
        return
    saida = Path(a.saida).resolve() if a.saida else RAIZ / "cenas" / "saida" / f"{a.caso}-blender-quadros"
    saida.mkdir(parents=True, exist_ok=True)
    cena = bpy.context.scene
    for q in render:
        png = saida / f"q{q:04d}.png"
        if png.exists() and png.stat().st_size > 0:
            continue
        cena.frame_set(q)
        cena.render.filepath = str(saida / f"parcial-{q:04d}.png")
        bpy.ops.render.render(write_still=True)
        Path(cena.render.filepath).replace(png)  # só aparece com o nome final depois de inteiro em disco
        print(f"quadro {q} → {png.name}", flush=True)
    print("pronto:", saida, flush=True)


main()
