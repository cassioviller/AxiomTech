#!/usr/bin/env bash
# Gera os PDFs (currículo e folhas de caso) a partir dos HTML, com o Chromium em modo headless.
set -euo pipefail
cd "$(dirname "$0")"
pdf(){ chromium --headless --no-sandbox --disable-gpu --no-pdf-header-footer --virtual-time-budget=8000 --print-to-pdf="$2" "file://$PWD/$1" 2>/dev/null; echo "$2: $(pdfinfo "$2" | awk '/Pages/{print $2}') pág."; }
pdf curriculo/curriculo.html curriculo/curriculo-cassio-viller.pdf
pdftotext -layout curriculo/curriculo-cassio-viller.pdf curriculo/curriculo-cassio-viller.txt
for f in casos/caso-*.html; do pdf "$f" "${f%.html}.pdf"; done
# o site serve os mesmos PDFs
cp curriculo/curriculo-cassio-viller.pdf site/
cp casos/caso-*.pdf site/casos/
# a imagem de compartilhamento (og:image), a partir de og.html
chromium --headless --no-sandbox --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --window-size=1200,630 --virtual-time-budget=8000 --screenshot=site/og.png "file://$PWD/og.html" 2>/dev/null; echo "site/og.png: $(identify -format '%w × %h' site/og.png)"
