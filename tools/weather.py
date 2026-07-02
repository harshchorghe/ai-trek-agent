import requests
from typing import Optional, Tuple
from tools.geocoder import get_coordinates

WEATHER_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    80: "Rain Showers",
    95: "Thunderstorm"
}

def get_weather_advice(condition: str, temp: float) -> str:
    cond = condition.lower()
    advice = []
    
    if "rain" in cond or "drizzle" in cond or "shower" in cond:
        advice.append("⛈️ Carry waterproof gear (raincoat, umbrella, dry bags). slippery paths are expected.")
    elif "thunderstorm" in cond:
        advice.append("⚡ High risk of lightning. Avoid exposed ridges, summits, and iron ladders. Seek indoor shelter.")
    elif "fog" in cond:
        advice.append("🌫️ Reduced visibility. Keep flashlights handy. Drive or hike with caution and stick to marked routes.")
    elif "snow" in cond:
        advice.append("❄️ Extremely cold & freezing. Dress in thick insulated layers, gloves, and thermal wear.")
    elif "clear" in cond:
        advice.append("☀️ Clear and sunny. Wear a cap, sunglasses, and sunscreen. Keep hydrated.")
    else:
        advice.append("👟 Good weather for sightseeing and outdoor exploration. Carry standard gear.")
        
    if temp < 10:
        advice.append("🧥 Temperature is chilly. Carry a light jacket or windbreaker.")
    elif temp > 32:
        advice.append("🥵 Temperature is hot. Limit afternoon outdoor exposure and carry plenty of water/electrolytes.")
        
    return " ".join(advice)

def get_weather(location: str) -> str:
    coordinates = get_coordinates(location)

    if not coordinates:
        return "Location not found."

    latitude, longitude = coordinates

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        "&current=temperature_2m,"
        "relative_humidity_2m,"
        "wind_speed_10m,"
        "weather_code"
        "&daily=precipitation_probability_max"
        "&forecast_days=1"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        current = data["current"]
        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind_speed = current["wind_speed_10m"]
        weather_code = current["weather_code"]

        weather_condition = WEATHER_CODES.get(weather_code, "Unknown")
        rain_probability = data["daily"]["precipitation_probability_max"][0]
        
        advice = get_weather_advice(weather_condition, temperature)

        return (
            f"🌤️ **Weather Forecast for {location.title()}**:\n"
            f"- 🌡️ **Temperature**: {temperature}°C\n"
            f"- 💧 **Humidity**: {humidity}%\n"
            f"- 💨 **Wind Speed**: {wind_speed} km/h\n"
            f"- ☔ **Rain Probability**: {rain_probability}%\n"
            f"- ☁️ **Condition**: {weather_condition}\n\n"
            f"📝 **Travel Advice**: {advice}"
        )

    except Exception as e:
        return f"Weather API Error: {e}"