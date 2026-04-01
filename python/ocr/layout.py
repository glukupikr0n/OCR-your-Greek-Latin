"""Layout detection: single vs. double column via horizontal projection profile."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from PIL import Image


class LayoutMode(Enum):
    SINGLE_COLUMN = 'single'
    DOUBLE_COLUMN = 'double'


@dataclass
class LayoutRegion:
    mode: LayoutMode
    bbox: tuple[int, int, int, int]  # x0, y0, x1, y1 in pixels
    column_index: int                 # 0=left, 1=right, -1=full-width


class LayoutDetector:
    # Minimum gap width (fraction of page width) to consider double-column
    MIN_GAP_FRACTION = 0.04
    # How much of the central region to examine
    CENTER_MARGIN = 0.1

    def detect(self, image: Image.Image) -> LayoutMode:
        gray = self._to_gray(image)
        binary = self._binarize(gray)

        # Horizontal projection: count black pixels per column
        h_proj = np.sum(binary == 0, axis=0).astype(np.float32)

        img_w = gray.shape[1]
        # Focus on the middle 80% of page width
        margin = int(img_w * self.CENTER_MARGIN)
        center_proj = h_proj[margin: img_w - margin]

        # Smooth projection
        kernel_size = max(3, int(img_w * 0.005))
        if kernel_size % 2 == 0:
            kernel_size += 1
        smoothed = cv2.GaussianBlur(
            center_proj.reshape(1, -1),
            (kernel_size, 1),
            0
        ).flatten()

        # Look for a valley (gap) in the center third of the projection
        center_start = len(smoothed) // 3
        center_end = 2 * len(smoothed) // 3
        center_region = smoothed[center_start:center_end]

        if len(center_region) == 0:
            return LayoutMode.SINGLE_COLUMN

        min_val = center_region.min()
        max_val = smoothed.max()

        if max_val == 0:
            return LayoutMode.SINGLE_COLUMN

        gap_depth = 1.0 - (min_val / max_val)
        return LayoutMode.DOUBLE_COLUMN if gap_depth > 0.6 else LayoutMode.SINGLE_COLUMN

    def split_columns(
        self,
        image: Image.Image
    ) -> tuple[Image.Image, Image.Image]:
        """Find gutter and return (left_col, right_col)."""
        gray = self._to_gray(image)
        binary = self._binarize(gray)

        img_w = gray.shape[1]
        img_h = gray.shape[0]

        h_proj = np.sum(binary == 0, axis=0).astype(np.float32)
        margin = int(img_w * self.CENTER_MARGIN)
        center_proj = h_proj[margin: img_w - margin]

        if len(center_proj) == 0:
            mid = img_w // 2
        else:
            # Find the minimum in the center third (the gutter)
            cs = len(center_proj) // 3
            ce = 2 * len(center_proj) // 3
            local_min_idx = int(np.argmin(center_proj[cs:ce])) + cs + margin
            mid = local_min_idx

        left_img = image.crop((0, 0, mid, img_h))
        right_img = image.crop((mid, 0, img_w, img_h))
        return left_img, right_img

    def get_regions(self, image: Image.Image) -> list[LayoutRegion]:
        """Return LayoutRegion list for the image."""
        mode = self.detect(image)
        img_w, img_h = image.size

        if mode == LayoutMode.SINGLE_COLUMN:
            return [LayoutRegion(mode, (0, 0, img_w, img_h), -1)]

        left_img, right_img = self.split_columns(image)
        lw = left_img.width
        return [
            LayoutRegion(LayoutMode.DOUBLE_COLUMN, (0, 0, lw, img_h), 0),
            LayoutRegion(LayoutMode.DOUBLE_COLUMN, (lw, 0, img_w, img_h), 1)
        ]

    @staticmethod
    def _to_gray(image: Image.Image) -> np.ndarray:
        if image.mode != 'L':
            image = image.convert('L')
        return np.array(image)

    @staticmethod
    def _binarize(gray: np.ndarray) -> np.ndarray:
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary
