from typing import TypeAlias, Literal, TypeGuard

TidalLocality: TypeAlias = Literal[
    "Amery Ice Shelf",
    "DRRIS",
    "Pine Island",
    "Nascent Rift RIS",
    "ARROW",
    "Langhovde Glacier",
]

tidal_localities = [
    "Amery Ice Shelf",
    "DRRIS",
    "Pine Island",
    "Nascent Rift RIS",
    "ARROW",
    "Langhovde Glacier",
]


def is_valid_tidal_locality(val: str) -> TypeGuard[TidalLocality]:
    return val in tidal_localities
