from pathlib import Path
from typing import TypedDict, NotRequired
from datetime import datetime


class SingleChannelNetworkConfig(TypedDict):
    network_id: str
    network_start: datetime
    network_end: datetime
    location_id: str
    channel_id: str
    save_directory: NotRequired[Path | str]


AMERY_ICE_SHELF: SingleChannelNetworkConfig = {
    "network_id": "X9",
    "network_start": datetime(2005, 1, 6, 0, 0, 0),
    "network_end": datetime(2007, 3, 1, 23, 59, 59),
    "location_id": "",
    "channel_id": "EPZ",
    "save_directory": Path("D:/seismic_data/amery_ice_shelf/trace_data/"),
}

PINE_ISLAND_GLACIER: SingleChannelNetworkConfig = {
    "network_id": "XC",
    "network_start": datetime(2012, 1, 1, 0, 0, 0),
    "network_end": datetime(2014, 12, 31),
    "location_id": "",
    "channel_id": "HHZ",
    "save_directory": Path("D:/seismic_data/pine_island_glacier/trace_data/"),
}

DRRIS: SingleChannelNetworkConfig = {
    "network_id": "XH",
    "network_start": datetime(2014, 1, 1, 0, 0, 0),
    "network_end": datetime(2017, 12, 31, 23, 59, 59),
    "location_id": "",
    "channel_id": "HHZ",
    "save_directory": Path("D:/seismic_data/drris/trace_data/"),
}
