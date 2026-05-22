from obspy.clients.fdsn import Client  # type: ignore
from obspy import UTCDateTime  # type: ignore

from examples.station_metadata_catalog import AmeryStation

import tidalseis.obspy_validation as vld
import csv

client = Client("Earthscope")

inventory = vld.validate_inventory(
    client.get_stations(
        network="X9",
        station="*",
        location="",
        channel="EP*",
        level="channel",
        starttime=UTCDateTime(AmeryStation.start),
        endtime=UTCDateTime(AmeryStation.end),
        includeavailability=True,
    )
)


pad_char = "="
for sta in inventory[0]:
    sta = vld.validate_station(sta)
    print(f"{sta.code:{pad_char}^{120}}")
    for cha in sta.channels:
        cha = vld.validate_channel(cha)
        avail = vld.validate_data_availability(cha.data_availability)
        print(f"{cha.code} // {cha.sample_rate}")

# waveform = client.get_waveforms(
#     network="X9",
#     station=sta.code,
#     location="",
#     channel=cha.code,
#     starttime=avail.start,
#     endtime=avail.end,
# )
# if not is_stream(waveform):
#     raise ValueError()

# for n, tr in enumerate(waveform.traces):
#     if not is_trace(tr):
#         raise ValueError()

#     tr_meta = make_trace_metadata(tr, sta)
#     tr_meta.to_json(
#         Path(__file__).parent
#         / "meta_dir"
#         / f"{sta.code}_trace{n}.json"
#     )

# waveform.write(
#     Path("D:/seismic_data/amery_ice_shelf")
#     / f"{sta.code}_{cha.code}.mseed",
#     format="MSEED",
# )
# tr: Trace = waveform.traces[0]
# plt.plot(tr.times(), tr.data)
# plt.ylim(-8e3, 8e3)
# plt.show()
