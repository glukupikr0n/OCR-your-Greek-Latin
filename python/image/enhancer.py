"""Image enhancement pipeline: deskew, grayscale, B&W, denoise, autocontrast."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image, ImageOps


@dataclass
class EnhancementOptions:
    deskew: bool = True
    grayscale: bool = True
    bw: bool = False
    denoise: bool = True
    auto_contrast: bool = True
    upscale_factor: int = 1


class ImageEnhancer:
    def enhance(self, image: Image.Image, opts: EnhancementOptions) -> Image.Image:
        """Apply the enhancement pipeline in order."""
        if opts.upscale_factor > 1:
            from image.upscaler import ImageUpscaler
            image = ImageUpscaler().upscale(image, opts.upscale_factor)

        if opts.grayscale:
            image = self.to_grayscale(image)

        if opts.bw:
            image = self.to_bw(image)

        if opts.denoise:
            image = self.denoise(image)

        if opts.deskew:
            image = self.deskew(image)

        if opts.auto_contrast:
            image = self.auto_contrast(image)

        return image

    def to_grayscale(self, image: Image.Image) -> Image.Image:
        return image.convert('L')

    def to_bw(self, image: Image.Image, threshold: int = 0) -> Image.Image:
        """Convert to binary using Otsu thresholding (threshold=0 means auto)."""
        if image.mode != 'L':
            image = image.convert('L')
        arr = np.array(image)
        flag = cv2.THRESH_BINARY
        if threshold == 0:
            flag |= cv2.THRESH_OTSU
            thresh_val = 0
        else:
            thresh_val = threshold
        _, binary = cv2.threshold(arr, thresh_val, 255, flag)
        return Image.fromarray(binary)

    def deskew(self, image: Image.Image) -> Image.Image:
        """Two-pass deskew: coarse ±10° (1° steps), fine ±1° (0.1° steps)."""
        # Coarse pass: find angle in ±10°
        angle = self._find_skew_angle(image, max_angle=10.0, step=1.0)
        if abs(angle) > 0.1:
            image = self._rotate(image, angle)

        # Fine pass: refine in ±1°
        fine_angle = self._find_skew_angle(image, max_angle=1.0, step=0.1)
        if abs(fine_angle) > 0.05:
            image = self._rotate(image, fine_angle)

        return image

    def denoise(self, image: Image.Image) -> Image.Image:
        arr = np.array(image)
        if len(arr.shape) == 2:
            # Grayscale
            denoised = cv2.fastNlMeansDenoising(arr, h=10, templateWindowSize=7, searchWindowSize=21)
        else:
            # Color
            denoised = cv2.fastNlMeansDenoisingColored(arr, h=10, hColor=10,
                                                        templateWindowSize=7, searchWindowSize=21)
        return Image.fromarray(denoised)

    def auto_contrast(self, image: Image.Image) -> Image.Image:
        if image.mode == '1':
            return image
        return ImageOps.autocontrast(image, cutoff=2)

    def _find_skew_angle(
        self,
        image: Image.Image,
        max_angle: float = 10.0,
        step: float = 1.0
    ) -> float:
        """Find the deskew angle using minAreaRect on detected contours."""
        if image.mode != 'L':
            gray = np.array(image.convert('L'))
        else:
            gray = np.array(image)

        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return 0.0

        # Concatenate all contour points
        all_points = np.concatenate(contours).squeeze()
        if all_points.ndim < 2 or len(all_points) < 5:
            return 0.0

        # Fit rotated rectangle
        rect = cv2.minAreaRect(all_points)
        angle = rect[2]

        # cv2.minAreaRect returns angles in [-90, 0)
        # Normalize to [-45, 45]
        if angle < -45:
            angle += 90

        # Clamp to requested range
        angle = max(-max_angle, min(max_angle, angle))
        return angle

    @staticmethod
    def _rotate(image: Image.Image, angle: float) -> Image.Image:
        """Rotate image by angle degrees, expanding canvas to avoid clipping."""
        if image.mode == 'L':
            fill = 255
        elif image.mode == '1':
            fill = 1
        else:
            fill = (255, 255, 255)
        return image.rotate(-angle, expand=True, fillcolor=fill, resample=Image.BICUBIC)
