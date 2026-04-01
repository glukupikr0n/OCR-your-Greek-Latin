"""Runtime configuration and constants."""

import os
from dataclasses import dataclass, field


@dataclass
class AppConfig:
    # OCR settings
    default_languages: list[str] = field(default_factory=lambda: ['grc', 'lat', 'eng'])
    confidence_threshold: float = 60.0
    parallel_threads: int = 4

    # Image enhancement defaults
    deskew: bool = True
    grayscale: bool = True
    bw: bool = False
    denoise: bool = True
    auto_contrast: bool = True
    upscale_factor: int = 1

    # PDF settings
    preview_dpi: int = 72
    ocr_dpi: int = 300
    toc_detection: bool = True
    page_numbering: bool = True
    split_bilingual: bool = False

    # Tesseract
    tesseract_cmd: str = field(default_factory=lambda: _find_tesseract())
    tessdata_dir: str = field(default_factory=lambda: _find_tessdata())


def _find_tesseract() -> str:
    candidates = [
        '/opt/homebrew/bin/tesseract',  # macOS Apple Silicon
        '/usr/local/bin/tesseract',      # macOS Intel
        '/usr/bin/tesseract',            # Linux
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return 'tesseract'


def _find_tessdata() -> str:
    candidates = [
        '/opt/homebrew/share/tessdata',
        '/usr/local/share/tessdata',
        '/usr/share/tesseract-ocr/4.00/tessdata',
        '/usr/share/tesseract-ocr/tessdata',
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    env = os.environ.get('TESSDATA_PREFIX', '')
    return env or ''


# Singleton config instance
config = AppConfig()
