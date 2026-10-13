# Optracks

Paragliding track analytics tool (Python 3.14, managed with uv). MVP pipeline: IGC → metric fixes → pattern labels + free distance → DuckDB → Streamlit map.

## Commands
- `source .venv/bin/activate`, then `uv sync` to install
- `python -m pytest`: tests
- `optracks ingest data/tracks/*.igc`: process IGC files into `optracks.duckdb` (re-ingesting a file replaces it)
- `streamlit run src/optracks/app.py`: map of the top N flights

## Read first
- `specs.md`: the user's spec. This is the source of truth.
- `specs.claude.md`: Claude's consolidated summary of the spec and of the decisions made, including the confirmed pattern classification rules. Keep it in sync when decisions change.

## Working with the user
- Do exactly what is asked. Don't take initiatives, add unrequested features or scope, or pad the spec with extra sections. Point out inconsistencies, but don't act on them.
- Don't edit `specs.md` unless asked; the user writes it.
- No Jupyter notebooks.
- No ML for now.
- Prefer existing Python libraries over custom code.
- Keep answers short and direct.

## Commits
- Make small commits: one logical change each (e.g. scaffold, one module plus its tests, one doc update).
- Explicit titles: imperative mood, saying what changed and where, e.g. `Add thermal detection from accumulated heading change`. No vague titles like `update`, `fixes` or `wip`.
- Run the tests before committing; don't commit a failing state.
