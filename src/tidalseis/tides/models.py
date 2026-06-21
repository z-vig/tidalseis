from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass
class TideData:
    time: list[datetime]
    height: np.ndarray
    _peaks: np.ndarray | None = None

    @property
    def length(self) -> int:
        return len(self.time)

    @property
    def peaks(self) -> np.ndarray:
        if self._peaks is None:
            raise AttributeError("Peaks have not been calculated.")
        return self._peaks

    @peaks.setter
    def peaks(self, val: np.ndarray) -> None:
        self._peaks = val

    @property
    def peak_times(self) -> list[datetime]:
        return [self.time[i] for i in self.peaks]

    def get_relative_times(
        self, reference_time: datetime | None = None
    ) -> np.ndarray:
        if reference_time is None:
            reference_time = self.time[0]
        return np.array(
            [(i - reference_time).total_seconds() for i in self.time]
        )

    def get_relative_peak_times(
        self, reference_time: datetime | None = None
    ) -> np.ndarray:
        if reference_time is None:
            reference_time = self.time[0]
        return np.array(
            [(i - reference_time).total_seconds() for i in self.peak_times]
        )
