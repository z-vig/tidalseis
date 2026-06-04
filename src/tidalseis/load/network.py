from pathlib import Path

from tidalseis.retrieval.models import StationTraces
from .models import OnDiskStation, TraceTimePath


def read_network_traces(trace_directory: str | Path) -> list[StationTraces]:
    all_network_traces: list[StationTraces] = []
    for f in Path(trace_directory).glob("*.json"):
        all_network_traces.append(StationTraces.from_json(f))
    return all_network_traces


def link_station_trace_paths(
    traces: list[StationTraces],
    trace_directory: Path | str,
    date_fmt="%m%d%YT%H%M%S",
) -> list[OnDiskStation]:
    station_groups: list[OnDiskStation] = []
    for sta_tr in traces:
        ttp_list: list[TraceTimePath] = []
        for tr in sta_tr.traces:
            name = (
                f"{tr.time.start.strftime(date_fmt)}_"
                f"{tr.time.end.strftime(date_fmt)}"
            )
            path = Path(trace_directory) / sta_tr.station.code / name
            ttp_list.append(
                TraceTimePath(
                    tr.time.start, tr.time.end, path.with_suffix(".mseed")
                )
            )
        station_groups.append(OnDiskStation(sta_tr, ttp_list))
    return station_groups


def flatten_station_traces(
    station_traces: list[OnDiskStation],
) -> list[TraceTimePath]:
    all_traces: list[TraceTimePath] = []
    for sta_tr in station_traces:
        all_traces.extend(sta_tr.filepaths)
    return all_traces
