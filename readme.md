To run:
```bash
source .venv/bin/activate
uv sync
python -c "import sys; from nodejs_wheel import npm; sys.exit(npm([\"install\"]))"  # installs igc-xc-score
optracks ingest data/tracks/*.igc
streamlit run src/optracks/app.py
```
