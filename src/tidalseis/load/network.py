"""
Collection of functions for dealing with a network of seismic stations. This
is in the format of a trace directory that contains serialized StationTrace
objects as .json files.
"""

from pathlib import Path
from datetime import datetime
from typing import overload

import obspy  # type: ignore

from tidalseis.retrieval.models import StationTraces, StationModel
from tidalseis.datetime_ops import is_time_between
import tidalseis._obspy_validation as vld
from tidalseis.catalog.preprocess import (
    PreprocessingConfig,
    PreprocessingFlag,
    preprocess_trace,
)
from tidalseis.types import PreprocessingFunc

from .models import OnDiskStation, TraceTimePath


def read_network_traces(trace_directory: str | Path) -> list[StationTraces]:
    """
    Reads a directory containing a set of .json files that are serialized
    StationTraces objects.

    Parameters
    ----------
    trace_directory: str | Path
        Path to a directory containing one or more serialized StationTraces.

    Returns
    -------
    list[StationTraces]
        List of StationTraces objects that were present in the directory.

    See Also
    --------
    `tidalseis.retrieval.traces.save_stationtraces_models()`
    """
    all_network_traces: list[StationTraces] = []
    for f in Path(trace_directory).glob("*.json"):
        all_network_traces.append(StationTraces.from_json(f))
    return all_network_traces


def link_station_trace_paths(
    traces: list[StationTraces],
    trace_directory: Path | str,
    date_fmt="%m%d%YT%H%M%S",
) -> list[OnDiskStation]:
    """
    Adds local path information to StationTraces objects in the form of
    OnDiskStation objects.
    """
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
) -> list[tuple[StationModel, TraceTimePath]]:
    """
    Each OnDiskStation object contains many TraceTimePath objects. This
    function flattens a list of OnDiskStation and puts all TraceTimePath
    objects from each OnDiskStation in a single list.

    Returns
    -------
    list[tuple[StationModel, TraceTimePath]]
        Each item in list is a tuple of the Station and a corresponding trace
        filepath.
    """
    all_traces: list[tuple[StationModel, TraceTimePath]] = []
    for sta_tr in station_traces:
        fplist = [(sta_tr.station_traces.station, i) for i in sta_tr.filepaths]
        all_traces.extend(fplist)
    return all_traces


@overload
def get_network_stream(
    trace_metadata_list: list[TraceTimePath],
    starttime: datetime,
    endtime: datetime,
    *,
    preprocessing: PreprocessingFunc | None,
) -> tuple[dict[str, obspy.Trace], obspy.Stream]: ...


@overload
def get_network_stream(
    trace_metadata_list: list[TraceTimePath],
    starttime: datetime,
    endtime: datetime,
    *,
    preprocessing: PreprocessingConfig,
) -> tuple[dict[str, obspy.Trace], obspy.Stream, PreprocessingFlag]: ...


def get_network_stream(
    trace_metadata_list: list[TraceTimePath],
    starttime: datetime,
    endtime: datetime,
    *,
    preprocessing: PreprocessingFunc | PreprocessingConfig | None,
) -> (
    tuple[dict[str, obspy.Trace], obspy.Stream]
    | tuple[dict[str, obspy.Trace], obspy.Stream, PreprocessingFlag]
):
    """
    Bundles a network of seismic traces of many different stations into one
    super stream that starts and end at a provided datetime. Optionally,
    preprocessing on the traces is applied via a preprocessing function.

    Parameters
    ----------
    trace_metadata_list: list[TraceTimePath]
        The trace metadata list needed to select which traces to load into the
        stream.
    starttime: datetime
        Start of the stream.
    endtime: datetime
        End of the stream.
    preprocessing: PreprocessingFunc | PreprocessingConfig, optional
        Custom function to apply to each trace before adding to the stream.
        --OR-- Preprocessing config options to pass to built in preprocessing
        function. Default is None and no preprocessing will be applied.

    Returns
    -------
    dict[str, obspy.Trace]
        Dictionary of all traces involved in the stream, split by station ID.
        If multiple traces are included for one station ID, they will be added
        together, concatenating their time series'.
    obspy.Stream
        The network stream containing all traces.
    PreprocessingFlag
        Only returned if the PreprocessingConfig object is provided to use the
        built-in preprocessor.
    """

    # ==== Initializing containers ====
    trace_dict: dict[str, obspy.Trace] = {}
    super_stream = obspy.Stream()

    # ==== Looping through trace metadata ====
    flag: PreprocessingFlag | None = None
    for trace_md in trace_metadata_list:
        # Only look at traces between start and end.
        if not is_time_between(starttime, endtime, trace_md.start):
            continue

        # Read in .mseed file as an obspy stream with only one trace.
        stream = vld.validate_stream(obspy.read(trace_md.path))
        if stream.count() > 1:
            raise ValueError("Single trace streams for now...")
        trace = vld.validate_trace(stream.traces[0])

        if preprocessing is None:
            pass
        elif callable(preprocessing):
            trace = preprocessing(trace)
        elif isinstance(preprocessing, PreprocessingConfig):
            flag, trace = preprocess_trace(trace, preprocessing)

        super_stream += trace
        if trace_dict.get(trace.id) is None:
            trace_dict[trace.id] = trace
        else:
            trace_dict[trace.id] += trace
    print(f"Super stream contains {super_stream.count()} traces")

    if flag is None:
        return trace_dict, super_stream
    return trace_dict, super_stream, flag
