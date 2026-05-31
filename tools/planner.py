from tools.weather import get_weather
from tools.packing import get_packing_list
from tools.itinerary import generate_itinerary


def create_trek_plan(location):

    weather = get_weather(location)
    packing = get_packing_list()
    itinerary = generate_itinerary()

    return f"""
========================
TREK PLAN : {location}
========================

WEATHER
--------
{weather}

PACKING LIST
------------
{packing}

ITINERARY
---------
{itinerary}

SAFETY TIPS
-----------
- Start early morning
- Carry extra water
- Wear trekking shoes
- Keep a power bank
- Check weather before departure
"""