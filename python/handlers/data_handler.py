"""Download verified OCR training data from Lace and OpenGreekAndLatin."""

from __future__ import annotations

import os
import json
import urllib.request
import urllib.error
from pathlib import Path

from core.config import AppConfig
from core.rpc_server import RPCServer


# Known tessdata download sources
_TESSDATA_SOURCES = {
    'grc': {
        'url': 'https://github.com/tesseract-ocr/tessdata_best/raw/main/grc.traineddata',
        'label': 'Ancient Greek (tessdata_best)',
    },
    'lat': {
        'url': 'https://github.com/tesseract-ocr/tessdata_best/raw/main/lat.traineddata',
        'label': 'Latin (tessdata_best)',
    },
    'eng': {
        'url': 'https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata',
        'label': 'English (tessdata_best)',
    },
}

# Ground truth / corpus sources
_CORPUS_SOURCES = [
    {
        'id': 'lace_greek',
        'label': 'LACE Greek OCR Corrections',
        'url': 'https://raw.githubusercontent.com/LATTICE-project/lace/master/README.md',
        'note': 'Verified Greek OCR ground truth from the LACE project.',
    },
    {
        'id': 'ogl_sample',
        'label': 'OpenGreekAndLatin TEI corpus (sample)',
        'url': 'https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/README.md',
        'note': 'Ancient Greek and Latin texts (TEI XML) from the First 1K Years of Greek project.',
    },
]


class DataDownloadHandler:
    def __init__(self, server: RPCServer, config: AppConfig):
        self._server = server
        self._config = config

    def list_sources(self, params: dict) -> dict:
        """Return available download sources."""
        return {
            'tessdata': list(_TESSDATA_SOURCES.keys()),
            'tessdata_details': {k: v['label'] for k, v in _TESSDATA_SOURCES.items()},
            'corpus': [{'id': c['id'], 'label': c['label'], 'note': c['note']}
                       for c in _CORPUS_SOURCES],
        }

    def download_tessdata(self, params: dict) -> dict:
        """
        Download tessdata files for the specified languages.
        params: {langs: ['grc', 'lat', ...], tessdata_dir: str (optional)}
        """
        langs = params.get('langs', ['grc', 'lat'])
        tessdata_dir = params.get('tessdata_dir') or self._config.tessdata_dir or self._find_tessdata_dir()

        if not tessdata_dir:
            return {'error': 'Could not determine tessdata directory. Please specify tessdata_dir.'}

        os.makedirs(tessdata_dir, exist_ok=True)
        results = {}

        for i, lang in enumerate(langs):
            source = _TESSDATA_SOURCES.get(lang)
            if not source:
                results[lang] = {'status': 'skipped', 'reason': 'Unknown language'}
                continue

            out_path = os.path.join(tessdata_dir, f'{lang}.traineddata')
            pct = int((i / len(langs)) * 100)
            self._server.notify('data.progress', {
                'pct': pct,
                'message': f'Downloading {source["label"]}…',
                'lang': lang
            })

            try:
                urllib.request.urlretrieve(source['url'], out_path)
                results[lang] = {'status': 'ok', 'path': out_path}
            except urllib.error.URLError as e:
                results[lang] = {'status': 'error', 'reason': str(e)}

        self._server.notify('data.progress', {'pct': 100, 'message': 'Download complete.'})
        return {'tessdata_dir': tessdata_dir, 'results': results}

    def download_corpus(self, params: dict) -> dict:
        """
        Download corpus data for training reference.
        params: {corpus_ids: [...], output_dir: str}
        """
        corpus_ids = params.get('corpus_ids', [])
        output_dir = params.get('output_dir', os.path.expanduser('~/scriptorium-corpus'))
        os.makedirs(output_dir, exist_ok=True)

        results = {}
        sources = [c for c in _CORPUS_SOURCES if c['id'] in corpus_ids]

        for i, source in enumerate(sources):
            pct = int((i / max(len(sources), 1)) * 100)
            self._server.notify('data.progress', {
                'pct': pct,
                'message': f'Fetching {source["label"]}…',
            })
            out_path = os.path.join(output_dir, f'{source["id"]}_info.md')
            try:
                urllib.request.urlretrieve(source['url'], out_path)
                results[source['id']] = {'status': 'ok', 'path': out_path, 'note': source['note']}
            except urllib.error.URLError as e:
                results[source['id']] = {'status': 'error', 'reason': str(e)}

        self._server.notify('data.progress', {'pct': 100, 'message': 'Download complete.'})
        return {'output_dir': output_dir, 'results': results}

    @staticmethod
    def _find_tessdata_dir() -> str:
        """Try common tessdata locations."""
        candidates = [
            '/usr/local/share/tessdata',
            '/usr/share/tessdata',
            '/opt/homebrew/share/tessdata',
        ]
        for p in candidates:
            if os.path.isdir(p):
                return p
        return ''
