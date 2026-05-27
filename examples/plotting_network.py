# ruff: noqa

from pathlib import Path
from typing import TypedDict, NotRequired
from datetime import datetime

from tidalseis.retrieval.inventory import get_iris_inventory
from tidalseis.read_network_traces import (
    read_network_traces,
    extract_coords,
    coords_to_csv,
)
from tidalseis.visualization import plot_network_timeline


def analyze_network(network_path: str | Path):
    traces = read_network_traces(Path(network_path) / "trace_data")
    coords_to_csv(traces, Path(network_path) / "station_coords.csv")
    plot_network_timeline(traces)


analyze_network("D:/seismic_data/amery_ice_shelf/")
