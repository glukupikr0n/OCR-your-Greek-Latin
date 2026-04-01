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

        # Build the invisible text content stream
        content = self._build_text_stream(page_result.words, dims)

        # Create a new content stream object
        text_stream = pikepdf.Stream(page.obj.objgen[0]._pdf if hasattr(page.obj.objgen[0], '_pdf') else None, content)
        # Use a fresh approach: encode and embed
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

    def _build_text_stream(self, words: list[WordResult], dims: PageDimensions) -> bytes:
        """Build PDF content stream bytes for an invisible text overlay."""
        lines = []
        lines.append(b'q')          # save graphics state
        lines.append(b'BT')         # begin text
        lines.append(b'/F1 8 Tf')   # font (invisible at size 0 causes issues; use 8pt)
        lines.append(b'3 Tr')       # invisible text rendering mode

        for word in words:
            if not word.text.strip():
                continue

            # Convert pixel coordinates to PDF points
            # PDF origin is bottom-left; pixel origin is top-left
            x_pt = word.left * dims.px_to_pt_x
            y_pt = dims.height_pts - (word.top + word.height) * dims.px_to_pt_y

            # Scale font to match word height (approximate)
            font_size = max(1.0, word.height * dims.px_to_pt_y)

            x_pt = round(x_pt, 2)
            y_pt = round(y_pt, 2)
            font_size = round(font_size, 2)

            # Set font size per word for accuracy
            lines.append(f'/F1 {font_size} Tf'.encode())
            lines.append(f'{x_pt} {y_pt} Td'.encode())

            # Encode text as PDF string
            escaped = self._pdf_escape(word.text)
            lines.append(f'({escaped}) Tj'.encode())

            # Reset position to absolute (use Tm matrix next word)
            # Actually use absolute positioning via Tm
            lines[-3] = f'/F1 {font_size} Tf'.encode()  # already set
            # Replace last Td with absolute Tm
            del lines[-2]
            lines.append(f'{font_size} 0 0 {font_size} {x_pt} {y_pt} Tm'.encode())
            lines.append(f'({escaped}) Tj'.encode())
            del lines[-3]  # remove duplicate Tj

        lines.append(b'ET')  # end text
        lines.append(b'Q')   # restore graphics state

        return b'\n'.join(lines) + b'\n'

    def _ensure_font(self, page: pikepdf.Page) -> None:
        """Add a standard font reference to page resources if missing."""
        if '/Resources' not in page.obj:
            page.obj['/Resources'] = Dictionary()

        resources = page.obj['/Resources']
        if '/Font' not in resources:
            resources['/Font'] = Dictionary()

        fonts = resources['/Font']
        if '/F1' not in fonts:
            # Use Helvetica (always available in PDF)
            fonts['/F1'] = Dictionary(
                Type=Name('/Font'),
                Subtype=Name('/Type1'),
                BaseFont=Name('/Helvetica'),
                Encoding=Name('/WinAnsiEncoding')
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
        """Escape special PDF string characters."""
        return (
            text
            .replace('\\', '\\\\')
            .replace('(', '\\(')
            .replace(')', '\\)')
            .replace('\n', '\\n')
            .replace('\r', '\\r')
        )
