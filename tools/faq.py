from typing import Optional, Any
from tools.trek import get_trek_difficulty, format_trek_info

FAQS = [
    {
        "keywords": ["when should i visit goa", "best time to visit goa", "when to visit goa"],
        "answer": "🌅 **Best Time to Visit Goa**:\n- **Peak Season (November to February)**: Perfect pleasant weather, beaches are fully active, water sports are open, and nightlife is buzzing.\n- **Monsoon Season (June to September)**: Beautiful lush green landscapes, lower prices, but beaches are closed for swimming and water sports are suspended.\n- **Off-Season (March to May)**: Warm and humid, but great for budget travelers who want peaceful, less crowded beaches."
    },
    {
        "keywords": ["is manali safe", "safety in manali", "manali safe"],
        "answer": "🏔️ **Manali Safety Information**:\n- Manali is generally very safe for solo travelers, couples, and families.\n- **Monsoon Warning (July to August)**: Travel is highly discouraged during peak monsoon due to risks of landslides, cloudbursts, and flash floods in the Beas river. Always check weather updates.\n- **Winter Travel**: Roads to Rohtang Pass or Solang Valley can get slippery due to black ice. Hire local experienced drivers rather than self-driving."
    },
    {
        "keywords": ["how difficult is rajmachi", "rajmachi difficulty", "difficulty of rajmachi"],
        "answer": "🥾 **Rajmachi Fort Trek Difficulty**:\n- **Difficulty Level**: Easy to Moderate.\n- **Duration**: 3-4 hours hike from Udhewadi base village.\n- **Details**: It is a relatively flat walk from Lonavala side (approx. 15 km dirt road) or a steep climb from Karjat side (Kondivade village). It is beginner-friendly, family-friendly, and very popular for night treks during the monsoon."
    },
    {
        "keywords": ["kedarnath suitable for senior citizens", "is kedarnath safe for old", "kedarnath senior citizens"],
        "answer": "⛰️ **Kedarnath Guidance for Senior Citizens**:\n- **Verdict**: Physically demanding and challenging.\n- **Altitude**: Located at 11,750 ft (3,583 m), where oxygen levels are thin.\n- **Trek Distance**: A steep 16 km climb from Gaurikund. \n- **Alternatives**: Helicopter services can be booked via the official IRCTC portal. Alternatively, horse/mule rides or palanquins (dandi) are available.\n- **Recommendations**: Seniors must undergo medical screening, check for cardiorespiratory issues, carry portable oxygen cylinders, and acclimatize properly in Haridwar/Rishikesh."
    },
    {
        "keywords": ["best time to visit kashmir", "when should i visit kashmir", "best season for kashmir"],
        "answer": "🌸 **Best Time to Visit Kashmir**:\n- **Spring (March to May)**: Tulip Festival in Srinagar, blooming flowers, and pleasant temperatures (15°C to 25°C).\n- **Autumn (September to November)**: Beautiful golden-red Chinar trees, clear skies, and cool weather.\n- **Winter (December to February)**: Perfect for snow lovers and skiing in Gulmarg. Temperatures drop below freezing.\n- **Summer (June to August)**: Lush green valleys, ideal for Amarnath Yatra and trekking."
    }
]

def answer_faq(query: str, llm: Optional[Any] = None) -> Optional[str]:
    text = query.lower().strip()
    
    # 1. Match FAQs deterministically
    for faq in FAQS:
        for keyword in faq["keywords"]:
            if keyword in text:
                return faq["answer"]
                
    # Check if they are asking about trek difficulties that we support in local database
    if "difficulty" in text or "how difficult" in text:
        from tools.trek import detect_trek
        trek_name = detect_trek(text)
        if trek_name:
            diff = get_trek_difficulty(trek_name)
            info = format_trek_info(trek_name)
            return f"🥾 **Trek Difficulty FAQ**:\nAccording to our trek database:\n{info}\n\nDifficulty rating: **{diff}**."

    # 2. If LLM is available, generate FAQ answer dynamically
    if llm:
        try:
            prompt = f"""You are a helpful travel customer success agent for Explorush.
Answer the customer's travel FAQ naturally and professionally:
FAQ: "{query}"

Give a structured, clear, and reassuring response. Keep it concise.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    return None
