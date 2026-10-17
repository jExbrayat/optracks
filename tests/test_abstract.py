import pandas as pd

from optracks.abstract import abstract
from optracks.patterns import FIGURE_OF_EIGHT, RIDGE, THERMAL, TRANSITION


def test_abstract_lines_and_symbols():
    paths = pd.DataFrame({
        "pattern": [TRANSITION, THERMAL, RIDGE, FIGURE_OF_EIGHT],
        "path": [[[0, 0], [1, 1], [2, 0]], [[2, 0], [3, 0], [3, 2]], [[3, 2], [4, 2], [5, 2]], [[5, 2], [6, 2]]],
    })
    lines, symbols = abstract(paths)
    assert lines["pattern"].tolist() == [TRANSITION, RIDGE]
    assert lines["path"].tolist() == [[[0, 0], [2, 0]], [[3, 2], [5, 2]]]
    assert symbols["pattern"].tolist() == [THERMAL, FIGURE_OF_EIGHT]
    assert symbols[["lon", "lat"]].iloc[0].tolist() == [8 / 3, 2 / 3]
    assert symbols["icon"].map(lambda i: i["url"].startswith("data:image/svg+xml")).all()
