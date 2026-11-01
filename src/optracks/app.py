"""Map of the top N flights by distance, coloured by pattern. Run: streamlit run src/optracks/app.py

Each visitor works on a private temporary copy of the database: uploaded IGC files are added to
that copy and always shown on the map, and are lost when the session ends.
"""

import shutil
import tempfile
from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st
from pydeck.types import String

from optracks.abstract import abstract
from optracks.cli import DEFAULT_DB, process_igc
from optracks.patterns import FIGURE_OF_EIGHT, RIDGE, THERMAL, TRANSITION, segments
from optracks.store import connect, flight_fixes, flights_by_id, save_flight, top_flights

COLORS = {
    THERMAL: [220, 50, 47],
    FIGURE_OF_EIGHT: [235, 150, 20],
    RIDGE: [40, 160, 70],
    TRANSITION: [40, 110, 220],
}

THERMAL_DIAMETER_M = 60  # icons have a fixed size on the ground

st.set_page_config(page_title="Optracks", layout="wide")
n = st.sidebar.number_input("Top N flights by distance (plus your uploads)", min_value=1, value=10)
for pattern, color in COLORS.items():
    st.sidebar.markdown(f"<span style='color:rgb{tuple(color)}'>━━</span> {pattern}", unsafe_allow_html=True)

if "workdir" not in st.session_state:
    st.session_state.workdir = Path(tempfile.mkdtemp())
    st.session_state.uploaded = {}  # upload file_id -> flight id
workdir = st.session_state.workdir
db = workdir / "session.duckdb"
if not db.exists() and DEFAULT_DB.exists():
    shutil.copy(DEFAULT_DB, db)

uploads = st.sidebar.file_uploader("Upload IGC tracks", type="igc", accept_multiple_files=True)
for upload in uploads:
    if upload.file_id in st.session_state.uploaded:
        continue
    path = workdir / upload.name
    path.write_bytes(upload.getvalue())
    try:
        with st.spinner(f"Processing {upload.name}"):
            flight, fixes = process_igc(path)
    except Exception as error:
        st.sidebar.error(f"{upload.name}: {error}")
        continue
    con = connect(db)
    save_flight(con, flight, fixes)
    con.close()
    st.session_state.uploaded[upload.file_id] = flight["id"]

if not db.exists():
    st.info("No flights yet. Upload an IGC file in the sidebar.")
    st.stop()
con = connect(db, read_only=True)
mine = list(st.session_state.uploaded.values())
flights = pd.concat([flights_by_id(con, mine), top_flights(con, n)]).drop_duplicates("id")
fixes = flight_fixes(con, flights["id"].tolist())
con.close()
if flights.empty:
    st.info("No flights stored yet.")
    st.stop()

flights = flights.assign(date=flights["date"].astype(str), distance_km=flights["distance_km"].round(1))
paths = segments(fixes).merge(flights, left_on="flight_id", right_on="id")
paths["color"] = paths["pattern"].map(COLORS)

if st.sidebar.checkbox("Abstract tracks"):
    lines, symbols = abstract(paths)
    layers = [
        pdk.Layer("PathLayer", lines, get_path="path", get_color="color", width_min_pixels=3, pickable=True),
        pdk.Layer(
            "IconLayer", symbols, get_position=["lon", "lat"], get_icon="icon", get_size=THERMAL_DIAMETER_M,
            size_units=String("meters"), size_min_pixels=8, pickable=True,
        ),
    ]
else:
    layers = [pdk.Layer("PathLayer", paths, get_path="path", get_color="color", width_min_pixels=2, pickable=True)]
view = pdk.data_utils.compute_view(fixes[["lon", "lat"]].to_numpy().tolist())
st.pydeck_chart(pdk.Deck(
    layers=layers,
    initial_view_state=view,
    tooltip={"text": "{pilot}, {date}\n{distance_km} km\n{pattern}"},
))
