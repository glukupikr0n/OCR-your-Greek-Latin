#!/usr/bin/env bash
# setup.sh — 원라인 설치/빌드/업데이트 스크립트
# 사용법:
#   처음 설치: bash <(curl -fsSL https://raw.githubusercontent.com/glukupikr0n/OCR-your-Greek-Latin/main/setup.sh)
#   이미 클론:  bash setup.sh

set -euo pipefail

REPO="OCR-your-Greek-Latin"
REPO_URL="https://github.com/glukupikr0n/$REPO.git"

# ── 1. 저장소 준비 ────────────────────────────────────────────────────────────
if [ -f "package.json" ] && grep -q "ocr-your-greek-latin" package.json 2>/dev/null; then
  echo "==> 기존 저장소 감지 — 최신 코드 pull..."
  git pull
else
  echo "==> 저장소 클론 중..."
  git clone "$REPO_URL" 2>/dev/null || git -C "$REPO" pull
  cd "$REPO"
fi

# ── 2. OS별 설치 + 빌드 ───────────────────────────────────────────────────────
case "$(uname -s)" in
  Darwin)
    echo "==> macOS 감지"
    ./scripts/install-mac.sh && ./scripts/build-mac-app.sh
    ;;
  Linux)
    echo "==> Linux 감지"
    ./scripts/install-linux.sh
    echo "==> Linux 빌드 중..."
    npm run build:linux
    ;;
  *)
    echo "지원하지 않는 OS: $(uname -s)"
    exit 1
    ;;
esac
