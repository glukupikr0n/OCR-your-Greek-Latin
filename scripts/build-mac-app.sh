#!/bin/bash
# Complete macOS .app build: icons → Python bundle → Electron packaging
# Usage: ./scripts/build-mac-app.sh
# Output: dist/mac/OCR Your Greek Latin.app  (or dist/mac-arm64/ on Apple Silicon)

set -e
cd "$(dirname "$0")/.."

echo "=== Step 1: Generate app icons ==="
if [ ! -f assets/icon.icns ]; then
  echo "Building icon.icns..."
  ./scripts/build-icns.sh
else
  echo "icon.icns already exists, skipping."
fi

echo ""
echo "=== Step 2: Bundle Python backend ==="
./scripts/bundle-python.sh

echo ""
echo "=== Step 3: Install npm dependencies ==="
npm install --silent

echo ""
echo "=== Step 4: Package Electron .app ==="
npm run build:mac:app

echo ""
echo "Build complete!"
ls -lh dist/mac*/*.app 2>/dev/null || ls -lh dist/*.app 2>/dev/null || echo "Check dist/ folder for output."
