from pathlib import Path
from datetime import datetime, timedelta
from collections.abc import Callable
from typing import Optional, Literal
from functools import partial, reduce
from operator import add

from tqdm import tqdm
import numpy as np
from obspy import UTCDateTime, Trace, Stream  # type: ignore
from obspy.core.inventory import Channel, Station  # type: ignore
from obspy.clients.fdsn import Client  # type: ignore
from obspy.clients.fdsn.header import FDSNNoDataException  # type: ignore

from .models import (
    ChannelModel,
    StationModel,
    TraceModel,
    make_trace_metadata,
)
import tidalseis.obspy_validation as vld


def to_datetime(date):
    """
    Converts a numpy datetime64 object to a python datetime object
    Input:
      date - a np.datetime64 object
    Output:
      DATE - a python datetime object
    """
    timestamp = (date - np.datetime64("1970-01-01T00:00:00")) / np.timedelta64(
        1, "s"
    )
    return datetime.fromtimestamp(timestamp)


def narrow_channel(val: Channel | Path | str | ChannelModel) -> ChannelModel:
    if isinstance(val, Channel):
        cha = ChannelModel.from_channel(val)
    elif isinstance(val, ChannelModel):
        cha = val
    else:
        cha = ChannelModel.from_json(val)
    return cha


def narrow_station(val: Station | StationModel) -> StationModel:
    if isinstance(val, Station):
        sta = StationModel.from_station(val)
    else:
        sta = val
    return sta


def split_timespan(
    start: datetime, end: datetime, split_length: timedelta
) -> np.ndarray:
    """
    Splits a timespan into start/end chunks

    Returns
    -------
    np.ndarray
        Split up array, where axis 1 is the number of splits and axis 2 is "
        "two columns; start times and end times, respectively
    """
    start_times = np.arange(
        str(start),
        str(end),
        np.timedelta64(split_length),
        dtype="datetime64[s]",
    )
    end_times = np.arange(
        str(start + split_length),
        str(end + split_length),
        np.timedelta64(split_length),
        dtype="datetime64[s]",
    )
    return np.stack([start_times, end_times], axis=-1)


def check_for_iris_data(
    network_id: str,
    station_id: str,
    location_id: str,
    channel_id: str,
    span: tuple[datetime, datetime],
    client: Client = Client("Earthscope"),
) -> Stream | None:
    """
    Checks for data from a client over a timespan. Returns none if no data
    exists for this timespan.
    """
    try:
        stream = vld.validate_stream(
            client.get_waveforms(
                network=network_id,
                station=station_id,
                location=location_id,
                channel=channel_id,
                starttime=UTCDateTime(span[0]),
                endtime=UTCDateTime(span[1]),
            )
        )
    except FDSNNoDataException:
        return None

    return stream


def split_large_trace(
    tr: Trace,
    split_length: timedelta,
    *,
    starttime: Optional[datetime] = None,
    endtime: Optional[datetime] = None,
    trace_model: Optional[TraceModel] = None,
) -> tuple[list[Trace], list[TraceModel]]:
    """Splits a long trace into parts of a specified length"""
    # ==== Validating inputs ====
    if (starttime is None) or (endtime is None):
        if trace_model is None:
            trace_model = make_trace_metadata(tr)
        tr_start, tr_end = trace_model.time.start, trace_model.time.end
    else:
        tr_start, tr_end = starttime, endtime

    # ==== Initializing collector ====
    trace_list: list[Trace] = []
    model_list: list[TraceModel] = []

    # ==== Creating split timespan iterator ====
    sub_spans = split_timespan(tr_start, tr_end, split_length)

    # ==== Looping through all sub timespans ====
    for n in range(sub_spans.shape[0]):
        sub_start_dt = to_datetime(sub_spans[n, 0])
        sub_end_dt = to_datetime(sub_spans[n, 1])
        sub_tr = tr.slice(UTCDateTime(sub_start_dt), UTCDateTime(sub_end_dt))
        sub_tr_model = make_trace_metadata(sub_tr)
        if sub_tr.count() == 0:
            continue
        trace_list.append(sub_tr)
        model_list.append(sub_tr_model)

    return trace_list, model_list


def _save_single_trace(
    trace: Trace,
    trace_model: TraceModel,
    save_directory: str | Path,
    date_fmt: str = "%m%d%YT%H%M%S",
    replace: bool = False,
) -> None:
    """Saves a single trace."""
    # ==== Creating save path name ====
    sv_path = (
        Path(save_directory) / f"{trace_model.time.start.strftime(date_fmt)}_"
        f"{trace_model.time.end.strftime(date_fmt)}"
    )

    # ==== Exiting if the file exists and replace is False ====
    if sv_path.exists() and not replace:
        print(f"{sv_path} already exists.")
        return

    # ==== Writing to disk...===
    trace.write(
        sv_path.with_suffix(".mseed"),
        format="MSEED",
    )


def save_trace(
    trace: Trace | list[Trace],
    trace_model: TraceModel | list[TraceModel],
    save_directory: Path | str,
    station_id: str,
    date_fmt: str = "%m%d%YT%H%M%S",
    replace: bool = False,
) -> None:
    """
    Saves either a single trace or a list of traces.
    """
    # ==== Handling save directory ====
    sv_subdir = Path(save_directory) / station_id
    if not sv_subdir.exists():
        sv_subdir.mkdir(parents=True)

    if isinstance(trace, Trace) and isinstance(trace_model, TraceModel):
        _save_single_trace(trace, trace_model, sv_subdir, date_fmt, replace)
    elif isinstance(trace, list) and isinstance(trace_model, list):
        for tr, tr_model in zip(trace, trace_model):
            _save_single_trace(tr, tr_model, sv_subdir, date_fmt, replace)


def _noop_save(
    trace: Trace | list[Trace],
    trace_model: TraceModel | list[TraceModel],
    *args,
) -> None:
    """
    A non-operation save-like function.
    """
    return


def _handle_trace_splitting(
    tr: Trace,
    span_list: list[tuple[datetime, datetime]],
    trace_list: list[TraceModel],
) -> tuple[list[Trace], list[TraceModel]]:
    tr = vld.validate_trace(tr)
    tr_model = make_trace_metadata(tr)
    span_list.append((tr_model.time.start, tr_model.time.end))
    sub_traces, sub_models = split_large_trace(
        tr, timedelta(days=1), trace_model=tr_model
    )
    trace_list.extend(sub_models)
    return sub_traces, sub_models


def load_traces(
    *,
    network_id: str,
    network_start: datetime,
    network_end: datetime,
    location_id: str,
    channel_id: str,
    station_id: str,
    trace_mode: Literal["separate", "add"] = "separate",
    save_directory: Path | str | None = None,
    date_fmt: str = "%m%d%YT%H%M%S",
    replace: bool = False,
) -> tuple[np.ndarray, list[TraceModel]]:
    """
    Loads seismic traces from a single station and a single channel from a
    seismic network and optionally saves them to disk.

    Parameters
    ----------
    network_id: str
        Network ID string.
    network_start: datetime
        Start time for the entire network deployment.
    network_end: datetime
        End time for the entire network deployment.
    location_id: str
        SEED Location ID string.
    channel_id: str
        SEED channel ID string.
    station_id: str
        Name of the seismic station within the network.
    trace_mode: "separate" or "add", optional:
        Determines how to save multi-trace streams. If "separate", distinct
        streams will be saved to different files so that each saved trace is
        100% continuous. If "add", the traces in the stream will be added and
        gaps marked by the fill value '0' will be included in the file.
    save_directory, optional:
        Directory into which the traces and the metadata will be saved.
        Default is None, and the data will not be saved to disk.
    date_fmt: str, optional
        Formatting string for the datetime name of each seismic trace.
    replace: bool, optional
        Whether to delete existing seismic data files. Default is False.

    Returns
    -------
    np.ndarray
        Array of timespans for the traces. Each row is a trace, column 1 is
        the start time of the span and column 2 is the end time of the span.
    list[TraceModel]
        List of trace model objects for each trace that was loaded.

    Notes
    -----
    ### Trace Splitting
    Traces will be saved in small chunks. First, the station lifespan is split
    into large timespans (20 days). These will each be loaded and checked for
    existing data. From there, these large timespans will be split into smaller
    traces ~1 UTC day long. If there are multiple distinct traces within a
    single day, they will be saved individually.

    ### Save Conventions
    Within the save directory that is input by the user, a subdirectory with
    the station name will be created and trace data will be saved within
    this subdirectory. The traces are saved in the [.mseed format](https://www.gfz.de/en/section/geophysical-imaging/infrastructure/geophysical-instrument-pool-potsdam-gipp/documents/data-format)
    with a .json metadata file at the same level as the subdirectory.
    """
    # ==== Initializing Client ====
    client = Client("Earthscope")

    # ==== Initializing collectors ====
    span_list: list[tuple[datetime, datetime]] = []
    trace_list: list[TraceModel] = []

    # ==== Initializing save function ====\
    save_trace_to_dir: Callable[
        [Trace | list[Trace], TraceModel | list[TraceModel]], None
    ]
    if save_directory is not None:
        save_trace_to_dir = partial(
            save_trace,
            save_directory=save_directory,
            station_id=station_id,
            date_fmt=date_fmt,
            replace=replace,
        )
    else:
        save_trace_to_dir = _noop_save

    day_by_day = split_timespan(network_start, network_end, timedelta(days=20))

    pbar = tqdm(
        range(day_by_day.shape[0]),
        desc=f"Loading station: {station_id}",
        disable=False,
    )

    for n in pbar:
        # Formatting timespan
        span = (to_datetime(day_by_day[n, 0]), to_datetime(day_by_day[n, 1]))

        # Checking for data existence
        stream = check_for_iris_data(
            network_id, station_id, location_id, channel_id, span, client
        )
        if not stream:
            continue  # Cuts the iteration if data not found.

        if trace_mode == "separate":
            for tr in stream.traces:
                sub_traces, sub_models = _handle_trace_splitting(
                    tr, span_list, trace_list
                )
                save_trace_to_dir(sub_traces, sub_models)
        elif trace_mode == "add":
            tr = reduce(add, stream.traces)
            sub_traces, sub_models = _handle_trace_splitting(
                tr, span_list, trace_list
            )
            save_trace_to_dir(sub_traces, sub_models)

    return np.array(span_list), trace_list
