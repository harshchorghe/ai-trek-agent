def get_safety_tips(weather_text):

    weather = weather_text.lower()

    tips = [
        "Carry sufficient water",
        "Wear trekking shoes",
        "Inform family before the trek",
        "Keep a power bank"
    ]

    if "rain" in weather:

        tips.extend([
            "Carry a raincoat",
            "Use a waterproof backpack cover",
            "Protect electronics from water"
        ])

    if "thunderstorm" in weather:

        tips.extend([
            "Avoid exposed ridges",
            "Seek shelter during lightning"
        ])

    if "fog" in weather:

        tips.extend([
            "Carry a flashlight",
            "Stay with your trekking group"
        ])

    return "\n".join(f"- {tip}" for tip in tips)