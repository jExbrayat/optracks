"""DuckDB storage of processed flights."""

from pathlib import Path

import duckdb
import pandas as pd

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
"""


def connect(path: Path, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(str(path), read_only=read_only)
    if not read_only:
        con.execute(SCHEMA)
    return con


def save_flight(con: duckdb.DuckDBPyConnection, flight: dict, fixes: pd.DataFrame) -> None:
    """Insert a flight and its classified fixes, replacing any previous version."""
    new_fixes = fixes[["time", "lat", "lon", "alt", "pattern"]]
    con.begin()
    con.execute("DELETE FROM fixes WHERE flight_id = ?", [flight["id"]])
    con.execute("DELETE FROM flights WHERE id = ?", [flight["id"]])
    con.execute(
        "INSERT INTO flights VALUES ($id, $filename, $pilot, $date, $distance_km)", flight
    )
    con.execute("INSERT INTO fixes SELECT ?, * FROM new_fixes", [flight["id"]])
    con.commit()


def top_flights(con: duckdb.DuckDBPyConnection, n: int) -> pd.DataFrame:
    return con.execute(
        "SELECT * FROM flights ORDER BY distance_km DESC LIMIT ?", [n]
    ).df()


def flight_fixes(con: duckdb.DuckDBPyConnection, flight_ids: list[str]) -> pd.DataFrame:
    return con.execute(
        "SELECT * FROM fixes WHERE flight_id IN (SELECT unnest(?)) ORDER BY flight_id, time",
        [flight_ids],
    ).df()
