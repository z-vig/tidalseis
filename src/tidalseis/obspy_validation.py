from typing import Any

from obspy import Stream, Inventory, Trace, UTCDateTime  # type: ignore
from obspy.core.trace import Stats  # type: ignore
from obspy.core.inventory.station import Station  # type: ignore
from obspy.core.inventory.channel import Channel  # type: ignore
from obspy.core.inventory.util import DataAvailability  # type: ignore


def validate_stream(val: Any) -> Stream:
    if not isinstance(val, Stream):
        raise TypeError(f"Value is not Stream: {val}")
    return val


def validate_inventory(val: Any) -> Inventory:
    if not isinstance(val, Inventory):
        raise TypeError(f"Value is not Inventory: {val}")
    return val


def validate_station(val: Any) -> Station:
    if not isinstance(val, Station):
        raise TypeError(f"Value is not Station: {val}")
    return val


def validate_channel(val: Any) -> Channel:
    if not isinstance(val, Channel):
        raise TypeError(f"Value is not Channel: {val}")
    return val


def validate_data_availability(val: Any) -> DataAvailability:
    if not isinstance(val, DataAvailability):
        raise TypeError(f"Value is not DataAvailability: {val}")
    return val


def validate_trace(val: Any) -> Trace:
    if not isinstance(val, Trace):
        raise TypeError(f"Value is not Trace: {val}")
    return val


def validate_utc(val: Any) -> UTCDateTime:
    if not isinstance(val, UTCDateTime):
        raise TypeError(f"Value is not UTCDateTime: {val}")
    return val


def validate_stats(val: Any) -> Stats:
    if not isinstance(val, Stats):
        raise TypeError(f"Value is not Stats: {val}")
    return val
