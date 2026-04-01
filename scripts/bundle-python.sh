#!/bin/bash
# Bundle the Python backend with PyInstaller for macOS .app distribution.
# Output: dist-python/guru-backend (standalone binary, no Python required)

set -e
cd "$(dirname "$0")/.."

VENV_PYTHON="python/.venv/bin/python3"
if [ ! -f "$VENV_PYTHON" ]; then
  echo "Error: Python venv not found. Run scripts/install-mac.sh first."
  exit 1
fi

echo "==> Installing PyInstaller..."
"$VENV_PYTHON" -m pip install pyinstaller --quiet

echo "==> Bundling Python backend..."
"$VENV_PYTHON" -m PyInstaller \
  --onefile \
  --name guru-backend \
  --distpath dist-python \
  --workpath dist-python/build \
  --specpath dist-python \
  --paths python \
  --hidden-import pikepdf \
  --hidden-import pytesseract \
  --hidden-import pdf2image \
  --hidden-import cv2 \
  --hidden-import scipy \
  --hidden-import numpy \
  --hidden-import PIL \
  --hidden-import pypdf \
  --hidden-import core.rpc_server \
  --hidden-import core.job_queue \
  --hidden-import core.config \
  --hidden-import handlers.ocr_handler \
  --hidden-import handlers.pdf_handler \
  --hidden-import handlers.system_handler \
  --hidden-import ocr.engine \
  --hidden-import ocr.confidence \
  --hidden-import ocr.layout \
  --hidden-import image.enhancer \
  --hidden-import image.upscaler \
  --hidden-import pdf.reader \
  --hidden-import pdf.writer \
  --hidden-import pdf.toc \
  --hidden-import pdf.page_numbering \
  --hidden-import pdf.splitter \
  python/main.py

echo ""
echo "Bundle complete: dist-python/guru-backend"
