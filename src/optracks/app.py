"""Map of the top N flights by distance, coloured by pattern. Run: streamlit run src/optracks/app.py"""

import pydeck as pdk
import streamlit as st

from optracks.abstract import abstract
from optracks.cli import DEFAULT_DB
from optracks.patterns import FIGURE_OF_EIGHT, RIDGE, THERMAL, TRANSITION, segments
from optracks.store import connect, flight_fixes, top_flights

COLORS = {
    THERMAL: [220, 50, 47],
    FIGURE_OF_EIGHT: [235, 150, 20],
    RIDGE: [40, 160, 70],
    TRANSITION: [40, 110, 220],
}

st.set_page_config(page_title="Optracks", layout="wide")
n = st.sidebar.number_input("Top N flights by distance", min_value=1, value=10)
for pattern, color in COLORS.items():
    st.sidebar.markdown(f"<span style='color:rgb{tuple(color)}'>━━</span> {pattern}", unsafe_allow_html=True)

if not DEFAULT_DB.exists():
    st.info(f"No {DEFAULT_DB} yet. Run `optracks ingest FILE.igc...` first.")
    st.stop()
con = connect(DEFAULT_DB, read_only=True)
flights = top_flights(con, n)
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
            "IconLayer", symbols, get_position=["lon", "lat"], get_icon="icon", get_size=28,
            size_units="pixels", pickable=True,
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
