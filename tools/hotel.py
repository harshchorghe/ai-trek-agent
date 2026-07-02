from typing import Dict, List, Optional, Any

HOTELS_DB = {
    "goa": {
        "Budget": ["Zostel Goa (Calangute)", "The Hostel Crowd (Anjuna)", "Jungle by Hostel Crowd"],
        "Mid-range": ["Bloom Suites (Calangute)", "Estrela Do Mar Beach Resort", "Casa Anjuna"],
        "Luxury": ["Taj Exotica Resort & Spa", "Cidade de Goa", "W Goa (Vagator)"]
    },
    "manali": {
        "Budget": ["Zostel Manali (Old Manali)", "Alt Life (Dharamkot style)", "The Lost Tribe Hostel"],
        "Mid-range": ["Hotel Highland", "Solang Valley Resort", "Johnson Lodge & Spa"],
        "Luxury": ["Span Resort & Spa", "The Orchard Greens Resort", "Manuallaya Resort"]
    },
    "ladakh": {
        "Budget": ["Zostel Leh", "Raybo Hostel", "Bijoo Guest House"],
        "Mid-range": ["Hotel Singge Palace", "Hotel Caravan Centre", "The Grand Dragon Ladakh (Standard Rooms)"],
        "Luxury": ["The Grand Dragon Ladakh (Luxury Suites)", "The Ultimate Travelling Camp (Chamba Camp Thiksey)", "Hotel Zen Ladakh"]
    },
    "lonavala": {
        "Budget": ["Zostel Plus Lonavala", "Hostel Backpackers Lonavala", "Saraswati Guest House"],
        "Mid-range": ["Fariyas Resort Lonavala", "Rhythm Lonavala", "Valvan Village Resort"],
        "Luxury": ["Della Resorts", "The Machan (Treehouses)", "Hilton Shillim Estate Retreat & Spa"]
    },
    "mahabaleshwar": {
        "Budget": ["Zostel Plus Panchgani (Nearby)", "Hotel Preeti Executive", "Grand Resort Mahabaleshwar"],
        "Mid-range": ["Mapro Garden Resort style", "Brightland Resort & Spa", "Saj Resort"],
        "Luxury": ["Le Meridien Mahabaleshwar Resort & Spa", "Evershine Resort", "Bella Vista Resort"]
    },
    "munnar": {
        "Budget": ["Zostel Munnar", "The Hosteller Munnar", "JJ Cottage"],
        "Mid-range": ["Tea Valley Resort", "Munnar Castle", "Elixir Hills (Junior Suites)"],
        "Luxury": ["Blanket Hotel & Spa", "The Panoramic Getaway", "Windermere Estate"]
    },
    "kashmir": {
        "Budget": ["Hostel In Srinagar", "Gulaab Tourist House", "Zostel Srinagar"],
        "Mid-range": ["Hotel Heevan (Pahalgam)", "Khyber Himalayan Resort (Gulmarg - Standard)", "Ahdoos (Srinagar)"],
        "Luxury": ["The Khyber Himalayan Resort & Spa (Gulmarg)", "The Lalit Grand Palace (Srinagar)", "Taj Lake Palace Srinagar (Taj Palace houseboat)"]
    },
    "jaipur": {
        "Budget": ["Zostel Jaipur", "Moustache Hostel Jaipur", "Backpacker Panda"],
        "Mid-range": ["Umaid Bhawan Hotel", "Shahpura House", "Alsisar Haveli"],
        "Luxury": ["Rambagh Palace", "The Oberoi Rajvilas", "Taj Jai Mahal Palace"]
    },
    "alibaug": {
        "Budget": ["Zostel Alibaug", "Outpost Alibaug (Standard)", "Local homestays at Kashid"],
        "Mid-range": ["Radisson Blu Resort & Spa Alibaug", "Tropicana Resort", "Sai Inn Resort"],
        "Luxury": ["The Mansion House", "Radisson Blu (Suites)", "U Tropicana Alibaug (Premium Villa)"]
    },
    "ujjain": {
        "Budget": ["MPT Shipra Residency (Dormitory)", "Mahakal Dharamshala", "Hotel Avanti clean rooms"],
        "Mid-range": ["MPT Shipra Residency", "Hotel Abika Elite", "Hotel Imperial"],
        "Luxury": ["Radisson Hotel Ujjain", "Hotel Anjushree", "Solitaire Hotel & Resort"]
    },
    "rishikesh": {
        "Budget": ["Zostel Rishikesh", "The Hostel Crowd (Tapovan)", "Madpackers Rishikesh"],
        "Mid-range": ["Aloha on the Ganges (Standard Rooms)", "Hotel Deep Palace", "Hotel Ganga Kinare"],
        "Luxury": ["Ananda in the Himalayas (Nearby luxury wellness)", "Taj Rishikesh Resort & Spa", "Aloha on the Ganges (Suites)"]
    }
}


def get_hotel_recommendations(destination: str, style: str = "Mid-range", llm: Optional[Any] = None) -> str:
    dest_key = destination.lower().strip()
    style_key = style.title().strip()
    if style_key not in ["Budget", "Mid-range", "Luxury"]:
        style_key = "Mid-range"

    # Find hotels
    hotels = []
    if dest_key in HOTELS_DB:
        hotels = HOTELS_DB[dest_key].get(style_key, [])
    else:
        # Default fallback recommendations
        hotels = [
            f"Local Homestay / Hostel in {destination.title()}",
            f"3-Star Boutique Hotel in {destination.title()}",
            f"Premium Heritage Resort in {destination.title()}"
        ]

    from tools.db import get_cached_item, save_cached_item
    section_category = f"hotel_{style_key.lower()}"
    cached = get_cached_item(section_category, destination)
    if cached:
        return cached

    # Format output
    if llm:
        try:
            if dest_key in HOTELS_DB:
                hotels_list = ", ".join(HOTELS_DB[dest_key].get(style_key, []))
                prompt = f"""You are a luxury travel concierge for Explorush.
Recommend accommodation options for a user traveling to {destination} with a "{style_key}" travel style.
Here are the recommendations from our database: {hotels_list}.

Write a brief, attractive, and helpful summary of these recommendations and why they are great fits. Keep it concise.
"""
            else:
                prompt = f"""You are a luxury travel concierge for Explorush.
Recommend 3 actual, real-world accommodation options (with names, budget range, and brief descriptions) for a user traveling to {destination} with a "{style_key}" travel style.
Make sure the hotels are realistic, popular, and match the budget class of "{style_key}". Keep it clean and concise.
"""
            res = llm.invoke(prompt)
            if res:
                save_cached_item(section_category, destination, res)
                return res
        except Exception:
            pass

    # Deterministic local reply
    output = f"🏨 **Recommended Accommodations in {destination.title()}** ({style_key} Style):\n"
    for hotel in hotels:
        if "zostel" in hotel.lower() or "hostel" in hotel.lower():
            emoji = "🎒" # Hostel
        elif "resort" in hotel.lower() or "spa" in hotel.lower() or "palace" in hotel.lower():
            emoji = "👑" # Resort/Luxury
        else:
            emoji = "🏢" # Hotel
        output += f"- {emoji} **{hotel}**\n"
        
    output += "\n💡 *Booking Tip*: We recommend checking reviews on TripAdvisor and booking hostels/resorts directly on their official website for the best cancelation policies."
    return output
