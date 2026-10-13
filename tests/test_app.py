from pathlib import Path

from streamlit.testing.v1 import AppTest
from synthetic import flight, to_igc_fixes, write_igc

from optracks.cli import main

APP = str(Path(__file__).parents[1] / "src" / "optracks" / "app.py")


def test_app_without_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(APP).run()
    assert not at.exception
    assert "optracks ingest" in at.info[0].value


def test_app_draws_stored_flights(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_igc(tmp_path / "f.igc", to_igc_fixes(flight((60, 0, -1), (48, 15, 2), (60, 0, -1))))
    main(["ingest", "f.igc"])
    at = AppTest.from_file(APP).run()
    assert not at.exception
    assert len(at.get("deck_gl_json_chart")) == 1
