from typing import (
    Any,
    TypedDict,
    NotRequired,
    get_type_hints,
    get_origin,
    get_args,
)
from datetime import datetime

from obspy import Stream, Inventory, Trace, UTCDateTime  # type: ignore
from obspy.core.trace import Stats  # type: ignore
from obspy.core.inventory.station import Station  # type: ignore
from obspy.core.inventory.channel import Channel  # type: ignore
from obspy.core.inventory.util import DataAvailability, SampleRate  # type: ignore


def _matches_type(value: Any, expected_type: Any) -> bool:
    origin = get_origin(expected_type)

    if origin is list:
        if not isinstance(value, list):
            return False

        (item_type,) = get_args(expected_type)
        return all(_matches_type(item, item_type) for item in value)

    return isinstance(value, expected_type)


def is_typed_dict_instance(
    val: dict,
    typed_dict_cls: type,
) -> bool:
    hints = get_type_hints(typed_dict_cls)

    for key, expected_type in hints.items():
        if key not in val:
            return False

        if not _matches_type(val[key], expected_type):
            return False

    return True


class TriggerDict(TypedDict):
    time: UTCDateTime
    stations: list[str]
    trace_ids: list[str]
    coincidence_sum: float
    similarity: dict
    duration: float
    cft_peaks: NotRequired[list[float]]
    cft_stds: NotRequired[list[float]]
    cft_peak_wmean: NotRequired[float]
    cft_std_wmean: NotRequired[float]


def validate_trigger(val: Any) -> TriggerDict:
    if not isinstance(val, dict):
        raise TypeError(f"Value is not a dictionary: {val}")
    if not is_typed_dict_instance(val, TriggerDict):
        raise TypeError(f"Value is not TriggerDict: {val}")

    trig_dict: TriggerDict = {
        "time": val["time"],
        "stations": val["stations"],
        "trace_ids": val["trace_ids"],
        "coincidence_sum": val["coincidence_sum"],
        "similarity": val["similarity"],
        "duration": val["duration"],
    }

    if (cft_peaks := val.get("cft_peaks")) is not None:
        trig_dict["cft_peaks"] = cft_peaks
    if (cft_stds := val.get("cft_stds")) is not None:
        trig_dict["cft_stds"] = cft_stds
    if (cft_peak_wmean := val.get("cft_peak_wmean")) is not None:
        trig_dict["cft_peak_wmean"] = cft_peak_wmean
    if (cft_std_wmean := val.get("cft_std_wmean")) is not None:
        trig_dict["cft_std_wmean"] = cft_std_wmean

    return trig_dict


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


def validate_sample_rate(val: Any) -> float:
    if not isinstance(val, SampleRate):
        raise TypeError(f"Value is not SampleRate: {val}")
    return val.real


def validate_datetime(val: Any) -> datetime:
    if not isinstance(val, datetime):
        raise TypeError(f"Value is not datetime: {val}")
    return val
