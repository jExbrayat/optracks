"""Command line entry point: optracks ingest FILE.igc... [--db optracks.duckdb]"""

import argparse
import hashlib
from pathlib import Path

import pandas as pd

from optracks.distance import free_distance
from optracks.igc import read_igc
from optracks.patterns import classify
from optracks.store import connect, save_flight
from optracks.track import prepare

DEFAULT_DB = Path("optracks.duckdb")


def process_igc(path: Path) -> tuple[dict, pd.DataFrame] | None:
    """Return the flight record and its classified fixes, or None if no flight is found."""
    header, fixes = read_igc(path)
    fixes = prepare(fixes)
    if len(fixes) < 2:
        return None
    distance, _ = free_distance(fixes)
    flight = {
        "id": hashlib.sha1(path.read_bytes()).hexdigest(),
        "filename": path.name,
        "pilot": header.get("pilot"),
        "date": header.get("utc_date"),
        "distance_km": distance / 1000,
    }
    return flight, fixes.assign(pattern=classify(fixes))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="optracks")
    commands = parser.add_subparsers(dest="command", required=True)
    ingest = commands.add_parser("ingest", help="process IGC files and store them")
    ingest.add_argument("files", nargs="+", type=Path)
    ingest.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args(argv)

    con = connect(args.db)
    for path in args.files:
        result = process_igc(path)
        if result is None:
            print(f"{path.name}: skipped, no flight found")
            continue
        save_flight(con, *result)
        print(f"{path.name}: {result[0]['distance_km']:.1f} km")
    con.close()
