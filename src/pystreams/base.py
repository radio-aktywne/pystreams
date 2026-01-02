from abc import ABC, abstractmethod
from asyncio.subprocess import DEVNULL
from typing import IO


class Stream(ABC):
    """Base class for streams."""

    @abstractmethod
    async def terminate(self) -> None:
        """Terminate the stream gracefully."""

    @abstractmethod
    async def kill(self) -> None:
        """Kill the stream forcefully."""

    @abstractmethod
    async def wait(self) -> None:
        """Wait for the stream to finish."""


class StreamFactory[T](ABC):
    """Base class for stream factories."""

    @abstractmethod
    async def create(
        self,
        metadata: T,
        stdin: IO | int | None = DEVNULL,
        stdout: IO | int | None = DEVNULL,
        stderr: IO | int | None = DEVNULL,
    ) -> Stream:
        """Create a stream."""
