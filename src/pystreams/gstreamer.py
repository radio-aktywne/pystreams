from collections.abc import Sequence
from typing import Any

from pystreams.process import ProcessBasedStreamMetadata


def _build_args_from_global_options(options: dict[str, Any] | None) -> list[str]:
    options = options or {}
    args = []

    for key, value in options.items():
        if value is False:
            pass
        elif value is True or value is None:
            args = args + [f"--{key}"]
        elif isinstance(value, str):
            args = args + [f"--{key}", value]
        else:
            try:
                for v in value:
                    args = args + [f"--{key}", str(v)]
            except TypeError:
                args = args + [f"--{key}", str(value)]

    return args


def _map_value(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _build_args_from_node_properties(properties: dict[str, Any] | None) -> list[str]:
    properties = properties or {}
    return [f"{key}={_map_value(value)}" for key, value in properties.items()]


class GStreamerNode:
    """A node in an GStreamer stream."""

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
    """Metadata for an GStreamer stream."""

    def __init__(
        self,
        nodes: GStreamerNode | Sequence[GStreamerNode],
        executable: str = "gst-launch-1.0",
        options: dict[str, Any] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        nodes = nodes if isinstance(nodes, Sequence) else [nodes]

        args = [executable]
        args = args + _build_args_from_global_options(options)

        for i, node in enumerate(nodes):
            args = args + [node.element]
            args = args + _build_args_from_node_properties(node.properties)

            if i < len(nodes) - 1:
                args = args + ["!"]

        super().__init__(args, env)
