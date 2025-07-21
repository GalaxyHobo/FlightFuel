import streamlit as st
import pandas as pd
from bisect import bisect_left
import os

# ——— PASSWORD from Streamlit secrets ———
PASSWORD = st.secrets["INTERP_PASS"]

# ——— simple session-state auth ———
if "authed" not in st.session_state:
    pwd = st.text_input("🔒 Enter password", type="password")
    if pwd == PASSWORD:
        st.session_state.authed = True
    else:
        st.stop()

# ——— load data.csv ———
df = pd.read_csv("data.csv")
xs, ys = df["range_nm"].tolist(), df["changeFlightFuel_pct"].tolist()

# ——— interpolation function ———
def interpolate(x):
    i = bisect_left(xs, x)
    if i == 0 or i == len(xs):
        return None
    x0, x1 = xs[i-1], xs[i]
    y0, y1 = ys[i-1], ys[i]
    return y0 + (y1-y0)*(x - x0)/(x1 - x0)

# ——— UI ———
st.title("🔍 Linear Interpolator")
x_val = st.number_input("Input a:", format="%.6f")
if st.button("Compute"):
    result = interpolate(x_val)
    if result is None:
        st.warning("❗️ Value out of range")
    else:
        st.success(f"Interpolated b = **{result:.6f}**")