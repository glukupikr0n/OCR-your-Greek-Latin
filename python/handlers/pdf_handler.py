"""PDF-specific handlers: preview and bilingual split."""

from __future__ import annotations

import os

from core.config import AppConfig
from pdf.reader import PDFReader
from pdf.splitter import BilingualSplitter


class PDFHandler:
    def __init__(self, config: AppConfig):
        self._config = config

    def preview(self, params: dict) -> dict:
        """Render a single page as base64 PNG for the UI preview."""
        pdf_path = params['path']
        page_num = params.get('page', 0)
        dpi = params.get('dpi', self._config.preview_dpi)

        reader = PDFReader(pdf_path)
        total = reader.page_count()
        b64_png = reader.render_page_preview(page_num, dpi=dpi)

        return {
            'page': page_num,
            'total_pages': total,
            'image': b64_png,
            'format': 'png'
        }

    def split(self, params: dict) -> dict:
        """Split a PDF into two language-specific files."""
        pdf_path = params['pdf_path']
        output_dir = params.get('output_dir', os.path.dirname(pdf_path))
        lang_a_pages = params.get('lang_a_pages', [])
        lang_b_pages = params.get('lang_b_pages', [])
        lang_a_name = params.get('lang_a_name', 'greek')
        lang_b_name = params.get('lang_b_name', 'latin')

        splitter = BilingualSplitter()
        path_a, path_b = splitter.split(
            pdf_path, output_dir, lang_a_pages, lang_b_pages,
            lang_a_name, lang_b_name
        )
        return {
            'lang_a_path': path_a,
            'lang_b_path': path_b
        }
