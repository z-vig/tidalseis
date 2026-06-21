"""
Routines for creating a seismic catalog from triggering.
"""

from pathlib import Path
from datetime import datetime

import obspy  # type: ignore

from .triggering import TriggeringConfig, run_coincidece_trigger
from .default_settings import DEFAULT_TRIGGERING
from .models import EventData, CatalogModel

import tidalseis._obspy_validation as vld


def get_stream_filepaths(
    stream_directory: str | Path,
    date_format: str = "%d%m%YT%H%M%S",
    sort: bool = True,
) -> list[tuple[datetime, Path]]:
    """
    Reads the start time of a trace from the trace file name, repeats this
    for all file names in a directory of .mseed files and returns the
    filepaths sorted in by the start time.

    Parameters
    ----------
    stream_directory: str | Path
        Directory where all the Stream objects are saved as .mseed files.
    date_format: str, optional
        Date format for the start time in the file name.

    Returns
    -------
    list[tuple[datetime, Path]]
        List of (start time, file path) sorted by start time.
    """
    path_list: list[tuple[datetime, Path]] = []
    for f in Path(stream_directory).glob("*mseed"):
        start_str, end_str = str(f.stem).split("_")
        path_list.append((datetime.strptime(start_str, date_format), f))

    if sort:
        return sorted(path_list, key=lambda x: x[0])
    else:
        return path_list


def create_coincidence_catalog(
    stream_directory: str | Path | list[tuple[datetime, Path]],
    triggering_config: TriggeringConfig = DEFAULT_TRIGGERING,
    iterative_saving: bool = True,
    save_directory: str | Path | None = None,
) -> list[vld.TriggerDict]:
    """
    Creates a catalog of seismic events on a network by running a coincidence
    trigger on all streams.

    Parameters
    ----------
    stream_directory: str | Path
        Directory where all the Stream objects are saved as .mseed files.
    triggering_config: TriggeringConfig, optional
        Config object for running the coincidence trigger. Defaults to package
        default.
    """
    if isinstance(stream_directory, str) or isinstance(stream_directory, Path):
        stream_files = get_stream_filepaths(stream_directory)
    elif isinstance(stream_directory, list):
        stream_files = stream_directory
    all_triggers: list[vld.TriggerDict] = []
    all_event_data: list[EventData] = []
    streams_to_process = len(stream_files)
    for n, (start, f) in enumerate(stream_files):
        network_stream: obspy.Stream = obspy.read(f)
        if network_stream.count() < triggering_config.num_coincident_stations:
            continue
        network_stream.merge(fill_value=0)
        print(
            f"{(n+1)/streams_to_process:.2%} Complete --> "
            f"{start.strftime("%B %d, %Y")}: ",
            end="",
        )
        triggers = run_coincidece_trigger(network_stream, triggering_config)
        all_triggers.extend(triggers)

        if iterative_saving:
            for trigger in triggers:
                event = EventData(
                    event_start=trigger["time"].datetime,
                    event_duration=trigger["duration"],
                    stations=trigger["stations"],
                )
                all_event_data.append(event)
            new_catalog = CatalogModel(events=all_event_data)

            if save_directory is None:
                raise ValueError(
                    "Save directory must be provided for iterative saving."
                )
            new_catalog.to_json(
                Path(save_directory, "event_catalog").with_suffix(".json")
            )

    return all_triggers
