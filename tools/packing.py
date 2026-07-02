from typing import List, Dict, Optional, Any

PACKING_CATEGORIES = {
    "beach": [
        "Swimwear & rash guards",
        "High SPF sunscreen & lip balm",
        "Polarized sunglasses",
        "Quick-dry beach towel",
        "Flip flops & water shoes",
        "Waterproof phone pouch",
        "Sun hat or cap"
    ],
    "mountain": [
        "Warm layers (fleece or down jacket)",
        "Sturdy hiking boots or trail runners",
        "Thermal innerwear",
        "Daypack (20-30L) with rain cover",
        "Beanies & gloves",
        "Trekking poles",
        "Hydration pack or water bottles"
    ],
    "business": [
        "Formal wear & suits",
        "Wrinkle-release spray or travel iron",
        "Laptop, chargers, & presentation accessories",
        "Notebook & professional pen",
        "Business cards",
        "Travel-sized premium grooming kit"
    ],
    "international": [
        "Passport (with at least 6 months validity)",
        "Visa copies & printed hotel bookings",
        "Universal travel adapter",
        "Forex card & local currency cash",
        "Travel insurance documents",
        "Copies of vital documents saved offline"
    ],
    "roadtrip": [
        "Car charger with multiple USB ports",
        "Phone mount for navigation",
        "Road trip playlist (downloaded offline)",
        "Durable cooler with snacks & drinks",
        "Travel neck pillow",
        "Hand sanitizer & wet wipes",
        "Emergency roadside kit"
    ],
    "camping": [
        "Tent, tarp, & stakes",
        "Sleeping bag & sleeping pad",
        "Headlamp & extra batteries",
        "Insect repellent (DEET based)",
        "Portable stove & fuel",
        "Swiss Army multi-tool",
        "Biodegradable soap"
    ],
    "winter": [
        "Heavy insulated coat or parka",
        "Thermal base layers (top & bottom)",
        "Woolen gloves, scarf, & socks",
        "Lip balm & heavy moisturizer",
        "Insulated boots with good grip",
        "Hand warmers"
    ],
    "monsoon": [
        "Compact umbrella & lightweight raincoat",
        "Waterproof backpack cover",
        "Quick-dry clothing (avoid denim)",
        "Silica gel packets for electronics",
        "Waterproof dry bag",
        "Spare socks & sandals with good grip"
    ],
    "luxury": [
        "Designer evening wear",
        "High-end camera or lenses",
        "Noise-canceling headphones",
        "Premium toiletries & perfumes",
        "Stylish sunglasses"
    ],
    "backpacking": [
        "Lightweight microfibre towel",
        "Combination locks for hostels",
        "Portable water purifier/lifestraw",
        "Compact first aid kit",
        "Multi-purpose utility cord",
        "Lightweight compression sacks"
    ],
    "family": [
        "Multi-port power bank",
        "Basic family first aid kit (painkillers, band-aids)",
        "Snack bars & dry fruits",
        "Travel card games or pocket entertainment",
        "Sanitizing sprays & wipes"
    ],
    "kids": [
        "Baby wipes & diapers",
        "Pediatric medicines & rehydration salts",
        "Kid-friendly snacks & formula",
        "Favorite small toy or coloring book",
        "Child carrier or compact stroller"
    ],
    "trekking": [
        "Trekking shoes with good ankle support",
        "Water bottle (2L minimum)",
        "Torch or headlamp (essential)",
        "First aid kit & personal medicines",
        "Energy bars, snacks, & ORS packets",
        "Power bank",
        "Raincoat/Poncho (especially in Sahyadris)"
    ]
}

def get_packing_list(query: str = "", destination: str = "", llm: Optional[Any] = None) -> str:
    text = (query + " " + destination).lower()
    
    # 1. Identify active categories based on keywords
    selected_categories = []
    
    # Check keywords for beach
    if any(w in text for w in ["beach", "goa", "alibaug", "sea", "ocean", "coastal", "kashid"]):
        selected_categories.append("beach")
    # Check keywords for mountain
    if any(w in text for w in ["mountain", "hill", "manali", "ladakh", "kashmir", "munnar", "kalsubai", "rajmachi", "harihar", "altitude", "elevation"]):
        selected_categories.append("mountain")
    # Check keywords for trekking
    if any(w in text for w in ["trek", "hike", "climb", "trekking", "fort"]):
        selected_categories.append("trekking")
    # Check keywords for business
    if any(w in text for w in ["business", "conference", "work", "meeting", "formal"]):
        selected_categories.append("business")
    # Check keywords for international
    if any(w in text for w in ["international", "visa", "abroad", "foreign"]):
        selected_categories.append("international")
    # Check keywords for roadtrip
    if any(w in text for w in ["road trip", "drive", "car", "roadtrip"]):
        selected_categories.append("roadtrip")
    # Check keywords for camping
    if any(w in text for w in ["camp", "camping", "tent"]):
        selected_categories.append("camping")
    # Check keywords for winter
    if any(w in text for w in ["winter", "cold", "snow", "ice", "december", "january"]):
        selected_categories.append("winter")
    # Check keywords for monsoon
    if any(w in text for w in ["monsoon", "rain", "rainy", "drizzle", "june", "july", "august"]):
        selected_categories.append("monsoon")
    # Check keywords for luxury
    if any(w in text for w in ["luxury", "resort", "premium", "5 star"]):
        selected_categories.append("luxury")
    # Check keywords for backpacking
    if any(w in text for w in ["backpacking", "backpacker", "hostel", "budget"]):
        selected_categories.append("backpacking")
    # Check keywords for kids
    if any(w in text for w in ["kids", "child", "baby", "infant", "toddler"]):
        selected_categories.append("kids")
    # Check keywords for family
    if any(w in text for w in ["family", "parent", "parents"]):
        selected_categories.append("family")

    # If no category detected, default to a general packing checklist
    if not selected_categories:
        # Default combination
        selected_categories = ["family", "roadtrip"]

    # Deduplicate categories
    selected_categories = list(set(selected_categories))
    
    # 2. Gather items
    packing_data = {}
    for cat in selected_categories:
        packing_data[cat.title()] = PACKING_CATEGORIES[cat]

    # 3. Format response
    if llm:
        try:
            items_str = ""
            for cat, items in packing_data.items():
                items_str += f"\n### {cat} Gear:\n" + "\n".join([f"- {i}" for i in items])
            prompt = f"""You are a travel packing specialist for Explorush.
The user wants a packing list. Query: "{query}", Destination: "{destination}".
Here are the selected gear items from our database:
{items_str}

Please organize these into a structured, neat, and highly friendly travel packing guide. Provide brief tips on how to pack efficiently (e.g. rolling clothes, keeping essentials accessible). Keep the output professional and concise.
"""
            return llm.invoke(prompt)
        except Exception:
            pass

    # Deterministic local fallback output
    output = "🎒 **Explorush Custom Packing Checklist**\n"
    output += "Here is your personalized gear list based on your trip parameters:\n\n"
    
    # Basic Essentials always included
    output += "📌 **Standard Essentials (Always Pack)**:\n"
    output += "- Valid IDs & booking confirmations\n"
    output += "- Phone, chargers & power bank\n"
    output += "- Personal toiletries & prescription medicines\n"
    output += "- Cash & credit/debit cards\n\n"
    
    # Categorized list
    for cat, items in packing_data.items():
        output += f"👕 **{cat} Trip Gear**:\n"
        for item in items:
            output += f"- {item}\n"
        output += "\n"
        
    output += "💡 *Travel Tip*: Roll your clothes instead of folding to save 30% suitcase space, and place heavy items at the bottom of your bag."
    return output