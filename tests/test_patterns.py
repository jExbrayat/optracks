import pandas as pd
from synthetic import flight

from optracks.patterns import FIGURE_OF_EIGHT, RIDGE, THERMAL, TRANSITION, classify, segments, turning_runs


def runs_of(df, min_angle):
    runs = turning_runs(df["x"].to_numpy(), df["y"].to_numpy())
    return runs[runs["angle"] >= min_angle]


def test_turning_runs_sum_a_full_circle():
    df = flight((30, 0, -1), (48, 15, 1), (30, 0, -1))  # two left turns
    runs = runs_of(df, 180)
    assert len(runs) == 1
    assert runs["direction"].iloc[0] == 1
    assert abs(runs["angle"].iloc[0] - 720) < 15


def test_turning_runs_straight_has_no_turn():
    assert runs_of(flight((120, 0, -1)), 30).empty


def test_turning_runs_alternate_direction():
    df = flight((20, 0, 0), (14, 15, 1), (14, -15, 1), (14, 15, 1), (20, 0, 0))
    runs = runs_of(df, 180)
    assert runs["direction"].tolist() == [1, -1, 1]


def test_turning_runs_tolerate_gps_noise():
    df = flight((30, 0, -1), (48, -15, 1), (30, 0, -1), noise=0.5)
    runs = runs_of(df, 270)
    assert runs["direction"].tolist() == [-1]
    assert runs["angle"].iloc[0] > 650


def labels(df):
    return classify(df).tolist()


def test_classify_thermal_on_full_turn():
    df = flight((60, 0, -1), (26, 15, 2), (60, 0, -1))  # 390 deg left turn
    out = labels(df)
    assert out[60:84].count(THERMAL) == 24
    assert out[:40].count(THERMAL) == 0


def test_classify_slow_full_turn_is_not_thermal():
    df = flight((60, 0, -1), (50, 8, 2), (60, 0, -1))  # 400 deg at 8 deg/s
    assert THERMAL not in labels(df)


def test_classify_three_quarter_turn_is_not_thermal():
    df = flight((60, 0, -1), (20, 15, 2), (60, 0, -1))  # 300 deg
    assert THERMAL not in labels(df)


def test_classify_figure_of_eight_when_climbing():
    legs = [(14, 15, 1), (3, 0, 1), (14, -15, 1), (3, 0, 1)] * 3
    out = labels(flight((60, 0, -1), *legs, (60, 0, -1)))
    assert out[70:150].count(FIGURE_OF_EIGHT) > 70


def test_classify_alternating_turns_without_climb_are_not_figure_of_eight():
    legs = [(14, 15, 0.2), (3, 0, 0.2), (14, -15, 0.2), (3, 0, 0.2)] * 3
    assert FIGURE_OF_EIGHT not in labels(flight((60, 0, -1), *legs, (60, 0, -1)))


def test_classify_turns_far_apart_are_not_figure_of_eight():
    legs = [(14, 15, 1), (40, 0, 1), (14, -15, 1), (40, 0, 1)] * 3
    assert FIGURE_OF_EIGHT not in labels(flight((60, 0, -1), *legs))


def test_classify_ridge_and_transition():
    out = labels(flight((300, 0, 0.3), (300, 0, -1)))
    assert set(out[:200]) == {RIDGE}
    assert set(out[400:]) == {TRANSITION}


def test_segments_split_on_pattern_change_and_join_paths():
    fixes = pd.DataFrame({
        "flight_id": ["a"] * 5 + ["b"] * 2,
        "lon": [0, 1, 2, 3, 4, 10, 11], "lat": [0, 0, 0, 0, 0, 5, 5],
        "pattern": [THERMAL, THERMAL, RIDGE, RIDGE, THERMAL, TRANSITION, TRANSITION],
    })
    out = segments(fixes)
    assert out["pattern"].tolist() == [THERMAL, RIDGE, THERMAL, TRANSITION]
    assert out["path"].tolist() == [
        [[0, 0], [1, 0], [2, 0]],
        [[2, 0], [3, 0], [4, 0]],
        [[4, 0]],
        [[10, 5], [11, 5]],
    ]
