"""Thread pool for parallel OCR page processing."""

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable


class JobQueue:
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._jobs: dict[str, Future] = {}

    def submit(self, job_id: str, fn: Callable, *args, **kwargs) -> Future:
        future = self._executor.submit(fn, *args, **kwargs)
        self._jobs[job_id] = future
        future.add_done_callback(lambda f: self._jobs.pop(job_id, None))
        return future

    def cancel(self, job_id: str) -> bool:
        future = self._jobs.get(job_id)
        if future is None:
            return False
        cancelled = future.cancel()
        if cancelled:
            self._jobs.pop(job_id, None)
        return cancelled

    def status(self, job_id: str) -> str:
        future = self._jobs.get(job_id)
        if future is None:
            return 'unknown'
        if future.cancelled():
            return 'cancelled'
        if future.running():
            return 'running'
        if future.done():
            return 'done'
        return 'pending'

    def shutdown(self, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait)
