import streamlit as st
import pandas as pd
from bisect import bisect_left
import os

# ——— Add custom CSS for font sizing ———
st.markdown(
    """
    <style>
    /* Title as h3 with smaller font */
    h3 {
        font-size: 32px !important;
    }
    /* Input label and number field larger */
    .stNumberInput label,
    .stNumberInput input {
        font-size: 18px !important;
    }
    /* Button text larger */
    .stButton > button {
        font-size: 18px !important;
    }
    /* Output text larger */
    .stMarkdown,
    .stText {
        font-size: 18px !important;
    }
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
    # out of bounds
    if x < xs[0] or x > xs[-1]:
        return None
    # find insertion index, ensure at least 1
    i = max(1, bisect_left(xs, x))
    x0, x1 = xs[i-1], xs[i]
    y0, y1 = ys[i-1], ys[i]
    # linear interpolation
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

# ——— UI ———
st.markdown("""
<h3>Finlet 737-800 Flight Fuel Savings (SXS Config)</h3>
""", unsafe_allow_html=True)

# Number input with min/max matching data range
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
