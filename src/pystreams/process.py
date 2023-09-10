import os
from asyncio import create_subprocess_exec
from asyncio.subprocess import DEVNULL
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
    ) -> None:
        self._args = args
        self._env = env

    @property
    def args(self) -> Sequence[str]:
        """The arguments to the process."""

        return self._args

    @property
    def env(self) -> dict[str, str] | None:
        """The environment variables for the process."""

        return self._env


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

    async def create(
        self,
        metadata: ProcessBasedStreamMetadata,
        stdin: IO[AnyStr] | None = DEVNULL,
        stdout: IO[AnyStr] | None = DEVNULL,
        stderr: IO[AnyStr] | None = DEVNULL,
    ) -> ProcessBasedStream:
        env = os.environ.copy() | (metadata.env or {})

        process = await create_subprocess_exec(
            *metadata.args,
            env=env,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
        )

        return ProcessBasedStream(process)
