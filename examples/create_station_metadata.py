from pathlib import Path
from station_metadata_catalog import AmeryStation, LembataStation

base = Path(__file__).parent / "station_metadata_json"

AmeryStation.to_json(base / "amery_station.json")
LembataStation.to_json(base / "lembata_station.json")
