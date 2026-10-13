from synthetic import flight

from optracks.patterns import turning_runs


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
