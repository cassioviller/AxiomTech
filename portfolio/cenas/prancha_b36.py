#!/usr/bin/env python3
"""Redesenha a prancha do B-36 ("como cada caixa viaja → como fica depois de unida") sem móveis: só paredes,
divisórias, escada do sótão em símbolo de planta, nomes dos ambientes, cotas, face de junção, vão livre e portão.
Mesmo tamanho e mesma posição dos elementos da prancha anterior (2308 × 1443), para o destaque e o recorte de
documentos.json continuarem valendo.

Uso: python portfolio/cenas/prancha_b36.py   → site/docs/b36-caixas.webp e b36-caixas-recorte.webp
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parent.parent  # portfolio/
W, H = 2308, 1443
AZUL, VERMELHO, VERDE, OURO = (31, 74, 90), (168, 59, 47), (21, 110, 82), (201, 160, 40)
PAREDE, PISO, BANHO, TEXTO, CINZA = (46, 51, 56), (244, 241, 232), (221, 231, 238), (40, 44, 48), (110, 110, 110)
FONTES = ["DejaVuSans{}.ttf", "C:/Windows/Fonts/segoeui{}.ttf", "C:/Windows/Fonts/arial{}.ttf"]


def fonte(tam, negrito=False):
    for f in FONTES:
        nome = f.format("-Bold" if negrito and "DejaVu" in f else ("b" if negrito and "segoe" in f else ("bd" if negrito else "")))
        try:
            return ImageFont.truetype(nome, tam)
        except OSError:
            continue
    return ImageFont.load_default()


img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)


def texto(xy, s, tam, cor=TEXTO, negrito=False, ancora="mm"):
    d.text(xy, s, fill=cor, font=fonte(tam, negrito), anchor=ancora)


def cota_h(x0, x1, y, rotulo):
    d.line([(x0, y), (x1, y)], fill=CINZA, width=2)
    for x, s in ((x0, 1), (x1, -1)):
        d.line([(x, y), (x + s * 12, y - 6)], fill=CINZA, width=2); d.line([(x, y), (x + s * 12, y + 6)], fill=CINZA, width=2)
    texto(((x0 + x1) / 2, y - 16), rotulo, 15)


def cota_v(x, y0, y1, rotulo):
    d.line([(x, y0), (x, y1)], fill=CINZA, width=2)
    for y, s in ((y0, 1), (y1, -1)):
        d.line([(x, y), (x - 6, y + s * 12)], fill=CINZA, width=2); d.line([(x, y), (x + 6, y + s * 12)], fill=CINZA, width=2)
    rot = Image.new("RGBA", (80, 30), (255, 255, 255, 0))
    ImageDraw.Draw(rot).text((40, 15), rotulo, fill=TEXTO, font=fonte(15), anchor="mm")
    rot = rot.rotate(90, expand=True)
    img.paste(rot, (int(x - 30), int((y0 + y1) / 2 - 40)), rot)


def caixa_planta(x0, y0, x1, y1, t=12):
    d.rectangle([x0, y0, x1, y1], fill=PAREDE)
    d.rectangle([x0 + t, y0 + t, x1 - t, y1 - t], fill=PISO)


def juncao(x0, x1, y, rotulo_y):
    d.rectangle([x0, y - 5, x1, y + 5], fill=(250, 235, 230), outline=VERMELHO, width=2)
    for x in range(int(x0) + 6, int(x1) - 6, 18):
        d.line([(x, y + 4), (x + 12, y - 4)], fill=VERMELHO, width=2)
    for x in (x0, x1 - 14):
        d.rectangle([x, y - 7, x + 14, y + 7], fill=VERMELHO)
    texto(((x0 + x1) / 2, rotulo_y), "FACE DE JUNÇÃO — pórtico contraventado + filme", 13, VERMELHO, True)


def escada(x0, y0, x1, y1, degraus=9):
    d.rectangle([x0, y0, x1, y1], fill=(236, 230, 216), outline=PAREDE, width=2)
    for k in range(1, degraus):
        x = x0 + (x1 - x0) * k / degraus
        d.line([(x, y0), (x, y1)], fill=(150, 140, 120), width=1)
    ym = (y0 + y1) / 2
    d.line([(x0 + 10, ym), (x1 - 18, ym)], fill=PAREDE, width=2)
    d.polygon([(x1 - 8, ym), (x1 - 20, ym - 6), (x1 - 20, ym + 6)], fill=PAREDE)
    texto((x0 + (x1 - x0) * .3, y1 + 13), "escada do sótão ↑", 12, CINZA)


def banho(x0, y0, x_div, y_div, y1, t=12):
    """Banheiro no canto inferior esquerdo: piso claro, divisória com a porta (vão) junto à parede da cozinha."""
    d.rectangle([x0 + t, y_div, x_div, y1 - t], fill=BANHO)
    d.rectangle([x0 + t, y_div - 4, x_div - 70, y_div + 4], fill=PAREDE)   # parede de cima (com o vão da porta)
    d.rectangle([x_div - 4, y_div - 4, x_div + 4, y1 - t], fill=PAREDE)    # parede da cozinha


# título
texto((29, 300), "COMO CADA CAIXA VIAJA  →  COMO FICA DEPOIS DE UNIDA", 30, AZUL, True, "lm")

# caixa 1: banho e cozinha; a face de junção em cima
caixa_planta(97, 625, 569, 866)
banho(97, 625, 285, 702, 866)
texto((193, 785), "BANHO", 16, TEXTO, True); texto((461, 782), "COZINHA", 15, TEXTO, True)
juncao(97, 569, 635, 601)
texto((317, 533), "CAIXA 1 · 3,00 × 6,00 m", 20, VERMELHO, True)
texto((317, 556), "banho e cozinha completos de fábrica", 20, VERMELHO, True)
cota_v(69, 635, 856, "3,00"); cota_h(107, 559, 900, "6,00")

# +
texto((661, 752), "+", 64, OURO, True)

# caixa 2: estar, jantar e a escada do sótão; a face de junção embaixo
caixa_planta(796, 625, 1267, 866)
escada(808, 637, 984, 703)
texto((1102, 760), "ESTAR · JANTAR", 17, TEXTO, True)
juncao(796, 1267, 856, 891)
texto((1015, 533), "CAIXA 2 · 3,00 × 6,00 m", 20, VERMELHO, True)
texto((1015, 556), "estar, jantar e escada do sótão", 20, VERMELHO, True)
cota_h(806, 1257, 591, "6,00"); cota_v(767, 635, 856, "3,00")

# =
texto((1371, 752), "=", 64, VERDE, True)

# unidas: caixa 2 em cima, caixa 1 embaixo, vão livre corrido na junta
caixa_planta(1598, 498, 2129, 1028)
escada(1612, 511, 1788, 577)
banho(1598, 763, 1806, 844, 1028)
texto((1925, 640), "ESTAR · JANTAR", 18, TEXTO, True); texto((1925, 664), "11,0 m²", 16, TEXTO, True)
texto((1706, 940), "BANHO", 16, TEXTO, True); texto((2008, 934), "COZINHA", 15, TEXTO, True)
for x in range(1620, 2110, 30):
    d.line([(x, 763), (x + 16, 763)], fill=VERMELHO, width=3)
for x in (1606, 2108):
    d.rectangle([x, 750, x + 14, 776], fill=VERMELHO)
texto((1863, 728), "VÃO LIVRE 6,00 m — viga de transferência acima", 13, VERMELHO, True)
texto((1863, 797), "diagonais provisórias já removidas", 12, VERMELHO)
d.rectangle([2117, 646, 2125, 883], fill=(255, 255, 255), outline=VERDE, width=2)  # o portão
d.line([(2193, 763), (2135, 763)], fill=VERDE, width=4)
d.polygon([(2131, 763), (2147, 754), (2147, 772)], fill=VERDE)
rot = Image.new("RGBA", (160, 30), (255, 255, 255, 0))
ImageDraw.Draw(rot).text((80, 15), "PORTÃO 2,60", fill=VERDE, font=fonte(14, True), anchor="mm")
rot = rot.rotate(90, expand=True); img.paste(rot, (2216, 683), rot)
texto((1894, 354), "UNIDAS NA OBRA · 6,00 × 6,00 m = 36 m²", 22, VERDE, True)
texto((1894, 377), "vão livre corrido, ambiente único", 22, VERDE, True)
cota_h(1608, 2119, 456, "6,00"); cota_v(1567, 508, 755, "3,00"); cota_v(1567, 771, 1018, "3,00")

# a nota de rodapé
texto((29, 1146), "Nenhuma marcenaria fixa, louça ou instalação atravessa a linha de junta — cada caixa sai da fábrica com seus "
      "ambientes completos. Na obra só se faz: selagem da junta, acabamento da linha e as ligações elétrica e hidráulica entre as caixas.",
      18, CINZA, False, "lm")

docs = RAIZ / "site" / "docs"
img.save(docs / "b36-caixas.webp", quality=92, method=6)
x, y, w, h = json.loads((RAIZ / "cenas" / "documentos.json").read_text(encoding="utf-8"))["b36-caixas"]["recorte"]
img.crop((x, y, x + w, y + h)).save(docs / "b36-caixas-recorte.webp", quality=92, method=6)
print("pronto:", docs / "b36-caixas.webp")
