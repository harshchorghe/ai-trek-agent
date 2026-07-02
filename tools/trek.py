import json
import requests
from typing import Optional, Dict, Any, Union

def get_wiki_summary(trek_name: str) -> Optional[str]:
    url = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        + trek_name.replace(" ", "_")
    )
    headers = {
        "User-Agent": "AITrekPlanner/1.0 (Educational Project)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        return data.get("extract", None)
    except Exception as e:
        print("Wiki Error:", e)
        return None

def get_trek_info(trek_name: str) -> Union[Dict[str, Any], str]:
    try:
        with open("data/treks.json", "r", encoding="utf-8") as file:
            treks = json.load(file)
        return treks.get(trek_name.lower(), "Trek not found.")
    except Exception:
        # Fallback dictionary if json is not available
        difficulties = {
            "rajmachi": {"difficulty": "Easy", "duration": "3-4 hours", "height": "2710 ft"},
            "kalsubai": {"difficulty": "Moderate", "duration": "4-5 hours", "height": "5400 ft"},
            "harihar": {"difficulty": "Hard", "duration": "3 hours", "height": "3676 ft"},
            "kalavantin": {"difficulty": "Hard", "duration": "3-4 hours", "height": "2300 ft"}
        }
        return difficulties.get(trek_name.lower(), "Trek not found.")

def format_trek_info(trek_name: str) -> str:
    info = get_trek_info(trek_name)
    if isinstance(info, str):
        return info
    return f"""Trek: {trek_name.title()}
Difficulty: {info['difficulty']}
Duration: {info['duration']}
Height: {info['height']}"""

def get_trek_difficulty(trek_name: str) -> str:
    info = get_trek_info(trek_name)
    if isinstance(info, dict):
        return info.get("difficulty", "Difficulty data not available.")
    return "Difficulty data not available."

def detect_trek(user_input: str) -> Optional[str]:
    text = user_input.lower()
    try:
        with open("data/treks.json", "r", encoding="utf-8") as file:
            treks = json.load(file)
        for trek_name in treks.keys():
            if trek_name in text:
                return trek_name
    except Exception:
        pass
    
    # Fallback checklist
    for trek_name in ["kalsubai", "rajmachi", "harihar", "kalavantin"]:
        if trek_name in text:
            return trek_name
    return None

def get_dynamic_trek_info(trek_name: str, llm: Any) -> str:
    summary = get_wiki_summary(trek_name)
    if not summary:
        # Fallback to local DB summary if Wikipedia fails
        info = get_trek_info(trek_name)
        if isinstance(info, dict):
            return f"Overview: A popular trek known for its beautiful trails. Difficulty: {info['difficulty']}. Highlights: Duration of {info['duration']}, height of {info['height']}."
        return f"No information found for {trek_name}."

    prompt = f"""You are a trekking expert.

Using the information below, create a trek guide.

Trek Name:
{trek_name}

Information:
{summary}

Provide:

1. Overview
2. Difficulty
3. Highlights

Keep it concise.
"""
    return llm.invoke(prompt)
