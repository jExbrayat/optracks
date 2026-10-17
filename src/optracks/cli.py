"""Command line entry point: optracks ingest FILE.igc... [--db optracks.duckdb]"""

import argparse
import hashlib
from pathlib import Path

import pandas as pd

from optracks.igc import read_igc
from optracks.patterns import classify
from optracks.scoring import create_scorer
from optracks.store import connect, save_flight
from optracks.track import project

DEFAULT_DB = Path("optracks.duckdb")


def process_igc(path: Path) -> tuple[dict, pd.DataFrame]:
    """Return the flight record and its classified fixes."""
    header, fixes = read_igc(path)
    fixes = project(fixes)
    score = create_scorer().free_distance(path)
    flight = {
        "id": hashlib.sha1(path.read_bytes()).hexdigest(),
        "filename": path.name,
        "pilot": header.get("pilot"),
        "date": header.get("utc_date"),
        "distance_km": score.distance_m / 1000,
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
        flight, fixes = process_igc(path)
        save_flight(con, flight, fixes)
        print(f"{path.name}: {flight['distance_km']:.1f} km")
    con.close()
