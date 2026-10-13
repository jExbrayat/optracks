# Optracks — consolidated spec (Claude's reference)

Summary of `specs.md` plus decisions made in discussion with the user (2026-10-13).
`specs.md` is the user's own document and the source of truth; if the two disagree, `specs.md` wins and this file should be updated.

## Goal
Paragliding track analytics: process raw flight tracks into pattern-based tracks, display them on a map, and later derive thermal hotspots / transition heatmaps (in the spirit of https://thermal.kk7.ch/) to help optimize flights and find new routes.

## MVP scope
- Input: IGC track files provided manually by the user. No connection to XContest or any other data source.
- Launch site selection: out of scope; the user supplies the tracks for one site.
- Display the **top N tracks, ranked by distance**, on a map. Distance = **free distance** as on XContest: start, up to 3 turnpoints, end, all on the track in time order (decided 2026-10-13).
- Segment each track into patterns (see below) and show them on the map.
- No advanced filtering, no weather conditioning, no ML.

## Pattern classification rules (confirmed)
Evaluated in this priority order:

| Pattern | Rule |
|---|---|
| Thermal | Heading change of at least **360°** (a full turn) in the same direction (changed from 3/4 turn on 2026-10-13). |
| Figure of eight | Successive turns of **at least 1/2 turn**, with the direction alternating after each turn (L→R→L…), **and** average climb rate over 20 s > 0.5 m/s. |
| Ridge soaring | Non-circling flight with **average climb rate over 120 s > 0 m/s**. It is its own category, separate from transition. |
| Transition | Everything else. |

Vario thresholds are always read as: "if the average climb rate over x seconds > threshold, then …".
Dropped for now: "sounding".

## Later features (not MVP)
- Thermal heatmap and hotspots, plus a transition heatmap, replace the original idea of "averaging tracks into an optimal track". Averaging was rejected.
- Weather conditioning (wind, time of day, season).
- Algorithms discussed (no ML):
  - Heatmap: put thermal points on a grid (square cells or H3 hexagons) and count them or average their climb rate per cell.
  - Transition heatmap: count the transition segments that cross each cell.
  - Hotspots: group thermal centers with DBSCAN, or take the cells with the highest values in the grid.

## Stack
- Python everywhere the user writes code. The user knows Python best.
- Python 3.14 with uv (`.venv`). Not 3.15: duckdb has no 3.15 wheel yet.
- Pattern detection runs on the backend as a precompute step, not in the browser. Python in the browser (Pyodide) was rejected.
- **No Jupyter notebooks.** The user hates them.
- Use existing libraries where possible:
  - `aerofiles` to parse IGC files
  - `igc_lib`: not on PyPI, so we use a small detector that adds up heading change instead
  - `pyproj` for metric coordinates
  - `scikit-learn` DBSCAN for hotspots, later
- Storage: the user agreed to store processed tracks and asked "Postgres?". Claude recommended **DuckDB**: a single file, no server, a spatial extension, good for aggregate queries. Postgres with PostGIS only if the tool is hosted for many users.
- Map/UI: the user likes kepler.gl. Claude recommended **Streamlit + pydeck**: all Python, built on deck.gl like kepler.gl, with path, heatmap and hexagon layers.

## Constraints / context
- XContest has no public API and its terms forbid scraping. The user accepted this, so there's no XContest interface for now.
