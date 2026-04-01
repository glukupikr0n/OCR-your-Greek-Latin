"""Bilingual PDF splitter: separates alternating-language pages."""

from __future__ import annotations

import os

import pikepdf

from ocr.engine import PageResult


class BilingualSplitter:
    def split(
        self,
        pdf_path: str,
        output_dir: str,
        lang_a_pages: list[int],
        lang_b_pages: list[int],
        lang_a_name: str = 'greek',
        lang_b_name: str = 'latin'
    ) -> tuple[str, str]:
        """
        Split a PDF into two files based on page indices.
        Returns (path_lang_a, path_lang_b).
        """
        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(pdf_path))[0]
        out_a = os.path.join(output_dir, f'{base}_{lang_a_name}.pdf')
        out_b = os.path.join(output_dir, f'{base}_{lang_b_name}.pdf')

        self._extract_pages(pdf_path, lang_a_pages, out_a)
        self._extract_pages(pdf_path, lang_b_pages, out_b)

        return out_a, out_b

    def detect_alternating_languages(
        self,
        page_results: list[PageResult]
    ) -> tuple[list[int], list[int]]:
        """
        Classify each page as belonging to one of two languages
        based on dominant language detection.
        Returns (lang_a_indices, lang_b_indices).
        """
        lang_counts: dict[str, list[int]] = {}

        for pr in page_results:
            lang = self._detect_dominant_language(pr)
            if lang not in lang_counts:
                lang_counts[lang] = []
            lang_counts[lang].append(pr.page_num)

        # Sort languages by frequency; the two most common are lang_a and lang_b
        sorted_langs = sorted(lang_counts.items(), key=lambda x: len(x[1]), reverse=True)

        if len(sorted_langs) == 0:
            return [], []
        if len(sorted_langs) == 1:
            return sorted_langs[0][1], []

        lang_a_pages = sorted_langs[0][1]
        lang_b_pages = sorted_langs[1][1]

        return sorted(lang_a_pages), sorted(lang_b_pages)

    def _detect_dominant_language(self, page_result: PageResult) -> str:
        """
        Heuristic: detect whether the page is primarily Greek, Latin, or English
        by looking at character sets.
        """
        text = page_result.plain_text
        if not text:
            return 'eng'

        greek_chars = sum(1 for c in text if '\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF')
        latin_chars = sum(1 for c in text if c.isalpha() and ord(c) < 256)

        if greek_chars > latin_chars * 0.3:
            return 'grc'
        return 'lat'

    @staticmethod
    def _extract_pages(pdf_path: str, page_indices: list[int], output_path: str) -> None:
        if not page_indices:
            return
        with pikepdf.open(pdf_path) as src:
            dst = pikepdf.Pdf.new()
            for idx in sorted(page_indices):
                if 0 <= idx < len(src.pages):
                    dst.pages.append(src.pages[idx])
            dst.save(output_path)
