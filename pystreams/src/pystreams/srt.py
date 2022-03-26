from typing import Any, Dict, Optional

from pystreams.ffmpeg import FFmpegNode


class SRTNode(FFmpegNode):
    def __init__(
        self, host: str, port: str, options: Optional[Dict[str, Any]] = None
    ) -> None:
        target = f"srt://{host}:{port}"
        super().__init__(target, options)
