from typing import Dict, List, Optional, Any

NEARBY_DB = {
    "goa": {
        "Attractions": ["Calangute & Baga beaches (crowded but lively)", "Aguada Fort", "Basilica of Bom Jesus (UNESCO heritage)"],
        "Hidden Gems": ["Cola Beach (blue lagoon beach in South Goa)", "Netravali Bubbling Lake", "Harvalem Waterfall & Caves"],
        "Photography Spots": ["Fontainhas Latin Quarter (colorful Portuguese houses)", "Sunset at Chapora Fort", "Parra Road (palm tree lined road)"]
    },
    "manali": {
        "Attractions": ["Hadimba Temple", "Solang Valley (adventure sports hub)", "Mall Road shopping"],
        "Hidden Gems": ["Sajla Waterfall (peaceful spot with a local cafe)", "Jogini Waterfall trek", "Soyal village traditional houses"],
        "Photography Spots": ["Rohtang Pass (snow peaks)", "Old Manali streets and cafes", "Sunset over the Beas river"]
    },
    "ladakh": {
        "Attractions": ["Pangong Tso Lake", "Khardung La Pass (highest motorable pass)", "Leh Palace & Shanti Stupa"],
        "Hidden Gems": ["Tso Moriri Lake (less crowded than Pangong)", "Basgo Plains ruins", "Zanskar Confluence rafting point"],
        "Photography Spots": ["Nubra Valley sand dunes with Bactrian camels", "Monasteries at sunrise (Thiksey/Hemis)", "Magnetic Hill perspective shots"]
    },
    "lonavala": {
        "Attractions": ["Tiger's Point / Lions Point", "Bhushi Dam", "Karla & Bhaja Caves"],
        "Hidden Gems": ["Kataldhar Waterfall (needs a trek)", "Canyon Valley hike", "Tikona Fort (panoramic view)"],
        "Photography Spots": ["Sunset over Pawna Lake", "Lohagad Fort stone staircases", "Lush valleys during monsoon fog"]
    },
    "mahabaleshwar": {
        "Attractions": ["Arthur's Seat (Queen of Points)", "Venna Lake boating", "Mapro Garden"],
        "Hidden Gems": ["Kate's Point / Elephant's Head Point at sunrise", "Dhobi Waterfall", "Tapola (mini Kashmir of Maharashtra)"],
        "Photography Spots": ["Lingmala Waterfall cascades", "Elphinstone Point valleys", "Strawberry fields during harvest season"]
    }
}

def get_nearby_attractions(destination: str, llm: Optional[Any] = None) -> str:
    dest_key = destination.lower().strip()
    
    attractions = []
    hidden_gems = []
    photo_spots = []
    
    if dest_key in NEARBY_DB:
        info = NEARBY_DB[dest_key]
        attractions = info.get("Attractions", [])
        hidden_gems = info.get("Hidden Gems", [])
        photo_spots = info.get("Photography Spots", [])
    else:
        # Default spots
        attractions = [f"Popular Local Market in {destination.title()}", f"Historic Town Fort/Monuments in {destination.title()}"]
        hidden_gems = [f"Secret local nature trail in {destination.title()}", f"Scenic viewpoint away from crowds in {destination.title()}"]
        photo_spots = [f"Scenic overlook during sunset in {destination.title()}", f"Local colorful architecture in {destination.title()}"]

    if llm:
        try:
            prompt = f"""You are a local tour guide and photographer for Explorush.
Recommend top sights, hidden gems, and photography spots for a user visiting {destination}.
Use these database points:
- Attractions: {', '.join(attractions)}
- Hidden Gems: {', '.join(hidden_gems)}
- Photography Spots: {', '.join(photo_spots)}

Write a friendly, inspiring, and professional travel guide. Keep it concise.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"📸 **Sightseeing & Hidden Gems Guide for {destination.title()}**\n\n"
    
    if attractions:
        output += "🏛️ **Top Popular Attractions**:\n"
        for a in attractions:
            output += f"- {a}\n"
        output += "\n"
        
    if hidden_gems:
        output += "💎 **Explorush Hidden Gems (Offbeat)**:\n"
        for h in hidden_gems:
            output += f"- {h}\n"
        output += "\n"
        
    if photo_spots:
        output += "📷 **Best Photography & Instagram Spots**:\n"
        for p in photo_spots:
            output += f"- {p}\n"
        output += "\n"
        
    output += "💡 *Sightseeing Tip*: Visit popular attractions early in the morning (before 9 AM) to avoid tourist crowds and get the best natural lighting for your photos."
    return output
