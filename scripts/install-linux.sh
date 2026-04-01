#!/usr/bin/env bash
# install-linux.sh — Setup for OCR Your Greek Latin on Linux (Debian/Ubuntu)

set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$APP_DIR/python/.venv"

echo "==> OCR Your Greek Latin — Linux Setup"

# ── 1. System dependencies ───────────────────────────────────────────────────
echo "==> Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y \
  tesseract-ocr \
  tesseract-ocr-grc \
  tesseract-ocr-lat \
  tesseract-ocr-eng \
  poppler-utils \
  python3.11 \
  python3.11-venv \
  python3-pip \
  nodejs \
  npm \
  libopencv-dev

# ── 2. Python virtual environment ────────────────────────────────────────────
echo "==> Setting up Python virtual environment..."
python3.11 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet
pip install -r "$APP_DIR/python/requirements.txt" --quiet
deactivate

# ── 3. Node.js dependencies ──────────────────────────────────────────────────
echo "==> Installing Node.js dependencies..."
cd "$APP_DIR"
npm install --silent

echo ""
echo "✓ Installation complete!"
echo "  Run: npm start"
