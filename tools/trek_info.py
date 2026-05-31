from tools.trek_db import get_trek_info


def format_trek_info(trek_name):

    info = get_trek_info(trek_name)

    if isinstance(info, str):
        return info

    return f"""
Trek: {trek_name.title()}

Difficulty: {info['difficulty']}
Duration: {info['duration']}
Height: {info['height']}
"""