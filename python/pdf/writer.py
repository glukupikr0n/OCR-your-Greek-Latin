"""
Searchable PDF writer.
Injects an invisible text layer over each page using pikepdf,
preserving the original visible content.
"""

from __future__ import annotations

import io
import struct
from dataclasses import dataclass

import pikepdf
from pikepdf import Array, Dictionary, Name, String, Pdf

from ocr.engine import PageResult, WordResult
from pdf.toc import TOCEntry


# PDF points per inch
PTS_PER_INCH = 72.0


@dataclass
class PageDimensions:
    width_pts: float
    height_pts: float
    width_px: int
    height_px: int
    dpi: int

    @property
    def px_to_pt_x(self) -> float:
        return self.width_pts / self.width_px

    @property
    def px_to_pt_y(self) -> float:
        return self.height_pts / self.height_px


class PDFWriter:
    def __init__(self, source_pdf_path: str, output_path: str):
        self._source_path = source_pdf_path
        self._output_path = output_path

    def write_searchable(
        self,
        page_results: list[PageResult],
        page_dimensions: list[PageDimensions],
        toc_entries: list[TOCEntry] | None = None,
        page_number_map: dict[int, str] | None = None
    ) -> None:
        with pikepdf.open(self._source_path) as pdf:
            for i, (page_result, dims) in enumerate(zip(page_results, page_dimensions)):
                if i < len(pdf.pages):
                    self._inject_text_layer(pdf.pages[i], page_result, dims)

            if toc_entries:
                self._inject_toc(pdf, toc_entries)

            pdf.save(self._output_path)

    def _inject_text_layer(
        self,
        page: pikepdf.Page,
        page_result: PageResult,
        dims: PageDimensions
    ) -> None:
        if not page_result.words:
            return

        # Build the invisible text content stream (line-level)
        content = self._build_text_stream(page_result.words, dims)
        text_obj = pikepdf.Stream(page.obj.owner, content)

        # Get existing content stream(s) and append our overlay
        existing = page.obj.get('/Contents')
        if existing is None:
            page.obj['/Contents'] = text_obj
        elif isinstance(existing, pikepdf.Array):
            existing.append(text_obj)
            page.obj['/Contents'] = existing
        else:
            page.obj['/Contents'] = pikepdf.Array([existing, text_obj])

        # Ensure /Resources has a font (invisible, but required for text ops)
        self._ensure_font(page)

    def _group_words_into_lines(self, words: list[WordResult]) -> list[list[WordResult]]:
        """Group words into lines by vertical proximity."""
        if not words:
            return []
        sorted_words = sorted(words, key=lambda w: w.top)

        lines: list[list[WordResult]] = []
        current: list[WordResult] = [sorted_words[0]]
        line_top = sorted_words[0].top
        line_height = max(sorted_words[0].height, 1)

        for word in sorted_words[1:]:
            if abs(word.top - line_top) < line_height * 0.6:
                current.append(word)
                line_height = max(line_height, word.height)
            else:
                lines.append(current)
                current = [word]
                line_top = word.top
                line_height = max(word.height, 1)

        if current:
            lines.append(current)
        return lines

    def _build_text_stream(self, words: list[WordResult], dims: PageDimensions) -> bytes:
        """Build PDF content stream with one text element per line."""
        stream: list[bytes] = [b'q', b'BT', b'3 Tr']  # invisible rendering mode

        for line_words in self._group_words_into_lines(words):
            # Sort left-to-right within the line
            line_words.sort(key=lambda w: w.left)

            x0 = min(w.left for w in line_words)
            y0 = min(w.top for w in line_words)
            line_h = max((w.height for w in line_words), default=12)

            # Convert pixel coords to PDF points (origin: bottom-left)
            x_pt = round(x0 * dims.px_to_pt_x, 2)
            y_pt = round(dims.height_pts - (y0 + line_h) * dims.px_to_pt_y, 2)
            font_size = round(max(1.0, line_h * dims.px_to_pt_y), 2)

            text = ' '.join(w.text for w in line_words if w.text.strip())
            if not text:
                continue

            escaped = self._pdf_escape(text)
            stream.append(f'/F1 {font_size} Tf'.encode())
            stream.append(f'{font_size} 0 0 {font_size} {x_pt} {y_pt} Tm'.encode())
            stream.append(f'<{escaped}> Tj'.encode())

        stream.extend([b'ET', b'Q'])
        return b'\n'.join(stream) + b'\n'

    def _ensure_font(self, page: pikepdf.Page) -> None:
        """Add a Unicode-capable composite font reference to page resources."""
        if '/Resources' not in page.obj:
            page.obj['/Resources'] = Dictionary()

        resources = page.obj['/Resources']
        if '/Font' not in resources:
            resources['/Font'] = Dictionary()

        fonts = resources['/Font']
        if '/F1' not in fonts:
            # Type0 composite font with Identity-H encoding supports full Unicode
            # (including Greek U+0370–U+03FF, polytonic U+1F00–U+1FFF)
            cid_font = Dictionary(
                Type=Name('/Font'),
                Subtype=Name('/CIDFontType2'),
                BaseFont=Name('/Helvetica'),
                CIDSystemInfo=Dictionary(
                    Registry=String('Adobe'),
                    Ordering=String('Identity'),
                    Supplement=0
                ),
                DW=1000
            )
            fonts['/F1'] = Dictionary(
                Type=Name('/Font'),
                Subtype=Name('/Type0'),
                BaseFont=Name('/Helvetica'),
                Encoding=Name('/Identity-H'),
                DescendantFonts=Array([cid_font])
            )

    def _inject_toc(self, pdf: Pdf, entries: list[TOCEntry]) -> None:
        """Write TOC entries as PDF outline (bookmarks)."""
        if not entries:
            return

        with pdf.open_outline() as outline:
            stack: list[tuple[int, pikepdf.OutlineItem]] = []
            for entry in entries:
                item = pikepdf.OutlineItem(
                    entry.title,
                    entry.page_num,
                    'XYZ',
                    0, None, None
                )
                # Find parent based on level
                while stack and stack[-1][0] >= entry.level:
                    stack.pop()

                if not stack:
                    outline.root.append(item)
                else:
                    stack[-1][1].children.append(item)

                stack.append((entry.level, item))

    @staticmethod
    def _pdf_escape(text: str) -> str:
        """Encode text as UTF-16BE hex string for Type0/Identity-H font.
        Supports full Unicode including Greek and polytonic characters."""
        return 'FEFF' + text.encode('utf-16-be').hex().upper()
