from typing import Optional, Any

FESTIVALS_DB = {
    "goa": {
        "culture": "Goan culture is a unique blend of Indian (Konkani) and Portuguese influences, reflected in its music, architecture, and food.",
        "events": [
            "**Sunburn Festival (December)**: One of Asia's largest electronic dance music festivals, held on Goan beaches.",
            "**Goa Carnival (February)**: A colorful street parade featuring music, floats, and dancing, introduced by the Portuguese.",
            "**Shigmo (March)**: The Konkani version of Holi, celebrated with traditional folk dances, drum beats, and massive street processions."
        ]
    },
    "manali": {
        "culture": "Himachali culture is rich in folklore, traditional Himachali woolen caps, and local dances like the Nati.",
        "events": [
            "**Winter Carnival (January)**: Celebrated on Mall Road with Himachali folk performances, beauty pageants, and local food stalls.",
            "**Dussehra (October)**: Kullu Dussehra (nearby) is a world-famous week-long festival where local deities are brought to the Dhalpur ground."
        ]
    },
    "maharashtra": {
        "culture": "Maharashtrian culture is deeply rooted in history, famous for its historic forts, Marathi literature, and vibrant festivals.",
        "events": [
            "**Ganesh Chaturthi (August/September)**: The largest and most energetic festival in Maharashtra, celebrated with massive idol installations and street processions.",
            "**Rajmachi Fireflies Festival (May/June)**: A natural phenomenon before the monsoons where millions of fireflies illuminate the forests of Rajmachi Fort."
        ]
    }
}

def get_cultural_events(destination: str, llm: Optional[Any] = None) -> str:
    dest_key = destination.lower().strip()
    
    culture = "Rich regional heritage blending traditional folklore, food, and warm local hospitality."
    events = [
        "Check local tourism calendars for agricultural, harvesting, or religious festivals matching your dates.",
        "Visit local handicraft centers and weekly markets to experience authentic community commerce."
    ]
    
    # Check match
    matched_key = None
    if "goa" in dest_key:
        matched_key = "goa"
    elif "manali" in dest_key:
        matched_key = "manali"
    elif any(w in dest_key for w in ["maharashtra", "lonavala", "mahabaleshwar", "kalsubai", "rajmachi", "harihar"]):
        matched_key = "maharashtra"
        
    if matched_key:
        info = FESTIVALS_DB[matched_key]
        culture = info["culture"]
        events = info["events"]

    if llm:
        try:
            events_list = "\n".join([f"- {e}" for e in events])
            prompt = f"""You are a cultural specialist and event advisor for Explorush.
Tell the user about the local culture and festivals/events in {destination}.
Culture overview: {culture}
Key events:
{events_list}

Write a warm, engaging, and professional response. Keep it concise.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"🎭 **Culture & Events Guide for {destination.title()}**\n\n"
    output += f"📜 **Local Culture**: {culture}\n\n"
    output += "🎉 **Key Festivals & Events**:\n"
    for e in events:
        output += f"- {e}\n"
        
    output += "\n💡 *Cultural Tip*: When visiting local religious shrines or temples, dress modestly (shoulders and knees covered) and remove your shoes before entering."
    return output
