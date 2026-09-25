import math
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpotCheck Kenya | Travel & Corridor Navigator",
    page_icon="📍",
    layout="wide",
)

# --- CLEAN & HIGH-CONTRAST STYLING ---
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #C2410C;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #4B5563;
        font-weight: 500;
        margin-bottom: 1.2rem;
    }
    .stMetric {
        background-color: #FFFFFF;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    .insight-box {
        background-color: #F3F4F6;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #C2410C;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- HAVERSINE DISTANCE CALCULATOR ---
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


# --- KENYA ROAD TRIP DATASET ---
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
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Great_Rift_Valley_Kenya.jpg/800px-Great_Rift_Valley_Kenya.jpg",
        },
        {
            "name": "Hell's Gate National Park & Gorge",
            "lat": -0.8872,
            "lon": 36.3153,
            "category": "National Park / Gorge",
            "route": "Nairobi - Naivasha Highway (A104)",
            "county": "Nakuru",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Hells_Gate_National_Park_Gorge_2.jpg/800px-Hells_Gate_National_Park_Gorge_2.jpg",
        },
        {
            "name": "Menengai Crater Viewpoint",
            "lat": -0.2000,
            "lon": 36.0667,
            "category": "Volcanic Crater / Viewpoint",
            "route": "Nairobi - Naivasha Highway (A104)",
            "county": "Nakuru",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Menengai_Crater.jpg/800px-Menengai_Crater.jpg",
        },
        # --- ELDORET - ITEN - KABARNET (C51 / B7) ---
        {
            "name": "Iten High Altitude Rim Viewpoint",
            "lat": 0.6728,
            "lon": 35.5081,
            "category": "Scenic Viewpoint / Athletics",
            "route": "Eldoret - Iten Road (C51)",
            "county": "Elgeyo Marakwet",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Iten_Kenya.jpg/800px-Iten_Kenya.jpg",
        },
        {
            "name": "Torok Waterfall",
            "lat": 0.4333,
            "lon": 35.5333,
            "category": "Waterfall Hike",
            "route": "Eldoret - Iten Road (C51)",
            "county": "Elgeyo Marakwet",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Kenya_waterfall.jpg/800px-Kenya_waterfall.jpg",
        },
        # --- NAIROBI - NANYUKI - MARSABIT (A2) ---
        {
            "name": "Ngare Ndare Forest Canopy Walk",
            "lat": 0.2833,
            "lon": 37.3500,
            "category": "Forest / Canopy Walk",
            "route": "Nairobi - Nanyuki Highway (A2)",
            "county": "Meru / Laikipia",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Ngare_Ndare_Forest_Canopy_Walk.jpg/800px-Ngare_Ndare_Forest_Canopy_Walk.jpg",
        },
        {
            "name": "Thomson's Falls (Nyahururu)",
            "lat": 0.0441,
            "lon": 36.3686,
            "category": "Waterfall Hike",
            "route": "Nyeri - Nyahururu Road (B21)",
            "county": "Laikipia",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Thomson%27s_Falls.jpg/800px-Thomson%27s_Falls.jpg",
        },
        # --- KAJIADO - MAGADI / MARA CORRIDOR ---
        {
            "name": "Lake Magadi Hot Springs",
            "lat": -1.9000,
            "lon": 36.2833,
            "category": "Hot Springs",
            "route": "Kajiado - Magadi Road",
            "county": "Kajiado",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Lake_Magadi.jpg/800px-Lake_Magadi.jpg",
        },
        {
            "name": "Fort Jesus Historic Monument",
            "lat": -4.0632,
            "lon": 39.6773,
            "category": "Historical Heritage",
            "route": "Nairobi - Mombasa Highway (A109)",
            "county": "Mombasa",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Fort_Jesus_Mombasa_Kenya.jpg/800px-Fort_Jesus_Mombasa_Kenya.jpg",
        },
    ]
    return pd.DataFrame(data)


df_all = load_data()

# --- INITIALIZE COMMUNITY INSIGHTS (IN-MEMORY SESSION STATE) ---
if "user_insights" not in st.session_state:
    st.session_state["user_insights"] = [
        {
            "spot": "Iten High Altitude Rim Viewpoint",
            "author": "Kipchoge Fan",
            "insight": "Best visited around 6:00 AM to see marathon runners training along the escarpment road!",
        },
        {
            "spot": "Mai Mahiu Great Rift Valley Viewpoint",
            "author": "RoadTripper254",
            "insight": "Watch out for heavy truck traffic on the descent. Stop by early for curio shop discounts.",
        },
    ]

# --- APP HEADER ---
st.markdown(
    '<div class="main-title">📍 SpotCheck Kenya</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">Travel Corridor Navigator & Community Traveler Insights</div>',
    unsafe_allow_html=True,
)

# --- SIDEBAR CONTROLS ---
st.sidebar.header("⚙️ Filter Options")

# Highway Corridor Filter
all_routes = ["All Kenya Corridors"] + sorted(list(df_all["route"].unique()))
selected_route = st.sidebar.selectbox("Select Highway / Corridor:", all_routes)

# Filter Dataframe
df = (
    df_all[df_all["route"] == selected_route].copy()
    if selected_route != "All Kenya Corridors"
    else df_all.copy()
)

# Category Filter
all_categories = ["All Categories"] + sorted(
    list(df_all["category"].unique())
)
selected_cat = st.sidebar.selectbox("Filter Category:", all_categories)

if selected_cat != "All Categories":
    df = df[df["category"] == selected_cat]

# Mode of Transport Selection
mode = st.sidebar.selectbox(
    "Travel Mode:",
    ["Vehicle (Driving)", "Walking", "Cycling", "Airplane (Direct)"],
)
mode_speeds = {
    "Vehicle (Driving)": {"speed": 70, "gmaps_mode": "driving"},
    "Walking": {"speed": 5, "gmaps_mode": "walking"},
    "Cycling": {"speed": 15, "gmaps_mode": "bicycling"},
    "Airplane (Direct)": {"speed": 500, "gmaps_mode": "driving"},
}

# --- BROWSER GEOLOCATION ---
loc = get_geolocation()
user_lat, user_lon = -1.286389, 36.817223  # Fallback: Nairobi CBD

if loc and "coords" in loc:
    user_lat = loc["coords"]["latitude"]
    user_lon = loc["coords"]["longitude"]
    st.success(f"📍 **GPS Fixed:** ({user_lat:.4f}, {user_lon:.4f})")
else:
    st.info(
        "📍 Using reference starting point (Nairobi CBD). Enable browser GPS for exact distance."
    )

# --- DISTANCE & ETA CALCULATION ---
if not df.empty:
    df["Distance_km"] = df.apply(
        lambda row: haversine_distance(
            user_lat, user_lon, row["lat"], row["lon"]
        ),
        axis=1,
    )
    speed = mode_speeds[mode]["speed"]
    df["ETA_hours"] = df["Distance_km"] / speed
    df = df.sort_values(by="Distance_km").reset_index(drop=True)

st.markdown("---")

# --- MAIN LAYOUT ---
if df.empty:
    st.warning("No spots match the selected filters.")
else:
    col1, col2 = st.columns([1, 1.1])

    with col1:
        st.subheader("🏁 Destination Details")

        selected_spot_name = st.selectbox(
            "Select a spot on this corridor:", df["name"]
        )
        spot = df[df["name"] == selected_spot_name].iloc[0]

        # Site Image
        st.image(
            spot["image_url"],
            caption=f"{spot['name']} - {spot['county']} County",
            use_container_width=True,
        )

        st.markdown(
            f"**Category:** `{spot['category']}` | **Corridor:** `{spot['route']}`"
        )

        # Distance Card
        st.metric(
            label=f"Distance ({mode})",
            value=f"{spot['Distance_km']:.1f} km",
            delta=(
                f"~{spot['ETA_hours']*60:.0f} mins"
                if spot["ETA_hours"] < 1
                else f"~{spot['ETA_hours']:.1f} hrs"
            ),
        )

        # Google Maps Direct Navigation Link
        gmaps_mode = mode_speeds[mode]["gmaps_mode"]
        gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={spot['lat']},{spot['lon']}&travelmode={gmaps_mode}"
        st.link_button("🚗 Open Navigation in Google Maps", gmaps_url)

    with col2:
        st.subheader("🗺️ Spatial Map")

        # Folium Map
        center_lat = (user_lat + spot["lat"]) / 2
        center_lon = (user_lon + spot["lon"]) / 2

        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles="OpenStreetMap",
        )

        # Origin Marker
        folium.Marker(
            location=[user_lat, user_lon],
            popup="Your Location",
            tooltip="Origin",
            icon=folium.Icon(color="red", icon="user", prefix="fa"),
        ).add_to(m)

        # Destination Marker
        folium.Marker(
            location=[spot["lat"], spot["lon"]],
            popup=f"<b>{spot['name']}</b><br>{spot['county']}",
            tooltip=spot["name"],
            icon=folium.Icon(color="green", icon="star", prefix="fa"),
        ).add_to(m)

        # Route Line
        folium.PolyLine(
            locations=[[user_lat, user_lon], [spot["lat"], spot["lon"]]],
            color="#C2410C",
            weight=4,
            opacity=0.8,
        ).add_to(m)

        st_folium(m, width="100%", height=420, returned_objects=[])

    # --- COMMUNITY INSIGHTS & EXPERIENCES SECTION ---
    st.markdown("---")
    st.subheader("💬 Community Insights & Traveler Tips")

    insight_col1, insight_col2 = st.columns([1, 1])

    with insight_col1:
        st.markdown(f"#### Shared Experiences for **{spot['name']}**")
        matching_insights = [
            i
            for i in st.session_state["user_insights"]
            if i["spot"] == spot["name"]
        ]

        if matching_insights:
            for item in matching_insights:
                st.markdown(
                    f"""
                    <div class="insight-box">
                        <b>{item['author']}</b> says:<br>
                        "{item['insight']}"
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.write(
                "No insights added for this location yet. Be the first to share!"
            )

    with insight_col2:
        st.markdown(f"#### Add Your Tip / Experience")
        with st.form("insight_form", clear_on_submit=True):
            author_name = st.text_input(
                "Your Name / Handle:", placeholder="e.g., Traveler_254"
            )
            user_message = st.text_area(
                "Share road conditions, best visit times, or tips:",
                placeholder="Write your experience here...",
            )
            submit_btn = st.form_submit_button("Submit Insight")

            if submit_btn:
                if author_name.strip() and user_message.strip():
                    new_entry = {
                        "spot": spot["name"],
                        "author": author_name.strip(),
                        "insight": user_message.strip(),
                    }
                    st.session_state["user_insights"].append(new_entry)
                    st.success("Your insight has been posted!")
                    st.rerun()
                else:
                    st.error(
                        "Please provide both your name and an insight message."
                    )
