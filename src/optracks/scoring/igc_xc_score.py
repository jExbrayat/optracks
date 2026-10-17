"""Scorer backed by mmomtchev/igc-xc-score (Node.js), run in a subprocess through solve.mjs."""

import json
import subprocess
from pathlib import Path

from nodejs_wheel import node

from optracks.scoring.base import Score, ScorerError

SCRIPT = Path(__file__).with_name("solve.mjs")
TIMEOUT = 600  # s, the optimiser can be slow on some flights


class IgcXcScoreScorer:
    def free_distance(self, igc_path: Path) -> Score:
        geojson = self._solve(igc_path, "od")
        features = geojson["features"]
        by_id = {f["id"]: f for f in features}
        ids = ["ep_start", *sorted(i for i in by_id if i.startswith("tp")), "ep_finish"]
        points = [tuple(by_id[i]["geometry"]["coordinates"][::-1]) for i in ids]
        legs_km = [f["properties"]["d"] for f in features if f["id"].startswith("seg")]
        return Score(distance_m=sum(legs_km) * 1000, points=points)

    def _solve(self, igc_path: Path, code: str) -> dict:
        try:
            result = node(
                [str(SCRIPT), str(igc_path.resolve()), code],
                return_completed_process=True,
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
                cwd=SCRIPT.parent,
            )
        except subprocess.TimeoutExpired as error:
            raise ScorerError(f"igc-xc-score timed out on {igc_path}") from error
        if result.returncode:
            raise ScorerError(
                f"igc-xc-score failed on {igc_path}: {result.stderr.strip()}\n"
                "Did you run `npm install` (see readme)?"
            )
        return json.loads(result.stdout)
