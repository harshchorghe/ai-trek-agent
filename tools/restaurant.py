from typing import Dict, List, Optional, Any

RESTAURANTS_DB = {
    "goa": {
        "Cafes": ["Artjuna (Anjuna) - Garden cafe & lifestyle shop", "Eva Cafe (Anjuna) - Sunset sea views", "Babka (Anjuna) - Great coffee & pastries"],
        "Restaurants": ["Gunpowder (Assagao) - South Indian coastal cuisine", "The Fisherman's Wharf (Cavelossim) - Seafood thali", "Thalassa (Siolim) - Greek dining with views"],
        "Street Food": ["Cutlet Bread at Maposa Stalls", "Fish Thali at local shacks", "Gadre's Ros Omlette (Panaji)"]
    },
    "manali": {
        "Cafes": ["Cafe 1947 (Old Manali) - Riverside cafe & live music", "Dylan's Toasted & Roasted - Legendary coffee", "Lazy Dog Cafe (Old Manali)"],
        "Restaurants": ["Chopsticks (Mall Road) - Tibetan & Chinese", "Johnson's Cafe - Famous for Trout fish", "Il Forno - Wood-fired Italian pizzas"],
        "Street Food": ["Siddu (traditional steamed wheat buns)", "Thukpa & Momos at Mall Road stalls", "Yak cheese slices"]
    },
    "ladakh": {
        "Cafes": ["Lala's Art Cafe (Leh) - Cozy traditional mudbrick cafe", "Leh Halal Cafe", "The Solitaire Cafe"],
        "Restaurants": ["The Tibetan Kitchen (Leh) - Authentic Tibetan food", "Bon Appetit - Continental with mountain views", "Chopsticks Noodle Bar"],
        "Street Food": ["Mutton Momos at local market", "Tigmo (fermented bread) with soup", "Butter tea (Gur-Gur Chai)"]
    },
    "lonavala": {
        "Cafes": ["Coopers Fudge Cafe", "Cafe 24 (Della Resorts)", "German Bakery Lonavala"],
        "Restaurants": ["The Kinara Village Dhaba - Multi-cuisine Punjabi theme", "Hotel Rama Krishna - South Indian & North Indian", "Sunny Da Dhaba (NH4)"],
        "Street Food": ["Lonavala Chikki (maganlal)", "Hot Corn Pakodas at Tiger Point", "Vada Pav at Golden Vada Pav"]
    },
    "mahabaleshwar": {
        "Cafes": ["Mapro Garden Cafe - Strawberry cream & wood-fired pizza", "The Sizzler Place", "Bagicha Corner"],
        "Restaurants": ["The Grapevine Restaurant - Famous for steaks & wine", "Hotel Rajmahal - Authentic Maharashtrian Thali", "Hirkani Garden Restaurant"],
        "Street Food": ["Fresh Strawberry with Whipped Cream", "Corn patties & hot bhaji", "Chana masala stalls"]
    },
    "mumbai": {
        "Cafes": ["Pizza By The Bay (Marine Drive)", "Mockingbird Cafe Bar (Churchgate)", "Kyani & Co. (Marine Lines) - Parsi Cafe"],
        "Restaurants": ["Gaylord (Churchgate) - Continental & Indian heritage", "Khyber (Kala Ghoda) - North Indian royal theme", "Leopold Cafe (Colaba)"],
        "Street Food": ["Pav Bhaji at Sardar / Chowpatty", "Bhel Puri at Girgaon Chowpatty", "Vada Pav at Ashok Vada Pav (Dadari)"]
    }
}

def get_restaurant_recommendations(destination: str, llm: Optional[Any] = None) -> str:
    dest_key = destination.lower().strip()
    
    # Check database
    cafes = []
    restaurants = []
    street_food = []
    
    if dest_key in RESTAURANTS_DB:
        cafes = RESTAURANTS_DB[dest_key].get("Cafes", [])
        restaurants = RESTAURANTS_DB[dest_key].get("Restaurants", [])
        street_food = RESTAURANTS_DB[dest_key].get("Street Food", [])
    else:
        # Default recommendations
        cafes = [f"Boutique Garden Cafe in {destination.title()}", f"Artisanal Coffee House in {destination.title()}"]
        restaurants = [f"Traditional Fine-Diner in {destination.title()}", f"Scenic Riverside/Hillside Restaurant in {destination.title()}"]
        street_food = [f"Local traditional street stalls in {destination.title()}", f"Famous sweet & snack outlets in {destination.title()}"]

    if llm:
        try:
            prompt = f"""You are an experienced food critic and travel guide for Explorush.
Write a rich, appetising recommendation for a user asking about where to eat in {destination}.
Highlight these spots from our database:
- Cafes: {', '.join(cafes)}
- Restaurants: {', '.join(restaurants)}
- Street Food: {', '.join(street_food)}

Write a friendly, enthusiastic, and conversational response. Keep it concise but mouth-watering!
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local reply
    output = f"🍽️ **Foodie Guide for {destination.title()}**:\n\n"
    
    if cafes:
        output += "☕ **Top Cafes**:\n"
        for c in cafes:
            output += f"- {c}\n"
        output += "\n"
        
    if restaurants:
        output += "🍲 **Recommended Restaurants**:\n"
        for r in restaurants:
            output += f"- {r}\n"
        output += "\n"
        
    if street_food:
        output += "🍢 **Must-Try Street Food & Local Eats**:\n"
        for sf in street_food:
            output += f"- {sf}\n"
        output += "\n"
        
    output += "💡 *Foodie Tip*: Always prefer bottled water, and look for stalls with high local turnaround for the freshest street food!"
    return output
