pip install uv && uv sync && uv run python -c "import sys; from nodejs_wheel import npm; sys.exit(npm(['install']))" && cp demo.duckdb optracks.duckdb
