import re

def choose_tool(user_input: str) -> str:
    text = user_input.lower().strip()

    # 1. TRAVEL PLANNER TOOL (Highest specificity)
    # E.g. "I'm going to Goa for 4 days", "plan a trip to Ladakh", "itinerary for Goa"
    if any(pattern in text for pattern in [
        "plan a trip", "plan my trip", "trip plan", "full plan", "complete plan",
        "itinerary for", "schedule for", "road trip to", "travel plan", "planning a",
        "planning to", "planning trip", "trip to", "going to", "travel to", "travelling to"
    ]) or re.search(r"(?:going to|travelling to|travel to|visit to|trip to)\s+[a-zA-Z]+?\s+(?:for|with|this|next|tomorrow)", text):
        return "planner"

    # 2. TRAVEL FAQ TOOL
    # E.g. "when should I visit Goa?", "is Manali safe?", "best time to visit Kashmir?"
    if any(phrase in text for phrase in [
        "when should i", "best time to", "when to visit", "suitable for", "is it safe", "is manali safe", "can i go to"
    ]):
        return "faq"

    # 3. BUDGET ESTIMATOR TOOL
    # E.g. "how much money do I need?", "budget estimate for Goa", "cost of trip"
    if any(word in text for word in [
        "budget", "cost", "how much money", "price", "expensive", "cheap", "estimate", "expense"
    ]):
        return "budget"

    # 4. PACKING TOOL
    # E.g. "what should I carry?", "packing list", "what to pack"
    if any(word in text for word in [
        "packing", "pack", "carry", "bag", "luggage", "checklist", "what should i carry", "what to carry"
    ]):
        return "packing"

    # 5. WEATHER TOOL
    # E.g. "weather in Manali", "temperature at Kalsubai", "forecast"
    if any(word in text for word in [
        "weather", "forecast", "temperature", "rain", "snow", "climate", "degree"
    ]):
        return "weather"

    # 6. HOTEL / ACCOMMODATION TOOL
    # E.g. "resorts in Goa", "hostels near me", "places to stay"
    if any(word in text for word in [
        "hotel", "hostel", "resort", "homestay", "stay", "accommodation", "where to sleep", "places to stay"
    ]):
        return "hotel"

    # 7. RESTAURANT / FOOD TOOL
    # E.g. "best cafes near Marine Drive", "food in Goa", "street food"
    if any(word in text for word in [
        "restaurant", "cafe", "food", "eat", "street food", "dining", "cuisine", "breakfast", "lunch", "dinner", "cafes"
    ]):
        return "restaurant"

    # 8. DESTINATION RECOMMENDATION TOOL
    # E.g. "I want to go somewhere this weekend", "suggest places under 10000"
    if any(phrase in text for phrase in [
        "suggest places", "recommend places", "where should i go", "go somewhere", "weekend trip", 
        "holiday destinations", "best destinations", "hidden places", "somewhere this weekend"
    ]):
        return "destination"

    # 9. TRANSPORTATION TOOL
    # E.g. "flight to Goa", "how to reach Manali", "train travel"
    if any(word in text for word in [
        "flight", "train", "cab", "bus", "transportation", "how to reach", "drive", "road trip", "public transport"
    ]):
        return "transport"

    # 10. SAFETY & EMERGENCY TOOL
    # E.g. "safety tips", "travel scams", "emergency number"
    if any(word in text for word in [
        "safety", "emergency", "scam", "danger", "safe", "hospital", "police", "scams"
    ]):
        return "emergency"

    # 11. VISA TOOL
    # E.g. "visa for Europe", "passport details"
    if any(word in text for word in [
        "visa", "passport", "entry requirements"
    ]):
        return "visa"

    # 12. CURRENCY TOOL
    # E.g. "currency in Nepal", "forex rate"
    if any(word in text for word in [
        "currency", "money exchange", "forex"
    ]):
        return "currency"

    # 13. SIGHTSEEING / NEARBY ATTRACTIONS TOOL
    # E.g. "photography spots", "hidden gems in Goa", "places to see"
    if any(word in text for word in [
        "attraction", "photography", "hidden gem", "sightseeing", "places to see", "tourist spot", "nearby points"
    ]):
        return "nearby"

    # 14. ACTIVITIES / SPORTS TOOL
    # E.g. "scuba diving", "camping at Pawna", "adventure sports"
    if any(word in text for word in [
        "activities", "camping", "adventure", "sports", "beach activities", "rafting", "paragliding"
    ]):
        return "activities"

    # 15. TREK SPECIFIC TOOL
    # E.g. "is Harihar difficult?", "kalsubai duration", "rajmachi height"
    if any(word in text for word in [
        "trek", "hike", "climb", "difficulty", "hard", "easy", "moderate", "how difficult",
        "kalsubai", "rajmachi", "harihar", "kalavantin", "height", "duration", "fort", "elevation"
    ]):
        return "trek"

    # DEFAULT
    # Normal chat assistant
    return "chat"