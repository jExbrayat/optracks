"""Prepare fixes for analysis: 1 Hz resampling, metric coordinates, in-flight part only."""

import numpy as np
import pandas as pd
from pyproj import Transformer

MIN_FLIGHT_SPEED = 15 / 3.6  # m/s, ground speed above which the glider is considered flying
SPEED_WINDOW = 10  # s, smoothing window for the flying test


def resample_1hz(fixes: pd.DataFrame) -> pd.DataFrame:
    """Linearly interpolate lat, lon and alt on a 1 s time grid."""
    t = (fixes["time"] - fixes["time"].iloc[0]).dt.total_seconds().to_numpy()
    grid = np.arange(0, np.floor(t[-1]) + 1)
    out = {"time": fixes["time"].iloc[0] + pd.to_timedelta(grid, unit="s")}
    for col in ("lat", "lon", "alt"):
        out[col] = np.interp(grid, t, fixes[col].to_numpy())
    return pd.DataFrame(out)


def project(fixes: pd.DataFrame) -> pd.DataFrame:
    """Add x, y (m) in an azimuthal equidistant projection centred on the first fix."""
    lat0, lon0 = fixes["lat"].iloc[0], fixes["lon"].iloc[0]
    transformer = Transformer.from_crs(
        "EPSG:4326", f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=m", always_xy=True
    )
    x, y = transformer.transform(fixes["lon"].to_numpy(), fixes["lat"].to_numpy())
    return fixes.assign(x=x, y=y)


def trim_to_flight(fixes: pd.DataFrame) -> pd.DataFrame:
    """Keep fixes from the first to the last one where the smoothed ground speed shows flight.

    Expects 1 Hz fixes with x, y columns.
    """
    speed = np.hypot(fixes["x"].diff(), fixes["y"].diff())
    flying = np.flatnonzero(speed.rolling(SPEED_WINDOW, center=True, min_periods=1).median() > MIN_FLIGHT_SPEED)
    if len(flying) == 0:
        return fixes.iloc[0:0]
    return fixes.iloc[flying[0]:flying[-1] + 1].reset_index(drop=True)


def prepare(fixes: pd.DataFrame) -> pd.DataFrame:
    """Resample to 1 Hz, project to metres and trim to the flight."""
    return trim_to_flight(project(resample_1hz(fixes)))
