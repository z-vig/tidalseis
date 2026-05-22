from datetime import datetime
from pathlib import Path
from typing import Self

from pydantic import BaseModel, computed_field
import numpy as np
from obspy.core.inventory.station import Station  # type: ignore
from obspy import Trace  # type: ignore

import tidalseis.obspy_validation as vld


class StationCoordinates(BaseModel):
    lat: float
    long: float
    elev: float


class DeploymentTime(BaseModel):
    start: datetime
    end: datetime
    elapsed: str


class TraceMetaData(BaseModel):
    coords: StationCoordinates
    nsamples: int
    time: DeploymentTime
    data_type: str
    seed_id: str

    @computed_field
    def size(self) -> float:
        return (self.nsamples * np.dtype(self.data_type).itemsize) / 1e6

    @classmethod
    def from_json(cls, load_fp: str | Path) -> Self:
        with open(load_fp, "r") as f:
            return cls.model_validate_json(f.read())

    def to_json(self, save_fp: str | Path) -> None:
        with open(Path(save_fp).with_suffix(".json"), "w") as f:
            f.write(self.model_dump_json(indent=2))


def make_trace_metadata(trace: Trace, station: Station) -> TraceMetaData:
    meta = vld.validate_stats(trace.meta)
    start = meta.starttime.datetime
    end = meta.endtime.datetime
    return TraceMetaData(
        coords=StationCoordinates(
            lat=station.latitude,
            long=station.longitude,
            elev=station.elevation,
        ),
        nsamples=trace.count(),
        time=DeploymentTime(start=start, end=end, elapsed=str(end - start)),
        data_type=str(trace.data.dtype),
        seed_id=trace.get_id(),
    )
