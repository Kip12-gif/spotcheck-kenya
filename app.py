import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import math

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpotCheck Kenya | Safari & Road Trip Navigator",
    page_icon="📍",
    layout="wide"
)

# --- CUSTOM CSS WITH SCENIC SAFARI BACKGROUND ---
st.markdown("""
    <style>
    /* Full App Background: Scenic Kenyan Safari Landscape */
    .stApp {
        background: linear-gradient(
            rgba(14, 17, 23, 0.78), 
            rgba(14, 17, 23, 0.88)
        ), 
        url('https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Modern Card Container Styling */
    .css-card {
        background-color: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: #FFFFFF;
    }
    
    /* Header Aesthetics */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #F97316; /* Warm Safari Orange */
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #E5E7EB;
        margin-bottom: 1.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- HAVERSINE DISTANCE CALCULATOR ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# --- DATASET WITH FULL KENYAN SPOTS & CORRIDORS ---
@st.cache_data
def load_data():
    data = [
        {
            "name": "Mai Mahiu Rift Valley Viewpoint", 
            "lat": -1.0858, 
            "lon": 36.5772, 
            "category": "Scenic Viewpoint", 
            "route": "Nairobi-Naivasha Corridor (A104)", 
            "county": "Nakuru",
            "image_url": "https://images.unsplash.com/photo-1547471080-7cc2caa01a7e?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Hell's Gate National Park", 
            "lat": -0.8872, 
            "lon": 36.3153, 
            "category": "National Park / Gorge", 
            "route": "Nairobi-Naivasha Corridor (A104)", 
            "county": "Nakuru",
            "image_url": "https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Iten High Altitude Rim Viewpoint", 
            "lat": 0.6728, 
            "lon": 35.5081, 
            "category": "Scenic Viewpoint / Athletics", 
            "route": "Eldoret-Iten Highway (C51)", 
            "county": "Elgeyo Marakwet",
            "image_url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Torok Waterfall", 
            "lat": 0.4333, 
            "lon": 35.5333, 
            "category": "Waterfall Hike", 
            "route": "Eldoret-Iten Highway (C51)", 
            "county": "Elgeyo Marakwet",
            "image_url": "https://images.unsplash.com/photo-1432405972618-c60b0225b8f9?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Ngare Ndare Canopy Walk", 
            "lat": 0.2833, 
            "lon": 37.3500, 
            "category": "Forest / Canopy Walk", 
            "route": "Nairobi-Nanyuki Highway (A2)", 
            "county": "Meru / Laikipia",
            "image_url": "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=800&q=80"
        },
        {
            "name": "Lake Magadi Hot Springs", 
            "lat": -1.9000, 
            "lon": 36.2833, 
            "category": "Hot Springs", 
            "route": "Kajiado-Magadi Road", 
            "county": "Kajiado",
            "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=800&q=80"
        },
    ]
    return pd.DataFrame(data)

df = load_data()

# --- APP HEADER ---
st.markdown('<div class="main-title">📍 SpotCheck Kenya</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-Time Road Trip Corridors, Nearest Routes & Voice Assistant</div>', unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Navigation Setup")

st.sidebar.subheader("1. Mode of Transport")
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

# --- BROWSER GEOLOCATION PROMPT ---
st.info("📍 **Location Request:** Please allow browser location access when prompted.")

loc = get_geolocation()

# Default fallback location (Nairobi CBD) if permission is still pending
user_lat = -1.286389
user_lon = 36.817223

if loc and 'coords' in loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"📍 **Live GPS Acquired!** Latitude: `{user_lat:.5f}` | Longitude: `{user_lon:.5f}`")
else:
    st.warning("⚠️ Using default reference point (Nairobi CBD). Enable location access to calculate exact distance from your phone/laptop.")

# --- CALCULATE DISTANCES & ETAS ---
df["Distance_km"] = df.apply(
    lambda row: haversine_distance(user_lat, user_lon, row["lat"], row["lon"]), axis=1
)
speed = mode_speeds[mode]["speed"]
df["ETA_hours"] = df["Distance_km"] / speed

# Sort dataframe by nearest spot
df = df.sort_values(by="Distance_km").reset_index(drop=True)

st.markdown("---")

# --- MAIN DASHBOARD LAYOUT ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("🏁 Nearest Road Trip Spots")
    
    selected_spot_name = st.selectbox("Select a spot to inspect route & details:", df["name"])
    spot = df[df["name"] == selected_spot_name].iloc[0]
    
    # SITE PREVIEW IMAGE
    st.image(
        spot["image_url"], 
        caption=f"Site View: {spot['name']} ({spot['county']} County)", 
        use_container_width=True
    )
    
    st.markdown(f"**Category:** `{spot['category']}`")
    st.markdown(f"**Road Corridor:** `{spot['route']}`")
    st.markdown(f"**County:** `{spot['county']}`")
    
    # Distance and ETA Metric
    st.metric(
        label=f"Calculated Distance ({mode})",
        value=f"{spot['Distance_km']:.2f} km",
        delta=f"~{spot['ETA_hours']*60:.0f} mins ETA" if spot['ETA_hours'] < 1 else f"~{spot['ETA_hours']:.1f} hrs ETA"
    )
    
    # --- DEEP LINK TO GOOGLE MAPS ---
    gmaps_mode = mode_speeds[mode]["gmaps_mode"]
    google_maps_url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={user_lat},{user_lon}"
        f"&destination={spot['lat']},{spot['lon']}"
        f"&travelmode={gmaps_mode}"
    )
    
    st.link_button("🚗 Open Turn-by-Turn Directions in Google Maps App", google_maps_url)
    
    # --- IN-APP VOICE ASSISTANT ---
    st.subheader("🔊 Voice Assistant")
    voice_script = f"Navigating to {spot['name']} in {spot['county']} county. Distance is {spot['Distance_km']:.1f} kilometers via the {spot['route']}. Estimated travel time by {mode} is approximately {spot['ETA_hours']*60:.0f} minutes."
    
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
            background-color: #F97316;
            color: #FFFFFF;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            font-size: 16px;
            width: 100%;">
            📢 Play Voice Navigation Brief
        </button>
    """
    st.components.v1.html(speech_html, height=65)

with col2:
    st.subheader("🗺️ Live Spatial Overlay & Boundary Route")
    
    # Center map between user GPS and destination spot
    center_lat = (user_lat + spot["lat"]) / 2
    center_lon = (user_lon + spot["lon"]) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="OpenStreetMap")
    
    # Marker 1: User Location
    folium.Marker(
        location=[user_lat, user_lon],
        popup="Your Current Position",
        tooltip="Your Position",
        icon=folium.Icon(color="red", icon="user", prefix="fa")
    ).add_to(m)
    
    # Marker 2: Destination Spot with Image Popup
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
    
    # Direct Line/Vector Connecting Origin & Destination
    folium.PolyLine(
        locations=[[user_lat, user_lon], [spot["lat"], spot["lon"]]],
        color="#F97316",
        weight=4,
        opacity=0.8,
        tooltip=f"Route Vector: {spot['name']}"
    ).add_to(m)
    
    st_folium(m, width="100%", height=530)
