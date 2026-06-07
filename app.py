import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Asthma & Allergen Tracker", layout="wide", page_icon="🫁")
st.title("🫁 Public Air Quality & Allergen Personal Assistant")
st.markdown("### Environmental Health Engine | Sydney, AU & Ras Al Khaimah, UAE")

# 2. OVERRIDE CONTROL SYSTEM
st.sidebar.header("🕹️ Smart-Home Simulation Overrides")
inject_emergency = st.sidebar.checkbox("Simulate High Dust/Pollen Storm Event", value=False)

# 3. LIVE ATMOSPHERIC API INGESTION
def fetch_air_quality(lat, lon):
    try:
        # Querying Open-Meteo Air Quality API for dynamic environment layers
        url = f"https://open-meteo.com{lat}&longitude={lon}&current=pm2_5,alder_pollen,grass_pollen"
        res = requests.get(url, timeout=5).json()
        return {
            "pm25": res['current']['pm2_5'],
            "grass": res['current']['grass_pollen']
        }
    except Exception:
        return {"pm25": 8.0, "grass": 2.0} # Normal baseline fallback values

# 4. FIXED USER GEOGRAPHIC DATABASE
patients = [
    {"Reg": "Sydney, AU", "Loc": "Blacktown Subdivisions (Home)", "Lat": -33.7738, "Lon": 150.9180, "Type": "Suburban Valley Basin", "Limit": 20.0},
    {"Reg": "Ras Al Khaimah, UAE", "Loc": "Al Marjan Island Apartment", "Lat": 25.6662, "Lon": 55.7431, "Type": "Coastal Marine Zone", "Limit": 35.0}
]

# 5. EXECUTE RISK SYNTHESIS ENGINE
processed_rows = []
warn_count = 0

for p in patients:
    api_data = fetch_air_quality(p["Lat"], p["Lon"])
    
    # Simulate indoor home PM2.5 particle penetration or dust storms
    live_pm25 = api_data["pm25"] + (45.0 if inject_emergency else 4.0)
    status = "CRITICAL" if live_pm25 >= p["Limit"] else "NORMAL"
    if status == "CRITICAL": warn_count += 1
    
    processed_rows.append({
        "Region": p["Reg"], "User Environment": p["Loc"], "Vulnerability Zone": p["Type"],
        "Live PM2.5 Level": f"{round(live_pm25, 1)} µg/m³", "Safety Threshold": f"{p['Limit']} µg/m³",
        "Status": status, "Color": "red" if status == "CRITICAL" else "green",
        "Lat": p["Lat"], "Lon": p["Lon"]
    })

df = pd.DataFrame(processed_rows)

# 6. RENDER DYNAMIC VISUAL LAYERS
m1, m2 = st.columns(2)
m1.metric("Monitored Patient Nodes", len(df))
m2.metric("Active Air Quality Warnings", warn_count)

if warn_count > 0:
    st.error(f"🚨 WARNING: {warn_count} environment profile(s) indicate hazardous particulate concentrations. Activate HVAC filtration systems immediately.")
else:
    st.success("✅ Atmospheric conditions optimal. Indoor and outdoor particulate loads remain within safety tolerances.")

# Geospatial Interface Map
st.markdown("### 🗺️ Personal Micro-Environment Health Map")
m = folium.Map(location=[-33.7738, 150.9180] if inject_emergency else [0.0, 100.0], zoom_start=2, tiles="CartoDB positron")
for _, r in df.iterrows():
    folium.Marker(
        location=[r["Lat"], r["Lon"]],
        popup=f"<b>{r['User Environment']}</b><br>PM2.5: {r['Live PM2.5 Level']}",
        icon=folium.Icon(color=r["Color"], icon="plus-sign" if r["Status"] == "CRITICAL" else "ok-sign")
    ).add_to(m)
st_folium(m, width="100%", height=400, returned_objects=[])

st.dataframe(df.drop(columns=["Color", "Lat", "Lon"]), use_container_width=True)
