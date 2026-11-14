from collections.abc import Iterator
from typing import Any


class Escaper:
    """Escaper for special characters."""

    def __init__(self, escapes: str, prefix: str = "\\") -> None:
        self._table = str.maketrans({c: f"{prefix}{c}" for c in escapes})

    def escape(self, value: str) -> str:
        """Escape a string."""
        return value.translate(self._table)


class CommandOptionsBuilder:
    """Builder for command options."""

    def __init__(
        self,
        *,
        escapes: str | None = None,
        flags: bool = True,
        prefix: str | None = None,
        repeat: bool = True,
        separator: str | None = None,
    ) -> None:
        self._escaper = Escaper(escapes or "")
        self._flags = flags
        self._prefix = prefix or ""
        self._repeat = repeat
        self._separator = separator

    def _iterate(self, options: dict[str, Any]) -> Iterator[tuple[str, str | None]]:
        for key, value in options.items():
            if self._flags and value is False:
                continue

            if self._flags and (value is True or value is None):
                yield key, None
            elif isinstance(value, bool):
                yield key, str(value).lower()
            elif isinstance(value, str) or not self._repeat:
                yield key, str(value)
            else:
                try:
                    values = iter(value)
                except TypeError:
                    yield key, str(value)
                else:
                    for item in values:
                        yield key, str(item)

    def build(self, options: dict[str, Any] | None) -> list[str]:
        """Build command arguments."""
        args = []

        for key, value in self._iterate(options or {}):
            name = f"{self._prefix}{key}"

            if value is None:
                args = [*args, name]
            elif self._separator is None:
                args = [*args, name, value]
            else:
                args = [*args, f"{name}{self._separator}{value}"]

        return [self._escaper.escape(arg) for arg in args]
