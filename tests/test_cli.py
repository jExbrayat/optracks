import pandas as pd
from synthetic import flight, to_igc_fixes, write_igc

from optracks.cli import main
from optracks.store import connect, flight_fixes, top_flights


def test_ingest_stores_classified_flight(tmp_path, capsys):
    ground = flight((60, 0, 0), speed=0)
    df = pd.concat([ground, flight((60, 0, -1), (48, 15, 2), (60, 0, -1)).iloc[1:]], ignore_index=True)
    path = tmp_path / "flight.igc"
    write_igc(path, to_igc_fixes(df))
    db = tmp_path / "t.duckdb"

    main(["ingest", str(path), "--db", str(db)])

    assert "flight.igc:" in capsys.readouterr().out
    con = connect(db, read_only=True)
    flights = top_flights(con, 10)
    assert flights["pilot"].tolist() == ["Test Pilot"]
    assert 1.0 < flights["distance_km"].iloc[0] < 1.4
    fixes = flight_fixes(con, flights["id"].tolist())
    assert len(fixes) < len(df) - 50  # ground time trimmed
    assert "thermal" in set(fixes["pattern"])
