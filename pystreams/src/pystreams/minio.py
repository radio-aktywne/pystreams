import os
from dataclasses import dataclass
from subprocess import PIPE, Popen
from typing import AnyStr, Dict, IO, List, Optional

from pystreams.stream import ProcessBasedStream


@dataclass
class MinioNode:
    host: str
    bucket: str
    path: str


class MinioStream(ProcessBasedStream):
    def __init__(self, output: MinioNode) -> None:
        super().__init__()
        self.output = output

    def minio_args(self) -> List[str]:
        return ["mc", "pipe", f"minio/{self.output.bucket}/{self.output.path}"]

    def minio_env(self) -> Dict[str, str]:
        env = os.environ.copy()
        env["MC_HOST_minio"] = self.output.host
        return env

    def start_process(
        self,
        stdin: Optional[IO[AnyStr]] = PIPE,
        stdout: Optional[IO[AnyStr]] = PIPE,
        stderr: Optional[IO[AnyStr]] = PIPE,
    ) -> Popen:
        return Popen(
            self.minio_args(),
            env=self.minio_env(),
            stdin=stdin,
            stdout=stdout,
            stderr=stderr,
        )
