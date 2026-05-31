def get_weather(location):

    weather_data = {
        "kalsubai": "Cloudy, 22°C",
        "rajmachi": "Rainy, 24°C",
        "harihar": "Sunny, 28°C"
    }

    return weather_data.get(
        location.lower(),
        "Weather data unavailable."
    )