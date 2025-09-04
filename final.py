import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import json
from urllib.request import urlopen
import plotly.express as px

# -----------------------------
# Streamlit page config
# -----------------------------
st.set_page_config(page_title="Noise Pollution Dashboard", layout="wide")

# -----------------------------
# Sidebar Navigation
# -----------------------------
st.sidebar.title("📄 Navigation")
page = st.sidebar.radio("Go to", [
    "Main Website", "Maharashtra Map", "Noise Heatmap Generator",
    "Noise Charts 2019", "Cities", "Datasets"
])

# -----------------------------
# MAIN WEBSITE
# -----------------------------
if page == "Main Website":
    st.title("Welcome to the Main Website")
    st.write("This is your homepage content.")

# -----------------------------
# NOISE POLLUTION HEATMAP GENERATOR
# -----------------------------
if page == "Noise Heatmap Generator":
    st.title("📊 Noise Pollution Heatmap Generator")

    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.subheader("📑 Data Preview")
        st.dataframe(df.head())

        required_columns = ["latitude", "longitude", "noise_level"]
        if all(col in df.columns for col in required_columns):
            map_center = [df["latitude"].mean(), df["longitude"].mean()]
            m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB positron")
            heat_data = df[["latitude", "longitude", "noise_level"]].values.tolist()
            HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)

            st.subheader("🌍 Heatmap Visualization")
            st_folium(m, width=1000, height=600)

            st.subheader("📈 Noise Level Statistics")
            st.write(f"Average Noise Level: {df['noise_level'].mean():.2f} dB")
            st.write(f"Maximum Noise Level: {df['noise_level'].max():.2f} dB")
            st.write(f"Minimum Noise Level: {df['noise_level'].min():.2f} dB")
        else:
            st.error(f"CSV must contain columns: {required_columns}")
    else:
        st.info("Please upload a CSV file with columns: latitude, longitude, noise_level")

# -----------------------------
# MAHARASHTRA MAP
# -----------------------------
if page == "Maharashtra Map":
    st.title("🗺️ Maharashtra — Main Map")

    MA_CENTER = (19.7515, 75.7139)
    DEFAULT_ZOOM = 6

    zoom = st.sidebar.slider("Zoom level", min_value=5, max_value=10, value=DEFAULT_ZOOM)
    tile = st.sidebar.selectbox("Tile style", ["CartoDB positron", "OpenStreetMap", "Stamen Terrain", "Stamen Toner"])
    show_markers = st.sidebar.checkbox("Show major city markers", True)
    show_heatmap = st.sidebar.checkbox("Show heatmap (requires CSV with lat/lon/value)", False)

    # GeoJSON overlay
    st.sidebar.subheader("Boundary / GeoJSON Overlay")
    geojson_option = st.sidebar.radio("GeoJSON input", ["None", "Upload file", "URL"], index=0)
    geojson_data = None

    if geojson_option == "Upload file":
        uploaded_geo = st.sidebar.file_uploader("Upload GeoJSON (.geojson/.json)", type=["geojson", "json"])
        if uploaded_geo:
            try:
                geojson_data = json.load(uploaded_geo)
                st.sidebar.success("GeoJSON loaded (upload).")
            except Exception as e:
                st.sidebar.error(f"Failed to parse uploaded GeoJSON: {e}")
    elif geojson_option == "URL":
        geojson_url = st.sidebar.text_input("Enter GeoJSON URL (raw GitHub link etc.)")
        if geojson_url:
            try:
                with urlopen(geojson_url) as response:
                    geojson_data = json.load(response)
                st.sidebar.success("GeoJSON loaded (URL).")
            except Exception as e:
                st.sidebar.error(f"Failed to fetch/parse GeoJSON: {e}")

    # Optional CSV for heatmap
    uploaded_csv = None
    csv_df = None
    if show_heatmap:
        uploaded_csv = st.sidebar.file_uploader("Upload CSV for heatmap", type=["csv"])
        if uploaded_csv:
            try:
                csv_df = pd.read_csv(uploaded_csv)
                st.sidebar.success("CSV loaded for heatmap.")
            except Exception as e:
                st.sidebar.error(f"Failed to read CSV: {e}")

    # Major Maharashtra cities
    maharashtra_cities = [
        ("Mumbai", 19.0760, 72.8777, 72.0),
        ("Pune", 18.5204, 73.8567, 70.5),
        ("Nagpur", 21.1458, 79.0882, 66.0),
        ("Nashik", 19.9975, 73.7898, 68.2),
        ("Thane", 19.2183, 72.9781, 73.1),
        ("Aurangabad", 19.8762, 75.3433, 71.9),
        ("Solapur", 17.6599, 75.9064, 69.8),
        ("Kolhapur", 16.7045, 74.2444, 70.2),
        ("Amravati", 20.9320, 77.7790, 67.5),
        ("Akola", 20.7057, 76.9840, 65.8),
    ]

    m = folium.Map(location=MA_CENTER, zoom_start=zoom, tiles=tile)

    if geojson_data:
        folium.GeoJson(
            geojson_data,
            name="Maharashtra boundary",
            style_function=lambda feat: {"fillColor": "transparent", "color": "#ff7800", "weight": 2},
        ).add_to(m)

    if show_markers:
        for name, lat, lon, val in maharashtra_cities:
            folium.Marker(location=(lat, lon), popup=f"{name}", tooltip=name).add_to(m)

    if show_heatmap:
        if csv_df is not None:
            lower_cols = [c.lower() for c in csv_df.columns]
            if "latitude" in lower_cols and "longitude" in lower_cols:
                lat_col = [c for c in csv_df.columns if c.lower() == "latitude"][0]
                lon_col = [c for c in csv_df.columns if c.lower() == "longitude"][0]
                val_col = None
                for candidate in ["value", "noise", "noise_level", "average_db", "avg_db"]:
                    matches = [c for c in csv_df.columns if c.lower() == candidate]
                    if matches:
                        val_col = matches[0]
                        break
                if val_col is None:
                    heat_data = csv_df[[lat_col, lon_col]].dropna().values.tolist()
                    HeatMap(heat_data, radius=15, blur=10).add_to(m)
                else:
                    heat_data = csv_df[[lat_col, lon_col, val_col]].dropna().values.tolist()
                    HeatMap(heat_data, radius=15, blur=10).add_to(m)
        else:
            sample_heat = [[lat, lon, val] for (_, lat, lon, val) in maharashtra_cities]
            HeatMap(sample_heat, radius=20, blur=15).add_to(m)

    folium.LayerControl().add_to(m)
    st.subheader("Maharashtra Map")
    st.write("Center:", MA_CENTER)
    st_folium(m, width=1000, height=650)

    st.markdown("---")
    st.subheader("Major Maharashtra cities (sample values)")
    cities_df = pd.DataFrame([{"city": name, "latitude": lat, "longitude": lon, "sample_value": val} 
                              for (name, lat, lon, val) in maharashtra_cities])
    st.dataframe(cities_df)

# -----------------------------
# NOISE POLLUTION CHARTS (2019)
# -----------------------------
if page == "Noise Charts 2019":
    st.title("📊 Noise Pollution — 2019")

    data_2019 = {
        "City": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Solapur"],
        "Average_dB": [72.5, 71.2, 66.5, 67.8, 70.1, 69.0],
        "Peak_dB": [84.2, 82.5, 80.3, 81.1, 83.7, 82.0],
    }
    df_2019 = pd.DataFrame(data_2019)

    # Line chart
    df_melted = df_2019.melt(id_vars="City", value_vars=["Average_dB", "Peak_dB"],
                             var_name="Noise Type", value_name="dB Level")
    fig_line = px.line(df_melted, x="City", y="dB Level", color="Noise Type", markers=True,
                       title="Average vs Peak Noise Levels by City (2019)")
    fig_line.update_layout(yaxis_title="Noise Level (dB)")
    st.plotly_chart(fig_line, use_container_width=True)

    # Bar chart
    fig_bar = px.bar(df_2019, x="City", y="Average_dB", color="Average_dB", text="Average_dB",
                     title="Average Noise Levels by City (2019)")
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(yaxis_title="Average Noise Level (dB)")
    st.plotly_chart(fig_bar, use_container_width=True)

    # Pie chart
    fig_pie = px.pie(df_2019, names="City", values="Average_dB", title="City-wise Contribution (2019)",
                     hole=0.3)
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie, use_container_width=True)

    # Scatter chart
    fig_scatter = px.scatter(df_2019, x="Average_dB", y="Peak_dB", size="Peak_dB", color="City",
                             hover_name="City", text="City", title="Average vs Peak Noise Levels")
    fig_scatter.update_traces(textposition="top center")
    fig_scatter.update_layout(xaxis_title="Average Noise Level (dB)", yaxis_title="Peak Noise Level (dB)")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("📑 Dataset Preview")
    st.dataframe(df_2019)

# -----------------------------
# CITIES PAGE
# -----------------------------
if page == "Cities":
    st.title("🏙 Cities of Maharashtra")

    col1, col2 = st.columns(2)
    col3, col4, col5 = st.columns(3)

    # Row 1
    with col1:
        st.image(r"C:\Users\DNYANDIP\Desktop\anjali\WhatsApp Image 2025-09-04 at 03.39.55_197fb81b.jpg",
                 use_container_width=True)
        st.caption("Amravati Maharashtra")
        if st.button("➡ Amravati Data"):
            st.write("Showing Amravati Data...")

    with col2:
        st.image(r"C:\Users\DNYANDIP\Desktop\anjali\WhatsApp Image 2025-09-04 at 03.39.55_5d9ac936.jpg",
                 use_container_width=True)
        st.caption("Nagpur Maharashtra")
        if st.button("➡ Nagpur Data"):
            st.write("Showing Nagpur Data...")

    # Row 2
    with col3:
        st.image(r"C:\Users\DNYANDIP\Desktop\anjali\WhatsApp Image 2025-09-04 at 03.39.56_19c731ae.jpg",
                 use_container_width=True)
        st.caption("Mumbai Maharashtra")
        if st.button("➡ Mumbai Data"):
            st.write("Showing Mumbai Data...")

    with col4:
        st.image(r"C:\Users\DNYANDIP\Desktop\anjali\WhatsApp Image 2025-09-04 at 03.39.56_aae06bcf.jpg",
                 use_container_width=True)
        st.caption("Pune Maharashtra")
        if st.button("➡ Pune Data"):
            st.write("Showing Pune Data...")

    with col5:
        st.image(r"C:\Users\DNYANDIP\Desktop\anjali\WhatsApp Image 2025-09-04 at 03.39.55_1bb4ea71.jpg",
                 use_container_width=True)
        st.caption("Nashik Maharashtra")
        if st.button("➡ Nashik Data"):
            st.write("Showing Nashik Data...")

# -----------------------------
# DATASETS PAGE
# -----------------------------
if page == "Datasets":
    st.title("Noise Pollution Datasets")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        st.write("### Preview of Dataset")
        st.dataframe(df)
        st.write("### Basic Info")
        st.write(df.describe())
