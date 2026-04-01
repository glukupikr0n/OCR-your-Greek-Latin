"""Lanczos image upscaling up to 4×."""

from PIL import Image

VALID_FACTORS = (1, 2, 3, 4)


class ImageUpscaler:
    def upscale(self, image: Image.Image, factor: int) -> Image.Image:
        if factor not in VALID_FACTORS:
            raise ValueError(f'Upscale factor must be one of {VALID_FACTORS}, got {factor}')
        if factor == 1:
            return image
        new_w = image.width * factor
        new_h = image.height * factor
        return image.resize((new_w, new_h), Image.LANCZOS)
