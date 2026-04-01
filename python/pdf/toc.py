"""Table of Contents detection from OCR results."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ocr.engine import PageResult


@dataclass
class TOCEntry:
    title: str
    page_num: int       # 0-indexed PDF page
    level: int          # 1=chapter, 2=section, 3=subsection
    display_num: str    # "III", "4b", "12", etc.

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'page_num': self.page_num,
            'level': self.level,
            'display_num': self.display_num
        }


# Heading patterns ordered by level
_HEADING_PATTERNS: list[tuple[int, re.Pattern]] = [
    (1, re.compile(
        r'^(LIBER|CAPUT|CHAPTER|BOOK|PART|PARS)\s+([IVXLCDM]+|\d+)',
        re.IGNORECASE
    )),
    (1, re.compile(
        r'^(ΒΙΒΛΙΟΝ|ΒΙΒΛ\.?|ΚΕΦΑΛΑΙΟΝ|ΚΕΦ\.?)\s+',
        re.UNICODE
    )),
    (2, re.compile(
        r'^(SECTIO|SECTION|CAPITA|CAPUT)\s+([IVXLCDM]+|\d+)',
        re.IGNORECASE
    )),
    (2, re.compile(
        r'^([IVXLCDM]{2,})\s*[\.\:]',
        re.IGNORECASE
    )),
    (3, re.compile(
        r'^(\d+[\.\):])\s+\S',
    )),
]


class TOCDetector:
    def detect(self, page_results: list[PageResult]) -> list[TOCEntry]:
        entries: list[TOCEntry] = []

        for page_result in page_results:
            lines = page_result.plain_text.splitlines()
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                entry = self._match_heading(line, page_result.page_num)
                if entry:
                    entries.append(entry)

        return entries

    def _match_heading(self, line: str, page_num: int) -> TOCEntry | None:
        for level, pattern in _HEADING_PATTERNS:
            m = pattern.match(line)
            if m:
                # Extract number from match if present
                display_num = m.group(2) if m.lastindex and m.lastindex >= 2 else ''
                return TOCEntry(
                    title=line[:80],
                    page_num=page_num,
                    level=level,
                    display_num=display_num
                )
        return None
