import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Page Setup ----------
st.set_page_config(page_title="Zomato Dashboard", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #FFE29F 0%, #FFA99F 48%, #FF719A 100%);
    color: #2C2C2C;
}
h1 {
    text-align: center;
    color: #22223b;
    font-family: 'Helvetica', sans-serif;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🍽️ Zomato Food Delivery Dashboard</h1>", unsafe_allow_html=True)

# ---------- Load Data ----------
@st.cache_data
def load_data():
    df = pd.read_csv("zomato_restaurants.csv", encoding='latin-1')
    return df

df = load_data()

# ---------- Data Cleaning ----------
df.drop_duplicates(inplace=True)
df.dropna(subset=['City', 'Cuisines', 'Aggregate rating', 'Average Cost for two'], inplace=True)

# ---------- Sidebar Filters ----------
st.sidebar.header("🔍 Filter Options")
city_list = sorted(df['City'].dropna().unique())
city = st.sidebar.selectbox("Select City", ["All"] + list(city_list))

if city != "All":
    df = df[df['City'] == city]

# ---------- KPIs ----------
col1, col2, col3 = st.columns(3)
col1.metric("🏙️ Total Restaurants", df.shape[0])
col2.metric("⭐ Average Rating", round(df['Aggregate rating'].mean(), 2))
col3.metric("💰 Avg Cost for Two", int(df['Average Cost for two'].mean()))

# ---------- Charts ----------
# Top cuisines
top_cuisines = (
    df['Cuisines'].value_counts().head(10).reset_index()
)
top_cuisines.columns = ['Cuisine', 'Count']

fig1 = px.bar(
    top_cuisines, x='Cuisine', y='Count', color='Count',
    title="🍛 Top 10 Cuisines by Number of Restaurants",
    color_continuous_scale='Tealrose', template='plotly_white'
)
st.plotly_chart(fig1, use_container_width=True)

# Pie chart for rating distribution
rating_dist = (
    df['Aggregate rating'].round().value_counts().sort_index().reset_index()
)
rating_dist.columns = ['Rating', 'Count']

fig2 = px.pie(
    rating_dist, names='Rating', values='Count',
    title="⭐ Restaurant Distribution by Rating",
    color_discrete_sequence=px.colors.sequential.RdPu
)
st.plotly_chart(fig2, use_container_width=True)

# Map visualization
if {'Latitude', 'Longitude'}.issubset(df.columns):
    st.markdown("### 🗺️ Restaurant Locations")
    fig3 = px.scatter_mapbox(
        df, lat='Latitude', lon='Longitude', hover_name='Restaurant Name',
        hover_data=['City', 'Cuisines', 'Aggregate rating'],
        color='Aggregate rating', size_max=10, zoom=4,
        mapbox_style='carto-positron', color_continuous_scale='sunset'
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.warning("Latitude/Longitude columns not found in dataset.")
