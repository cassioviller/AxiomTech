"""Modelos procedurais do escritório do caso 2 (veks: o sistema de orçamento) para o --visual cinema do montar.py: a mesa,
o gaveteiro, o monitor (a tela é o documento real do kit, intocada), o teclado e o mouse, a impressora (a fenda e a
bandeja ficam onde a proposta sai e pousa), a cadeira giratória, a luminária, a caneca, o porta-canetas, o capacete, o
escalímetro, o celular, a trena, a estante com pastas, rolos e caixas, o cesto, a lixeira de aramado, o quadro de
cortiça e a planta (modelo do Poly Haven).

Cada função modela nas coordenadas locais do grupo marcado no caso-orcamento.html (Y para cima, metros), com as
medidas do kit. Nenhum texto, marca ou logotipo (sigilo)."""
import math

import bpy
import numpy as np
from mathutils import Matrix

from veiculos import B, Oficina

PASTAS = [0x2F4A73, 0x2A2A2C, 0x3F6B4A, 0x7B7F84, 0x7A2E2E, 0x24507A, 0x565A5E]
CANETAS = [0x1F3F7A, 0x202224, 0xB03030, 0x2E7D4F, 0xE8C060]


# ---------- mesa, gaveteiro ----------
def mesa_tampo(of, raiz):
    """Origem no centro do tampo do kit (as medidas vêm da peça do kit: 1,8 × 0,04 × 0,8 no orçamento)."""
    L, _, P = raiz["dims"] if raiz is not None and "dims" in raiz else (1.8, .04, .8)
    of.caixa("tampo", (L, .036, P), (0, .002, 0), "madeira", .004)
    of.caixa("fita-borda", (L + .002, .036, P + .002), (0, .002, 0), of.cor(0x3B3530, .5), .003)
    of.caixa("tampo-face", (L - .01, .002, P - .01), (0, .0205, 0), "madeira", 0)
    of.caixa("calha-cabos", (L * .5, .06, .1), (.0, -.06, -P * .38), of.cor(0x2E3034, .5, .4), .005)


def mesa_perna(of, raiz):
    """Origem no centro da perna do kit (0,05 × 0,71 × 0,05)."""
    of.caixa("perna", (.05, .69, .05), (0, .01, 0), of.cor(0x2E3034, .45, .5, .3), .006)
    of.cilindro("sapata-mesa", .022, .012, (0, -.349, 0), "y", "plastico", 12)


def gaveteiro(of, raiz):
    of.caixa("corpo-gav", (.42, .6, .5), (0, .35, 0), of.cor(0x5A5F66, .45, .4, .2), .01)
    for i in range(3):
        y = .13 + i * .19
        of.caixa("frente-gav", (.39, .175, .014), (0, y + .04, .256), "madeira", .004)
        of.caixa("puxador-gav", (.12, .012, .012), (0, y + .1, .272), "cromo", .004)
        of.cilindro("apoio-puxador", .005, .02, (-.05, y + .1, .265), "z", "cromo", 6)
        of.cilindro("apoio-puxador", .005, .02, (.05, y + .1, .265), "z", "cromo", 6)
    of.cilindro("fechadura", .009, .01, (.15, .63, .257), "z", "cromo", 12)
    for x in (-.17, .17):
        for z in (-.2, .2):
            of.cilindro("rodizio-gav", .022, .018, (x, .025, z), "x", "borracha", 12)


# ---------- monitor, teclado, mouse ----------
def monitor(of, raiz):
    """Origem no grupo do kit (pé na mesa); a tela 0,64 × 0,40 do documento fica em z 0,046, centro y 0,42."""
    preto = of.cor(0x16181B, .35)
    of.cilindro("base-monitor", .12, .012, (0, .006, .01), "y", preto, 32)
    of.caixa("braco-monitor", (.06, .36, .025), (0, .2, -.005), of.cor(0x2B2E33, .4, .6), .01)
    of.cilindro("furo-cabo", .012, .03, (0, .1, -.005), "z", "plastico", 12)
    of.caixa("carcaca", (.6, .36, .035), (0, .42, .012), preto, .015)
    of.caixa("painel", (.68, .44, .012), (0, .42, .037), preto, .004)
    for (x, y, w, h) in ((0, .208, .68, .026), (0, .634, .68, .006), (-.3375, .42, .005, .44), (.3375, .42, .005, .44)):
        of.caixa("moldura", (w, h, .004), (x, y, .0445), preto, 0)
    of.caixa("led", (.006, .003, .002), (.3, .203, .0475), "farol", 0)


def teclado(of, raiz):
    """Origem no centro do teclado do kit (0,44 × 0,015 × 0,14)."""
    base = of.cor(0x1E2024, .45)
    tecla = of.cor(0x2C2F34, .5)
    of.caixa("base-teclado", (.44, .014, .14), (0, -.001, 0), base, .006, rot=(-.04, 0, 0))
    for lin in range(5):
        z = -.05 + lin * .022
        x = -.205
        for col in range(14):
            w = .018 if not (lin == 4 and 4 <= col <= 8) else 0
            if lin == 4 and col == 4:
                of.caixa("barra-espaco", (.11, .007, .016), (-.205 + 4 * .021 + .045, .009, z), tecla, .002)
            if w:
                of.caixa("tecla", (w, .007, .016), (x, .009 + .0004 * lin, z), tecla, .002)
            x += .021
    for lin in range(4):
        for col in range(3):
            of.caixa("tecla-num", (.018, .007, .016), (.13 + col * .021, .009, -.05 + lin * .022), tecla, .002)


def mouse(of, raiz):
    corpo = of.cor(0x1E2024, .35)
    of.elipsoide("mouse", (.03, .017, .05), (0, -.004, 0), corpo)
    of.cilindro("roda-mouse", .005, .005, (0, .011, -.022), "x", "borracha", 12)
    of.caixa("divisao-mouse", (.001, .004, .035), (0, .01, -.025), "plastico", 0)


# ---------- impressora ----------
def impressora(of, raiz):
    """Origem no grupo do kit (na mesa); a fenda de saída fica em y 0,05 / z 0,173, a bandeja em y 0,013 / z 0,295."""
    corpo = of.cor(0x2A2D31, .45)
    claro = of.cor(0xCDD0D3, .4)
    of.caixa("corpo-impressora", (.40, .12, .34), (0, .06, 0), corpo, .015)
    of.caixa("tampa-scanner", (.40, .05, .33), (0, .145, -.005), claro, .012)
    of.caixa("vidro-scanner-borda", (.38, .004, .02), (0, .172, .155), corpo, .002)
    of.caixa("painel-impressora", (.14, .03, .06), (.12, .135, .16), corpo, .006, rot=(-.5, 0, 0))
    of.caixa("visor-impressora", (.06, .002, .035), (.1, .15, .17), "vidro", 0, rot=(-.5, 0, 0))
    for k in range(3):
        of.cilindro("botao", .006, .004, (.155 + 0 * k, .145 - k * .008, .175 + k * .006), "y", claro, 10)
    of.caixa("fenda", (.30, .012, .01), (0, .05, .171), "chassi", 0)
    of.caixa("bandeja", (.32, .006, .25), (0, .013, .295), claro, .003)
    of.caixa("batente-bandeja", (.32, .02, .006), (0, .022, .418), claro, .002)
    of.caixa("gaveta-papel", (.36, .045, .012), (0, .03, .171), corpo, .004)
    of.caixa("puxador-gaveta", (.1, .008, .008), (0, .02, .178), "plastico", .002)
    of.caixa("alimentador", (.3, .006, .14), (0, .2, -.2), claro, .003, rot=(.9, 0, 0))
    of.caixa("papel-entrada", (.21, .012, .13), (0, .205, -.195), of.cor(0xF6F5F0, .8), .001, rot=(.9, 0, 0))
    for k in range(6):
        of.caixa("ventilacao", (.004, .05, .002), (.201, .06, -.1 + k * .03), "chassi", 0)


# ---------- cadeira giratória ----------
def cadeira(of, raiz):
    plast = of.cor(0x1D1F23, .5)
    tecido = of.cor(0x2E3947, .96)
    for i in range(5):
        a = i * 2 * math.pi / 5
        ext = (math.sin(a) * .3, .05, math.cos(a) * .3)
        of.barra("pe-cadeira", (0, .085, 0), ext, .018, plast)
        g = (math.sin(a) * .3, .028, math.cos(a) * .3)
        of.cilindro("rodizio", .025, .012, (g[0] - .01, g[1], g[2]), "x", "borracha", 14)
        of.cilindro("rodizio", .025, .012, (g[0] + .01, g[1], g[2]), "x", "borracha", 14)
        of.caixa("garfo", (.03, .03, .03), (g[0], .055, g[2]), plast, .005)
    of.cilindro("cubo-base", .045, .05, (0, .09, 0), "y", plast, 16)
    of.cilindro("pistao", .022, .3, (0, .24, 0), "y", "cromo", 16)
    of.cilindro("capa-pistao", .035, .14, (0, .17, 0), "y", plast, 16)
    of.caixa("mecanismo", (.24, .05, .22), (0, .385, 0), plast, .01)
    of.caixa("assento", (.48, .075, .46), (0, .445, 0), tecido, .035)
    of.caixa("costura-assento", (.44, .002, .42), (0, .4835, 0), of.cor(0x253040, .96), 0)
    of.caixa("encosto", (.46, .55, .06), (0, .78, .24), tecido, .03, rot=(-.1, 0, 0))
    of.caixa("lombar", (.38, .1, .03), (0, .63, .205), of.cor(0x253040, .96), .012, rot=(-.1, 0, 0))
    of.caixa("haste-encosto", (.06, .32, .03), (0, .55, .28), plast, .01, rot=(-.1, 0, 0))
    for x in (-.26, .26):
        of.caixa("suporte-braco", (.03, .22, .05), (x, .58, .05), plast, .008)
        of.caixa("braco", (.065, .025, .26), (x, .7, .03), plast, .01)


# ---------- objetos da mesa ----------
def luminaria(of, raiz):
    preto = of.cor(0x202226, .4, .3)
    of.cilindro("base-lum", .072, .022, (0, .011, 0), "y", preto, 32)
    a, b, c = (0, .02, 0), (-.03, .30, -.05), (.16, .33, .12)
    for dz in (-.008, .008):
        of.barra("haste1", (a[0], a[1], a[2] + dz), (b[0], b[1], b[2] + dz), .005, preto)
        of.barra("haste2", (b[0], b[1], b[2] + dz), (c[0], c[1], c[2] + dz), .005, preto)
    of.barra("mola", (0, .06, 0), (-.022, .2, -.035), .009, "cromo", 8)
    of.elipsoide("junta", (.016, .016, .016), b, "cromo")
    of.elipsoide("junta2", (.014, .014, .014), c, "cromo")
    # cúpula apontando para a planta
    d = np.array([.35, -1, .5]); d /= np.linalg.norm(d)
    of.barra("cupula", (c[0] + d[0] * .01, c[1] + d[1] * .01, c[2] + d[2] * .01),
             (c[0] + d[0] * .1, c[1] + d[1] * .1, c[2] + d[2] * .1), .022, preto, 24, r2=.055)
    if "lampada-acesa" not in of.mats:  # a luminária acesa: luz quente (2700 K) sobre a planta
        from veiculos import principled
        of.mats["lampada-acesa"] = principled("lampada-acesa", (1, .85, .65), .3, emissao=((1.0, .78, .5), 25))[0]
    of.barra("lampada", (c[0] + d[0] * .095, c[1] + d[1] * .095, c[2] + d[2] * .095),
             (c[0] + d[0] * .1, c[1] + d[1] * .1, c[2] + d[2] * .1), .048, "lampada-acesa", 24)
    luz = bpy.data.lights.new("luminaria", "SPOT")
    luz.energy = 6; luz.spot_size = math.radians(80); luz.spot_blend = .6; luz.shadow_soft_size = .03
    luz.color = (1.0, .8, .58)
    lo = bpy.data.objects.new("luminaria", luz); bpy.context.scene.collection.objects.link(lo)
    lo.parent = raiz; lo.matrix_parent_inverse = Matrix.Identity(4)
    from veiculos import B
    from mathutils import Vector
    lo.location = B(c[0] + d[0] * .11, c[1] + d[1] * .11, c[2] + d[2] * .11)
    lo.rotation_mode = "QUATERNION"; lo.rotation_quaternion = B(*d).to_track_quat("-Z", "Y")


def caneca(of, raiz):
    cer = of.cor(0xE2DAD0, .3, 0, .5)
    of.torno("caneca", [(0, .0), (0, .036), (.003, .038), (.093, .04), (.095, .04), (.095, .036), (.006, .033), (.006, 0)],
             (0, 0, 0), "y", cer, 32)
    of.cilindro("cafe", .034, .002, (0, .082, 0), "y", of.cor(0x2A1A10, .15, 0, 1), 24)
    of.torno("alca", [(-.005, .02), (.005, .02), (.005, .03), (-.005, .03), (-.005, .02)], (.045, .05, 0), "z", cer, 20)


def porta_canetas(of, raiz):
    of.torno("copo", [(0, 0), (0, .034), (.095, .036), (.095, .032), (.005, .03), (.005, 0)], (0, 0, 0), "y",
             of.cor(0x2B2F34, .45, .3), 28)
    for i, (x, z, rz) in enumerate([(.012, .01, .12), (-.014, .008, -.1), (0, -.016, .05), (-.01, -.005, -.16), (.018, -.012, .1)]):
        of.cilindro("caneta", .0045, .15, (x, .085, z), "y", of.cor(CANETAS[i], .4), 10, rot=(-rz * .6, 0, rz))
        of.cilindro("tampa-caneta", .0052, .035, (x - math.sin(rz) * .06, .085 + math.cos(rz) * .06, z), "y", of.cor(CANETAS[i], .4), 10, rot=(-rz * .6, 0, rz))


def capacete(of, raiz):
    """Capacete de obra: casco oval com aba larga na frente (pala), friso central e dois laterais."""
    br = of.cor(0xF3F3EF, .3, 0, .6)
    perfil = [(0, .118), (.03, .116), (.06, .1), (.085, .07), (.1, .035), (.105, 0.0)]
    of.torno("casco", perfil, (0, .006, 0), "y", br, 40)
    of.elipsoide("aba", (.135, .006, .17), (0, .005, .025), br)
    of.elipsoide("friso", (.012, .02, .105), (0, .1, 0), br)
    for x in (-.045, .045):
        of.elipsoide("friso-lado", (.008, .012, .085), (x, .088, 0), br, rot=(0, 0, -x * 6))
    of.caixa("suspensao", (.15, .01, .12), (0, .02, 0), "plastico", .004)


def escalimetro(of, raiz):
    """Origem no centro do prisma do kit (cilindro de 3 faces, eixo y, r 0,016, 0,30)."""
    of.cilindro("escalimetro", .016, .30, (0, 0, 0), "y", of.cor(0xEFE8D6, .5), 3)
    for k, c in enumerate((0x3E6B55, 0x2E4A7A, 0xB03030)):
        a = k * 2 * math.pi / 3 + math.pi / 3
        of.caixa("friso-escala", (.003, .28, .001), (math.cos(a) * .0081, 0, math.sin(a) * .0081), of.cor(c, .5), 0, rot=(0, -a, 0))


def celular(of, raiz):
    of.caixa("celular", (.072, .008, .148), (0, .004, 0), of.cor(0x2B2F34, .3, .7), .006)
    of.caixa("tela-cel", (.066, .001, .14), (0, .0085, 0), of.cor(0x0E1013, .1, .3, 1), .004)
    of.cilindro("camera-cel", .006, .002, (-.022, .0089, -.062), "y", "chassi", 12)


def trena(of, raiz):
    of.caixa("corpo-trena", (.066, .066, .034), (0, .034, 0), of.cor(0xF0BE2E, .45), .016)
    of.caixa("borracha-trena", (.07, .024, .036), (0, .034, 0), "borracha", .01)
    of.caixa("ponta-trena", (.012, .014, .02), (.036, .012, 0), "cromo", .002)
    of.caixa("fita", (.004, .012, .018), (.04, .012, 0), of.cor(0xE8D27A, .4, .3), 0)
    of.caixa("clipe-trena", (.04, .05, .004), (0, .035, -.019), "cromo", .003)
    of.caixa("trava-trena", (.012, .008, .016), (-.01, .068, 0), "chassi", .003)


# ---------- estante, cesto, lixeira, quadro, planta ----------
def pasta(of, x, y, i):
    c = of.cor(PASTAS[i % len(PASTAS)], .55)
    of.caixa("pasta", (.072, .32, .29), (x, y + .16, .02), c, .008)
    of.caixa("etiqueta", (.042, .13, .002), (x, y + .2, .166), of.cor(0xF2F0EA, .7), .001)
    of.cilindro("furo-pasta", .009, .004, (x, y + .07, .166), "z", "aluminio", 12)


def estante(of, raiz):
    mad = "madeira"
    for y in (0, .45, .9, 1.35):
        of.caixa("prateleira", (1.17, .03, .35), (0, y + .03, 0), mad, .004)
        of.caixa("borda-prat", (1.17, .03, .004), (0, y + .03, .176), of.cor(0x3B3530, .5), 0)
    for x in (-.6, .6):
        of.caixa("lateral", (.03, 1.5, .35), (x, .75, 0), mad, .004)
    of.caixa("fundo", (1.2, 1.5, .012), (0, .75, -.169), mad, .002)
    of.caixa("rodape-estante", (1.17, .05, .02), (0, .025, .16), mad, .003)
    for i in range(8):
        pasta(of, -.53 + i * .078, .045, i)
    for i in range(5):
        pasta(of, -.53 + i * .078, .495, i + 3)
    for i in range(3):
        of.caixa("catalogo", (.22, .012, .3), (.38, .505 + i * .013, 0), of.cor(0xF2F0EA, .7) if i % 2 else of.cor(PASTAS[5], .6), .002)
    for i, (x, y, z) in enumerate([(-.25, .99, -.05), (-.25, .99, .04), (-.25, 1.065, -.005)]):
        of.cilindro("rolo", .043, .95, (x, y, z), "x", of.cor(0xF2F0EA, .8) if i == 1 else of.cor(0xD8C39C, .9), 20)
        of.cilindro("elastico", .0445, .008, (x + .22 - i * .1, y, z), "x", of.cor(0xE8742A, .5), 20)
    for x in (-.4, .4):
        of.caixa("caixa-arquivo", (.33, .13, .26), (x, 1.46, .02), of.cor(0xD8C39C, .9), .005)
        of.caixa("tampa-caixa", (.335, .02, .265), (x, 1.52, .02), of.cor(0xCDB78F, .9), .004)
        of.caixa("pega-caixa", (.06, .02, .002), (x, 1.47, .151), "chassi", 0)
    for i in range(3):
        pasta(of, -.13 + i * .078, 1.395, i + 1)


def cesto(of, raiz):
    vime = of.cor(0x5B4634, .85)
    of.torno("cesto", [(0, 0), (0, .14), (.38, .17), (.38, .16), (.01, .13), (.01, 0)], (0, 0, 0), "y", vime, 28)
    for k in range(6):
        of.torno("trama", [(.03 + k * .06, .143 + k * .005), (.04 + k * .06, .145 + k * .005)], (0, 0, 0), "y", of.cor(0x4A3828, .9), 28)
    for i, (x, z, rz) in enumerate([(-.06, .0, .08), (.06, .03, -.05), (0, -.06, .1), (.07, -.03, .06)]):
        of.cilindro("rolo-cesto", .04, .9, (x, .48, z), "y", of.cor(0xD8C39C, .9) if i % 2 else of.cor(0xF2F0EA, .8), 18, rot=(rz * .6, 0, rz))


def lixeira(of, raiz):
    aco = of.cor(0x3A3D42, .45, .7)
    of.cilindro("fundo-lixeira", .11, .01, (0, .005, 0), "y", aco, 24)
    of.torno("aro-topo", [(.295, .127), (.305, .127), (.305, .133), (.295, .133)], (0, 0, 0), "y", aco, 32)
    of.torno("aro-meio", [(.145, .117), (.155, .117), (.155, .122), (.145, .122)], (0, 0, 0), "y", aco, 32)
    for k in range(28):
        a = 2 * math.pi * k / 28
        of.barra("arame", (math.cos(a) * .11, .01, math.sin(a) * .11), (math.cos(a) * .13, .3, math.sin(a) * .13), .0018, aco, 4)
    of.elipsoide("papel-amassado", (.045, .036, .045), (.02, .1, .02), of.cor(0xF2F0EA, .9))


def quadro_cortica(of, raiz):
    cortica = of.cor(0xC49B6B, .96)
    of.caixa("cortica", (.9, .6, .02), (0, 0, .01), cortica, .002)
    for (x, y, w, h) in ((0, .315, .93, .03), (0, -.315, .93, .03), (-.45, 0, .03, .66), (.45, 0, .03, .66)):
        of.caixa("moldura-quadro", (w, h, .03), (x, y, .015), "madeira", .004)
    rnd = np.random.default_rng(4)
    for (x, y, rz, tipo) in [(-.28, .14, .05, 0), (-.02, .12, -.03, 0), (.25, .15, .02, 0), (-.25, -.14, -.04, 1), (.05, -.13, .03, 2), (.3, -.15, -.02, 0)]:
        w, h = (.2, .15) if tipo == 2 else (.17, .23)
        cor = {0: 0xF2F0EA, 1: 0x8B8F94, 2: 0x6E7F5A}[tipo]
        of.caixa("folha-quadro", (w, h, .0015), (x, y, .021), of.cor(cor, .8), 0, rot=(rnd.uniform(-.02, .02), rnd.uniform(-.03, .03), rz))
        if tipo == 0:
            for k in range(5):
                of.caixa("linha-folha", (w * .7, .004, .0005), (x, y + .07 - k * .03, .0225), of.cor(0x9AA0A6, .8), 0, rot=(0, 0, rz))
        px, py = x - math.sin(rz) * .1, y + math.cos(rz) * .1
        of.elipsoide("percevejo", (.007, .007, .004), (px, py, .027), of.cor((0xE8742A, 0xB03030, 0x2F4A73)[tipo], .4))


def planta_vaso(of, raiz, colecao, modelos):
    """A planta em vaso: o modelo do Poly Haven (potted_plant_02), com ~1 m de altura, no lugar do vaso do kit."""
    if not modelos:
        return
    col, alt, base = modelos[0]
    e = 1.0 / alt
    ob = bpy.data.objects.new("planta-vaso", None)
    ob.instance_type = "COLLECTION"; ob.instance_collection = col
    ob.parent = raiz; ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = Matrix.Diagonal((e, e, e, 1)) @ Matrix.Translation((0, 0, -base))
    bpy.context.scene.collection.objects.link(ob)


def quadro_planta(of, centro, larg, alt, eixo_normal, seed=1):
    """Quadro emoldurado com uma planta baixa desenhada só com linhas (sem texto). eixo_normal: "z" (parede de fundo,
    olhando +z) ou "-x" (parede da direita, olhando −x). Coordenadas do mundo (three)."""
    rnd = np.random.default_rng(seed)
    cx, cy, cz = centro
    def pos(u, v, w):  # u: largura, v: altura, w: para fora da parede
        return (cx + u, cy + v, cz + w) if eixo_normal == "z" else (cx - w, cy + v, cz - u)
    def tam(a, b, c):
        return (a, b, c) if eixo_normal == "z" else (c, b, a)
    preto = of.cor(0x1E1F22, .4)
    of.caixa("moldura", tam(larg + .06, alt + .06, .03), pos(0, 0, .015), preto, .006)
    of.caixa("passe-partout", tam(larg, alt, .005), pos(0, 0, .032), of.cor(0xF4F2EC, .8), 0)
    linha = of.cor(0x3A3D42, .7)
    w, h = larg * .7, alt * .62
    for (u, v, a, b) in ((0, h / 2, w, .004), (0, -h / 2, w, .004), (-w / 2, 0, .004, h), (w / 2, 0, .004, h)):
        of.caixa("parede-planta", tam(a, b, .002), pos(u, v, .036), linha, 0)
    for k in range(4):  # divisões internas
        u = rnd.uniform(-w / 2 + .03, w / 2 - .03)
        v0, v1 = sorted(rnd.uniform(-h / 2, h / 2, 2))
        of.caixa("divisao", tam(.003, max(v1 - v0, .04), .002), pos(u, (v0 + v1) / 2, .036), linha, 0)
        v = rnd.uniform(-h / 2 + .02, h / 2 - .02)
        of.caixa("divisao", tam(rnd.uniform(.05, w * .5), .003, .002), pos(rnd.uniform(-w / 4, w / 4), v, .036), linha, 0)


def extras(vm, ctx):
    """O computador que o monitor pede: um gabinete sob a mesa, à esquerda (coordenadas do mundo, three)."""
    of = Oficina(None, vm)
    preto = of.cor(0x16181B, .4)
    x, z = -.55, -1.72
    of.caixa("gabinete", (.2, .44, .45), (x, .24, z), preto, .012)
    of.caixa("frente-gabinete", (.2, .44, .01), (x, .24, z + .226), of.cor(0x2B2E33, .35, .4), .006)
    of.cilindro("botao-liga", .012, .006, (x, .42, z + .232), "z", "aluminio", 16)
    of.caixa("led-gabinete", (.004, .004, .002), (x + .04, .42, z + .232), "farol", 0)
    for k in range(6):
        of.caixa("ventilacao-gab", (.14, .006, .002), (x, .1 + k * .025, z + .232), "chassi", 0)
    for dx in (-.08, .08):
        for dz in (-.18, .18):
            of.cilindro("pe-gabinete", .012, .02, (x + dx, .01, z + dz), "y", "borracha", 10)
    # o cabo de vídeo: da traseira do gabinete sobe pela perna até a calha da mesa
    pts = [(x, .3, z - .23), (x - .02, .2, z - .3), (-.3, .1, -1.98), (-.12, .2, -1.95), (-.1, .6, -1.92), (-.05, .7, -1.9)]
    for a_, b_ in zip(pts, pts[1:]):
        of.barra("cabo-video", a_, b_, .0045, "plastico", 6)
    # tomada na parede do fundo, régua no chão com o plugue do gabinete; o quadro da planta na parede da direita
    of.caixa("tomada", (.08, .12, .015), (-.3, .3, -2.945), "plastico-branco", .005)
    of.caixa("regua", (.32, .045, .06), (-.3, .025, -2.85), "plastico-branco", .01)
    of.caixa("interruptor-regua", (.02, .012, .03), (-.43, .05, -2.85), of.cor(0xB03030, .4), .003)
    of.caixa("plugue", (.04, .03, .03), (-.2, .06, -2.85), "plastico", .004)
    quadro_planta(of, (3.95, 1.55, -.9), .7, .5, "-x", seed=2)
    m = ctx["indice"].get("modelos", {}).get("relogio", [])
    if m:  # o relógio na parede da direita (x = 4), de frente para a sala
        col, alt, base = ctx["colecao"](m[0])
        ob = bpy.data.objects.new("relogio", None)
        ob.instance_type = "COLLECTION"; ob.instance_collection = col
        e = .3 / alt
        ob.matrix_world = (Matrix.Translation((3.94, .4, 2.0)) @ Matrix.Rotation(-math.pi / 2, 4, "Z")
                           @ Matrix.Diagonal((e, e, e, 1)) @ Matrix.Translation((0, 0, -base)))
        bpy.context.scene.collection.objects.link(ob)


PLANTAS = []  # [(coleção, altura, base)] carregadas em extras()
MODELOS = {
    "mesa-tampo": mesa_tampo, "mesa-perna": mesa_perna, "gaveteiro": gaveteiro, "monitor": monitor, "teclado": teclado,
    "mouse": mouse, "impressora": impressora, "cadeira": cadeira, "luminaria": luminaria, "caneca": caneca,
    "porta-canetas": porta_canetas, "capacete": capacete, "escalimetro": escalimetro, "celular": celular, "trena": trena,
    "estante": estante, "cesto": cesto, "lixeira": lixeira, "quadro-cortica": quadro_cortica,
    "vaso-planta": lambda of, raiz: planta_vaso(of, raiz, None, PLANTAS),
}
INSTANCIADOS = {}
SUBSTITUIDOS = set(MODELOS)


def carregar(ctx):
    """Antes de montar: os modelos do Poly Haven que este caso usa (indice["modelos"]["planta"])."""
    PLANTAS[:] = [ctx["colecao"](m) for m in ctx["indice"].get("modelos", {}).get("planta", [])]
