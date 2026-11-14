from collections.abc import Sequence
from typing import Any

from pystreams.process import ProcessBasedStreamMetadata
from pystreams.utils import CommandOptionsBuilder


class GStreamerNode:
    """Node in a GStreamer stream."""

    def __init__(self, element: str, properties: dict[str, Any] | None = None) -> None:
        self._element = element
        self._properties = properties

    @property
    def element(self) -> str:
        """The element of the node."""
        return self._element

    @property
    def properties(self) -> dict[str, Any] | None:
        """The properties of the node."""
        return self._properties


class GStreamerStreamMetadata(ProcessBasedStreamMetadata):
    """Metadata for a GStreamer stream."""

    def __init__(
        self,
        nodes: GStreamerNode | Sequence[GStreamerNode],
        executable: str = "gst-launch-1.0",
        options: dict[str, Any] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        nodes = nodes if isinstance(nodes, Sequence) else [nodes]

        builder = CommandOptionsBuilder(prefix="--")
        args = [executable, *builder.build(options)]

        builder = CommandOptionsBuilder(flags=False, repeat=False, separator="=")
        for i, node in enumerate(nodes):
            args = [*args, node.element, *builder.build(node.properties)]

            if i < len(nodes) - 1:
                args = [*args, "!"]

        super().__init__(args, env)
