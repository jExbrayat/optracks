"""Pattern detection on fixes (see specs.claude.md for the rules)."""

import numpy as np
import pandas as pd

HEADING_SMOOTHING = 5  # s, window used to decide the turning direction

THERMAL_TURN = 270  # deg, at least 3/4 of a turn in the same direction
EIGHT_TURN = 180  # deg, each turn of a figure of eight is at least 1/2 turn
EIGHT_MAX_GAP = 10  # s, max straight flight between two successive turns of a figure of eight
EIGHT_VARIO, EIGHT_WINDOW = 0.5, 20  # m/s, s
RIDGE_VARIO, RIDGE_WINDOW = 0.0, 120  # m/s, s

THERMAL, FIGURE_OF_EIGHT, RIDGE, TRANSITION = "thermal", "figure_of_eight", "ridge", "transition"


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


def climb_rate(alt: pd.Series, window: int) -> pd.Series:
    """Average climb rate (m/s) over a centred window of `window` seconds."""
    return alt.diff().rolling(window, center=True, min_periods=1).mean().fillna(0)


def figure_of_eight_spans(turns: pd.DataFrame) -> pd.DataFrame:
    """Fix spans (start, end) covering 2+ successive turns of alternating direction."""
    successive = (turns["direction"] != turns["direction"].shift()) & (
        turns["start"] - turns["end"].shift() <= EIGHT_MAX_GAP
    )
    spans = turns.groupby((~successive).cumsum()).agg(
        start=("start", "first"), end=("end", "last"), turns=("start", "size")
    )
    return spans[spans["turns"] >= 2]


def classify(fixes: pd.DataFrame) -> pd.Series:
    """Label each fix as thermal, figure_of_eight, ridge or transition.

    Expects fixes with x, y and alt columns. Rules are applied in priority order.
    """
    runs = turning_runs(fixes["x"].to_numpy(), fixes["y"].to_numpy())
    pattern = np.full(len(fixes), TRANSITION, dtype=object)

    pattern[climb_rate(fixes["alt"], RIDGE_WINDOW).to_numpy() > RIDGE_VARIO] = RIDGE

    eights = np.zeros(len(fixes), dtype=bool)
    for span in figure_of_eight_spans(runs[(runs["direction"] != 0) & (runs["angle"] >= EIGHT_TURN)]).itertuples():
        eights[span.start:span.end] = True
    pattern[eights & (climb_rate(fixes["alt"], EIGHT_WINDOW).to_numpy() > EIGHT_VARIO)] = FIGURE_OF_EIGHT

    for run in runs[(runs["direction"] != 0) & (runs["angle"] >= THERMAL_TURN)].itertuples():
        pattern[run.start:run.end] = THERMAL

    return pd.Series(pattern, index=fixes.index, name="pattern")


def segments(fixes: pd.DataFrame) -> pd.DataFrame:
    """One row per run of same-pattern fixes of a flight: flight_id, pattern, path ([lon, lat] list).

    Each path also ends on the first fix of the next segment so the drawn track has no gaps.
    """
    rows = []
    for flight_id, flight in fixes.groupby("flight_id", sort=False):
        flight = flight.reset_index(drop=True)
        runs = (flight["pattern"] != flight["pattern"].shift()).cumsum()
        for _, run in flight.groupby(runs):
            end = min(run.index[-1] + 1, len(flight) - 1)
            path = flight.loc[run.index[0]:end, ["lon", "lat"]].to_numpy().tolist()
            rows.append({"flight_id": flight_id, "pattern": run["pattern"].iloc[0], "path": path})
    return pd.DataFrame(rows, columns=["flight_id", "pattern", "path"])
