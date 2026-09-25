import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpotCheck Kenya | Real-Time Navigation",
    page_icon="📍",
    layout="wide"
)

# --- HAVERSINE DISTANCE CALCULATOR ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- DATASET WITH SITE IMAGE URLS ---
@st.cache_data
def load_data():
    data = [
        {
            "name": "Mai Mahiu Rift Valley Viewpoint", 
            "lat": -1.0858, 
            "lon": 36.5772, 
            "category": "Scenic Viewpoint", 
            "route": "Nairobi-Naivasha (A104)", 
            "county": "Nakuru",
            "image_url": "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Hell's Gate National Park", 
            "lat": -0.8872, 
            "lon": 36.3153, 
            "category": "National Park / Gorge", 
            "route": "Nairobi-Naivasha (A104)", 
            "county": "Nakuru",
            "image_url": "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Iten High Altitude Rim Viewpoint", 
            "lat": 0.6728, 
            "lon": 35.5081, 
            "category": "Scenic Viewpoint", 
            "route": "Eldoret-Iten (C51)", 
            "county": "Elgeyo Marakwet",
            "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Torok Waterfall", 
            "lat": 0.4333, 
            "lon": 35.5333, 
            "category": "Waterfall Hike", 
            "route": "Eldoret-Iten (C51)", 
            "county": "Elgeyo Marakwet",
            "image_url": "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Ngare Ndare Canopy Walk", 
            "lat": 0.2833, 
            "lon": 37.3500, 
            "category": "Forest / Canopy", 
            "route": "Nairobi-Nanyuki (A2)", 
            "county": "Meru / Laikipia",
            "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Lake Magadi Hot Springs", 
            "lat": -1.9000, 
            "lon": 36.2833, 
            "category": "Hot Springs", 
            "route": "Kajiado-Magadi", 
            "county": "Kajiado",
            "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80"
        },
    ]
    return pd.DataFrame(data)

df = load_data()

st.title("📍 SpotCheck Kenya")
st.caption("Interactive Road Trip Corridors, Distance Matrix & Voice-Assisted Navigation")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Navigation Setup")

# 1. User Location Inputs (Default: Nairobi Center)
st.sidebar.subheader("1. Your Current Location")
user_lat = st.sidebar.number_input("Latitude", value=-1.286389, format="%.6f")
user_lon = st.sidebar.number_input("Longitude", value=36.817223, format="%.6f")

# 2. Travel Mode Selection
st.sidebar.subheader("2. Mode of Transport")
mode = st.sidebar.selectbox(
    "Select Travel Mode",
    ["Vehicle (Driving)", "Walking", "Cycling", "Airplane (Direct Flight)"]
)

mode_speeds = {
    "Vehicle (Driving)": {"speed": 70, "gmaps_mode": "driving"},
    "Walking": {"speed": 5, "gmaps_mode": "walking"},
    "Cycling": {"speed": 15, "gmaps_mode": "bicycling"},
    "Airplane (Direct Flight)": {"speed": 500, "gmaps_mode": "driving"}
}

# --- CALCULATE DISTANCES AND ETA ---
df["Distance_km"] = df.apply(
    lambda row: haversine_distance(user_lat, user_lon, row["lat"], row["lon"]), axis=1
)

speed = mode_speeds[mode]["speed"]
df["ETA_hours"] = df["Distance_km"] / speed

# Sort by nearest spot
df = df.sort_values(by="Distance_km").reset_index(drop=True)

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🏁 Nearest Road Trip Spots")
    
    selected_spot_name = st.selectbox("Select a spot for detailed route assist:", df["name"])
    spot = df[df["name"] == selected_spot_name].iloc[0]
    
    # SITE IMAGE DISPLAY
    st.image(spot["image_url"], caption=f"Site View: {spot['name']}", use_column_width=True)
    
    st.markdown(f"**Category:** {spot['category']} | **Route Corridor:** {spot['route']}")
    st.markdown(f"**County:** {spot['county']}")
    
    # Distance and ETA Card
    st.metric(
        label=f"Distance from Your Location ({mode})",
        value=f"{spot['Distance_km']:.2f} km",
        delta=f"~{spot['ETA_hours']*60:.0f} mins estimated" if spot['ETA_hours'] < 1 else f"~{spot['ETA_hours']:.1f} hrs estimated"
    )
    
    # --- GOOGLE MAPS DIRECT LINK ---
    gmaps_mode = mode_speeds[mode]["gmaps_mode"]
    google_maps_url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={user_lat},{user_lon}"
        f"&destination={spot['lat']},{spot['lon']}"
        f"&travelmode={gmaps_mode}"
    )
    
    st.link_button("🚗 Open Live Turn-by-Turn Directions in Google Maps", google_maps_url)
    
    # --- IN-APP VOICE ASSISTANT ---
    st.subheader("🔊 Voice Assistant")
    voice_script = f"Navigating to {spot['name']} in {spot['county']} county. Distance is {spot['Distance_km']:.1f} kilometers via the {spot['route']} corridor. Estimated travel time by {mode} is approximately {spot['ETA_hours']*60:.0f} minutes."
    
    speech_html = f"""
        <script>
        function speakRoute() {{
            var msg = new SpeechSynthesisUtterance();
            msg.text = "{voice_script}";
            msg.rate = 0.95;
            window.speechSynthesis.speak(msg);
        }}
        </script>
        <button onclick="speakRoute()" style="
            background-color: #0E1117;
            color: #FFFFFF;
            border: 1px solid #4B5563;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            width: 100%;">
            📢 Play Voice Navigation Brief
        </button>
    """
    st.components.v1.html(speech_html, height=60)

with col2:
    st.subheader("🗺️ Live Route Map")
    
    # Initialize Map centered between user and selected spot
    center_lat = (user_lat + spot["lat"]) / 2
    center_lon = (user_lon + spot["lon"]) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles="OpenStreetMap")
    
    # User Location Marker
    folium.Marker(
        location=[user_lat, user_lon],
        popup="Your Location",
        tooltip="Your Location",
        icon=folium.Icon(color="red", icon="user", prefix="fa")
    ).add_to(m)
    
    # Destination Marker with HTML Image Popup inside Folium
    popup_html = f"""
        <div style="width:200px">
            <b>{spot['name']}</b><br>
            <img src="{spot['image_url']}" width="100%" style="border-radius:4px; margin-top:5px;"><br>
            <small>{spot['category']} - {spot['county']}</small>
        </div>
    """
    
    folium.Marker(
        location=[spot["lat"], spot["lon"]],
        popup=folium.Popup(popup_html, max_width=220),
        tooltip=spot["name"],
        icon=folium.Icon(color="green", icon="star", prefix="fa")
    ).add_to(m)
    
    # Direct Route Line
    folium.PolyLine(
        locations=[[user_lat, user_lon], [spot["lat"], spot["lon"]]],
        color="blue",
        weight=4,
        opacity=0.7,
        tooltip=f"Route to {spot['name']}"
    ).add_to(m)
    
    st_folium(m, width="100%", height=500)
