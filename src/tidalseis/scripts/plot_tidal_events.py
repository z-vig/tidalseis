from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import click

from tidalseis.tides.tide_peaks import get_tide_data, find_tide_peaks
from tidalseis.tides.phase_wrapping import (
    utc2phase,
    wrap_phase_arr,
)
from tidalseis.catalog.models import CatalogModel
from tidalseis.types import (
    TidalLocality,
    tidal_localities,
    is_valid_tidal_locality,
)

plt.style.use(Path(__file__).parent / "publications.mplstyle")


@click.command()
@click.argument(
    "network", type=click.Choice(tidal_localities), case_sensitive=False
)
@click.argument("event_catalog_fp", type=str)
@click.option("-s", "--save_directory", type=str)
def main(
    network: TidalLocality,
    event_catalog_fp: str | Path,
    save_directory: str | Path = "none",
) -> None:
    cap_network = network.title()
    if not is_valid_tidal_locality(cap_network):
        raise ValueError(f"Invalid network name: {cap_network}")
    td = get_tide_data(cap_network)
    find_tide_peaks(td)
    phase_arr = utc2phase(td.time, td.get_relative_peak_times())

    wrapped_height, phase_bins, wrapped_std = wrap_phase_arr(
        td.height, phase_arr % 360
    )

    event_catalog = CatalogModel.from_json(event_catalog_fp)

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

    if save_directory == "none":
        save_dir = Path(event_catalog_fp)
    else:
        save_dir = Path(save_directory)
    save_fp = save_dir / "tide_height_seismic_activity"
    for i in [".svg", ".png"]:
        plt.savefig(save_fp.with_suffix(i))
    plt.show()
