def choose_tool(user_input):

    text = user_input.lower()

    # ========================================================
    # PLANNER TOOL
    # ========================================================

    if any(word in text for word in [
        "plan a trek",
        "trek plan",
        "plan trek",
        "complete plan",
        "full plan",
        "create a trek plan",
        "plan my trek"
    ]):
        return "planner"

    # ========================================================
    # PACKING TOOL
    # ========================================================

    if any(word in text for word in [
        "packing",
        "packing list",
        "pack",
        "carry",
        "bag",
        "what should i carry"
    ]):
        return "packing"

    # ========================================================
    # DIFFICULTY TOOL
    # ========================================================

    if any(word in text for word in [
        "difficulty",
        "hard",
        "easy",
        "moderate",
        "how difficult"
    ]):
        return "difficulty"

    # ========================================================
    # ITINERARY TOOL
    # ========================================================

    if any(word in text for word in [
        "itinerary",
        "schedule"
    ]):
        return "itinerary"

    # ========================================================
    # WEATHER TOOL
    # ========================================================

    if any(word in text for word in [
        "weather",
        "forecast",
        "temperature",
        "rain"
    ]):
        return "weather"


    # ========================================================
    # DEFAULT
    # ========================================================
     
    if any(word in text for word in [
        "tell me about",
        "information about",
        "details about",
        "height",
        "duration"
    ]):
        return "trek_info"

    return "chat"