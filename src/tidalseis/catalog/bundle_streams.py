"""
Functions for bundling a network of individual traces into related stream
objects that can be cataloged.
"""

from pathlib import Path

from tidalseis.load.network import (
    read_network_traces,
    link_station_trace_paths,
    flatten_station_traces,
)
from tidalseis.load.models import TraceTimePath
from tidalseis.retrieval.models import StationModel


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
