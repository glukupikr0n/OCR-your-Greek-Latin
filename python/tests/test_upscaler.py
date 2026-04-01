"""Unit tests for ImageUpscaler."""

import pytest
from PIL import Image

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from image.upscaler import ImageUpscaler


@pytest.fixture
def upscaler():
    return ImageUpscaler()


def test_upscale_1x_returns_same_size(upscaler):
    img = Image.new('RGB', (100, 80))
    result = upscaler.upscale(img, 1)
    assert result.size == (100, 80)


def test_upscale_2x_doubles_dimensions(upscaler):
    img = Image.new('RGB', (100, 80))
    result = upscaler.upscale(img, 2)
    assert result.size == (200, 160)


def test_upscale_4x_quadruples_dimensions(upscaler):
    img = Image.new('RGB', (50, 40))
    result = upscaler.upscale(img, 4)
    assert result.size == (200, 160)


def test_upscale_invalid_factor_raises(upscaler):
    img = Image.new('RGB', (100, 100))
    with pytest.raises(ValueError):
        upscaler.upscale(img, 5)

    with pytest.raises(ValueError):
        upscaler.upscale(img, 0)
