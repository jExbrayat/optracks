import numpy as np
import pandas as pd

from optracks.track import project


def make_fixes(seconds, lat, lon, alt):
    t0 = pd.Timestamp("2026-07-01 12:00", tz="UTC")
    return pd.DataFrame({
        "time": t0 + pd.to_timedelta(seconds, unit="s"),
        "lat": lat, "lon": lon, "alt": alt,
    })


def test_project_is_metric_around_first_fix():
    out = project(make_fixes([0, 1], [45.0, 45.001], [6.0, 6.0], [1000.0, 1000.0]))
    assert np.allclose([out["x"][0], out["y"][0]], [0, 0])
    assert abs(out["x"][1]) < 1e-6
    assert 110 < out["y"][1] < 112  # 0.001 deg of latitude is about 111 m

