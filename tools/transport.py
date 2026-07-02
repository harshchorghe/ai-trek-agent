from typing import Dict, List, Optional, Any

TRANSPORT_DB = {
    "goa": {
        "Flights": "Dabolim Airport (GOI) in South Goa or Manohar International Airport (GOX) in Mopa, North Goa. Flights connect daily from all major hubs.",
        "Trains": "Madgaon (MAO) or Vasco da Gama (VSG) for South Goa; Thivim (THVM) or Karmali (KRMI) for North Goa. Popular train: Mandovi Express or Tejas Express.",
        "Road Trips": "NH66 route from Mumbai/Pune (approx. 10-12 hours drive). Beautiful scenic route through the Western Ghats.",
        "Public Transport": "Self-drive scooters/bikes are highly popular and cost-effective (₹300-₹600/day). Local pilot bikes or yellow-black cabs are also available."
    },
    "manali": {
        "Flights": "Bhuntar Airport (KUU), 50 km away (limited flights). Alternate is Chandigarh International Airport (IXC), 250 km away, followed by a 7-8 hour cab or bus ride.",
        "Trains": "Joginder Nagar railway station (narrow gauge, 144 km away) or Chandigarh Railway Station (broad gauge, 250 km away).",
        "Road Trips": "Drive from Delhi via NH44 (approx. 12-14 hours). HRTC Volvo buses run overnight from ISBT Kashmiri Gate, Delhi.",
        "Public Transport": "Local auto-rickshaws, local buses, or private cabs for sightseeing. Walking is perfect for Old Manali."
    },
    "ladakh": {
        "Flights": "Kushok Bakula Rimpochee Airport (IXL) in Leh. Directly connected to Delhi, Jammu, and Srinagar. Essential to rest for 24-48 hours on arrival to acclimatize.",
        "Trains": "Jammu Tawi (approx. 700 km away) is the nearest railway station. Not recommended to travel by train.",
        "Road Trips": "Srinagar-Leh Highway (NH1D, open May-Oct) or Manali-Leh Highway (open Jun-Oct). Highly popular for motorbiking road trips.",
        "Public Transport": "Shared taxis or private local cabs are standard. Outside vehicles are not allowed for local sightseeing in Nubra/Pangong; you must hire Leh-registered cabs."
    },
    "lonavala": {
        "Flights": "Pune International Airport (PNQ) - 60 km away, or Mumbai Chhatrapati Shivaji Maharaj Airport (BOM) - 90 km away.",
        "Trains": "Lonavala Railway Station (LNL). Local trains run regularly from Pune, and express trains connect from Mumbai (e.g., Deccan Queen, Sinhagad Express).",
        "Road Trips": "Drive via the Mumbai-Pune Expressway (approx. 2 hours from Mumbai, 1 hour from Pune). Two-wheelers must use the old NH4 highway.",
        "Public Transport": "Local auto-rickshaws, tourist taxis, or walking. Renting scooters is also popular."
    },
    "ujjain": {
        "Flights": "Devi Ahilyabai Holkar Airport in Indore (IDR), 55 km away. Taxi transfers or local buses take about 1 hour to reach Ujjain from Indore.",
        "Trains": "Ujjain Junction (UJN) is a major A-category railway station directly connected to Delhi, Mumbai, Chennai, and Kolkata. Avantika Express, Malwa Express are popular choices.",
        "Road Trips": "Indore-Ujjain road is a smooth 4-lane highway (NH52, approx 1-1.5 hours drive). Easily accessible from Indore, Bhopal, and Ahmedabad.",
        "Public Transport": "Shared auto-rickshaws, e-rickshaws, and municipal city buses are cheap and widely available. Walking is great for central temple lanes."
    }
}

def get_transportation_guidance(destination: str, llm: Optional[Any] = None) -> str:
    dest_key = destination.lower().strip()
    
    flights = ""
    trains = ""
    road_trip = ""
    public_transport = ""
    
    if dest_key in TRANSPORT_DB:
        info = TRANSPORT_DB[dest_key]
        flights = info.get("Flights", "")
        trains = info.get("Trains", "")
        road_trip = info.get("Road Trips", "")
        public_transport = info.get("Public Transport", "")
    else:
        # Default transportation recommendations
        flights = f"Fly into the nearest commercial airport to {destination.title()}, followed by local taxi transfer."
        trains = f"Check the nearest railway junction to {destination.title()} on IRCTC and arrange a local pickup."
        road_trip = f"Plan a road trip via major National Highways routing to {destination.title()}."
        public_transport = "Renting a local vehicle, auto-rickshaws, or using state-run bus transport is recommended."

    from tools.db import get_cached_item, save_cached_item
    cached = get_cached_item("transport", destination)
    if cached:
        return cached

    if llm:
        try:
            if dest_key in TRANSPORT_DB:
                prompt = f"""You are a logistics and transport coordinator for Explorush.
Write a clear, structured transportation guide for a user traveling to {destination}.
Integrate these guidelines:
- Flights: {flights}
- Trains: {trains}
- Road Trips: {road_trip}
- Local Transport: {public_transport}

Write a professional, friendly, and practical response. Keep it concise.
"""
            else:
                prompt = f"""You are a logistics and transport coordinator for Explorush.
Write a clear, structured transportation guide for a user traveling to {destination}.
Provide real-world, practical logistics advice on:
1) Nearest airport and typical transfer details.
2) Major nearby railway station.
3) Best highway routes or bus connections.
4) Best local commute options (rentals, autos, etc.).
Keep it realistic and concise.
"""
            res = llm.invoke(prompt)
            if res:
                save_cached_item("transport", destination, res)
                return res
        except Exception:
            pass

    # Deterministic local reply
    output = f"🚗 **Transportation Guidance for {destination.title()}**:\n\n"
    output += f"✈️ **By Flight**: {flights}\n\n"
    output += f"🚂 **By Train**: {trains}\n\n"
    output += f"🛣️ **By Road (Road Trip)**: {road_trip}\n\n"
    output += f"🛵 **Local Commute**: {public_transport}\n\n"
    output += "💡 *Logistics Tip*: Pre-book airport transfers or rental cars during peak holiday seasons (Oct-Jan) to avoid surge pricing."
    return output
