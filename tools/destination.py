from typing import List, Dict, Any, Optional

# Structured Local Destination Database
DESTINATIONS = [
    {
        "name": "Goa",
        "tags": ["beach", "nightlife", "seafood", "water sports", "couple", "solo", "group", "winter", "monsoon"],
        "min_budget": 8000,
        "starting_hub": "Mumbai",
        "description": "India's pocket-sized paradise, known for its beautiful beaches, Portuguese heritage, and vibrant nightlife.",
        "highlights": ["Calangute Beach", "Fontainhas Latin Quarter", "Basilica of Bom Jesus", "Dudhsagar Falls", "Chapora Fort"]
    },
    {
        "name": "Manali",
        "tags": ["mountain", "snow", "adventure", "trekking", "camping", "couple", "solo", "group", "winter"],
        "min_budget": 12000,
        "starting_hub": "Delhi",
        "description": "A high-altitude Himalayan resort town known for its cool climate, snow-capped peaks, and adventure sports.",
        "highlights": ["Solang Valley", "Rohtang Pass", "Hadimba Temple", "Old Manali", "Jogini Waterfalls"]
    },
    {
        "name": "Ladakh",
        "tags": ["mountain", "roadtrip", "adventure", "trekking", "photography", "hidden", "solo", "group", "summer"],
        "min_budget": 25000,
        "starting_hub": "Delhi",
        "description": "A land of high passes, spectacular lakes, and ancient monasteries, perfect for road trips and adventure seekers.",
        "highlights": ["Pangong Tso Lake", "Khardung La Pass", "Nubra Valley", "Magnetic Hill", "Diskit Monastery"]
    },
    {
        "name": "Lonavala",
        "tags": ["weekend", "monsoon", "waterfalls", "family", "couple", "hills", "group", "maharashtra"],
        "min_budget": 3000,
        "starting_hub": "Mumbai",
        "description": "A popular hill station close to Mumbai and Pune, famous for its lush green valleys, waterfalls, and chikki.",
        "highlights": ["Tiger's Point", "Bhushi Dam", "Karla Caves", "Lohagad Fort", "Kune Falls"]
    },
    {
        "name": "Mahabaleshwar",
        "tags": ["weekend", "couple", "family", "hills", "strawberry", "winter", "monsoon", "maharashtra"],
        "min_budget": 4500,
        "starting_hub": "Mumbai",
        "description": "A scenic hill station in the Western Ghats range, known for its strawberry farms, valleys, and colonial style.",
        "highlights": ["Arthur's Seat", "Venna Lake", "Mapro Garden", "Elephant's Head Point", "Lingmala Waterfall"]
    },
    {
        "name": "Munnar",
        "tags": ["mountain", "tea gardens", "couple", "family", "winter", "photography", "hills"],
        "min_budget": 10000,
        "starting_hub": "Kochi",
        "description": "A serene town and former resort for the British Raj elite, surrounded by rolling hills dotted with tea plantations.",
        "highlights": ["Eravikulam National Park", "Mattupetty Dam", "Anamudi Peak", "Tea Museum", "Echo Point"]
    },
    {
        "name": "Kashmir",
        "tags": ["mountain", "snow", "photography", "couple", "family", "winter", "spring"],
        "min_budget": 20000,
        "starting_hub": "Delhi",
        "description": "Often called 'Paradise on Earth', known for its snow-capped mountains, pristine lakes, houseboats, and gardens.",
        "highlights": ["Dal Lake", "Gulmarg Gondola", "Pahalgam Valley", "Shalimar Bagh", "Sonamarg Meadow"]
    },
    {
        "name": "Jaipur",
        "tags": ["historical", "culture", "shopping", "family", "couple", "winter"],
        "min_budget": 6000,
        "starting_hub": "Delhi",
        "description": "The capital of Rajasthan, known as the 'Pink City' due to the dominant color scheme of its historic buildings.",
        "highlights": ["Amer Fort", "Hawa Mahal", "City Palace", "Jantar Mantar", "Chokhi Dhani"]
    },
    {
        "name": "Alibaug",
        "tags": ["weekend", "beach", "seafood", "family", "couple", "roadtrip", "maharashtra"],
        "min_budget": 3500,
        "starting_hub": "Mumbai",
        "description": "A coastal town south of Mumbai, popular for its sandy beaches, ancient forts, and delicious Konkani cuisine.",
        "highlights": ["Alibaug Beach", "Kolaba Fort", "Kashid Beach", "Varsoli Beach", "Murud Janjira Fort"]
    },
    {
        "name": "Kalsubai",
        "tags": ["trekking", "weekend", "adventure", "hills", "monsoon", "winter", "maharashtra"],
        "min_budget": 1500,
        "starting_hub": "Mumbai",
        "description": "The highest peak in Maharashtra, offering stunning panoramic views of the Western Ghats and a thrilling climb.",
        "highlights": ["Kalsubai Temple", "Bhandardara Dam nearby", "Arthur Lake", "Sunrise view"]
    },
    {
        "name": "Rajmachi",
        "tags": ["trekking", "weekend", "camping", "monsoon", "fort", "maharashtra"],
        "min_budget": 1200,
        "starting_hub": "Mumbai",
        "description": "A historic fort situated in the rugged hills of Sahyadri, famous for its lush greenery and fireflies festival.",
        "highlights": ["Shrivardhan Fort", "Manaranjan Fort", "Kondana Caves", "Rajmachi Lake"]
    }
]

def recommend_destinations(query: str, llm: Optional[Any] = None) -> str:
    text = query.lower()
    
    # 1. Filter destinations based on tags and budget
    matched = []
    
    # Parse budget
    max_budget = None
    import re
    budget_match = re.search(r"(?:under|rs\.?|inr|₹|budget of)\s*(\d+)(?:\s*k|\b)", text)
    if budget_match:
        max_budget = int(budget_match.group(1))
        if "k" in text[budget_match.start():budget_match.end() + 10] or (max_budget < 1000 and "k" in text):
            max_budget *= 1000
    elif "10k" in text or "10000" in text:
        max_budget = 10000
    elif "5k" in text or "5000" in text:
        max_budget = 5000
    elif "20k" in text or "20000" in text:
        max_budget = 20000

    # Parse search keywords
    filters = []
    if "weekend" in text:
        filters.append("weekend")
    if "couple" in text or "romantic" in text:
        filters.append("couple")
    if "solo" in text:
        filters.append("solo")
    if "family" in text:
        filters.append("family")
    if "monsoon" in text or "rain" in text:
        filters.append("monsoon")
    if "winter" in text or "snow" in text:
        filters.append("winter")
    if "beach" in text:
        filters.append("beach")
    if "mountain" in text or "hill" in text:
        filters.append("mountain")
    if "trekking" in text or "trek" in text:
        filters.append("trekking")
    if "hidden" in text or "offbeat" in text:
        filters.append("hidden")
    if "history" in text or "heritage" in text or "historical" in text:
        filters.append("historical")
    if "camping" in text:
        filters.append("camping")
    if "adventure" in text:
        filters.append("adventure")
    if "photography" in text:
        filters.append("photography")
    if "road trip" in text:
        filters.append("roadtrip")
    if "maharashtra" in text or "near mumbai" in text or "near pune" in text:
        filters.append("maharashtra")

    # Match process
    for dest in DESTINATIONS:
        # Check budget first
        if max_budget and dest["min_budget"] > max_budget:
            continue
            
        # Check tags
        match_score = 0
        for f in filters:
            if f in dest["tags"]:
                match_score += 1
                
        # If filters are present, must match at least one (unless query is general)
        if filters and match_score == 0:
            continue
            
        matched.append((dest, match_score))

    # Sort by match score descending
    matched.sort(key=lambda x: x[1], reverse=True)
    results = [item[0] for item in matched]
    
    # If nothing matched, show all within budget or general list
    if not results:
        if max_budget:
            results = [d for d in DESTINATIONS if d["min_budget"] <= max_budget]
        else:
            results = DESTINATIONS[:4]

    # Generate response
    if llm:
        try:
            dest_list_str = "\n".join([
                f"- {d['name']}: {d['description']} (Highlights: {', '.join(d['highlights'])}, Min Budget: ₹{d['min_budget']})"
                for d in results
            ])
            prompt = f"""You are an experienced travel consultant for Explorush.
Given the user prompt: "{query}"

And these matching destinations from our database:
{dest_list_str}

Write a friendly, conversational, and professional recommendation. Tell the user why these spots are a great fit, and highlight their top features. Keep it concise but engaging.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Local fallback output formatting
    output = "🎒 Recommended Destinations for You:\n\n"
    for d in results[:3]:
        output += f"📍 **{d['name']}** ({', '.join([t.title() for t in d['tags'] if t in filters] or [t.title() for t in d['tags'][:2]])})\n"
        output += f"   - *Overview*: {d['description']}\n"
        output += f"   - *Top Highlights*: {', '.join(d['highlights'])}\n"
        output += f"   - *Est. Minimum Budget*: ₹{d['min_budget']}\n\n"
        
    output += "💡 *Travel Consultant Tip*: Let me know if you would like me to build a daily itinerary or a budget plan for any of these places!"
    return output
