"""Synthetic 1 Hz flights in metric coordinates for tests."""

import numpy as np
import pandas as pd


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
