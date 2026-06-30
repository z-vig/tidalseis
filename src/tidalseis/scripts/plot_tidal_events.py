from pathlib import Path
from importlib.resources import files, as_file

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


@click.command()
@click.argument(
    "network", type=click.Choice(tidal_localities, case_sensitive=False)
)
@click.argument("event_catalog_fp", type=str)
@click.option("-d", "--degree_per_bin", type=float, default=8)
@click.option("-s", "--save_directory", type=str, default="none")
def main(
    network: TidalLocality,
    event_catalog_fp: str | Path,
    degree_per_bin: float,
    save_directory: str | Path,
) -> None:
    with as_file(
        files("tidalseis.data").joinpath("publications.mplstyle")
    ) as style:
        plt.style.use(style)
    cap_network = network.title()
    if not is_valid_tidal_locality(cap_network):
        raise ValueError(f"Invalid network name: {cap_network}")
    td = get_tide_data(cap_network)
    find_tide_peaks(td)
    phase_arr = utc2phase(td.time, td.get_relative_peak_times())

    nbins = int(360 / degree_per_bin)

    wrapped_height, phase_bins, wrapped_std = wrap_phase_arr(
        td.height, phase_arr % 360, nbins=nbins
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

    # ax.set_title("Pine Island Glacier Seismic Activity")

    ax.set_gid("MainAxes")

    if save_directory == "none":
        save_dir = Path(event_catalog_fp)
    else:
        save_dir = Path(save_directory)
        if not save_dir.is_dir():
            save_dir.mkdir(parents=True)

    save_fp = save_dir / "tide_height_seismic_activity"
    for i in [".svg", ".png"]:
        plt.savefig(save_fp.with_suffix(i))

    summary = np.stack(
        [phase_bins[1:], wrapped_height, wrapped_std, wrapped_events], axis=-1
    )

    with open(save_dir / "tide_height_seismic_activity_data.csv", "w") as file:
        file.write(
            "tidal_phase, tidal_height, tidal_height_std, number_of_events\n"
        )
        for n in range(summary.shape[0]):
            vals = [str(float(i)) for i in summary[n, :]]
            file.write(", ".join(vals))
            file.write("\n")

    plt.show()
