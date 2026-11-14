import os
import signal
from asyncio import create_subprocess_exec
from asyncio.subprocess import DEVNULL, Process as AsyncioProcess
from collections.abc import Sequence
from contextlib import suppress
from dataclasses import dataclass
from typing import IO, override

from pystreams.base import Stream, StreamFactory


@dataclass(frozen=True)
class ProcessSignals:
    """Signals used to request process termination and killing."""

    terminate: int = signal.SIGTERM
    kill: int = getattr(signal, "SIGKILL", signal.SIGTERM)


class ProcessBasedStreamMetadata:
    """Metadata for a process-based stream."""

    def __init__(
        self,
        args: Sequence[str],
        env: dict[str, str] | None = None,
        signals: ProcessSignals | None = None,
    ) -> None:
        self._args = args
        self._env = env
        self._signals = signals if signals is not None else ProcessSignals()

    @property
    def args(self) -> Sequence[str]:
        """The arguments to the process."""
        return self._args

    @property
    def env(self) -> dict[str, str] | None:
        """The environment variables for the process."""
        return self._env

    @property
    def signals(self) -> ProcessSignals:
        """The signals used to stop the process."""
        return self._signals


class ProcessBasedStream(Stream):
    """Stream based on a process."""

    def __init__(
        self,
        process: AsyncioProcess,
        signals: ProcessSignals,
    ) -> None:
        self._process = process
        self._signals = signals

    @property
    def process(self) -> AsyncioProcess:
        """The underlying process."""
        return self._process

    @override
    async def terminate(self) -> None:
        with suppress(ProcessLookupError):
            self._process.send_signal(self._signals.terminate)

    @override
    async def kill(self) -> None:
        with suppress(ProcessLookupError):
            self._process.send_signal(self._signals.kill)

    @override
    async def wait(self) -> None:
        await self._process.wait()


class ProcessBasedStreamFactory(StreamFactory[ProcessBasedStreamMetadata]):
    """Factory for ProcessBasedStream."""

    @override
    async def create(
        self,
        metadata: ProcessBasedStreamMetadata,
        stdin: IO | int | None = DEVNULL,
        stdout: IO | int | None = DEVNULL,
        stderr: IO | int | None = DEVNULL,
    ) -> ProcessBasedStream:
        env = os.environ.copy() | (metadata.env or {})

        process = await create_subprocess_exec(
            *metadata.args,
            env=env,
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
        )

        return ProcessBasedStream(process, metadata.signals)
