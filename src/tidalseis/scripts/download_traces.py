from pathlib import Path

import click

from tidalseis.types import TidalLocality, tidal_localities
import tidalseis.data.network_catalog as cat
from tidalseis.retrieval.inventory import get_iris_inventory, get_channel_info
from tidalseis.retrieval.traces import (
    get_trace_models,
    save_stationtraces_model,
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
@click.option("--save", help="Location of the save directory.", type=str)
def main(network: TidalLocality, save: Path | str | None) -> None:
    """Download seismic traces of NETWORK

    NETWORK is the name of the seismic network.
    """
    net = _get_network(network)
    inv = get_iris_inventory(
        net["network_id"],
        net["network_start"],
        net["network_end"],
        channel_search=net["channel_id"],
        station_search=net.get("station_id"),
        location_code=net["location_id"],
    )
    info = get_channel_info(inv)

    if save is not None:
        net["save_directory"] = Path(save)

    for sta, cha_list in info:
        if len(cha_list) > 1:
            raise ValueError("Single channel networks only.")
        net.update({"station_id": sta.code})
        _, trace_models = get_trace_models(
            **net,
        )

        if (svdir := net.get("save_directory")) is None:
            raise ValueError()

        save_stationtraces_model(sta, cha_list[0], trace_models, svdir)
