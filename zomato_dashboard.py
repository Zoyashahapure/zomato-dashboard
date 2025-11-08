import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Zomato Dashboard", layout="centered", page_icon="🍽️")

# ---------- CUSTOM STYLING ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg, #FFE29F 0%, #FFA99F 50%, #FF719A 100%);
    color: #2C2C2C;
}
h1 {
    text-align: center;
    color: #22223b;
    font-family: 'Helvetica', sans-serif;
}
.sidebar .sidebar-content {
    background-color: rgba(255, 255, 255, 0.6);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🍽️ Zomato Food Delivery Dashboard</h1>", unsafe_allow_html=True)

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    # ✅ Use your own valid Google Drive direct download link
    url = "https://drive.google.com/uc?export=download&id=1i_LAZ3XmZOBujgwJrjd4VWQ3NJMixpjU"
    try:
        df = pd.read_csv(url, encoding="latin-1", on_bad_lines="skip", low_memory=False)
        return df
    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        return pd.DataFrame()

df = load_data()

# ---------- DATA VALIDATION ----------
if df.empty:
    st.error("⚠️ Data not loaded properly. Please check the CSV link or file format.")
    st.stop()

st.success("✅ Data Loaded Successfully!")
st.write("### Data Preview")
st.dataframe(df.head())

required_cols = ["City", "Cuisines", "Aggregate rating", "Average Cost for two"]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"🚨 Missing columns: {', '.join(missing)}. Please upload a valid Zomato dataset.")
    st.stop()

# ---------- DATA CLEANING ----------
df.drop_duplicates(inplace=True)
df.dropna(subset=required_cols, inplace=True)

# ---------- SIDEBAR FILTER ----------
st.sidebar.header("🔍 Filter Options")

city_list = sorted(df["City"].dropna().unique())
city = st.sidebar.selectbox("Select City", ["All"] + city_list)

if city != "All":
    df = df[df["City"] == city]

# ---------- KPIs ----------
col1, col2, col3 = st.columns(3)
col1.metric("🏙️ Total Restaurants", len(df))
col2.metric("⭐ Average Rating", round(df["Aggregate rating"].mean(), 2))
col3.metric("💰 Avg Cost for Two", int(df["Average Cost for two"].mean()))

st.divider()

# ---------- CHART 1: TOP CUISINES ----------
top_cuisines = df["Cuisines"].value_counts().head(10).reset_index()
top_cuisines.columns = ["Cuisine", "Count"]

fig1 = px.bar(
    top_cuisines, x="Cuisine", y="Count", color="Count",
    title="🍛 Top 10 Cuisines by Number of Restaurants",
    color_continuous_scale="Agsunset", template="plotly_white"
)
st.plotly_chart(fig1, use_container_width=True)

# ---------- CHART 2: RATING DISTRIBUTION ----------
rating_dist = df["Aggregate rating"].round().value_counts().sort_index().reset_index()
rating_dist.columns = ["Rating", "Count"]

fig2 = px.pie(
    rating_dist, names="Rating", values="Count",
    title="⭐ Restaurant Distribution by Rating",
    color_discrete_sequence=px.colors.sequential.RdPu
)
st.plotly_chart(fig2, use_container_width=True)

# ---------- CHART 3: MAP ----------
if {"Latitude", "Longitude"}.issubset(df.columns):
    st.markdown("### 🗺️ Restaurant Locations")
    fig3 = px.scatter_mapbox(
        df,
        lat="Latitude", lon="Longitude",
        hover_name="Restaurant Name",
        hover_data=["City", "Cuisines", "Aggregate rating"],
        color="Aggregate rating",
        color_continuous_scale="sunset",
        mapbox_style="carto-positron",
        zoom=4, size_max=8
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("⚠️ Latitude/Longitude columns not found — map cannot be displayed.")
