"""Scorer interface: the rest of optracks only depends on this module and the factory."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class ScorerError(RuntimeError):
    """The scoring backend is unavailable or failed."""


@dataclass(frozen=True)
class Score:
    distance_m: float
    points: list[tuple[float, float]]  # (lat, lon): start, turnpoints, end


class Scorer(Protocol):
    def free_distance(self, igc_path: Path) -> Score:
        """Free distance: start, up to 3 turnpoints and end, in time order."""
