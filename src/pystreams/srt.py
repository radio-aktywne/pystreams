from typing import Any

from pystreams.ffmpeg import FFmpegNode


class SRTNode(FFmpegNode):
    """An SRT node in an FFmpeg stream."""

    def __init__(
        self, host: str, port: str, options: dict[str, Any] | None = None
    ) -> None:
        target = f"srt://{host}:{port}"
        super().__init__(target, options)
