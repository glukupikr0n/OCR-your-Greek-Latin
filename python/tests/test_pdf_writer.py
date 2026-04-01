"""Unit tests for PDFWriter."""

import os
import tempfile
import pytest

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pikepdf
    HAS_PIKEPDF = True
except ImportError:
    HAS_PIKEPDF = False

from ocr.engine import PageResult, WordResult
from pdf.writer import PDFWriter, PageDimensions
from pdf.toc import TOCEntry


def make_sample_pdf(path: str, num_pages: int = 1) -> None:
    """Create a minimal valid PDF for testing."""
    if not HAS_PIKEPDF:
        pytest.skip("pikepdf not installed")
    pdf = pikepdf.Pdf.new()
    for _ in range(num_pages):
        page = pikepdf.Dictionary(
            Type=pikepdf.Name('/Page'),
            MediaBox=pikepdf.Array([0, 0, 595, 842]),
        )
        pdf.pages.append(page)
    pdf.save(path)


def make_page_result(page_num: int = 0) -> PageResult:
    words = [
        WordResult(text='Αρχή', conf=85, left=50, top=50, width=60, height=20),
        WordResult(text='τοῦ', conf=88, left=120, top=50, width=30, height=20),
        WordResult(text='κατὰ', conf=90, left=160, top=50, width=40, height=20),
    ]
    return PageResult(
        page_num=page_num,
        words=words,
        plain_text='Αρχή τοῦ κατὰ',
        avg_confidence=87.6
    )


def make_page_dims() -> PageDimensions:
    return PageDimensions(
        width_pts=595.0,
        height_pts=842.0,
        width_px=2480,
        height_px=3508,
        dpi=300
    )


@pytest.mark.skipif(not HAS_PIKEPDF, reason="pikepdf not installed")
def test_write_searchable_produces_valid_pdf():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, 'source.pdf')
        out = os.path.join(tmpdir, 'output.pdf')

        make_sample_pdf(src)
        writer = PDFWriter(src, out)
        writer.write_searchable(
            [make_page_result()],
            [make_page_dims()]
        )

        assert os.path.exists(out)
        # Verify it's a valid PDF
        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) == 1


@pytest.mark.skipif(not HAS_PIKEPDF, reason="pikepdf not installed")
def test_write_searchable_multi_page():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, 'source.pdf')
        out = os.path.join(tmpdir, 'output.pdf')

        make_sample_pdf(src, num_pages=3)
        results = [make_page_result(i) for i in range(3)]
        dims = [make_page_dims() for _ in range(3)]

        writer = PDFWriter(src, out)
        writer.write_searchable(results, dims)

        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) == 3


@pytest.mark.skipif(not HAS_PIKEPDF, reason="pikepdf not installed")
def test_write_searchable_with_toc():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, 'source.pdf')
        out = os.path.join(tmpdir, 'output.pdf')

        make_sample_pdf(src, num_pages=2)
        toc = [
            TOCEntry('Book I', 0, 1, 'I'),
            TOCEntry('Chapter 1', 1, 2, '1'),
        ]
        writer = PDFWriter(src, out)
        writer.write_searchable(
            [make_page_result(i) for i in range(2)],
            [make_page_dims() for _ in range(2)],
            toc_entries=toc
        )

        # Should not raise
        with pikepdf.open(out) as pdf:
            assert len(pdf.pages) == 2
