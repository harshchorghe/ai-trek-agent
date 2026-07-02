from typing import Optional, Any

TRIP_TYPE_DB = {
    "solo": {
        "focus": "Independence, meeting people, and safety.",
        "tips": [
            "Stay in social hostels (like Zostel) to easily meet fellow travelers.",
            "Keep emergency contacts on speed dial and share your live location with family.",
            "Pack light—you are responsible for carrying your own luggage.",
            "Join local walking tours or group day-trips to explore safely."
        ]
    },
    "couple": {
        "focus": "Romance, experiences, and relaxation.",
        "tips": [
            "Book private cottages or boutique villas instead of standard hotel rooms.",
            "Plan a special sunset dinner or local wine-tasting experience.",
            "Mix adventure with relaxation—don't overschedule your days.",
            "Look for adult-only resorts if you prefer a quieter environment."
        ]
    },
    "family": {
        "focus": "Comfort, convenience, and child/elderly-friendly logistics.",
        "tips": [
            "Choose accommodations with 24/7 room service and kid-friendly play areas.",
            "Keep itineraries relaxed with fewer transits to avoid fatigue.",
            "Carry a small medical kit containing pediatric and elderly-friendly medicines.",
            "Pre-book spacious private cabs rather than relying on public transport."
        ]
    },
    "group": {
        "focus": "Coordination, shared expenses, and collective activities.",
        "tips": [
            "Look for full villa rentals or apartments with common spaces.",
            "Use split-expense apps (like Splitwise) to track shared costs transparently.",
            "Plan group activities (trekking, camping, beach volleyball) that match everyone's physical levels.",
            "Pre-book tables or entry passes—large groups are hard to accommodate at the last minute."
        ]
    }
}

def get_trip_type_advice(trip_style: str, llm: Optional[Any] = None) -> str:
    key = trip_style.lower().strip()
    if key not in TRIP_TYPE_DB:
        # Check substrings
        if "solo" in key:
            key = "solo"
        elif "couple" in key or "romantic" in key:
            key = "couple"
        elif "family" in key or "kids" in key:
            key = "family"
        elif "group" in key or "friends" in key:
            key = "group"
        else:
            key = "group" # Default fallback

    data = TRIP_TYPE_DB[key]
    focus = data["focus"]
    tips = data["tips"]

    if llm:
        try:
            tips_list = "\n".join([f"- {t}" for t in tips])
            prompt = f"""You are a travel consulting expert for Explorush.
Write customized advice for a user planning a "{key.title()}" trip.
Focus area: {focus}
Tips from database:
{tips_list}

Make the response highly engaging, professional, and friendly. Keep it brief.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"👥 **Explorush Travel Guide for {key.title()} Trips**\n"
    output += f"🎯 **Primary Focus**: {focus}\n\n"
    output += "📌 **Expert Recommendations**:\n"
    for tip in tips:
        output += f"- {tip}\n"
    output += "\n💡 *Consultant Tip*: Let me know if you would like me to adjust your accommodation or budget plan to better suit this travel style!"
    return output
