import os
from asyncio import create_subprocess_exec
from asyncio.subprocess import DEVNULL
from asyncio.subprocess import Process as AsyncioProcess
from collections.abc import Sequence
from typing import IO, AnyStr

from pystreams.process import ProcessBasedStreamMetadata
from pystreams.stream import Stream, StreamFactory


class PipedStreamMetadata:
    """Metadata for a piped stream."""

    def __init__(
        self,
        streams: Sequence[ProcessBasedStreamMetadata],
    ) -> None:
        self._streams = streams

    @property
    def streams(self) -> Sequence[ProcessBasedStreamMetadata]:
        """The streams in the pipe."""

        return self._streams


class PipedStream(Stream):
    """A stream based on a pipe of multiple process-based streams."""

    def __init__(self, processes: Sequence[AsyncioProcess]) -> None:
        self._processes = processes

    async def terminate(self) -> None:
        for process in reversed(self._processes):
            process.terminate()

    async def kill(self) -> None:
        for process in reversed(self._processes):
            process.kill()

    async def wait(self) -> None:
        for process in reversed(self._processes):
            await process.wait()


class PipedStreamFactory(StreamFactory[PipedStreamMetadata]):
    """A factory for creating piped streams."""

    async def create(
        self,
        metadata: PipedStreamMetadata,
        stdin: IO[AnyStr] | None = DEVNULL,
        stdout: IO[AnyStr] | None = DEVNULL,
        stderr: IO[AnyStr] | None = DEVNULL,
    ) -> PipedStream:
        processes = []
        pipes = []
        current_stdin = stdin

        try:
            for stream in metadata.streams[:-1]:
                env = os.environ.copy() | (stream.env or {})

                pipe = os.pipe()

                process = await create_subprocess_exec(
                    *stream.args,
                    env=env,
                    stdin=current_stdin,
                    stdout=pipe[1],
                    stderr=stderr,
                )

                processes = processes + [process]
                pipes = pipes + [pipe]
                current_stdin = pipe[0]

            last_stream = metadata.streams[-1]

            env = os.environ.copy() | (last_stream.env or {})

            last_process = await create_subprocess_exec(
                *last_stream.args,
                env=env,
                stdin=current_stdin,
                stdout=stdout,
                stderr=stderr,
            )

            processes = processes + [last_process]

            return PipedStream(processes)
        finally:
            for pipe in pipes:
                os.close(pipe[0])
                os.close(pipe[1])
