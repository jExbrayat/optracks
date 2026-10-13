import numpy as np
import pandas as pd

from optracks.track import project, resample_1hz, trim_to_flight


def make_fixes(seconds, lat, lon, alt):
    t0 = pd.Timestamp("2026-07-01 12:00", tz="UTC")
    return pd.DataFrame({
        "time": t0 + pd.to_timedelta(seconds, unit="s"),
        "lat": lat, "lon": lon, "alt": alt,
    })


def test_resample_1hz_interpolates():
    fixes = make_fixes([0, 2, 4], [45.0, 45.002, 45.004], [6.0, 6.0, 6.0], [1000.0, 1004.0, 1008.0])
    out = resample_1hz(fixes)
    assert len(out) == 5
    assert np.allclose(out["alt"], [1000, 1002, 1004, 1006, 1008])
    assert out["time"].diff().dropna().dt.total_seconds().eq(1).all()


def test_project_is_metric_around_first_fix():
    out = project(make_fixes([0, 1], [45.0, 45.001], [6.0, 6.0], [1000.0, 1000.0]))
    assert np.allclose([out["x"][0], out["y"][0]], [0, 0])
    assert abs(out["x"][1]) < 1e-6
    assert 110 < out["y"][1] < 112  # 0.001 deg of latitude is about 111 m


def test_trim_to_flight_drops_ground_time():
    ground = np.zeros(60)
    flight = np.arange(1, 121) * 10.0  # 10 m/s
    y = np.concatenate([ground, flight, np.full(60, flight[-1])])
    fixes = pd.DataFrame({"x": np.zeros_like(y), "y": y})
    out = trim_to_flight(fixes)
    assert 115 <= len(out) <= 125
