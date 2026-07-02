from typing import Optional, Any

ACTIVITIES_DB = {
    "goa": {
        "type": "Coastal & Water Sports",
        "list": [
            "**Scuba Diving & Snorkeling**: Explore marine life near Grand Island.",
            "**Water Sports**: Parasailing, jet skiing, banana boat rides, and bumper rides at Calangute/Baga.",
            "**Kayaking**: Quiet backwater kayaking in the mangroves of Sal river or Nerul.",
            "**Spice Plantation Tours**: Guided walks with traditional Goan lunch in Ponda."
        ]
    },
    "manali": {
        "type": "Himalayan Adventure & Snow Sports",
        "list": [
            "**Paragliding**: High-flying glides in Solang Valley or Dobhi.",
            "**River Rafting**: Exciting Class II-III white-water rafting in the Beas River.",
            "**Skiing & Snowboarding**: Seasonal winter sports in Rohtang Pass or Solang Valley.",
            "**Trekking & Camping**: Day hikes to Jogini Waterfall or multi-day treks like Hampta Pass."
        ]
    },
    "lonavala": {
        "type": "Sahyadri Monsoons & Camping",
        "list": [
            "**Lakeside Camping**: Overnight camping under the stars near Pawna Lake with BBQ.",
            "**Waterfall Rappelling**: Thrilling monsoon rope descents at Madhe Ghat or Duke's Nose.",
            "**Fort Trekking**: Hiking up Lohagad, Visapur, or Tikona forts.",
            "**Hot Air Ballooning**: Early morning hot air balloon rides over Sahyadri valleys."
        ]
    }
}

def get_adventure_activities(destination: str, llm: Optional[Any] = None) -> str:
    dest_key = destination.lower().strip()
    
    act_type = "Outdoor Sightseeing & Exploration"
    activities = [
        "Local walking tours and sightseeing walks.",
        "Experiencing traditional food trails and market shopping.",
        "Short nature walks to nearby sunset viewpoints."
    ]
    
    matched_key = None
    if "goa" in dest_key:
        matched_key = "goa"
    elif "manali" in dest_key:
        matched_key = "manali"
    elif any(w in dest_key for w in ["lonavala", "mahabaleshwar", "rajmachi", "kalsubai", "harihar"]):
        matched_key = "lonavala"

    if matched_key:
        info = ACTIVITIES_DB[matched_key]
        act_type = info["type"]
        activities = info["list"]

    if llm:
        try:
            act_list = "\n".join([f"- {a}" for a in activities])
            prompt = f"""You are an adventure sports coordinator for Explorush.
Write an exciting, active description of adventure activities, camping, or beach sports in {destination}.
Activity type: {act_type}
Activities from database:
{act_list}

Write an enthusiastic, professional, and friendly response. Keep it brief.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"🏂 **Adventure & Outdoor Activities in {destination.title()}**\n"
    output += f"Category: *{act_type}*\n\n"
    output += "📌 **Top Recommended Activities**:\n"
    for a in activities:
        output += f"- {a}\n"
        
    output += "\n💡 *Safety Tip*: Always verify if the operator is certified by local tourism boards, and wear lifejackets/harnesses for all water and high-altitude sports!"
    return output
