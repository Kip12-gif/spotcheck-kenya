# 📍 SpotCheck Kenya

> **Curated Road Trip Corridors, Hidden Gems & Stopovers Across Kenya.**

SpotCheck Kenya is a geospatial web application designed to bridge the gap between social discovery and road trip navigation. While traditional navigation platforms excel at point A-to-B routing, **SpotCheck Kenya** curates multi-stop road trip corridors based on vibe, highway routes, scenic stopovers, and local recommendations.

---

## 🚀 Key Features

* **Highway Corridor Filtering:** Filter curated spots along major travel routes (e.g., *Nairobi–Naivasha (A104)*, *Nairobi–Nanyuki (A2)*, *Eldoret–Iten (C51)*, *Kiserian–Magadi*, *Mombasa–Malindi (B8)*).
* **Experience & Vibe Search:** Discover places categorized by activity—*Scenic Viewpoints, Hidden Eateries, Waterfall Hikes, Heritage Sites, Hot Springs, and Beach Coves*.
* **Interactive Spatial Map:** Powered by **Folium** and **OpenStreetMap** with satellite overlay capabilities for off-road visibility.
* **Curated Itinerary Cards:** Get instant coordinates, county metadata, and descriptions for each destination.

---

## 🛠️ Project Structure

```text
spotcheck-kenya/
├── app.py              # Main Streamlit application
├── kenya_spots.csv     # Spatial dataset of road trip spots
├── requirements.txt    # Python dependencies
└── README.md           # Documentation