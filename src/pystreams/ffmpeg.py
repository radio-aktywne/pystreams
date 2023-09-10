from collections.abc import Sequence
from typing import Any

from pystreams.process import ProcessBasedStreamMetadata


def _build_args_from_options(options: dict[str, Any] | None) -> list[str]:
    options = options or {}
    args = []

    for key, value in options.items():
        if value is False:
            pass
        elif value is True or value is None:
            args = args + [f"-{key}"]
        elif isinstance(value, str):
            args = args + [f"-{key}", value]
        else:
            try:
                for v in value:
                    args = args + [f"-{key}", str(v)]
            except TypeError:
                args = args + [f"-{key}", str(value)]

    return args


class FFmpegNode:
    """A node in an FFmpeg stream."""

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


def _build_tee_target_args_from_options(options: dict[str, Any] | None) -> list[str]:
    options = options or {}
    args = []

    for key, value in options.items():
        if value is False:
            pass
        elif value is True or value is None:
            args = args + [key]
        elif isinstance(value, str):
            args = args + [f"{key}={value}"]
        else:
            try:
                for v in value:
                    args = args + [f"{key}={v}"]
            except TypeError:
                args = args + [f"{key}={value}"]

    return [arg.replace(":", "\\:") for arg in args]


def _build_tee_target(nodes: Sequence[FFmpegNode]) -> str:
    targets = []

    for node in nodes:
        args = _build_tee_target_args_from_options(node.options)
        targets.append(f"[{':'.join(args)}]{node.target}")

    return "|".join(targets)


class FFmpegTeeNode(FFmpegNode):
    """A tee node in an FFmpeg stream."""

    def __init__(
        self,
        nodes: Sequence[FFmpegNode],
        options: dict[str, Any] | None = None,
    ) -> None:
        options = options or {}

        target = _build_tee_target(nodes)
        options = options | {"f": "tee"}

        super().__init__(target, options)


class FFmpegStreamMetadata(ProcessBasedStreamMetadata):
    """Metadata for an FFmpeg stream."""

    def __init__(
        self,
        input: FFmpegNode | Sequence[FFmpegNode],
        output: FFmpegNode | Sequence[FFmpegNode],
        options: dict[str, Any] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        input = input if isinstance(input, Sequence) else [input]
        output = output if isinstance(output, Sequence) else [output]

        args = ["ffmpeg"]
        args = args + _build_args_from_options(options)

        for node in input:
            args = args + _build_args_from_options(node.options)
            args = args + ["-i", node.target]

        for node in output:
            args = args + _build_args_from_options(node.options)
            args = args + [node.target]

        super().__init__(args, env)
