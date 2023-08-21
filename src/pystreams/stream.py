from abc import ABC, abstractmethod
from typing import Generic, TypeVar

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
    async def create(self, metadata: StreamMetadataType) -> Stream:
        """Create a stream."""

        pass
