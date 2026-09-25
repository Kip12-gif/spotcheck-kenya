import math
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpotCheck Kenya | Relax & Discover",
    page_icon="🦁",
    layout="wide",
)

# --- SAFARI THEME & ELEVATED RELAX VIBES CSS ---
st.markdown(
    """
    <style>
    /* Full App Background with Safari Atmosphere Overlay */
    .stApp {
        background: linear-gradient(
            rgba(255, 255, 255, 0.85), 
            rgba(245, 240, 230, 0.90)
        ), 
        url('https://images.unsplash.com/photo-1516426122078-c23e76319801?q=80&w=1920');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Global Typography & Contrast */
    body, p, div, span, label {
        color: #2D3748 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Vibrant Safari Main Title */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #9A3412; /* Warm Earthy Savannah Orange */
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #4A5568;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }

    /* Content Cards Styling */
    .stMetric, div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.92) !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    .insight-card {
        background-color: #FFFFFF;
        padding: 14px;
        border-radius: 10px;
        border-left: 5px solid #EA580C;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
        margin-bottom: 12px;
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


# --- INITIAL DATASET ---
def get_initial_spots():
    return [
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
        {
            "name": "Ngare Ndare Forest Canopy Walk",
            "lat": 0.2833,
            "lon": 37.3500,
            "category": "Forest / Canopy Walk",
            "route": "Nairobi - Nanyuki Highway (A2)",
            "county": "Meru / Laikipia",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Ngare_Ndare_Forest_Canopy_Walk.jpg/800px-Ngare_Ndare_Forest_Canopy_Walk.jpg",
        },
    ]


# Initialize Spots Data in Session State (Allows dynamic additions)
if "spots_data" not in st.session_state:
    st.session_state["spots_data"] = get_initial_spots()

# Initialize Insights in Session State
if "user_insights" not in st.session_state:
    st.session_state["user_insights"] = [
        {
            "spot": "Iten High Altitude Rim Viewpoint",
            "author": "Kipchoge Fan",
            "insight": "Best visited around 6:00 AM to see marathon runners training along the escarpment road!",
        }
    ]

# --- APP HEADER ---
st.markdown(
    '<div class="main-title">🦁 SpotCheck Kenya</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-title">Scenic Highway Corridors, Interactive Maps & Travel Community</div>',
    unsafe_allow_html=True,
)

# Convert Session State Spots to DataFrame
df_all = pd.DataFrame(st.session_state["spots_data"])

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🌿 Route Filters")

# Highway Corridor Filter
all_routes = ["All Kenya Corridors"] + sorted(list(df_all["route"].unique()))
selected_route = st.sidebar.selectbox("Select Highway Corridor:", all_routes)

# Filter Dataset
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

# Mode of Transport
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
user_lat, user_lon = -1.286389, 36.817223  # Default: Nairobi CBD

if loc and "coords" in loc:
    user_lat = loc["coords"]["latitude"]
    user_lon = loc["coords"]["longitude"]
    st.success(f"📍 **GPS Fixed:** ({user_lat:.4f}, {user_lon:.4f})")

# Calculate Distance & ETA
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

# --- MAIN DASHBOARD LAYOUT ---
if df.empty:
    st.info("No spots found matching the selected filters.")
else:
    col1, col2 = st.columns([1, 1.1])

    with col1:
        st.subheader("🏁 Spot Details")

        selected_spot_name = st.selectbox("Choose a destination:", df["name"])
        spot = df[df["name"] == selected_spot_name].iloc[0]

        # Site Photo
        st.image(
            spot["image_url"],
            caption=f"{spot['name']} ({spot['county']} County)",
            use_container_width=True,
        )

        st.markdown(
            f"**Category:** `{spot['category']}`  \n**Corridor:** `{spot['route']}`"
        )

        # Distance Display
        st.metric(
            label=f"Distance ({mode})",
            value=f"{spot['Distance_km']:.1f} km",
            delta=(
                f"~{spot['ETA_hours']*60:.0f} mins"
                if spot["ETA_hours"] < 1
                else f"~{spot['ETA_hours']:.1f} hrs"
            ),
        )

        # Google Maps Direct Directions
        gmaps_mode = mode_speeds[mode]["gmaps_mode"]
        gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={spot['lat']},{spot['lon']}&travelmode={gmaps_mode}"
        st.link_button("🚗 Navigate in Google Maps", gmaps_url)

    with col2:
        st.subheader("🗺️ Spatial Map")

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

        # Direct Line
        folium.PolyLine(
            locations=[[user_lat, user_lon], [spot["lat"], spot["lon"]]],
            color="#EA580C",
            weight=4,
            opacity=0.85,
        ).add_to(m)

        st_folium(m, width="100%", height=430, returned_objects=[])

# --- COMMUNITY SECTION: TIPS & ADD NEW SPOTS ---
st.markdown("---")

tab1, tab2 = st.tabs(
    ["💬 Community Tips & Experiences", "➕ Submit a New Spot"]
)

with tab1:
    if not df.empty:
        st.markdown(f"#### Traveler Insights for **{spot['name']}**")
        matching_insights = [
            i
            for i in st.session_state["user_insights"]
            if i["spot"] == spot["name"]
        ]

        if matching_insights:
            for item in matching_insights:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <b>{item['author']}</b> shared:<br>
                        "{item['insight']}"
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.write("No tips added for this location yet.")

        # Post Insight Form
        with st.form("add_tip_form", clear_on_submit=True):
            author_name = st.text_input(
                "Your Name:", placeholder="e.g., Jane Mwangi"
            )
            user_tip = st.text_area(
                "Share road updates, best visit times, or scenic tips:"
            )
            if st.form_submit_button("Post Tip"):
                if author_name.strip() and user_tip.strip():
                    st.session_state["user_insights"].append(
                        {
                            "spot": spot["name"],
                            "author": author_name.strip(),
                            "insight": user_tip.strip(),
                        }
                    )
                    st.success("Tip added successfully!")
                    st.rerun()

with tab2:
    st.markdown("#### Know a great spot? Add it to SpotCheck Kenya!")
    st.caption(
        "Submitted spots instantly appear on the app map and filter corridors."
    )

    with st.form("add_spot_form", clear_on_submit=True):
        new_name = st.text_input(
            "Spot Name", placeholder="e.g., Kerio Valley Viewpoint"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            new_lat = st.number_input(
                "Latitude", value=0.67, format="%.4f"
            )
            new_county = st.text_input(
                "County", placeholder="e.g., Elgeyo Marakwet"
            )
            new_category = st.selectbox(
                "Category",
                [
                    "Scenic Viewpoint",
                    "Waterfall Hike",
                    "National Park / Gorge",
                    "Forest / Canopy Walk",
                    "Historical Heritage",
                    "Hot Springs",
                ],
            )

        with col_b:
            new_lon = st.number_input(
                "Longitude", value=35.50, format="%.4f"
            )
            new_route = st.text_input(
                "Road Highway / Corridor",
                placeholder="e.g., Eldoret - Iten Road (C51)",
            )
            new_img = st.text_input(
                "Image URL",
                value="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Iten_Kenya.jpg/800px-Iten_Kenya.jpg",
            )

        submit_spot = st.form_submit_button("Add Spot to Map")

        if submit_spot:
            if new_name.strip() and new_route.strip():
                new_spot_entry = {
                    "name": new_name.strip(),
                    "lat": float(new_lat),
                    "lon": float(new_lon),
                    "category": new_category,
                    "route": new_route.strip(),
                    "county": new_county.strip(),
                    "image_url": new_img.strip(),
                }
                st.session_state["spots_data"].append(new_spot_entry)
                st.success(
                    f"'{new_name}' has been added to the map and database!"
                )
                st.rerun()
            else:
                st.error("Please fill in the Spot Name and Road Corridor.")
