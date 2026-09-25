import io
import math
import folium
import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SpotCheck Kenya | Travel & Scenic Navigator",
    page_icon="🦁",
    layout="wide",
)

# --- VIBRANT TOURISM DESIGN & HIGH-CONTRAST VISUALS ---
st.markdown(
    """
    <style>
    /* Full App Background with Warm African Sunset Theme */
    .stApp {
        background: linear-gradient(
            135deg, 
            rgba(255, 248, 240, 0.93), 
            rgba(254, 237, 213, 0.95)
        ), 
        url('https://images.unsplash.com/photo-1516426122078-c23e76319801?q=80&w=1920');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Global Typography & Elements */
    body, p, div, span, label {
        color: #1A1A1A !important;
        font-family: 'Poppins', 'Segoe UI', Roboto, sans-serif;
    }

    /* Vibrant Safari Main Header */
    .hero-banner {
        background: linear-gradient(115deg, #9A3412, #EA580C, #B45309);
        padding: 24px 28px;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(154, 52, 18, 0.22);
        color: white !important;
        margin-bottom: 20px;
    }
    
    .hero-banner h1 {
        color: #FFFFFF !important;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .hero-banner p {
        color: #FEF3C7 !important;
        font-size: 1.15rem;
        font-weight: 500;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* Refined Color Bar Accent below Location Box */
    .location-box {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
        position: relative;
    }

    .accent-bar {
        height: 5px;
        width: 100%;
        background: linear-gradient(90deg, #EA580C 0%, #15803D 50%, #D97706 100%);
        border-radius: 4px;
        margin-top: 14px;
        margin-bottom: 6px;
    }

    /* Cards & Containers */
    .description-card {
        background: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        border-left: 6px solid #D97706;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        margin-top: 12px;
        margin-bottom: 16px;
        font-size: 0.98rem;
        line-height: 1.6;
    }

    .badge-category {
        background-color: #15803D;
        color: white !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }

    .badge-route {
        background-color: #C2410C;
        color: white !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }

    .insight-card {
        background-color: #FFFFFF;
        padding: 14px;
        border-radius: 10px;
        border-left: 5px solid #059669;
        box-shadow: 0 3px 8px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }

    /* Button Customization */
    .stButton>button {
        background: linear-gradient(90deg, #EA580C, #D97706) !important;
        color: white !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(234, 88, 12, 0.35) !important;
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


# --- INITIAL KENYA SPOTS DATASET ---
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
            "images": [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Great_Rift_Valley_Kenya.jpg/800px-Great_Rift_Valley_Kenya.jpg"
            ],
        },
        {
            "name": "Hell's Gate National Park & Gorge",
            "lat": -0.8872,
            "lon": 36.3153,
            "category": "National Park / Gorge",
            "route": "Nairobi - Naivasha Highway (A104)",
            "county": "Nakuru",
            "description": "Famous for towering red cliffs, geothermal steam plumes, and Ol Njorowa Gorge. Visitors can cycle or hike right alongside zebras, giraffes, and gazelles.",
            "images": [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Hells_Gate_National_Park_Gorge_2.jpg/800px-Hells_Gate_National_Park_Gorge_2.jpg"
            ],
        },
        {
            "name": "Iten High Altitude Rim Viewpoint",
            "lat": 0.6728,
            "lon": 35.5081,
            "category": "Scenic Viewpoint / Athletics",
            "route": "Eldoret - Iten Road (C51)",
            "county": "Elgeyo Marakwet",
            "description": "Located at 2,400m above sea level along the Elgeyo Escarpment, Iten is the global training capital for elite marathon runners, featuring views dropping into the Kerio Valley.",
            "images": [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Iten_Kenya.jpg/800px-Iten_Kenya.jpg"
            ],
        },
        {
            "name": "Torok Waterfall",
            "lat": 0.4333,
            "lon": 35.5333,
            "category": "Waterfall Hike",
            "route": "Eldoret - Iten Road (C51)",
            "county": "Elgeyo Marakwet",
            "description": "A magnificent 150-meter cascade tumbling down the sheer red face of the Elgeyo Escarpment, accessed via scenic hiking trails through indigenous flora.",
            "images": [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Kenya_waterfall.jpg/800px-Kenya_waterfall.jpg"
            ],
        },
        {
            "name": "Ngare Ndare Forest Canopy Walk",
            "lat": 0.2833,
            "lon": 37.3500,
            "category": "Forest / Canopy Walk",
            "route": "Nairobi - Nanyuki Highway (A2)",
            "county": "Meru / Laikipia",
            "description": "An indigenous forest featuring a 450-meter elevated canopy walk suspended among ancient trees, leading to crystal-clear blue glacial pools fed by Mount Kenya.",
            "images": [
                "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Ngare_Ndare_Forest_Canopy_Walk.jpg/800px-Ngare_Ndare_Forest_Canopy_Walk.jpg"
            ],
        },
    ]


# Initialize Session States
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

# Default User Origin: Nairobi CBD
if "user_lat" not in st.session_state:
    st.session_state["user_lat"] = -1.286389
if "user_lon" not in st.session_state:
    st.session_state["user_lon"] = 36.817223
if "location_source" not in st.session_state:
    st.session_state["location_source"] = "Default Reference (Nairobi CBD)"

# --- HERO HEADER ---
st.markdown(
    """
    <div class="hero-banner">
        <h1>🦁 SpotCheck Kenya</h1>
        <p>Explore Travel Corridors, Scenic Viewpoints & Field Insights Across Kenya</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- EXPLICIT GEOLOCATION PERMISSION SECTION & CLEAN ACCENT BAR ---
with st.container():
    st.markdown('<div class="location-box">', unsafe_allow_html=True)
    st.subheader("📍 Origin & Live Distance Setup")

    loc_col1, loc_col2 = st.columns([1.2, 1])

    with loc_col1:
        st.write(f"**Current Reference Origin:** `{st.session_state['location_source']}`")
        st.write(
            f"Coordinates: `{st.session_state['user_lat']:.4f}, {st.session_state['user_lon']:.4f}`"
        )

        st.markdown("**Request Live GPS Location:**")

        if st.button("📡 Detect My Current Location"):
            loc = get_geolocation()
            if loc and "coords" in loc:
                st.session_state["user_lat"] = loc["coords"]["latitude"]
                st.session_state["user_lon"] = loc["coords"]["longitude"]
                st.session_state["location_source"] = "Live Device GPS"
                st.success("Location acquired successfully!")
                st.rerun()
            else:
                st.warning(
                    "Location request sent. Please allow browser location access if prompted."
                )

    with loc_col2:
        st.markdown("**Or Set Manual Origin Point:**")
        manual_city = st.selectbox(
            "Select Reference Town/City:",
            [
                "Nairobi CBD (-1.2864, 36.8172)",
                "Iten Town (0.6728, 35.5081)",
                "Eldoret Town (0.5143, 35.2698)",
                "Nakuru City (-0.3031, 36.0800)",
                "Nanyuki Town (0.0167, 37.0728)",
                "Mombasa CBD (-4.0435, 39.6682)",
            ],
        )

        if st.button("Set Selected City as Origin"):
            coords_map = {
                "Nairobi CBD (-1.2864, 36.8172)": (-1.286389, 36.817223),
                "Iten Town (0.6728, 35.5081)": (0.6728, 35.5081),
                "Eldoret Town (0.5143, 35.2698)": (0.5143, 35.2698),
                "Nakuru City (-0.3031, 36.0800)": (-0.3031, 36.0800),
                "Nanyuki Town (0.0167, 37.0728)": (0.0167, 37.0728),
                "Mombasa CBD (-4.0435, 39.6682)": (-4.0435, 39.6682),
            }
            c = coords_map[manual_city]
            st.session_state["user_lat"] = c[0]
            st.session_state["user_lon"] = c[1]
            st.session_state["location_source"] = manual_city.split(" (")[0]
            st.success(f"Origin set to {st.session_state['location_source']}")
            st.rerun()

    # Sleek Solid Multi-Color Gradient Bar
    st.markdown('<div class="accent-bar"></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

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

# Distance Computations
if not df.empty:
    df["Distance_km"] = df.apply(
        lambda row: haversine_distance(
            st.session_state["user_lat"],
            st.session_state["user_lon"],
            row["lat"],
            row["lon"],
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
    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.subheader("🏁 Destination Overview")

        selected_spot_name = st.selectbox(
            "Select Destination Spot:", df["name"]
        )
        spot_idx = next(
            i
            for i, item in enumerate(st.session_state["spots_data"])
            if item["name"] == selected_spot_name
        )
        spot = st.session_state["spots_data"][spot_idx]

        spot_dist = haversine_distance(
            st.session_state["user_lat"],
            st.session_state["user_lon"],
            spot["lat"],
            spot["lon"],
        )
        spot_eta = spot_dist / mode_speeds[mode]["speed"]

        # Display Image Gallery
        images = spot.get("images", [])
        if images:
            st.image(
                images[0],
                caption=f"{spot['name']} — {spot['county']} County",
                use_container_width=True,
            )
            if len(images) > 1:
                st.write("**Additional Photos:**")
                sub_cols = st.columns(min(len(images) - 1, 3))
                for idx, extra_img in enumerate(images[1:]):
                    with sub_cols[idx % 3]:
                        st.image(extra_img, use_container_width=True)

        # Place Description & Badges
        st.markdown(
            f"""
            <div style="margin-top: 10px; margin-bottom: 10px;">
                <span class="badge-category">{spot['category']}</span>
                <span class="badge-route">{spot['route']}</span>
            </div>
            <div class="description-card">
                <b>About this Location:</b><br>
                {spot['description']}
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Upload image to EXISTING spot
        with st.expander("📷 Add a new photo to this destination"):
            existing_upload = st.file_uploader(
                "Upload a photo taken at this spot:",
                type=["jpg", "jpeg", "png"],
                key="existing_upload",
            )
            if existing_upload:
                img_bytes = existing_upload.read()
                image = Image.open(io.BytesIO(img_bytes))
                st.image(image, caption="Preview Upload", width=200)

                if st.button("Save Photo to Spot"):
                    st.session_state["spots_data"][spot_idx]["images"].append(
                        image
                    )
                    st.success("Photo added to spot gallery!")
                    st.rerun()

        # Distance & ETA Metric
        st.metric(
            label=f"Calculated Distance from {st.session_state['location_source']} ({mode})",
            value=f"{spot_dist:.1f} km",
            delta=(
                f"~{spot_eta*60:.0f} mins ETA"
                if spot_eta < 1
                else f"~{spot_eta:.1f} hrs ETA"
            ),
        )

        # Google Maps Navigation Link
        gmaps_mode = mode_speeds[mode]["gmaps_mode"]
        gmaps_url = f"https://www.google.com/maps/dir/?api=1&origin={st.session_state['user_lat']},{st.session_state['user_lon']}&destination={spot['lat']},{spot['lon']}&travelmode={gmaps_mode}"
        st.link_button("🚗 Open Route in Google Maps", gmaps_url)

    with col2:
        st.subheader("🗺️ Location & Multi-Layer Map")

        center_lat = (st.session_state["user_lat"] + spot["lat"]) / 2
        center_lon = (st.session_state["user_lon"] + spot["lon"]) / 2

        # Initialize Base Map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=8,
            tiles=None,  # Handled by TileLayers below
        )

        # --- MULTI-BASEMAP TILE LAYERS ---
        folium.TileLayer(
            tiles="OpenStreetMap",
            name="Standard Street Map",
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri World Imagery",
            name="Esri Satellite Imagery",
            control=True,
        ).add_to(m)

        folium.TileLayer(
            tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            attr="OpenTopoMap",
            name="Topographic Map",
            control=True,
        ).add_to(m)

        # Origin Marker
        folium.Marker(
            location=[
                st.session_state["user_lat"],
                st.session_state["user_lon"],
            ],
            popup=f"Origin: {st.session_state['location_source']}",
            tooltip="Origin Point",
            icon=folium.Icon(color="red", icon="user", prefix="fa"),
        ).add_to(m)

        # Destination Marker
        popup_html = f"""
        <div style='width:220px;'>
            <b>{spot['name']}</b><br>
            <i style='font-size:0.85rem; color:#555;'>{spot['county']} County</i><br><br>
            <p style='font-size:0.85rem;'>{spot['description'][:100]}...</p>
        </div>
        """

        folium.Marker(
            location=[spot["lat"], spot["lon"]],
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=spot["name"],
            icon=folium.Icon(color="green", icon="star", prefix="fa"),
        ).add_to(m)

        # Polyline Route Line
        folium.PolyLine(
            locations=[
                [st.session_state["user_lat"], st.session_state["user_lon"]],
                [spot["lat"], spot["lon"]],
            ],
            color="#EA580C",
            weight=4,
            opacity=0.85,
        ).add_to(m)

        # Layer Control Widget on Top Right of Map
        folium.LayerControl(position="topright", collapsed=False).add_to(m)

        st_folium(m, width="100%", height=520, returned_objects=[])

# --- COMMUNITY & ADD LOCATION TABS ---
st.markdown("---")

tab1, tab2 = st.tabs(
    ["💬 Traveler Insights", "➕ Add New Destination with Image"]
)

with tab1:
    if not df.empty:
        st.markdown(f"#### Community Tips for **{spot['name']}**")
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

        with st.form("add_tip_form", clear_on_submit=True):
            author_name = st.text_input(
                "Your Name / Handle:", placeholder="e.g., Marathoner_Elgeyo"
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
                    st.success("Tip added successfully!")
                    st.rerun()

with tab2:
    st.markdown("#### Add a Brand New Location")

    with st.form("add_spot_form", clear_on_submit=True):
        new_name = st.text_input(
            "Location Name", placeholder="e.g., Chepkiit Waterfalls"
        )
        new_desc = st.text_area(
            "Place Description",
            placeholder="Describe what makes this location worth visiting...",
        )

        col_a, col_b = st.columns(2)
        with col_a:
            new_lat = st.number_input(
                "Latitude", value=0.5167, format="%.4f"
            )
            new_county = st.text_input(
                "County", placeholder="e.g., Nandi County"
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
                "Longitude", value=35.1833, format="%.4f"
            )
            new_route = st.text_input(
                "Highway / Corridor",
                placeholder="e.g., Eldoret - Kapsabet Road (C39)",
            )
            new_img_file = st.file_uploader(
                "Upload Image File:", type=["jpg", "jpeg", "png"]
            )
            new_img_url = st.text_input(
                "Or Provide Image URL:",
                placeholder="https://example.com/image.jpg",
            )

        submit_spot = st.form_submit_button("Add Destination")

        if submit_spot:
            if new_name.strip() and new_route.strip() and new_desc.strip():
                images_list = []

                if new_img_file is not None:
                    img_bytes = new_img_file.read()
                    uploaded_image = Image.open(io.BytesIO(img_bytes))
                    images_list.append(uploaded_image)
                elif new_img_url.strip():
                    images_list.append(new_img_url.strip())
                else:
                    images_list.append(
                        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Iten_Kenya.jpg/800px-Iten_Kenya.jpg"
                    )

                new_spot_entry = {
                    "name": new_name.strip(),
                    "lat": float(new_lat),
                    "lon": float(new_lon),
                    "category": new_category,
                    "route": new_route.strip(),
                    "county": new_county.strip(),
                    "description": new_desc.strip(),
                    "images": images_list,
                }
                st.session_state["spots_data"].append(new_spot_entry)
                st.success(f"'{new_name}' added to destination map!")
                st.rerun()
            else:
                st.error(
                    "Please complete the Name, Description, and Highway Corridor fields."
                )
