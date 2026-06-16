"""
Operations dealing with python's datetime module.
"""

from datetime import datetime, timedelta
import numpy as np


def is_time_between(
    begin_time: datetime,
    end_time: datetime,
    check_time: datetime | None = None,
) -> bool:
    """If check time is not given, default to current UTC time"""
    if check_time is None:
        check_time = datetime.now()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else:  # crosses midnight
        return check_time >= begin_time or check_time <= end_time


def chunk_long_timespan(
    timespan_start: datetime, timespan_end: datetime
) -> tuple[np.ndarray, np.ndarray]:
    """
    Chunks a long timespan into 24-hour chunks.

    Parameters
    ----------
    timespan_start: datetime
        Start of the timespan.
    timespan_end
        End of the timespan.

    Returns
    -------
    np.ndarray
        Array of type np.datetime64, showing all start times for the chunks.
    np.ndarray
        Array of type np.datetime64, showing all end times for the chunks.
    """
    network_start = np.datetime64(timespan_start)
    network_end = np.datetime64(timespan_end)
    oneday = np.timedelta64(timedelta(days=1))

    start_range = np.arange(
        network_start, network_end, step=oneday, dtype="datetime64[s]"
    )
    end_range = np.arange(
        network_start + oneday,
        network_end + oneday,
        step=oneday,
        dtype="datetime64[s]",
    )

    return start_range, end_range
