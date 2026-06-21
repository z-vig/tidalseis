from pathlib import Path

import click

from tidalseis.catalog.preprocess import PreprocessingConfig
from tidalseis.catalog.bundle_streams import bundle_network
import tidalseis.data.network_catalog as cat
from tidalseis.types import (
    filter_types,
    FilterType,
    tidal_localities,
    TidalLocality,
)


def _get_network(network: TidalLocality) -> cat.SingleChannelNetworkConfig:
    net_name = network.upper().replace(" ", "_")
    obj: cat.SingleChannelNetworkConfig = getattr(cat, net_name)
    return obj


@click.command()
@click.argument(
    "network",
    type=click.Choice(tidal_localities, case_sensitive=False),
)
@click.argument("trace_directory", type=str)
@click.option("-d", "--detrend", is_flag=True)
@click.option(
    "-f",
    "--filter_type",
    type=click.Choice(filter_types, case_sensitive=False),
    default="Bandpass",
)
@click.option("-l", "--low_frequency", type=float, default=5)
@click.option("-h", "--high_frequency", type=float, default=20)
@click.option("-s", "--save_directory", type=str, default="none")
def main(
    network: TidalLocality,
    trace_directory: str | Path,
    detrend: bool,
    filter_type: FilterType,
    low_frequency: float,
    high_frequency: float,
    save_directory: str | Path,
):
    net = _get_network(network)
    if save_directory == "none":
        save_directory = Path(trace_directory).parent / "stream_data"
    preprocessing_config = PreprocessingConfig(
        detrend=detrend,
        filter_type=filter_type,
        low_frequency_cutoff=low_frequency,
        high_frequency_cutoff=high_frequency,
    )

    bundle_network(
        trace_directory,
        net["network_start"],
        net["network_end"],
        save_directory,
        preprocessing_config,
    )
