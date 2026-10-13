"""Read IGC files into a table of fixes."""

from pathlib import Path

import pandas as pd
from aerofiles.igc import Reader


def read_igc(path: Path) -> tuple[dict, pd.DataFrame]:
    """Return the IGC header and the fixes as columns time (UTC), lat, lon, alt (m).

    Altitude is the pressure altitude, or the GPS altitude when the logger has no barometer.
    """
    with open(path, encoding="utf-8", errors="replace") as f:
        igc = Reader().read(f)
    header = igc["header"][1]
    records = pd.DataFrame(igc["fix_records"][1])
    alt = "pressure_alt" if (records["pressure_alt"] != 0).any() else "gps_alt"
    fixes = pd.DataFrame({
        "time": records["datetime"],
        "lat": records["lat"],
        "lon": records["lon"],
        "alt": records[alt].astype(float),
    })
    return header, fixes.drop_duplicates("time").reset_index(drop=True)
