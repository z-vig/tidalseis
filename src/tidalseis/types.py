"""
Custom types for `tidalseis` package
"""

from collections.abc import Callable
from typing import TypeAlias, Literal, TypeGuard

import obspy  # type: ignore

TidalLocality: TypeAlias = Literal[
    "Amery Ice Shelf",
    "DRRIS",
    "Pine Island",
    "Nascent Rift RIS",
    "ARROW",
    "Langhovde Glacier",
]

tidal_localities: list[TidalLocality] = [
    "Amery Ice Shelf",
    "DRRIS",
    "Pine Island",
    "Nascent Rift RIS",
    "ARROW",
    "Langhovde Glacier",
]


def is_valid_tidal_locality(val: str) -> TypeGuard[TidalLocality]:
    return val in tidal_localities


FilterType: TypeAlias = Literal["Lowpass", "Highpass", "Bandpass", "None"]
filter_types: list[FilterType] = ["Lowpass", "Highpass", "Bandpass", "None"]

PreprocessingFunc: TypeAlias = Callable[[obspy.Trace], obspy.Trace]

TriggerType: TypeAlias = Literal["classicstalta"]
trigger_types: list[TriggerType] = ["classicstalta"]
