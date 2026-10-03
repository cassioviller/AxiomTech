"""Modelos procedurais do caso SIGE (a obra dos galpões numa fazenda e o escritório de obra) para o --visual cinema do
montar.py. Reaproveita os modelos do canteiro do modulares (objetos.py) e dos veículos (veiculos.py) com as medidas do
kit desta cena, os do escritório (objetos_veks.py, objetos_abertura.py) e acrescenta o gerador, o contêiner-almoxarifado,
a caçamba retangular, a garrafa térmica, o galão de água, a caixa térmica, a prancheta e o gado ao longe. A tela do
notebook e as folhas na parede são os documentos do kit, intocados. Coordenadas locais de cada grupo marcado no
caso-sige.html (Y para cima, metros); sem textos nem marcas."""
import math

import bpy
from mathutils import Matrix

import objetos as O
import objetos_abertura as A
import objetos_veks as V
import veiculos


# ---------- veículos ----------
def caminhao(of, raiz):
    veiculos.caminhao(of, topo=1.23, rodas=((-1.05, 1.05), (3.3, -1.7, -3.0)), R=.52)
    for z0 in (-4.5, -1.35):  # as cintas amarelas das duas fiadas de painéis
        for z in (z0 + .5, z0 + 2.5):
            of.caixa("cinta", (2.42, .04, .05), (0, 1.75, z), of.cor(0xE3B72B, .55), .005)
            for x in (-1.21, 1.21):
                of.caixa("cinta-lado", (.02, .5, .05), (x, 1.5, z), of.cor(0xE3B72B, .55), .003)
            of.caixa("catraca", (.08, .05, .07), (1.22, 1.3, z), "cromo", .01)


# ---------- canteiro ----------
def cone(of, raiz):
    """Origem no centro do cone do kit (0,7 m, r 0,22): o cone do modulares, um pouco maior, com a base no chão."""
    of.caixa("base-cone", (.5, .03, .5), (0, -.355, 0), "plastico", .03)
    p = [(.015, .21), (.04, .2), (.68, .035), (.695, .028), (.7, 0)]
    of.torno("cone", [(a - .37, r) for a, r in p], (0, 0, 0), "y", "cone", 24)
    of.torno("faixa-cone", [(-.0, .118), (.09, .096)], (0, 0, 0), "y", "refletivo", 24)
    of.torno("faixa-cone2", [(.15, .075), (.2, .062)], (0, 0, 0), "y", "refletivo", 24)


def betoneira(of, raiz):
    for x in (-.55, .55):
        of.roda("roda-betoneira", (x, .22, -.25), .22, .1, "x", .12, "aro", lado=1 if x > 0 else -1)
    of.cilindro("eixo", .025, 1.15, (0, .22, -.25), "x", "chassi", 10)
    of.caixa("travessa", (1.1, .08, .08), (0, .45, 0), "laranja", .01)
    of.caixa("lanca-reboque", (.08, .08, 1.0), (0, .45, 0), "laranja", .01)
    of.cilindro("engate", .05, .06, (0, .4, .52), "y", "chassi", 12)
    for x in (-.5, .5):
        of.caixa("coluna", (.06, .9, .06), (x, .9, .2), "laranja", .01)
    perfil = [(-.15, .0), (-.15, .3), (.0, .42), (.15, .45), (.3, .4), (.5, .3), (.6, .26), (.62, .28)]
    of.torno("tambor", perfil, (0, 1.25, .2), "y", "laranja", 40, rot=(-.6, 0, 0))
    of.torno("coroa", [(.05, .44), (.05, .47), (.1, .47), (.1, .44)], (0, 1.25, .2), "y", "chassi", 40, rot=(-.6, 0, 0))
    of.caixa("motor", (.4, .3, .35), (.4, .3, .35), "cinza", .03)
    of.cilindro("polia", .1, .04, (.4, .5, .35), "x", "chassi", 20)


def caixa_dagua(of, raiz):
    O.caixa_dagua(of, torre="cinza")


def gerador(of, raiz):
    verde = of.cor(0x4C5B4A, .45, .3, .2)
    of.caixa("base-gerador", (1.4, .12, .8), (0, .06, 0), "chassi", .01)
    of.caixa("cabine-gerador", (1.2, .8, .7), (0, .52, 0), verde, .03)
    for k in range(9):  # venezianas
        of.caixa("aleta", (.5, .02, .01), (-.25, .3 + k * .05, .356), "chassi", 0)
    of.caixa("painel-gerador", (.3, .25, .02), (.35, .6, .356), "chassi", .005)
    for k in range(3):
        of.cilindro("instrumento", .025, .006, (.27 + k * .08, .65, .368), "z", "farol", 16)
    of.cilindro("escapamento", .04, .5, (.4, 1.1, 0), "y", "cromo", 12)
    of.cilindro("chapeu", .06, .03, (.4, 1.36, 0), "y", "chassi", 12)
    of.caixa("tampa-tanque", (.3, .25, .3), (-.35, 1.04, 0), "cinza", .02)
    for x in (-.5, .5):
        of.caixa("olhal-gerador", (.08, .06, .02), (x, .95, 0), "chassi", .005)
    for z in (-.2, .2):  # galões de diesel
        of.caixa("galao-diesel", (.3, .4, .3), (.95, .2, z), of.cor(0x2A3F5E, .5), .04)
        of.cilindro("bocal", .03, .04, (1.0, .42, z), "y", "plastico", 12)


def conteiner(of, raiz):
    """Origem no centro do corpo do kit (6 × 2,55 × 2,4)."""
    of.caixa("corpo", (6, 2.55, 2.4), (0, 0, 0), "conteiner", .01)
    for x in (-2.97, 2.97):
        for z in (-1.17, 1.17):
            of.caixa("coluna", (.12, 2.55, .12), (x, 0, z), of.cor(0x2A3F5E, .5, .3), .01)
            for y in (-1.2, 1.2):
                of.caixa("quina", (.18, .14, .16), (x, y, z), "chassi", .01)
    for y in (-1.2, 1.2):
        for z in (-1.18, 1.18):
            of.caixa("trilho", (6, .14, .1), (0, y, z), of.cor(0x2A3F5E, .5, .3), .01)
    for x in (-3.02, 3.02):  # portas com as barras de travamento
        of.caixa("porta", (.04, 2.2, 2.1), (x, 0, 0), of.cor(0x2A3F5E, .5, .3), .01)
        for z in (-.75, -.3, .3, .75):
            of.cilindro("barra-trava", .02, 2.25, (x * 1.008, 0, z), "y", "galvanizado", 8)
            of.caixa("manopla", (.03, .25, .03), (x * 1.012, -.2, z + .08), "galvanizado", .005)
    for p in ((-1.5, -.85), (1.5, -.85), (-1.5, .85), (1.5, .85)):
        of.caixa("viga-chao", (.6, .3, .4), (p[0], -1.43, p[1]), "concreto", .02)


def cacamba(of, raiz):
    az = of.cor(0x2A3F5E, .5, .3)
    of.caixa("fundo-cacamba", (3.4, .12, 1.9), (0, .3, 0), az, .01)
    for x in (-1.7, 1.7):
        of.caixa("cabeceira", (.1, 1.5, 1.9), (x, 1.05, 0), az, .015)
    for z in (-.95, .95):
        of.caixa("lateral", (3.4, 1.5, .1), (0, 1.05, z), az, .015)
        for x in (-1.2, -.4, .4, 1.2):
            of.caixa("reforco", (.08, 1.45, .06), (x, 1.05, z * 1.06), az, .008)
        for x in (-1.3, 1.3):
            of.cilindro("olhal", .08, .1, (x, 1.6, z * 1.05), "z", "chassi", 16)
    for p in ((-1.5, -.8), (1.5, -.8), (-1.5, .8), (1.5, .8)):
        of.caixa("pe-cacamba", (.3, .3, .3), (p[0], .15, p[1]), "borracha", .03)


def monte_areia(of, raiz):
    O.monte(of, 1.0, 1.0, "areia-fina", 3, base=-.05, aspereza=.025, lisa=False, cone=True, grao=.03)


def monte_brita(of, raiz):
    O.monte(of, 1.0, 1.0, "brita", 4, base=-.05, aspereza=.16, lisa=False, cone=True)
    # pedriscos soltos rolados para a base do monte (o grupo do kit tem escala r × h × 0,85r)
    import numpy as np
    rnd = np.random.default_rng(8)
    for k in range(40):
        a, d = rnd.uniform(0, 6.3), rnd.uniform(.85, 1.15)
        of.caixa("pedrisco", tuple(rnd.uniform(.02, .05, 3)), (d * math.cos(a), rnd.uniform(0, .05), d * math.sin(a)), "brita", .01,
                 rot=tuple(rnd.uniform(0, 3, 3)))


def mourao(of):
    of.cilindro("mourao", .07, 1.7, (0, 0, 0), "y", "tronco", 10, r2=.06)
    of.cilindro("topo-mourao", .062, .01, (0, .852, 0), "y", "madeira", 10)


def boi(of, raiz):
    """Nelore ao longe: corpo, cupim, cabeça, barbela, pernas e rabo (formas lisas; só se vê de longe)."""
    couro = of.cor(0xCFCBC2, .85)
    escuro = of.cor(0x6B6660, .85)
    of.elipsoide("corpo", (.33, .42, .78), (0, 1.15, -.05), couro)
    of.elipsoide("cupim", (.18, .2, .22), (0, 1.55, .5), couro)
    of.elipsoide("pescoco", (.2, .26, .3), (0, 1.2, .78), couro)
    of.elipsoide("cabeca", (.13, .17, .3), (0, 1.05, 1.15), couro, rot=(.5, 0, 0))
    of.elipsoide("focinho", (.09, .08, .08), (0, .9, 1.38), escuro)
    for x in (-.12, .12):
        of.elipsoide("orelha", (.08, .03, .05), (x * 1.4, 1.17, 1.05), couro)
        of.barra("chifre", (x * .6, 1.2, 1.05), (x * 1.0, 1.32, 1.0), .018, escuro, 6, r2=.006)
    of.elipsoide("barbela", (.08, .2, .25), (0, .85, .75), couro)
    for (x, z) in ((-.2, .55), (.2, .55), (-.2, -.6), (.2, -.6)):
        of.barra("perna", (x, .95, z), (x, .08, z), .055, couro, 8, r2=.04)
        of.cilindro("casco", .045, .08, (x, .04, z), "y", escuro, 8)
    of.barra("rabo", (0, 1.25, -.82), (0, .55, -.9), .02, couro, 6)


# ---------- escritório ----------
def notebook_aberto(of, raiz):
    """Origem no grupo `note` do kit: base 0,34 × 0,018 × 0,24; a tampa gira −15° em x na dobradiça (0; 0,018; −0,12)."""
    of.caixa("base-note", (.34, .018, .24), (0, .009, 0), of.cor(0x3A3D42, .35, .6), .006)
    of.caixa("teclado-note", (.3, .002, .11), (0, .0185, -.025), of.cor(0x16181B, .5), .002)
    for lin in range(5):
        for col in range(13):
            of.caixa("tecla-note", (.018, .002, .016), (-.135 + col * .0225, .02, -.072 + lin * .02), of.cor(0x22252A, .5), .002)
    of.caixa("touchpad", (.1, .001, .06), (0, .0185, .075), of.cor(0x2B2E33, .3), .003)
    th = -math.radians(15)
    def tampa(y, z):  # tampa-local → note-local
        return (0, .018 + y * math.cos(th) - z * math.sin(th), -.12 + y * math.sin(th) + z * math.cos(th))
    of.caixa("tampa-note", (.34, .23, .007), tampa(.115, -.0005), of.cor(0x3A3D42, .35, .6), .005, rot=(th, 0, 0))
    of.caixa("moldura-tela", (.34, .23, .001), tampa(.115, .0035), of.cor(0x0B0D10, .2), .004, rot=(th, 0, 0))
    of.cilindro("dobradica", .006, .3, (0, .018, -.12), "x", "chassi", 10)


def quadro_cortica(of, raiz):
    """Origem no centro da cortiça do kit (0,9 × 0,66, na parede)."""
    V.quadro_cortica(of, raiz)


def garrafa(of, raiz):
    """Origem no centro do corpo da garrafa térmica do kit (r 0,05, 0,3)."""
    of.torno("garrafa", [(-.15, 0), (-.15, .048), (-.14, .05), (.12, .05), (.15, .045), (.15, 0)], (0, 0, 0), "y", "cromo", 32)
    of.torno("tampa-garrafa", [(.15, .045), (.24, .045), (.25, .03), (.25, 0)], (0, 0, 0), "y", "plastico", 24)
    of.torno("alca-garrafa", [(-.005, .06), (.005, .06), (.005, .075), (-.005, .075), (-.005, .06)], (.06, .0, 0), "z", "plastico", 20)


def galao(of, raiz):
    """Galão de 20 L (origem no centro do corpo do kit, r 0,14, 0,45)."""
    azul = of.cor(0x2F62A8, .25, 0, .6)
    p = [(-.225, 0), (-.225, .13), (-.21, .14), (-.12, .14), (-.1, .13), (-.08, .14), (.1, .14), (.16, .12), (.2, .07),
         (.24, .05), (.27, .05), (.27, 0)]
    of.torno("galao", p, (0, 0, 0), "y", azul, 32)


def caixa_termica(of, raiz):
    az = of.cor(0x2F62A8, .45)
    of.caixa("caixa-termica", (.5, .38, .36), (0, 0, 0), az, .04)
    of.caixa("tampa-termica", (.52, .05, .38), (0, .21, 0), of.cor(0xE8E4D8, .4), .02)
    of.cilindro("alca-termica", .015, .45, (0, .25, 0), "x", "plastico", 10)
    for x in (-.24, .24):
        of.caixa("suporte-alca", (.03, .05, .04), (x, .23, 0), "plastico", .006)


def prancheta(of, raiz):
    of.caixa("prancheta", (.24, .008, .33), (0, 0, 0), of.cor(0x6B4A2E, .6), .004)
    of.caixa("papel-prancheta", (.21, .002, .29), (0, .005, .01), of.cor(0xF2F0EA, .8), 0)
    for k in range(8):
        of.caixa("linha", (.16, .0005, .003), (0, .0062, -.08 + k * .03), of.cor(0x9AA0A6, .8), 0)
    of.caixa("prendedor", (.1, .015, .04), (0, .01, -.15), "cromo", .004)


def cadeira_plastica(of, raiz):
    """A cadeira do kit (assento a 0,47 m) vira a cadeira monobloco do Poly Haven."""
    if CADEIRAS:
        A.instancia_presa(raiz, *CADEIRAS[0], .8, "cadeira-monobloco")


_PAINEIS = {}


def painel_lsf(of, raiz):
    """Painel de Light Steel Frame como sai da fábrica: guias U em cima e embaixo, montantes C (90 × 40 mm com
    enrijecedor) a cada 40 cm, bloqueador U no meio, fitas metálicas em X numa face. Grupo do kit: x 0…compr, y 0…alt,
    espessura 9 cm centrada em z. Um modelo por tamanho, instanciado (os galpões têm ~50 painéis)."""
    compr, alt = raiz["params"] if "params" in raiz else (3.0, 2.2)
    chave = (round(compr, 3), round(alt, 3))
    if chave not in _PAINEIS:
        col = bpy.data.collections.new(f"painel-lsf-{chave[0]}x{chave[1]}")
        o = veiculos.Oficina(None, of.mats, col)
        t, W, F = .0025, .09, .04  # chapa, alma, aba
        g = "galvanizado"
        for y0, s in ((0, 1), (alt, -1)):  # guias
            o.caixa("guia-alma", (compr, t, W), (compr / 2, y0 + s * t / 2, 0), g, 0)
            for z in (-W / 2, W / 2):
                o.caixa("guia-aba", (compr, F, t), (compr / 2, y0 + s * F / 2, z), g, 0)
        n = round(compr / .4)
        H = alt - 2 * t
        for i in range(n + 1):
            x = min(i * .4, compr - .02)
            lado = 1 if x < compr - .05 else -1
            o.caixa("montante-alma", (t, H, W), (x, alt / 2, 0), g, 0)
            for z in (-W / 2, W / 2):
                o.caixa("montante-aba", (F, H, t), (x + lado * F / 2, alt / 2, z), g, 0)
                o.caixa("enrijecedor", (t, H, .012), (x + lado * F, alt / 2, z - (z / abs(z)) * .006), g, 0)
        o.caixa("bloqueador-alma", (compr, t, W), (compr / 2, alt / 2, 0), g, 0)
        for z in (-W / 2, W / 2):
            o.caixa("bloqueador-aba", (compr, F, t), (compr / 2, alt / 2 + F / 2, z), g, 0)
        L = math.hypot(compr, alt)
        for sinal in (1, -1):  # fitas em X na face de fora
            o.caixa("fita", (L, .05, .0012), (compr / 2, alt / 2, W / 2 + .002), g, 0, rot=(0, 0, sinal * math.atan2(alt, compr)))
        _PAINEIS[chave] = col
    ob = bpy.data.objects.new("painel-lsf", None)
    ob.instance_type = "COLLECTION"; ob.instance_collection = _PAINEIS[chave]
    ob.parent = raiz; ob.matrix_parent_inverse = Matrix.Identity(4)
    bpy.context.scene.collection.objects.link(ob)


def pilar(of, raiz):
    """Pilar metálico da cobertura (o kit: caixa 0,25 × 4,8 centrada): perfil I soldado, placa de base com 4
    chumbadores e porcas, chapa de topo para a tesoura."""
    H, g = 4.8, of.cor(0x6A7078, .45, .5)
    of.caixa("alma", (.012, H - .04, .22), (0, 0, 0), g, .002)
    for x in (-.12, .12):
        of.caixa("mesa", (.016, H - .04, .25), (x, 0, 0), g, .003)
    of.caixa("placa-base", (.4, .025, .4), (0, -H / 2 + .0125, 0), g, .004)
    of.caixa("placa-topo", (.3, .02, .3), (0, H / 2 - .01, 0), g, .004)
    for x in (-.15, .15):
        for z in (-.15, .15):
            of.cilindro("chumbador", .012, .08, (x, -H / 2 + .05, z), "y", "galvanizado", 8)
            of.cilindro("porca", .022, .02, (x, -H / 2 + .035, z), "y", "galvanizado", 6)
    of.caixa("enrijecedor", (.22, .15, .01), (0, -H / 2 + .1, 0), g, .002)  # enrijecedor da base


def bota(of, raiz):
    """Bota de borracha (origem no pé do kit: caixa 0,11 × 0,1 × 0,3)."""
    b = of.cor(0x16181A, .55)
    of.elipsoide("pe", (.06, .055, .15), (0, -.01, .02), b)
    of.caixa("sola", (.115, .025, .3), (0, -.04, .0), of.cor(0x2A2522, .8), .012)
    of.cilindro("cano", .058, .3, (0, .19, -.08), "y", b, 16, r2=.064)
    of.torno("borda-cano", [(-.01, .064), (.01, .066)], (0, .34, -.08), "y", of.cor(0xE3B72B, .5), 16)


CADEIRAS = []
MODELOS = {
    "pilar": pilar, "bota": bota,
    "painel-lsf": painel_lsf,
    "caminhao-sige": caminhao, "caminhonete": lambda of, raiz: veiculos.picape(of), "cone-sige": cone,
    "betoneira-sige": betoneira, "carrinho-sige": lambda of, raiz: O.carrinho(of),
    "balde-sige-preto": lambda of, raiz: O.balde(of, "plastico"), "balde-sige-pvc": lambda of, raiz: O.balde(of, "plastico-branco"),
    "tambor-sige-azul": lambda of, raiz: O.tambor(of, "azul"), "tambor-sige-cinza": lambda of, raiz: O.tambor(of, "cinza"),
    "caixa-dagua-sige": caixa_dagua, "gerador": gerador, "banheiro-sige": lambda of, raiz: O.banheiro(of),
    "conteiner-sige": conteiner, "cacamba-sige": cacamba, "monte-areia-sige": monte_areia, "monte-brita-sige": monte_brita,
    "boi": boi, "mesa-tampo": V.mesa_tampo, "mesa-perna": V.mesa_perna, "notebook-aberto": notebook_aberto,
    "cortica-sige": quadro_cortica, "capacete-sige": V.capacete, "garrafa": garrafa, "caneca-sige": A.caneca,
    "galao": galao, "caixa-termica": caixa_termica, "prancheta": prancheta, "cadeira-plastica": cadeira_plastica,
}
INSTANCIADOS = {"mourao-sige": mourao}
# a céu aberto na obra: as cores lisas ganham poeira e uso (o escritório e o gado ficam limpos)
SUJOS = {"caminhao-sige", "caminhonete", "cone-sige", "betoneira-sige", "carrinho-sige", "balde-sige-preto", "balde-sige-pvc",
         "tambor-sige-azul", "tambor-sige-cinza", "caixa-dagua-sige", "gerador", "banheiro-sige", "conteiner-sige", "cacamba-sige"}
# itens do kit que saem sem modelo próprio (a peça nova já os inclui)
SUBSTITUIDOS = set(MODELOS) | set(INSTANCIADOS) | {"cone-sige-base", "tambor-aro", "bota-cano", "cortica-extra", "capacete-extra",
                                                   "garrafa-extra", "galao-extra", "caixa-termica-extra"}


def carregar(ctx):
    CADEIRAS[:] = [ctx["colecao"](x) for x in ctx["indice"].get("modelos", {}).get("cadeira-plastica", [])]
