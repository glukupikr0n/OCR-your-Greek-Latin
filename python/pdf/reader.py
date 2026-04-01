"""PDF reader using pdf2image (Poppler backend)."""

from __future__ import annotations

import base64
import io
import os

from PIL import Image
from pdf2image import convert_from_path
import pikepdf


class PDFReader:
    def __init__(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f'PDF not found: {pdf_path}')
        self._path = pdf_path
        self._page_count: int | None = None

    def page_count(self) -> int:
        if self._page_count is None:
            with pikepdf.open(self._path) as pdf:
                self._page_count = len(pdf.pages)
        return self._page_count

    def render_page(self, page_num: int, dpi: int = 300) -> Image.Image:
        """Render a single page to a PIL Image (page_num is 0-indexed)."""
        pages = convert_from_path(
            self._path,
            dpi=dpi,
            first_page=page_num + 1,
            last_page=page_num + 1
        )
        if not pages:
            raise ValueError(f'Could not render page {page_num}')
        return pages[0]

    def render_page_preview(self, page_num: int, dpi: int = 72) -> str:
        """Render page at low resolution, return as base64 PNG string."""
        img = self.render_page(page_num, dpi=dpi)
        buf = io.BytesIO()
        img.save(buf, format='PNG', optimize=True)
        return base64.b64encode(buf.getvalue()).decode('ascii')

    def render_all_pages(self, dpi: int = 300) -> list[Image.Image]:
        """Render all pages at once (memory-intensive for large PDFs)."""
        return convert_from_path(self._path, dpi=dpi)
