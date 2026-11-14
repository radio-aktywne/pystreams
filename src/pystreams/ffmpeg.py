from collections.abc import Sequence
from typing import Any

from pystreams.process import ProcessBasedStreamMetadata
from pystreams.utils import CommandOptionsBuilder, Escaper


class FFmpegNode:
    """Node in an FFmpeg stream."""

    def __init__(self, target: str, options: dict[str, Any] | None = None) -> None:
        self._target = target
        self._options = options

    @property
    def target(self) -> str:
        """The target of the node."""
        return self._target

    @property
    def options(self) -> dict[str, Any] | None:
        """The options of the node."""
        return self._options


class FFmpegTeeNode(FFmpegNode):
    """Tee node in an FFmpeg stream."""

    def __init__(
        self,
        nodes: Sequence[FFmpegNode],
        options: dict[str, Any] | None = None,
    ) -> None:
        builder = CommandOptionsBuilder(escapes="\\' \n\t\r:]", separator="=")
        escaper = Escaper("\\' \n\t\r|")
        targets = []

        for node in nodes:
            args = ":".join(builder.build(node.options))
            targets = [*targets, escaper.escape(f"[{args}]{node.target}")]

        super().__init__("|".join(targets), (options or {}) | {"f": "tee"})


class FFmpegStreamMetadata(ProcessBasedStreamMetadata):
    """Metadata for an FFmpeg stream."""

    def __init__(
        self,
        input: FFmpegNode | Sequence[FFmpegNode],  # noqa: A002
        output: FFmpegNode | Sequence[FFmpegNode],
        options: dict[str, Any] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        input_ = input if isinstance(input, Sequence) else [input]
        output_ = output if isinstance(output, Sequence) else [output]

        builder = CommandOptionsBuilder(prefix="-")
        args = ["ffmpeg", *builder.build(options)]

        for node in input_:
            args = [*args, *builder.build(node.options), "-i", node.target]

        for node in output_:
            args = [*args, *builder.build(node.options), node.target]

        super().__init__(args, env)
