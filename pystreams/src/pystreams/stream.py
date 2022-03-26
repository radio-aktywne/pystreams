from abc import ABC, abstractmethod
from subprocess import PIPE, Popen
from threading import Event, Lock, Thread
from typing import AnyStr, IO, Optional


class Stream(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def end(self) -> None:
        pass

    @abstractmethod
    def wait(self) -> bool:
        pass


class ProcessBasedStream(Stream, ABC):
    def __init__(self) -> None:
        self.lock = Lock()
        self.ended_event = Event()
        self.process = None

    @abstractmethod
    def start_process(
        self,
        stdin: Optional[IO[AnyStr]] = PIPE,
        stdout: Optional[IO[AnyStr]] = PIPE,
        stderr: Optional[IO[AnyStr]] = PIPE,
    ) -> Popen:
        pass

    def monitor(self) -> None:
        self.process.wait()
        with self.lock:
            self.process = None
            self.ended_event.set()
            self.ended_event.clear()

    def start(self) -> None:
        with self.lock:
            if self.process is not None:
                raise RuntimeError("Stream already started.")
            self.process = self.start_process()
            Thread(target=self.monitor).start()

    def end(self) -> None:
        with self.lock:
            if self.process is None:
                return
            self.process.kill()

    def wait(self) -> None:
        self.ended_event.wait()
