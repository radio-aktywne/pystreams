import os
from asyncio.subprocess import DEVNULL, Process as AsyncioProcess
from collections.abc import Sequence
from contextlib import ExitStack
from typing import IO, override

from pystreams.base import Stream, StreamFactory
from pystreams.process import (
    ProcessBasedStream,
    ProcessBasedStreamFactory,
    ProcessBasedStreamMetadata,
)


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
    """Stream based on a pipe of multiple process-based streams."""

    def __init__(self, streams: Sequence[ProcessBasedStream]) -> None:
        self._streams = streams

    @property
    def processes(self) -> Sequence[AsyncioProcess]:
        """The underlying processes."""
        return [stream.process for stream in self._streams]

    @override
    async def terminate(self) -> None:
        for stream in reversed(self._streams):
            await stream.terminate()

    @override
    async def kill(self) -> None:
        for stream in reversed(self._streams):
            await stream.kill()

    @override
    async def wait(self) -> None:
        for stream in reversed(self._streams):
            await stream.wait()


class PipedStreamFactory(StreamFactory[PipedStreamMetadata]):
    """Factory for PipedStream."""

    @override
    async def create(
        self,
        metadata: PipedStreamMetadata,
        stdin: IO | int | None = DEVNULL,
        stdout: IO | int | None = DEVNULL,
        stderr: IO | int | None = DEVNULL,
    ) -> PipedStream:
        factory = ProcessBasedStreamFactory()
        streams: list[ProcessBasedStream] = []

        try:
            with ExitStack() as stack:
                for i, item in enumerate(metadata.streams):
                    read, write = None, stdout

                    if i < len(metadata.streams) - 1:
                        read, write = os.pipe()
                        stack.callback(os.close, read)
                        stack.callback(os.close, write)

                    stream = await factory.create(
                        item, stdin=stdin, stdout=write, stderr=stderr
                    )
                    streams = [*streams, stream]

                    stdin = read
        except BaseException:
            for stream in reversed(streams):
                await stream.kill()

            for stream in streams:
                await stream.wait()

            raise

        return PipedStream(streams)
