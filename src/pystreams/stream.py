from abc import ABC, abstractmethod
from asyncio.subprocess import DEVNULL
from typing import IO, AnyStr, Generic, TypeVar

StreamMetadataType = TypeVar("StreamMetadataType")


class Stream(ABC):
    """A handle to a running stream."""

    @abstractmethod
    async def terminate(self) -> None:
        """Terminate the stream gracefully."""

        pass

    @abstractmethod
    async def kill(self) -> None:
        """Kill the stream forcefully."""

        pass

    @abstractmethod
    async def wait(self) -> None:
        """Wait for the stream to finish."""

        pass


class StreamFactory(ABC, Generic[StreamMetadataType]):
    """A factory for creating streams."""

    @abstractmethod
    async def create(
        self,
        metadata: StreamMetadataType,
        stdin: IO[AnyStr] | None = DEVNULL,
        stdout: IO[AnyStr] | None = DEVNULL,
        stderr: IO[AnyStr] | None = DEVNULL,
    ) -> Stream:
        """Create a stream."""

        pass
