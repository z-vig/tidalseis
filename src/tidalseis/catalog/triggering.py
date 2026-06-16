from dataclasses import dataclass
from typing import Optional, TypedDict, NotRequired
from pydantic import BaseModel
from datetime import datetime


import obspy  # type: ignore
from obspy.signal.trigger import coincidence_trigger  # type: ignore

import tidalseis._obspy_validation as vld
from tidalseis.retrieval.models import StationModel


class TriggerDict(TypedDict):
    time: obspy.UTCDateTime
    stations: list[str]
    trace_ids: list[str]
    coincidence_sum: float
    similarity: dict
    duration: float
    cft_peaks: NotRequired[list[float]]
    cft_stds: NotRequired[list[float]]
    cft_peak_wmean: NotRequired[float]
    cft_std_wmean: NotRequired[float]


class CoincidenceTriggerArgs(TypedDict):
    trigger_type: str
    thr_on: float
    thr_off: float
    thr_coincidence_sum: int
    lta: float
    sta: float


@dataclass(frozen=True)
class TriggeringConfig:
    trigger_type: str
    trigger_on_threshold: float
    trigger_off_threshold: float
    num_coincident_stations: int
    long_term_average_length: Optional[float]
    short_term_average_length: Optional[float]

    def as_coincidence_trigger_args(self) -> CoincidenceTriggerArgs:
        if self.long_term_average_length is None:
            raise ValueError(
                "Cannot create coincidence trigger args without `long_term_average_length`"
            )
        if self.short_term_average_length is None:
            raise ValueError(
                "Cannot create coincidence trigger args without `short_term_average_length`"
            )
        arg_dict: CoincidenceTriggerArgs = {
            "trigger_type": self.trigger_type,
            "thr_on": self.trigger_on_threshold,
            "thr_off": self.trigger_off_threshold,
            "thr_coincidence_sum": self.num_coincident_stations,
            "lta": self.long_term_average_length,
            "sta": self.short_term_average_length,
        }
        return arg_dict


class EventData(BaseModel):
    event_start: datetime
    event_end: datetime
    stations: list[StationModel]
    waveforms: list[float]


def run_coincidece_trigger(
    stream: obspy.Stream, config: TriggeringConfig
) -> list[TriggerDict]:
    """
    Runs a coincidence trigger for a stream and returns a list of the triggers.
    """
    triggers = coincidence_trigger(
        stream=stream, **config.as_coincidence_trigger_args(), details=True
    )
    trig_list: list[TriggerDict] = []
    for t in triggers:
        trig_dict = vld.validate_trigger(t)

        # ==== Eliminating invalid triggers ====
        if trig_dict["duration"] > 120:
            continue

        trig_list.append(trig_dict)

    print(f"{len(trig_list)} Events Detected")

    return trig_list


def parse_event_data(
    trace_dict: dict[str, obspy.Trace], triggers: list[TriggerDict]
) -> None:
    return
