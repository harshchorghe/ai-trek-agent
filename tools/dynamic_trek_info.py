from tools.wiki_search import get_wiki_summary


def get_dynamic_trek_info(trek_name, llm):

    summary = get_wiki_summary(trek_name)

    if not summary:
        return f"No information found for {trek_name}."

    prompt = f"""
You are a trekking expert.

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