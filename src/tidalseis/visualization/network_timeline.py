"""
Creats a plot of the deployment timeline for a seismic network.
"""

from dataclasses import dataclass

import cmap
import matplotlib.pyplot as plt
import matplotlib.colors as mcolor
import numpy as np

from tidalseis.retrieval.models import StationTraces
from tidalseis.read_network_traces import extract_stations, extract_timelines


@dataclass
class TimelinePlotComponents:
    timelines: dict[str, np.ndarray]
    stations: list[str]

    def __post_init__(self) -> None:
        if (t_len := len(self.timelines)) != (s_len := len(self.stations)):
            raise ValueError(f"Invalid plot components: {t_len}, {s_len}")


def get_plot_components(traces: list[StationTraces]) -> TimelinePlotComponents:
    """
    Creates a container for station traces to be used in plotting.
    """
    return TimelinePlotComponents(
        extract_timelines(traces), extract_stations(traces)
    )


def sort_stations_by_start_time(
    timeline_dict: dict[str, np.ndarray],
) -> list[str]:
    return [
        i[0]
        for i in sorted(
            timeline_dict.items(), key=lambda x: np.min(x[1][:, 0])
        )
    ]


def plot_network_timeline(traces: list[StationTraces]) -> None:
    """
    Plots out all station activity over a network, organized by station start
    time.
    """
    components = get_plot_components(traces)
    sorted_stations = sort_stations_by_start_time(components.timelines)

    # ==== Initializing plot ====
    f, ax = plt.subplots(figsize=(10, 8))
    clrmap = cmap.Colormap("seaborn:tab20")
    norm = mcolor.Normalize(0, len(components.stations) - 1)

    for n, sta in enumerate(sorted_stations):
        timespan_arr = components.timelines[sta]
        for start, end in timespan_arr:
            span = np.arange(str(start), str(end), dtype="datetime64[m]")
            if len(span) == 0:
                continue
            ax.plot(span, [n] * len(span), color=clrmap(norm(n)), lw=10)
    ax.set_yticks(
        np.arange(0, len(components.stations)), labels=components.stations
    )
    ax.set(xlabel="Time", ylabel="Station ID")
    plt.show()
