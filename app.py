import streamlit as st
from streamlit_js_eval import get_geolocation

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="SpotCheck Kenya",
    page_icon="📍",
    layout="wide"
)

# Modern, clean CSS theme styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .spot-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    .status-badge {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# App Header
# ---------------------------------------------------------
st.markdown('<div class="main-header">📍 SpotCheck Kenya</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Discover and verify field locations around Kenya seamlessly.</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# User Location Section (1-Click GPS Capture)
# ---------------------------------------------------------
st.subheader("1. Your Current Location")

col_gps, col_info = st.columns([1, 2])

with col_gps:
    st.info("Tap below to permit location access via your browser/phone.")
    loc = get_geolocation()

user_lat, user_lon = None, None

if loc and 'coords' in loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    with col_info:
        st.success(f"📍 **Location Detected!**\n\n**Latitude:** {user_lat:.5f} | **Longitude:** {user_lon:.5f}")
else:
    with col_info:
        st.warning("Location access is pending. Allow location permission when prompted by your browser.")
        # Non-professional user friendly alternative (City/County search fallback)
        fallback_region = st.selectbox(
            "Or select your nearest town/area:",
            ["Nairobi", "Iten", "Eldoret", "Mombasa", "Kisumu", "Nakuru"]
        )

st.markdown("---")

# ---------------------------------------------------------
# Spot Inspection / Gallery Section (Fixes line 133 bug)
# ---------------------------------------------------------
st.subheader("2. Nearby Spots & Sites")

# Sample dataset
spots = [
    {
        "name": "Kipchoge Keino Stadium",
        "county": "Elgeyo Marakwet",
        "image_url": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800",
        "desc": "High-altitude athletic training grounds."
    },
    {
        "name": "Rift Valley Viewpoint",
        "county": "Nakuru / Kiambu",
        "image_url": "https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800",
        "desc": "Panoramic view of the Great Rift Valley floor."
    }
]

cols = st.columns(len(spots))

for idx, spot in enumerate(spots):
    with cols[idx]:
        st.markdown(f"""
        <div class="spot-card">
            <span class="status-badge">{spot['county']}</span>
            <h3>{spot['name']}</h3>
            <p>{spot['desc']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # FIXED: Replaced use_column_width=True with use_container_width=True
        st.image(
            spot["image_url"], 
            caption=f"Site View: {spot['name']}", 
            use_container_width=True
        )
