from typing import IO, AnyStr

from pystreams.process import ProcessBasedStreamMetadata


class MinioStreamMetadata(ProcessBasedStreamMetadata):
    """Metadata for a Minio stream."""

    def __init__(
        self,
        host: str,
        bucket: str,
        path: str,
        env: dict[str, str] | None = None,
        stdin: IO[AnyStr] | None = None,
        stdout: IO[AnyStr] | None = None,
        stderr: IO[AnyStr] | None = None,
    ) -> None:
        env = env or {}

        args = ["mc", "pipe", f"minio/{bucket}/{path}"]
        env = env | {"MC_HOST_minio": host}

        super().__init__(args, env, stdin, stdout, stderr)
