"""Unit tests for ConfidenceRetry."""

import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ocr.engine import PageResult, WordResult
from ocr.confidence import ConfidenceRetry


def make_word(text, conf, left=0, top=0, w=50, h=20):
    return WordResult(text=text, conf=conf, left=left, top=top, width=w, height=h)


def make_page_result(words, page_num=0):
    confs = [w.conf for w in words if w.conf >= 0]
    avg = sum(confs) / len(confs) if confs else 0.0
    return PageResult(
        page_num=page_num,
        words=words,
        plain_text=' '.join(w.text for w in words),
        avg_confidence=avg
    )


def make_image(w=400, h=100):
    return Image.new('L', (w, h), 255)


def test_high_confidence_words_unchanged():
    engine = MagicMock()
    retry = ConfidenceRetry(engine, threshold=60.0)

    words = [
        make_word('hello', 90, left=10, top=10),
        make_word('world', 85, left=70, top=10)
    ]
    page_result = make_page_result(words)
    img = make_image()

    result = retry.retry_low_confidence(img, page_result)

    # Engine should not have been called since all words are high-confidence
    engine.run_on_region.assert_not_called()
    assert len(result.words) == 2
    assert result.words[0].text == 'hello'


def test_low_confidence_word_replaced_if_improved():
    engine = MagicMock()
    # Mock run_on_region to return a better word
    engine.run_on_region.return_value = {
        'text': ['alpha', ''],
        'conf': [85, -1],
        'left': [0, 0],
        'top': [0, 0],
        'width': [50, 0],
        'height': [20, 0]
    }

    retry = ConfidenceRetry(engine, threshold=60.0)

    words = [make_word('alph', 30, left=10, top=10, w=50, h=20)]
    page_result = make_page_result(words)
    img = make_image()

    result = retry.retry_low_confidence(img, page_result)

    assert result.words[0].conf > 30  # improved
    assert result.words[0].text == 'alpha'


def test_low_confidence_word_kept_if_not_improved():
    engine = MagicMock()
    # Mock returns even worse result
    engine.run_on_region.return_value = {
        'text': ['??', ''],
        'conf': [10, -1],
        'left': [0, 0],
        'top': [0, 0],
        'width': [50, 0],
        'height': [20, 0]
    }

    retry = ConfidenceRetry(engine, threshold=60.0)

    words = [make_word('alph', 30, left=10, top=10, w=50, h=20)]
    page_result = make_page_result(words)
    img = make_image()

    result = retry.retry_low_confidence(img, page_result)

    # Keep original word since retry made it worse
    assert result.words[0].text == 'alph'
    assert result.words[0].conf == 30


def test_empty_page_result_unchanged():
    engine = MagicMock()
    retry = ConfidenceRetry(engine, threshold=60.0)
    page_result = make_page_result([])
    img = make_image()

    result = retry.retry_low_confidence(img, page_result)
    assert result.words == []
    engine.run_on_region.assert_not_called()
