"""Page number extraction: Roman and Arabic numeral support."""

from __future__ import annotations

import re

from ocr.engine import PageResult


# Roman numeral regex (handles upper and lower case)
_ROMAN_RE = re.compile(
    r'^(?=[MDCLXVImdclxvi])(M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$',
    re.IGNORECASE
)

# Arabic numeral (optionally with letter suffix: 23a, 4b)
_ARABIC_RE = re.compile(r'^(\d+)([a-z]?)$', re.IGNORECASE)

# Max words on a margin line to consider it a page number
_MAX_MARGIN_WORDS = 3

# Margin fraction: percentage of page height to consider as margin area
_MARGIN_FRACTION = 0.1


class PageNumberExtractor:
    def extract(self, page_results: list[PageResult]) -> dict[int, str]:
        """Return map: page_index (0-based) → display_number_string."""
        result: dict[int, str] = {}
        for page_result in page_results:
            num = self._find_page_number(page_result)
            if num:
                result[page_result.page_num] = num
        return result

    def _find_page_number(self, page_result: PageResult) -> str | None:
        if not page_result.words:
            return None

        # Get approximate image height from word coordinates
        all_tops = [w.top for w in page_result.words]
        all_bottoms = [w.top + w.height for w in page_result.words]
        if not all_tops:
            return None

        page_top = min(all_tops)
        page_bottom = max(all_bottoms)
        page_height = page_bottom - page_top
        if page_height <= 0:
            return None

        top_margin = page_top + page_height * _MARGIN_FRACTION
        bottom_margin = page_bottom - page_height * _MARGIN_FRACTION

        # Check top margin words
        top_words = [w for w in page_result.words if w.top <= top_margin]
        num = self._parse_number_from_words(top_words)
        if num:
            return num

        # Check bottom margin words
        bottom_words = [w for w in page_result.words if (w.top + w.height) >= bottom_margin]
        return self._parse_number_from_words(bottom_words)

    def _parse_number_from_words(self, words) -> str | None:
        if not words or len(words) > _MAX_MARGIN_WORDS:
            return None

        for word in words:
            text = word.text.strip().rstrip('.,;:')
            m_arabic = _ARABIC_RE.match(text)
            if m_arabic:
                return text

            m_roman = _ROMAN_RE.match(text)
            if m_roman and len(text) >= 2:
                return text.upper()

        return None

    @staticmethod
    def roman_to_int(s: str) -> int:
        roman_values = {
            'M': 1000, 'CM': 900, 'D': 500, 'CD': 400,
            'C': 100,  'XC': 90,  'L': 50,  'XL': 40,
            'X': 10,   'IX': 9,   'V': 5,   'IV': 4, 'I': 1
        }
        s = s.upper()
        result = 0
        i = 0
        while i < len(s):
            if i + 1 < len(s) and s[i:i+2] in roman_values:
                result += roman_values[s[i:i+2]]
                i += 2
            else:
                result += roman_values.get(s[i], 0)
                i += 1
        return result

    @staticmethod
    def int_to_roman(n: int) -> str:
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
        result = ''
        for v, s in zip(val, syms):
            while n >= v:
                result += s
                n -= v
        return result
