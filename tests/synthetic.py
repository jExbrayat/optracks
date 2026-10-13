"""Synthetic 1 Hz flights in metric coordinates for tests."""

import datetime

import numpy as np
import pandas as pd
from aerofiles.igc import Writer


def flight(*legs, speed=10.0, noise=0.0, seed=0):
    """Build a flight from legs of (seconds, turn rate in deg/s, climb rate in m/s).

    Positive turn rates turn left. noise adds Gaussian GPS noise (m) to x and y.
    """
    heading, x, y, alt = 0.0, 0.0, 0.0, 1000.0
    rows = [(x, y, alt)]
    for seconds, rate, climb in legs:
        for _ in range(seconds):
            heading += np.radians(rate)
            x += speed * np.cos(heading)
            y += speed * np.sin(heading)
            alt += climb
            rows.append((x, y, alt))
    df = pd.DataFrame(rows, columns=["x", "y", "alt"])
    rng = np.random.default_rng(seed)
    df[["x", "y"]] += rng.normal(0, noise, (len(df), 2)) if noise else 0
    return df


def write_igc(path, fixes, pressure=True):
    """Write (time, lat, lon, alt) fixes to an IGC file dated 2026-07-01."""
    with open(path, "wb") as f:
        w = Writer(f)
        w.write_logger_id("XXX", "ABC", validate=False)
        w.write_date(datetime.date(2026, 7, 1))
        w.write_pilot("Test Pilot")
        for t, lat, lon, alt in fixes:
            w.write_fix(t, latitude=lat, longitude=lon, valid=True,
                        pressure_alt=alt if pressure else 0, gps_alt=alt + 20)


def to_igc_fixes(df, lat0=45.0, lon0=6.0):
    """Turn a synthetic metric flight into (time, lat, lon, alt) fixes, one per second from 12:00."""
    start = datetime.datetime(2026, 7, 1, 12)
    return [
        ((start + datetime.timedelta(seconds=i)).time(),
         lat0 + row.y / 111_320, lon0 + row.x / (111_320 * np.cos(np.radians(lat0))), round(row.alt))
        for i, row in enumerate(df.itertuples())
    ]
