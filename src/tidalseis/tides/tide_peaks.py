from importlib.resources import files, as_file
from datetime import datetime

import pandas as pd
import numpy as np
from scipy.signal import find_peaks

from tidalseis.types import TidalLocality
from .models import TideData


def get_tide_data(locality: TidalLocality) -> TideData:
    """Retrieves tidal model data."""
    model_fp = files("tidalseis").joinpath(
        f"data/tidal_heights/{locality.upper().replace(" ", "_")}.txt"
    )

    with as_file(model_fp) as f:
        tides = pd.read_csv(f, delimiter=" ")
        tide_height = tides.z
        tide_date = tides.date
        tide_time = tides.time
        tide_datetime: list[tuple[datetime, float]] = []
        FMT = "%m-%d-%Y%H:%M:%S"
        for i, j, z in zip(tide_date, tide_time, tide_height):
            tide_datetime.append((datetime.strptime(i + j, FMT), float(z)))

        times = [i[0] for i in tide_datetime]
        heights = np.array([i[1] for i in tide_datetime])

        td = TideData(times, heights)

        return td


def find_tide_peaks(tide_date: TideData) -> None:
    sec_per_sample = (
        tide_date.time[-1] - tide_date.time[0]
    ).total_seconds() / len(tide_date.time)
    samples_per_day = 86400 / sec_per_sample
    peaks, properties = find_peaks(
        tide_date.height, distance=0.9 * samples_per_day, prominence=0.2
    )
    tide_date.peaks = peaks


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    td = get_tide_data("Amery Ice Shelf")
    find_tide_peaks(td)

    peak_times = np.array(td.get_relative_peak_times())
    peak_times = np.insert(peak_times, 0, 0)

    cum_phase = np.arange(0, 360 * peak_times.size, 360)
    arr = np.interp(
        np.linspace(0, peak_times[-1], 100000), peak_times, cum_phase
    )

    plt.scatter(peak_times, cum_phase % 360, color="r", s=1, zorder=2)
    plt.plot(np.linspace(0, peak_times[-1], 100000), arr % 360, color="k")

    # plt.plot(td.get_relative_times(), td.height, color="k")
    # plt.vlines(
    #     td.get_relative_peak_times(),
    #     ymin=td.height.min(),
    #     ymax=td.height.max(),
    #     color="r",
    # )
    # plt.xlim(0, 900000)
    plt.show()
