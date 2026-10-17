"""Abstract a pattern-labelled track: straight lines for transitions and ridges, symbols for thermals and eights."""

import base64

import pandas as pd

from optracks.patterns import FIGURE_OF_EIGHT, RIDGE, THERMAL, TRANSITION

LINE_PATTERNS = (TRANSITION, RIDGE)
SYMBOL_SIZE = 64

_CIRCLE = (
    '<path d="M32 8 A24 24 0 1 1 8 32" fill="none" stroke="rgb(220,50,47)" stroke-width="6"/>'
    '<polygon points="0,26 16,26 8,42" fill="rgb(220,50,47)"/>'
)
_EIGHT = (
    '<path d="M32 32 C32 8 6 8 6 20 C6 32 32 32 32 44 C32 56 58 56 58 44 C58 32 32 32 32 20 C32 8 58 8 58 20"'
    ' fill="none" stroke="rgb(235,150,20)" stroke-width="6" transform="translate(0 -2)"/>'
)


def _icon(body: str) -> dict:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{SYMBOL_SIZE}" height="{SYMBOL_SIZE}" viewBox="0 0 64 64">{body}</svg>'
    url = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
    return {"url": url, "width": SYMBOL_SIZE, "height": SYMBOL_SIZE, "anchorY": SYMBOL_SIZE // 2}


ICONS = {THERMAL: _icon(_CIRCLE), FIGURE_OF_EIGHT: _icon(_EIGHT)}


def abstract(paths: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split segments (pattern, path columns) into straight lines and symbols.

    Lines keep the segment's first and last point. Symbols sit at the segment's mean position
    (lon, lat columns) with an icon column. Other columns are kept.
    """
    is_line = paths["pattern"].isin(LINE_PATTERNS)
    lines = paths[is_line].assign(path=lambda d: d["path"].map(lambda p: [p[0], p[-1]]))
    symbols = paths[~is_line].copy()
    symbols["lon"] = symbols["path"].map(lambda p: sum(pt[0] for pt in p) / len(p))
    symbols["lat"] = symbols["path"].map(lambda p: sum(pt[1] for pt in p) / len(p))
    symbols["icon"] = symbols["pattern"].map(ICONS)
    return lines.reset_index(drop=True), symbols.drop(columns="path").reset_index(drop=True)
