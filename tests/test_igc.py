import datetime

from synthetic import write_igc

from optracks.igc import read_igc


def test_read_igc(tmp_path):
    path = tmp_path / "flight.igc"
    write_igc(path, [
        (datetime.time(12, 0, 0), 45.5, 6.2, 1500),
        (datetime.time(12, 0, 1), 45.5001, 6.2001, 1501),
        (datetime.time(12, 0, 1), 45.5001, 6.2001, 1501),  # duplicate fix
    ])
    header, fixes = read_igc(path)
    assert header["pilot"] == "Test Pilot"
    assert list(fixes.columns) == ["time", "lat", "lon", "alt"]
    assert len(fixes) == 2
    assert fixes["alt"].tolist() == [1500.0, 1501.0]
    assert fixes["time"].iloc[0] == datetime.datetime(2026, 7, 1, 12, tzinfo=datetime.UTC)


def test_read_igc_falls_back_to_gps_altitude(tmp_path):
    path = tmp_path / "flight.igc"
    write_igc(path, [(datetime.time(12, 0, 0), 45.5, 6.2, 1500)], pressure=False)
    _, fixes = read_igc(path)
    assert fixes["alt"].tolist() == [1520.0]
