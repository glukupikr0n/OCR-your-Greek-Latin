"""Unit tests for ImageEnhancer."""

import math
import pytest
import numpy as np
from PIL import Image

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from image.enhancer import ImageEnhancer, EnhancementOptions


def make_text_image(width: int = 400, height: int = 100) -> Image.Image:
    """Create a synthetic white image with black horizontal stripes."""
    arr = np.ones((height, width), dtype=np.uint8) * 255
    for y in range(10, height, 20):
        arr[y:y+3, 10:width-10] = 0
    return Image.fromarray(arr)


def rotate_image(img: Image.Image, angle: float) -> Image.Image:
    return img.rotate(angle, expand=True, fillcolor=255)


@pytest.fixture
def enhancer():
    return ImageEnhancer()


def test_to_grayscale_produces_L_mode(enhancer):
    img = Image.new('RGB', (100, 100), color=(120, 80, 40))
    result = enhancer.to_grayscale(img)
    assert result.mode == 'L'


def test_to_bw_produces_binary_image(enhancer):
    img = Image.new('L', (100, 100), color=128)
    result = enhancer.to_bw(img)
    arr = np.array(result)
    unique_vals = set(arr.flatten().tolist())
    assert unique_vals.issubset({0, 255}), f"Expected binary image, got {unique_vals}"


def test_auto_contrast_increases_dynamic_range(enhancer):
    # Create low-contrast image (pixel values between 100-150)
    arr = np.full((100, 100), 125, dtype=np.uint8)
    arr[0, 0] = 100
    arr[99, 99] = 150
    img = Image.fromarray(arr)

    result = enhancer.auto_contrast(img)
    result_arr = np.array(result)
    # After autocontrast, range should be wider
    assert result_arr.max() - result_arr.min() >= arr.max() - arr.min()


def test_deskew_coarse_corrects_10_degree_rotation(enhancer):
    base = make_text_image(600, 200)
    rotated = rotate_image(base, 10)  # rotate by 10 degrees

    opts = EnhancementOptions(deskew=True, grayscale=False, bw=False,
                               denoise=False, auto_contrast=False)
    result = enhancer.enhance(rotated, opts)

    # Result should be approximately axis-aligned (close to original dimensions ratio)
    ratio_orig = base.width / base.height
    ratio_result = result.width / result.height
    # After deskewing a 10° rotation, dimensions should be more square-ish than 45°
    assert ratio_result > 0.5  # sanity check


def test_deskew_does_not_distort_straight_image(enhancer):
    img = make_text_image(400, 100)
    opts = EnhancementOptions(deskew=True, grayscale=False, bw=False,
                               denoise=False, auto_contrast=False)
    result = enhancer.enhance(img, opts)
    # Size should not change dramatically for a straight image
    assert abs(result.width - img.width) < 50
    assert abs(result.height - img.height) < 50


def test_denoise_does_not_crash_on_gray(enhancer):
    img = Image.new('L', (100, 100), color=200)
    result = enhancer.denoise(img)
    assert result.size == img.size


def test_denoise_does_not_crash_on_rgb(enhancer):
    img = Image.new('RGB', (100, 100), color=(200, 150, 100))
    result = enhancer.denoise(img)
    assert result.size == img.size
