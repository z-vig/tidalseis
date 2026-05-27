from tidalseis.retrieval.traces import load_traces
from tidalseis.retrieval.inventory import get_iris_inventory, get_channel_info
from tidalseis.retrieval.models import StationTraces
import network_catalog as pn

from pathlib import Path

NET = pn.AMERY_ICE_SHELF

inv = get_iris_inventory(
    NET["network_id"],
    NET["network_start"],
    NET["network_end"],
    NET["channel_id"],
)
info = get_channel_info(inv)

for sta, cha_list in info:
    span_arr, trace_models = load_traces(
        **NET, station_id=sta.code, replace=False
    )
    if len(cha_list) > 1:
        raise ValueError("Single channel networks only.")
    sta_tra = StationTraces(
        station=sta, channel=cha_list[0], traces=trace_models
    )

    svdir = NET.get("save_directory")
    if svdir is None:
        raise ValueError()
    sta_tra.to_json(Path(svdir) / sta.code)
