import requests
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


def get_weather(location):

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

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        current = data["current"]

        temperature = current["temperature_2m"]

        humidity = current["relative_humidity_2m"]

        wind_speed = current["wind_speed_10m"]

        weather_code = current["weather_code"]

        weather_condition = WEATHER_CODES.get(
            weather_code,
            "Unknown"
        )

        rain_probability = data[
            "daily"
        ][
            "precipitation_probability_max"
        ][0]

        return (
            f"Temperature: {temperature}°C\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} km/h\n"
            f"Rain Probability: {rain_probability}%\n"
            f"Weather: {weather_condition}"
        )

    except Exception as e:

        return f"Weather API Error: {e}"