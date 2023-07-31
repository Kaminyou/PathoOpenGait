import typing as t
from abc import ABC, abstractmethod


class Analyzer(ABC):
    def __init__(
        self,
        pretrained_path: str,
    ):
        self.pretrained_path = pretrained_path

    @abstractmethod
    def run(
        self,
        data_root_dir: str,
        file_id: str,
    ) -> t.List[t.Dict[str, t.Any]]:
        pass
