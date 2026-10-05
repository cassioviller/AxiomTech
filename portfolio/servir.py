#!/usr/bin/env python3
"""Servidor estático com Range (HTTP 206). O Chrome só busca (`currentTime`) num vídeo cujo servidor responde
`Accept-Ranges: bytes` e 206 a `Range: bytes=a-b`; o `python3 -m http.server` responde 200 e o vídeo fica preso
no primeiro quadro. Mesma linha de comando do http.server:
    python3 portfolio/servir.py 5000 --bind 0.0.0.0 --directory portfolio/site
"""
import argparse
import io
import os
import re
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer


class ComRange(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".webp": "image/webp", ".mp4": "video/mp4", ".js": "text/javascript"}

    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError):
            # Navegação e busca em vídeos podem cancelar a requisição em curso.
            # Apenas encerre esta conexão; os demais erros continuam visíveis.
            self.close_connection = True

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Cache-Control", "no-cache")  # o navegador sempre confere se o arquivo mudou (304 se não mudou)
        super().end_headers()

    def send_head(self):
        m = re.match(r"bytes=(\d+)-(\d*)$", self.headers.get("Range", ""))
        caminho = self.translate_path(self.path)
        if not m or not os.path.isfile(caminho):
            return super().send_head()
        tamanho = os.path.getsize(caminho)
        a = int(m.group(1))
        b = min(int(m.group(2)) if m.group(2) else tamanho - 1, tamanho - 1)
        if a >= tamanho or a > b:
            self.send_error(416, "Range Not Satisfiable")
            return None
        with open(caminho, "rb") as f:
            f.seek(a)
            dados = f.read(b - a + 1)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(caminho))
        self.send_header("Content-Range", f"bytes {a}-{b}/{tamanho}")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        return io.BytesIO(dados)

    def log_message(self, *_):
        pass


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("porta", type=int, nargs="?", default=8000)
    p.add_argument("--bind", default="127.0.0.1")
    p.add_argument("--directory", default=".")
    a = p.parse_args()
    ThreadingHTTPServer((a.bind, a.porta), partial(ComRange, directory=a.directory)).serve_forever()


if __name__ == "__main__":
    main()
