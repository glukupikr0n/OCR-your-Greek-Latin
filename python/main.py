"""
OCR Your Greek Latin — Python backend entry point.
JSON-RPC 2.0 server over stdin/stdout.
"""

import sys
import os

# Ensure our package is importable
sys.path.insert(0, os.path.dirname(__file__))

from core.rpc_server import RPCServer
from core.job_queue import JobQueue
from core.config import config

from handlers.ocr_handler import OCRHandler
from handlers.pdf_handler import PDFHandler
from handlers.system_handler import SystemHandler
from handlers.data_handler import DataDownloadHandler


def main() -> None:
    server = RPCServer()
    queue = JobQueue(max_workers=config.parallel_threads)

    ocr_handler = OCRHandler(server, queue, config)
    pdf_handler = PDFHandler(config)
    system_handler = SystemHandler(config)
    data_handler = DataDownloadHandler(server, config)

    server.register_handler('ocr.process',         ocr_handler.process)
    server.register_handler('ocr.cancel',          ocr_handler.cancel)
    server.register_handler('system.check',        system_handler.check)
    server.register_handler('pdf.preview',         pdf_handler.preview)
    server.register_handler('pdf.split',           pdf_handler.split)
    server.register_handler('data.list_sources',   data_handler.list_sources)
    server.register_handler('data.download_tessdata', data_handler.download_tessdata)
    server.register_handler('data.download_corpus',   data_handler.download_corpus)

    try:
        server.run()
    finally:
        queue.shutdown(wait=False)


if __name__ == '__main__':
    main()
