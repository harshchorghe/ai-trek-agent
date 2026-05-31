import json


def get_trek_info(trek_name):

    with open(
        "data/treks.json",
        "r",
        encoding="utf-8"
    ) as file:

        treks = json.load(file)

    return treks.get(
        trek_name.lower(),
        "Trek not found."
    )