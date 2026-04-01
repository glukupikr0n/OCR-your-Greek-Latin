"""JSON-RPC 2.0 server over stdin/stdout."""

import json
import sys
import threading
import traceback
from typing import Callable


class RPCServer:
    def __init__(self):
        self._handlers: dict[str, Callable] = {}
        self._write_lock = threading.Lock()

    def register_handler(self, method: str, fn: Callable) -> None:
        self._handlers[method] = fn

    def run(self) -> None:
        """Main read loop. Blocks until stdin closes."""
        for raw_line in sys.stdin:
            line = raw_line.strip()
            if not line:
                continue
            threading.Thread(
                target=self._handle_line,
                args=(line,),
                daemon=True
            ).start()

    def write(self, obj: dict) -> None:
        """Thread-safe write to stdout."""
        with self._write_lock:
            sys.stdout.write(json.dumps(obj, ensure_ascii=False) + '\n')
            sys.stdout.flush()

    def notify(self, method: str, params: dict) -> None:
        """Send a notification (id=null) to Electron."""
        self.write({
            'jsonrpc': '2.0',
            'id': None,
            'method': method,
            'params': params
        })

    def _handle_line(self, line: str) -> None:
        request_id = None
        try:
            msg = json.loads(line)
            request_id = msg.get('id')
            method = msg.get('method', '')
            params = msg.get('params', {})

            if method not in self._handlers:
                self._send_error(request_id, -32601, f'Method not found: {method}')
                return

            result = self._handlers[method](params)
            self.write({
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            })

        except json.JSONDecodeError as e:
            self._send_error(request_id, -32700, f'Parse error: {e}')
        except Exception as e:
            tb = traceback.format_exc()
            self._send_error(request_id, -32000, str(e), {'traceback': tb})

    def _send_error(self, request_id, code: int, message: str, data: dict | None = None) -> None:
        error = {'code': code, 'message': message}
        if data:
            error['data'] = data
        self.write({
            'jsonrpc': '2.0',
            'id': request_id,
            'error': error
        })
