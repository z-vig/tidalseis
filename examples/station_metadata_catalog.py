from datetime import datetime

from tidalseis.station_models import ChannelModel, StationModel

# ==== Amery Station, Antarctica ====
AmeryChannels = {
    "EPE": ChannelModel(id="EPE"),
    "EPN": ChannelModel(id="EPN"),
    "EPZ": ChannelModel(id="EPZ"),
}

AmeryStation = StationModel(
    network="X9",
    id="HFS3",
    channels=AmeryChannels,
    start=datetime(2005, 1, 6, 0, 0, 0),
    end=datetime(2007, 3, 1, 23, 59, 59),
)

# ==== Banda Arc-Australia Collision, Lembata Island Indoensia ====
LembataChannels = {"BHZ": ChannelModel(id="BHZ")}
LembataStation = StationModel(
    network="YS",
    id="BAOP",
    channels=LembataChannels,
    start=datetime(2014, 11, 1),
    end=datetime(2016, 10, 10, 7, 26, 9),
)
