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
from mathutils import Matrix

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent  # portfolio/
ASSETS = AQUI / "assets"
# three.js (Y para cima) → Blender (Z para cima): (x, y, z) → (x, −z, y). A malha fica nas coordenadas locais do three.
C = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.float64)


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
        return m

    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs[0], saida.inputs["Surface"])
    p.inputs["Metallic"].default_value = d["metal"]
    p.inputs["Roughness"].default_value = d["rugosidade"]
    p.inputs["Base Color"].default_value = (*d["cor"], 1)
    if d["vidro"]:  # vidro de fachada do kit: escuro e espelhado
        p.inputs["Roughness"].default_value = .04
        p.inputs["Coat Weight"].default_value = 1
        return m
    if d["transparente"] and d["opacidade"] < 1:  # vidraça dos interiores
        p.inputs["Transmission Weight"].default_value = 1
        p.inputs["Roughness"].default_value = .02
        p.inputs["IOR"].default_value = 1.45
        p.inputs["Base Color"].default_value = (.95, .97, .98, 1)
        return m
    if any(d["emissivo"]):
        p.inputs["Emission Color"].default_value = (*d["emissivo"], 1); p.inputs["Emission Strength"].default_value = 1
    if foto:  # textura fotografada, no tamanho real
        mx, my = foto["metros"]
        vetor = no_uv(nt, "uvMetros", (1 / mx, 1 / my))
        mapas = foto["mapas"]
        cor = no_imagem(nt, imagem(ASSETS / mapas["cor"]), vetor).outputs["Color"]
        if foto.get("tom"):  # matiz e saturação do tom, luminosidade da foto
            h = foto["tom"].lstrip("#")
            srgb = [int(h[k:k + 2], 16) / 255 for k in (0, 2, 4)]
            linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb]
            tom = nt.nodes.new("ShaderNodeMix"); tom.data_type = "RGBA"; tom.blend_type = "COLOR"; tom.inputs["Factor"].default_value = .85
            tom.inputs["B"].default_value = (*linear, 1)
            nt.links.new(cor, tom.inputs["A"])
            cor = tom.outputs["Result"]
        if d["tipo"] in ("pasto", "solo", "asfalto"):  # manchas de dezenas de metros por cima do ladrilho: escondem a repetição
            ruido = nt.nodes.new("ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = .06; ruido.inputs["Detail"].default_value = 4
            nt.links.new(nt.nodes.new("ShaderNodeTexCoord").outputs["Object"], ruido.inputs["Vector"])
            faixa = nt.nodes.new("ShaderNodeMapRange"); faixa.inputs["To Min"].default_value = .7; faixa.inputs["To Max"].default_value = 1.25
            nt.links.new(ruido.outputs["Fac"], faixa.inputs["Value"])
            mul = nt.nodes.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs["Factor"].default_value = 1
            nt.links.new(cor, mul.inputs["A"]); nt.links.new(faixa.outputs["Result"], mul.inputs["B"])
            cor = mul.outputs["Result"]
        nt.links.new(cor, p.inputs["Base Color"])
        if "rugosidade" in mapas:
            nt.links.new(no_imagem(nt, imagem(ASSETS / mapas["rugosidade"], False), vetor).outputs["Color"], p.inputs["Roughness"])
        if "normal" in mapas:
            nm = nt.nodes.new("ShaderNodeNormalMap"); nm.uv_map = "uvMetros"
            nt.links.new(no_imagem(nt, imagem(ASSETS / mapas["normal"], False), vetor).outputs["Color"], nm.inputs["Color"])
            nt.links.new(nm.outputs["Normal"], p.inputs["Normal"])
    elif d["mapa"] and (pasta / f"{d['mapa']}.png").exists():  # sem foto: o mapa de cor pintado pelo kit, no ladrilho do kit
        L = d["ladrilho"] or 1
        vetor = no_uv(nt, "uvMetros", (1 / L, 1 / L))
        nt.links.new(no_imagem(nt, imagem(pasta / f"{d['mapa']}.png"), vetor).outputs["Color"], p.inputs["Base Color"])
        p.inputs["Roughness"].default_value = .55 if tipo in ("acoPintado", "plastico", "acento", "vermelho") else .9
    return m


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


def construir(dados, indice, pasta, quadros):
    N = dados["meta"]["quadros"]
    col = bpy.context.scene.collection
    geos = {}
    for k, g in dados["geometrias"].items():
        n = g["vertices"]
        geos[k] = (f32(g["posicao"], (n, 3)), f32(g["normal"], (n, 3)) if g["normal"] else None,
                   f32(g["uvMetros"], (n, 2)), f32(g["uv"], (n, 2)) if g["uv"] else None)
    mats = [material(d, indice, pasta, quadros) for d in dados["materiais"]]
    malhas = {}
    for it in dados["itens"]:
        pos, nor, uv_m, uv = geos[it["geometria"]]
        if len(pos) < 3:
            continue
        n_inst = max(1, it["instancias"])
        Ms = matrizes(it["matrizes"], (N if it["animado"] else 1) * n_inst).reshape(-1, n_inst, 4, 4)
        mat = mats[it["material"]]
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


def mundo(dados, indice):
    w = bpy.data.worlds.new("ceu"); bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree; nt.nodes.clear()
    img = bpy.data.images.load(str(ASSETS / indice["hdri"]))
    az_hdri, elev = azimute_do_sol(img)
    s = dados["sol"]["posicao"]  # three → Blender: (x, −z, y)
    az_cena = math.atan2(-s[2], s[0])
    coord = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, az_hdri - az_cena)
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = img
    fundo = nt.nodes.new("ShaderNodeBackground"); fundo.inputs["Strength"].default_value = 1
    sai = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(coord.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], fundo.inputs["Color"]); nt.links.new(fundo.outputs[0], sai.inputs["Surface"])
    print(f"céu: sol do HDRI a {elev:.0f}° de altura; girado {math.degrees(az_hdri - az_cena):.0f}° para o azimute da cena", flush=True)


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
    cy.use_adaptive_sampling = True; cy.adaptive_threshold = .01
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


def compor():
    """A curva de tons AgX em tudo, menos no documento-alvo (objetos com pass_index 1): a emissão dele sai com as cores
    exatas da imagem, como na página, que põe o documento real por cima do último quadro. A cena fica em "Standard" e o
    AgX é aplicado aqui (linear → AgX Base sRGB, relido como sRGB); a máscara vem do passe de índice do objeto."""
    cena = bpy.context.scene
    cena.view_layers[0].use_pass_object_index = True
    g = bpy.data.node_groups.new("composicao", "CompositorNodeTree")
    g.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = g.nodes.new("CompositorNodeRLayers"); rl.scene = cena
    ida = g.nodes.new("CompositorNodeConvertColorSpace"); ida.from_color_space = "Linear Rec.709"; ida.to_color_space = "AgX Base sRGB"
    volta = g.nodes.new("CompositorNodeConvertColorSpace"); volta.from_color_space = "sRGB"; volta.to_color_space = "Linear Rec.709"
    mascara = g.nodes.new("CompositorNodeIDMask"); mascara.inputs["Index"].default_value = 1; mascara.inputs["Anti-Alias"].default_value = True
    por_cima = g.nodes.new("CompositorNodeAlphaOver")
    sai = g.nodes.new("NodeGroupOutput")
    indice = next(o for o in rl.outputs if o.name in ("Object Index", "IndexOB"))
    g.links.new(rl.outputs["Image"], ida.inputs["Image"]); g.links.new(ida.outputs["Image"], volta.inputs["Image"])
    g.links.new(indice, mascara.inputs["ID value"])
    g.links.new(volta.outputs["Image"], por_cima.inputs["Background"]); g.links.new(rl.outputs["Image"], por_cima.inputs["Foreground"])
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
    chaves = list(todos) if len(render) > 24 else sorted({q for r in render for q in (r - 1, r, r + 1) if q in todos})

    bpy.ops.wm.read_factory_settings(use_empty=True)
    configurar(a, dados)
    construir(dados, indice, pasta, chaves)
    camera(dados, chaves)
    mundo(dados, indice)
    compor()
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
