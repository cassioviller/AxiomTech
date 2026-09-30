#!/usr/bin/env python3
"""Extrai as paredes a construir (vermelhas) da planta do cliente (site/img/upa-plan.webp) como segmentos horizontais,
numa grade de 4 px, para a cena do caso 2 levantá-las em 3D sobre a folha. Escreve cenas/paredes-upa.js.

Uso: python3 portfolio/cenas/paredes.py
"""
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PLANTA = AQUI.parent / "site" / "img" / "upa-plan.webp"
SAIDA = AQUI / "paredes-upa.js"
CELULA = 4  # px da planta por célula


def mascara():
    """Grade booleana (linhas × colunas) do vermelho da planta, reduzida a CELULA px."""
    largura, altura = map(int, subprocess.check_output(["magick", "identify", "-format", "%w %h", str(PLANTA)]).split())
    cols, rows = largura // CELULA, altura // CELULA
    # vermelho saturado: canal R alto, G e B baixos → branco; o resto → preto; depois reduz (média) e limiariza
    pbm = subprocess.check_output(["magick", str(PLANTA), "-fx", "(r>0.55 && g<0.4 && b<0.4) ? 1 : 0", "-scale", f"{cols}x{rows}!",
                                   "-threshold", "30%", "-negate", "-compress", "none", "pbm:-"])  # PBM: 1 = preto = vermelho
    linhas = [l for l in pbm.decode().split("\n") if l and not l.startswith("#")]
    assert linhas[0] == "P1"
    dados = "".join(linhas[2:]).replace(" ", "")
    return [[dados[r * cols + c] == "1" for c in range(cols)] for r in range(rows)], cols, rows


def segmentos(grade, cols, rows):
    """Corridas horizontais de células vermelhas: [c0, c1, r] (c1 exclusivo)."""
    seg = []
    for r in range(rows):
        c = 0
        while c < cols:
            if grade[r][c]:
                c0 = c
                while c < cols and grade[r][c]:
                    c += 1
                seg.append([c0, c, r])
            else:
                c += 1
    return seg


if __name__ == "__main__":
    grade, cols, rows = mascara()
    seg = [s for s in segmentos(grade, cols, rows) if s[2] >= 8 and s[1] > 5]  # fora: a linha de divisa à esquerda e a barra do topo
    cheias = sum(1 for r in grade for v in r if v)
    SAIDA.write_text("// gerado por paredes.py a partir de site/img/upa-plan.webp: corridas horizontais [c0, c1, linha] numa grade de "
                     f"{cols}×{rows} células de {CELULA} px\nexport const GRADE = [{cols}, {rows}];\nexport const SEGMENTOS = "
                     + "[" + ",".join(f"[{a},{b},{c}]" for a, b, c in seg) + "];\n", encoding="utf-8")
    print(f"{cols}×{rows} células, {cheias} vermelhas, {len(seg)} segmentos → {SAIDA.name} ({SAIDA.stat().st_size // 1024} KB)")
    # imagem de conferência
    linhas = ["P1", f"{cols} {rows}"] + ["".join("1" if v else "0" for v in r) for r in grade]
    subprocess.run(["magick", "pbm:-", "-negate", "-fill", "red", "-opaque", "black", "-scale", "400%", str(AQUI / "saida" / "paredes-debug.png")],
                   input="\n".join(linhas).encode(), check=True)
