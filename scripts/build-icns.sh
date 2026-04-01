#!/usr/bin/env bash
# build-icns.sh — Convert assets/icon.png to assets/icon.icns using macOS tools
# Requires: sips, iconutil (bundled with macOS)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_DIR="$SCRIPT_DIR/../assets"
SRC="$ASSETS_DIR/icon.png"
ICONSET="$ASSETS_DIR/icon.iconset"
DEST="$ASSETS_DIR/icon.icns"

if [[ ! -f "$SRC" ]]; then
  echo "Error: $SRC not found." >&2
  exit 1
fi

if ! command -v sips &>/dev/null || ! command -v iconutil &>/dev/null; then
  echo "Error: sips/iconutil not available. This script requires macOS." >&2
  exit 1
fi

mkdir -p "$ICONSET"

# Generate all required sizes
sizes=(16 32 64 128 256 512)
for SIZE in "${sizes[@]}"; do
  sips -z "$SIZE" "$SIZE" "$SRC" --out "$ICONSET/icon_${SIZE}x${SIZE}.png" &>/dev/null
  DOUBLE=$((SIZE * 2))
  sips -z "$DOUBLE" "$DOUBLE" "$SRC" --out "$ICONSET/icon_${SIZE}x${SIZE}@2x.png" &>/dev/null
done

iconutil -c icns "$ICONSET" -o "$DEST"
rm -rf "$ICONSET"

echo "Built $DEST"
