from asyncio import create_subprocess_exec
from asyncio.subprocess import Process as AsyncioProcess
from collections.abc import Sequence
from typing import IO, AnyStr

from pystreams.stream import Stream, StreamFactory


class ProcessBasedStreamMetadata:
    """Metadata for a process-based stream."""

    def __init__(
        self,
        args: Sequence[str],
        env: dict[str, str] | None = None,
        stdin: IO[AnyStr] | None = None,
        stdout: IO[AnyStr] | None = None,
        stderr: IO[AnyStr] | None = None,
    ) -> None:
        self._args = args
        self._env = env
        self._stdin = stdin
        self._stdout = stdout
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
    def stdin(self) -> IO[AnyStr] | None:
        """The standard input for the process."""

        return self._stdin

    @property
    def stdout(self) -> IO[AnyStr] | None:
        """The standard output for the process."""

        return self._stdout

    @property
    def stderr(self) -> IO[AnyStr] | None:
        """The standard error for the process."""

        return self._stderr


class ProcessBasedStream(Stream):
    """A stream based on a process."""

    def __init__(self, process: AsyncioProcess) -> None:
        self._process = process

    async def terminate(self) -> None:
        self._process.terminate()

    async def kill(self) -> None:
        self._process.kill()

    async def wait(self) -> int:
        return await self._process.wait()


class ProcessBasedStreamFactory(StreamFactory[ProcessBasedStreamMetadata]):
    """A factory for creating process-based streams."""

    async def create(self, metadata: ProcessBasedStreamMetadata) -> ProcessBasedStream:
        process = await create_subprocess_exec(
            *metadata.args,
            env=metadata.env,
            stdin=metadata.stdin,
            stdout=metadata.stdout,
            stderr=metadata.stderr,
        )

        return ProcessBasedStream(process)
