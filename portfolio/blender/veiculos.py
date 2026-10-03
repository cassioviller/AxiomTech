"""Modelos procedurais dos veículos do caso modulares para o --visual cinema do montar.py: caminhão-prancha (cabine
avançada), guindaste sobre rodas (patolas, torre com cabine do operador e contrapeso, lança telescópica com cilindro
hidráulico) e picape. Substituem as caixas do kit e ficam presos aos grupos animados que o exportar.js grava em
`grupos` (caminhao, guindaste-base, guindaste-torre, guindaste-lanca, picape), então a animação é a mesma.

Tudo é modelado nas coordenadas locais do grupo no three.js (Y para cima, metros), com as mesmas medidas do kit
(caso-modulares.html): a prancha do caminhão tem o topo a 1,30 m, onde a caixa 1 viaja; as rodas ficam onde estavam.
B() converte para o Blender (Z para cima). Feito só com geometria e materiais próprios: nenhum asset de terceiros.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector


def B(x, y, z):
    """three (Y para cima) → Blender (Z para cima), no espaço local do grupo."""
    return Vector((x, -z, y))


CM = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))  # a mesma troca de eixos, como matriz


def giro(rot):
    """Euler XYZ do three (rad) → matriz 3×3 no Blender."""
    from mathutils import Euler
    return CM @ Euler(rot, "XYZ").to_matrix() @ CM.transposed()


# ---------- materiais ----------
def principled(nome, cor, rug=.5, metal=0.0, coat=0.0, emissao=None):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(p.outputs[0], nt.nodes.new("ShaderNodeOutputMaterial").inputs["Surface"])
    p.inputs["Base Color"].default_value = (*cor, 1)
    p.inputs["Roughness"].default_value = rug
    p.inputs["Metallic"].default_value = metal
    p.inputs["Coat Weight"].default_value = coat
    if emissao:
        p.inputs["Emission Color"].default_value = (*emissao[0], 1); p.inputs["Emission Strength"].default_value = emissao[1]
    return m, nt, p


_DESGASTE = None


def materiais(desgaste, madeira):
    """desgaste(nt, p, d, normal, pintado) é o do montar.py (poeira de laterita, AO, brilho variável); madeira é o
    material da madeira do kit (foto do Poly Haven, mapeada em metros pelo UV "uvMetros")."""
    global _DESGASTE
    _DESGASTE = desgaste
    M = {}

    def tinta(nome, cor, rug=.32, coat=.6, sujo=True):
        m, nt, p = principled(nome, cor, rug, coat=coat)
        p.inputs["Coat Roughness"].default_value = .08
        if sujo:
            desgaste(nt, p, {"tipo": None, "cor": list(cor), "mapa": None}, None, True)
        M[nome] = m

    tinta("branco", (.72, .72, .70))
    tinta("amarelo", (.75, .42, .01))  # amarelo de máquina: não vira oliva com a névoa e a poeira
    tinta("cinza", (.16, .17, .18), rug=.45, coat=.2)
    M["plastico"] = principled("plastico", (.025, .025, .027), .55)[0]
    M["chassi"] = principled("chassi", (.03, .03, .032), .5, metal=.5)[0]
    M["cromo"] = principled("cromo", (.85, .85, .85), .12, metal=1.0)[0]
    M["aco"] = principled("aco", (.42, .43, .44), .35, metal=.9)[0]
    M["aro"] = principled("aro", (.62, .62, .6), .3, metal=.85)[0]
    M["vidro"] = principled("vidro-veiculo", (.05, .06, .07), .03, metal=.35, coat=1.0)[0]
    M["farol"] = principled("farol", (.85, .85, .82), .05, coat=1.0)[0]
    M["lanterna"] = principled("lanterna", (.45, .015, .01), .1, coat=1.0)[0]
    M["ambar"] = principled("ambar", (.8, .3, .01), .1, coat=1.0)[0]
    m, nt, p = principled("borracha", (.017, .017, .018), .82)
    ruido = nt.nodes.new("ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = 60
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .25
    nt.links.new(ruido.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    M["borracha"] = m
    M["madeira"] = madeira or principled("madeira-prancha", (.25, .16, .09), .8)[0]
    tinta("laranja", (.8, .2, .015))
    tinta("azul", (.03, .12, .3), rug=.45, coat=.1)
    tinta("vermelho", (.55, .03, .02), rug=.4, coat=.3)
    tinta("verde", (.06, .16, .07), rug=.45, coat=.2)
    m, nt, p = principled("areia-fina", (.5, .4, .26), .95)  # areia de obra: bege, grão fino, manchas de umidade
    p.inputs["Specular IOR Level"].default_value = .25
    grao = nt.nodes.new("ShaderNodeTexNoise"); grao.inputs["Scale"].default_value = 90; grao.inputs["Detail"].default_value = 8
    grao.inputs["Roughness"].default_value = .7
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .8; bump.inputs["Distance"].default_value = .02
    nt.links.new(grao.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    manchas = nt.nodes.new("ShaderNodeTexNoise"); manchas.inputs["Scale"].default_value = 3
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    nt.links.new(manchas.outputs[0], mix.inputs["Factor"]); mix.inputs["A"].default_value = (.5, .4, .26, 1)
    mix.inputs["B"].default_value = (.62, .58, .54, 1)
    cor_grao = nt.nodes.new("ShaderNodeMix"); cor_grao.data_type = "RGBA"; cor_grao.blend_type = "MULTIPLY"
    faixa = nt.nodes.new("ShaderNodeMapRange"); faixa.inputs["To Min"].default_value = .75; faixa.inputs["To Max"].default_value = 1.15
    nt.links.new(grao.outputs[0], faixa.inputs["Value"])
    cor_grao.inputs["Factor"].default_value = 1
    nt.links.new(mix.outputs["Result"], cor_grao.inputs["A"]); nt.links.new(faixa.outputs["Result"], cor_grao.inputs["B"])
    nt.links.new(cor_grao.outputs["Result"], p.inputs["Base Color"])
    M["areia-fina"] = m
    m, nt, p = principled("concreto-poste", (.42, .42, .4), .85)
    ruido = nt.nodes.new("ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = 30; ruido.inputs["Detail"].default_value = 8
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .15
    nt.links.new(ruido.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    M["concreto-poste"] = m
    tinta("tijolo", (.42, .12, .06), rug=.85, coat=0)
    M["ambar-placa"] = principled("ambar-placa", (.85, .55, .02), .4)[0]
    m, nt, p = principled("manta", (.32, .32, .31), .85)
    desgaste(nt, p, {"tipo": None, "cor": [.32, .32, .31], "mapa": None}, None, False)
    M["manta"] = m
    M["manta-emenda"] = principled("manta-emenda", (.22, .22, .21), .7)[0]
    M["aluminio"] = principled("aluminio", (.6, .61, .62), .3, metal=.9)[0]
    M["galvanizado"] = principled("galvanizado", (.5, .51, .52), .42, metal=.9)[0]
    M["porcelana"] = principled("porcelana", (.75, .74, .7), .15, coat=1.0)[0]
    M["plastico-azul"] = principled("plastico-azul", (.02, .13, .36), .4)[0]
    M["plastico-branco"] = principled("plastico-branco", (.7, .7, .68), .35)[0]
    M["cone"] = principled("cone", (.75, .1, .015), .45)[0]
    M["refletivo"] = principled("refletivo", (.8, .8, .8), .25, metal=.3)[0]
    m, nt, p = principled("saco", (.52, .44, .31), .9)
    desgaste(nt, p, {"tipo": None, "cor": [.52, .44, .31], "mapa": None}, None, False)
    M["saco"] = m
    m, nt, p = principled("lona", (.04, .15, .38), .65)
    ruido = nt.nodes.new("ShaderNodeTexNoise"); ruido.inputs["Scale"].default_value = 8; ruido.inputs["Detail"].default_value = 6
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .4
    nt.links.new(ruido.outputs[0], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    M["lona"] = m
    return M


# ---------- geometria ----------
def uv_metros(me):
    """UV "uvMetros" por projeção na face dominante, em metros: as fotos do kit ficam no tamanho real."""
    uv = me.uv_layers.new(name="uvMetros")
    for poly in me.polygons:
        n = poly.normal
        eixo = max(range(3), key=lambda k: abs(n[k]))
        a, b = [k for k in range(3) if k != eixo]
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv = (co[a], co[b])


class Oficina:
    """Cria objetos já presos (pai) ao grupo animado; coordenadas sempre em three-local."""

    def __init__(self, pai, mats, colecao=None, sujar=False):
        self.pai, self.mats, self.n, self.colecao, self.sujar = pai, mats, 0, colecao, sujar

    def _girar(self, bm, centro, rot):
        if rot:
            bmesh.ops.rotate(bm, verts=bm.verts, cent=B(*centro), matrix=giro(rot))

    def objeto(self, nome, bm, mat, chanfro=0.0, angulo=35):
        self.n += 1
        me = bpy.data.meshes.new(nome)
        bm.normal_update(); bm.to_mesh(me); bm.free()
        uv_metros(me)
        me.materials.append(self.mats[mat])
        for p in me.polygons:
            p.use_smooth = True
        me.set_sharp_from_angle(angle=math.radians(angulo))
        ob = bpy.data.objects.new(nome, me)
        (self.colecao or bpy.context.scene.collection).objects.link(ob)
        if self.pai is not None:
            ob.parent = self.pai; ob.matrix_parent_inverse = Matrix.Identity(4)
        if chanfro:
            bv = ob.modifiers.new("chanfro", "BEVEL")
            bv.width = chanfro; bv.segments = 3; bv.limit_method = "ANGLE"; bv.harden_normals = True
        return ob

    def caixa(self, nome, tam, centro, mat, chanfro=.02, rot=None):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        sx, sy, sz = tam
        bmesh.ops.scale(bm, vec=(sx, sz, sy), verts=bm.verts)
        bmesh.ops.translate(bm, vec=B(*centro), verts=bm.verts)
        self._girar(bm, centro, rot)
        return self.objeto(nome, bm, mat, min(chanfro, min(tam) * .45))

    def perfil(self, nome, pts, largura, mat, c0=0.0, chanfro=.05, eixo="x"):
        """Silhueta extrudada: eixo "x" → pts [(z, y)] (vista lateral, cabines e carrocerias) extrudados ao longo de x;
        eixo "z" → pts [(x, y)] extrudados ao longo de z. c0 é o centro da extrusão."""
        bm = bmesh.new()
        if eixo == "x":
            vs = [bm.verts.new(B(c0 - largura / 2, y, z)) for z, y in pts]
            passo = B(largura, 0, 0)
        else:
            vs = [bm.verts.new(B(x, y, c0 - largura / 2)) for x, y in pts]
            passo = B(0, 0, largura)
        f = bm.faces.new(vs)
        ext = bmesh.ops.extrude_face_region(bm, geom=[f])
        novos = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, vec=passo, verts=novos)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return self.objeto(nome, bm, mat, chanfro)

    def placa(self, nome, cantos, mat):
        """Um quadrilátero (vidro, faróis): cantos em three-local, na ordem."""
        bm = bmesh.new()
        bm.faces.new([bm.verts.new(B(*c)) for c in cantos])
        return self.objeto(nome, bm, mat)

    def _orientar(self, bm, eixo, centro):
        if eixo == "x":
            bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Y"))
        elif eixo == "z":  # z do three = −Y do Blender
            bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "X"))
        bmesh.ops.translate(bm, vec=B(*centro), verts=bm.verts)

    def cilindro(self, nome, r, comp, centro, eixo, mat, segs=24, chanfro=0.0, rot=None, r2=None):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r if r2 is None else r2, depth=comp)
        self._orientar(bm, eixo, centro)
        self._girar(bm, centro, rot)
        return self.objeto(nome, bm, mat, chanfro)

    def torno(self, nome, perfil, centro, eixo, mat, segs=40, rot=None):
        """Sólido de revolução: perfil [(a, r)] ao longo do eixo do Blender Z, girado; depois orientado no eixo."""
        bm = bmesh.new()
        vs = [bm.verts.new((r, 0, a)) for a, r in perfil]
        es = [bm.edges.new((vs[i], vs[i + 1])) for i in range(len(vs) - 1)]
        bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), steps=segs, angle=2 * math.pi)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        self._orientar(bm, eixo, centro)
        self._girar(bm, centro, rot)
        return self.objeto(nome, bm, mat, angulo=50)

    def barra(self, nome, a, b, r, mat, segs=10, r2=None):
        """Cilindro de a até b (three-local)."""
        A, Bv = B(*a), B(*b)
        d = Bv - A
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r if r2 is None else r2, depth=d.length)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix())
        bmesh.ops.translate(bm, vec=(A + Bv) / 2, verts=bm.verts)
        return self.objeto(nome, bm, mat, angulo=50)

    def elipsoide(self, nome, raios, centro, mat, rot=None):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0)
        rx, ry, rz = raios
        bmesh.ops.scale(bm, vec=(rx, rz, ry), verts=bm.verts)
        bmesh.ops.translate(bm, vec=B(*centro), verts=bm.verts)
        self._girar(bm, centro, rot)
        return self.objeto(nome, bm, mat, angulo=80)

    def cor(self, hexa, rug=.6, metal=0.0, coat=0.0):
        """Material de cor lisa (hex sRGB do three), criado uma vez e guardado em mats."""
        sujo = self.sujar and _DESGASTE is not None
        chave = f"#{hexa:06X}-{rug}-{metal}-{coat}" + ("-sujo" if sujo else "")
        if chave not in self.mats:
            srgb = [((hexa >> s) & 255) / 255 for s in (16, 8, 0)]
            lin = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in srgb)
            m, nt, p = principled(chave, lin, rug, metal, coat)
            if sujo and max(lin) > .06:  # obra a céu aberto: poeira, oclusão, brilho variável (não no que é quase preto)
                _DESGASTE(nt, p, {"tipo": None, "cor": list(lin), "mapa": None}, None, True)
            self.mats[chave] = m
        return chave

    def arco(self, nome, r0, r1, larg, centro, eixo, mat, ang=math.pi, segs=20):
        """Meio anel (para-lama em arco): raio r0→r1, largura no eixo, abrindo para baixo."""
        bm = bmesh.new()
        w = larg / 2
        vs = [bm.verts.new((r, 0, a)) for a, r in ((-w, r0), (w, r0), (w, r1), (-w, r1))]
        es = [bm.edges.new((vs[i], vs[(i + 1) % 4])) for i in range(4)]
        bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), steps=segs, angle=ang)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bmesh.ops.contextual_create(bm, geom=bm.edges)  # tampa as pontas
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        # o meio do arco tem de apontar para cima depois de _orientar: −X antes do giro de "x", +Y antes do de "z"
        meio = math.pi if eixo == "x" else math.pi / 2
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(meio - ang / 2, 3, "Z"))
        self._orientar(bm, eixo, centro)
        return self.objeto(nome, bm, mat, angulo=50)

    def roda(self, nome, centro, R, larg, eixo, aro_r, mat_aro="aro", lado=1):
        """Pneu torneado (ombro arredondado) e aro em disco com cubo e porcas; `lado` ±1 é a face de fora."""
        w = larg / 2
        pneu = [(-w, aro_r), (-w, R - .07), (-w + .025, R - .02), (-w + .07, R), (w - .07, R), (w - .025, R - .02),
                (w, R - .07), (w, aro_r)]
        self.torno(nome + "-pneu", pneu, centro, eixo, "borracha")
        f = lado * (w - .03)
        disco = [(f, aro_r), (f - lado * .02, aro_r * .92), (f - lado * .06, aro_r * .55), (f - lado * .05, aro_r * .3),
                 (f - lado * .02, aro_r * .28), (f, 0.0)]
        if lado < 0:
            disco = disco[::-1]
        self.torno(nome + "-aro", disco, centro, eixo, mat_aro, segs=32)
        cubo = [(f - lado * .01, aro_r * .22), (f + lado * .03, aro_r * .18), (f + lado * .035, 0.0)]
        self.torno(nome + "-cubo", cubo if lado > 0 else cubo[::-1], centro, eixo, "cromo", segs=16)
        # porcas: 6 em volta do cubo
        cx, cy, cz = centro
        for k in range(6):
            a = 2 * math.pi * k / 6
            d = aro_r * .38
            if eixo == "x":
                p = (cx + f + lado * .01, cy + d * math.cos(a), cz + d * math.sin(a))
            else:
                p = (cx + d * math.cos(a), cy + d * math.sin(a), cz + f + lado * .01)
            self.cilindro(f"{nome}-porca{k}", .022, .03, p, eixo, "cromo", segs=6)


def em_y(p0, p1, y):
    """Ponto do segmento (z, y) p0→p1 na altura y."""
    t = (y - p0[1]) / (p1[1] - p0[1])
    return p0[0] + (p1[0] - p0[0]) * t


# ---------- caminhão-prancha (frente em +z; prancha z −4,4…2,9, topo 1,30) ----------
def caminhao(of, topo=1.30, rodas=((-1.2, 1.2), (-3.2, -1.6, 3.5)), R=.55):
    """topo: altura do topo da prancha; rodas: (xs, zs) dos eixos; R: raio da roda (as medidas do kit de cada cena)."""
    dy = topo - 1.30  # o conjunto chassi/prancha acompanha o topo da prancha
    for x in (-.5, .5):  # longarinas e o calço até a prancha
        of.caixa("longarina", (.2, .28, 9.0), (x, .78, .1), "chassi", .01)
        of.caixa("subchassi", (.2, .26, 7.3), (x, 1.05, -.75), "chassi", .01)
    of.caixa("prancha", (2.5, .12, 7.3), (0, 1.24 + dy, -.75), "madeira", .01)
    for x in (-1.22, 1.22):  # perfis da prancha e bolsas de fueiro
        of.caixa("perfil-prancha", (.08, .2, 7.3), (x, 1.2, -.75), "cinza", .01)
        for k in range(8):
            of.caixa("fueiro", (.1, .14, .08), (x * 1.02, 1.12, -4.1 + k * .95), "cinza", .005)
    of.caixa("travessa-traseira", (2.5, .2, .1), (0, 1.2, -4.42), "cinza", .01)
    for x in (-1.18, 1.18):  # protetor lateral entre os eixos
        for y in (.62, .88):
            of.caixa("protetor-lateral", (.04, .1, 2.9), (x, y, 1.15), "galvanizado", .01)
    for x in (-1.0, 1.0):
        of.caixa("suporte-protecao", (.08, .4, .08), (x, .55, -4.4), "chassi", .01)
    of.caixa("para-choque-protecao", (2.3, .12, .1), (0, .38, -4.4), "galvanizado", .01)
    of.caixa("para-choque-traseiro", (2.3, .14, .12), (0, .55, -4.45), "plastico", .01)
    for x in (-1.05, 1.05):
        of.caixa("lanterna-traseira", (.3, .1, .03), (x, .62, -4.52), "lanterna", .005)
    # cabine avançada: silhueta com para-brisa inclinado
    S = [(2.95, 1.12), (4.98, 1.12), (4.98, 1.95), (4.84, 2.95), (4.6, 3.22), (3.25, 3.25), (2.95, 3.12)]  # acima da roda
    of.perfil("cabine", S, 2.45, "branco", chanfro=.07)
    # para-brisa no plano inclinado (1,98 → 2,92 m)
    y0, y1 = 2.0, 2.9
    z0, z1 = em_y(S[2], S[3], y0) + .012, em_y(S[2], S[3], y1) + .012
    of.placa("para-brisa", [(-1.1, y0, z0), (1.1, y0, z0), (1.1, y1, z1), (-1.1, y1, z1)], "vidro")
    for x in (-.55, .45):  # limpadores
        of.caixa("limpador", (.9, .025, .02), (x, y0 + .12, z0 + .03), "plastico", 0, rot=(0, 0, .28))
    for x in (-1.229, 1.229):  # janelas das portas e vincos
        s = 1 if x > 0 else -1
        cantos = [(x, 2.05, 3.85), (x, 2.05, 4.82), (x, 2.85, 4.72), (x, 2.85, 3.85)]
        of.placa("janela", cantos if s > 0 else cantos[::-1], "vidro")
        of.caixa("vinco-porta", (.012, 2.0, .015), (x, 1.9, 3.7), "plastico", 0)
        of.caixa("vinco-porta2", (.012, 1.75, .015), (x, 2.0, 4.9), "plastico", 0)
        of.caixa("moldura-janela", (.015, .03, 1.0), (x * 1.002, 2.05, 4.33), "plastico", 0)
        of.caixa("moldura-janela", (.015, .82, .03), (x * 1.002, 2.45, 3.86), "plastico", 0)
        of.caixa("macaneta", (.02, .04, .18), (x * 1.005, 1.85, 3.85), "cromo", .005)
        of.caixa("degrau", (.35, .05, .3), (x * .95, .62, 4.2), "chassi", .01)
        of.caixa("degrau2", (.35, .05, .3), (x * .95, .92, 4.2), "chassi", .01)
        of.cilindro("braco-espelho", .02, .35, (x * 1.08, 2.55, 4.85), "x", "plastico", 8)
        of.caixa("espelho", (.06, .42, .22), (x * 1.18, 2.5, 4.85), "plastico", .02)
    # frente: grade, faróis, setas, para-choque, para-sol, luzes do teto
    of.caixa("grade", (1.5, .62, .03), (0, 1.5, 4.99), "plastico", .01)
    for k in range(5):
        of.caixa("filete", (1.46, .03, .02), (0, 1.25 + k * .12, 5.005), "cromo", .003)
    of.caixa("painel-baixo", (1.9, .3, .4), (0, .99, 4.8), "branco", .04)  # entre as rodas dianteiras
    for x in (-.72, .72):
        of.caixa("farol", (.36, .17, .03), (x, 1.0, 5.005), "farol", .02)
    for x in (-1.0, 1.0):
        of.caixa("seta", (.16, .1, .03), (x, 1.24, 4.995), "ambar", .01)
    of.caixa("para-choque", (2.45, .3, .24), (0, .7, 5.05), "plastico", .03)
    of.caixa("para-sol", (2.2, .06, .3), (0, 3.02, 4.92), "branco", .02)
    of.perfil("defletor", [(3.3, 3.25), (4.35, 3.25), (3.6, 3.55), (3.3, 3.55)], 2.1, "branco", chanfro=.04)  # baixo
    for x in (-.8, -.4, 0, .4, .8):
        of.caixa("luz-teto", (.12, .05, .06), (x, 3.245, 4.45), "ambar", .01)
    # tanque, escape, para-lamas
    of.cilindro("tanque", .3, 1.1, (1.0, .72, 1.9), "z", "aco", 24, .02)
    of.cilindro("escape", .065, 2.3, (1.33, 2.25, 2.86), "y", "cromo", 16)  # ao lado da quina da cabine, fora da prancha
    of.caixa("caixa-bateria", (.5, .45, .6), (-1.0, .72, 1.9), "chassi", .02)
    for z in rodas[1]:
        for x in rodas[0]:
            of.roda("roda", (x, R, z), R, .45, "x", R * .58, "aro", lado=1 if x > 0 else -1)
    for z in (-2.4,):  # para-lama do conjunto traseiro e lameiros
        for x in (-1.2, 1.2):
            of.caixa("para-lama", (.5, .05, 2.6), (x, 1.15, z), "plastico", .015)
            of.caixa("lameiro", (.5, .45, .02), (x, .5, z - 1.4), "plastico", .005)


# ---------- guindaste: base (comprimento em x), torre (gira em y), lança (+x, inclina em z) ----------
def guindaste_base(of):
    of.caixa("chassi-guindaste", (4.6, .62, 1.6), (0, .98, 0), "amarelo", .06)  # estreito: as rodas ficam por fora
    of.caixa("convés", (4.4, .05, 1.5), (0, 1.31, 0), "galvanizado", .01)
    of.caixa("capo-motor", (1.1, .45, 1.3), (1.65, 1.55, 0), "amarelo", .06)  # motor na traseira do chassi
    for k in range(6):
        of.caixa("aleta-motor", (.8, .02, .02), (1.65, 1.5 + k * .05, .66), "plastico", 0)
    of.cilindro("escape-guindaste", .05, .8, (1.9, 2.0, -.45), "y", "cromo", 12)
    for x in (-1.0, .2):
        for z in (-.82, .82):
            of.caixa("degrau-guindaste", (.35, .04, .18), (x, .62, z), "galvanizado", .005)
    for x in (-2.2, 2.2):
        for z in (-1.6, 1.6):  # pontas das patolas zebradas
            for k in range(3):
                of.caixa("zebra", (.31, .31, .08), (x, .62, z * (1 - k * .06)), "plastico", .005)
    for x in (-2.38, 2.38):  # cabeceiras com faróis
        of.caixa("cabeceira", (.12, .5, 1.6), (x, .95, 0), "plastico", .02)
        for z in (-.55, .55):
            of.caixa("farol-guindaste", (.03, .14, .26), (x * 1.02, 1.02, z), "farol", .01)
    for x in (-2.2, 2.2):  # patolas estendidas, macacos e sapatas
        of.caixa("patola", (.3, .3, 3.5), (x, .62, 0), "amarelo", .03)
        for z in (-1.75, 1.75):
            of.cilindro("macaco", .1, .55, (x, .3, z), "y", "cromo", 16)
            of.cilindro("camisa-macaco", .14, .3, (x, .62, z), "y", "amarelo", 16)
            of.cilindro("sapata", .32, .05, (x, .025, z), "y", "chassi", 24)
    for x in (-1.42, 1.42):  # longe das patolas (x ±2,2)
        for z in (-1.15, 1.15):
            of.roda("roda-guindaste", (x, .6, z), .6, .5, "z", .34, "aro", lado=1 if z > 0 else -1)
            of.caixa("para-lama-guindaste", (1.4, .05, .55), (x, 1.24, z * 1.02), "plastico", .015)
    of.cilindro("anel-giro", .95, .14, (-.6, 1.38, 0), "y", "chassi", 40)


def guindaste_torre(of):
    of.caixa("plataforma-torre", (2.7, .45, 1.95), (.1, .3, 0), "amarelo", .05)
    of.caixa("contrapeso", (.75, .9, 1.85), (-1.55, .6, 0), "amarelo", .06)
    for k in range(7):  # faixa zebrada na traseira do contrapeso
        of.caixa("zebra-contrapeso", (.012, .12, .7), (-1.935, .6, -.75 + k * .25), "plastico", 0, rot=(.8, 0, 0))
    for z in (-.38, .38):  # olhais do pino da lança
        of.caixa("olhal", (.7, .75, .06), (.55, .75, z), "amarelo", .02)
    # cabine do operador ao lado da lança: perfil (x, y) extrudado em z
    pts = [(-.35, .52), (.95, .52), (1.12, 1.15), (.92, 1.82), (-.35, 1.82)]
    of.perfil("cabine-operador", pts, .9, "amarelo", c0=1.0, chanfro=.04, eixo="z")
    # vidros da cabine do operador: frente inclinada e lateral de fora
    of.placa("vidro-operador-frente", [(1.12, 1.2, .6), (1.12, 1.2, 1.4), (.955, 1.75, 1.4), (.955, 1.75, .6)], "vidro")
    of.placa("vidro-operador-lado", [(-.25, .9, 1.456), (.9, .9, 1.456), (.88, 1.72, 1.456), (-.25, 1.72, 1.456)], "vidro")
    of.placa("vidro-operador-dentro", [(.9, .9, .544), (-.25, .9, .544), (-.25, 1.72, .544), (.88, 1.72, .544)], "vidro")
    of.placa("vidro-operador-tras", [(-.356, 1.0, .62), (-.356, 1.0, 1.38), (-.356, 1.72, 1.38), (-.356, 1.72, .62)], "vidro")
    of.caixa("teto-operador", (1.25, .04, .92), (.3, 1.84, 1.0), "plastico", .01)
    for x in (-1.2, -.2):  # guarda-corpo sobre a torre
        of.cilindro("poste-guarda", .02, .5, (x, .78, -.85), "y", "amarelo", 8)
    of.cilindro("corrimao", .02, 1.1, (-.7, 1.03, -.85), "x", "amarelo", 8)
    of.cilindro("giroflex", .07, .1, (-1.55, 1.1, 0), "y", "ambar", 16)
    of.caixa("limpador", (.02, .5, .02), (1.06, 1.45, 1.0), "plastico", 0, rot=(0, 0, .3))


def guindaste_lanca(of):
    of.cilindro("pino-lanca", .16, .9, (0, 0, 0), "z", "cromo", 20)
    of.caixa("lanca-1", (8.3, .62, .52), (3.65, 0, 0), "amarelo", .07)
    of.caixa("lanca-2", (4.8, .48, .4), (8.9, .02, 0), "amarelo", .06)
    of.caixa("colar", (.25, .66, .56), (7.65, 0, 0), "cinza", .03)
    for y in (-.2, .2):  # faixas de desgaste das sapatas de deslizamento
        of.caixa("patim", (.4, .04, .42), (7.5, y * 1.4, 0), "plastico", .01)
    of.caixa("cabeca", (.7, .62, .5), (11.25, -.05, 0), "amarelo", .05)
    for z in (-.12, .12):
        of.cilindro("roldana", .27, .06, (11.55, -.12, z), "z", "chassi", 28)
    of.cilindro("eixo-roldana", .05, .5, (11.55, -.12, 0), "z", "cromo", 12)
    for z in (-.29, -.25):  # mangueiras hidráulicas na lateral da lança
        of.cilindro("mangueira", .018, 7.0, (4.0, .12, z), "x", "plastico", 8)
    for k in range(5):
        of.caixa("presilha-mangueira", (.05, .08, .08), (1.2 + k * 1.5, .12, -.27), "chassi", .005)
    of.caixa("luz-ponta", (.08, .08, .08), (11.62, .22, .2), "ambar", .01)


def cilindro_de_elevacao(torre, lanca, mats):
    """Camisa presa à torre e haste presa à lança, cada uma apontando para a outra (Damped Track): o cilindro acompanha
    o ângulo da lança em todos os quadros sem chaves próprias."""
    def ancora(pai, p):
        e = bpy.data.objects.new("ancora", None); bpy.context.scene.collection.objects.link(e)
        e.parent = pai; e.matrix_parent_inverse = Matrix.Identity(4); e.location = B(*p)
        return e
    a_torre, a_lanca = ancora(torre, (1.45, .5, 0)), ancora(lanca, (3.2, -.32, 0))
    for nome, pai, alvo, r, comp, mat in (("camisa", a_torre, a_lanca, .17, 2.3, "amarelo"), ("haste", a_lanca, a_torre, .09, 2.5, "cromo")):
        of = Oficina(pai, mats)
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=20, radius1=r, radius2=r, depth=comp)
        bmesh.ops.translate(bm, vec=(0, 0, comp / 2), verts=bm.verts)
        ob = of.objeto(nome, bm, mat)
        c = ob.constraints.new("DAMPED_TRACK"); c.target = alvo; c.track_axis = "TRACK_Z"


# ---------- picape (frente em +z; z −2,5…2,5; rodas r 0,36 em x ±0,85, z ±1,6) ----------
def picape(of):
    S = [(-2.5, .45), (2.42, .45), (2.5, .58), (2.5, 1.02), (2.28, 1.22), (1.38, 1.38), (.95, 1.84), (-.22, 1.86),
         (-.38, 1.78), (-.38, .82), (-2.5, .82)]
    of.perfil("carroceria", S, 1.82, "branco", chanfro=.1)
    for x in (-.88, .88):  # laterais e tampa da caçamba
        of.caixa("lateral-cacamba", (.07, .3, 2.12), (x, .96, -1.44), "branco", .025)
    of.caixa("tampa", (1.82, .3, .07), (0, .96, -2.47), "branco", .025)
    of.caixa("fundo-cacamba", (1.7, .02, 2.05), (0, .83, -1.42), "plastico", 0)
    of.caixa("macaneta-tampa", (.25, .04, .02), (0, 1.02, -2.51), "plastico", .005)
    for x in (-.85, .85):
        of.caixa("para-barro", (.26, .3, .015), (x, .32, -2.05), "plastico", .004)
    # vidros: para-brisa, laterais, traseiro
    y0, y1 = 1.42, 1.8
    z0, z1 = em_y(S[5], S[6], y0) - .01, em_y(S[5], S[6], y1) - .01
    of.placa("para-brisa-picape", [(-.78, y0, z0 + .03), (.78, y0, z0 + .03), (.74, y1, z1 + .03), (-.74, y1, z1 + .03)], "vidro")
    for x in (-.912, .912):
        cantos = [(x, 1.42, -.3), (x, 1.42, 1.3), (x, 1.78, .93), (x, 1.78, -.25)]
        of.placa("janela-picape", cantos if x > 0 else cantos[::-1], "vidro")
        of.caixa("coluna-b", (.012, .38, .06), (x * 1.002, 1.6, .5), "plastico", 0)
        of.caixa("vinco-portas", (.01, .6, .012), (x * 1.002, 1.1, -.3), "plastico", 0)
        of.caixa("vinco-portas", (.01, .6, .012), (x * 1.002, 1.1, 1.3), "plastico", 0)
        of.caixa("macaneta-picape", (.02, .03, .12), (x * 1.01, 1.3, .2), "plastico", .005)
        of.caixa("friso", (.012, .025, 4.2), (x * 1.008, .98, 0), "cromo", .004)
        of.caixa("espelho-picape", (.06, .13, .2), (x * 1.06, 1.45, 1.25), "plastico", .02)
        for z in (-1.6, 1.6):  # caixas de roda
            of.caixa("caixa-roda", (.04, .12, .95), (x * 1.0, .82, z), "plastico", .02)
    of.placa("vidro-traseiro", [(.7, 1.45, -.39), (-.7, 1.45, -.39), (-.66, 1.74, -.39), (.66, 1.74, -.39)], "vidro")
    # frente e traseira
    of.caixa("grade-picape", (1.0, .2, .03), (0, .9, 2.505), "plastico", .01)
    for k in range(3):
        of.caixa("filete-picape", (.96, .02, .01), (0, .84 + k * .06, 2.522), "cromo", .002)
    for x in (-.62, .62):
        of.caixa("farol-picape", (.34, .13, .04), (x, .95, 2.49), "farol", .02)
        of.caixa("lanterna-picape", (.12, .32, .04), (x * 1.38, .95, -2.51), "lanterna", .015)
    of.caixa("para-choque-diant", (1.9, .2, .22), (0, .55, 2.56), "cromo", .05)
    of.caixa("para-choque-tras", (1.9, .18, .2), (0, .55, -2.56), "cromo", .05)
    for z in (-1.6, 1.6):  # para-lamas em arco
        for x in (-.93, .93):
            of.arco("para-lama-picape", .4, .47, .09, (x, .36, z), "x", "plastico")
    for z in (-1.6, 1.6):
        for x in (-.85, .85):
            of.roda("roda-picape", (x, .36, z), .36, .26, "x", .22, "aro", lado=1 if x > 0 else -1)


def montar(raizes, mats):
    """raizes: {"caminhao": objeto animado, "guindaste-base": …, …}; mats: materiais(). Devolve o nº de peças."""
    total = 0
    for chave, fazer in (("caminhao", caminhao), ("guindaste-base", guindaste_base), ("guindaste-torre", guindaste_torre),
                         ("guindaste-lanca", guindaste_lanca), ("picape", picape)):
        if chave in raizes:
            of = Oficina(raizes[chave], mats)
            fazer(of)
            total += of.n
    if "guindaste-torre" in raizes and "guindaste-lanca" in raizes:
        cilindro_de_elevacao(raizes["guindaste-torre"], raizes["guindaste-lanca"], mats)
    return total
