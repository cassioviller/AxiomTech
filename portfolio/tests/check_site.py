#!/usr/bin/env python3
"""Checagens do site do portfólio.

Garante que reescrever texto não muda número conferido, não apaga ressalva
honesta, não quebra o HTML e que cada caso abre pelo resultado (Minto).
Uso: python3 portfolio/tests/check_site.py
"""
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # portfolio/
SITE = ROOT / "site" / "portfolio.html"  # o portfólio completo; a história é o index.html
BASE = "2a686cf"  # commit de referência dos números conferidos
FALHAS = []

# Casos já reescritos em Minto (título exato do <h4>). As Tasks 3–5 preenchem.
CASOS_MINTO = [
    "Redesenhei a casa para caber no teto de R$ 500 mil",
    "R$ 24,5 milhões medidos no desenho, sem quantidades do cliente",
    "71 → 0 menções internas numa proposta de R$ 964.917",
    "O diário que estava no WhatsApp",
    "O cliente confirma que leu",
    "Da venda à obra",
    "Compras com governança",
    "O celeiro não cabe inteiro no caminhão",
    "Geminar 4 unidades corta cerca de 28% do custo por unidade",
    "A planta do cliente não cabia no terreno dele",
]

RESSALVAS = [
    "cópia do sistema",
    "onde a empresa ligou",
    "nos 19 serviços conferidos",
    "ligadas empresa por empresa",
    "assistentes de IA",
    "Dados de exemplo do manual",
]

DESIGN = ROOT / "DESIGN.md"
SECOES_DESIGN = [
    "## 1. Tema visual e atmosfera",
    "## 2. Paleta de cores e papéis",
    "## 3. Tipografia",
    "## 4. Componentes",
    "## 5. Layout",
    "## 6. Profundidade e elevação",
    "## 7. Faça e não faça",
    "## 8. Comportamento responsivo",
    "## 9. Guia para agentes",
]


def check(cond, msg):
    if not cond:
        FALHAS.append(msg)


def main_html(html):
    return html[html.index("<main"):html.index("</main>")]


def texto(html):
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def numeros(html):
    return set(re.findall(r"\d+(?:[.,]\d+)*", texto(main_html(html))))


def casos(html):
    """título do <h4> → HTML interno do <div class="body"> de cada caso numerado."""
    out = {}
    for parte in html.split("<details")[1:]:
        if '<span class="n">' not in parte:
            continue
        seg = parte.split("</details>")[0]
        titulo = re.search(r"<h4>(.*?)</h4>", seg).group(1)
        corpo = seg[seg.index('<div class="body">') + len('<div class="body">'):]
        corpo = corpo[:corpo.rindex("</div>")]
        out[titulo] = corpo.strip()
    return out


class Balanco(HTMLParser):
    TAGS = {"div", "details", "figure", "section", "ul", "ol", "main", "summary"}

    def __init__(self):
        super().__init__()
        self.pilha = []
        self.erros = []

    def handle_starttag(self, tag, attrs):
        if tag in self.TAGS:
            self.pilha.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag):
        if tag not in self.TAGS:
            return
        if not self.pilha or self.pilha[-1][0] != tag:
            self.erros.append(f"</{tag}> inesperado na linha {self.getpos()[0]}")
        else:
            self.pilha.pop()


def checar_invariantes(atual, base):
    # fase 3 do site v2 (spec §5): o multiplicador "≈ 27×" saiu do portfólio; nenhum outro número pode sumir ou aparecer
    na, nb = numeros(atual), numeros(base) - {"27"}
    check(na == nb, f"números mudaram — novos: {sorted(na - nb)}; sumiram: {sorted(nb - na)}")
    t = texto(atual)
    for r in RESSALVAS:
        check(
            t.count(r) >= texto(base).count(r) and r in t,
            f"ressalva {r!r}: {t.count(r)} ocorrências, base tinha {texto(base).count(r)}",
        )
    b = Balanco()
    b.feed(atual)
    check(not b.erros and not b.pilha, f"tags desbalanceadas: {b.erros[:3]} abertas: {b.pilha[:3]}")
    check(atual.count("<details open>") == 3, "o primeiro caso de cada lista precisa continuar <details open> (3 no total)")


def checar_minto(atual):
    cs = casos(atual)
    for titulo in CASOS_MINTO:
        corpo = cs.get(titulo)
        check(corpo is not None, f"caso não encontrado: {titulo!r}")
        if corpo is None:
            continue
        check(
            corpo.startswith("<p><strong>Resultado.</strong>") or corpo.startswith("<div><h5>Resultado</h5>"),
            f"caso não abre pelo resultado: {titulo!r}",
        )
        n = corpo.count("<strong>Resultado.</strong>") + corpo.count("<h5>Resultado</h5>")
        check(n == 1, f"caso com {n} blocos Resultado: {titulo!r}")
        check("Resultado:" not in corpo, f"'Resultado:' solto no corpo: {titulo!r}")
    check("O que o sistema fez" not in atual, "ainda há 'O que o sistema fez' — a autoria deve ser 'O que fiz'")
    for titulo in CASOS_MINTO[:3]:
        corpo = cs.get(titulo, "")
        check("com o sistema" in corpo, f"caso da Folha 02 sem 'com o sistema' no O que fiz: {titulo!r}")


def checar_design(atual):
    check(DESIGN.exists(), "portfolio/DESIGN.md não existe")
    if not DESIGN.exists():
        return
    d = DESIGN.read_text(encoding="utf-8")
    for s in SECOES_DESIGN:
        check(s in d, f"DESIGN.md sem a seção {s!r}")
    raiz = re.findall(r":root[^{]*\{(.*?)\}", atual, flags=re.S)
    for hexa in sorted({h.upper() for bloco in raiz for h in re.findall(r"#[0-9A-Fa-f]{6}", bloco)}):
        check(hexa in d.upper(), f"DESIGN.md não documenta a cor {hexa}")


LEGENDAS = {
    # antiga → nova
    "Rede de restaurantes de rodovia · o prédio medido e desenhado pelo sistema a partir do arquivo do cliente, cobertura em corte":
        "Rede de restaurantes de rodovia · sem nenhuma quantidade no pacote, o prédio foi medido no próprio arquivo do cliente — cobertura em corte",
    "B-36 · celeiro 6 × 6 m com sótão, entregue em duas caixas":
        "B-36 · o celeiro 6 × 6 m não cabe inteiro no caminhão: vai em duas caixas",
    "B-36 · interior com bancada sob a viga da junção":
        "B-36 · a viga da junção ficou aparente — sai mais barato que fechar — e a bancada vai embaixo dela",
    "Kitnet modular 30 m² · layouts validados por código":
        "Kitnet modular 30 m² · cada layout passa pelo validador de colisões antes de ser desenhado",
    "Como cada caixa viaja e como fica depois de unida":
        "Como cada caixa viaja e onde fica a junção depois de unida",
}


def checar_legendas(atual):
    for antiga, nova in LEGENDAS.items():
        check(antiga not in atual, f"legenda antiga ainda no site: {antiga[:50]!r}")
        check(nova in atual, f"legenda nova ausente: {nova[:50]!r}")


def main():
    atual = SITE.read_text(encoding="utf-8")
    base = subprocess.run(
        ["git", "show", f"{BASE}:portfolio/site/index.html"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout
    checar_invariantes(atual, base)
    checar_minto(atual)
    checar_design(atual)
    checar_legendas(atual)
    if FALHAS:
        print("FALHOU:")
        for f in FALHAS:
            print(" -", f)
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
