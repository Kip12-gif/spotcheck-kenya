import math
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpotCheck Kenya | Travel & Corridor Navigator",
    page_icon="🦁",
    layout="wide",
)

# --- SAFARI THEME & HIGH-CONTRAST VISUALS ---
st.markdown(
    """
    <style>
    /* Full App Background with Safari Atmosphere Overlay */
    .stApp {
        background: linear-gradient(
            rgba(255, 255, 255, 0.88), 
            rgba(245, 240, 230, 0.92)
        ), 
        url('https://images.unsplash.com/photo-1516426122078-c23e76319801?q=80&w=1920');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Global Typography & Contrast */
    body, p, div, span, label {
        color: #1F2937 !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* Vibrant Main Header */
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #9A3412;
        margin-bottom: 2px;
        letter-spacing: -0.5px;
    }
    
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        font-weight: 500;
        margin-bottom: 1.5rem;
    }

    /* Content Containers & Cards */
    .stMetric, div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 10px !important;
        border: 1px solid #D1D5DB !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    .description-card {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 14px;
        border-radius: 8px;
        border-left: 4px solid #EA580C;
        margin-top: 10px;
        margin-bottom: 15px;
        font-size: 0.95rem;
        line-height: 1.5;
        color: #374151 !important;
    }

    .insight-card {
        background-color: #FFFFFF;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #C2410C;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
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


# --- DETAILED KENYA SPOTS DATASET ---
def get_initial_spots():
    return [
        {
            "name": "Mai Mahiu Great Rift Valley Viewpoint",
            "lat": -1.0858,
            "lon": 36.5772,
            "category": "Scenic Viewpoint",
            "route": "Nairobi - Naivasha Highway (A104)",
            "county": "Nakuru",
            "description": "Perched on the edge of the Gregory Rift escarpment, this iconic stop offers panoramic views across the vast Rift Valley floor toward Mount Longonot and Lake Naivasha.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Great_Rift_Valley_Kenya.jpg/800px-Great_Rift_Valley_Kenya.jpg",
        },
        {
            "name": "Hell's Gate National Park & Gorge",
            "lat": -0.8872,
            "lon": 36.3153,
            "category": "National Park / Gorge",
            "route": "Nairobi - Naivasha Highway (A104)",
            "county": "Nakuru",
            "description": "Famous for towering red cliffs, geothermal steam plumes, and Ol Njorowa Gorge. Visitors can cycle or hike right alongside zebras, giraffes, and gazelles.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Hells_Gate_National_Park_Gorge_2.jpg/800px-Hells_Gate_National_Park_Gorge_2.jpg",
        },
        {
            "name": "Menengai Crater Viewpoint",
            "lat": -0.2000,
            "lon": 36.0667,
            "category": "Volcanic Crater / Viewpoint",
            "route": "Nairobi - Naivasha Highway (A104)",
            "county": "Nakuru",
            "description": "One of the largest intact volcanic calderas in the world. The viewpoint offers views over the caldera floor covered in dense forest and active geothermal vents.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Menengai_Crater.jpg/800px-Menengai_Crater.jpg",
        },
        {
            "name": "Iten High Altitude Rim Viewpoint",
            "lat": 0.6728,
            "lon": 35.5081,
            "category": "Scenic Viewpoint / Athletics",
            "route": "Eldoret - Iten Road (C51)",
            "county": "Elgeyo Marakwet",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Iten_Kenya.jpg/800px-Iten_Kenya.jpg",
            "description": "Located at 2,400m above sea level along the Elgeyo Escarpment, Iten is the global training capital for elite marathon runners, featuring views dropping into the Kerio Valley.",
        },
        {
            "name": "Torok Waterfall",
            "lat": 0.4333,
            "lon": 35.5333,
            "category": "Waterfall Hike",
            "route": "Eldoret - Iten Road (C51)",
            "county": "Elgeyo Marakwet",
            "description": "A magnificent 150-meter cascade tumbling down the sheer red face of the Elgeyo Escarpment, accessed via scenic hiking trails through indigenous flora.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Kenya_waterfall.jpg/800px-Kenya_waterfall.jpg",
        },
        {
            "name": "Ngare Ndare Forest Canopy Walk",
            "lat": 0.2833,
            "lon": 37.3500,
            "category": "Forest / Canopy Walk",
            "route": "Nairobi - Nanyuki Highway (A2)",
            "county": "Meru / Laikipia",
            "description": "An indigenous forest featuring a 450-meter elevated canopy walk suspended among ancient trees, leading to crystal-clear blue glacial pools fed by Mount Kenya.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Ngare_Ndare_Forest_Canopy_Walk.jpg/800px-Ngare_Ndare_Forest_Canopy_Walk.jpg",
        },
        {
            "name": "Thomson's Falls (Nyahururu)",
            "lat": 0.0441,
            "lon": 36.3686,
            "category": "Waterfall Hike",
            "route": "Nyeri - Nyahururu Road (B21)",
            "county": "Laikipia",
            "description": "A 74-meter waterfall on the Ewaso Nyiro River on the equator, surrounded by lush mist forest and scenic viewing platforms.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Thomson%27s_Falls.jpg/800px-Thomson%27s_Falls.jpg",
        },
        {
            "name": "Lake Magadi Hot Springs",
            "lat": -1.9000,
            "lon": 36.2833,
            "category": "Hot Springs",
            "route": "Kajiado - Magadi Road",
            "county": "Kajiado",
            "description": "Natural geothermal springs rich in minerals located at the southernmost soda lake in Kenya's Rift Valley, set against dramatic alkaline salt pans.",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Lake_Magadi.jpg/800px-Lake_Magadi.jpg",
        },
    ]


# Initialize Datasets in Session State
if "spots_data" not in st.session_state:
    st.session_state["spots_data"] = get_initial_spots()

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
    '<div class="sub-title">Travel Corridor Navigator, Scenic Maps & Field Insights</div>',
    unsafe_allow_html=True,
)

df_all = pd.DataFrame(st.session_state["spots_data"])

# --- SIDEBAR FILTERS ---
st.sidebar.header("🌿 Route Filters")

all_routes = ["All Kenya Corridors"] + sorted(list(df_all["route"].unique()))
selected_route = st.sidebar.selectbox("Select Highway Corridor:", all_routes)

df = (
    df_all[df_all["route"] == selected_route].copy()
    if selected_route != "All Kenya Corridors"
    else df_all.copy()
)

all_categories = ["All Categories"] + sorted(
    list(df_all["category"].unique())
)
selected_cat = st.sidebar.selectbox("Filter Category:", all_categories)

if selected_cat != "All Categories":
    df = df[df["category"] == selected_cat]

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

# --- SILENT GEOLOCATION FETCH ---
loc = get_geolocation()
user_lat, user_lon = -1.286389, 36.817223  # Internal Reference: Nairobi CBD

if loc and "coords" in loc:
    user_lat = loc["coords"]["latitude"]
    user_lon = loc["coords"]["longitude"]

# Calculate Distances
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

# --- MAIN DISPLAY ---
if df.empty:
    st.info("No spots match the current corridor filters.")
else:
    col1, col2 = st.columns([1, 1.1])

    with col1:
        st.subheader("🏁 Destination Overview")

        selected_spot_name = st.selectbox(
            "Select destination spot:", df["name"]
        )
        spot = df[df["name"] == selected_spot_name].iloc[0]

        # Destination Image
        st.image(
            spot["image_url"],
            caption=f"{spot['name']} — {spot['county']} County",
            use_container_width=True,
        )

        # Place Description Box
        st.markdown(
            f"""
            <div class="description-card">
                <b>About this Location:</b><br>
                {spot['description']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"**Category:** `{spot['category']}` | **Corridor:** `{spot['route']}`"
        )

        # Distance & ETA Metric
        st.metric(
            label=f"Calculated Distance ({mode})",
            value=f"{spot['Distance_km']:.1f} km",
            delta=(
                f"~{spot['ETA_hours']*60:.0f} mins ETA"
                if spot["ETA_hours"] < 1
                else f"~{spot['ETA_hours']:.1f} hrs ETA"
            ),
        )

        # Direct Google Navigation Link
        gmaps_mode = mode_speeds[mode]["gmaps_mode"]
        gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={spot['lat']},{spot['lon']}&travelmode={gmaps_mode}"
        st.link_button("🚗 Navigate via Google Maps", gmaps_url)

    with col2:
        st.subheader("🗺️ Location & Route Map")

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
            popup="Origin Point",
            tooltip="Origin",
            icon=folium.Icon(color="red", icon="user", prefix="fa"),
        ).add_to(m)

        # Destination Marker with Rich Popup Image & Description
        popup_html = f"""
        <div style='width:220px;'>
            <b>{spot['name']}</b><br>
            <i style='font-size:0.85rem; color:#555;'>{spot['county']} County</i><br><br>
            <img src='{spot['image_url']}' width='100%' style='border-radius:4px;'><br><br>
            <p style='font-size:0.85rem;'>{spot['description'][:100]}...</p>
        </div>
        """

        folium.Marker(
            location=[spot["lat"], spot["lon"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=spot["name"],
            icon=folium.Icon(color="green", icon="star", prefix="fa"),
        ).add_to(m)

        # Route Line
        folium.PolyLine(
            locations=[[user_lat, user_lon], [spot["lat"], spot["lon"]]],
            color="#EA580C",
            weight=4,
            opacity=0.85,
        ).add_to(m)

        st_folium(m, width="100%", height=460, returned_objects=[])

# --- COMMUNITY SECTION ---
st.markdown("---")

tab1, tab2 = st.tabs(
    ["💬 Traveler Tips & Field Insights", "➕ Add a New Location"]
)

with tab1:
    if not df.empty:
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
                    <div class="insight-card">
                        <b>{item['author']}</b>:<br>
                        "{item['insight']}"
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.write("No community tips posted for this spot yet.")

        # Tip Submission Form
        with st.form("add_tip_form", clear_on_submit=True):
            author_name = st.text_input(
                "Your Name / Handle:", placeholder="e.g., Traveler_254"
            )
            user_tip = st.text_area(
                "Share road conditions, scenic stop advice, or tips:"
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
                    st.success("Tip added!")
                    st.rerun()

with tab2:
    st.markdown("#### Add a New Highway Spot to SpotCheck")

    with st.form("add_spot_form", clear_on_submit=True):
        new_name = st.text_input(
            "Location Name", placeholder="e.g., Kerio Valley Viewpoint"
        )
        new_desc = st.text_area(
            "Place Description",
            placeholder="Provide details about what makes this place special...",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            new_lat = st.number_input(
                "Latitude", value=0.6728, format="%.4f"
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
                "Longitude", value=35.5081, format="%.4f"
            )
            new_route = st.text_input(
                "Highway / Corridor",
                placeholder="e.g., Eldoret - Iten Road (C51)",
            )
            new_img = st.text_input(
                "Image URL",
                value="https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Iten_Kenya.jpg/800px-Iten_Kenya.jpg",
            )

        submit_spot = st.form_submit_button("Submit Location")

        if submit_spot:
            if new_name.strip() and new_route.strip() and new_desc.strip():
                new_spot_entry = {
                    "name": new_name.strip(),
                    "lat": float(new_lat),
                    "lon": float(new_lon),
                    "category": new_category,
                    "route": new_route.strip(),
                    "county": new_county.strip(),
                    "description": new_desc.strip(),
                    "image_url": new_img.strip(),
                }
                st.session_state["spots_data"].append(new_spot_entry)
                st.success(f"'{new_name}' added to the map dataset!")
                st.rerun()
            else:
                st.error(
                    "Please complete the Name, Description, and Highway Corridor fields."
                )
