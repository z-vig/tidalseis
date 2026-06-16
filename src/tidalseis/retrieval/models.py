from datetime import datetime
from pathlib import Path
from typing import Self
from uuid import uuid4, UUID

from pydantic import BaseModel, computed_field, ConfigDict
import numpy as np
from obspy.core.inventory import Station, Channel  # type: ignore
from obspy import Trace  # type: ignore

import tidalseis._obspy_validation as vld


class ChannelModel(BaseModel):
    code: str
    start: datetime
    end: datetime
    sample_rate: float

    @classmethod
    def from_channel(cls, channel: Channel) -> Self:
        avail = vld.validate_data_availability(channel.data_availability)
        return cls(
            code=channel.code,
            start=vld.validate_utc(avail.start).datetime,
            end=vld.validate_utc(avail.end).datetime,
            sample_rate=vld.validate_sample_rate(channel.sample_rate),
        )

    @classmethod
    def from_json(cls, fp: Path | str) -> Self:
        with open(fp, "r") as f:
            return cls.model_validate_json(f.read())


class StationModel(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    lat: float
    long: float
    elev: float

    @classmethod
    def from_station(cls, station: Station) -> Self:
        return cls(
            code=station.code,
            lat=station.latitude,
            long=station.longitude,
            elev=station.elevation,
        )


class DeploymentTime(BaseModel):
    start: datetime
    end: datetime
    elapsed: str


class TraceModel(BaseModel):
    id: UUID = uuid4()
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


def make_trace_metadata(trace: Trace) -> TraceModel:
    meta = vld.validate_stats(trace.meta)

    start = meta.starttime.datetime
    end = meta.endtime.datetime
    return TraceModel(
        nsamples=trace.count(),
        time=DeploymentTime(start=start, end=end, elapsed=str(end - start)),
        data_type=str(trace.data.dtype),
        seed_id=trace.get_id(),
    )


class StationTraces(BaseModel):
    """
    Container for the traces that can be found at one station over one channel.
    """

    station: StationModel
    channel: ChannelModel
    traces: list[TraceModel]

    @classmethod
    def from_json(cls, fp: str | Path) -> Self:
        with open(fp, "r") as f:
            return cls.model_validate_json(f.read())

    def to_json(self, save_fp: str | Path) -> None:
        with open(Path(save_fp).with_suffix(".json"), "w") as f:
            f.write(self.model_dump_json(indent=2))
