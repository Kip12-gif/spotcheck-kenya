%%writefile app.py
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# Set Streamlit layout
st.set_page_config(page_title="SpotCheck Kenya", page_icon="📍", layout="wide")

st.title("📍 SpotCheck Kenya")
st.caption("Curated Road Trip Corridors, Hidden Gems & Stopovers across Kenya")

DATA_FILE = "kenya_spots.csv"

@st.cache_data
def load_spots():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    
    # 20 Essential Kenya Road Trip Spots
    initial_spots = [
        # --- Corridor 1: Nairobi to Naivasha / Nakuru Highway ---
        {"name": "Mai Mahiu Rift Valley Viewpoint", "category": "Scenic Viewpoint", "corridor": "Nairobi-Naivasha (A104)", "county": "Nakuru", "description": "Classic escarpment view overlooking Mt. Longonot and Mt. Suswa.", "lat": -1.0264, "lng": 36.5683, "vibe": "Quick Stop / Photos"},
        {"name": "Old Italian Church", "category": "Cultural & Heritage", "corridor": "Nairobi-Naivasha (A104)", "county": "Nakuru", "description": "Historic smallest church built by Italian POWs in 1942.", "lat": -1.0345, "lng": 36.5741, "vibe": "Heritage & History"},
        {"name": "Camp Carnelley's (Lazybones)", "category": "Hidden Eatery / Cafe", "corridor": "Nairobi-Naivasha (A104)", "county": "Nakuru", "description": "Boho lakeside restaurant and campsite on South Lake Road.", "lat": -0.8031, "lng": 36.3812, "vibe": "Chill / Lakeside Food"},
        {"name": "Hell's Gate Fischer's Tower", "category": "Hiking & Outdoor", "corridor": "Nairobi-Naivasha (A104)", "county": "Nakuru", "description": "Volcanic plug popular for rock climbing and cycling alongside wildlife.", "lat": -0.8872, "lng": 36.3155, "vibe": "Adventure / Cycling"},
        {"name": "Olkaria Geothermal Spa", "category": "Hot Springs & Chill", "corridor": "Nairobi-Naivasha (A104)", "county": "Nakuru", "description": "Naturally heated warm brine swimming pool inside Hell's Gate.", "lat": -0.8931, "lng": 36.2941, "vibe": "Relaxation / Wellness"},
        {"name": "Sleeping Warrior & Ugali Hill", "category": "Hiking & Outdoor", "corridor": "Nairobi-Nakuru (A104)", "county": "Nakuru", "description": "Trail overlooking Lake Elementaita shaped like a resting Maasai warrior.", "lat": -0.4281, "lng": 36.2301, "vibe": "Hiking / Day Trip"},

        # --- Corridor 2: Central Highlands / Nanyuki / Mt. Kenya ---
        {"name": "Blue Post Waterfalls", "category": "Waterfall & Nature", "corridor": "Nairobi-Nanyuki (A2)", "county": "Kiambu", "description": "Classic stopover between Chania and Thika falls along the A2 highway.", "lat": -1.0331, "lng": 37.0691, "vibe": "Breakfast / River View"},
        {"name": "Castle Forest Lodge", "category": "Hiking & Outdoor", "corridor": "Nairobi-Nanyuki (A2)", "county": "Kirinyaga", "description": "Deep forest retreat at the foot of Mt. Kenya with waterfalls.", "lat": -0.3791, "lng": 37.2881, "vibe": "Nature Walk / Quiet"},
        {"name": "Trout Tree Restaurant", "category": "Hidden Eatery / Cafe", "corridor": "Nairobi-Nanyuki (A2)", "county": "Nyeri", "description": "Open-air restaurant built inside a huge fig tree over trout ponds.", "lat": -0.1102, "lng": 37.0392, "vibe": "Unique Dining"},
        {"name": "Nanyuki Equator Marker", "category": "Cultural & Heritage", "corridor": "Nairobi-Nanyuki (A2)", "county": "Laikipia", "description": "Official equator line cross point with science demonstrations.", "lat": 0.0000, "lng": 37.0722, "vibe": "Quick Photo Stop"},
        {"name": "Ngare Ndare Forest Canopy Walkway", "category": "Waterfall & Nature", "corridor": "Nanyuki-Timau (A2)", "county": "Meru", "description": "Turquoise blue waterfall pools and a 450m canopy walk.", "lat": 0.1781, "lng": 37.3821, "vibe": "Swimming / Canopy Walk"},

        # --- Corridor 3: Rift Valley Escarpment / North Rift ---
        {"name": "Iten Rim Viewpoint", "category": "Scenic Viewpoint", "corridor": "Eldoret-Iten (C51)", "county": "Elgeyo Marakwet", "description": "High-altitude cliff edge overlooking the Kerio Valley escarpment.", "lat": 0.6731, "lng": 35.5082, "vibe": "Panoramic Views"},
        {"name": "Torok Waterfall", "category": "Waterfall & Nature", "corridor": "Eldoret-Iten (C51)", "county": "Elgeyo Marakwet", "description": "200-meter vertical waterfall cascading down the Elgeyo Escarpment.", "lat": 0.4351, "lng": 35.5391, "vibe": "Trekking / Hidden Gem"},
        {"name": "Cheploch Gorge", "category": "Cultural & Heritage", "corridor": "Kabarnet Highway", "county": "Baringo", "description": "Deep rocky gorge on the Kerio River where local divers perform cliff jumps.", "lat": 0.5511, "lng": 35.6311, "vibe": "Sightseeing / Local Talent"},

        # --- Corridor 4: Southern Rift & Kajiado / Magadi ---
        {"name": "Champagne Ridge Viewpoint", "category": "Scenic Viewpoint", "corridor": "Kiserian-Magadi Road", "county": "Kajiado", "description": "Dramatic cliffside road trip location with views over the Rift Valley floor.", "lat": -1.5301, "lng": 36.6541, "vibe": "Sunset / Sundowner"},
        {"name": "Olorgesailie Prehistoric Site", "category": "Cultural & Heritage", "corridor": "Kiserian-Magadi Road", "county": "Kajiado", "description": "World-famous handaxe archaeological site managed by NMK.", "lat": -1.5791, "lng": 36.4441, "vibe": "History & Museum"},
        {"name": "Lake Magadi Hot Springs", "category": "Hot Springs & Chill", "corridor": "Kiserian-Magadi Road", "county": "Kajiado", "description": "Pink soda lake with natural hot water pools rich in minerals.", "lat": -1.8981, "lng": 36.2821, "vibe": "Off-Road / Adventure"},

        # --- Corridor 5: Coastal Kenya / Malindi & South Coast ---
        {"name": "Bofa Beach Hidden Cove", "category": "Beach & Water", "corridor": "Mombasa-Malindi (B8)", "county": "Kilifi", "description": "Uncrowded powder-white sand beach line with natural coral overhangs.", "lat": -3.6121, "lng": 39.8651, "vibe": "Beach / Chill"},
        {"name": "Marafa Hell's Kitchen", "category": "Scenic Viewpoint", "corridor": "Malindi-Marafa", "county": "Kilifi", "description": "Canyon carved by erosion with vibrant red, orange, and white sandstone.", "lat": -3.0011, "lng": 39.9881, "vibe": "Sunset / Photography"},
        {"name": "Kwale Kongo Mosque & River Mouth", "category": "Cultural & Heritage", "corridor": "Likoni-Diani (A14)", "county": "Kwale", "description": "Ancient 14th-century coral stone mosque where the estuary enters the ocean.", "lat": -4.2791, "lng": 39.5921, "vibe": "Sunset Kayaking"}
    ]
    df = pd.DataFrame(initial_spots)
    df.to_csv(DATA_FILE, index=False)
    return df

df_spots = load_spots()

# Sidebar - Route Filters
st.sidebar.header("🛣️ Select Road Trip Corridor")
corridor_list = ["All Corridors"] + list(df_spots["corridor"].unique())
selected_corridor = st.sidebar.selectbox("Route / Highway", corridor_list)

category_list = ["All Categories"] + list(df_spots["category"].unique())
selected_category = st.sidebar.selectbox("Filter by Experience", category_list)

# Filter Data
filtered_df = df_spots.copy()
if selected_corridor != "All Corridors":
    filtered_df = filtered_df[filtered_df["corridor"] == selected_corridor]
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

# Main Map Rendering
col_map, col_list = st.columns([1.3, 0.7])

with col_map:
    st.subheader(f"Mapped Stops ({len(filtered_df)})")
    
    # Initialize Folium Map centered on Kenya
    m = folium.Map(location=[0.0236, 37.9062], zoom_start=7, tiles="OpenStreetMap")
    
    # Esri Satellite Layer
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri World Imagery",
        name="Satellite Imagery"
    ).add_to(m)

    for idx, row in filtered_df.iterrows():
        popup_content = f"""
        <b>{row['name']}</b><br>
        <i>{row['category']}</i><br>
        <b>County:</b> {row['county']}<br>
        <b>Vibe:</b> {row['vibe']}<br>
        <p>{row['description']}</p>
        """
        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=row["name"],
            icon=folium.Icon(color="red" if "Eatery" in row["category"] else "blue", icon="info-sign")
        ).add_to(m)

    folium.LayerControl().add_to(m)
    st_folium(m, width="100%", height=550)

with col_list:
    st.subheader("Itinerary Spotlist")
    for idx, row in filtered_df.iterrows():
        with st.expander(f"📍 {row['name']} ({row['county']})"):
            st.write(f"**Route:** {row['corridor']}")
            st.write(f"**Vibe:** `{row['vibe']}`")
            st.write(row['description'])
            st.caption(f"Coordinates: {row['lat']}, {row['lng']}")