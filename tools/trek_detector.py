import json


def detect_trek(user_input):

    with open(
        "data/treks.json",
        "r",
        encoding="utf-8"
    ) as file:

        treks = json.load(file)

    text = user_input.lower()

    for trek_name in treks.keys():

        if trek_name in text:
            return trek_name

    return None