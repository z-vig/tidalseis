import numpy as np

from tidalseis.tides.tide_peaks import get_tide_data, find_tide_peaks
from tidalseis.tides.phase_wrapping import (
    utc2phase,
    wrap_phase_arr,
)

import matplotlib.pyplot as plt
from pathlib import Path
from tidalseis.catalog.models import CatalogModel

plt.style.use(Path(__file__).parent / "publications.mplstyle")

td = get_tide_data("Amery Ice Shelf")
find_tide_peaks(td)
phase_arr = utc2phase(td.time, td.get_relative_peak_times())

wrapped_height, phase_bins, wrapped_std = wrap_phase_arr(
    td.height, phase_arr % 360
)

event_catalog = CatalogModel.from_json(
    "D:/seismic_data/amery_ice_shelf/event_catalog.json"
)

print(f"{event_catalog.nevents} Events loaded.")

events = event_catalog.get_relative_times(td.time[0])
event_phase = utc2phase(events, td.get_relative_peak_times())
wrapped_events, bins = np.histogram(event_phase % 360, bins=phase_bins)

f, ax = plt.subplots()
ax2 = ax.twinx()
ax.errorbar(
    phase_bins[1:],
    wrapped_height,
    wrapped_std,
    linestyle="",
    capsize=4,
    color="k",
)
ax.plot(phase_bins[1:], wrapped_height, color="r")
ax2.plot(phase_bins[1:], wrapped_events, color="b")

ax.set_xlabel("Tidal Phase")
ax.set_ylabel("Tide Height", color="r")
ax2.set_ylabel("# of Events", color="b")

ax.set_title("Amery Ice Shelf Seismic Activity")
save_fp = Path(
    "D:/seismic_data/amery_ice_shelf/plots/tide_height_seismic_activity"
)
for i in [".svg", ".png"]:
    plt.savefig(save_fp.with_suffix(i))
plt.show()
