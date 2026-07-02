import re
from typing import Dict, Any, Optional

def extract_trip_details(user_input: str, llm: Optional[Any] = None) -> Dict[str, Any]:
    text = user_input.lower()
    
    # 1. Deterministic location extraction via regex
    # Common pattern: "going to X", "travelling to X", "visit to X", "trip to X", "plan a trip to X", "X for Y days", "X with Y"
    location = None
    loc_match = re.search(
        r"(?:going to|travelling to|travel to|visit to|trip to|plan a trip to|plan to visit|destination is|for|at|in|near)\s+([a-zA-Z\s]+?)(?:\s+(?:for|with|under|this|next|tomorrow|in|at|on|budget)\b|$)", 
        text
    )
    if loc_match:
        extracted = loc_match.group(1).strip()
        # Filter out common stop words
        if extracted not in ["my", "the", "a", "an", "some", "weekend", "friends", "couple", "family", "solo"]:
            location = extracted.title()
            
    # If no match, try to pick the first capital word or a sensible fallback word
    # For example, "I'm travelling to Ladakh" -> "travel to Ladakh" matches
    # "Plan a Goa trip" -> Let's check for specific known destinations or fallback
    known_destinations = ["goa", "manali", "ladakh", "kashmir", "munnar", "jaipur", "lonavala", "mahabaleshwar", "alibaug", "pune", "mumbai", "kalsubai", "rajmachi", "harihar"]
    for dest in known_destinations:
        if dest in text:
            location = dest.title()
            break

    # 2. Extract Duration (days)
    duration = 3  # Default fallback
    days_match = re.search(r"(\d+)\s*(?:day|night)", text)
    if days_match:
        duration = int(days_match.group(1))
    elif "weekend" in text:
        duration = 2
    elif "one day" in text or "1 day" in text or "single day" in text:
        duration = 1

    # 3. Extract Travellers
    travellers = 1  # Default fallback (solo)
    travellers_match = re.search(r"(\d+)\s*(?:people|traveller|traveler|friend|adult|person|member)", text)
    if travellers_match:
        travellers = int(travellers_match.group(1))
    elif "friends" in text or "group" in text:
        travellers = 4  # Default group size
    elif "couple" in text or "partner" in text or "wife" in text or "husband" in text:
        travellers = 2
    elif "family" in text:
        travellers = 4

    # 4. Extract Travel Style
    style = "Mid-range"  # Default fallback
    if any(word in text for word in ["luxury", "resort", "premium", "5 star", "expensive"]):
        style = "Luxury"
    elif any(word in text for word in ["budget", "cheap", "hostel", "backpacker", "backpacking", "low cost"]):
        style = "Budget"

    # 5. Extract Budget (in INR)
    budget = None
    budget_match = re.search(r"(?:under|rs\.?|inr|₹|budget of)\s*(\d+)(?:\s*k|\b)", text)
    if budget_match:
        budget = int(budget_match.group(1))
        # Handle "10k" or "5k" shorthand
        if "k" in text[budget_match.start():budget_match.end() + 10] or (budget < 1000 and "k" in text):
            budget = budget * 1000
    elif "10k" in text:
        budget = 10000
    elif "5k" in text:
        budget = 5000
    elif "20k" in text:
        budget = 20000
    elif "15k" in text:
        budget = 15000

    # 6. Extract Date and Time (for historical/trek details flow compatibility)
    date = "Not specified"
    time_of_day = "Not specified"
    
    # Date extraction
    if "today" in text:
        date = "Today"
    elif "tomorrow" in text:
        date = "Tomorrow"
    elif "this weekend" in text:
        date = "This weekend"
    elif "next weekend" in text:
        date = "Next weekend"
        
    # Time extraction
    if "morning" in text:
        time_of_day = "Morning"
    elif "afternoon" in text:
        time_of_day = "Afternoon"
    elif "evening" in text:
        time_of_day = "Evening"
    elif "night" in text:
        time_of_day = "Night"

    # If LLM is available, we can use it to refine the extraction if deterministic method is uncertain
    if llm and not location:
        try:
            prompt = f"""Analyze the travel request and extract the parameters:
Request: "{user_input}"

Format your output exactly as:
Destination: <name of place or None>
Duration: <number of days or 3>
Travellers: <number of travellers or 1>
Style: <Budget/Mid-range/Luxury>
Budget: <number or None>
Date: <date or Not specified>
Time: <time or Not specified>
"""
            llm_response = llm.invoke(prompt)
            lines = llm_response.strip().split("\n")
            for line in lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip().lower()
                    val = val.strip()
                    if "destination" in key and val.lower() != "none" and val:
                        location = val.title()
                    elif "duration" in key:
                        try:
                            duration = int(re.sub(r"\D", "", val))
                        except ValueError:
                            pass
                    elif "travellers" in key:
                        try:
                            travellers = int(re.sub(r"\D", "", val))
                        except ValueError:
                            pass
                    elif "style" in key and val in ["Budget", "Mid-range", "Luxury"]:
                        style = val
                    elif "budget" in key and val.lower() != "none":
                        try:
                            budget = int(re.sub(r"\D", "", val))
                        except ValueError:
                            pass
        except Exception:
            pass

    return {
        "destination": location,
        "duration": duration,
        "travellers": travellers,
        "style": style,
        "budget": budget,
        "date": date,
        "time": time_of_day
    }
