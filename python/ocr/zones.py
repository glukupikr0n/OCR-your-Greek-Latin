"""Zone management for layout-aware OCR: presets, custom zones, auto-detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import cv2
import numpy as np
import pytesseract
from PIL import Image


class ZonePreset(Enum):
    FULL_PAGE = 'full_page'
    LEFT_MARGIN = 'left_margin'
    RIGHT_MARGIN = 'right_margin'
    BOTH_MARGINS = 'both_margins'
    BODY_ONLY = 'body_only'
    AUTO_DETECT = 'auto_detect'


@dataclass
class OCRZone:
    """A rectangular OCR region. Coordinates are normalized 0.0–1.0."""
    x0: float
    y0: float
    x1: float
    y1: float
    psm: int = 3           # Tesseract page-segmentation mode for this zone
    lang: str = ''         # Override language (empty = use page default)
    label: str = ''        # Human-readable label

    def to_dict(self) -> dict:
        return {
            'x0': self.x0, 'y0': self.y0,
            'x1': self.x1, 'y1': self.y1,
            'psm': self.psm,
            'lang': self.lang,
            'label': self.label,
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'OCRZone':
        return cls(
            x0=float(d.get('x0', 0)),
            y0=float(d.get('y0', 0)),
            x1=float(d.get('x1', 1)),
            y1=float(d.get('y1', 1)),
            psm=int(d.get('psm', 3)),
            lang=str(d.get('lang', '')),
            label=str(d.get('label', '')),
        )

    def pixel_bbox(self, width: int, height: int) -> tuple[int, int, int, int]:
        return (
            int(self.x0 * width),
            int(self.y0 * height),
            int(self.x1 * width),
            int(self.y1 * height),
        )


@dataclass
class MarginConfig:
    top: float = 0.05
    bottom: float = 0.05
    left: float = 0.07
    right: float = 0.07

    @classmethod
    def from_dict(cls, d: dict) -> 'MarginConfig':
        return cls(
            top=float(d.get('top', 0.05)),
            bottom=float(d.get('bottom', 0.05)),
            left=float(d.get('left', 0.07)),
            right=float(d.get('right', 0.07)),
        )


class ZoneManager:
    def get_preset_zones(
        self,
        preset: str | ZonePreset,
        image: Image.Image | None = None,
        margins: MarginConfig | None = None
    ) -> list[OCRZone]:
        """Return zones for a given preset string or enum value."""
        if isinstance(preset, str):
            try:
                preset = ZonePreset(preset)
            except ValueError:
                preset = ZonePreset.FULL_PAGE

        m = margins or MarginConfig()
        body_x0 = m.left
        body_y0 = m.top
        body_x1 = 1.0 - m.right
        body_y1 = 1.0 - m.bottom

        if preset == ZonePreset.FULL_PAGE:
            return [OCRZone(0, 0, 1, 1, label='Full Page')]

        if preset == ZonePreset.BODY_ONLY:
            return [OCRZone(body_x0, body_y0, body_x1, body_y1, label='Body')]

        if preset == ZonePreset.LEFT_MARGIN:
            return [OCRZone(0, body_y0, m.left, body_y1, label='Left Margin')]

        if preset == ZonePreset.RIGHT_MARGIN:
            return [OCRZone(1.0 - m.right, body_y0, 1.0, body_y1, label='Right Margin')]

        if preset == ZonePreset.BOTH_MARGINS:
            return [
                OCRZone(0, body_y0, m.left, body_y1, label='Left Margin'),
                OCRZone(1.0 - m.right, body_y0, 1.0, body_y1, label='Right Margin'),
            ]

        if preset == ZonePreset.AUTO_DETECT:
            if image is not None:
                return self.auto_detect_zones(image)
            return [OCRZone(0, 0, 1, 1, label='Full Page')]

        return [OCRZone(0, 0, 1, 1, label='Full Page')]

    def auto_detect_zones(self, image: Image.Image) -> list[OCRZone]:
        """Use Tesseract block-level analysis to find text regions."""
        img_w, img_h = image.size
        data = pytesseract.image_to_data(
            image,
            config='--psm 1',
            output_type=pytesseract.Output.DICT
        )

        zones: list[OCRZone] = []
        n = len(data['level'])
        for i in range(n):
            # Level 2 = block, Level 3 = paragraph
            if data['level'][i] in (2, 3):
                w = data['width'][i]
                h = data['height'][i]
                if w < 10 or h < 10:
                    continue
                x0 = data['left'][i] / img_w
                y0 = data['top'][i] / img_h
                x1 = (data['left'][i] + w) / img_w
                y1 = (data['top'][i] + h) / img_h
                x0, y0 = max(0.0, x0), max(0.0, y0)
                x1, y1 = min(1.0, x1), min(1.0, y1)
                zones.append(OCRZone(x0, y0, x1, y1, psm=6, label=f'Block {len(zones)+1}'))

        return zones if zones else [OCRZone(0, 0, 1, 1, label='Full Page')]
