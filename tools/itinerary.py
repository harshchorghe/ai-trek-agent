from typing import Optional, Any

ITINERARIES_DB = {
    "goa": [
        "**Day 1: North Goa Vibe & Beaches**\n  - Morning: Check-in, head to Calangute or Candolim beach.\n  - Afternoon: Relax at beach shacks, enjoy Goan fish curry.\n  - Evening: Watch sunset at Chapora Fort or Vagator beach.\n  - Night: Explore cafes/nightlife at Tito's Lane or Curlies.",
        "**Day 2: South Goa Heritage & Culture**\n  - Morning: Visit Basilica of Bom Jesus and Se Cathedral in Old Goa.\n  - Afternoon: Walk through Fontainhas, the colorful Latin Quarter in Panaji.\n  - Evening: Sunset river cruise on the Mandovi river.\n  - Night: Dinner at Mum's Kitchen or Fisherman's Wharf.",
        "**Day 3: Water Sports & Waterfalls**\n  - Morning: Travel to Dudhsagar Waterfalls or book water sports (parasailing, jet-ski) at Baga.\n  - Afternoon: Tour a spice plantation in Ponda with a traditional Goan buffet.\n  - Evening: Relax at Miramar beach.\n  - Night: Visit one of Goa's premium casinos or beach clubs.",
        "**Day 4: Offbeat South Goa & Coastal Drive**\n  - Morning: Drive down to Palolem or Cola Beach (scenic lagoon beach).\n  - Afternoon: Kayaking at Palolem backwaters.\n  - Evening: Sunset view from Cabo de Rama Fort.\n  - Night: Quiet dinner in South Goa."
    ],
    "manali": [
        "**Day 1: Arrival & Local Cafe Hopping**\n  - Morning: Arrive in Manali, check-in, rest.\n  - Afternoon: Visit Hadimba Temple & Vashisht Hot Water Springs.\n  - Evening: Walk around Mall Road & explore riverside cafes in Old Manali.\n  - Night: Dinner with live music at Cafe 1947.",
        "**Day 2: Adventure Sports in Solang Valley**\n  - Morning: Drive to Solang Valley for paragliding or zorbing.\n  - Afternoon: Short trek to Jogini Waterfalls from Vashisht village.\n  - Evening: Shopping for local woodwork and Himachali shawls at Tibetan Market.\n  - Night: Try traditional food (Siddu) at local joints.",
        "**Day 3: Snow Peaks & Rohtang Pass**\n  - Morning: Drive up to Rohtang Pass (needs permit) for snow sports or scenic valley views.\n  - Afternoon: Visit Atal Tunnel and drive through to Sissu village in Lahaul Valley.\n  - Evening: Return to Manali, relax at hotel.\n  - Night: Cozy dinner near fireplace.",
        "**Day 4: Offbeat Hikes & Departure**\n  - Morning: Hike up to Soyal Village or visit Naggar Castle (scenic gallery).\n  - Afternoon: Lunch at Naggar, explore local art galleries.\n  - Evening: Head to bus stand for return overnight Volvo to Delhi."
    ],
    "ladakh": [
        "**Day 1: Acclimatization & Leh Town**\n  - Morning: Arrive in Leh (11,500 ft), check-in, rest completely for acclimatization.\n  - Afternoon: Drink plenty of water, light walk in Leh Market.\n  - Evening: Visit Shanti Stupa for sunset view over Leh valley.\n  - Night: Warm dinner at Tibetan Kitchen.",
        "**Day 2: Leh to Nubra Valley via Khardung La**\n  - Morning: Drive to Nubra Valley over Khardung La Pass (17,582 ft - highest motorable road).\n  - Afternoon: Arrive Hunder, enjoy double-humped camel safari in cold sand dunes.\n  - Evening: Visit Diskit Monastery & see the giant Buddha statue.\n  - Night: Camping in Hunder.",
        "**Day 3: Nubra to Pangong Tso via Shyok Route**\n  - Morning: Drive along Shyok River route to Pangong Lake (14,270 ft).\n  - Afternoon: Watch the lake change colors (blue, green, turquoise).\n  - Evening: Photography walk by the lake.\n  - Night: Stay in lakeside cottages/homestay.",
        "**Day 4: Pangong Tso to Leh via Chang La**\n  - Morning: Drive back to Leh over Chang La Pass (17,586 ft).\n  - Afternoon: Stop at Thiksey Monastery for pictures.\n  - Evening: Last-minute souvenir shopping in Leh.\n  - Night: Farewell dinner."
    ],
    "ujjain": [
        "**Day 1: Arrival & Evening Shipra River Aarti**\n  - Morning: Arrive in Ujjain Junction, check-in to your hotel.\n  - Afternoon: Take rest, have lunch at Guru Kripa (Daal Bafla).\n  - Evening: Visit Ram Ghat for the grand Shipra River sunset Aarti.\n  - Night: Visit local markets and sample Tower Chowk Poha-Jalebi.",
        "**Day 2: Mahakaleshwar & Local Temples**\n  - Morning: Pre-book and attend the famous Bhasma Aarti at Mahakaleshwar Jyotirlinga.\n  - Afternoon: Explore the grand Mahakal Corridor and Harsiddhi Shaktipeeth Temple.\n  - Evening: Visit Kal Bhairav Temple (famous for the liquor offering ritual).\n  - Night: Relax at hotel or standard restaurant dinner.",
        "**Day 3: Historical Exploration & Ashram**\n  - Morning: Visit Sandipani Ashram (where Lord Krishna studied) and Sandipani temple.\n  - Afternoon: Head to Jantar Mantar (Ved Shala observatory) and Mangalnath Temple.\n  - Evening: Walk around Kaliadeh Palace on the outskirts of the city.\n  - Night: Dinner at Apna Sweets.",
        "**Day 4: Day Trip to Omkareshwar / Departure**\n  - Morning: Plan a quick morning road trip to Omkareshwar Jyotirlinga (140 km, optional) or explore local handloom fabrics (Bhairavgarh block prints).\n  - Afternoon: Pack bags, shop for local sweets/crafts.\n  - Evening: Head to Ujjain Junction or Indore airport for return journey."
    ]
}

def generate_itinerary(destination: str = "", days: int = 3, llm: Optional[Any] = None) -> str:
    dest_key = destination.lower().strip()
    
    # 1. Match specific itineraries
    matched_key = None
    if "goa" in dest_key:
        matched_key = "goa"
    elif "manali" in dest_key:
        matched_key = "manali"
    elif "ladakh" in dest_key:
        matched_key = "ladakh"
    elif "ujjain" in dest_key:
        matched_key = "ujjain"
        
    itinerary_days = []
    
    if matched_key:
        itinerary_days = ITINERARIES_DB[matched_key][:days]
    else:
        # Check if it is a known trek (Kalsubai, Rajmachi, Harihar)
        # Old trek itinerary logic fallback
        if any(w in dest_key for w in ["kalsubai", "rajmachi", "harihar", "trek", "hike"]):
            itinerary_days = [
                "**Day 1: Base Camp & Ascent**\n  - Morning: Travel from Mumbai/Pune to base village (e.g. Bari for Kalsubai, Udhewadi for Rajmachi).\n  - Afternoon: Start trek with local guide, climb through scenic ridges.\n  - Evening: Reach summit, pitch tents or check into local village homestay.\n  - Night: Bonfire, stargazing, and traditional Maharashtrian dinner.",
                "**Day 2: Peak Exploration & Descent**\n  - Morning: Sunrise summit views, hot breakfast at village.\n  - Afternoon: Explore fort ruins/temples, start descent to base village.\n  - Evening: Drive back to Mumbai/Pune."
            ]
        else:
            # General itinerary generation
            itinerary_days = [
                f"**Day 1: Arrival & Local Orientation**\n  - Check-in at hotel/hostel.\n  - Explore nearby markets and local cafes.\n  - Evening walk to a popular scenic viewpoint.",
                f"**Day 2: Sightseeing & Signature Highlights**\n  - Full day guided tour of major tourist attractions in {destination.title()}.\n  - Taste traditional meals at recommended local restaurants.",
                f"**Day 3: Adventure & Offbeat Exploration**\n  - Choose an adventure sport or visit a hidden nature spot.\n  - Souvenir shopping and departure preparations."
            ]
            
            # Pad or slice to match requested days
            if len(itinerary_days) < days:
                for i in range(len(itinerary_days) + 1, days + 1):
                    itinerary_days.append(f"**Day {i}: Free Exploration & Leisure**\n  - Relax and explore the neighborhood at your own pace.\n  - Visit local craft workshops or hidden cafes.")
            itinerary_days = itinerary_days[:days]

    if llm:
        try:
            itinerary_text = "\n\n".join(itinerary_days)
            prompt = f"""You are a custom travel planner for Explorush.
Given the destination: {destination} and duration: {days} days, refine and format this base itinerary:
{itinerary_text}

Make it look highly professional, exciting, client-ready, and cohesive. Keep it clear and concise.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"📅 **Suggested {days}-Day Itinerary for {destination.title()}**\n\n"
    output += "\n\n".join(itinerary_days)
    output += "\n\n💡 *Tip*: Daily timings are suggestive. Feel free to swap days or activities based on weather conditions!"
    return output