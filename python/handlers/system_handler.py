"""System check handler — verifies Tesseract, Poppler, language data."""

import re
import shutil
import subprocess
import os
from core.config import AppConfig


class SystemHandler:
    def __init__(self, config: AppConfig):
        self._config = config

    def check(self, params: dict) -> dict:
        result = {
            'tesseract': self._check_tesseract(),
            'poppler': self._check_poppler(),
            'languages': self._check_languages(),
            'python_version': self._python_version(),
        }
        result['ready'] = (
            result['tesseract']['found'] and
            result['poppler']['found'] and
            len(result['languages']['missing']) == 0
        )
        return result

    def _check_tesseract(self) -> dict:
        cmd = self._config.tesseract_cmd
        path = shutil.which(cmd) or (cmd if os.path.exists(cmd) else None)
        if not path:
            return {'found': False, 'version': None, 'path': None}
        try:
            out = subprocess.check_output([path, '--version'], stderr=subprocess.STDOUT, text=True)
            version = out.split('\n')[0].strip()
        except Exception:
            version = 'unknown'
        return {'found': True, 'version': version, 'path': path}

    def _check_poppler(self) -> dict:
        path = shutil.which('pdftoppm')
        if not path:
            return {'found': False, 'version': None}
        try:
            out = subprocess.check_output(['pdftoppm', '-v'], stderr=subprocess.STDOUT, text=True)
            version = out.split('\n')[0].strip()
        except Exception:
            version = 'unknown'
        return {'found': True, 'version': version}

    def _check_languages(self) -> dict:
        required = self._config.default_languages
        tessdata = self._config.tessdata_dir
        available = []
        missing = []

        try:
            cmd = self._config.tesseract_cmd
            if os.path.exists(cmd) or shutil.which(cmd):
                out = subprocess.check_output(
                    [cmd, '--list-langs'],
                    stderr=subprocess.STDOUT,
                    text=True
                )
                available = [
                    l.strip() for l in out.splitlines()
                    if l.strip() and re.match(r'^[a-z0-9_]+$', l.strip())
                ]
        except Exception:
            pass

        for lang in required:
            if lang not in available:
                missing.append(lang)

        return {'available': available, 'required': required, 'missing': missing}

    def _python_version(self) -> str:
        import sys
        return sys.version
