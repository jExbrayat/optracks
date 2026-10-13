"""Metric coordinates for fixes."""

import pandas as pd
from pyproj import Transformer


def project(fixes: pd.DataFrame) -> pd.DataFrame:
    """Add x, y (m) in an azimuthal equidistant projection centred on the first fix."""
    lat0, lon0 = fixes["lat"].iloc[0], fixes["lon"].iloc[0]
    transformer = Transformer.from_crs(
        "EPSG:4326", f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +units=m", always_xy=True
    )
    x, y = transformer.transform(fixes["lon"].to_numpy(), fixes["lat"].to_numpy())
    return fixes.assign(x=x, y=y)
