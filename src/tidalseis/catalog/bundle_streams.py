"""
Functions for bundling a network of individual traces into related stream
objects that can be cataloged.
"""

from pathlib import Path
from functools import partial
from datetime import datetime
from dataclasses import dataclass
from typing import overload

import numpy as np
import obspy  # type: ignore

from .preprocess import PreprocessingConfig, PreprocessingFlag
from .default_settings import DEFAULT_PREPROCESSING
from tidalseis.load.network import (
    read_network_traces,
    link_station_trace_paths,
    flatten_station_traces,
    get_network_stream,
)
from tidalseis.load.models import TraceTimePath
from tidalseis.retrieval.models import StationModel
from tidalseis.datetime_ops import (
    is_time_between,
    to_datetime,
    chunk_long_timespan,
)


@dataclass
class BundledStream:
    nactive: int
    start_time: datetime
    end_time: datetime
    _stream: obspy.Stream | None = None
    preprocessing_flag: PreprocessingFlag = PreprocessingFlag.NONE

    def _make_time_string(self, fmt: str) -> str:
        return f"{self.start_time.strftime(fmt)}_{self.end_time.strftime(fmt)}"

    @property
    def file_name(self) -> str:
        return self._make_time_string("%d%m%YT%H%M%S")

    @property
    def stream(self) -> obspy.Stream:
        if self._stream is None:
            raise AttributeError("Stream has not been set.")
        return self._stream

    @stream.setter
    def stream(self, val: obspy.Stream) -> None:
        self._stream = val

    def __str__(self) -> str:
        return self._make_time_string("%B %d %Y")

    def save(self, save_directory: str | Path) -> None:
        """
        Saves the stream to an mseed within the specified directory.
        """
        sv_filepath = Path(save_directory, self.file_name).with_suffix(
            ".mseed"
        )
        self.stream.write(sv_filepath, format="MSEED")


def get_trace_model_list(
    base_directory: str | Path,
) -> tuple[list[StationModel], list[TraceTimePath]]:
    """
    Pulls all individual trace models associated with a seismic network. These
    models contain pertinent metadata for all traces including station info,
    start/end time and local file location for the data.

    Parameters
    ----------
    base_directory: str | Path
        File path to the netwrok trace directory.

    Returns
    -------
    list[StationModel]
        List of all stations. Stations may repeat as multiple traces are found
        per station.
    list[TraceTimePath]
        List of all traces, with time and filepath info in the object.
    """
    # ==== Reads all saved station traces====
    station_traces = read_network_traces(base_directory)
    # ==== Links station traces to local filepath info ====
    station_traces_linked = link_station_trace_paths(
        station_traces, base_directory
    )
    # ==== List of all traces preceded by the relevant station model ====
    all_traces = flatten_station_traces(station_traces_linked)

    # ==== Station models only. Stations will repeat for multi-traces ====
    stations_only = [i[0] for i in all_traces]

    # ==== Trace time paths ====
    traces_only = [i[1] for i in all_traces]

    return stations_only, traces_only


def _check_timestamp_for_existing_traces(
    trace_time_paths: list[TraceTimePath],
    begin_time: datetime,
    end_time: datetime,
) -> int:
    check_range_for_traces = partial(
        is_time_between, begin_time=begin_time, end_time=end_time
    )
    all_check = np.array(
        [check_range_for_traces(check_time=i.start) for i in trace_time_paths]
    )
    return int(np.count_nonzero(all_check))


def bundle_stream(
    trace_time_paths: list[TraceTimePath],
    begin_time: datetime | np.datetime64,
    end_time: datetime | np.datetime64,
    preprocessing_config: PreprocessingConfig = DEFAULT_PREPROCESSING,
) -> BundledStream | None:
    """
    Given a list of trace time path objects and a start and end time, select
    all traces from all stations within the given time range, run preprocessing
    and return a bundled stream object.

    Parameters
    ----------
    trace_time_paths: list[TraceTimePath]
        List of trace time paths for a network.
    begin_time: datetime | np.datetime64
        Start of bundle.
    end_time: datetime | np.datetime64
        End of bundle.
    preprocessing_config: PreprocessingConfig, optional
        Preprocessing configuration. Defaults to package default.

    See Also
    --------
    `tidalseis.catalog.preprocess`
        For preprocessing models.
    `tidalseis.catalog.default_settings`
        Default preprocessing configuration is stored here.
    """
    begin_time = to_datetime(begin_time)
    end_time = to_datetime(end_time)

    nactive = _check_timestamp_for_existing_traces(
        trace_time_paths, begin_time, end_time
    )

    if nactive == 0:
        return None

    _, network_stream, flag = get_network_stream(
        trace_time_paths,
        begin_time,
        end_time,
        preprocessing=preprocessing_config,
    )

    bundled_stream = BundledStream(
        nactive, begin_time, end_time, network_stream, flag
    )

    start_str, end_str = str(bundled_stream).split("_")

    print(f"{nactive} traces were found from {start_str} --> {end_str}")

    return bundled_stream


@overload
def bundle_network(
    traces: list[TraceTimePath],
    network_start: datetime,
    network_end: datetime,
    save_directory: str | Path,
    preprocessing_config: PreprocessingConfig = DEFAULT_PREPROCESSING,
) -> None: ...


@overload
def bundle_network(
    traces: Path | str,
    network_start: datetime,
    network_end: datetime,
    save_directory: str | Path,
    preprocessing_config: PreprocessingConfig = DEFAULT_PREPROCESSING,
) -> tuple[list[StationModel], list[TraceTimePath]]: ...


def bundle_network(
    traces: Path | str | list[TraceTimePath],
    network_start: datetime,
    network_end: datetime,
    save_directory: str | Path,
    preprocessing_config: PreprocessingConfig = DEFAULT_PREPROCESSING,
    overwrite: bool = False,
) -> tuple[list[StationModel], list[TraceTimePath]] | None:
    """
    Bundles all streams in a network and saves them as a directory of .mseed
    files.

    Parameters
    ----------
    trace_time_paths: list[TraceTimePath]
        List of trace time path objects for a network.
    network_start: datetime
        Start of network data.
    network_end: datetime
        End of network data.
    save_directory: str | Path
        Directory to save bundled streams to.
    """
    if not (save_directory := Path(save_directory)).exists():
        save_directory.mkdir(parents=True)
    return_val = None
    if isinstance(traces, str) or isinstance(traces, Path):
        stations, traces = get_trace_model_list(Path(traces))
        return_val = (stations, traces)

    start_list, end_list = chunk_long_timespan(network_start, network_end)
    for s_np, e_np in zip(start_list, end_list):
        s, e = to_datetime(s_np), to_datetime(e_np)
        nactive = _check_timestamp_for_existing_traces(traces, s, e)
        if nactive == 0:
            continue

        stream = BundledStream(nactive, s, e)

        if (
            Path(save_directory, stream.file_name)
            .with_suffix(".mseed")
            .exists()
            and not overwrite
        ):
            print(
                f"{Path(save_directory, stream.file_name).with_suffix(".mseed")} already exists."
            )
            continue

        _, network_stream, flag = get_network_stream(
            traces, s, e, preprocessing=preprocessing_config
        )

        stream.stream = network_stream
        stream.preprocessing_flag = flag
        stream.save(Path(save_directory))

    return return_val
