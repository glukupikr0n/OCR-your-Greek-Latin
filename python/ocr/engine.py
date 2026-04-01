"""Tesseract OCR engine wrapper with multi-language support."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable

import pytesseract
from PIL import Image


@dataclass
class WordResult:
    text: str
    conf: float
    left: int
    top: int
    width: int
    height: int


@dataclass
class PageResult:
    page_num: int
    words: list[WordResult] = field(default_factory=list)
    plain_text: str = ''
    avg_confidence: float = 0.0
    dominant_language: str = 'eng'

    def to_dict(self) -> dict:
        return {
            'page_num': self.page_num,
            'plain_text': self.plain_text,
            'avg_confidence': self.avg_confidence,
            'dominant_language': self.dominant_language,
            'word_count': len(self.words)
        }


class OCREngine:
    def __init__(self, languages: list[str], tesseract_cmd: str = 'tesseract', tessdata_dir: str = ''):
        self._languages = languages
        self._lang_str = '+'.join(languages)

        if tesseract_cmd and tesseract_cmd != 'tesseract':
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        if tessdata_dir:
            os.environ['TESSDATA_PREFIX'] = tessdata_dir

    def process_page(
        self,
        image: Image.Image,
        page_num: int,
        progress_cb: Callable[[int, float], None] | None = None
    ) -> PageResult:
        """Run OCR on a single page image and return word-level results."""
        data = self._run_tesseract(image, self._lang_str, psm=3, oem=1)
        result = self._build_page_result(data, page_num)

        if progress_cb:
            progress_cb(page_num, result.avg_confidence)

        return result

    def _run_tesseract(
        self,
        image: Image.Image,
        lang_str: str,
        psm: int = 3,
        oem: int = 1
    ) -> dict:
        config = f'--psm {psm} --oem {oem}'
        data = pytesseract.image_to_data(
            image,
            lang=lang_str,
            config=config,
            output_type=pytesseract.Output.DICT
        )
        return data

    def run_on_region(
        self,
        image: Image.Image,
        psm: int = 8,
        oem: int = 1
    ) -> dict:
        """Run Tesseract on a cropped region (used by confidence retry)."""
        config = f'--psm {psm} --oem {oem}'
        return pytesseract.image_to_data(
            image,
            lang=self._lang_str,
            config=config,
            output_type=pytesseract.Output.DICT
        )

    def _build_page_result(self, data: dict, page_num: int) -> PageResult:
        words: list[WordResult] = []
        confidences: list[float] = []

        n = len(data['text'])
        for i in range(n):
            text = data['text'][i].strip()
            conf = float(data['conf'][i])
            if not text or conf < 0:
                continue

            words.append(WordResult(
                text=text,
                conf=conf,
                left=data['left'][i],
                top=data['top'][i],
                width=data['width'][i],
                height=data['height'][i]
            ))
            confidences.append(conf)

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        plain_text = ' '.join(w.text for w in words)

        return PageResult(
            page_num=page_num,
            words=words,
            plain_text=plain_text,
            avg_confidence=round(avg_conf, 2)
        )
