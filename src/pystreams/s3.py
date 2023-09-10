from pystreams.process import ProcessBasedStreamMetadata


class S3StreamMetadata(ProcessBasedStreamMetadata):
    """Metadata for a stream piped to S3 bucket."""

    def __init__(
        self,
        endpoint: str,
        user: str,
        password: str,
        bucket: str,
        path: str,
        env: dict[str, str] | None = None,
    ) -> None:
        env = env or {}

        args = ["s5cmd", "pipe", f"s3://{bucket}/{path}"]
        env = env | {
            "S3_ENDPOINT_URL": endpoint,
            "AWS_ACCESS_KEY_ID": user,
            "AWS_SECRET_ACCESS_KEY": password,
        }

        super().__init__(args, env)
