from pathlib import Path
from datetime import datetime, timedelta

import numpy as np

from tidalseis.retrieval.models import StationTraces


def read_network_traces(trace_directory: str | Path) -> list[StationTraces]:
    all_network_traces: list[StationTraces] = []
    for f in Path(trace_directory).glob("*.json"):
        all_network_traces.append(StationTraces.from_json(f))
    return all_network_traces


def extract_coords(
    traces: list[StationTraces],
) -> tuple[np.ndarray, list[str]]:
    coord_arr = np.empty((len(traces), 3), dtype=np.float32)
    row_names: list[str] = []
    for n, tr in enumerate(traces):
        coord_arr[n, :] = (tr.station.lat, tr.station.long, tr.station.elev)
        row_names.append(tr.station.code)
    return coord_arr, row_names


def consolidate_span_arr(
    a: np.ndarray, threshold: timedelta = timedelta(seconds=1)
) -> np.ndarray:
    consolidated = []
    current_start, current_end = a[0, :]
    for next_start, next_end in a[1:, :]:
        gap = next_start - current_end
        if gap <= threshold:
            if next_end > current_end:
                current_end = next_end
        else:
            consolidated.append([current_start, current_end])
            current_start = next_start
            current_end = next_end

    consolidated.append([current_start, current_end])

    return np.array(consolidated, dtype=a.dtype)


def extract_timelines(
    traces: list[StationTraces],
) -> dict[str, np.ndarray]:
    station_timelines: dict[str, np.ndarray] = {}
    for tr in traces:
        time_span_list: list[tuple[datetime, datetime]] = []
        for i in tr.traces:
            time_span_list.append((i.time.start, i.time.end))
        time_span_arr = consolidate_span_arr(np.array(time_span_list))
        station_timelines[tr.station.code] = time_span_arr
    return station_timelines


def extract_stations(traces: list[StationTraces]) -> list[str]:
    station_names = set()
    for tr in traces:
        station_names.add(tr.station.code)
    return list(station_names)


def coords_to_csv(traces: list[StationTraces], save_fp: str | Path) -> None:
    coords, row_names = extract_coords(traces)
    with open(save_fp, "w") as f:
        f.write("StationName, Latitude, Longitude, Elevation\n")
        for n in range(coords.shape[0]):
            row = ",".join([str(i) for i in coords[n, :]])
            f.write(f"{row_names[n]},{row}\n")
