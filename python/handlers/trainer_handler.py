"""Custom model training handler."""

from __future__ import annotations

from core.config import AppConfig
from core.rpc_server import RPCServer
from ocr.trainer import ModelTrainer


class TrainerHandler:
    def __init__(self, server: RPCServer, config: AppConfig):
        self._server = server
        self._config = config

    def train(self, params: dict) -> dict:
        ground_truth_dir = params['ground_truth_dir']
        base_lang = params.get('base_lang', 'grc')
        output_model_name = params.get('output_model_name', f'{base_lang}_custom')

        trainer = ModelTrainer(self._config)

        def progress_cb(pct: int, message: str) -> None:
            self._server.notify('ocr.train.progress', {
                'pct': pct,
                'message': message
            })

        output_path = trainer.train(
            ground_truth_dir=ground_truth_dir,
            base_lang=base_lang,
            output_model_name=output_model_name,
            progress_cb=progress_cb
        )

        return {
            'status': 'done',
            'output_path': output_path,
            'model_name': output_model_name
        }
