"""Unit tests for TOCDetector."""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ocr.engine import PageResult, WordResult
from pdf.toc import TOCDetector, TOCEntry


def make_page(page_num: int, text: str) -> PageResult:
    return PageResult(
        page_num=page_num,
        words=[],
        plain_text=text,
        avg_confidence=80.0
    )


@pytest.fixture
def detector():
    return TOCDetector()


def test_detect_latin_chapter_heading(detector):
    pages = [make_page(0, "LIBER I\nSome text follows here")]
    entries = detector.detect(pages)
    assert len(entries) >= 1
    assert entries[0].level == 1
    assert entries[0].page_num == 0
    assert 'LIBER' in entries[0].title


def test_detect_caput_heading(detector):
    pages = [make_page(2, "CAPUT III\nLorem ipsum")]
    entries = detector.detect(pages)
    assert len(entries) >= 1
    assert entries[0].level == 1
    assert entries[0].display_num == 'III'


def test_detect_chapter_heading(detector):
    pages = [make_page(5, "CHAPTER 7\nSome content")]
    entries = detector.detect(pages)
    assert len(entries) >= 1
    assert entries[0].level == 1


def test_detect_roman_numeral_heading(detector):
    pages = [make_page(3, "IV.\nSome section text")]
    entries = detector.detect(pages)
    # Roman numeral at start of line = level 2
    assert len(entries) >= 1


def test_no_false_positives_on_regular_text(detector):
    pages = [make_page(0, "The quick brown fox jumps over the lazy dog.\nAnother ordinary line.")]
    entries = detector.detect(pages)
    assert len(entries) == 0


def test_multiple_pages_multiple_entries(detector):
    pages = [
        make_page(0, "LIBER I\nText"),
        make_page(3, "LIBER II\nMore text"),
        make_page(7, "LIBER III\nEven more"),
    ]
    entries = detector.detect(pages)
    assert len(entries) == 3
    assert [e.page_num for e in entries] == [0, 3, 7]


def test_toc_entry_to_dict():
    entry = TOCEntry(title='LIBER I', page_num=0, level=1, display_num='I')
    d = entry.to_dict()
    assert d['title'] == 'LIBER I'
    assert d['page_num'] == 0
    assert d['level'] == 1
    assert d['display_num'] == 'I'
