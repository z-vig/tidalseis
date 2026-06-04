from datetime import datetime

from obspy.clients.fdsn import Client  # type: ignore
from obspy import UTCDateTime, Inventory  # type: ignore

import tidalseis._obspy_validation as vld
from .models import ChannelModel, StationModel


def get_iris_inventory(
    network_code: str,
    network_start: datetime,
    network_end: datetime,
    channel_search: str = "*",
) -> Inventory:

    client = Client("Earthscope")
    inventory = vld.validate_inventory(
        client.get_stations(
            network=network_code,
            station="*",
            location="",
            channel=channel_search,
            level="channel",
            starttime=UTCDateTime(network_start),
            endtime=UTCDateTime(network_end),
            includeavailability=True,
        )
    )
    return inventory


def get_channel_info(
    inventory: Inventory,
) -> list[tuple[StationModel, list[ChannelModel]]]:
    """
    Returns all channel sampling rates

    Returns
    -------
    list[tuple[str, StationCoordinates, list[ChannelModel]]]
    """
    stations: list[tuple[StationModel, list[ChannelModel]]] = []
    for sta in inventory[0]:
        sta = vld.validate_station(sta)
        channels: list[ChannelModel] = []
        for cha in sta.channels:
            cha = vld.validate_channel(cha)
            cha_model = ChannelModel.from_channel(cha)
            channels.append(cha_model)
        stations.append((StationModel.from_station(sta), channels))
    return stations
