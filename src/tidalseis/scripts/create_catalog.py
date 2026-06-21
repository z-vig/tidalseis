from pathlib import Path

import click

from tidalseis.catalog.triggering import TriggeringConfig
from tidalseis.catalog.create import (
    get_stream_filepaths,
    create_coincidence_catalog,
)
from tidalseis.catalog.models import EventData, CatalogModel
from tidalseis.types import TriggerType, trigger_types


@click.command()
@click.argument("stream_directory", type=str)
@click.option(
    "-t",
    "--trigger_type",
    type=click.Choice(trigger_types),
    default="classicstalta",
)
@click.option("-on", "--on_threshold", type=float, default=6)
@click.option("-off", "--off_threshold", type=float, default=5)
@click.option("-n", "--number_coincident", type=int, default=3)
@click.option("-lta", "--long_term_average_length", type=float, default=60)
@click.option("-sta", "--short_term_average_length", type=float, default=2)
@click.option("-s", "--save_directory", type=str, default="none")
def main(
    stream_directory: str | Path,
    trigger_type: TriggerType,
    on_threshold: float,
    off_threshold: float,
    number_coincident: int,
    long_term_average_length: float,
    short_term_average_length: float,
    save_directory: str | Path,
):
    if save_directory == "none":
        save_directory = Path(stream_directory).parent

    triggering_config = TriggeringConfig(
        trigger_type=trigger_type,
        trigger_on_threshold=on_threshold,
        trigger_off_threshold=off_threshold,
        num_coincident_stations=number_coincident,
        long_term_average_length=long_term_average_length,
        short_term_average_length=short_term_average_length,
    )
    stream_dir = Path(stream_directory)
    streams = get_stream_filepaths(stream_dir)

    all_events = create_coincidence_catalog(
        streams,
        triggering_config=triggering_config,
        iterative_saving=True,
        save_directory=save_directory,
    )

    event_list: list[EventData] = []

    for trigger in all_events:
        event = EventData(
            event_start=trigger["time"].datetime,
            event_duration=trigger["duration"],
            stations=trigger["stations"],
        )
        event_list.append(event)

    catalog = CatalogModel(events=event_list)

    catalog.to_json(Path(save_directory, "event_catalog").with_suffix(".json"))

    print(f"Total of {len(all_events)} were catalogged.")
