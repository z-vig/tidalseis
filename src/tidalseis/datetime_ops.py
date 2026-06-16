"""
Operations dealing with python's datetime module.
"""

from datetime import datetime


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
