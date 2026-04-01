"""Custom Tesseract model training interface."""

from __future__ import annotations

import os
import subprocess
import shutil
from typing import Callable

from core.config import AppConfig


class ModelTrainer:
    def __init__(self, config: AppConfig):
        self._config = config

    def prepare_ground_truth(
        self,
        image_paths: list[str],
        output_dir: str
    ) -> None:
        """
        Generate .box files for each image so the user can correct them.
        Runs Tesseract with --psm 6 to produce LSTM box files.
        """
        os.makedirs(output_dir, exist_ok=True)
        cmd = self._config.tesseract_cmd

        for img_path in image_paths:
            basename = os.path.splitext(os.path.basename(img_path))[0]
            out_base = os.path.join(output_dir, basename)
            subprocess.run(
                [cmd, img_path, out_base, '--psm', '6', 'lstmbox'],
                check=True
            )

    def train(
        self,
        ground_truth_dir: str,
        base_lang: str,
        output_model_name: str,
        progress_cb: Callable[[int, str], None] | None = None
    ) -> str:
        """
        Run Tesseract LSTM fine-tuning pipeline.
        Returns path to the resulting .traineddata file.
        """
        tessdata = self._config.tessdata_dir
        work_dir = os.path.join(ground_truth_dir, '_training_work')
        os.makedirs(work_dir, exist_ok=True)

        # Step 1: Generate unicharset
        if progress_cb:
            progress_cb(10, 'Generating unicharset...')
        box_files = [
            os.path.join(ground_truth_dir, f)
            for f in os.listdir(ground_truth_dir)
            if f.endswith('.box')
        ]
        if not box_files:
            raise ValueError('No .box files found in ground truth directory')

        unicharset_path = os.path.join(work_dir, 'unicharset')
        subprocess.run(
            ['unicharset_extractor', '--output_unicharset', unicharset_path] + box_files,
            check=True
        )

        # Step 2: Generate lstmf training files
        if progress_cb:
            progress_cb(30, 'Generating training data...')
        cmd = self._config.tesseract_cmd
        for box_file in box_files:
            img_path = box_file.replace('.box', '.png')
            if not os.path.exists(img_path):
                img_path = box_file.replace('.box', '.tif')
            basename = os.path.splitext(os.path.basename(box_file))[0]
            out_base = os.path.join(work_dir, basename)
            subprocess.run(
                [cmd, img_path, out_base, '--psm', '6',
                 f'--tessdata-dir', tessdata,
                 '-l', base_lang, 'lstm.train'],
                check=True
            )

        # Step 3: LSTM training
        if progress_cb:
            progress_cb(50, 'Training LSTM model...')
        lstmf_files = [
            os.path.join(work_dir, f)
            for f in os.listdir(work_dir)
            if f.endswith('.lstmf')
        ]
        training_list = os.path.join(work_dir, 'training_list.txt')
        with open(training_list, 'w') as f:
            f.write('\n'.join(lstmf_files))

        checkpoint_dir = os.path.join(work_dir, 'checkpoints')
        os.makedirs(checkpoint_dir, exist_ok=True)

        base_model = os.path.join(tessdata, f'{base_lang}.traineddata')
        subprocess.run(
            [
                'lstmtraining',
                '--model_output', os.path.join(checkpoint_dir, output_model_name),
                '--continue_from', base_model,
                '--train_listfile', training_list,
                '--target_error_rate', '0.01',
                '--max_iterations', '400',
            ],
            check=True
        )

        # Step 4: Combine model
        if progress_cb:
            progress_cb(80, 'Combining model...')
        output_traineddata = os.path.join(work_dir, f'{output_model_name}.traineddata')
        checkpoint_file = os.path.join(checkpoint_dir, f'{output_model_name}_checkpoint')
        subprocess.run(
            [
                'lstmtraining',
                '--stop_training',
                '--continue_from', checkpoint_file,
                '--traineddata', base_model,
                '--model_output', output_traineddata,
            ],
            check=True
        )

        if progress_cb:
            progress_cb(100, 'Training complete.')

        return output_traineddata
