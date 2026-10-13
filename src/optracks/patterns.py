"""Pattern detection on prepared 1 Hz fixes (see specs.claude.md for the rules)."""

import numpy as np
import pandas as pd

HEADING_SMOOTHING = 5  # s, window used to decide the turning direction


def heading_change(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Signed heading change (rad, positive = left turn) at each fix, 0 at both ends."""
    heading = np.arctan2(np.diff(y), np.diff(x))
    change = (np.diff(heading) + np.pi) % (2 * np.pi) - np.pi
    return np.concatenate([[0.0], change, [0.0]])


def turning_runs(x: np.ndarray, y: np.ndarray) -> pd.DataFrame:
    """Split the track into runs of constant turning direction.

    Returns one row per run: start, end (fix indices, end exclusive), direction
    (1 left, -1 right, 0 straight) and angle (degrees turned in that direction).
    """
    change = heading_change(x, y)
    smoothed = pd.Series(change).rolling(HEADING_SMOOTHING, center=True, min_periods=1).mean()
    direction = np.sign(smoothed.round(9)).astype(int).to_numpy()
    starts = np.r_[0, np.flatnonzero(np.diff(direction)) + 1]
    ends = np.r_[starts[1:], len(direction)]
    angles = [np.degrees(change[s:e].sum()) * direction[s] for s, e in zip(starts, ends)]
    return pd.DataFrame({"start": starts, "end": ends, "direction": direction[starts], "angle": angles})
