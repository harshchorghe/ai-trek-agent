from tools.weather import get_weather
from tools.packing import get_packing_list
from tools.itinerary import generate_itinerary
from tools.safety import get_safety_tips
from tools.trek_info import format_trek_info
from tools.smart_packing import get_smart_packing_list


def create_trek_plan(location):

    trek_info = format_trek_info(location)

    weather = get_weather(location)

    packing = get_smart_packing_list(weather)

    itinerary = generate_itinerary()

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