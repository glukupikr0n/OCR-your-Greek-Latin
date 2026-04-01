#!/usr/bin/env bash
# install-mac.sh — One-line macOS setup for OCR Your Greek Latin
# Usage: ./scripts/install-mac.sh

set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$APP_DIR/python/.venv"

echo "==> OCR Your Greek Latin — macOS Setup"
echo "    App directory: $APP_DIR"
echo ""

# ── 1. Homebrew ──────────────────────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
  echo "==> Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Add brew to PATH for Apple Silicon
  if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
fi

# ── 2. System dependencies ───────────────────────────────────────────────────
echo "==> Installing system dependencies via Homebrew..."
brew install tesseract poppler python@3.11 node || true

# Check for tesseract-lang (optional, has grc/lat)
brew install tesseract-lang 2>/dev/null || true

# ── 3. Tesseract language data (grc, lat) ────────────────────────────────────
TESSDATA_DIR="$(brew --prefix)/share/tessdata"
if [[ ! -d "$TESSDATA_DIR" ]]; then
  mkdir -p "$TESSDATA_DIR"
fi

for LANG in grc lat; do
  if [[ ! -f "$TESSDATA_DIR/$LANG.traineddata" ]]; then
    echo "==> Downloading $LANG.traineddata (tessdata_best)..."
    curl -fsSL \
      "https://github.com/tesseract-ocr/tessdata_best/raw/main/$LANG.traineddata" \
      -o "$TESSDATA_DIR/$LANG.traineddata"
    echo "    Saved to $TESSDATA_DIR/$LANG.traineddata"
  else
    echo "==> $LANG.traineddata already present, skipping."
  fi
done

# ── 4. Python virtual environment ────────────────────────────────────────────
echo "==> Setting up Python virtual environment..."
PYTHON_BIN="$(brew --prefix)/bin/python3.11"
if [[ ! -f "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python3"
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet
pip install -r "$APP_DIR/python/requirements.txt" --quiet
deactivate
echo "    Virtual environment ready: $VENV_DIR"

# ── 5. Node.js dependencies ──────────────────────────────────────────────────
echo "==> Installing Node.js dependencies..."
cd "$APP_DIR"
npm install --silent

# ── 6. Build ICNS icon ───────────────────────────────────────────────────────
echo "==> Building app icon..."
if [[ -f "$APP_DIR/assets/icon.png" ]]; then
  bash "$APP_DIR/scripts/build-icns.sh"
else
  echo "    Warning: assets/icon.png not found. Run scripts/download-assets.sh first."
fi

echo ""
echo "✓ Installation complete!"
echo ""
echo "  To run in development mode:"
echo "    npm start"
echo ""
echo "  To build a macOS DMG:"
echo "    npm run build:mac"
