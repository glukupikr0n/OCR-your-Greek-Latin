'use strict'

export const STRINGS = {
  ko: {
    // 파일 영역
    'drop-hint': 'PDF 또는 이미지를 여기에 드래그하세요',
    'drop-hint-sub': '또는',
    'open-file': '파일 열기…',
    'pages-unit': '페이지',

    // 섹션 헤더
    'sec-languages': '인식 언어',
    'sec-enhancement': '이미지 전처리',
    'sec-ocr': 'OCR 옵션',

    // 언어 체크박스
    'lang-grc': '고대 그리스어',
    'lang-lat': '라틴어',
    'lang-eng': '영어',

    // 이미지 전처리
    'opt-deskew': '기울기 보정 (2단계)',
    'opt-deskew-sub': '최대 각도 (°)',
    'opt-grayscale': '그레이스케일 변환',
    'opt-bw': '흑백 변환 (B&W)',
    'opt-denoise': '노이즈 제거',
    'opt-denoise-sub': '강도',
    'opt-autocontrast': '자동 대비',
    'opt-upscale': '이미지 업스케일',
    'opt-upscale-sub': '배율',
    'upscale-none': '없음 (1×)',

    // 존 / 레이아웃
    'sec-zones': '레이아웃 존',
    'opt-zone-preset': '존 프리셋',
    'zone-auto': '자동 감지',
    'zone-full': '전체 페이지',
    'zone-body': '본문만',
    'zone-left-margin': '왼쪽 여백',
    'zone-right-margin': '오른쪽 여백',
    'zone-both-margins': '양쪽 여백',
    'zone-auto-detect': '블록 자동 감지',
    'opt-custom-margins': '여백 설정',
    'margin-top': '위 %',
    'margin-bottom': '아래',
    'margin-left': '왼쪽',
    'margin-right': '오른쪽',
    'opt-custom-zones': '커스텀 존 편집',
    'btn-clear-zones': '초기화',

    // OCR 옵션
    'sec-ocr': 'OCR 옵션',
    'opt-layout': '레이아웃 감지 (단/복칸)',
    'opt-confidence-retry': '스마트 재시도',
    'opt-confidence-sub': '신뢰도 임계값 (%)',
    'opt-toc': '목차 자동 감지',
    'opt-page-numbers': '페이지 번호 추출',
    'opt-split-bilingual': '이중 언어 PDF 분리',
    'opt-split-lang-a': '언어 A',
    'opt-split-lang-b': '언어 B',
    'opt-split-shared': '공유 범위',
    'opt-page-range': '처리 페이지 범위',
    'opt-page-range-from': '시작',
    'opt-threads': '처리 스레드 수',

    // 버튼
    'btn-process': '파일 처리',
    'btn-cancel': '취소',
    'btn-open-output': '출력 PDF 열기',
    'btn-download-data': '데이터 다운로드…',

    // 데이터 다운로드
    'data-dialog-title': 'OCR 데이터 다운로드',
    'data-dialog-desc': 'tessdata_best 및 검증된 그리스어/라틴어 코퍼스를 다운로드합니다.',
    'data-tessdata-label': 'Tesseract 언어 데이터',
    'data-corpus-label': '코퍼스 (참고용)',
    'data-start-btn': '다운로드 시작',
    'data-close-btn': '닫기',

    // 수동 목차
    'manual-toc-title': '수동 목차 항목',
    'toc-level-chapter': '챕터',
    'toc-level-section': '섹션',
    'toc-level-subsection': '소섹션',
    'toc-add-btn': '+',

    // 결과
    'result-title': '처리 결과',
    'stat-pages': '처리된 페이지',
    'stat-confidence': '평균 신뢰도',
    'stat-output': '저장 경로',
    'toc-title': '목차',
    'log-title': '로그',

    // 미리보기
    'preview-placeholder': 'PDF를 열면 미리보기가 표시됩니다',
    'page-indicator': '페이지',

    // 시스템
    'system-missing-langs': '누락된 Tesseract 언어팩: {langs}. install-mac.sh를 실행하세요.',
    'system-backend-error': '백엔드 오류: {msg}',

    // 업데이트
    'update-available': '새 버전 {ver}이 있습니다.',
    'update-downloading': '업데이트 다운로드 중… {pct}%',
    'update-ready': '업데이트 준비 완료. 지금 재시작할까요?',
    'update-btn-restart': '재시작하여 업데이트',
    'update-btn-later': '나중에',
    'update-none': '최신 버전입니다.',

    // 언어 토글
    'lang-toggle': 'EN',
  },

  en: {
    'drop-hint': 'Drop a PDF or image here',
    'drop-hint-sub': 'or',
    'open-file': 'Open File…',
    'pages-unit': 'pages',

    'sec-languages': 'Languages',
    'sec-enhancement': 'Image Enhancement',
    'sec-ocr': 'OCR Options',

    'lang-grc': 'Ancient Greek',
    'lang-lat': 'Latin',
    'lang-eng': 'English',

    'opt-deskew': 'Deskew (2-pass)',
    'opt-deskew-sub': 'Max angle (°)',
    'opt-grayscale': 'Grayscale',
    'opt-bw': 'Convert to B&W',
    'opt-denoise': 'Denoise',
    'opt-denoise-sub': 'Strength',
    'opt-autocontrast': 'Auto Contrast',
    'opt-upscale': 'Image Upscale',
    'opt-upscale-sub': 'Factor',
    'upscale-none': 'None (1×)',

    'opt-layout': 'Layout detection (columns)',
    'opt-confidence-retry': 'Smart confidence retry',
    'opt-confidence-sub': 'Confidence threshold (%)',
    'opt-toc': 'Detect Table of Contents',
    'opt-page-numbers': 'Extract page numbers',
    // Zones
    'sec-zones': 'Layout Zones',
    'opt-zone-preset': 'Zone preset',
    'zone-auto': 'Auto',
    'zone-full': 'Full Page',
    'zone-body': 'Body Only',
    'zone-left-margin': 'Left Margin',
    'zone-right-margin': 'Right Margin',
    'zone-both-margins': 'Both Margins',
    'zone-auto-detect': 'Auto-detect blocks',
    'opt-custom-margins': 'Margin settings',
    'margin-top': 'Top %',
    'margin-bottom': 'Bottom',
    'margin-left': 'Left',
    'margin-right': 'Right',
    'opt-custom-zones': 'Custom zone editor',
    'btn-clear-zones': 'Clear',

    'opt-split-bilingual': 'Split bilingual PDF',
    'opt-split-lang-a': 'Lang A',
    'opt-split-lang-b': 'Lang B',
    'opt-split-shared': 'Shared range',
    'opt-page-range': 'OCR page range',
    'opt-page-range-from': 'From',
    'opt-threads': 'Processing threads',

    'btn-process': 'Process File',
    'btn-cancel': 'Cancel',
    'btn-open-output': 'Open Output PDF',
    'btn-download-data': 'Download Data…',

    'data-dialog-title': 'Download OCR Data',
    'data-dialog-desc': 'Download tessdata_best models and verified Greek/Latin corpora.',
    'data-tessdata-label': 'Tesseract Language Data',
    'data-corpus-label': 'Corpus (reference)',
    'data-start-btn': 'Start Download',
    'data-close-btn': 'Close',

    'manual-toc-title': 'Manual TOC Entries',
    'toc-level-chapter': 'Chapter',
    'toc-level-section': 'Section',
    'toc-level-subsection': 'Subsection',
    'toc-add-btn': '+',

    'result-title': 'Results',
    'stat-pages': 'Pages processed',
    'stat-confidence': 'Avg. confidence',
    'stat-output': 'Output path',
    'toc-title': 'Table of Contents',
    'log-title': 'Log',

    'preview-placeholder': 'Open a PDF to see a preview',
    'page-indicator': 'Page',

    'system-missing-langs': 'Missing Tesseract language data: {langs}. Run install-mac.sh.',
    'system-backend-error': 'Backend error: {msg}',

    'update-available': 'New version {ver} is available.',
    'update-downloading': 'Downloading update… {pct}%',
    'update-ready': 'Update ready. Restart now?',
    'update-btn-restart': 'Restart & Update',
    'update-btn-later': 'Later',
    'update-none': 'You are up to date.',

    'lang-toggle': '한국어',
  }
}

let _lang = 'ko'

export function setLang (lang) { _lang = lang }
export function getLang () { return _lang }

export function t (key, vars = {}) {
  let str = STRINGS[_lang][key] ?? STRINGS.en[key] ?? key
  for (const [k, v] of Object.entries(vars)) {
    str = str.replace(`{${k}}`, v)
  }
  return str
}

export function applyI18n () {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n
    el.textContent = t(key)
  })
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPlaceholder)
  })
}
