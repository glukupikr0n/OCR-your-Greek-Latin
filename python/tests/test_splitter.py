"""Unit tests for BilingualSplitter."""

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

from ocr.engine import PageResult
from pdf.splitter import BilingualSplitter


def make_page(page_num, text, avg_conf=80.0):
    return PageResult(
        page_num=page_num,
        words=[],
        plain_text=text,
        avg_confidence=avg_conf
    )


def make_sample_pdf(path, num_pages=4):
    if not HAS_PIKEPDF:
        pytest.skip("pikepdf not installed")
    pdf = pikepdf.Pdf.new()
    for _ in range(num_pages):
        page = pikepdf.Dictionary(
            Type=pikepdf.Name('/Page'),
            MediaBox=pikepdf.Array([0, 0, 595, 842])
        )
        pdf.pages.append(page)
    pdf.save(path)


def test_detect_alternating_languages_greek_latin():
    splitter = BilingualSplitter()
    # Pages with Greek characters
    greek_text = "Ἐν ἀρχῇ ἦν ὁ λόγος καὶ ὁ λόγος ἦν πρὸς τὸν θεόν"
    latin_text = "In principio erat Verbum et Verbum erat apud Deum"

    pages = [
        make_page(0, greek_text),
        make_page(1, latin_text),
        make_page(2, greek_text),
        make_page(3, latin_text),
    ]

    lang_a, lang_b = splitter.detect_alternating_languages(pages)

    assert len(lang_a) == 2
    assert len(lang_b) == 2
    assert 0 in lang_a or 0 in lang_b  # page 0 classified somewhere


def test_detect_all_same_language():
    splitter = BilingualSplitter()
    latin_text = "Lorem ipsum dolor sit amet consectetur"
    pages = [make_page(i, latin_text) for i in range(4)]

    lang_a, lang_b = splitter.detect_alternating_languages(pages)
    # All pages go to lang_a (most common), lang_b is empty
    assert len(lang_a) + len(lang_b) == 4


@pytest.mark.skipif(not HAS_PIKEPDF, reason="pikepdf not installed")
def test_split_produces_two_output_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        src = os.path.join(tmpdir, 'bilingual.pdf')
        make_sample_pdf(src, num_pages=4)

        splitter = BilingualSplitter()
        path_a, path_b = splitter.split(
            src, tmpdir,
            lang_a_pages=[0, 2],
            lang_b_pages=[1, 3],
            lang_a_name='greek',
            lang_b_name='latin'
        )

        assert os.path.exists(path_a)
        assert os.path.exists(path_b)

        with pikepdf.open(path_a) as p:
            assert len(p.pages) == 2
        with pikepdf.open(path_b) as p:
            assert len(p.pages) == 2
