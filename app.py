import streamlit as st
import pandas as pd
import altair as alt
from bisect import bisect_left

# ——— Add custom CSS for font sizing ———
st.markdown(
    """
    <style>
    h3 { font-size: 32px !important; }
    .stNumberInput label, .stNumberInput input { font-size: 18px !important; }
    .stButton > button { font-size: 18px !important; }
    .stMarkdown, .stText { font-size: 18px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ——— PASSWORD from Streamlit secrets ———
PASSWORD = st.secrets.get("INTERP_PASS")
if "authed" not in st.session_state:
    pwd = st.text_input("🔒 Enter password", type="password")
    if pwd == PASSWORD:
        st.session_state.authed = True
    else:
        st.stop()

# ——— Load & clean CSVs ———
df = pd.read_csv("data.csv", skipinitialspace=True)
df.columns = df.columns.str.strip()
xs = df["range_nm"].tolist()
ys_pct = df["changeFlightFuel_pct"].tolist()

# second file (gallons)
df2 = pd.read_csv("data_gal.csv", skipinitialspace=True)
df2.columns = df2.columns.str.strip()
xs2 = df2["range_nm"].tolist()
ys_gal = df2["changeFlightFuel_gal"].tolist()

# ——— Generic interpolation ———
def interp_generic(x, xs_arr, ys_arr):
    if x < xs_arr[0] or x > xs_arr[-1]:
        return None
    i = max(1, bisect_left(xs_arr, x))
    x0, x1 = xs_arr[i-1], xs_arr[i]
    y0, y1 = ys_arr[i-1], ys_arr[i]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

# ——— Initialize history ———
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: range_nm, pct, gal

# ——— UI ———
st.markdown("""
<h3>Finlet 737-800 Flight Fuel Savings (SXS Config)</h3>
""", unsafe_allow_html=True)

x_val = st.number_input(
    f"Input range in nautical miles (min {xs[0]}, max {xs[-1]}):",
    min_value=float(xs[0]),
    max_value=float(xs[-1]),
    value=float(xs[0]),
    format="%.0f",
    step=100.0
)

if st.button("Compute"):
    result_pct = interp_generic(x_val, xs, ys_pct)
    result_gal = interp_generic(x_val, xs2, ys_gal)
    if result_pct is None or result_gal is None:
        st.warning("❗️ Value out of range")
    else:
        st.success(f"Reduction in flight fuel = {result_pct:.2f}%  |  {result_gal:,.1f} gal")
        st.session_state.history.append({
            "range_nm": x_val,
            "savings_pct": result_pct,
            "savings_gal": result_gal
        })

# ——— Plot accumulated points ———
if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)

    pct_chart = alt.Chart(hist_df).mark_line(point={"filled": True, "size": 180}).encode(
        x=alt.X('range_nm:Q', title='Range (nm)'),
        y=alt.Y('savings_pct:Q', title='% Fuel Savings')
    ).properties(width=700, height=350)

    gal_chart = alt.Chart(hist_df).mark_line(point={"filled": True, "size": 180}).encode(
        x=alt.X('range_nm:Q', title='Range (nm)'),
        y=alt.Y('savings_gal:Q', title='Fuel Savings (gal)')
    ).properties(width=700, height=350)

    st.altair_chart(pct_chart, use_container_width=True)
    st.altair_chart(gal_chart, use_container_width=True)

    if st.button("Clear"):
        st.session_state.history = []
