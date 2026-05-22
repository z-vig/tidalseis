from datetime import datetime
from pathlib import Path
from typing import Self

from pydantic import BaseModel


class ChannelModel(BaseModel):
    id: str
    location: str = ""


class StationModel(BaseModel):
    network: str
    id: str
    channels: dict[str, ChannelModel]
    start: datetime
    end: datetime

    @classmethod
    def from_json(cls, save_path: Path | str) -> Self:
        with open(save_path, "r") as f:
            return cls.model_validate_json(f.read())

    def to_json(self, save_path: Path | str):
        json = self.model_dump_json(indent=2)
        with open(Path(save_path).with_suffix(".json"), "w") as f:
            f.write(json)
