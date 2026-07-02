from typing import Optional, Any
from tools.trip_details import extract_trip_details
from tools.weather import get_weather
from tools.packing import get_packing_list
from tools.itinerary import generate_itinerary
from tools.budget import estimate_budget
from tools.hotel import get_hotel_recommendations
from tools.restaurant import get_restaurant_recommendations
from tools.nearby import get_nearby_attractions
from tools.transport import get_transportation_guidance
from tools.emergency import get_emergency_guidance
from tools.travel_tips import get_travel_tips
from tools.events import get_cultural_events
from tools.activities import get_adventure_activities
from tools.trek import detect_trek, format_trek_info
from tools.db import get_cached_plan, save_plan_to_cache

def create_travel_plan(query: str, llm: Optional[Any] = None) -> str:
    # 1. Extract details from the user prompt
    details = extract_trip_details(query, llm)
    
    destination = details.get("destination")
    duration = details.get("duration", 3)
    travellers = details.get("travellers", 1)
    style = details.get("style", "Mid-range")
    budget_limit = details.get("budget")
    
    if not destination:
        # Check if a trek is detected instead
        trek_name = detect_trek(query)
        if trek_name:
            destination = trek_name
        else:
            destination = "Goa"  # Fallback destination if none extracted

    destination_title = destination.title()

    # CHECK CACHE FIRST BEFORE GENERATING HEAVY PARTS
    cached_plan = get_cached_plan(destination, duration, travellers, style)
    if cached_plan:
        return cached_plan

    # 2. Invoke sub-tools to build sections
    weather_info = get_weather(destination)
    packing_info = get_packing_list(query, destination, llm)
    itinerary_info = generate_itinerary(destination, duration, llm)
    budget_info = estimate_budget(destination, duration, travellers, style, budget_limit, llm)
    hotel_info = get_hotel_recommendations(destination, style, llm)
    food_info = get_restaurant_recommendations(destination, llm)
    sightseeing_info = get_nearby_attractions(destination, llm)
    transport_info = get_transportation_guidance(destination, llm)
    safety_info = get_emergency_guidance(query, destination, llm)
    culture_info = get_cultural_events(destination, llm)
    adventure_info = get_adventure_activities(destination, llm)
    general_tips = get_travel_tips(query, llm)

    # 3. Synthesize the final document
    divider = "========================================================\n"
    section_divider = "--------------------------------------------------------\n"
    
    plan = []
    plan.append(divider)
    plan.append(f"🏝️ EXPLORUSH TRAVEL PLAN: {destination_title.upper()} 🏝️\n")
    plan.append(f"Parameters: {duration} Days · {travellers} Traveller(s) · {style} Travel Style\n")
    plan.append(divider)
    
    plan.append("📊 TRIP SUMMARY\n")
    plan.append(f"- Destination: {destination_title}\n")
    plan.append(f"- Duration: {duration} Days / {duration - 1 if duration > 1 else 1} Nights\n")
    plan.append(f"- Travellers: {travellers} person(s)\n")
    plan.append(f"- Travel Style: {style}\n")
    if budget_limit:
        plan.append(f"- Target Budget Limit: ₹{budget_limit:,}\n")
    plan.append("\n" + section_divider)
    
    plan.append("🚗 TRANSPORTATION & ROUTES\n")
    plan.append(transport_info + "\n")
    plan.append(section_divider)
    
    plan.append("🏨 ACCOMMODATION PLANNED\n")
    plan.append(hotel_info + "\n")
    plan.append(section_divider)
    
    plan.append("📅 DAILY ITINERARY\n")
    plan.append(itinerary_info + "\n")
    plan.append(section_divider)
    
    plan.append("🍽️ DINING & LOCAL CUISINE\n")
    plan.append(food_info + "\n")
    plan.append(section_divider)
    
    plan.append("📸 SIGHTSEEING & HIDDEN GEMS\n")
    plan.append(sightseeing_info + "\n")
    plan.append(section_divider)
    
    plan.append("🏂 ADVENTURE ACTIVITIES & FESTIVALS\n")
    plan.append(adventure_info + "\n\n")
    plan.append(culture_info + "\n")
    plan.append(section_divider)
    
    plan.append("💰 ESTIMATED BUDGET BREAKDOWN\n")
    plan.append(budget_info + "\n")
    plan.append(section_divider)
    
    plan.append("☁️ WEATHER WINDOW & ADVISORY\n")
    plan.append(weather_info + "\n")
    plan.append(section_divider)
    
    plan.append("🎒 PACKING LIST\n")
    plan.append(packing_info + "\n")
    plan.append(section_divider)
    
    plan.append("🛡️ SAFETY & EMERGENCY INFORMATION\n")
    plan.append(safety_info + "\n")
    plan.append(section_divider)
    
    plan.append("💡 GENERAL TRAVEL TIPS\n")
    plan.append(general_tips + "\n")
    plan.append(divider)
    
    plan.append("Prepared by Explorush AI Travel Consultant. Safe travels! 🎒✈️")
    
    plan_text = "\n".join(plan)
    
    # SAVE TO CACHE FOR NEXT TIME
    save_plan_to_cache(destination, duration, travellers, style, plan_text)
    
    return plan_text