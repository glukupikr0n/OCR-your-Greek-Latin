# Guru, Your Ancient OCR Master

<p align="center">
  <img src="assets/icon.png" width="120" alt="Guru icon">
</p>

---

스캔된 PDF 및 이미지를 완전히 검색 가능한 문서로 변환하는 데스크탑 OCR 앱입니다.  
고대 그리스어, 라틴어, 영어에 특화된 지원을 제공합니다.

A desktop OCR application for converting scanned PDFs and images into fully searchable documents, with specialized support for Ancient Greek, Latin, and English.

---

## 기능 / Features

| 기능 | Feature |
|---|---|
| 다국어 OCR | Multi-language OCR — Ancient Greek, Latin, English (동시 인식) |
| 검색 가능한 PDF | Searchable PDF — invisible text layer for copy/paste/search |
| 스마트 재시도 | Smart Confidence Retry — PSM 8/10으로 저신뢰도 단어 재처리 |
| 병렬 처리 | Parallel Processing — 최대 4스레드 동시 OCR |
| 레이아웃 감지 | Layout Intelligence — 단/복칸 자동 감지 |
| 이미지 전처리 | Image Enhancement — 2단계 기울기 보정, 노이즈 제거, 자동 대비 |
| 이중 언어 분리 | Bilingual PDF Splitting — 언어별 페이지 분리 |
| 페이지 번호 | Page Numbering — 로마/아라비아 숫자 인식 |
| 목차 감지 | Table of Contents — PDF 북마크 자동 생성 |
| 이미지 업스케일 | Image Upscaling — Lanczos 최대 4× |
| 커스텀 모델 훈련 | Custom Model Training — 사본 특화 Tesseract 파인튜닝 |

---

## 기술 스택 / Technology Stack

| 레이어 | 기술 |
|---|---|
| 프론트엔드 | Electron 33, JavaScript, HTML/CSS |
| 백엔드 | Python 3.10+ |
| OCR 엔진 | Tesseract (pytesseract) |
| PDF 처리 | pikepdf, pdf2image (Poppler) |
| 이미지 처리 | OpenCV, Pillow, NumPy |
| IPC | JSON-RPC 2.0 over stdin/stdout |
| 빌드 | electron-builder, npm |

---

## 프로젝트 구조 / Project Structure

```
src/               Electron 메인 프로세스, preload, renderer UI
python/            Python 백엔드
  core/            RPC 서버, job queue, 설정
  ocr/             Tesseract 래퍼, 레이아웃, 신뢰도 재시도, 훈련
  image/           이미지 전처리, 업스케일러
  pdf/             PDF 읽기/쓰기, TOC, 페이지 번호, 분리기
  handlers/        JSON-RPC 요청 핸들러
  tests/           Python 단위 테스트 (pytest)
assets/            앱 아이콘 (icon.png, icon.ico)
scripts/           install-mac.sh, build-icns.sh, generate-icon.py
tests/             JavaScript 테스트 (unit + e2e)
```

---

## 설치 / Installation

### macOS

```bash
./scripts/install-mac.sh
```

Homebrew, Tesseract, Poppler, Python 3.11, Node.js를 설치하고,  
tessdata_best에서 고대 그리스어(`grc`) / 라틴어(`lat`) 언어팩을 다운로드합니다.

### Linux (Debian/Ubuntu)

```bash
./scripts/install-linux.sh
```

---

## 개발 / Development

```bash
npm install
npm start           # 개발 모드로 실행 / Launch in development mode
```

---

## 빌드 / Build

```bash
npm run build:mac   # macOS DMG (x64 + arm64)
npm run build:linux # AppImage + deb
npm run build:win   # Windows NSIS installer
```

---

## 테스트 / Testing

```bash
# Python 단위 테스트 / Python unit tests
cd python && pytest tests/ -v

# JavaScript 단위 테스트 / JavaScript unit tests
npm test

# E2E 테스트 / End-to-end tests
npm run test:e2e
```

---

## Tesseract 언어 데이터 / Tesseract Language Data

설치 스크립트가 [tessdata_best](https://github.com/tesseract-ocr/tessdata_best)에서  
`grc.traineddata`와 `lat.traineddata`를 자동으로 다운로드합니다.

The installer automatically downloads `grc.traineddata` and `lat.traineddata` from [tessdata_best](https://github.com/tesseract-ocr/tessdata_best).

---

## 커스텀 모델 훈련 / Custom Model Training

메뉴의 **OCR → 커스텀 모델 훈련…** 을 통해 사본 특화 스크립트에 맞게  
Tesseract를 파인튜닝할 수 있습니다. `.box` 정정 파일이 포함된 ground truth 이미지를 제공하세요.

Use **OCR → Train Custom Model…** in the menu to fine-tune Tesseract for a specific manuscript style.

---

## 라이선스 / License

MIT
