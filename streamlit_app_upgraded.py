# streamlit_app.py (Upgraded with full mines data)
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import folium
from streamlit_folium import st_folium
import time

# --------- Auto-refresh ----------
use_st_autorefresh = False
try:
    from streamlit_autorefresh import st_autorefresh
    use_st_autorefresh = True
except:
    use_st_autorefresh = False

# --------- Load data from GitHub ----------
CSV_URL = "https://raw.githubusercontent.com/<your-username>/<repo>/main/wcl_daily.csv"
try:
    df = pd.read_csv(CSV_URL)
except:
    st.warning("Could not load CSV from GitHub. Using sample data.")
    df = pd.DataFrame([
        ("Wani", "Durgapur Rayyatwari OC", 1729000, 19.95, 78.95),
        ("Wani", "Bellora-Naigaon OC (Expansion)", 2460000, 19.95, 78.95),
        ("Wani", "Ukni OC (Expansion)", 3810000, 19.95, 78.95),
        ("Wani", "Penganga OC", 1857000, 19.95, 78.95),
        ("Nagpur", "Saoner OC", 1200000, 21.15, 79.08),
        ("Wani North", "Amalgamation Yekona I & II OC", 1030000, 20.00, 78.92),
        ("Wani North", "Dahegaon Makardhokra 2&4 OC", 3500000, 20.00, 78.92),
        ("Wani North", "Kosar Gokul OC", 1680000, 20.00, 78.92),
        ("Wani North", "Yekona II UG->OC", 1156000, 20.00, 78.92),
        ("Wani North", "Niljai Deep OC", 1670000, 20.00, 78.92),
        ("Wani North", "Naglon OC", 1289000, 20.00, 78.92),
        ("Wani North", "Naigaon Develi OC", 1228000, 20.00, 78.92),
        ("Ballarpur", "Ballarpur Opencast Mine", 625000, 19.92, 79.33),
        ("Ballarpur", "Gouri Deep OC", 378000, 19.92, 79.33),
        ("Ballarpur", "GouriPauni OC (Amalgamation)", 2574000, 19.92, 79.33),
        ("Ballarpur", "Pauni-II Expansion OC", 3250000, 19.92, 79.33),
        ("Ballarpur", "Dhuptala OC", 1681000, 19.92, 79.33),
        ("Ballarpur", "Sasti OC", 1889000, 19.92, 79.33),
        ("Ballarpur", "Ballarpur Colliery 3&4 Pits (UG)", 71000, 19.92, 79.33),
        ("Nagpur", "Adasa UG to OC", 715460, 21.15, 79.08),
        ("Nagpur", "Amalgamated InderKamptee Deep OC", 3090000, 21.15, 79.08),
        ("Nagpur", "Bhanegaon OC", 1149700, 21.15, 79.08),
        ("Nagpur", "Gondegaon Extension OC", 3500000, 21.15, 79.08),
        ("Nagpur", "Patansaongi UG (Expansion)", 38640, 21.15, 79.08),
        ("Nagpur", "Saoner UG (Expansion)", 504960, 21.15, 79.08),
        ("Nagpur", "Silewara UG (Expansion)", 69080, 21.15, 79.08),
        ("Nagpur", "Singhori OC (Expansion)", 1199000, 21.15, 79.08),
        ("Umrer", "Makardhokra-I OC", 4200000, 21.00, 79.20),
        ("Umrer", "Dinesh OC (MKD-III)", 4432500, 21.00, 79.20),
        ("Umrer", "Umrer OC", 3110000, 21.00, 79.20),
        ("Umrer", "Gokul OC", 1807000, 21.00, 79.20),
        ("Chandrapur", "Durgapur OC", 2500000, 19.95, 79.30),
        ("Chandrapur", "Durgapur Rayatwari Colliery (UG)", 100000, 19.95, 79.30),
        ("Chandrapur", "Chanda Rayatwari Colliery", 60000, 19.95, 79.30),
        ("Kanhan", "Ambara OC", 1000000, 21.10, 79.20),
        ("Kanhan", "Ghorawari OC", 1500000, 21.10, 79.20),
        ("Kanhan", "Mohan (Maori) UG", 38330, 21.10, 79.20),
        ("Kanhan", "Nandan UG", 405000, 21.10, 79.20),
        ("Kanhan", "Sharda UG", 34555, 21.10, 79.20),
        ("Kanhan", "Tandsi UG", 35505, 21.10, 79.20),
        ("Pench", "Barkuhi OC", 750000, 20.50, 79.00),
        ("Pench", "Chhinda OC Mine", 1300000, 20.50, 79.00),
        ("Pench", "Dhankasa UG Mine", 1200000, 20.50, 79.00),
        ("Pench", "Jamuniya UG Mine", 828000, 20.50, 79.00),
    ], columns=["Region", "Mine Name", "Daily Output (tonnes)", "Lat", "Lon"])

# ---------- Streamlit UI ----------
st.set_page_config(page_title="WCL Daily Coal Making", layout="wide")
st.title("⛏️ WCL Daily Coal Production Dashboard")

# Sidebar controls
st.sidebar.header("Controls")
refresh_enabled = st.sidebar.checkbox("Enable Auto-refresh", value=True)
refresh_minutes = st.sidebar.slider("Refresh interval (minutes)", 1, 60, 5)

if refresh_enabled:
    interval_ms = refresh_minutes * 60 * 1000
    if use_st_autorefresh:
        st_autorefresh(interval=interval_ms, limit=None, key="autorefresh")
    else:
        st.markdown(f"<script>setTimeout(()=>{{location.reload();}}, {interval_ms});</script>", unsafe_allow_html=True)

# ---------- KPIs ----------
total_output = int(df["Daily Output (tonnes)"].sum())
region_totals = df.groupby("Region")["Daily Output (tonnes)"].sum().sort_values(ascending=False)
k1, k2, k3 = st.columns(3)
k1.metric("🔹 Total Daily Output", f"{total_output:,} t")
k2.metric("🔹 Number of Mines", len(df))
k3.metric("🔹 Regions", len(region_totals))

# ---------- Region-wise Bar Chart ----------
st.subheader("📊 Region-wise Daily Production")
fig = px.bar(x=region_totals.index, y=region_totals.values, labels={"x":"Region","y":"Output (t)"}, text=region_totals.values)
st.plotly_chart(fig, use_container_width=True)

# ---------- Mine-level Table ----------
st.subheader("🏭 Mine-wise Production")
region_filter = st.selectbox("Filter by Region", ["All"] + df["Region"].unique().tolist())
df_filtered = df if region_filter=="All" else df[df["Region"]==region_filter]
st.dataframe(df_filtered[["Region","Mine Name","Daily Output (tonnes)"]], use_container_width=True)

# ---------- Top & Bottom Mines ----------
st.subheader("🏆 Top / Bottom Mines")
if not df.empty:
    top = df.loc[df["Daily Output (tonnes)"].idxmax()]
    bottom = df.loc[df["Daily Output (tonnes)"].idxmin()]
    c1,c2 = st.columns(2)
    c1.success(f"Top Mine: {top['Mine Name']} ({top['Daily Output (tonnes)']:,} t)")
    c2.error(f"Lowest Mine: {bottom['Mine Name']} ({bottom['Daily Output (tonnes)']:,} t)")

# ---------- Download Excel ----------
def to_excel_bytes(df_):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_.to_excel(writer, index=False, sheet_name="WCL_Output")
    return output.getvalue()

st.download_button("⬇️ Download Excel", data=to_excel_bytes(df), file_name="wcl_output.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------- Forecast ----------
st.subheader("📈 Forecast: Tomorrow's Total Output")
try:
    hist_df = pd.read_csv("wcl_history.csv", parse_dates=["ds"]).sort_values("ds")
except:
    # create fake history
    dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
    hist_df = pd.DataFrame({"ds":dates, "y":[total_output*0.9]*30})

forecast_val = None
try:
    from prophet import Prophet
    m = Prophet(daily_seasonality=True)
    m.fit(hist_df)
    future = m.make_future_dataframe(periods=1)
    fcast = m.predict(future)
    forecast_val = int(fcast.iloc[-1]["yhat"])
    st.line_chart(fcast.set_index("ds")["yhat"])
except:
    forecast_val = int(hist_df.tail(7)["y"].mean())
    st.line_chart(hist_df.set_index("ds")["y"])

st.info(f"Predicted Total Output Tomorrow: **{forecast_val:,} t**")

# ---------- Map ----------
st.subheader("🗺️ Mine Locations Map")
m = folium.Map(location=[df["Lat"].mean(), df["Lon"].mean()], zoom_start=7)
for _, r in df.iterrows():
    folium.Marker([r["Lat"], r["Lon"]], tooltip=r["Mine Name"], popup=f"{r['Mine Name']} ({r['Daily Output (tonnes)']:,} t)").add_to(m)
st_folium(m, width="100%", height=450)

# ---------- Insights ----------
st.subheader("🔎 Quick Insights")
insights=[]
if not region_totals.empty:
    insights.append(f"🔸 Highest contributing region: **{region_totals.idxmax()}** ({int(region_totals.max()):,} t)")
insights.append(f"🔸 Number of mines reporting: **{len(df)}**")
st.markdown("\n".join(insights))

st.markdown("---")
st.markdown("Made with ❤️ — replace sample CSV with your GitHub CSV for real data.")
