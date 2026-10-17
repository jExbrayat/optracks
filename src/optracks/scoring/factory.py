"""Scorer factory: callers ask for a scorer by name and never import a backend."""

from collections.abc import Callable

from optracks.scoring.base import Scorer
from optracks.scoring.builtin import BuiltinScorer
from optracks.scoring.igc_xc_score import IgcXcScoreScorer

DEFAULT_SCORER = "igc-xc-score"

_registry: dict[str, Callable[[], Scorer]] = {
    "igc-xc-score": IgcXcScoreScorer,
    "builtin": BuiltinScorer,
}


def register_scorer(name: str, builder: Callable[[], Scorer]) -> None:
    _registry[name] = builder


def create_scorer(name: str = DEFAULT_SCORER) -> Scorer:
    try:
        return _registry[name]()
    except KeyError:
        raise ValueError(f"Unknown scorer {name!r}, available: {sorted(_registry)}") from None
