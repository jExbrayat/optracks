from pathlib import Path

from streamlit.testing.v1 import AppTest
from synthetic import flight, to_igc_fixes, write_igc

from optracks.cli import main

APP = str(Path(__file__).parents[1] / "src" / "optracks" / "app.py")


def test_app_without_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    at = AppTest.from_file(APP).run()
    assert not at.exception
    assert "Upload an IGC file" in at.info[0].value


def test_app_draws_stored_flights(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_igc(tmp_path / "f.igc", to_igc_fixes(flight((60, 0, -1), (48, 15, 2), (60, 0, -1))))
    main(["ingest", "f.igc"])
    at = AppTest.from_file(APP).run()
    assert not at.exception
    assert len(at.get("deck_gl_json_chart")) == 1


def test_app_abstract_mode(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_igc(tmp_path / "f.igc", to_igc_fixes(flight((60, 0, -1), (48, 15, 2), (60, 0, -1))))
    main(["ingest", "f.igc"])
    at = AppTest.from_file(APP).run()
    at.sidebar.checkbox[0].check().run()
    assert not at.exception
    assert len(at.get("deck_gl_json_chart")) == 1


def test_app_upload_is_shown_without_touching_stored_database(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    write_igc(tmp_path / "f.igc", to_igc_fixes(flight((60, 0, -1), (48, 15, 2), (60, 0, -1))))
    at = AppTest.from_file(APP).run(timeout=60)
    at.sidebar.number_input[0].set_value(1)
    at.sidebar.file_uploader[0].upload("f.igc", (tmp_path / "f.igc").read_bytes())
    at.run(timeout=60)
    assert not at.exception
    assert len(at.get("deck_gl_json_chart")) == 1
    assert not (tmp_path / "optracks.duckdb").exists()
