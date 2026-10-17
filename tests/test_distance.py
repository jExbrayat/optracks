import pandas as pd
from synthetic import flight

from optracks.scoring.free_distance import free_distance


def test_free_distance_straight_line():
    distance, points = free_distance(flight((100, 0, 0)))
    assert abs(distance - 1000) < 1e-6
    assert points[0] == 0 and points[-1] == 100


def test_free_distance_uses_three_turnpoints():
    square = pd.DataFrame({"x": [0, 1000, 1000, 0, 0], "y": [0, 0, 1000, 1000, 0]})
    distance, points = free_distance(square)
    assert abs(distance - 4000) < 1e-6
    assert points == [0, 1, 2, 3, 4]


def test_free_distance_out_and_return():
    distance, _ = free_distance(flight((50, 0, 0), (12, 15, 0), (50, 0, 0)))
    assert distance > 1000


def test_free_distance_on_decimated_long_track():
    distance, _ = free_distance(flight((5000, 0, 0)))
    assert abs(distance - 50_000) < 30
