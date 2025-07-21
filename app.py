import streamlit as st
import pandas as pd
import altair as alt
from bisect import bisect_left
import os

# ——— Add custom CSS for font sizing ———
st.markdown(
    """
    <style>
    /* Title as h3 with smaller font */
    h3 { font-size: 32px !important; }
    /* Input label and number field larger */
    .stNumberInput label,
    .stNumberInput input { font-size: 18px !important; }
    /* Button text larger */
    .stButton > button { font-size: 18px !important; }
    /* Output text larger */
    .stMarkdown,
    .stText { font-size: 18px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ——— PASSWORD from Streamlit secrets ———
PASSWORD = st.secrets.get("INTERP_PASS")

# ——— Simple session-state auth ———
if "authed" not in st.session_state:
    pwd = st.text_input("🔒 Enter password", type="password")
    if pwd == PASSWORD:
        st.session_state.authed = True
    else:
        st.stop()

# ——— Load & clean your CSV ———
df = pd.read_csv("data.csv", skipinitialspace=True)
df.columns = df.columns.str.strip()

# ——— Extract arrays ———
xs = df["range_nm"].tolist()
ys = df["changeFlightFuel_pct"].tolist()

# ——— Interpolation function ———
def interpolate(x):
    if x < xs[0] or x > xs[-1]:
        return None
    i = max(1, bisect_left(xs, x))
    x0, x1 = xs[i-1], xs[i]
    y0, y1 = ys[i-1], ys[i]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

# ——— Initialize history for plotted points ———
if "history" not in st.session_state:
    st.session_state.history = []

# ——— UI ———
st.markdown("""
<h3>Finlet 737-800 Flight Fuel Savings (SXS Config)</h3>
""", unsafe_allow_html=True)

x_val = st.number_input(
    f"Input range in nautical miles (min {xs[0]}, max {xs[-1]}):",
    min_value=float(xs[0]),
    max_value=float(xs[-1]),
    value=float(xs[0]),
    format="%.1f"
)

if st.button("Compute"):
    result = interpolate(x_val)
    if result is None:
        st.warning("❗️ Value out of range")
    else:
        st.success(f"% reduction in flight fuel = {result:.2f}%")
        # Append new point to history
        st.session_state.history.append({"range_nm": x_val, "savings_pct": result})

# ——— Plot accumulated points with larger markers ———
if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)
    chart = alt.Chart(hist_df).mark_line(
        point={"filled": True, "size": 150}
    ).encode(
        x=alt.X('range_nm:Q', title='Range (nm)'),
        y=alt.Y('savings_pct:Q', title='% Fuel Savings')
    ).properties(width=700, height=400)
    st.altair_chart(chart, use_container_width=True)
