# Explorush Travel Knowledge Base Cache Policies
# Time values defined in seconds. None indicates permanent caching (no auto-expiry).

CACHE_EXPIRY = {
    "weather": 3600,             # 1 Hour (Weather changes frequently)
    "events": 86400,             # 24 Hours (Daily cultural events/fairs)
    
    # Permanent travel assets (No Auto-Expiry, updated only on manual refresh)
    "planner": None,
    "itinerary": None,
    "budget": None,
    "hotel": None,
    "restaurant": None,
    "transport": None,
    "nearby": None,
    "activities": None,
    "packing": None,
    "faq": None,
    "emergency": None,
    "visa": None,
    "currency": None,
    "travelTips": None,
    "localInsights": None,
    "history": None
}
