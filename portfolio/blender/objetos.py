"""Modelos procedurais dos objetos do canteiro do caso modulares (--visual cinema do montar.py), no lugar das caixas do
kit: as duas caixas modulares, o moitão e o balancim, o contêiner de canteiro, a caixa d'água, o banheiro químico, a
caçamba, os tambores, os paletes e as cargas, a betoneira, os montes de areia e brita, a pá, os baldes, o carrinho de
mão, o andaime, a escada, os cones, a placa de obra, a rede elétrica e as pedras do pasto.

Como em veiculos.py: cada grupo marcado no caso-modulares.html (userData.asset) chega em `grupos` com a matriz por
quadro; o modelo é feito nas coordenadas locais do three (Y para cima, metros), com as medidas do kit, e fica preso ao
grupo. Os cones e as pedras são InstancedMesh: o modelo vira uma coleção instanciada nas matrizes de cada instância.
Nenhum texto, marca ou nome em lugar nenhum (sigilo).
"""
import math

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

from veiculos import B, Oficina, em_y


# ---------- as caixas modulares (6,00 × 3,00 × 2,85 m) ----------
def caixa_modular(of, frente):
    W, H, D, y0 = 6.0, 2.85, 3.0, .27
    # chassi de aço: perímetro em perfil e travessas
    for z in (-D / 2 + .075, D / 2 - .075):
        of.caixa("viga-chassi", (W, .22, .15), (0, .11, z), "chassi", .01)
    for x in (-W / 2 + .075, W / 2 - .075, -1.0, 1.0):
        of.caixa("travessa-chassi", (.15, .2, D - .3), (x, .11, 0), "chassi", .01)
    of.caixa("piso", (W - .04, .05, D - .04), (0, .245, 0), "madeira", .005)
    of.caixa("corpo", (W - .02, H, D - .02), (0, y0 + H / 2, 0), "branco", .015)
    # rufos (topo) e rodapé; cobertura em manta com emendas e olhais de içamento nos cantos
    of.caixa("rufo", (W + .04, .08, D + .04), (0, y0 + H - .02, 0), "branco", .015)
    of.caixa("manta", (W - .12, .02, D - .12), (0, y0 + H + .025, 0), "manta", .005)
    for k in range(1, 6):
        of.caixa("emenda-manta", (.04, .008, D - .14), (-W / 2 + k * 1.0, y0 + H + .037, 0), "manta-emenda", 0)
    for x in (-W / 2 + .25, W / 2 - .25):
        for z in (-D / 2 + .2, D / 2 - .2):
            of.caixa("olhal-icamento", (.16, .14, .03), (x, y0 + H + .09, z), "galvanizado", .01)
    of.caixa("rodape", (W + .02, .1, D + .02), (0, y0 + .05, 0), "cinza", .01)
    for x in (-W / 2, W / 2):
        for z in (-D / 2, D / 2):
            of.caixa("pilar-canto", (.1, H + .06, .1), (x, y0 + H / 2, z), "cinza", .01)
    # juntas verticais dos painéis (a cada 1,2 m) nas faces de fora
    zf = D / 2 + .004 if frente else -D / 2 - .004
    for k in range(1, 5):
        x = -W / 2 + k * 1.2
        if not frente or abs(x) > 1.35:  # na frente, o vão envidraçado ocupa o meio
            of.caixa("junta", (.012, H - .2, .006), (x, y0 + H / 2, zf), "cinza", 0)
    for x in (-W / 2 - .004, W / 2 + .004):
        for z in (-.75, .75):
            of.caixa("junta-lateral", (.006, H - .2, .012), (x, y0 + H / 2, z), "cinza", 0)
    # face de junção: montantes de aço a cada 40 cm, guias e contraventamento em X (como sai da fábrica)
    zj = -D / 2 - .03 if frente else D / 2 + .03
    for i in range(16):
        of.caixa("montante", (.04, H - .1, .05), (-W / 2 + .02 + i * .4, y0 + H / 2, zj), "galvanizado", .004)
    for y in (y0 + .06, y0 + H - .06):
        of.caixa("guia", (W, .06, .055), (0, y, zj), "galvanizado", .004)
    diag = math.atan2(H - .2, W / 2 - .1)
    for sx in (-1, 1):
        for sd in (-1, 1):
            of.caixa("diagonal", (math.hypot(W / 2 - .1, H - .2), .05, .012), (sx * W / 4, y0 + H / 2, zj + .03 * (1 if not frente else -1)),
                     "galvanizado", 0, rot=(0, 0, sd * diag))
    # aberturas
    def janela(cx, cy, w, h, face, nome):
        """face: ("z", ±) ou ("x", ±). Vidro, caixilho de alumínio e peitoril."""
        eixo, sinal = face
        e = .035
        if eixo == "z":
            z = sinal * (D / 2 + .012)
            of.caixa(nome + "-vidro", (w, h, .01), (cx, cy, z), "vidro", 0)
            for dy in (-h / 2, h / 2):
                of.caixa(nome + "-caixilho", (w + 2 * e, e, .05), (cx, cy + dy, z), "aluminio", .005)
            for dx in (-w / 2, w / 2):
                of.caixa(nome + "-caixilho", (e, h, .05), (cx + dx, cy, z), "aluminio", .005)
            of.caixa(nome + "-peitoril", (w + .1, .03, .08), (cx, cy - h / 2 - .03, z + sinal * .03), "aluminio", .005)
        else:
            x = sinal * (W / 2 + .012)
            of.caixa(nome + "-vidro", (.01, h, w), (x, cy, cx), "vidro", 0)
            for dy in (-h / 2, h / 2):
                of.caixa(nome + "-caixilho", (.05, e, w + 2 * e), (x, cy + dy, cx), "aluminio", .005)
            for dz in (-w / 2, w / 2):
                of.caixa(nome + "-caixilho", (.05, h, e), (x, cy, cx + dz), "aluminio", .005)
            of.caixa(nome + "-peitoril", (.08, .03, w + .1), (x + sinal * .03, cy - h / 2 - .03, cx), "aluminio", .005)
    janela(0, y0 + 1.4, 1.1, 1.0, ("x", -1), "janela-oeste")
    janela(0, y0 + 1.4, 1.1, 1.0, ("x", 1), "janela-leste")
    if frente:
        janela(0, y0 + 1.05, 2.55, 2.05, ("z", 1), "porta-vidro")
        of.caixa("montante-porta", (.04, 2.05, .05), (0, y0 + 1.05, D / 2 + .02), "aluminio", .005)
        for x in (-.1, .1):
            of.caixa("puxador-vidro", (.025, .45, .03), (x, y0 + 1.05, D / 2 + .06), "aluminio", .006)
        for x in (-1.55, 1.55):  # portões de madeira (tábuas, travessas e mão-francesa)
            of.caixa("portao", (1.3, 2.2, .05), (x, y0 + 1.1, D / 2 + .04), "madeira", .008)
            for y in (.35, 1.1, 1.85):
                of.caixa("travessa-portao", (1.2, .1, .03), (x, y0 + y, D / 2 + .075), "madeira", .006)
            of.caixa("mao-francesa", (1.35, .09, .03), (x, y0 + .72, D / 2 + .08), "madeira", .006, rot=(0, 0, .55 if x < 0 else -.55))
            of.caixa("dobradica", (.12, .05, .02), (x - .6 * (1 if x > 0 else -1) * -1, y0 + 1.85, D / 2 + .08), "chassi", .004)
            of.cilindro("puxador", .015, .3, (x - .55 * (1 if x > 0 else -1), y0 + 1.1, D / 2 + .1), "y", "cromo", 8)
        of.caixa("arandela", (.16, .22, .1), (-2.45, y0 + 2.35, D / 2 + .06), "chassi", .02)
        of.caixa("difusor", (.12, .14, .02), (-2.45, y0 + 2.33, D / 2 + .115), "farol", .01)
    else:
        janela(-1.6, y0 + 1.5, 1.2, 1.0, ("z", -1), "janela-fundo")
        of.caixa("quadro-medicao", (.45, .6, .18), (1.9, y0 + 1.35, -D / 2 - .09), "cinza", .02)
        of.caixa("visor-medicao", (.18, .14, .01), (1.9, y0 + 1.45, -D / 2 - .182), "vidro", 0)
        of.cilindro("eletroduto", .025, 1.3, (1.9, y0 + .45, -D / 2 - .1), "y", "plastico", 10)


# ---------- o gancho: moitão e balancim ----------
def gancho(of):
    for z in (-.15, .15):
        of.caixa("placa-moitao", (.48, .42, .05), (0, 0, z), "laranja", .03)
    of.cilindro("roldana-moitao", .16, .22, (0, .05, 0), "z", "chassi", 24)
    of.cilindro("eixo-moitao", .035, .4, (0, .05, 0), "z", "cromo", 12)
    of.cilindro("haste-gancho", .045, .25, (0, -.32, 0), "y", "cromo", 12)
    of.torno("gancho", [(-.03, .07), (.03, .07), (.03, .11), (-.03, .11), (-.03, .07)], (0, -.55, 0), "z", "laranja", 20)
    # balancim em perfil I
    I = [(-.07, -.6), (.07, -.6), (.07, -.585), (.012, -.585), (.012, -.415), (.07, -.415), (.07, -.4), (-.07, -.4),
         (-.07, -.415), (-.012, -.415), (-.012, -.585), (-.07, -.585)]
    of.perfil("balancim", [(z, y) for z, y in I], 6.2, "amarelo", chanfro=.004)
    for x in (-3.0, -1.0, 1.0, 3.0):
        of.cilindro("olhal-balancim", .05, .03, (x, -.38 if abs(x) < 2 else -.62, 0), "z", "chassi", 12)
    for x in (-1.0, 1.0):  # lingas do moitão ao balancim
        L = math.hypot(x, .2)
        of.caixa("linga", (L, .025, .025), (x / 2, -.3, 0), "chassi", 0, rot=(0, 0, math.atan2(.2, -x) if x < 0 else -math.atan2(.2, x)))


# ---------- contêiner de canteiro (6 × 2,6 × 2,6 sobre blocos) ----------
def conteiner(of, foto):
    for x in (-2.6, 2.6):
        for z in (-1, 1):
            of.caixa("bloco-apoio", (.4, .3, .4), (x, .15, z), "concreto", .02)
    of.caixa("corpo-conteiner", (6, 2.6, 2.6), (0, 1.6, 0), "conteiner", .01)
    for x in (-2.97, 2.97):  # quinas e cabeceiras
        for z in (-1.27, 1.27):
            of.caixa("coluna-quina", (.12, 2.6, .12), (x, 1.6, z), "azul", .01)
            for y in (.38, 2.82):
                of.caixa("peca-quina", (.18, .12, .16), (x, y, z), "chassi", .01)
    for y in (.36, 2.84):
        for z in (-1.28, 1.28):
            of.caixa("longarina-conteiner", (6, .14, .1), (0, y, z), "azul", .01)
    of.caixa("cobertura", (6.1, .06, 2.7), (0, 2.93, 0), "zinco", .01)
    # porta, janela com grade e ar-condicionado
    of.caixa("porta", (.9, 2.05, .05), (-1.8, 1.33, 1.33), "cinza", .01)
    of.caixa("batente", (1.0, 2.12, .03), (-1.8, 1.36, 1.315), "azul", .01)
    of.cilindro("macaneta-conteiner", .018, .14, (-1.45, 1.3, 1.38), "x", "cromo", 8)
    of.caixa("vidro-conteiner", (1.3, .9, .02), (1.2, 1.9, 1.32), "vidro", 0)
    for k in range(6):
        of.caixa("grade", (1.3, .02, .02), (1.2, 1.48 + k * .17, 1.36), "chassi", 0)
    for k in range(4):
        of.caixa("grade-v", (.02, .9, .02), (.6 + k * .4, 1.9, 1.37), "chassi", 0)
    of.caixa("ar-condicionado", (.72, .52, .45), (2.4, 2.2, 1.52), "plastico-branco", .03)
    for k in range(8):
        of.caixa("aleta", (.6, .015, .02), (2.4, 2.02 + k * .05, 1.755), "cinza", 0)
    of.cilindro("tubo-ar", .02, .6, (2.65, 1.8, 1.35), "y", "plastico-branco", 8)
    of.caixa("degrau", (1.0, .18, .5), (-1.8, .09, 1.6), "concreto", .02)
    of.caixa("degrau2", (1.0, .18, .3), (-1.8, .27, 1.5), "concreto", .02)
    for x in (-2.35, -1.25):  # corrimão da escadinha
        of.cilindro("poste-corrimao", .02, .9, (x, .45, 1.75), "y", "galvanizado", 8)
    of.cilindro("corrimao-conteiner", .02, 1.1, (-1.8, .9, 1.75), "x", "galvanizado", 8)


# ---------- caixa d'água sobre torre de madeira; banheiro químico ----------
def caixa_dagua(of, torre="madeira"):
    for x in (-.6, .6):
        for z in (-.6, .6):
            of.caixa("pe-torre", (.12, 3.2, .12), (x, 1.6, z), torre, .015)
    for y in (1.0, 2.3):
        for (cx, cz, rot) in ((0, -.6, 0), (0, .6, 0), (-.6, 0, math.pi / 2), (.6, 0, math.pi / 2)):
            of.caixa("travessa-torre", (1.32, .08, .06), (cx, y, cz), torre, .01, rot=(0, rot, 0))
    a = math.atan2(1.3, 1.2)
    for (cx, cz, ry) in ((0, -.63, 0), (0, .63, 0), (-.63, 0, math.pi / 2), (.63, 0, math.pi / 2)):
        of.caixa("diagonal-torre", (math.hypot(1.2, 1.3), .07, .04), (cx, 1.65, cz), torre, .008, rot=(0, ry, a))
    for k in range(7):  # estrado
        of.caixa("tabua-estrado", (1.7, .05, .22), (0, 3.24, -.75 + k * .25), "madeira", .008)
    perfil = [(0, .0), (.05, .74), (.12, .78), (.2, .8), (.35, .8), (.4, .77), (.47, .8), (.62, .8), (.67, .77), (.74, .8),
              (.9, .8), (.95, .77), (1.02, .8), (1.2, .79), (1.3, .72), (1.42, .45), (1.48, .2), (1.5, .0)]
    of.torno("tanque", [(a_, r) for a_, r in perfil], (0, 3.28, 0), "y", "plastico-azul", 48)
    of.cilindro("tampa-rosca", .2, .08, (0, 4.8, 0), "y", "plastico-azul", 24)
    of.cilindro("tubo-descida", .03, 3.2, (.7, 1.6, .5), "y", "plastico-branco", 12)
    of.cilindro("joelho", .035, .3, (.62, 3.45, .5), "x", "plastico-branco", 12)
    of.cilindro("registro", .05, .08, (.7, 1.2, .5), "y", "cromo", 12)


def banheiro(of):
    of.caixa("base-banheiro", (1.16, .1, 1.16), (0, .05, 0), "plastico", .02)
    of.caixa("corpo-banheiro", (1.1, 2.15, 1.1), (0, 1.17, 0), "plastico-azul", .04)
    for k in range(5):  # nervuras laterais
        for x in (-.556, .556):
            of.caixa("nervura", (.02, 1.9, .05), (x, 1.15, -.4 + k * .2), "plastico-azul", .008)
    of.perfil("teto-banheiro", [(-.62, 2.24), (.62, 2.24), (.55, 2.36), (.3, 2.42), (-.3, 2.42), (-.55, 2.36)], 1.22,
              "plastico-branco", chanfro=.02)
    of.caixa("porta-banheiro", (.72, 1.95, .04), (0, 1.07, .565), "plastico-azul", .02)
    for k in range(4):
        of.caixa("veneziana", (.5, .025, .03), (0, 1.88 + k * .05, .59), "plastico", 0)
    of.caixa("trinco", (.08, .05, .03), (.27, 1.15, .59), "plastico-branco", .005)
    of.cilindro("respiro", .04, .5, (-.4, 2.55, -.4), "y", "plastico", 10)


# ---------- caçamba de entulho, tambores ----------
def cacamba(of):
    pts = [(-.9, .05), (.9, .05), (1.25, 1.35), (-1.25, 1.35)]
    of.perfil("cacamba", pts, 1.5, "amarelo", chanfro=.02, eixo="z")
    of.perfil("entulho", [(-1.12, 1.0), (1.12, 1.0), (1.18, 1.22), (-1.18, 1.22)], 1.38, "concreto", chanfro=.05, eixo="z")
    a = math.atan2(.35, 1.3)
    for x in (-1.0, 1.0):
        for z in (-.45, 0, .45):
            of.caixa("reforco", (.04, 1.32, .08), (x * 1.09, .7, z), "amarelo", .008, rot=(0, 0, -x * a))
    for z in (-.77, .77):
        of.caixa("aro-cacamba", (2.55, .07, .05), (0, 1.33, z), "amarelo", .01)
        for x in (-.75, .75):
            of.cilindro("olhal-cacamba", .07, .1, (x, 1.0, z * 1.04), "z", "chassi", 16)
    rnd = np.random.default_rng(5)
    for k in range(22):  # caliça assentada: pedaços de concreto, tijolos e sobras de madeira
        tipo = ("concreto", "tijolo", "madeira")[k % 3]
        tam = {"concreto": (rnd.uniform(.2, .45), rnd.uniform(.1, .2), rnd.uniform(.15, .35)),
               "tijolo": (.19, .09, .09), "madeira": (rnd.uniform(.5, 1.1), .025, .1)}[tipo]
        of.caixa("calica", tam, (rnd.uniform(-1.0, 1.0), 1.21 + tam[1] / 2 - .02, rnd.uniform(-.6, .6)), tipo, .015,
                 rot=(rnd.uniform(-.25, .25), rnd.uniform(0, 3.1), rnd.uniform(-.25, .25)))


def tambor(of, cor):
    """Origem no centro do cilindro do kit (r 0,29, h 0,88)."""
    p = [(-.44, 0), (-.44, .28), (-.43, .29), (-.33, .29), (-.32, .3), (-.3, .29), (-.02, .29), (0, .3), (.02, .29),
         (.3, .29), (.32, .3), (.33, .29), (.43, .29), (.44, .28), (.44, 0)]
    of.torno("tambor", p, (0, 0, 0), "y", cor, 36)
    of.cilindro("bujao", .03, .02, (.15, .445, .08), "y", "cromo", 10)


# ---------- paletes e cargas ----------
def palete(of):
    for z in (-.4, 0, .4):
        of.caixa("tabua-base", (1.2, .022, .1), (0, .011, z), "madeira", .004)
        for x in (-.55, 0, .55):
            of.caixa("taco", (.1, .078, .1), (x, .061, z), "madeira", .008)
        of.caixa("longarina-palete", (1.2, .022, .1), (0, .111, z), "madeira", .004)
    for k in range(7):
        of.caixa("tabua-topo", (.1, .02, 1.0), (-.54 + k * .18, .132, 0), "madeira", .004)


def palete_lsf(of):
    palete(of)
    C = [(-.045, -.045), (.045, -.045), (.045, -.03), (-.033, -.03), (-.033, .03), (.045, .03), (.045, .045), (-.045, .045)]
    for i in range(4):
        for j in range(2):
            cx, cy = -.3 + i * .2, .19 + j * .1
            of.perfil("montante-lsf", [(cx + x, cy + y) for x, y in C], 3.0, "galvanizado", chanfro=.002, eixo="z")
    for s in (-1, 1):
        of.caixa("cinta", (.88, .27, .012), (0, .23, s * 1.05), "plastico", .004)


def palete_sacos(of):
    palete(of)
    rnd = np.random.default_rng(3)
    for k in range(3):
        for i in range(3):
            x, z = (-.32 + i * .32, 0) if k % 2 else (0, -.32 + i * .32)
            ry = (0 if k % 2 else math.pi / 2) + rnd.uniform(-.08, .08)
            of.caixa("saco", (.5, .13, .32), (x, .21 + k * .13, z), "saco", .05, rot=(0, ry, 0))


def palete_lona(of):
    palete(of)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=8, use_grid_fill=True)
    rnd = np.random.default_rng(9)
    for v in bm.verts:  # rugas da lona
        v.co *= Vector((1.12, .97, .82))
        v.co += Vector(rnd.normal(0, .012, 3))
    bmesh.ops.translate(bm, vec=B(0, .55, 0), verts=bm.verts)
    ob = of.objeto("lona", bm, "lona", angulo=60)
    ob.modifiers.new("lisa", "SUBSURF").levels = 1
    for x in (-.35, .35):
        of.caixa("corda", (.025, .84, .99), (x, .55, 0), "plastico", .01)


# ---------- betoneira, montes, pá, baldes, carrinho ----------
def betoneira(of):
    for x in (-.45, .45):
        of.roda("roda-betoneira", (x, .25, .3), .25, .1, "x", .14, "aro", lado=1 if x > 0 else -1)
    of.cilindro("eixo-betoneira", .025, 1.0, (0, .25, .3), "x", "chassi", 10)
    for x in (-.35, .35):
        of.caixa("perna", (.06, .95, .06), (x, .55, -.05), "laranja", .01, rot=(.35, 0, 0))
    of.caixa("travessa-betoneira", (.08, .06, .8), (0, .95, -.15), "laranja", .01)
    tambor_p = [(0, .02), (.05, .3), (.3, .42), (.36, .43), (.42, .43), (.6, .42), (.8, .3), (.88, .26), (.9, .27), (.92, .25)]
    of.torno("tambor-betoneira", tambor_p, (0, .8, -.05), "y", "laranja", 40, rot=(-.7, 0, 0))
    of.torno("coroa", [(.34, .44), (.34, .47), (.4, .47), (.4, .44)], (0, .8, -.05), "y", "chassi", 40, rot=(-.7, 0, 0))
    of.caixa("motor", (.32, .27, .34), (0, .5, -.45), "cinza", .03)
    of.cilindro("volante", .14, .03, (.28, .9, -.2), "x", "chassi", 20)


def monte(of, raio, altura, mat, seed, base=None, aspereza=.07, lisa=True, cone=False, grao=.035):
    """Monte irregular (origem no centro do cone do kit): anéis com ruído, perfil arredondado."""
    rnd = np.random.default_rng(seed)
    bm = bmesh.new()
    an, rg = 40, 10
    ruido = rnd.normal(0, 1, (rg + 1, an))
    aneis = []
    for i in range(rg + 1):
        t = i / rg
        r = raio * (1 - t) ** .9
        # cone: material solto no ângulo de repouso (lados retos, topo levemente arredondado); senão cúpula
        perfil = (t * (1 - .25 * t ** 3) / .75 if t > .0 else 0) if cone else (1 - (1 - t) ** 2)
        y = (-altura / 2 if base is None else base) + altura * min(perfil, 1.0)
        anel = []
        for j in range(an):
            a = 2 * math.pi * j / an
            rr = r * (1 + aspereza * ruido[i, j] * (1 - t)) if i < rg else 0
            anel.append(bm.verts.new(B(rr * math.cos(a), y + .03 * ruido[i, (j + 3) % an] * t, rr * math.sin(a))))
        aneis.append(anel)
    for i in range(rg):
        for j in range(an):
            k = (j + 1) % an
            vs = [aneis[i][j], aneis[i][k], aneis[i + 1][k], aneis[i + 1][j]]
            if i + 1 == rg:
                vs = [aneis[i][j], aneis[i][k], aneis[i + 1][0]]
            try:
                bm.faces.new(vs)
            except ValueError:
                pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = of.objeto("monte", bm, mat, angulo=80)
    if lisa:
        ob.modifiers.new("lisa", "SUBSURF").levels = 1
    else:  # material solto (brita): superfície granulada, deslocada por ruído fino
        ob.modifiers.new("fina", "SUBSURF").levels = 3
        tex = bpy.data.textures.get("granulado") or bpy.data.textures.new("granulado", "CLOUDS")
        tex.noise_scale = .025; tex.noise_depth = 2
        d = ob.modifiers.new("granulado", "DISPLACE"); d.texture = tex; d.strength = grao; d.mid_level = .5


def pa(of):
    of.cilindro("cabo-pa", .018, 1.3, (0, .65, 0), "y", "madeira", 10, rot=(-.55, 0, 0))
    of.caixa("lamina", (.24, .3, .012), (0, .06, -.02), "chassi", .03, rot=(.2, 0, 0))
    of.caixa("pega", (.14, .03, .03), (0, 1.2, -.68), "plastico", .01)


def balde(of, mat):
    p = [(-.15, 0), (-.15, .13), (-.14, .135), (.12, .155), (.13, .165), (.15, .165), (.15, .158)]
    of.torno("balde", p, (0, 0, 0), "y", mat, 32)
    of.torno("alca", [(-.005, .17), (.005, .17), (.005, .175), (-.005, .175)], (0, .16, 0), "x", "cromo", 16)


def carrinho(of):
    pts = [(-.4, .3), (.32, .3), (.45, .62), (-.48, .62)]  # caçamba em perfil (z, y), oca
    of.perfil("cacamba-carrinho", pts, .6, "verde", chanfro=.03)
    of.perfil("fundo-carrinho", [(-.36, .58), (.36, .58), (.42, .625), (-.44, .625)], .52, "chassi", chanfro=.01)
    of.caixa("aba-carrinho", (.64, .03, .95), (0, .625, -.015), "verde", .012)
    of.roda("roda-carrinho", (0, .18, .5), .18, .08, "x", .09, "aro", lado=1)
    for x in (-.25, .25):
        of.caixa("braco", (.035, .035, 1.45), (x, .35, -.15), "chassi", .008, rot=(.18, 0, 0))
        of.caixa("pe-carrinho", (.035, .3, .035), (x, .15, -.25), "chassi", .008)
        of.cilindro("manopla", .022, .14, (x, .23, -.86), "z", "plastico", 10, rot=(.18, 0, 0))


# ---------- andaime com caixa de ferramentas; escada ----------
def andaime(of):
    for x in (-.6, .6):
        for z in (-.4, .4):
            of.cilindro("montante-andaime", .024, 2.0, (x, 1.0, z), "y", "galvanizado", 12)
            of.caixa("sapata-andaime", (.15, .01, .15), (x, .005, z), "galvanizado", .002)
    for y in (.45, .95, 1.45, 1.95):
        for z in (-.4, .4):
            of.cilindro("travessa-andaime", .022, 1.2, (0, y, z), "x", "galvanizado", 10)
        for x in (-.6, .6):
            of.cilindro("travessa-andaime", .022, .8, (x, y, 0), "z", "galvanizado", 10)
        for x in (-.6, .6):
            for z in (-.4, .4):
                of.caixa("abracadeira", (.07, .07, .07), (x, y, z), "chassi", .01)
    a = math.atan2(1.5, 1.2)
    for z in (-.4, .4):
        of.cilindro("diagonal-andaime", .02, math.hypot(1.2, 1.5), (0, 1.2, z), "x", "galvanizado", 10, rot=(0, 0, a if z < 0 else -a))
    for k in range(3):
        of.caixa("prancha-andaime", (1.25, .04, .26), (0, 1.5, -.28 + k * .28), "madeira", .006)
    of.caixa("rodape-andaime", (1.25, .12, .02), (0, 1.58, .42), "madeira", .004)
    of.caixa("caixa-ferramentas", (.62, .26, .28), (-.2, .13, -1.0), "vermelho", .02)
    of.caixa("tampa-ferramentas", (.63, .05, .29), (-.2, .285, -1.0), "vermelho", .015)
    of.cilindro("alca-ferramentas", .012, .3, (-.2, .34, -1.0), "x", "chassi", 8)
    for x in (-.45, .05):
        of.caixa("fecho", (.04, .05, .02), (x, .25, -.86), "cromo", .004)


def escada(of):
    for x in (-.19, .19):
        of.caixa("banzo", (.035, 3.4, .07), (x, 1.7, 0), "aluminio", .006)
        of.caixa("sapata-escada", (.05, .05, .09), (x, .025, 0), "plastico", .01)
    for i in range(10):
        of.cilindro("degrau-escada", .016, .38, (0, .3 + i * .32, 0), "x", "aluminio", 10)


# ---------- cone, placa de obra, rede elétrica, pedra ----------
def cone(of):
    of.caixa("base-cone", (.42, .03, .42), (0, 0, 0), "plastico", .03)
    p = [(.015, .19), (.04, .18), (.62, .03), (.635, .025), (.64, 0)]
    of.torno("cone", p, (0, 0, 0), "y", "cone", 24)
    of.torno("faixa-cone", [(.34, .106), (.42, .086)], (0, 0, 0), "y", "refletivo", 24)
    of.torno("faixa-cone2", [(.5, .065), (.55, .052)], (0, 0, 0), "y", "refletivo", 24)


def placa_obra(of):
    for x in (-1.05, 1.05):
        of.caixa("poste-placa", (.08, 2.7, .08), (x, 1.35, 0), "madeira", .01)
    of.caixa("chapa-placa", (2.3, 1.35, .02), (0, 2.0, .05), "plastico-branco", .005)
    of.caixa("faixa-placa", (2.3, .26, .01), (0, 2.5, .065), "plastico-azul", .002)
    for y in (1.325, 2.675):
        of.caixa("moldura-placa", (2.34, .04, .03), (0, y, .05), "aluminio", .005)
    for x in (-1.17, 1.17):
        of.caixa("moldura-placa", (.04, 1.39, .03), (x, 2.0, .05), "aluminio", .005)
    of.caixa("travessa-placa", (2.1, .06, .04), (0, 1.6, -.02), "madeira", .006)
    for k in range(4):  # pictogramas de EPI (círculos azuis) e um triângulo de atenção, sem texto
        of.cilindro("pictograma", .14, .006, (-.85 + k * .38, 1.62, .064), "z", "plastico-azul", 24)
        of.cilindro("pictograma-miolo", .07, .007, (-.85 + k * .38, 1.62, .066), "z", "plastico-branco", 4)
    of.cilindro("atencao", .17, .006, (.75, 1.6, .064), "z", "ambar-placa", 3)  # ponta para cima


def poste(of):
    """Origem no centro do cilindro do kit (9 m de altura)."""
    of.torno("poste", [(-4.5, .2), (4.5, .12), (4.5, 0)], (0, 0, 0), "y", "concreto-poste", 16)
    of.torno("topo-poste", [(4.5, .12), (4.52, 0)], (0, 0, 0), "y", "concreto-poste", 16)
    of.caixa("placa-poste", (.12, .2, .01), (0, -2.6, .2), "plastico-branco", .003)  # a plaqueta de numeração (lisa)
    of.cilindro("braco-luminaria", .03, 1.4, (-.65, 2.9, 0), "x", "galvanizado", 10, rot=(0, 0, -.25))
    of.caixa("luminaria", (.55, .1, .22), (-1.35, 3.1, 0), "cinza", .03)
    of.caixa("lente-luminaria", (.4, .02, .16), (-1.35, 3.045, 0), "farol", .005)


def cruzeta(of):
    """Origem no centro da cruzeta do kit (1,7 × 0,1 × 0,12)."""
    of.caixa("cruzeta", (1.7, .1, .12), (0, 0, 0), "madeira", .012)
    for s in (-1, 1):
        of.caixa("mao-francesa-poste", (.7, .03, .015), (s * .3, -.28, .075), "galvanizado", .002, rot=(0, 0, s * .75))
    of.caixa("cinta-poste", (.3, .06, .26), (0, -.08, 0), "galvanizado", .005)


def isolador(of):
    p = [(-.07, .015), (-.05, .03), (-.045, .06), (-.02, .045), (-.01, .065), (.015, .05), (.025, .07), (.05, .04),
         (.07, .025), (.075, 0)]
    of.torno("isolador", [(a * 1.5, r * 1.5) for a, r in p], (0, 0, 0), "y", "porcelana", 24)


# ---------- frontão do telhado em kit e os caibros da pilha ----------
def frontao(of):
    """Origem e eixos da ExtrudeGeometry do kit: o desenho no plano XY (x −3…3, y 0…3,26) extrudado 0,1 m em z."""
    XQ = 1.68
    HQ = (3 - XQ) * math.tan(math.pi / 3)
    HH = HQ + XQ * math.tan(math.pi / 6)
    pts = [(-3, 0), (3, 0), (XQ, HQ), (0, HH), (-XQ, HQ)]
    of.perfil("frontao", pts, .1, "branco", c0=.05, chanfro=.01, eixo="z")

    def altura(x):
        x = abs(x)
        return HQ * (3 - x) / (3 - XQ) if x > XQ else HQ + (HH - HQ) * (XQ - x) / XQ
    for z in (-.008, .108):  # mata-juntas verticais nas duas faces
        for k in range(1, 15):
            x = -3 + k * .4
            h = altura(x) - .12
            if h > .2:
                of.caixa("mata-junta", (.05, h, .015), (x, .06 + h / 2, z), "branco", .004)
        of.caixa("rodape-frontao", (6.0, .1, .02), (0, .05, z), "cinza", .004)
    for (xa, ya), (xb, yb) in zip(pts[1:], pts[2:] + pts[:1]):  # acabamento nas bordas inclinadas
        if ya == yb == 0:
            continue
        L = math.hypot(xb - xa, yb - ya)
        of.caixa("acabamento-frontao", (L, .08, .14), ((xa + xb) / 2, (ya + yb) / 2, .05), "cinza", .008,
                 rot=(0, 0, math.atan2(yb - ya, xb - xa)))


def agua(of):
    """Uma água do telhado em kit (o bloco 6,6 × 0,16 × L do kit, centrado na origem): painel-sanduíche com a telha
    trapezoidal por cima (nervuras a cada 25 cm, ao longo do caimento) e testeiras de chapa."""
    sx, sy, L = of.pai["dims"] if of.pai is not None and "dims" in of.pai else (6.6, .16, 3.0)
    of.caixa("base-agua", (sx, sy - .04, L), (0, -.02, 0), "cinza", .01)
    of.caixa("chapa-agua", (sx, .012, L), (0, sy / 2 - .03, 0), "zinco", 0)
    n = int(sx / .25)
    for k in range(n + 1):
        of.caixa("nervura", (.035, .035, L), (-sx / 2 + k * sx / n, sy / 2 - .008, 0), "zinco", .004)
    for z in (-L / 2, L / 2):
        of.caixa("testeira", (sx + .02, sy + .02, .02), (0, 0, z), "galvanizado", .004)


def padrao_de_entrada(mats):
    """Poste de entrada de energia do canteiro (concreto, caixa do medidor, disjuntor) junto ao tapume, com o cabo
    descendo em catenária até o contêiner. Coordenadas do mundo (three)."""
    of = Oficina(None, mats)
    px, pz = -11.6, -12.3
    of.caixa("poste-padrao", (.16, 5.0, .16), (px, 2.5, pz), "concreto-poste", .01)
    of.caixa("caixa-medidor", (.38, .55, .22), (px, 1.55, pz + .2), "plastico-branco", .02)
    of.caixa("visor-medidor", (.16, .12, .01), (px, 1.65, pz + .312), "vidro", 0)
    of.caixa("caixa-disjuntor", (.25, .3, .15), (px, 1.05, pz + .17), "cinza", .015)
    of.cilindro("eletroduto-padrao", .025, 3.0, (px + .1, 3.3, pz + .12), "y", "plastico", 10)
    of.cilindro("isolador-padrao", .05, .12, (px, 5.0, pz), "y", "porcelana", 16)
    # cabo até o canto do contêiner (−12,0; 2,9; −11,3), com flecha de 0,6 m
    a, b = Vector((px, 4.95, pz)), Vector((-12.05, 2.95, -11.25))
    pts = [a.lerp(b, t) - Vector((0, .6 * 4 * t * (1 - t), 0)) for t in [k / 8 for k in range(9)]]
    for p0, p1 in zip(pts, pts[1:]):
        meio, d = (p0 + p1) / 2, p1 - p0
        rx = math.atan2(math.hypot(d.x, d.z), d.y)
        ry = math.atan2(d.x, d.z)
        of.cilindro("cabo-energia", .012, d.length, tuple(meio), "y", "plastico", 6, rot=(rx, ry, 0))
    return of.n


def caibros_da_pilha(mats):
    """Caibros de madeira sob a pilha do telhado em kit (no chão, em x 2,2…8,8 × z 3…6,2 do three)."""
    of = Oficina(None, mats)
    for x in (2.9, 4.5, 6.5, 8.1):
        of.caixa("caibro", (.12, .08, 3.6), (x, .06, 4.6), "madeira", .01)
    return of.n


# ---------- restos de obra espalhados pela terra ----------
def restos(mats, solo, vias, cena):
    """~60 sobras no chão do canteiro (tijolo, madeira, vergalhão, pedrisco), longe da estrada e só onde o chão está
    livre (raio vertical). solo: (xmin, xmax, ymin, ymax) no Blender."""
    if not solo:
        return 0
    rnd = np.random.default_rng(21)
    of = Oficina(None, mats)
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    x0, x1, y0, y1 = solo
    feitos = 0
    for k in range(400):
        if feitos >= 60:
            break
        bx, by = rnd.uniform(x0 + 1, x1 - 1), rnd.uniform(y0 + 1, y1 - 1)
        if any(v[0] - 1 < bx < v[1] + 1 for v in vias):
            continue
        achou, ponto, _, _, ob, _ = cena.ray_cast(dg, Vector((bx, by, 6)), Vector((0, 0, -1)))
        if not achou or ponto.z > 1.0 or (ob is not None and ob.name.startswith(("pasto", "Mesh-32")) is False and ponto.z > .25):
            continue
        tipo = rnd.choice(["tijolo", "tijolo", "madeira", "vergalhao", "pedrisco", "pedrisco"])
        tx, tz = bx, -by  # Blender → three
        ry = rnd.uniform(0, 3.14)
        if tipo == "tijolo":
            of.caixa("resto-tijolo", (.19, .09, .09), (tx, ponto.z + .04, tz), "tijolo", .01, rot=(rnd.uniform(-.2, .2), ry, rnd.uniform(0, 1.6)))
        elif tipo == "madeira":
            of.caixa("resto-madeira", (rnd.uniform(.4, 1.2), .025, rnd.uniform(.07, .15)), (tx, ponto.z + .015, tz), "madeira", .005, rot=(0, ry, 0))
        elif tipo == "vergalhao":
            of.cilindro("resto-vergalhao", .006, rnd.uniform(.6, 1.5), (tx, ponto.z + .008, tz), "x", "chassi", 6, rot=(0, ry, 0))
        else:
            of.caixa("resto-pedra", tuple(rnd.uniform(.05, .14, 3)), (tx, ponto.z + .02, tz), "concreto", .02, rot=tuple(rnd.uniform(0, 3, 3)))
        feitos += 1
    return feitos


def extras(vm, ctx):
    """O que o caso modulares acrescenta fora dos grupos: caibros da pilha, padrão de entrada, restos de obra."""
    caibros_da_pilha(vm)
    padrao_de_entrada(vm)
    print(f"restos de obra: {restos(vm, ctx['solo'], ctx['vias'], ctx['cena'])}", flush=True)


# ---------- montagem ----------
MODELOS = {
    "caixa-frente": lambda of, f: caixa_modular(of, True), "caixa-fundo": lambda of, f: caixa_modular(of, False),
    "gancho": lambda of, f: gancho(of), "conteiner": lambda of, f: conteiner(of, f),
    "caixa-dagua": lambda of, f: caixa_dagua(of), "banheiro": lambda of, f: banheiro(of), "cacamba": lambda of, f: cacamba(of),
    "tambor-azul": lambda of, f: tambor(of, "azul"), "tambor-cinza": lambda of, f: tambor(of, "cinza"),
    "palete": lambda of, f: palete(of), "palete-lsf": lambda of, f: palete_lsf(of), "palete-sacos": lambda of, f: palete_sacos(of),
    "palete-lona": lambda of, f: palete_lona(of), "betoneira": lambda of, f: betoneira(of),
    "monte-areia": lambda of, f: monte(of, 1.25, .78, "areia", 1), "monte-brita": lambda of, f: monte(of, 1.1, .55, "brita", 2),
    "pa": lambda of, f: pa(of), "balde-azul": lambda of, f: balde(of, "plastico-azul"), "balde-preto": lambda of, f: balde(of, "plastico"),
    "carrinho": lambda of, f: carrinho(of), "andaime": lambda of, f: andaime(of), "escada": lambda of, f: escada(of),
    "placa-obra": lambda of, f: placa_obra(of), "poste": lambda of, f: poste(of), "poste-cruzeta": lambda of, f: cruzeta(of),
    "poste-isolador": lambda of, f: isolador(of), "frontao": lambda of, f: frontao(of), "agua": lambda of, f: agua(of),
}
def mourao(of):
    """Origem no centro do mourão do kit (caixa 0,11 × 1,3): eucalipto roliço com casca e topo cortado."""
    of.cilindro("mourao", .06, 1.3, (0, 0, 0), "y", "tronco", 10, r2=.055)
    of.cilindro("topo-mourao", .056, .01, (0, .652, 0), "y", "madeira", 10)


def bloco_concreto(of):
    """Origem no centro do bloco do kit (0,39 × 0,19 × 0,19): bloco vazado de dois furos."""
    of.caixa("bloco", (.39, .19, .19), (0, 0, 0), "concreto", .006)
    for x in (-.095, .095):
        of.caixa("furo", (.13, .005, .12), (x, .094, 0), "chassi", 0)


INSTANCIADOS = {"cone-base": cone, "mourao": mourao, "bloco-concreto": bloco_concreto}  # o modelo é instanciado nas matrizes de cada instância do item do kit
SUBSTITUIDOS = set(MODELOS) | {"cone", "cone-faixa", "cone-base", "pedra", "mourao", "bloco-concreto"}  # itens do kit que saem


def colecao_modelo(nome, fazer, mats):
    col = bpy.data.collections.new(nome)
    fazer(Oficina(None, mats, col))
    return col


def montar(raizes, instancias, mats, pedras=None, modelos=None, instanciados=None, sujos=()):
    """raizes: {asset: [objetos animados]}; instancias: {asset: [Matrix no Blender]}; mats: materiais (veiculos.materiais
    mais os de foto: concreto, conteiner, zinco, areia, brita). pedras: [(coleção, altura, base)] dos modelos de pedra."""
    modelos = MODELOS if modelos is None else modelos
    instanciados = INSTANCIADOS if instanciados is None else instanciados
    total = 0
    for asset, lista in raizes.items():
        chave, *params = asset.split(":")  # "painel-lsf:3:2.2" → modelo "painel-lsf" com os parâmetros do kit
        if chave in modelos:
            for raiz in lista:
                of = Oficina(raiz, mats, sujar=chave in sujos)
                if params:
                    raiz["params"] = [float(x) for x in params]
                modelos[chave](of, raiz)
                total += of.n
    for asset, fazer in instanciados.items():
        if asset in instancias:
            col = colecao_modelo(asset, fazer, mats)
            for k, M in enumerate(instancias[asset]):
                ob = bpy.data.objects.new(f"{asset}.{k}", None)
                ob.instance_type = "COLLECTION"; ob.instance_collection = col; ob.matrix_world = M
                bpy.context.scene.collection.objects.link(ob)
            total += len(col.objects)
    if pedras and "pedra" in instancias:
        rnd = np.random.default_rng(13)
        for k, M in enumerate(instancias["pedra"]):
            col, alt, base = pedras[k % len(pedras)]
            loc, rot, esc = M.decompose()
            e = 1.3 * esc.x / alt  # a pedra do kit tem ~2·s de largura e 1,2·s de altura
            ob = bpy.data.objects.new(f"pedra.{k}", None)
            ob.instance_type = "COLLECTION"; ob.instance_collection = col
            ob.matrix_world = (Matrix.Translation((loc.x, loc.y, loc.z - .45 * esc.y)) @ Matrix.Rotation(rnd.uniform(0, 6.3), 4, "Z")
                               @ Matrix.Diagonal((e, e, e, 1)) @ Matrix.Translation((0, 0, -base)))
            bpy.context.scene.collection.objects.link(ob)
    return total

