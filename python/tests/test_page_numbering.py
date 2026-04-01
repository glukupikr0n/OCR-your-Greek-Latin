"""Unit tests for PageNumberExtractor."""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ocr.engine import PageResult, WordResult
from pdf.page_numbering import PageNumberExtractor


def make_page_with_margin_number(page_num, number_text, position='bottom'):
    """Create a PageResult that looks like it has a page number in the margin."""
    # Simulate a page 3508px tall (300dpi A4), margin is bottom 10%
    page_height = 3508
    margin_top = int(page_height * 0.9)  # bottom 10%

    if position == 'bottom':
        word_top = margin_top + 50
    else:
        word_top = 10  # top margin

    words = [
        WordResult(text='Lorem', conf=90, left=50, top=200, width=60, height=20),
        WordResult(text='ipsum', conf=88, left=120, top=200, width=50, height=20),
        WordResult(text=number_text, conf=85, left=280, top=word_top, width=30, height=20),
    ]
    confs = [w.conf for w in words]
    return PageResult(
        page_num=page_num,
        words=words,
        plain_text=' '.join(w.text for w in words),
        avg_confidence=sum(confs)/len(confs)
    )


@pytest.fixture
def extractor():
    return PageNumberExtractor()


def test_extract_arabic_numeral_from_bottom_margin(extractor):
    pages = [make_page_with_margin_number(0, '42', position='bottom')]
    result = extractor.extract(pages)
    assert 0 in result
    assert result[0] == '42'


def test_extract_roman_numeral(extractor):
    pages = [make_page_with_margin_number(0, 'IV', position='bottom')]
    result = extractor.extract(pages)
    assert 0 in result
    assert result[0] == 'IV'


def test_roman_to_int(extractor):
    assert extractor.roman_to_int('IV') == 4
    assert extractor.roman_to_int('XIV') == 14
    assert extractor.roman_to_int('XLII') == 42
    assert extractor.roman_to_int('MCMXCIX') == 1999


def test_int_to_roman(extractor):
    assert extractor.int_to_roman(4) == 'IV'
    assert extractor.int_to_roman(14) == 'XIV'
    assert extractor.int_to_roman(42) == 'XLII'
    assert extractor.int_to_roman(1999) == 'MCMXCIX'


def test_no_number_returns_empty(extractor):
    pages = [PageResult(
        page_num=0,
        words=[WordResult(text='Lorem', conf=90, left=50, top=200, width=60, height=20)],
        plain_text='Lorem',
        avg_confidence=90.0
    )]
    result = extractor.extract(pages)
    assert result == {}
