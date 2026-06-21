from datetime import datetime, timedelta
from pathlib import Path
from typing import Self

from pydantic import BaseModel, computed_field
import numpy as np


class EventData(BaseModel):
    event_start: datetime
    event_duration: float
    stations: list[str]

    @computed_field
    def event_end(self) -> datetime:
        return self.event_start + timedelta(self.event_duration)


class CatalogModel(BaseModel):
    events: list[EventData]

    @computed_field
    def nevents(self) -> int:
        return len(self.events)

    def get_relative_times(self, anchor_time: datetime) -> np.ndarray:
        return np.array(
            [
                (i.event_start - anchor_time).total_seconds()
                for i in self.events
            ]
        )

    def to_json(self, save_fp: Path | str) -> None:
        with open(save_fp, "w") as f:
            f.write(self.model_dump_json(indent=2))

    @classmethod
    def from_json(cls, json_fp: Path | str) -> Self:
        with open(json_fp, "r") as f:
            return cls.model_validate_json(f.read())
