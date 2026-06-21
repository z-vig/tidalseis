from dataclasses import dataclass
from typing import Literal, Optional, overload
from enum import IntFlag, auto

import obspy  # type: ignore

from tidalseis.types import FilterType

BAD_BANDPASS_MESSAGE = (
    "If bandpass filtering is used, both high and low frequency cutoffs must"
    "be provided."
)
BAD_LOWPASS_MESSAGE = (
    "If lowpass filtering is used, a high frequency cutoff must be provided."
)
BAD_HIGHPASS_MESSAGE = (
    "If highpass filtering is used, a low frequency cutoff must be provided."
)


class PreprocessingFlag(IntFlag):
    NONE = 0
    DETRENDED = auto()
    FILTERED = auto()


@dataclass
class PreprocessingConfig:
    detrend: bool
    filter_type: FilterType
    low_frequency_cutoff: Optional[float] = None
    high_frequency_cutoff: Optional[float] = None

    def __post_init__(self):
        self.validate_filtering()

    def validate_filtering(self) -> None:
        if self.filter_type.lower() == "bandpass":
            if (self.low_frequency_cutoff is None) or (
                self.high_frequency_cutoff is None
            ):
                raise ValueError(BAD_BANDPASS_MESSAGE)
        elif self.filter_type.lower() == "highpass":
            if self.low_frequency_cutoff is None:
                raise ValueError(BAD_HIGHPASS_MESSAGE)
        elif self.filter_type.lower() == "lowpass":
            if self.high_frequency_cutoff is None:
                raise ValueError(BAD_LOWPASS_MESSAGE)
        elif self.filter_type.lower() == "none":
            return
        else:
            raise ValueError("Invalid filter type.")


def run_filtering(
    trace: obspy.Trace, config: PreprocessingConfig
) -> obspy.Trace:
    if config.filter_type == "Bandpass":
        trace.filter(
            type="bandpass",
            freqmin=config.low_frequency_cutoff,
            freqmax=config.high_frequency_cutoff,
        )
    elif config.filter_type == "Highpass":
        trace.filter(type="highpass", freqmax=config.low_frequency_cutoff)
    elif config.filter_type == "Lowpass":
        trace.filter(type="lowpass", freqmax=config.high_frequency_cutoff)
    return trace


@overload
def preprocess_trace(
    trace: obspy.Trace,
    config: PreprocessingConfig,
    return_original: Literal[True],
) -> tuple[PreprocessingFlag, obspy.Trace, obspy.Trace]: ...


@overload
def preprocess_trace(
    trace: obspy.Trace,
    config: PreprocessingConfig,
    return_original: Literal[False] = False,
) -> tuple[PreprocessingFlag, obspy.Trace]: ...


def preprocess_trace(
    trace: obspy.Trace,
    config: PreprocessingConfig,
    return_original: bool = False,
) -> (
    tuple[PreprocessingFlag, obspy.Trace]
    | tuple[PreprocessingFlag, obspy.Trace, obspy.Trace]
):
    """Run preprocessing on a trace object."""
    flag = PreprocessingFlag.NONE
    og_trace = trace.copy()
    if config.detrend:
        flag |= PreprocessingFlag.DETRENDED
        trace.detrend()
    if config.filter_type != "None":
        flag |= PreprocessingFlag.FILTERED
        trace = run_filtering(trace, config)

    if return_original:
        return flag, trace, og_trace
    return flag, trace
