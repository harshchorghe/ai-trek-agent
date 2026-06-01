def get_smart_packing_list(weather_text):

    weather = weather_text.lower()

    items = [
        "Water Bottle",
        "Trekking Shoes",
        "Snacks",
        "Power Bank"
    ]

    if "rain" in weather:

        items.extend([
            "Raincoat",
            "Waterproof Backpack Cover",
            "Extra Clothes"
        ])

    if "fog" in weather:

        items.extend([
            "Flashlight",
            "Reflective Jacket"
        ])

    if "clear" in weather:

        items.extend([
            "Cap",
            "Sunscreen"
        ])

    return "\n".join(
        f"- {item}"
        for item in items
    )