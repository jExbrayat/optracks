import pytest
from synthetic import flight, to_igc_fixes, write_igc

from optracks.scoring import create_scorer


@pytest.fixture
def igc(tmp_path):
    path = tmp_path / "straight.igc"
    write_igc(path, to_igc_fixes(flight((600, 0, 0))))
    return path


@pytest.mark.parametrize("name", ["igc-xc-score", "builtin"])
def test_scorers_agree_on_straight_line(name, igc):
    score = create_scorer(name).free_distance(igc)
    assert abs(score.distance_m - 6000) < 60
    assert len(score.points) >= 2


def test_unknown_scorer():
    with pytest.raises(ValueError, match="Unknown scorer"):
        create_scorer("nope")
