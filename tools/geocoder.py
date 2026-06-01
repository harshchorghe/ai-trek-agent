import requests


def get_coordinates(place_name):

    url = (
        "https://nominatim.openstreetmap.org/search"
        f"?q={place_name}"
        "&format=json"
        "&limit=1"
    )

    headers = {
        "User-Agent": "AI-Trek-Planner"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        data = response.json()

        if not data:
            return None

        latitude = data[0]["lat"]
        longitude = data[0]["lon"]

        return (
            float(latitude),
            float(longitude)
        )

    except Exception:

        return None