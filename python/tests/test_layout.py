"""Unit tests for LayoutDetector."""

import numpy as np
import pytest
from PIL import Image, ImageDraw

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ocr.layout import LayoutDetector, LayoutMode


@pytest.fixture
def detector():
    return LayoutDetector()


def make_single_column_image(width=600, height=800):
    """White image with black text-like stripes across full width."""
    img = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(img)
    for y in range(50, height - 50, 25):
        draw.rectangle([30, y, width - 30, y + 3], fill=0)
    return img


def make_double_column_image(width=600, height=800, gutter_x=300):
    """White image with text stripes in two columns separated by a gutter."""
    img = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(img)
    gutter_start = gutter_x - 20
    gutter_end = gutter_x + 20

    for y in range(50, height - 50, 25):
        # Left column
        draw.rectangle([30, y, gutter_start - 10, y + 3], fill=0)
        # Right column
        draw.rectangle([gutter_end + 10, y, width - 30, y + 3], fill=0)
    return img


def test_detect_single_column(detector):
    img = make_single_column_image()
    mode = detector.detect(img)
    assert mode == LayoutMode.SINGLE_COLUMN


def test_detect_double_column(detector):
    img = make_double_column_image()
    mode = detector.detect(img)
    assert mode == LayoutMode.DOUBLE_COLUMN


def test_split_columns_returns_two_images(detector):
    img = make_double_column_image(width=600)
    left, right = detector.split_columns(img)
    assert left.size[0] > 0
    assert right.size[0] > 0
    assert abs(left.size[0] + right.size[0] - img.size[0]) <= 5


def test_get_regions_single_column_returns_one_region(detector):
    img = make_single_column_image()
    regions = detector.get_regions(img)
    assert len(regions) == 1
    assert regions[0].column_index == -1


def test_get_regions_double_column_returns_two_regions(detector):
    img = make_double_column_image()
    regions = detector.get_regions(img)
    assert len(regions) == 2
    assert regions[0].column_index == 0
    assert regions[1].column_index == 1
