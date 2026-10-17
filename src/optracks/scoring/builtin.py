"""NOTE: the pipeline does NOT use this scorer; free distance is routed to igc_xc_score.

Pure-Python fallback kept for reference and tests (decimated dynamic programming, free distance only).
"""

from pathlib import Path

from optracks.distance import free_distance
from optracks.igc import read_igc
from optracks.scoring.base import Score
from optracks.track import project


class BuiltinScorer:
    def free_distance(self, igc_path: Path) -> Score:
        _, fixes = read_igc(igc_path)
        fixes = project(fixes)
        distance, indices = free_distance(fixes)
        points = [(fixes["lat"].iloc[i], fixes["lon"].iloc[i]) for i in indices]
        return Score(distance_m=distance, points=points)
