from tidalseis.retrieval.traces import (
    get_trace_models,
    save_stationtraces_model,
)
from tidalseis.retrieval.inventory import get_iris_inventory, get_channel_info
import network_catalog as pn

NET = pn.AMERY_ICE_SHELF

inv = get_iris_inventory(
    NET["network_id"],
    NET["network_start"],
    NET["network_end"],
    NET["channel_id"],
)
info = get_channel_info(inv)


for sta, cha_list in info:
    if len(cha_list) > 1:
        raise ValueError("Single channel networks only.")
    span_arr, trace_models = get_trace_models(
        **NET,
        station_id=sta.code,
    )

    if (svdir := NET.get("save_directory")) is None:
        raise ValueError()

    save_stationtraces_model(sta, cha_list[0], trace_models, svdir)
