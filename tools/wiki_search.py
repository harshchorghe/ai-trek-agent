import requests


def get_wiki_summary(trek_name):

    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + trek_name.replace(" ", "_")
    )

    headers = {
        "User-Agent": "AITrekPlanner/1.0 (Educational Project)"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()

        return data.get(
            "extract",
            None
        )

    except Exception as e:

        print("Wiki Error:", e)

        return None