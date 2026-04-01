"""OCR processing handler: orchestrates the full pipeline."""

from __future__ import annotations

import os
import uuid
from typing import Callable

from core.config import AppConfig
from core.job_queue import JobQueue
from core.rpc_server import RPCServer

from image.enhancer import ImageEnhancer, EnhancementOptions
from image.upscaler import ImageUpscaler
from ocr.engine import OCREngine, PageResult
from ocr.confidence import ConfidenceRetry
from ocr.layout import LayoutDetector
from pdf.reader import PDFReader
from pdf.writer import PDFWriter, PageDimensions
from pdf.toc import TOCDetector
from pdf.page_numbering import PageNumberExtractor
from pdf.splitter import BilingualSplitter


class OCRHandler:
    def __init__(self, server: RPCServer, queue: JobQueue, config: AppConfig):
        self._server = server
        self._queue = queue
        self._config = config
        self._active_jobs: dict[str, bool] = {}  # job_id → cancelled flag

    def process(self, params: dict) -> dict:
        input_path = params['input_path']
        output_path = params['output_path']
        languages = params.get('languages', self._config.default_languages)
        options = params.get('options', {})
        job_id = params.get('job_id', str(uuid.uuid4()))

        self._active_jobs[job_id] = False

        try:
            result = self._run_pipeline(input_path, output_path, languages, options, job_id)
        finally:
            self._active_jobs.pop(job_id, None)

        return result

    def cancel(self, params: dict) -> dict:
        job_id = params.get('job_id', '')
        if job_id and job_id in self._active_jobs:
            self._active_jobs[job_id] = True
            self._queue.cancel(job_id)
            return {'cancelled': True, 'job_id': job_id}
        elif not job_id and self._active_jobs:
            # Cancel all active jobs when no specific id is provided
            for jid in list(self._active_jobs.keys()):
                self._active_jobs[jid] = True
                self._queue.cancel(jid)
            return {'cancelled': True, 'job_id': 'all'}
        return {'cancelled': False, 'job_id': job_id}

    def _is_cancelled(self, job_id: str) -> bool:
        return self._active_jobs.get(job_id, False)

    def _run_pipeline(
        self,
        input_path: str,
        output_path: str,
        languages: list[str],
        options: dict,
        job_id: str
    ) -> dict:
        # Parse options
        enh_opts = EnhancementOptions(
            deskew=options.get('enhancement', {}).get('deskew', True),
            grayscale=options.get('enhancement', {}).get('grayscale', True),
            bw=options.get('enhancement', {}).get('bw', False),
            denoise=options.get('enhancement', {}).get('denoise', True),
            auto_contrast=options.get('enhancement', {}).get('auto_contrast', True),
            upscale_factor=options.get('enhancement', {}).get('upscale_factor', 1)
        )
        confidence_threshold = options.get('confidence_threshold', self._config.confidence_threshold)
        use_layout = options.get('layout_detection', True)
        use_confidence_retry = options.get('confidence_retry', True)
        toc_detection = options.get('toc_detection', True)
        page_numbering = options.get('page_numbering', True)
        split_bilingual = options.get('split_bilingual', False)
        page_range = options.get('page_range', [0, None])
        ocr_dpi = options.get('dpi', self._config.ocr_dpi)

        # Initialize components
        reader = PDFReader(input_path)
        total_pages = reader.page_count()
        engine = OCREngine(
            languages=languages,
            tesseract_cmd=self._config.tesseract_cmd,
            tessdata_dir=self._config.tessdata_dir
        )
        enhancer = ImageEnhancer()
        layout_detector = LayoutDetector()
        confidence_retry = ConfidenceRetry(engine, threshold=confidence_threshold)

        start_page = page_range[0] or 0
        end_page = page_range[1] if page_range[1] is not None else total_pages - 1
        pages_to_process = list(range(start_page, min(end_page + 1, total_pages)))

        page_results: list[PageResult] = []
        page_dims: list[PageDimensions] = []

        for i, page_num in enumerate(pages_to_process):
            if self._is_cancelled(job_id):
                break

            # Render page
            image = reader.render_page(page_num, dpi=ocr_dpi)
            orig_w, orig_h = image.size

            # Get PDF page dimensions in points
            import pikepdf
            with pikepdf.open(input_path) as pdf_obj:
                page_obj = pdf_obj.pages[page_num]
                media = page_obj.mediabox
                w_pts = float(media[2]) - float(media[0])
                h_pts = float(media[3]) - float(media[1])

            # Enhance
            enhanced = enhancer.enhance(image, enh_opts)
            enh_w, enh_h = enhanced.size

            dims = PageDimensions(
                width_pts=w_pts,
                height_pts=h_pts,
                width_px=enh_w,
                height_px=enh_h,
                dpi=ocr_dpi
            )
            page_dims.append(dims)

            # Layout detection
            if use_layout:
                regions = layout_detector.get_regions(enhanced)
            else:
                from ocr.layout import LayoutMode, LayoutRegion
                regions = [LayoutRegion(LayoutMode.SINGLE_COLUMN, (0, 0, enh_w, enh_h), -1)]

            # OCR per region, combine results
            combined_words = []
            for region in regions:
                x0, y0, x1, y1 = region.bbox
                region_img = enhanced.crop((x0, y0, x1, y1))
                region_result = engine.process_page(region_img, page_num)

                # Offset word coordinates back to full-page space
                for word in region_result.words:
                    word.left += x0
                    word.top += y0
                combined_words.extend(region_result.words)

            from ocr.engine import PageResult
            confs = [w.conf for w in combined_words if w.conf >= 0]
            avg_conf = sum(confs) / len(confs) if confs else 0.0
            page_result = PageResult(
                page_num=page_num,
                words=combined_words,
                plain_text=' '.join(w.text for w in combined_words),
                avg_confidence=round(avg_conf, 2)
            )

            # Confidence retry
            if use_confidence_retry:
                page_result = confidence_retry.retry_low_confidence(enhanced, page_result)

            page_results.append(page_result)

            # Send progress notification
            pct = int((i + 1) / len(pages_to_process) * 100)
            self._server.notify('ocr.progress', {
                'job_id': job_id,
                'page': page_num,
                'total_pages': total_pages,
                'pct': pct,
                'current_word_confidence': page_result.avg_confidence,
                'status': 'processing'
            })

        if self._is_cancelled(job_id):
            return {'status': 'cancelled', 'job_id': job_id}

        # TOC detection
        toc_entries = []
        if toc_detection:
            detector = TOCDetector()
            toc_entries = detector.detect(page_results)

        # Page numbering
        page_number_map = {}
        if page_numbering:
            extractor = PageNumberExtractor()
            page_number_map = extractor.extract(page_results)

        # Write searchable PDF
        writer = PDFWriter(input_path, output_path)
        writer.write_searchable(page_results, page_dims, toc_entries, page_number_map)

        # Bilingual splitting
        split_files = []
        if split_bilingual:
            splitter = BilingualSplitter()
            lang_a, lang_b = splitter.detect_alternating_languages(page_results)
            out_dir = os.path.dirname(output_path)
            lang_a_name = options.get('split_lang_a', 'greek')
            lang_b_name = options.get('split_lang_b', 'latin')
            shared_start = options.get('split_shared_start')
            shared_end = options.get('split_shared_end')
            shared_range = None
            if shared_start is not None and shared_end is not None:
                shared_range = (int(shared_start) - 1, int(shared_end) - 1)  # convert 1-indexed UI to 0-indexed
            path_a, path_b = splitter.split(
                output_path, out_dir, lang_a, lang_b,
                lang_a_name=lang_a_name,
                lang_b_name=lang_b_name,
                shared_range=shared_range
            )
            split_files = [path_a, path_b]

        overall_conf = sum(pr.avg_confidence for pr in page_results) / max(len(page_results), 1)

        return {
            'status': 'done',
            'job_id': job_id,
            'output_path': output_path,
            'pages_processed': len(page_results),
            'avg_confidence': round(overall_conf, 2),
            'toc_entries': [e.to_dict() for e in toc_entries],
            'page_number_map': {str(k): v for k, v in page_number_map.items()},
            'split_files': split_files
        }
