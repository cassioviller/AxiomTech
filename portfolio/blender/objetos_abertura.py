"""Modelos procedurais da abertura (a mesa do orçamentista com os documentos dos casos) para o --visual cinema do
montar.py. Os documentos (folhas, a tela do tablet) são os do kit, intocados; aqui entram o armário com pastas, rolos e
capacete, o cesto de rolos, a planta (Poly Haven), a cadeira, a lixeira, o tampo e as pernas da mesa, o tablet (só o
corpo), a caneca, o lápis, a trena, o celular, o notebook fechado, a calculadora, o escalímetro, a caneta e a
suculenta (Poly Haven). Coordenadas locais de cada grupo marcado no abertura.html (Y para cima, metros); sem textos."""
import math

import bpy
from mathutils import Matrix

import objetos_veks as V

PASTAS = [0x2E4A7A, 0x2A2B2E, 0x6F7780, 0x3E6B55, 0x2E4A7A, 0x2A2B2E]


def instancia_presa(raiz, col, alt, base, altura, nome):
    e = altura / alt
    ob = bpy.data.objects.new(nome, None)
    ob.instance_type = "COLLECTION"; ob.instance_collection = col
    ob.parent = raiz; ob.matrix_parent_inverse = Matrix.Identity(4)
    ob.matrix_basis = Matrix.Diagonal((e, e, e, 1)) @ Matrix.Translation((0, 0, -base))
    bpy.context.scene.collection.objects.link(ob)


def armario(of, raiz):
    of.caixa("rodape-armario", (1.56, .08, .4), (0, .04, -.02), of.cor(0x2A2B2E, .6), .005)
    of.caixa("corpo-armario", (1.6, .7, .45), (0, .43, 0), "madeira", .006)
    of.caixa("tampo-armario", (1.64, .03, .48), (0, .795, .015), "madeira", .006)
    for x in (-.4, .4):
        of.caixa("porta-armario", (.77, .64, .02), (x, .43, .235), of.cor(0xC6C9CC, .45), .004)
        of.caixa("puxador-armario", (.012, .14, .018), (x + (.3 if x < 0 else -.3), .43, .255), "aluminio", .004)
    for i in range(6):
        c = of.cor(PASTAS[i], .55)
        x = -.72 + i * .076
        of.caixa("pasta-az", (.068, .31, .28), (x, .965, -.03), c, .008)
        of.caixa("etiqueta-az", (.04, .12, .002), (x, 1.0, .111), of.cor(0xF2F0EA, .7), .001)
        of.cilindro("furo-az", .009, .004, (x, .87, .111), "z", "aluminio", 12)
    of.caixa("aparador-livros", (.005, .16, .2), (-.72 + 6 * .076 - .03, .89, -.03), "aluminio", .001)
    of.caixa("base-aparador", (.1, .004, .2), (-.72 + 6 * .076 + .02, .812, -.03), "aluminio", .001)
    for (x, y, z, L) in ((.15, .838, -.08, .72), (.1, .838, .0, .68), (.13, .888, -.04, .7)):
        of.cilindro("rolo", .028, L, (x, y, z), "x", of.cor(0xF2F0EA, .8), 18)
        for d in (-.25, .25):
            of.cilindro("elastico", .0295, .006, (x + d * L, y, z), "x", of.cor(0x1F1F1F, .8), 18)
    # capacete sobre o armário (girado −0,4 em y)
    cx, cy, cz = .62, .81, -.02
    br = of.cor(0xF6F6F3, .3, 0, .6)
    perfil = [(0, .118), (.03, .116), (.06, .1), (.085, .07), (.1, .035), (.105, 0.0)]
    of.torno("casco", perfil, (cx, cy + .007, cz), "y", br, 40)
    of.elipsoide("aba-frente", (.13, .006, .16), (cx + .02 * math.sin(-.4), cy + .004, cz + .02 * math.cos(-.4)), br, rot=(0, -.4, 0))
    of.elipsoide("friso", (.012, .018, .1), (cx, cy + .1, cz), br, rot=(0, -.4, 0))


def cesto_rolos(of, raiz):
    of.torno("cesto-aco", [(0, 0), (0, .14), (.42, .16), (.42, .152), (.01, .132), (.01, 0)], (0, 0, 0), "y",
             of.cor(0x4A5058, .45, .5), 28)
    for i, (x, z, r) in enumerate([(0, 0, .08), (.07, .05, -.05), (-.06, .06, .0), (.03, -.07, .12), (-.05, -.04, -.1), (.08, -.02, .04)]):
        L = .7 + .1 * (i % 3)
        of.cilindro("rolo-cesto", .03, L, (x, .05 + L / 2, z), "y", of.cor(0xF2F0EA, .8), 16, rot=(r * .6, 0, -x * 1.5))


def lixeira(of, raiz):
    """Origem no centro do cilindro do kit (r 0,13/0,11, h 0,28)."""
    of.torno("lixeira", [(-.14, 0), (-.14, .11), (.13, .13), (.14, .135), (.14, .125), (-.13, .1), (-.13, 0)], (0, 0, 0), "y",
             of.cor(0x2A2D31, .5), 32)


def tablet(of, raiz):
    """O corpo do tablet (0,26 × 0,008 × 0,17); a tela do documento fica em y 0,0085 (0,24 × 0,15)."""
    of.caixa("tablet-traseira", (.26, .007, .17), (0, .0035, 0), "aluminio", .004)
    of.caixa("tablet-moldura", (.26, .001, .17), (0, .0076, 0), of.cor(0x0B0D10, .2), .003)


def caneca(of, raiz):
    """Origem no centro do cilindro do kit (r 0,04/0,036, h 0,095)."""
    cer = of.cor(0xF2F0EA, .3, 0, .5)
    of.torno("caneca", [(-.0475, 0), (-.0475, .034), (-.045, .036), (.0475, .04), (.0475, .036), (-.04, .033), (-.04, 0)],
             (0, 0, 0), "y", cer, 32)
    of.cilindro("cafe", .034, .002, (0, .036, 0), "y", of.cor(0x2A1608, .15, 0, 1), 24)
    of.torno("alca", [(-.005, .02), (.005, .02), (.005, .03), (-.005, .03), (-.005, .02)], (.045, .0, 0), "z", cer, 20)


def lapis(of, raiz):
    """Origem no centro do lápis do kit (cilindro r 0,004, 0,18, eixo y local)."""
    of.cilindro("lapis", .0042, .16, (0, -.01, 0), "y", of.cor(0xE8742A, .5), 6)
    of.cilindro("ponta-madeira", .0042, .016, (0, .078, 0), "y", of.cor(0xD9B38C, .7), 6, r2=.0012)
    of.cilindro("borracha", .0042, .012, (0, -.094, 0), "y", of.cor(0xE88A9A, .8), 12)
    of.cilindro("ponteira", .0045, .01, (0, -.084, 0), "y", "aluminio", 12)


def trena(of, raiz):
    """Deitada: o corpo 0,062 × 0,032 × 0,068 com a cinta de borracha."""
    of.caixa("corpo-trena", (.062, .032, .068), (0, .016, 0), of.cor(0xF0C130, .45), .012)
    of.caixa("cinta-trena", (.066, .014, .072), (0, .016, 0), "borracha", .006)
    of.caixa("ponta-trena", (.022, .006, .012), (0, .004, .04), "cromo", .002)
    of.cilindro("trava", .006, .006, (.018, .034, .0), "y", "chassi", 10)


def notebook(of, raiz):
    of.caixa("base-nb", (.30, .01, .21), (0, .005, 0), "aluminio", .005)
    of.caixa("tampa-nb", (.30, .008, .21), (0, .014, .004), of.cor(0x6F7780, .35, .6), .005)
    of.caixa("fresta-nb", (.29, .001, .2), (0, .0101, .004), "chassi", 0)
    of.cilindro("dobradica-nb", .006, .26, (0, .011, -.103), "x", of.cor(0x2A2B2E, .4), 12)
    for x in (-.12, .12):
        for z in (-.08, .08):
            of.cilindro("pe-nb", .006, .002, (x, .0, z), "y", "borracha", 8)


def calculadora(of, raiz):
    of.caixa("corpo-calc", (.085, .012, .16), (0, .006, 0), of.cor(0xC6C9CC, .45), .005)
    of.caixa("visor-calc", (.07, .002, .028), (0, .012, -.058), of.cor(0x3A4A3E, .2, 0, 1), .001)
    for k in range(20):
        x, z = -.03 + (k % 4) * .02, -.03 + (k // 4) * .017
        of.caixa("tecla-calc", (.015, .005, .011), (x, .0135, z), of.cor(0x8A9098 if k % 4 == 3 else 0xF1F1EE, .4), .002)
    of.caixa("painel-solar", (.04, .001, .01), (.015, .0125, -.074), of.cor(0x2A2D3A, .2), 0)


def escalimetro(of, raiz):
    """Ao longo de z, 0,30 m, prisma triangular de raio 0,0095 (centro do grupo)."""
    of.cilindro("escalimetro", .0095, .3, (0, 0, 0), "z", of.cor(0xF3F3F0, .45), 3, rot=(0, 0, math.pi / 2))
    for k, c in enumerate((0x3E6B55, 0x2E4A7A)):
        a = (30, 150)[k] * math.pi / 180
        of.caixa("friso-esc", (.0025, .0008, .28), (.0048 * math.cos(a), .0048 * math.sin(a), 0), of.cor(c, .5), 0, rot=(0, 0, a - math.pi / 2))


def caneta(of, raiz):
    """Ao longo de x, 0,13 m (o grupo do kit)."""
    of.cilindro("corpo-caneta", .0045, .11, (-.01, 0, 0), "x", of.cor(0x2E4A7A, .35), 12)
    of.cilindro("ponta-caneta", .0045, .02, (.055, 0, 0), "x", "aluminio", 12, r2=.0012)
    of.caixa("clipe-caneta", (.04, .002, .003), (-.045, .005, 0), "aluminio", .001)
    of.cilindro("tampa-fundo", .0048, .01, (-.068, 0, 0), "x", of.cor(0x2E4A7A, .35), 12)


def extras(vm, ctx):
    """O quadro com a planta acima do armário e o relógio de parede (Poly Haven) à direita (coordenadas do mundo, three)."""
    from veiculos import Oficina
    V.quadro_planta(Oficina(None, vm), (-.7, 1.55, -2.425), .9, .6, "z", seed=5)
    m = ctx["indice"].get("modelos", {}).get("relogio", [])
    if not m:
        return
    col, alt, base = ctx["colecao"](m[0])
    ob = bpy.data.objects.new("relogio", None)
    ob.instance_type = "COLLECTION"; ob.instance_collection = col
    e = .32 / alt  # 32 cm de diâmetro
    ob.matrix_world = (Matrix.Translation((1.35, 2.41, 2.05 - .16)) @ Matrix.Diagonal((e, e, e, 1))
                       @ Matrix.Translation((0, 0, -base)))  # o modelo já vem em pé, de frente para −Y (a sala)
    bpy.context.scene.collection.objects.link(ob)


PLANTAS, SUCULENTAS = [], []
MODELOS = {
    "armario": armario, "cesto-rolos": cesto_rolos, "lixeira-ab": lixeira, "tablet": tablet, "caneca-ab": caneca,
    "lapis": lapis, "trena-ab": trena, "celular-ab": V.celular, "notebook": notebook, "calculadora": calculadora,
    "escalimetro-ab": escalimetro, "caneta": caneta, "cadeira-ab": V.cadeira, "mesa-tampo": V.mesa_tampo,
    "mesa-perna": V.mesa_perna,
    "planta-chao": lambda of, raiz: PLANTAS and instancia_presa(raiz, *PLANTAS[0], .95, "planta-chao"),
    "suculenta": lambda of, raiz: SUCULENTAS and instancia_presa(raiz, *SUCULENTAS[0], .13, "suculenta"),
}
INSTANCIADOS = {}
SUBSTITUIDOS = set(MODELOS) | {"caneca-extra"}  # o café e a asa do kit saem (a caneca nova já os tem)


def carregar(ctx):
    m = ctx["indice"].get("modelos", {})
    PLANTAS[:] = [ctx["colecao"](x) for x in m.get("planta", [])]
    SUCULENTAS[:] = [ctx["colecao"](x) for x in m.get("suculenta", [])]
