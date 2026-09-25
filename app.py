import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import math

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpotCheck Kenya | Travel & Corridor Navigator",
    page_icon="📍",
    layout="wide"
)

# --- HIGH CONTRAST & LIGHT OVERLAY SAFARI CSS ---
st.markdown("""
    <style>
    /* Full App Background with high-contrast semi-transparent light overlay */
    .stApp {
        background: linear-gradient(
            rgba(255, 255, 255, 0.88), 
            rgba(243, 244, 246, 0.92)
        ), 
        url('https://upload.wikimedia.org/wikipedia/commons/e/e0/Giraffe_in_Masai_Mara.jpg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Dark readable text for global contrast */
    body, p, div, span {
        color: #1F2937 !important;
    }

    /* Header Aesthetics */
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #C2410C; /* Kenyan Ochre/Orange */
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #374151;
        font-weight: 500;
        margin-bottom: 1.2rem;
    }
    
    /* Styled Content Cards */
    .stMetric {
        background-color: #FFFFFF;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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

# --- EXPANDED AUTHENTIC KENYA DATASET ---
@st.cache_data
def load_data():
    data = [
        # --- NAIROBI - NAIVASHA - NAKURU (A104) ---
        {
            "name": "Mai Mahiu Great Rift Valley Viewpoint", 
            "lat": -1.0858, 
            "lon": 36.5772, 
            "category": "Scenic Viewpoint", 
            "route": "Nairobi - Naivasha Highway (A104)", 
            "county": "Nakuru",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Great_Rift_Valley_Kenya.jpg/800px-Great_Rift_Valley_Kenya.jpg"
        },
        {
            "name": "Hell's Gate National Park & Gorge", 
            "lat": -0.8872, 
            "lon": 36.3153, 
            "category": "National Park / Gorge", 
            "route": "Nairobi - Naivasha Highway (A104)", 
            "county": "Nakuru",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Hells_Gate_National_Park_Gorge_2.jpg/800px-Hells_Gate_National_Park_Gorge_2.jpg"
        },
        {
            "name": "Menengai Crater Viewpoint", 
            "lat": -0.2000, 
            "lon": 36.0667, 
            "category": "Volcanic Crater / Viewpoint", 
            "route": "Nairobi - Naivasha Highway (A104)", 
            "county": "Nakuru",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Menengai_Crater.jpg/800px-Menengai_Crater.jpg"
        },

        # --- ELDORET - ITEN - KABARNET (C51 / B7) ---
        {
            "name": "Iten High Altitude Rim Viewpoint", 
            "lat": 0.6728, 
            "lon": 35.5081, 
            "category": "Scenic Viewpoint / Athletics", 
            "route": "Eldoret - Iten Road (C51)", 
            "county": "Elgeyo Marakwet",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Iten_Kenya.jpg/800px-Iten_Kenya.jpg"
        },
        {
            "name": "Torok Waterfall", 
            "lat": 0.4333, 
            "lon": 35.5333, 
            "category": "Waterfall Hike", 
            "route": "Eldoret - Iten Road (C51)", 
            "county": "Elgeyo Marakwet",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Kenya_waterfall.jpg/800px-Kenya_waterfall.jpg"
        },

        # --- NAIROBI - NANYUKI - MARSABIT (A2) ---
        {
            "name": "Ngare Ndare Forest Canopy Walk", 
            "lat": 0.2833, 
            "lon": 37.3500, 
            "category": "Forest / Canopy Walk", 
            "route": "Nairobi - Nanyuki Highway (A2)", 
            "county": "Meru / Laikipia",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Ngare_Ndare_Forest_Canopy_Walk.jpg/800px-Ngare_Ndare_Forest_Canopy_Walk.jpg"
        },
        {
            "name": "Thomson's Falls (Nyahururu)", 
            "lat": 0.0441, 
            "lon": 36.3686, 
            "category": "Waterfall Hike", 
            "route": "Nyeri - Nyahururu Road (B21)", 
            "county": "Laikipia",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Thomson%27s_Falls.jpg/800px-Thomson%27s_Falls.jpg"
        },
        {
            "name": "Mt. Ololokwe Sacred Mountain", 
            "lat": 0.8500, 
            "lon": 37.5333, 
            "category": "Scenic Viewpoint", 
            "route": "Nairobi - Nanyuki Highway (A2)", 
            "county": "Samburu",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Mount_Ololokwe.jpg/800px-Mount_Ololokwe.jpg"
        },

        # --- KAJIADO - MAGADI / MARA CORRIDOR ---
        {
            "name": "Lake Magadi Hot Springs", 
            "lat": -1.9000, 
            "lon": 36.2833, 
            "category": "Hot Springs", 
            "route": "Kajiado - Magadi Road", 
            "county": "Kajiado",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Lake_Magadi.jpg/800px-Lake_Magadi.jpg"
        },
        {
            "name": "Masai Mara River Crossing Point", 
            "lat": -1.4000, 
            "lon": 35.0000, 
            "category": "National Reserve", 
            "route": "Narok - Sekenani Corridor (C12)", 
            "county": "Narok",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Wildebeest_crossing_the_Mara_River.jpg/800px-Wildebeest_crossing_the_Mara_River.jpg"
        },

        # --- NAIROBI - MOMBASA HIGHWAY (A109) & WESTERN ---
        {
            "name": "Fort Jesus Historic Monument", 
            "lat": -4.0632, 
            "lon": 39.6773, 
            "category": "Historical Heritage", 
            "route": "Nairobi - Mombasa Highway (A109)", 
            "county": "Mombasa",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Fort_Jesus_Mombasa_Kenya.jpg/800px-Fort_Jesus_Mombasa_Kenya.jpg"
        },
        {
            "name": "Kisumu Impala Sanctuary", 
            "lat": -0.1167, 
            "lon": 34.7500, 
            "category": "Wildlife Sanctuary", 
            "route": "Nakuru - Kisumu Highway (B1)", 
            "county": "Kisumu",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Impala_in_Kisumu.jpg/800px-Impala_in_Kisumu.jpg"
        }
    ]
    return pd.DataFrame(data)

df_all = load_data()

# --- APP HEADER ---
st.markdown('<div class="main-title">📍 SpotCheck Kenya</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Real-Time Corridor Navigator, Distance Matrix & Voice Assist</div>', unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Navigation Setup")

# 1. Road Corridor Filter (RESTORED)
st.sidebar.subheader("1. Road Corridor Filter")
all_routes = ["All Kenya Corridors"] + sorted(list(df_all["route"].unique()))
selected_route = st.sidebar.selectbox("Filter by Highway / Corridor:", all_routes)

# Filter Dataframe by Corridor
if selected_route != "All Kenya Corridors":
    df = df_all[df_all["route"] == selected_route].copy()
else:
    df = df_all.copy()

# 2. Category Filter
st.sidebar.subheader("2. Spot Category")
all_categories = ["All Categories"] + sorted(list(df_all["category"].unique()))
selected_cat = st.sidebar.selectbox("Filter by Category:", all_categories)

if selected_cat != "All Categories":
    df = df[df["category"] == selected_cat]

# 3. Mode of Transport Selection
st.sidebar.subheader("3. Mode of Transport")
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

# --- BROWSER GEOLOCATION CAPTURE ---
st.info("📍 **GPS Check:** Please allow browser location access when prompted.")

loc = get_geolocation()

# Default fallback location (Nairobi CBD)
user_lat = -1.286389
user_lon = 36.817223

if loc and 'coords' in loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"📍 **Live GPS Detected!** Latitude: `{user_lat:.5f}` | Longitude: `{user_lon:.5f}`")
else:
    st.warning("⚠️ Location access pending or disabled. Using reference point (Nairobi CBD). Enable browser location for precise distances.")

# --- DISTANCE & ETA CALCULATION ---
if not df.empty:
    df["Distance_km"] = df.apply(
        lambda row: haversine_distance(user_lat, user_lon, row["lat"], row["lon"]), axis=1
    )
    speed = mode_speeds[mode]["speed"]
    df["ETA_hours"] = df["Distance_km"] / speed
    df = df.sort_values(by="Distance_km").reset_index(drop=True)

st.markdown("---")

# --- MAIN DASHBOARD LAYOUT ---
if df.empty:
    st.error("No spots found matching the selected corridor and category combination.")
else:
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("🏁 Nearest Road Trip Spots")
        
        selected_spot_name = st.selectbox("Select a spot to inspect route & details:", df["name"])
        spot = df[df["name"] == selected_spot_name].iloc[0]
        
        # REAL IMAGE DISPLAY
        st.image(
            spot["image_url"], 
            caption=f"Site Photo: {spot['name']} ({spot['county']} County)", 
            use_container_width=True
        )
        
        st.markdown(f"**Category:** `{spot['category']}`")
        st.markdown(f"**Road Corridor:** `{spot['route']}`")
        st.markdown(f"**County:** `{spot['county']}`")
        
        # Distance and ETA Card
        st.metric(
            label=f"Calculated Distance ({mode})",
            value=f"{spot['Distance_km']:.2f} km",
            delta=f"~{spot['ETA_hours']*60:.0f} mins ETA" if spot['ETA_hours'] < 1 else f"~{spot['ETA_hours']:.1f} hrs ETA"
        )
        
        # GOOGLE MAPS DEEP LINK
        gmaps_mode = mode_speeds[mode]["gmaps_mode"]
        google_maps_url = (
            f"https://www.google.com/maps/dir/?api=1"
            f"&origin={user_lat},{user_lon}"
            f"&destination={spot['lat']},{spot['lon']}"
            f"&travelmode={gmaps_mode}"
        )
        
        st.link_button("🚗 Open Turn-by-Turn Directions in Google Maps", google_maps_url)
        
        # IN-APP VOICE ASSISTANT
        st.subheader("🔊 Voice Navigation Brief")
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
                background-color: #C2410C;
                color: #FFFFFF;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: bold;
                font-size: 15px;
                width: 100%;">
                📢 Play Voice Navigation Brief
            </button>
        """
        st.components.v1.html(speech_html, height=65)

    with col2:
        st.subheader("🗺️ Live Spatial Route Map")
        
        # Center map between origin and spot
        center_lat = (user_lat + spot["lat"]) / 2
        center_lon = (user_lon + spot["lon"]) / 2
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="OpenStreetMap")
        
        # User Marker
        folium.Marker(
            location=[user_lat, user_lon],
            popup="Your Location",
            tooltip="Your Location",
            icon=folium.Icon(color="red", icon="user", prefix="fa")
        ).add_to(m)
        
        # Destination Marker with Image Popup
        popup_html = f"""
            <div style="width:210px">
                <b>{spot['name']}</b><br>
                <img src="{spot['image_url']}" width="100%" style="border-radius:4px; margin-top:5px; height:120px; object-fit:cover;"><br>
                <small>{spot['category']} | {spot['county']}</small>
            </div>
        """
        
        folium.Marker(
            location=[spot["lat"], spot["lon"]],
            popup=folium.Popup(popup_html, max_width=230),
            tooltip=spot["name"],
            icon=folium.Icon(color="green", icon="star", prefix="fa")
        ).add_to(m)
        
        # Polyline connecting Origin & Destination
        folium.PolyLine(
            locations=[[user_lat, user_lon], [spot["lat"], spot["lon"]]],
            color="#C2410C",
            weight=4,
            opacity=0.8,
            tooltip=f"Direct Route Vector: {spot['name']}"
        ).add_to(m)
        
        st_folium(m, width="100%", height=540)
