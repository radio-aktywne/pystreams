from subprocess import PIPE, Popen
from typing import Any, AnyStr, Dict, IO, Optional, Sequence, Union

import ffmpeg

from pystreams.stream import ProcessBasedStream


class FFmpegNode:
    def __init__(
        self, target: str, options: Optional[Dict[str, Any]] = None
    ) -> None:
        self.target = target
        self.options = options


class FFmpegStream(ProcessBasedStream):
    def __init__(
        self,
        input: FFmpegNode,
        output: Union[FFmpegNode, Sequence[FFmpegNode]],
    ) -> None:
        super().__init__()
        self.input = input
        self.outputs = [output] if isinstance(output, FFmpegNode) else output

    def start_process(
        self,
        stdin: Optional[IO[AnyStr]] = PIPE,
        stdout: Optional[IO[AnyStr]] = PIPE,
        stderr: Optional[IO[AnyStr]] = PIPE,
    ) -> Popen:
        input = ffmpeg.input(
            self.input.target, enable_cuda=False, **self.input.options
        )
        outputs = [
            input.output(output.target, enable_cuda=False, **output.options)
            for output in self.outputs
        ]
        args = ffmpeg.merge_outputs(*outputs).compile(print_cmd=False)
        return Popen(args, stdin=stdin, stdout=stdout, stderr=stderr)
