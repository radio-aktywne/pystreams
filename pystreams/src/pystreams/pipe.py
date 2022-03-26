from subprocess import PIPE, Popen
from typing import AnyStr, IO, Optional

from pystreams.stream import ProcessBasedStream


class Pipe(ProcessBasedStream):
    def __init__(self, *streams: ProcessBasedStream) -> None:
        super().__init__()
        self.streams = streams

    def start_process(
        self,
        stdin: Optional[IO[AnyStr]] = PIPE,
        stdout: Optional[IO[AnyStr]] = PIPE,
        stderr: Optional[IO[AnyStr]] = PIPE,
    ) -> Popen:
        previous_stdout = stdin
        for i in range(len(self.streams) - 1):
            process = self.streams[i].start_process(stdin=previous_stdout)
            previous_stdout = process.stdout
        return self.streams[-1].start_process(
            stdin=previous_stdout, stdout=stdout, stderr=stderr
        )
