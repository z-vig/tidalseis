from pathlib import Path
from datetime import datetime, timedelta
from tidalseis.load_datasets import load_traces
from tidalseis.station_models import StationModel

station = StationModel.from_json(
    Path(__file__).parent / "station_metadata_json" / "lembata_station.json"
)
start = datetime(2015, 8, 11, 16, 22, 15)
end = start + timedelta(minutes=2)
load_traces(station, "BHZ", start, end)
