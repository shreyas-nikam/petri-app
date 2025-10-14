import io
import logging

class QueueHandler(logging.Handler):
    def __init__(self, q):
        super().__init__()
        self.q = q
    def emit(self, record):
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.q.put(("LOG", msg))

class StreamToQueue(io.TextIOBase):
    """File-like that writes to queue, line-buffered."""
    def __init__(self, q, tag="OUT"):
        self.q = q
        self.tag = tag
        self._buf = ""
    def write(self, s):
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self.q.put((self.tag, line + "\n"))
        return len(s)
    def flush(self):
        if self._buf:
            self.q.put((self.tag, self._buf))
            self._buf = ""
