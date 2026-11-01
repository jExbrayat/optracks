"""DuckDB storage of processed flights."""

from pathlib import Path

import duckdb
import pandas as pd

from optracks.patterns import segments

SCHEMA = """
CREATE TABLE IF NOT EXISTS flights (
    id VARCHAR PRIMARY KEY,  -- SHA-1 of the IGC file
    filename VARCHAR,
    pilot VARCHAR,
    date DATE,
    distance_km DOUBLE
);
CREATE TABLE IF NOT EXISTS fixes (
    flight_id VARCHAR,
    time TIMESTAMPTZ,
    lat DOUBLE,
    lon DOUBLE,
    alt DOUBLE,
    pattern VARCHAR
);
CREATE TABLE IF NOT EXISTS segments (
    flight_id VARCHAR,
    pattern VARCHAR,
    path DOUBLE[][]  -- [lon, lat] points
);
"""


def connect(path: Path, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(path), read_only=read_only)
    if not read_only:
        con.execute(SCHEMA)
        backfill_segments(con)
    return con


def _insert_segments(con: duckdb.DuckDBPyConnection, fixes: pd.DataFrame) -> None:
    """Store the pattern segments of fixes (with a flight_id column)."""
    new_segments = segments(fixes)
    con.execute("INSERT INTO segments SELECT * FROM new_segments")


def backfill_segments(con: duckdb.DuckDBPyConnection) -> None:
    """Compute the segments of flights stored before the segments table existed."""
    missing = con.execute("SELECT id FROM flights WHERE id NOT IN (SELECT flight_id FROM segments)").fetchall()
    for (flight_id,) in missing:
        _insert_segments(con, flight_fixes(con, [flight_id]))


def save_flight(con: duckdb.DuckDBPyConnection, flight: dict, fixes: pd.DataFrame) -> None:
    """Insert a flight and its classified fixes, replacing any previous version."""
    new_fixes = fixes[["time", "lat", "lon", "alt", "pattern"]]
    con.begin()
    con.execute("DELETE FROM segments WHERE flight_id = ?", [flight["id"]])
    con.execute("DELETE FROM fixes WHERE flight_id = ?", [flight["id"]])
    con.execute("DELETE FROM flights WHERE id = ?", [flight["id"]])
    con.execute(
        "INSERT INTO flights VALUES ($id, $filename, $pilot, $date, $distance_km)", flight
    )
    con.execute("INSERT INTO fixes SELECT ?, * FROM new_fixes", [flight["id"]])
    _insert_segments(con, new_fixes.assign(flight_id=flight["id"]))
    con.commit()


def top_flights(con: duckdb.DuckDBPyConnection, n: int) -> pd.DataFrame:
    return con.execute(
        "SELECT * FROM flights ORDER BY distance_km DESC LIMIT ?", [n]
    ).df()


def flights_by_id(con: duckdb.DuckDBPyConnection, flight_ids: list[str]) -> pd.DataFrame:
    return con.execute("SELECT * FROM flights WHERE id IN (SELECT unnest(?))", [flight_ids]).df()


def flight_fixes(con: duckdb.DuckDBPyConnection, flight_ids: list[str]) -> pd.DataFrame:
    return con.execute(
        "SELECT * FROM fixes WHERE flight_id IN (SELECT unnest(?)) ORDER BY flight_id, time",
        [flight_ids],
    ).df()


def flight_segments(con: duckdb.DuckDBPyConnection, flight_ids: list[str]) -> pd.DataFrame:
    """Stored segments (flight_id, pattern, path as a list of [lon, lat])."""
    stored = con.execute(
        "SELECT * FROM segments WHERE flight_id IN (SELECT unnest(?)) ORDER BY rowid", [flight_ids]
    ).df()
    return stored.assign(path=stored["path"].map(lambda path: [point.tolist() for point in path]))
