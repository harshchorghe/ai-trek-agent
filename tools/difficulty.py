def get_trek_difficulty(trek_name):

    difficulties = {
        "rajmachi": "Easy",
        "kalsubai": "Moderate",
        "harihar": "Hard",
        "kalavantin": "Hard"
    }

    return difficulties.get(
        trek_name.lower(),
        "Difficulty data not available."
    )