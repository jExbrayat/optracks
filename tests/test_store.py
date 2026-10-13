import datetime

import pandas as pd

from optracks.store import connect, flight_fixes, save_flight, top_flights


def make_flight(id, distance_km):
    flight = {"id": id, "filename": f"{id}.igc", "pilot": "P", "date": datetime.date(2026, 7, 1),
              "distance_km": distance_km}
    fixes = pd.DataFrame({
        "time": pd.date_range("2026-07-01 12:00", periods=3, freq="s", tz="UTC"),
        "lat": [45.0, 45.1, 45.2], "lon": [6.0, 6.1, 6.2], "alt": [1000.0, 1001.0, 1002.0],
        "pattern": ["transition", "thermal", "thermal"],
    })
    return flight, fixes


def test_store_round_trip(tmp_path):
    con = connect(tmp_path / "t.duckdb")
    for id, km in [("a", 10.0), ("b", 30.0), ("c", 20.0)]:
        save_flight(con, *make_flight(id, km))
    assert top_flights(con, 2)["id"].tolist() == ["b", "c"]
    fixes = flight_fixes(con, ["a", "b"])
    assert fixes["flight_id"].tolist() == ["a"] * 3 + ["b"] * 3
    assert fixes["pattern"].tolist()[:3] == ["transition", "thermal", "thermal"]


def test_save_flight_replaces_previous_version(tmp_path):
    con = connect(tmp_path / "t.duckdb")
    save_flight(con, *make_flight("a", 10.0))
    save_flight(con, *make_flight("a", 12.0))
    assert top_flights(con, 10)["distance_km"].tolist() == [12.0]
    assert len(flight_fixes(con, ["a"])) == 3
