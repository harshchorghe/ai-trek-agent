from tools.weather import get_weather
from tools.itinerary import generate_itinerary
from tools.safety import get_safety_tips
from tools.smart_packing import get_smart_packing_list
from tools.dynamic_trek_info import get_dynamic_trek_info


def create_trek_plan(location, llm):

    # Dynamic trek information from Wikipedia + Phi3
    trek_info = get_dynamic_trek_info(
        location,
        llm
    )

    # Real weather
    weather = get_weather(location)

    # Weather-aware packing list
    packing = get_smart_packing_list(weather)

    # Trek itinerary
    itinerary = generate_itinerary()

    # Weather-aware safety tips
    safety_tips = get_safety_tips(weather)

    return f"""
=================================
TREK PLAN : {location.title()}
=================================

TREK INFORMATION
----------------
{trek_info}

WEATHER
-------
{weather}

PACKING LIST
------------
{packing}

ITINERARY
---------
{itinerary}

SAFETY TIPS
-----------
{safety_tips}
"""