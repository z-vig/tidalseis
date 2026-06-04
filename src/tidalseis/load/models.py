from datetime import datetime, timedelta
from dataclasses import dataclass
from pathlib import Path

from obspy import Trace, read  # type: ignore

from tidalseis.retrieval.models import StationTraces
import tidalseis._obspy_validation as vld


def is_time_between(
    begin_time: datetime,
    end_time: datetime,
    check_time: datetime | None = None,
) -> bool:
    # If check time is not given, default to current UTC time
    if check_time is None:
        check_time = datetime.now()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


@dataclass
class TraceTimePath:
    start: datetime
    end: datetime
    path: Path


@dataclass
class OnDiskStation:
    station_traces: StationTraces
    filepaths: list[TraceTimePath]

    @property
    def cum_start(self) -> datetime:
        start_time_list = [i.start for i in self.filepaths]
        return min(start_time_list)

    @property
    def cum_end(self) -> datetime:
        end_time_list = [i.end for i in self.filepaths]
        return max(end_time_list)

    @property
    def cum_elapsed(self) -> timedelta:
        return self.cum_end - self.cum_start

    def load_data(
        self, start_time: datetime, end_time: datetime
    ) -> list[Trace]:
        """Loads a single trace stream."""
        loaded_traces: list[Trace] = []
        for ttp in self.filepaths:
            if not is_time_between(start_time, end_time, ttp.start):
                continue
            tr = vld.validate_trace(read(ttp.path))
            loaded_traces.append(tr)
        return loaded_traces
