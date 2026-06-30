# ruff: noqa
from obspy import UTCDateTime  # type: ignore
from obspy.clients.fdsn import Client  # type: ignore

from tidalseis.retrieval.inventory import get_channel_info

from tidalseis.data.network_catalog import DRRIS


def get_data(
    network_id,
    channel_id,
    location_id,
    network_start,
    network_end,
    save_directory,
    station_id=None,
):
    client = Client("Earthscope")
    print(DRRIS)
    stations = client.get_stations(
        network=network_id,
        station=station_id,
        location=location_id,
        channel=channel_id,
        level="channel",
        starttime=UTCDateTime(network_start),
        endtime=UTCDateTime(network_end),
    )
    print(stations)


get_data(**DRRIS)
