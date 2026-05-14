"""
`load_datasets`
---
Utilities for loading datasets and extracting different data types from them.
"""

from obspy.clients.fdsn import Client as FDSNClient  # type: ignore
import numpy as np


from .types import TidalLocality


def load_traces(dataset_name: TidalLocality) -> np.ndarray:
    """
    Loads seismic traces from all known stations at the locality of interest.
    """
    client = FDSNClient(
        service_mappings={
            "dataselect": "https://service.earthscope.org/fdsnws/dataselect/1/"
        }
    )
    print(client.get_stations())
    return np.empty(0)


if __name__ == "__main__":
    load_traces("Amery Ice Shelf")
