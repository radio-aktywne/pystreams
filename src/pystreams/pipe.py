from asyncio import create_subprocess_exec
from asyncio.subprocess import PIPE
from asyncio.subprocess import Process as AsyncioProcess
from collections.abc import Sequence
from typing import IO, AnyStr

from pystreams.stream import Stream, StreamFactory


class PipedProcessBasedStreamMetadata:
    """Metadata for a process-based stream in a pipe."""

    def __init__(
        self,
        args: Sequence[str],
        env: dict[str, str] | None = None,
        stderr: IO[AnyStr] | None = None,
    ) -> None:
        self._args = args
        self._env = env
        self._stderr = stderr

    @property
    def args(self) -> Sequence[str]:
        """The arguments to the process."""

        return self._args

    @property
    def env(self) -> dict[str, str] | None:
        """The environment variables for the process."""

        return self._env

    @property
    def stderr(self) -> IO[AnyStr] | None:
        """The standard error for the process."""

        return self._stderr


class PipedStreamMetadata:
    """Metadata for a piped stream."""

    def __init__(
        self,
        streams: Sequence[PipedProcessBasedStreamMetadata],
        stdin: IO[AnyStr] | None = None,
        stdout: IO[AnyStr] | None = None,
    ) -> None:
        self._streams = streams
        self._stdin = stdin
        self._stdout = stdout

    @property
    def streams(self) -> Sequence[PipedProcessBasedStreamMetadata]:
        """The streams in the pipe."""

        return self._streams

    @property
    def stdin(self) -> IO[AnyStr] | None:
        """The standard input for the first stream in the pipe."""

        return self._stdin

    @property
    def stdout(self) -> IO[AnyStr] | None:
        """The standard output for the last stream in the pipe."""

        return self._stdout


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

    async def create(self, metadata: PipedStreamMetadata) -> PipedStream:
        processes = []
        previous_stdout = metadata.stdin

        for stream in metadata.streams[:-1]:
            process = await create_subprocess_exec(
                *stream.args,
                env=stream.env,
                stdin=previous_stdout,
                stdout=PIPE,
                stderr=stream.stderr,
            )
            processes = processes + [process]
            previous_stdout = process.stdout

        last_stream = metadata.streams[-1]
        last_process = await create_subprocess_exec(
            *last_stream.args,
            env=last_stream.env,
            stdin=previous_stdout,
            stdout=metadata.stdout,
            stderr=last_stream.stderr,
        )
        processes = processes + [last_process]

        return PipedStream(processes)
