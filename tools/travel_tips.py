from typing import Optional, Any

def get_travel_tips(query: str = "", llm: Optional[Any] = None) -> str:
    tips = [
        "**Pack Light**: Lay out everything you think you need, then put back half of it. Focus on lightweight, fast-drying clothes.",
        "**Go Digital**: Save a copy of your passport, visa, travel insurance, and bookings in a Google Drive folder marked 'available offline' on your phone.",
        "**Card Protection**: Inform your bank of international travel so they don't block your cards for suspicious transactions. Set transaction limits on your banking app.",
        "**Acclimatize**: When traveling to high-altitude places like Ladakh, Leh, or Kashmir, schedule a complete day of rest to avoid Acute Mountain Sickness (AMS).",
        "**Local Sim Card**: Buy a local physical SIM or eSIM (like Airalo or local providers) at the airport or city center for maps and translations.",
        "**Hydration & Snacks**: Always carry a reusable water bottle and some energy bars. It saves money and reduces single-use plastic waste."
    ]

    if llm:
        try:
            tips_list = "\n".join([f"- {t}" for t in tips])
            prompt = f"""You are a travel consultant for Explorush.
Given the query: "{query}"

Provide a set of 4-5 premium travel tips and checks for a smooth trip experience. Add any relevant advice. Keep it friendly and professional.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = "💡 **Explorush Expert Travel Tips & Checklist**\n\n"
    output += "Here are some of our best travel tips to keep your journey smooth and stress-free:\n\n"
    for t in tips:
        output += f"- {t}\n"
    output += "\n✏️ *Travel Checklist*: Did you remember to carry power banks, universal adapter, personal meds, and cash?"
    return output
