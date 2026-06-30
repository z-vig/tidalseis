from pathlib import Path

from tidalseis.load.network import read_network_traces
from tidalseis.load.extract_info import coords_to_csv


def get_locations(trace_directory: str | Path):
    traces = read_network_traces(trace_directory)
    coords_to_csv(traces, Path(trace_directory).parent / "station_coords.csv")


get_locations("D:/seismic_data/drris/trace_data/")
