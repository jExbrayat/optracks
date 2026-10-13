"""Free distance: start, up to 3 turnpoints and end, all on the track in time order (as on XContest)."""

import numpy as np
import pandas as pd

TURNPOINTS = 3
MAX_POINTS = 2000  # the track is decimated to this many fixes before optimising


def free_distance(fixes: pd.DataFrame) -> tuple[float, list[int]]:
    """Return the free distance (m) and the indices of its start, turnpoints and end.

    Expects x, y columns in metres. The optimum is searched on the decimated track,
    so it is exact up to the spacing between kept fixes.
    """
    step = max(1, -(-len(fixes) // MAX_POINTS))
    index = np.arange(0, len(fixes), step)
    xy = fixes[["x", "y"]].to_numpy()[index]
    dist = np.hypot(*(xy[:, None, :] - xy[None, :, :]).transpose(2, 0, 1))
    dist[np.tril_indices(len(xy), -1)] = -np.inf  # legs only go forward in time

    best = np.zeros(len(xy))  # best[j]: longest path so far ending at fix j
    previous = []
    for _ in range(TURNPOINTS + 1):
        total = best[:, None] + dist
        previous.append(total.argmax(axis=0))
        best = total.max(axis=0)

    points = [int(best.argmax())]
    for prev in reversed(previous):
        points.append(int(prev[points[-1]]))
    return float(best.max()), [int(index[p]) for p in reversed(points)]
