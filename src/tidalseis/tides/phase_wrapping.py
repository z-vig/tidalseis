from datetime import datetime

import numpy as np
from scipy.stats import binned_statistic


def _resolve_time_list(timelist: np.ndarray | list[datetime]) -> np.ndarray:
    if isinstance(timelist, np.ndarray):
        return timelist
    return np.array([(i - timelist[0]).total_seconds() for i in timelist])


def utc2phase(
    resample_utc: np.ndarray | list[datetime],
    peak_utc: np.ndarray | list[datetime],
) -> np.ndarray:
    """
    Converts UTC times to tidal phase.
    """
    peak_times = _resolve_time_list(peak_utc)  # array of relative times (s)
    peak_times = np.insert(peak_times, 0, 0)  # with zero time for start

    resamp_times = _resolve_time_list(resample_utc)  # relative times (s)

    cum_phase = np.arange(0, 360 * peak_times.size, 360)

    phase_interp = np.interp(resamp_times, peak_times, cum_phase)

    return phase_interp


def wrap_phase_arr(
    data: np.ndarray, tidal_phase: np.ndarray, nbins: int = 36
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Wraps data to a single tidal phase, averaging to a set bin width of tidal
    phase.
    """
    if (data.ndim > 1) or (tidal_phase.ndim > 1):
        raise ValueError("Data and Phase arrays must be 1D.")
    if data.size != tidal_phase.size:
        raise ValueError("Data and Tidal Phase arrays are not the same size.")

    res = binned_statistic(tidal_phase, data, bins=nbins)
    res_std = binned_statistic(tidal_phase, data, bins=nbins, statistic="std")

    return res.statistic, res.bin_edges, res_std.statistic
