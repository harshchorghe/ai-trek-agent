from typing import Dict, Any, Optional

def estimate_budget(
    destination: str, 
    days: int = 3, 
    travellers: int = 1, 
    style: str = "Mid-range", 
    user_budget: Optional[int] = None,
    llm: Optional[Any] = None
) -> str:
    # Normalize style
    style = style.title()
    if style not in ["Budget", "Mid-range", "Luxury"]:
        style = "Mid-range"

    # Rates dictionary per traveller per day based on style
    # Base daily rates
    base_rates = {
        "Budget": {
            "accommodation": 800,   # Hostels / homestays
            "transport": 400,       # Local public transport / sharing
            "food": 500,            # Street food / local diners
            "activities": 300,      # Free sights / minor entries
            "shopping": 150         # Minor souvenirs
        },
        "Mid-range": {
            "accommodation": 2500,  # 3-star hotel / private room
            "transport": 1200,      # Cabs / auto rentals
            "food": 1200,           # Casual dining / cafes
            "activities": 800,      # Guided tours / entry tickets
            "shopping": 500         # Moderate shopping
        },
        "Luxury": {
            "accommodation": 7000,  # 4/5-star resorts
            "transport": 3000,      # Private hired cars / SUV
            "food": 3000,           # Fine dining / premium bars
            "activities": 2000,     # Premium activities / private tours
            "shopping": 1500        # High-end souvenirs / clothing
        }
    }

    rates = base_rates[style]
    
    # Destination adjustments
    dest_lower = destination.lower() if destination else ""
    if "ladakh" in dest_lower or "kashmir" in dest_lower:
        # Mountains have higher transport costs
        rates["transport"] += 1000
    elif "goa" in dest_lower:
        # Goa has higher food/nightlife and activity rates
        rates["food"] += 300
        rates["activities"] += 200

    # Calculate totals
    # Accommodation: room sharing factor (e.g. 2 people can share a room)
    rooms = (travellers + 1) // 2
    if style == "Budget":
        # Hostels are priced per bed (no sharing discount)
        accommodation_total = rates["accommodation"] * days * travellers
    else:
        accommodation_total = rates["accommodation"] * days * rooms

    transport_total = rates["transport"] * days
    # If mid-range/luxury, transport is usually per vehicle (shared by group)
    if style == "Budget":
        transport_total *= travellers

    food_total = rates["food"] * days * travellers
    activities_total = rates["activities"] * days * travellers
    shopping_total = rates["shopping"] * travellers
    
    subtotal = accommodation_total + transport_total + food_total + activities_total + shopping_total
    emergency_buffer = int(subtotal * 0.10)  # 10% buffer
    total_estimate = subtotal + emergency_buffer

    # Formatting local output
    output_lines = [
        f"💰 **Estimated Budget Plan for {destination.title()}**",
        f"📊 **Parameters**: {days} Days · {travellers} Traveller(s) · {style} Style",
        "",
        "| Expense Category | Cost (INR) | Details |",
        "| :--- | :--- | :--- |",
        f"| 🏨 **Accommodation** | ₹{accommodation_total:,} | {rooms} room(s) for {days} nights |" if style != "Budget" else f"| 🏨 **Accommodation** | ₹{accommodation_total:,} | Hostel beds for {days} nights |",
        f"| 🚗 **Transport** | ₹{transport_total:,} | Local cabs / rentals |" if style != "Budget" else f"| 🚗 **Transport** | ₹{transport_total:,} | Public transit / shared rides |",
        f"| 🍽️ **Food & Drinks** | ₹{food_total:,} | Daily meals & snacks |",
        f"| 🎡 **Activities** | ₹{activities_total:,} | Sightseeing & entry fees |",
        f"| 🛍️ **Shopping** | ₹{shopping_total:,} | Local souvenirs & items |",
        f"| 🛡️ **Emergency Buffer** | ₹{emergency_buffer:,} | 10% contingency fund |",
        f"| 💵 **Total Estimate** | **₹{total_estimate:,}** | **Estimated grand total** |",
        ""
    ]

    if user_budget:
        diff = user_budget - total_estimate
        if diff >= 0:
            output_lines.append(f"✅ *Your budget of ₹{user_budget:,} is sufficient! You have a surplus of ₹{diff:,}.*")
        else:
            output_lines.append(f"⚠️ *Note: Your budget limit is ₹{user_budget:,}. This plan exceeds it by ₹{abs(diff):,}. Try switching to a more budget-friendly style or reducing trip days.*")
            
    output_lines.append("\n💡 *Travel Consultant Tip*: Prices fluctuate seasonally. Booking flights and stays 45 days in advance can save up to 30%!")

    local_reply = "\n".join(output_lines)

    if llm:
        try:
            prompt = f"""You are an experienced travel consultant for Explorush.
We have computed a structured budget breakdown for a trip to {destination} for {days} days, with {travellers} travellers, and style "{style}".
Here are the details:
- Accommodation: ₹{accommodation_total}
- Transport: ₹{transport_total}
- Food: ₹{food_total}
- Activities: ₹{activities_total}
- Shopping: ₹{shopping_total}
- Emergency Buffer: ₹{emergency_buffer}
- Total Estimate: ₹{total_estimate}
- User's budget limit: {f'₹{user_budget}' if user_budget else 'Not specified'}

Write a friendly, professional, and conversational response presenting these numbers clearly and advising the user on how they can optimize their expenses.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    return local_reply
